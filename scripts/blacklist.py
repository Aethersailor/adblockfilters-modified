import os
import asyncio
import re
import time
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import httpx
from tld import get_tld
from loguru import logger
import dns.message
import dns.query
import dns.rcode
from dns.asyncresolver import Resolver as DNSResolver
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers
from dns.exception import Timeout
from dns.rdatatype import RdataType as DNSRdataType


DNS_STATUS_SUCCESS = "success"
DNS_STATUS_NXDOMAIN = "nxdomain"
DNS_STATUS_NOANSWER = "noanswer"
DNS_STATUS_NO_A_RECORD = "no_a_record"
DNS_STATUS_NONAMESERVERS = "nonameservers"
DNS_STATUS_TIMEOUT = "timeout"
DNS_STATUS_ERROR = "error"

RETRYABLE_DNS_STATUSES = frozenset(
    {
        DNS_STATUS_NONAMESERVERS,
        DNS_STATUS_TIMEOUT,
        DNS_STATUS_ERROR,
    }
)


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(value, minimum)


def _env_float(name: str, default: float, minimum: float = 0.0) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(value, minimum)


def _harden_regexp(pattern: str) -> str:
    # Avoid nested greedy matching in the known geosite subdomain pattern.
    if pattern.startswith(r"^(.+\.)*"):
        return r"^(?:[^.]+\.)*" + pattern[len(r"^(.+\.)*"):]
    return pattern


class ChinaDomian(object):
    def __init__(self, fileName, url):
        self.__fileName = fileName
        self.__url = url
        self.fullSet = set()
        self.domainSet = set()
        self.regexpSet = set()
        self.keywordSet = set()
        self.__update()
        self.__resolve()

    def __normalize_domain(self, domain: str) -> str:
        domain = domain.strip().lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        try:
            domain = domain.encode("idna").decode("ascii")
        except Exception:
            pass
        return domain

    def __update(self):
        try:
            file_download = self.__fileName + ".download"
            if os.path.exists(file_download):
                os.remove(file_download)
            
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(self.__url)
                response.raise_for_status()
                with open(file_download,'wb') as f:
                    f.write(response.content)
            if os.path.exists(file_download):
                if os.path.exists(self.__fileName):
                    os.remove(self.__fileName)
                os.rename(file_download, self.__fileName)
        except Exception as e:
            logger.error("%s"%(e))
    
    def __isDomain(self, address):
        fld, subdomain = '', ''
        try:
            res = get_tld(address, fix_protocol=True, as_object=True)
            fld, subdomain = res.fld, res.subdomain
        except Exception:
            pass  # 静默处理非域名，避免大量错误日志
        finally:
            return fld, subdomain

    def __resolve(self):
        try:
            if not os.path.exists(self.__fileName):
                return
            
            with open(self.__fileName, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '#' in line:
                        line = line[:line.find('#')].strip()
                    
                    # regexp
                    if line.startswith('regexp:'):
                        self.regexpSet.add(line[7:])
                        continue
                    
                    # keyword
                    if line.startswith('keyword:'):
                        self.keywordSet.add(line[8:])
                        continue
                    
                    if line.startswith('full:'):
                        domain = line[5:]
                    elif line.startswith('domain:'):
                        domain = line[7:]
                    else:
                        domain = line
                    domain = self.__normalize_domain(domain)
                    fld, subdomian = self.__isDomain(domain)
                    if fld:
                        if subdomian:
                            self.fullSet.add(domain)
                        else:
                            self.domainSet.add(domain)
        except Exception as e:
            logger.error("%s"%(e))


class BlackList(object):
    def __init__(self):
        root = os.getcwd()
        self.__buildDir = os.path.join(root, "build")
        self.__geoDir = os.path.join(root, "data", "geo")
        os.makedirs(self.__buildDir, exist_ok=True)
        os.makedirs(self.__geoDir, exist_ok=True)

        self.__ChinalistFile = os.path.join(self.__buildDir, "china.txt")
        self.__blacklistFile = os.path.join(self.__buildDir, "black.txt")
        self.__domainlistFile = os.path.join(self.__buildDir, "domain.txt")
        self.__domainlistFile_CN = os.path.join(self.__geoDir, "direct-list.txt")
        self.__domainlistUrl_CN = "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/refs/heads/release/direct-list.txt"
        self.__domainlistFile_CN_Apple = os.path.join(self.__geoDir, "apple-cn.txt")
        self.__domainlistUrl_CN_Apple = "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/refs/heads/release/apple-cn.txt"
        self.__domainlistFile_CN_Google = os.path.join(self.__geoDir, "google-cn.txt")
        self.__domainlistUrl_CN_Google = "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/refs/heads/release/google-cn.txt"
        self.__iplistFile_CN = os.path.join(self.__geoDir, "CN-ip-cidr.txt")
        geoip_repo = os.environ.get("GEOIP_REPO", "Aethersailor/geoip").strip()
        if not geoip_repo:
            geoip_repo = "Aethersailor/geoip"
        self.__iplistUrl_CN = "https://raw.githubusercontent.com/%s/refs/heads/release/text/cn-ipv4.txt" % geoip_repo
        self.__maxTask = _env_int("BLACKLIST_DNS_CONCURRENCY", 300, 1)
        self.__dns_retries = _env_int("BLACKLIST_DNS_RETRIES", 1, 0)
        self.__dns_timeout = _env_float("BLACKLIST_DNS_TIMEOUT", 5.0, 0.1)
        self.__dns_lifetime = _env_float("BLACKLIST_DNS_LIFETIME", 8.0, 0.1)
        self.__connect_timeout = _env_float("BLACKLIST_CONNECT_TIMEOUT", 3.0, 0.1)
        self.__health_check_interval = _env_int("BLACKLIST_BATCH_SIZE", 30000, 1)
        self.__health_check_timeout = _env_float("BLACKLIST_HEALTH_TIMEOUT", 5.0, 0.1)
        self.__health_check_sleep = _env_int("BLACKLIST_HEALTH_SLEEP", 5, 1)
        self.__health_check_max_wait = _env_int("BLACKLIST_HEALTH_MAX_WAIT", 600, 1)
        default_workers = max((os.cpu_count() or 2) * 2, 8)
        self.__classification_workers = _env_int(
            "BLACKLIST_CLASSIFY_WORKERS",
            default_workers,
            1,
        )
        self.__dns_stats = Counter()
        self.__min_change_ratio = 0.7
        self.__max_change_ratio = 1.5
        self.__min_change_abs = 50000

    def __normalize_domain(self, domain: str) -> str:
        domain = domain.strip().lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        try:
            domain = domain.encode("idna").decode("ascii")
        except Exception:
            pass
        return domain

    def __split_host_port(self, address: str):
        address = address.strip()
        if address.startswith('[') and ']' in address:
            host = address[1:address.find(']')]
            port_part = address[address.find(']') + 1:]
            port = int(port_part[1:]) if port_part.startswith(':') and port_part[1:].isdigit() else None
            return host, port
        if address.count(':') == 1 and address.rfind(':') > 0:
            host, port = address.rsplit(':', 1)
            if port.isdigit():
                return host, int(port)
        return address, None

    def __count_lines(self, filename: str) -> int:
        if not os.path.exists(filename):
            return 0
        try:
            with open(filename, "r") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0

    def __getList(self, filename: str) -> list:
        if not os.path.exists(filename):
            return []
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def __is_anomalous_change(self, new_count: int, old_count: int) -> bool:
        if old_count < 1:
            return False
        diff = abs(new_count - old_count)
        if diff < self.__min_change_abs:
            return False
        ratio = new_count / old_count if old_count else 1
        return ratio < self.__min_change_ratio or ratio > self.__max_change_ratio

    def __safe_write_list(self, fileName: str, items: list, label: str) -> bool:
        old_count = self.__count_lines(fileName)
        new_count = len(items)
        if self.__is_anomalous_change(new_count, old_count):
            raise RuntimeError(
                "%s list anomaly: old=%d, new=%d" % (label, old_count, new_count)
            )
        if os.path.exists(fileName):
            os.remove(fileName)
        with open(fileName, "w") as f:
            f.write('\n'.join(items) + '\n')
        return True

    def __log_dns_stats(self):
        if not self.__dns_stats:
            return
        primary_queries = self.__dns_stats.get("primary_queries", 0)
        primary_success = self.__dns_stats.get("primary_success", 0)
        details = []
        for key in [
            "primary_nxdomain",
            "primary_noanswer",
            "primary_no_a_record",
            "primary_nonameservers",
            "primary_timeout",
            "primary_error",
            "primary_retries",
        ]:
            value = self.__dns_stats.get(key, 0)
            if value:
                details.append("%s=%d" % (key, value))
        detail_text = ", ".join(details) if details else "none"
        logger.info(
            "dns stats: primary=%d/%d, failures=%s"
            % (primary_success, primary_queries, detail_text)
        )
        logger.info(
            "final dns results: success=%d, nxdomain=%d, noanswer=%d, "
            "no_a_record=%d, transient=%d, fallback_black=%d, "
            "fallback_china=%d, fallback_unclassified=%d"
            % (
                self.__dns_stats.get("final_success", 0),
                self.__dns_stats.get("final_nxdomain", 0),
                self.__dns_stats.get("final_noanswer", 0),
                self.__dns_stats.get("final_no_a_record", 0),
                sum(
                    self.__dns_stats.get("final_" + status, 0)
                    for status in RETRYABLE_DNS_STATUSES
                ),
                self.__dns_stats.get("fallback_previous_black", 0),
                self.__dns_stats.get("fallback_previous_china", 0),
                self.__dns_stats.get("fallback_unclassified", 0),
            )
        )

    def __check_smartdns(self, host: str, port: int) -> tuple:
        try:
            q = dns.message.make_query("example.com", "A")
            r = dns.query.udp(q, host, port=port, timeout=self.__health_check_timeout)
            rcode = r.rcode()
            return rcode == dns.rcode.NOERROR, dns.rcode.to_text(rcode)
        except Exception as e:
            return False, str(e)

    def __wait_for_smartdns(self, host: str, port: int):
        start = time.time()
        attempt = 0
        delay = self.__health_check_sleep
        while True:
            healthy, detail = self.__check_smartdns(host, port)
            if healthy:
                if attempt > 0:
                    logger.info("SmartDNS healthy: %s after %d attempts" % (detail, attempt))
                return
            attempt += 1
            logger.warning(
                "SmartDNS unhealthy: %s (attempt=%d). Wait %ds"
                % (detail, attempt, delay)
            )
            time.sleep(delay)
            if self.__health_check_max_wait and (time.time() - start) >= self.__health_check_max_wait:
                raise RuntimeError("SmartDNS unhealthy for %ds" % self.__health_check_max_wait)
            delay = min(delay * 2, 60)

    def __stop_smartdns(self, bin_path: str):
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/f", "/im", "smartdns.exe"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                return
            subprocess.run(
                ["pkill", "-f", os.path.basename(bin_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            time.sleep(1)
        except Exception as e:
            logger.warning("stop smartdns failed: %s" % e)

    def __restart_smartdns(self):
        smartdns_path = os.environ.get("SMARTDNS_PATH", "/tmp/smartdns")
        bin_path = os.path.join(smartdns_path, "smartdns")
        conf_path = os.path.join(smartdns_path, "smartdns.conf")
        if not os.path.exists(bin_path):
            logger.warning("smartdns binary not found: %s" % bin_path)
            return False
        if not os.path.exists(conf_path):
            logger.warning("smartdns config not found: %s" % conf_path)
            return False
        self.__stop_smartdns(bin_path)
        try:
            subprocess.Popen(
                [bin_path, "-f", "-x", "-c", conf_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            logger.info("smartdns restarted")
            return True
        except Exception as e:
            logger.warning("smartdns restart failed: %s" % e)
            return False

    def __getDomainList(self):
        logger.info("resolve adblock dns backup...")
        domainList = []
        try:
            if os.path.exists(self.__domainlistFile):
                with open(self.__domainlistFile, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        host, port = self.__split_host_port(line)
                        host = self.__normalize_domain(host)
                        domain = "%s:%d" % (host, port) if port else host
                        domainList.append(domain)
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            logger.info("adblock dns backup: %d"%(len(domainList)))
            return domainList
        
    def __getDomainSet_CN(self):
        logger.info("resolve China domain list...")
        fullSet,domainSet,regexpSet,keywordSet = set(),set(),set(),set()
        try:
            domain_cn = ChinaDomian(self.__domainlistFile_CN, self.__domainlistUrl_CN)
            domain_apple = ChinaDomian(self.__domainlistFile_CN_Apple, self.__domainlistUrl_CN_Apple)
            domain_google = ChinaDomian(self.__domainlistFile_CN_Google, self.__domainlistUrl_CN_Google)

            fullSet = domain_cn.fullSet | domain_apple.fullSet | domain_google.fullSet
            domainSet = domain_cn.domainSet | domain_apple.domainSet | domain_google.domainSet
            regexpSet = domain_cn.regexpSet | domain_apple.regexpSet | domain_google.regexpSet
            keywordSet = domain_cn.keywordSet | domain_apple.keywordSet | domain_google.keywordSet
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            logger.info("China domain list: full[%d], domain[%d], regexp[%d], keyword[%d]"%(len(fullSet),len(domainSet),len(regexpSet),len(keywordSet)))
            return fullSet,domainSet,regexpSet,keywordSet
        
    def __getIPTrie_CN(self):
        """构建中国 IP 前缀树，使用 pytricia 实现 O(32) 时间复杂度的 CIDR 匹配"""
        logger.info("resolve China IP list...")
        import pytricia

        pyt = pytricia.PyTricia()
        try:
            file_download = self.__iplistFile_CN + ".download"
            if os.path.exists(file_download):
                os.remove(file_download)
            
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(self.__iplistUrl_CN)
                response.raise_for_status()
                with open(file_download,'wb') as f:
                    f.write(response.content)
            
            if os.path.exists(file_download):
                if os.path.exists(self.__iplistFile_CN):
                    os.remove(self.__iplistFile_CN)
                os.rename(file_download, self.__iplistFile_CN)
            
            if os.path.exists(self.__iplistFile_CN):
                with open(self.__iplistFile_CN, 'r') as f:
                    for line in f:
                        cidr = line.strip()
                        if cidr and not cidr.startswith('#'):
                            pyt.insert(cidr, True)
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            logger.info("China IP Trie entries: %d"%(len(pyt)))
            return pyt
    
    async def __resolve(self, dnsresolver, domain, source="primary"):
        ipList = []
        status = DNS_STATUS_ERROR
        stat_prefix = "%s_" % source
        self.__dns_stats[stat_prefix + "queries"] += 1
        try:
            query_object = await dnsresolver.resolve(qname=domain, rdtype="A")
            query_item = None
            for item in query_object.response.answer:
                if item.rdtype == DNSRdataType.A:
                    query_item = item
                    break
            if query_item is None:
                self.__dns_stats[stat_prefix + "no_a_record"] += 1
                status = DNS_STATUS_NO_A_RECORD
            else:
                for item in query_item:
                    ip = '{}'.format(item)
                    if ip != "0.0.0.0":
                        ipList.append(ip)
                if ipList:
                    self.__dns_stats[stat_prefix + "success"] += 1
                    status = DNS_STATUS_SUCCESS
                else:
                    self.__dns_stats[stat_prefix + "no_a_record"] += 1
                    status = DNS_STATUS_NO_A_RECORD
        except NXDOMAIN:
            self.__dns_stats[stat_prefix + "nxdomain"] += 1
            status = DNS_STATUS_NXDOMAIN
        except NoAnswer:
            self.__dns_stats[stat_prefix + "noanswer"] += 1
            status = DNS_STATUS_NOANSWER
        except NoNameservers:
            self.__dns_stats[stat_prefix + "nonameservers"] += 1
            status = DNS_STATUS_NONAMESERVERS
        except Timeout:
            self.__dns_stats[stat_prefix + "timeout"] += 1
            status = DNS_STATUS_TIMEOUT
        except Exception:
            self.__dns_stats[stat_prefix + "error"] += 1
            status = DNS_STATUS_ERROR
        if not ipList:
            self.__dns_stats[stat_prefix + "empty"] += 1
        return ipList, status

    async def __try_connect(self, host: str, port: int) -> bool:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.__connect_timeout,
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False

    async def __pingx(self, dnsresolver, domain, semaphore):
        async with semaphore:
            host, port = self.__split_host_port(domain)
            host = self.__normalize_domain(host)
            ipList = []
            try:
                get_tld(host, fix_protocol=True, as_object=True)
            except Exception:
                port = 80
            if port:
                if await self.__try_connect(host, port):
                    ipList.append(host)
                elif port == 80:
                    port = 443
                    if await self.__try_connect(host, port):
                        ipList.append(host)
            status = DNS_STATUS_SUCCESS if ipList else DNS_STATUS_ERROR
            if not ipList:
                attempts = self.__dns_retries + 1
                for attempt in range(attempts):
                    ipList, status = await self.__resolve(
                        dnsresolver,
                        host,
                        source="primary",
                    )
                    if ipList or status not in RETRYABLE_DNS_STATUSES:
                        break
                    if attempt + 1 < attempts:
                        self.__dns_stats["primary_retries"] += 1
            return domain, ipList, status

    def __generateBlackList(self, blackList):
        logger.info("generate black list...")
        if self.__safe_write_list(self.__blacklistFile, blackList, "black"):
            logger.info("block domain: %d"%(len(blackList)))
    
    def __generateChinaList(self, ChinaList):
        logger.info("generate China list...")
        if self.__safe_write_list(self.__ChinalistFile, ChinaList, "china"):
            logger.info("China domain: %d"%(len(ChinaList)))

    def __testDomain(self, domainList, nameservers, port=53):
        logger.info("resolve domain...")
        # 配置 DNS 解析器
        dnsresolver = DNSResolver()
        dnsresolver.nameservers = nameservers
        dnsresolver.port = port
        dnsresolver.timeout = self.__dns_timeout
        dnsresolver.lifetime = self.__dns_lifetime
        async def resolve_batch():
            semaphore = asyncio.Semaphore(self.__maxTask)
            tasks = [
                self.__pingx(dnsresolver, domain, semaphore)
                for domain in domainList
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)

        results = asyncio.run(resolve_batch())
        domainDict = {}
        for domain, result in zip(domainList, results):
            if isinstance(result, Exception):
                domainDict[domain] = ([], DNS_STATUS_ERROR)
                continue
            resolvedDomain, ipList, status = result
            domainDict[resolvedDomain] = (ipList, status)

        resolved = sum(1 for ipList, _ in domainDict.values() if ipList)
        logger.info("resolve domain: %d, success: %d, fail: %d"%(len(domainDict), resolved, len(domainDict) - resolved))
        return domainDict

    def __iterDomainBatches(self, domainList, nameservers, port=53):
        if not self.__health_check_interval or self.__health_check_interval <= 0:
            yield 1, len(domainList), self.__testDomain(domainList, nameservers, port)
            return
        host = nameservers[0] if nameservers else "127.0.0.1"
        total = len(domainList)
        self.__wait_for_smartdns(host, port)
        for start in range(0, total, self.__health_check_interval):
            end = min(start + self.__health_check_interval, total)
            logger.info("resolve domain batch: %d-%d/%d" % (start + 1, end, total))
            batchDict = self.__testDomain(domainList[start:end], nameservers, port)
            yield start + 1, end, batchDict
            if end < total:
                if self.__restart_smartdns():
                    self.__wait_for_smartdns(host, port)

    def __compileRegexps(self, regexpSet):
        compiled = []
        for pattern in sorted(regexpSet):
            safe_pattern = _harden_regexp(pattern)
            try:
                compiled.append(re.compile(safe_pattern))
            except re.error as e:
                logger.warning('skip invalid China regexp "%s": %s' % (pattern, e))
        return compiled

    def __isChinaDomain(self, domain, ipList, fullSet_CN, domainSet_CN, compiled_regexps, keywordSet_CN, IPTrie_CN):
        """判断域名是否属于中国，使用预编译正则和前缀树进行高效判定"""
        isChinaDomain = False
        try:
            if ':' in domain:
                domain = domain[:domain.find(':')]
            domain = self.__normalize_domain(domain)
            
            # .cn 域名直接判定为中国
            if domain.endswith('.cn'):
                return domain, True
            
            # full: 完全匹配
            if domain in fullSet_CN:
                return domain, True
            
            # domain: 主域名匹配
            try:
                res = get_tld(domain, fix_protocol=True, as_object=True)
                if res.fld in domainSet_CN:
                    return domain, True
            except Exception:
                pass
            
            # regexp: 使用预编译正则
            for pattern in compiled_regexps:
                if pattern.search(domain):
                    return domain, True
            
            # keyword: 使用 in 操作符替代正则
            for keyword in keywordSet_CN:
                if keyword in domain:
                    return domain, True
            
            # IP 归属判定：使用前缀树 O(32) 时间复杂度
            for ip in ipList:
                if ip in IPTrie_CN:
                    return domain, True
                    
        except Exception as e: 
            logger.error('"%s": not domain'%(domain))
        
        return domain, isChinaDomain

    def __classifyBatch(
        self,
        domainDict,
        previousBlackSet,
        previousChinaSet,
        classifier,
        thread_pool,
    ):
        blackList = []
        ChinaSet = set()
        resolvedDomains = []
        resolvedIPs = []

        for domain, (ipList, status) in domainDict.items():
            self.__dns_stats["final_" + status] += 1
            if ipList:
                resolvedDomains.append(domain)
                resolvedIPs.append(ipList)
                continue

            if status in RETRYABLE_DNS_STATUSES:
                if domain in previousBlackSet:
                    blackList.append(domain)
                    self.__dns_stats["fallback_previous_black"] += 1
                elif domain in previousChinaSet:
                    ChinaSet.add(domain)
                    self.__dns_stats["fallback_previous_china"] += 1
                else:
                    self.__dns_stats["fallback_unclassified"] += 1
                continue

            blackList.append(domain)

        for domain, isChinaDomain in thread_pool.map(
            classifier,
            resolvedDomains,
            resolvedIPs,
        ):
            if isChinaDomain:
                ChinaSet.add(domain)

        return blackList, ChinaSet

    def generate(self):
        try:
            self.__dns_stats = Counter()
            domainList = self.__getDomainList()
            if len(domainList) < 1:
                return

            fullSet_CN, domainSet_CN, regexpSet_CN, keywordSet_CN = self.__getDomainSet_CN()
            IPTrie_CN = self.__getIPTrie_CN()

            compiled_regexps = self.__compileRegexps(regexpSet_CN)
            logger.info("Compiled %d regexp patterns" % len(compiled_regexps))

            if len(domainSet_CN) <= 100 or len(IPTrie_CN) <= 100:
                raise RuntimeError("China list or IP list is unexpectedly small")

            previousBlackSet = set(self.__getList(self.__blacklistFile))
            previousChinaSet = set(self.__getList(self.__ChinalistFile))
            blackList = []
            ChinaSet_tmp = set()
            classifier = partial(
                self.__isChinaDomain,
                fullSet_CN=fullSet_CN,
                domainSet_CN=domainSet_CN,
                compiled_regexps=compiled_regexps,
                keywordSet_CN=keywordSet_CN,
                IPTrie_CN=IPTrie_CN,
            )
            total = len(domainList)
            logger.info(
                "Streaming classification with %d workers, batch size %d"
                % (self.__classification_workers, self.__health_check_interval)
            )
            with ThreadPoolExecutor(max_workers=self.__classification_workers) as thread_pool:
                for start, end, domainDict in self.__iterDomainBatches(
                    domainList,
                    ["127.0.0.1"],
                    5053,
                ):
                    batchBlackList, batchChinaSet = self.__classifyBatch(
                        domainDict,
                        previousBlackSet,
                        previousChinaSet,
                        classifier,
                        thread_pool,
                    )
                    blackList.extend(batchBlackList)
                    ChinaSet_tmp.update(batchChinaSet)
                    logger.info(
                        "processed domain batch: %d-%d/%d, black=%d, china=%d"
                        % (
                            start,
                            end,
                            total,
                            len(blackList),
                            len(ChinaSet_tmp),
                        )
                    )

            self.__log_dns_stats()
            ChinaList = [domain for domain in domainList if domain in ChinaSet_tmp]
            self.__generateChinaList(ChinaList)
            self.__generateBlackList(blackList)
        except Exception as e:
            logger.error("%s"%(e))
            raise

if __name__ == "__main__":
    blackList = BlackList()
    blackList.generate()

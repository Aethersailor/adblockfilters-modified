import os
import sys
import re
import ipaddress
from typing import Tuple, Dict, Set, List, NamedTuple, Optional

from tld import get_tld
from loguru import logger

from readme import Rule

class FilterDomainInfo(NamedTuple):
    domains: Set[str]
    source: str  # target|context|none

class Resolver(object):
    def __init__(self, paths):
        if isinstance(paths, (list, tuple)):
            self.paths = [p for p in paths if p]
        else:
            self.paths = [paths] if paths else []
        self.options = {# Adblock Plus filter options
                        'script',         '~script',
                        'image',          '~image',
                        'stylesheet',     '~stylesheet',
                        'object',         '~object',
                        'subdocument',    '~subdocument',
                        'xmlhttprequest', '~xmlhttprequest',
                        'websocket',      '~websocket',
                        'webrtc',         '~webrtc',
                        'popup',
                        'generichide',
                        'genericblock',
                        'document',
                        'elemhide',
                        'third-party', '~third-party',
                        'ping',
                        'other',
                        'match-case',
                        # AdGuard Advanced capabilities
                        'ctag',
                        'all',
                        'redirect',
                        'stealth',
                        'domain'
                    }

    def _find_file(self, filename: str) -> str:
        for base in self.paths:
            candidate = os.path.join(base, filename)
            if os.path.exists(candidate):
                return candidate
        return ""
    
    def __normalize_domain(self, domain: str) -> str:
        domain = domain.strip().lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        try:
            domain = domain.encode("idna").decode("ascii")
        except Exception:
            pass
        return domain

    def __is_ip_address(self, address: str) -> bool:
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    def __split_host_port(self, address: str) -> Tuple[str, Optional[str]]:
        address = address.strip()
        if address.startswith('[') and ']' in address:
            host = address[1:address.find(']')]
            port_part = address[address.find(']') + 1:]
            port = port_part[1:] if port_part.startswith(':') else None
            return host, port
        if address.count(':') == 1 and address.rfind(':') > 0:
            host, port = address.rsplit(':', 1)
            if port.isdigit():
                return host, port
        return address, None

    def __ip_or_domain(self, address:str) -> Tuple[str]: # ip, fld, subdomain
        ip, fld, subdomain = None, None, None
        try:
            address = self.__normalize_domain(address)
            res = get_tld(address, fix_protocol=True, as_object=True)
            fld = self.__normalize_domain(res.fld)
            subdomain = self.__normalize_domain(res.subdomain) if res.subdomain else ''
        except Exception as e:
            try:
                if ipaddress.ip_address(address).is_global:
                    ip = address
            except Exception as e:
                pass
        finally:
            return ip, fld, subdomain
    
    def __analysis(self, address:str) -> Tuple[str]:
        address_tmp, _ = self.__split_host_port(address)
        ip, fld, subdomain = self.__ip_or_domain(address_tmp)
        if ip:
            return address, "" # 可能包含port，因此直接return address
        if fld:
            return fld, subdomain
        raise Exception('"%s": not domain or public ip'%(address))

    def __normalize_domain_candidate(self, domain: str) -> Optional[str]:
        domain = domain.strip()
        if not domain or domain.startswith('~'):
            return None
        if ',' in domain or '|' in domain:
            return None
        if domain.startswith('*.'):
            domain = domain[2:]
        if domain.startswith('.') or domain.startswith('/'):
            domain = domain[1:]
        if '"' in domain:
            domain = domain[:domain.find('"')]
        if '^' in domain:
            domain = domain[:domain.find('^')]
        if '/' in domain:
            domain = domain[:domain.find('/')]
        if '*' in domain or domain.endswith('.') or domain.startswith('-'):
            return None
        return domain

    def __parse_domain_list(self, domain_list: str, separator: str) -> Set[str]:
        domains = set()
        for item in domain_list.split(separator):
            candidate = self.__normalize_domain_candidate(item)
            if not candidate:
                continue
            try:
                fld, subdomain = self.__analysis(candidate)
                domain = "%s.%s" % (subdomain, fld) if subdomain else "%s" % (fld)
                domains.add(domain)
            except Exception:
                continue
        return domains

    def __parse_domain_option(self, filter: str) -> Set[str]:
        if '$' not in filter:
            return set()
        options = filter.split('$', 1)[1]
        for part in options.split(','):
            part = part.strip()
            if part.startswith('domain='):
                domain_value = part[len('domain='):]
                return self.__parse_domain_list(domain_value, '|')
        return set()

    # host 模式
    def __resolveHost(self, line) -> List[Tuple[str, str]]:
        def match(pattern, string):
            return True if re.match(pattern, string) else False
        try:
            blocks = []
            while True:
                # #* 注释
                if match('^#.*', line):
                    break
                if match('^!.*', line):
                    break

                line = line.replace('\t', ' ')
                
                if line.find('#') > 0:
                    line = line[:line.find('#')].strip()
                line = line.strip()
                if not line:
                    break
                
                row = line.split()
                if len(row) < 2:
                    break
                if not self.__is_ip_address(row[0]):
                    break
                for domain in row[1:]:
                    if domain in {
                        'localhost',
                        'localhost.localdomain',
                        'local',
                        '0.0.0.0',
                        '127.0.0.1',
                        '::1',
                        '::',
                        'ip6-localhost',
                        'ip6-loopback',
                    }:
                        continue
                    try:
                        blocks.append(self.__analysis(domain))
                    except Exception:
                        continue
                break
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            return blocks

    # 从 filter 规则中找出包含的域名
    def __resolveFilterDomain(self, filter) -> Tuple[str, FilterDomainInfo]:
        def match(pattern, string) -> bool:
            return True if re.match(pattern, string) else False
        domain = None
        domain_set = set()
        source = "none"
        try:
            domain_tmp = None
            while True:
                '''
                # for test
                if filter == "@@|https://media.amazon.map.fastly.net^$script":
                    print(filter)
                '''
                if filter.startswith('#%#var'):
                    break

                if filter.startswith('###'):
                    break

                if filter.startswith('##') and filter.find('://') < 0:
                    break

                if match('^/.*/$', filter):
                    break

                # ||example.org^$option
                # @@||example.org^$option
                if match('^\|\|.*\^\$.*', filter) or match('^@@\|\|.*\^\$.*', filter):
                    anchor = filter.find('^$')
                    if anchor > 0:
                        if filter.startswith('@@||'):
                            domain_tmp = filter[len('@@||'):anchor]
                        else:
                            domain_tmp = filter[len('||'):anchor]
                    break
                # ||example.org
                if match('^\|\|.*', filter):
                    domain_tmp = filter[len('||'):]
                    if domain_tmp.find('/') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('/')]
                    if domain_tmp.find('$') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('$')]
                    if domain_tmp.find('^*') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('^*')]
                    if domain_tmp.find('*') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('*')]
                    break
                # @@||example.org
                if match('^@@\|\|.*', filter):
                    domain_tmp = filter[len('@@||'):]
                    if domain_tmp.find('/') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('/')]
                    if domain_tmp.find('$') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('$')]
                    if domain_tmp.find('^*') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('^*')]
                    if domain_tmp.find('*') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('*')]
                    break

                # ip$network
                if match('.*\$network$', filter):
                    domain_tmp = filter[:-len('$network')]
                    if domain_tmp.startswith('@@'):
                        domain_tmp = domain_tmp[2:]
                    break

                if filter.startswith('@@/') and filter.count('/') >= 2:
                    break

                # example.org$image or @@example.org$script
                if '$' in filter:
                    candidate = filter
                    if candidate.startswith('@@'):
                        candidate = candidate[2:]
                    if candidate.startswith('||'):
                        candidate = candidate[2:]
                    elif candidate.startswith('|'):
                        candidate = candidate[1:]
                    if candidate.startswith('http://') or candidate.startswith('https://'):
                        candidate = candidate.split('://', 1)[1]
                    candidate = candidate[:candidate.find('$')].strip()
                    if candidate and not candidate.startswith('~'):
                        domain_tmp = candidate
                    break

                # example.org^
                if match('.*\^$', filter):
                    domain_tmp = filter[:-1]
                    break
                
                # ##
                # example.com##selector
                # ~example.com##selector
                # example.com,example.edu##selector
                # example.com,~mail.example.com##selector
                connector = '##'
                if match('.*%s.*'%(connector), filter) and not filter.startswith(connector) and not filter.endswith(connector):
                    domain_tmp = filter[ : filter.find(connector)]
                    domain_set = self.__parse_domain_list(domain_tmp, ',')
                    if domain_set:
                        source = "context"
                    domain_tmp = None
                    break
                # #?#
                # example.com#?#selector
                # ~example.com#?#selector
                # example.com,example.edu#?#selector
                # example.com,~mail.example.com#?#selector
                connector = '#\?#'
                if match('.*%s.*'%(connector), filter) and not filter.startswith(connector) and not filter.endswith(connector):
                    domain_tmp = filter[ : filter.find('#?#')] # 需去掉转义符'#\?#' -> '#?#'
                    domain_set = self.__parse_domain_list(domain_tmp, ',')
                    if domain_set:
                        source = "context"
                    domain_tmp = None
                    break
                # #@#
                # example.com#@#selector
                # ~example.com#@#selector
                # example.com,example.edu#@#selector
                # example.com,~mail.example.com#@#selector
                connector = '#@#'
                if match('.*%s.*'%(connector), filter) and not filter.startswith(connector) and not filter.endswith(connector):
                    domain_tmp = filter[ : filter.find(connector)]
                    domain_set = self.__parse_domain_list(domain_tmp, ',')
                    if domain_set:
                        source = "context"
                    domain_tmp = None
                    break
                # #$#
                # example.com#$#selector
                # ~example.com#$#selector
                # example.com,example.edu#$#selector
                # example.com,~mail.example.com#$#selector
                connector = '#\$#'
                if match('.*%s.*'%(connector), filter) and not filter.startswith(connector) and not filter.endswith(connector):
                    domain_tmp = filter[ : filter.find('#$#')] # 需去掉转义符'#\$#' -> '#$#'
                    domain_set = self.__parse_domain_list(domain_tmp, ',')
                    if domain_set:
                        source = "context"
                    domain_tmp = None
                    break
                # #%#
                # example.com#%#selector
                # ~example.com#%#selector
                # example.com,example.edu#%#selector
                # example.com,~mail.example.com#%#selector
                connector = '#%#'
                if match('.*%s.*'%(connector), filter) and not filter.startswith(connector) and not filter.endswith(connector):
                    domain_tmp = filter[ : filter.find(connector)]
                    domain_set = self.__parse_domain_list(domain_tmp, ',')
                    if domain_set:
                        source = "context"
                    domain_tmp = None
                    break
                
                # a[href^="http://sarcasmadvisor.com/"]
                if match('.*http:\/\/.*', filter):
                    domain_tmp = filter[filter.find('http://') + len('http://'):]
                    if domain_tmp.startswith('*.'):
                        domain_tmp = domain_tmp[2:]
                    if domain_tmp.find("'") > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find("'")]
                    if domain_tmp.find("^") > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find("^")]
                    if domain_tmp.find('$') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('$')]
                    if domain_tmp.find(',') > 0:
                        domain_tmp = None
                    break

                # a[href^="https://sarcasmadvisor.com/"]
                if match('.*https:\/\/.*', filter):
                    domain_tmp = filter[filter.find('https://') + len('https://'):]
                    if domain_tmp.startswith('*.'):
                        domain_tmp = domain_tmp[2:]
                    if domain_tmp.find("'") > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find("'")]
                    if domain_tmp.find("^") > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find("^")]
                    if domain_tmp.find('$') > 0:
                        domain_tmp = domain_tmp[:domain_tmp.find('$')]
                    break

                # fallback: treat as a plain domain rule with anchors/options
                candidate = filter
                if candidate.startswith('@@'):
                    candidate = candidate[2:]
                if candidate.startswith('||'):
                    candidate = candidate[2:]
                elif candidate.startswith('|'):
                    candidate = candidate[1:]
                for sep in ['$', '^', '/']:
                    if sep in candidate:
                        candidate = candidate[:candidate.find(sep)]
                candidate = candidate.strip()
                if candidate:
                    domain_tmp = candidate
                break
            
            if domain_tmp and not domain_set:
                candidate = self.__normalize_domain_candidate(domain_tmp)
                if candidate:
                    try:
                        fld, subdomain = self.__analysis(candidate)
                        domain = "%s.%s"%(subdomain,fld) if len(subdomain) > 0 else "%s"%(fld)
                        domain_set = {domain}
                        source = "target"
                    except Exception:
                        pass

            if not domain_set:
                domain_set = self.__parse_domain_option(filter)
                if domain_set:
                    source = "context"
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            return filter, FilterDomainInfo(domain_set, source)

    # dns 模式
    def __resolveDNS(self, line) -> Tuple[Tuple[str],Tuple[str],Tuple[str, FilterDomainInfo]]:
        def match(pattern, string):
            return True if re.match(pattern, string) else False
        try:
            block,unblock,filter=None,None,None
            while True:
                # !* 注释
                if match('^!.*', line):
                    break
                # [*] 注释
                if match('^\[.*\]$', line):
                    break
                # #* 注释
                if match('^#.*', line):
                    break

                # 干掉注释
                if line.find('#') > 0:
                    line = line[:line.find('#')].strip()

                # ||example.org^
                if match('^\|\|.*\^$', line):
                    domain = line[2:-1]
                    if domain.find('*') >= 0:
                        if domain.startswith('*.') and domain[2:].find('*')<0:
                            domain = domain[2:]
                            block = self.__analysis(domain)
                            break
                        filter = line
                        break
                    block = self.__analysis(domain)
                    break
                # @@||example.org^
                if match('^@@\|\|.*\^$', line):
                    domain = line[4:-1]
                    if domain.find('*') >= 0:
                        if domain.startswith('*.') and domain[2:].find('*')<0:
                            domain = domain[2:]
                            unblock = self.__analysis(domain)
                            break
                        filter = line
                        break
                    unblock = self.__analysis(domain)
                    break
                # @@* (exceptions with options or regex)
                if line.startswith('@@'):
                    filter = line
                    break
                # /REGEX/
                if match('^/.*/$', line):
                    filter = line
                    break
                # ||example. or ||example.org^$ctag=device_tv
                if match('^\|\|.*', line):
                    filter = line
                    break
                # other
                raise Exception('"%s": not keep'%(line))
            
            if filter:
                filter = self.__resolveFilterDomain(filter)
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            return block,unblock,filter

    # filter 模式
    def __resolveFilter(self, line) -> Tuple[Tuple[str],Tuple[str],Tuple[str, FilterDomainInfo]]:
        def match(pattern, string):
            return True if re.match(pattern, string) else False
        try:
            block,unblock,filter=None,None,None
            while True:
                # !* 注释
                if match('^!.*', line):
                    break
                # [*] 注释
                if match('^\[.*\]$', line):
                    break
                # ## or ###
                if match('^##.*', line):
                    filter = line
                    break
                # #%#
                if match('^#%#.*', line):
                    filter = line
                    break
                # #* 注释
                if match('^#.*', line):
                    break

                # 干掉注释
                #if line.find(' #') > 0:
                #    line = line[:line.find(' #')].strip()

                # ||example.org^: block access to the example.org domain and all its subdomains, like www.example.org.
                if match('^\|\|.*\^$', line):
                    domain = line[2:-1]
                    if domain.find('/') >= 0:
                        filter = line
                        break
                    if domain.find('*') >= 0:
                        if domain.startswith('*.') and domain[2:].find('*')<0:
                            domain = domain[2:]
                            block = self.__analysis(domain)
                            break
                        else:
                            filter = line
                            break
                    block = self.__analysis(domain)
                    break
                # @@||example.org^: unblock access to the example.org domain and all its subdomains.
                if match('^@@\|\|.*\^$', line):
                    domain = line[4:-1]
                    if domain.find('*') >= 0 or domain.find('/') >= 0:
                        filter = line
                        break
                    unblock = self.__analysis(domain)
                    break
                # @@||example.org^|: unblock access to the example.org domain and all its subdomains.
                if match('^@@\|\|.*\^\|$', line):
                    domain = line[4:-2]
                    if domain.find('*') >= 0 or domain.find('/') >= 0:
                        filter = line
                        break
                    unblock = self.__analysis(domain)
                    break
                # /REGEX/: block access to the domains matching the specified regular expression
                if match('^/.*/$', line):
                    filter = line
                    break
                # 判断是否为单纯的域名
                if line.find('.')>0 and not line.startswith('*.') and not line.startswith('-') and line.find('=')<0 and line.find(':')<0 and line.find('*')<0 and line.find('_')<0 and line.find('?')<0 and line.find(';')<0 and line.find('|')<0 and line.find('$')<0 and line.find('#')<0 and line.find('/')<0 and line.find('%')<0 and line.find('^') < 0:
                    domain = line
                    block = self.__analysis(domain)
                    break
                # other
                filter = line
                break

            if filter:
                filter = self.__resolveFilterDomain(filter)
        except Exception as e:
            logger.error("%s"%(e))
        finally:
            return block,unblock,filter

    def resolveHost(self, rule:Rule) -> Tuple[Dict[str,Set[str]],Dict[str,Set[str]],Dict[str,FilterDomainInfo]]:
        blockDict:Dict[str,Set[str]] = dict()
        unblockDict:Dict[str,Set[str]] = dict()
        filterDict:Dict[str,FilterDomainInfo] = dict()

        filename = self._find_file(rule.filename)

        if not filename or not os.path.exists(filename):
            return blockDict,unblockDict,filterDict

        with open(filename, "r") as f:
            for line in f:
                # 去掉换行符
                line = line.replace('\r', '').replace('\n', '').strip()
                # 去掉空行
                if len(line) < 1:
                    continue

                blocks = self.__resolveHost(line)
                for block in blocks:
                    if block[0] not in blockDict:
                        blockDict[block[0]] = {block[1],}
                    else:
                        blockDict[block[0]].add(block[1])
        logger.info("%s: block=%d, unblock=%d, filter=%d"%(rule.name,len(blockDict),len(unblockDict),len(filterDict)))
        return blockDict,unblockDict,filterDict

    def resolveDNS(self, rule:Rule) -> Tuple[Dict[str,Set[str]],Dict[str,Set[str]],Dict[str,FilterDomainInfo]]:
        blockDict:Dict[str,Set[str]] = dict()
        unblockDict:Dict[str,Set[str]] = dict()
        filterDict:Dict[str,FilterDomainInfo] = dict()

        filename = self._find_file(rule.filename)

        if not filename or not os.path.exists(filename):
            return blockDict,unblockDict,filterDict

        with open(filename, "r") as f:
            for line in f:
                # 去掉换行符
                line = line.replace('\r', '').replace('\n', '').strip()
                # 去掉空行
                if len(line) < 1:
                    continue

                block,unblock,filter = self.__resolveDNS(line)
                
                if block:
                    if block[0] not in blockDict:
                        blockDict[block[0]] = {block[1],}
                    else:
                        blockDict[block[0]].add(block[1])
                if unblock:
                    if unblock[0] not in unblockDict:
                        unblockDict[unblock[0]] = {unblock[1],}
                    else:
                        unblockDict[unblock[0]].add(unblock[1])
                if filter:
                    filterDict[filter[0]] = filter[1]
        logger.info("%s: block=%d, unblock=%d, filter=%d"%(rule.name,len(blockDict),len(unblockDict),len(filterDict)))
        return blockDict,unblockDict,filterDict
    
    def resolveFilter(self, rule:Rule) -> Tuple[Dict[str,Set[str]],Dict[str,Set[str]],Dict[str,FilterDomainInfo]]:
        blockDict:Dict[str,Set[str]] = dict()
        unblockDict:Dict[str,Set[str]] = dict()
        filterDict:Dict[str,FilterDomainInfo] = dict()

        filename = self._find_file(rule.filename)

        if not filename or not os.path.exists(filename):
            return blockDict,unblockDict,filterDict

        with open(filename, "r") as f:
            for line in f:
                # 去掉换行符
                line = line.replace('\r', '').replace('\n', '').strip()
                # 去掉空行
                if len(line) < 1:
                    continue

                block,unblock,filter = self.__resolveFilter(line)
                
                if block:
                    if block[0] not in blockDict:
                        blockDict[block[0]] = {block[1],}
                    else:
                        blockDict[block[0]].add(block[1])
                if unblock:
                    if unblock[0] not in unblockDict:
                        unblockDict[unblock[0]] = {unblock[1],}
                    else:
                        unblockDict[unblock[0]].add(unblock[1])
                if filter:
                    filterDict[filter[0]] = filter[1]
        logger.info("%s: block=%d, unblock=%d, filter=%d"%(rule.name,len(blockDict),len(unblockDict),len(filterDict)))
        return blockDict,unblockDict,filterDict

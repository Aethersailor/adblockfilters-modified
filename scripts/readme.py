import re
import os
import subprocess
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from typing import List

from loguru import logger

class Rule(object):
    def __init__(self, name:str, type:str, url:str, latest:str, update:bool=False):
        self.name = name
        safe_name = self.name.replace(' ', '_')
        for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            safe_name = safe_name.replace(ch, '_')
        self.filename = safe_name + '.txt'
        self.type = type
        self.url = url
        self.latest = latest
        self.update = update

# redme文件操作
class ReadMe(object):
    def __init__(self, filename:str):
        self.filename = filename
        self.ruleList:List[Rule] = []
        self.accel_size_threshold = 20 * 1024 * 1024
        self.proxyList = [
            "",
            "https://testingcf.jsdelivr.net/gh",
        ]
        self.upstream_repo = os.environ.get("UPSTREAM_REPO", "217heidai/adblockfilters")
        self.upstream_branch = os.environ.get("UPSTREAM_BRANCH", "main")
        self.repo = self._resolve_repo()
        self.branch = self._resolve_branch()

    def getRules(self) -> List[Rule]:
        logger.info("resolve readme...")
        self.ruleList = []
        with open(self.filename, "r") as f:
            for line in f:
                line = line.replace('\r', '').replace('\n', '')
                if line.find('|')==0 and line.rfind('|')==len(line)-1:
                    rule = list(map(lambda x: x.strip(), line[1:-1].split('|')))
                    if len(rule) < 4:
                        continue
                    if rule[2].find('(') > 0 and rule[2].find(')') > 0 and rule[1].find('(') < 0:
                        url = rule[2][rule[2].find('(')+1:rule[2].find(')')]
                        matchObj1 = re.match('(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', url)
                        if matchObj1:
                            self.ruleList.append(Rule(rule[0], rule[1], url, rule[-1]))
        return self.ruleList

    def getRulesNames(self) -> str:
        names = ""
        
        for rule in self.ruleList:
            names += rule.name + '、'
        
        return names[:-1]

    def setRules(self, ruleList:List[Rule]):
        self.ruleList = ruleList

    def _get_local_path(self, base_dir: str, fileName: str) -> str:
        base_dir = base_dir.strip("/")
        base_root = os.path.dirname(self.filename)
        return os.path.join(base_root, base_dir, fileName)

    def _should_use_boki(self, base_dir: str, fileName: str) -> bool:
        if base_dir.strip("/") != "rules":
            return False
        try:
            return os.path.getsize(self._get_local_path(base_dir, fileName)) >= self.accel_size_threshold
        except Exception:
            return False

    def __subscribeLink(self, fileName:str, url:str=None, base_dir:str="rules"):
        link = ""
        base_dir = base_dir.strip("/")
        raw_url = ""

        if url:
            link += " [原始链接](%s) |"%(url)
        else:
            raw_url = "https://raw.githubusercontent.com/%s/%s/%s/%s" % (
                self.repo,
                self.branch,
                base_dir,
                fileName,
            )
            link += " [原始链接](%s) |" % raw_url
        
        for i in range(1, len(self.proxyList)):
            proxy = self.proxyList[i]
            link_name = "加速链接" if len(self.proxyList) == 2 else "加速链接%d" % i
            if raw_url and self._should_use_boki(base_dir, fileName):
                link += " [%s](https://github.boki.moe/%s) |"%(link_name, raw_url)
                continue
            if proxy.rstrip("/").endswith("/gh"):
                link += " [%s](%s/%s@%s/%s/%s) |"%(
                    link_name,
                    proxy,
                    self.repo,
                    self.branch,
                    base_dir,
                    fileName,
                )
            else:
                link += " [%s](%s/https://raw.githubusercontent.com/%s/%s/%s/%s) |"%(
                    link_name,
                    proxy,
                    self.repo,
                    self.branch,
                    base_dir,
                    fileName,
                )
        
        return link
    
    def regenerate(self):
        logger.info("regenerate readme...")
        if os.path.exists(self.filename):
            os.remove(self.filename)
        
        beijing_tz = timezone(timedelta(hours=8))
        update_time = datetime.now(beijing_tz).strftime("%Y/%m/%d %H:%M:%S") + " (UTC+08:00)"
        total_rules, china_rules = self._get_rule_counts()
        china_ratio = self._format_ratio(china_rules, total_rules)
        upstream_raw, upstream_unique, upstream_dedupe_rate = self._get_upstream_stats()
        effective_count, effective_ratio = self._get_effective_stats()
        source_meta = self._load_source_meta()

        with open(self.filename, 'a') as f:
            f.write("# AdBlock DNS Filters Modified\n")
            f.write("[217heidai/adblockfilters](https://github.com/217heidai/adblockfilters) 去广告合并规则增强版，每天更新一次。  \n")
            f.write("\n")
            f.write("| 指标 | 数值 |\n")
            f.write("| :- | :- |\n")
            f.write("| 上次更新（北京时间） | %s |\n" % update_time)
            f.write("| 上游规则总数（去重前） | %s |\n" % (upstream_raw if upstream_raw is not None else "N/A"))
            f.write("| 上游规则总数（去重后） | %s |\n" % (upstream_unique if upstream_unique is not None else "N/A"))
            f.write("| 上游规则去重率 | %s |\n" % (upstream_dedupe_rate if upstream_dedupe_rate is not None else "N/A"))
            f.write("| 有效规则数量（可解析） | %s |\n" % (effective_count if effective_count is not None else "N/A"))
            f.write("| 有效规则占比（检测域名） | %s |\n" % (effective_ratio if effective_ratio is not None else "N/A"))
            f.write("| 中国规则数（Lite） | %s |\n" % (china_rules if china_rules is not None else "N/A"))
            f.write("| 中国规则占比（Lite/成品） | %s |\n" % (china_ratio if china_ratio is not None else "N/A"))
            f.write("\n")

            f.write("## 说明\n")
            f.write("1. 定时从上游各规则源获取更新，合并去重。\n")
            f.write("2. 工作流程：拉取上游规则 → 解析提取域名/规则 → 使用本地 SmartDNS 验证连通性并剔除失效域名（上游规则中存在大量无法解析的域名）→ 生成各类成品规则与统计。\n")
            f.write("3. 上游规则源增删方法：维护 README 中“上游规则源”表格的规则名/类型/链接，工作流会按表格自动拉取并参与生成。\n")
            f.write("4. 本地新增拦截/白名单：在 `sources/local/myblock.txt` 添加自定义拦截域名/规则；在 `sources/local/white2.txt` 添加放行域名或 `@@||domain^` 形式白名单规则，支持 `+.example.com`（主域+子域）/`*.example.com`（仅子域）语法，工作流会自动合并生效。\n")
            f.write("5. 本项目仅对上游规则进行合并、去重、去除无效域名，不做任何修改。如发现误拦截情况，可在 `sources/local/white2.txt` 中自行添加白名单（支持 `+.example.com`/`*.example.com` 语法），或临时添加放行规则（如 `@@||www.example.com^$important`），并向上游规则反馈。\n")
            f.write("\n")
            f.write("性能说明：实测在 J4125 或同级别性能的 x86 主机上，百万级规则规模对 dnsmasq/AdGuard Home 的解析耗时影响不超过 1ms，可放心使用。\n")
            f.write("\n")

            f.write("## 相比原版 adblockfilters 的改进与新增\n")
            f.write("1. 改进了处理逻辑，缩短工作流运行时间。\n")
            f.write("2. 每次生成规则前均验证中国规则和无效规则；仅在 DNS 暂时失败时沿用上一版分类，避免网络波动污染结果。\n")
            f.write("3. 白名单自动同步上游仓库，并支持 `sources/local/white2.txt` 本地补充合并。\n")
            f.write("4. 域名提取与规则解析更完善，覆盖更多 filter/dns/host 规则格式，减少漏提取。\n")
            f.write("5. 新增/独有规则源（相对上游仓库，详见下表）：\n")
            f.write("<details>\n")
            f.write("<summary>点击展开/收起新增与独有规则源列表</summary>\n\n")
            unique_rules = self._get_unique_rule_names()
            if unique_rules is None:
                f.write("- （暂时无法获取上游 README，自动对比未完成）\n")
            elif not unique_rules:
                f.write("- （无）\n")
            else:
                for name in unique_rules:
                    f.write("- %s\n" % name)
            f.write("\n</details>\n")
            f.write("\n")

            f.write("## 订阅链接\n")
            f.write("1. 规则x’为规则x的 Lite 版，仅针对国内域名拦截，体积较小（如添加完整规则报错数量限制，请尝试 Lite 规则）\n")
            f.write("2. 默认使用 testingcf.jsdelivr.net CDN，加速大文件会自动切换至 github.boki.moe\n")
            f.write("3. AdGuard 等浏览器插件使用规则1 + 规则2（规则2为规则1的补充，仅适用浏览器插件）\n")
            f.write("\n")
            tmp = "| 规则 | 原始链接 |"
            for i in range(1, len(self.proxyList)):
                if len(self.proxyList) == 2:  # Only one CDN
                    tmp += " 加速链接 |"
                else:
                    tmp += " 加速链接%d |"%(i)
            tmp += " 文件体积(MB) | 规则数量 | 适配说明 |\n"
            f.write(tmp)
            tmp = "| " + ":- | " * ( 1 + len(self.proxyList) + 3) + "\n"
            f.write(tmp)
            f.write("| 规则1 |" + self.__subscribeLink("adblockdns.txt") + " %s | %s | AdGuard、AdGuard Home 等 |\n" % (self._get_product_size_mb("adblockdns.txt") or "N/A", self._get_product_count("adblockdns.txt") or "N/A"))
            f.write("| 规则1' |" + self.__subscribeLink("adblockdnslite.txt") + " %s | %s | AdGuard、AdGuard Home 等 |\n" % (self._get_product_size_mb("adblockdnslite.txt") or "N/A", self._get_product_count("adblockdnslite.txt") or "N/A"))
            f.write("| 规则2 |" + self.__subscribeLink("adblockfilters.txt") + " %s | %s | AdGuard 等 |\n" % (self._get_product_size_mb("adblockfilters.txt") or "N/A", self._get_product_count("adblockfilters.txt") or "N/A"))
            f.write("| 规则2' |" + self.__subscribeLink("adblockfilterslite.txt") + " %s | %s | AdGuard 等 |\n" % (self._get_product_size_mb("adblockfilterslite.txt") or "N/A", self._get_product_count("adblockfilterslite.txt") or "N/A"))
            f.write("| 规则3 |" + self.__subscribeLink("adblockdomain.txt") + " %s | %s | InviZible Pro、personalDNSfilter |\n" % (self._get_product_size_mb("adblockdomain.txt") or "N/A", self._get_product_count("adblockdomain.txt") or "N/A"))
            f.write("| 规则3' |" + self.__subscribeLink("adblockdomainlite.txt") + " %s | %s | InviZible Pro、personalDNSfilter |\n" % (self._get_product_size_mb("adblockdomainlite.txt") or "N/A", self._get_product_count("adblockdomainlite.txt") or "N/A"))
            f.write("| 规则4 |" + self.__subscribeLink("adblockdnsmasq.txt") + " %s | %s | DNSMasq conf |\n" % (self._get_product_size_mb("adblockdnsmasq.txt") or "N/A", self._get_product_count("adblockdnsmasq.txt") or "N/A"))
            f.write("| 规则4' |" + self.__subscribeLink("adblockdnsmasqlite.txt") + " %s | %s | DNSMasq conf |\n" % (self._get_product_size_mb("adblockdnsmasqlite.txt") or "N/A", self._get_product_count("adblockdnsmasqlite.txt") or "N/A"))
            f.write("| 规则5 |" + self.__subscribeLink("adblocksmartdns.conf") + " %s | %s | SmartDNS |\n" % (self._get_product_size_mb("adblocksmartdns.conf") or "N/A", self._get_product_count("adblocksmartdns.conf") or "N/A"))
            f.write("| 规则5' |" + self.__subscribeLink("adblocksmartdnslite.conf") + " %s | %s | SmartDNS |\n" % (self._get_product_size_mb("adblocksmartdnslite.conf") or "N/A", self._get_product_count("adblocksmartdnslite.conf") or "N/A"))
            f.write("| 规则6 |" + self.__subscribeLink("adblockclash.list") + " %s | %s | Shadowrocket |\n" % (self._get_product_size_mb("adblockclash.list") or "N/A", self._get_product_count("adblockclash.list") or "N/A"))
            f.write("| 规则6' |" + self.__subscribeLink("adblockclashlite.list") + " %s | %s | Shadowrocket |\n" % (self._get_product_size_mb("adblockclashlite.list") or "N/A", self._get_product_count("adblockclashlite.list") or "N/A"))
            f.write("| 规则7 |" + self.__subscribeLink("adblockqx.conf") + " %s | %s | QuantumultX |\n" % (self._get_product_size_mb("adblockqx.conf") or "N/A", self._get_product_count("adblockqx.conf") or "N/A"))
            f.write("| 规则7' |" + self.__subscribeLink("adblockqxlite.conf") + " %s | %s | QuantumultX |\n" % (self._get_product_size_mb("adblockqxlite.conf") or "N/A", self._get_product_count("adblockqxlite.conf") or "N/A"))
            f.write("| 规则8 |" + self.__subscribeLink("adblockmihomo.yaml") + " %s | %s | Clash Meta(Mihomo) yaml |\n" % (self._get_product_size_mb("adblockmihomo.yaml") or "N/A", self._get_product_count("adblockmihomo.yaml") or "N/A"))
            f.write("| 规则8' |" + self.__subscribeLink("adblockmihomolite.yaml") + " %s | %s | Clash Meta(Mihomo) yaml |\n" % (self._get_product_size_mb("adblockmihomolite.yaml") or "N/A", self._get_product_count("adblockmihomolite.yaml") or "N/A"))
            f.write("| 规则9 |" + self.__subscribeLink("adblockmihomo.mrs") + " %s | %s | Clash Meta(Mihomo) mrs |\n" % (self._get_product_size_mb("adblockmihomo.mrs") or "N/A", self._get_product_count("adblockmihomo.mrs") or "N/A"))
            f.write("| 规则9' |" + self.__subscribeLink("adblockmihomolite.mrs") + " %s | %s | Clash Meta(Mihomo) mrs |\n" % (self._get_product_size_mb("adblockmihomolite.mrs") or "N/A", self._get_product_count("adblockmihomolite.mrs") or "N/A"))
            f.write("| 规则10 |" + self.__subscribeLink("adblockhosts.txt") + " %s | %s | Hosts |\n" % (self._get_product_size_mb("adblockhosts.txt") or "N/A", self._get_product_count("adblockhosts.txt") or "N/A"))
            f.write("| 规则10' |" + self.__subscribeLink("adblockhostslite.txt") + " %s | %s | Hosts |\n" % (self._get_product_size_mb("adblockhostslite.txt") or "N/A", self._get_product_count("adblockhostslite.txt") or "N/A"))
            f.write("| 规则11 |" + self.__subscribeLink("adblocksingbox.json") + " %s | %s | sing-box 1.12.x json |\n" % (self._get_product_size_mb("adblocksingbox.json") or "N/A", self._get_product_count("adblocksingbox.json") or "N/A"))
            f.write("| 规则11' |" + self.__subscribeLink("adblocksingboxlite.json") + " %s | %s | sing-box 1.12.x json |\n" % (self._get_product_size_mb("adblocksingboxlite.json") or "N/A", self._get_product_count("adblocksingboxlite.json") or "N/A"))
            f.write("| 规则12 |" + self.__subscribeLink("adblocksingbox.srs") + " %s | %s | sing-box 1.12.x srs |\n" % (self._get_product_size_mb("adblocksingbox.srs") or "N/A", self._get_product_count("adblocksingbox.srs") or "N/A"))
            f.write("| 规则12' |" + self.__subscribeLink("adblocksingboxlite.srs") + " %s | %s | sing-box 1.12.x srs |\n" % (self._get_product_size_mb("adblocksingboxlite.srs") or "N/A", self._get_product_count("adblocksingboxlite.srs") or "N/A"))
            f.write("| 规则13 |" + self.__subscribeLink("adblockloon.list") + " %s | %s | Loon |\n" % (self._get_product_size_mb("adblockloon.list") or "N/A", self._get_product_count("adblockloon.list") or "N/A"))
            f.write("| 规则13' |" + self.__subscribeLink("adblockloonlite.list") + " %s | %s | Loon |\n" % (self._get_product_size_mb("adblockloonlite.list") or "N/A", self._get_product_count("adblockloonlite.list") or "N/A"))
            f.write("| 规则14 |" + self.__subscribeLink("adblocksurge.list") + " %s | %s | Surge |\n" % (self._get_product_size_mb("adblocksurge.list") or "N/A", self._get_product_count("adblocksurge.list") or "N/A"))
            f.write("| 规则14' |" + self.__subscribeLink("adblocksurgelite.list") + " %s | %s | Surge |\n" % (self._get_product_size_mb("adblocksurgelite.list") or "N/A", self._get_product_count("adblocksurgelite.list") or "N/A"))
            f.write("| 规则15 |" + self.__subscribeLink("adblockmosdns.txt") + " %s | %s | MosDNS v5 |\n" % (self._get_product_size_mb("adblockmosdns.txt") or "N/A", self._get_product_count("adblockmosdns.txt") or "N/A"))
            f.write("| 规则15' |" + self.__subscribeLink("adblockmosdnslite.txt") + " %s | %s | MosDNS v5 |\n" % (self._get_product_size_mb("adblockmosdnslite.txt") or "N/A", self._get_product_count("adblockmosdnslite.txt") or "N/A"))
            f.write("| 规则16 |" + self.__subscribeLink("adblocksurgeruleset.list") + " %s | %s | Surge RULE-SET |\n" % (self._get_product_size_mb("adblocksurgeruleset.list") or "N/A", self._get_product_count("adblocksurgeruleset.list") or "N/A"))
            f.write("| 规则16' |" + self.__subscribeLink("adblocksurgerulesetlite.list") + " %s | %s | Surge RULE-SET |\n" % (self._get_product_size_mb("adblocksurgerulesetlite.list") or "N/A", self._get_product_count("adblocksurgerulesetlite.list") or "N/A"))
            f.write("| 规则17 |" + self.__subscribeLink("adblockclashclassical.yaml") + " %s | %s | Clash Classical yaml |\n" % (self._get_product_size_mb("adblockclashclassical.yaml") or "N/A", self._get_product_count("adblockclashclassical.yaml") or "N/A"))
            f.write("| 规则17' |" + self.__subscribeLink("adblockclashclassicallite.yaml") + " %s | %s | Clash Classical yaml |\n" % (self._get_product_size_mb("adblockclashclassicallite.yaml") or "N/A", self._get_product_count("adblockclashclassicallite.yaml") or "N/A"))
            f.write("| 规则18 |" + self.__subscribeLink("adblockrouteros.txt") + " %s | %s | RouterOS |\n" % (self._get_product_size_mb("adblockrouteros.txt") or "N/A", self._get_product_count("adblockrouteros.txt") or "N/A"))
            f.write("| 规则18' |" + self.__subscribeLink("adblockrouteroslite.txt") + " %s | %s | RouterOS |\n" % (self._get_product_size_mb("adblockrouteroslite.txt") or "N/A", self._get_product_count("adblockrouteroslite.txt") or "N/A"))
            f.write("| 规则19 |" + self.__subscribeLink("adblockrouterosadlist.txt") + " %s | %s | RouterOS AdList |\n" % (self._get_product_size_mb("adblockrouterosadlist.txt") or "N/A", self._get_product_count("adblockrouterosadlist.txt") or "N/A"))
            f.write("| 规则19' |" + self.__subscribeLink("adblockrouterosadlistlite.txt") + " %s | %s | RouterOS AdList |\n" % (self._get_product_size_mb("adblockrouterosadlistlite.txt") or "N/A", self._get_product_count("adblockrouterosadlistlite.txt") or "N/A"))
            f.write("| 规则20 |" + self.__subscribeLink("adblockdnsmasqaddnhosts.txt") + " %s | %s | DNSMasq addn-hosts |\n" % (self._get_product_size_mb("adblockdnsmasqaddnhosts.txt") or "N/A", self._get_product_count("adblockdnsmasqaddnhosts.txt") or "N/A"))
            f.write("| 规则20' |" + self.__subscribeLink("adblockdnsmasqaddnhostslite.txt") + " %s | %s | DNSMasq addn-hosts |\n" % (self._get_product_size_mb("adblockdnsmasqaddnhostslite.txt") or "N/A", self._get_product_count("adblockdnsmasqaddnhostslite.txt") or "N/A"))
            f.write("| 规则21 |" + self.__subscribeLink("adblockdnsmasqservers.txt") + " %s | %s | DNSMasq servers |\n" % (self._get_product_size_mb("adblockdnsmasqservers.txt") or "N/A", self._get_product_count("adblockdnsmasqservers.txt") or "N/A"))
            f.write("| 规则21' |" + self.__subscribeLink("adblockdnsmasqserverslite.txt") + " %s | %s | DNSMasq servers |\n" % (self._get_product_size_mb("adblockdnsmasqserverslite.txt") or "N/A", self._get_product_count("adblockdnsmasqserverslite.txt") or "N/A"))
            f.write("\n")

            f.write("## 上游规则源\n")
            f.write("1. 感谢各位广告过滤规则维护大佬们的辛苦付出。\n")
            f.write("\n")

            tmp = "| 规则 | 类型 | 原始链接 |"
            for i in range(1, len(self.proxyList)):
                if len(self.proxyList) == 2:  # Only one CDN
                    tmp += " 加速链接 |"
                else:
                    tmp += " 加速链接%d |"%(i)
            tmp += " 规则数量 | 更新日期 |\n"
            f.write(tmp)
            tmp = "| " + ":- | " * ( 2 + len(self.proxyList) + 2) + "\n"
            f.write(tmp)
            for rule in self.ruleList:
                count = self._get_source_count(rule, source_meta)
                count_text = str(count) if count is not None else "N/A"
                f.write("| %s | %s |%s %s | %s |\n" % (
                    rule.name,
                    rule.type,
                    self.__subscribeLink(rule.filename, rule.url, base_dir="sources/upstream"),
                    count_text,
                    rule.latest,
                ))
            f.write("\n")
            
            f.write("## Star History\n")
            f.write('<a href="https://www.star-history.com/#%s&Date">\n' % self.repo)
            f.write(' <picture>\n')
            f.write('   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=%s&type=Date&theme=dark" />\n' % self.repo)
            f.write('   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=%s&type=Date" />\n' % self.repo)
            f.write('   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=%s&type=Date" />\n' % self.repo)
            f.write(' </picture>\n')
            f.write('</a>\n')
            '''

            '''

    def _get_rule_counts(self):
        base_dir = os.path.dirname(self.filename)
        total_path = os.path.join(base_dir, "rules", "adblockfilters.txt")
        china_path = os.path.join(base_dir, "rules", "adblockfilterslite.txt")
        total_rules = self._read_blocked_filters(total_path)
        china_rules = self._read_blocked_filters(china_path)
        return total_rules, china_rules

    def _read_blocked_filters(self, path: str):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("! Blocked Filters:"):
                        value = line.split(":", 1)[1].strip()
                        if value.isdigit():
                            return int(value)
                        break
        except Exception:
            return None

        return self._count_rule_lines(path)

    def _count_rule_lines(self, path: str):
        try:
            count = 0
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith(("!", "#")):
                        continue
                    count += 1
            return count
        except Exception:
            return None

    def _count_yaml_payload(self, path: str):
        try:
            count = 0
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("-"):
                        count += 1
            return count
        except Exception:
            return None

    def _count_singbox_json(self, path: str):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            total = 0
            for rule in data.get("rules", []):
                if not isinstance(rule, dict):
                    continue
                for _, value in rule.items():
                    if isinstance(value, list):
                        total += len(value)
            return total
        except Exception:
            return self._count_rule_lines(path)

    def _map_binary_product(self, file_name: str) -> str:
        lower = file_name.lower()
        if lower.endswith(".mrs"):
            return file_name[:-4] + ".yaml"
        if lower.endswith(".srs"):
            return file_name[:-4] + ".json"
        return file_name

    def _format_ratio(self, numerator, denominator):
        if numerator is None or denominator is None or denominator == 0:
            return None
        return "{:.2%}".format(numerator / denominator)

    def _get_upstream_stats(self):
        base_dir = os.path.dirname(self.filename)
        upstream_dir = os.path.join(base_dir, "sources", "upstream")
        raw_count = 0
        unique_rules = set()
        if not self.ruleList:
            return None, None, None
        for rule in self.ruleList:
            path = os.path.join(upstream_dir, rule.filename)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith(("#", "!")):
                            continue
                        raw_count += 1
                        unique_rules.add(line)
            except Exception:
                continue
        unique_count = len(unique_rules) if raw_count else 0
        dedupe_rate = self._format_ratio(raw_count - unique_count, raw_count)
        return raw_count, unique_count, dedupe_rate

    def _get_effective_stats(self):
        base_dir = os.path.dirname(self.filename)
        build_dir = os.path.join(base_dir, "build")
        invalid_path = os.path.join(build_dir, "black.txt")
        domain_path = os.path.join(build_dir, "domain.txt")
        invalid_count = self._count_non_empty_lines(invalid_path)
        domain_count = self._count_non_empty_lines(domain_path)
        if invalid_count is None or domain_count is None:
            return None, None
        effective_count = max(domain_count - invalid_count, 0)
        effective_ratio = self._format_ratio(effective_count, domain_count)
        return effective_count, effective_ratio

    def _get_product_size_mb(self, file_name: str):
        base_dir = os.path.dirname(self.filename)
        path = os.path.join(base_dir, "rules", file_name)
        try:
            size_bytes = os.path.getsize(path)
        except Exception:
            return None
        return "{:.2f}".format(size_bytes / (1024 * 1024))

    def _get_product_count(self, file_name: str):
        base_dir = os.path.dirname(self.filename)
        mapped_name = self._map_binary_product(file_name)
        path = os.path.join(base_dir, "rules", mapped_name)
        ext = os.path.splitext(mapped_name)[1].lower()
        if ext == ".yaml":
            return self._count_yaml_payload(path)
        if ext == ".json":
            return self._count_singbox_json(path)
        return self._read_blocked_filters(path)

    def _load_source_meta(self) -> dict:
        base_dir = os.path.dirname(self.filename)
        meta_path = os.path.join(base_dir, "sources", "upstream", ".source_meta.json")
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _count_non_empty_lines(self, path: str) -> int:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                count = 0
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(("#", "!")):
                        continue
                    count += 1
                return count
        except Exception:
            return 0

    def _get_source_count(self, rule: Rule, meta: dict):
        if meta:
            entry = meta.get(rule.filename)
            if isinstance(entry, dict):
                lines = entry.get("lines")
                if isinstance(lines, int):
                    return lines
        base_dir = os.path.dirname(self.filename)
        source_path = os.path.join(base_dir, "sources", "upstream", rule.filename)
        if os.path.exists(source_path):
            return self._count_non_empty_lines(source_path)
        return None

    def _fetch_text(self, url: str, timeout: int = 20) -> str:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def _extract_section(self, text: str, header: str) -> str:
        if not text:
            return ""
        start = text.find(header)
        if start < 0:
            return ""
        rest = text[start + len(header):]
        next_idx = rest.find("\n## ")
        if next_idx >= 0:
            return rest[:next_idx]
        return rest

    def _parse_rule_names_from_section(self, section: str) -> List[str]:
        names = []
        if not section:
            return names
        for line in section.splitlines():
            line = line.strip()
            if not (line.startswith("|") and line.endswith("|")):
                continue
            parts = [p.strip() for p in line[1:-1].split("|")]
            if len(parts) < 3:
                continue
            if parts[0] in ("规则", "Rule"):
                continue
            if "[原始链接]" not in parts[2]:
                continue
            names.append(parts[0])
        return names

    def _get_upstream_rule_names(self):
        if not self.upstream_repo:
            return None
        url = "https://raw.githubusercontent.com/%s/%s/README.md" % (
            self.upstream_repo,
            self.upstream_branch,
        )
        text = self._fetch_text(url)
        if not text:
            return None
        section = self._extract_section(text, "## 上游规则源")
        names = self._parse_rule_names_from_section(section)
        return set(name.strip() for name in names if name.strip())

    def _get_unique_rule_names(self):
        if not self.ruleList:
            return []
        upstream_names = self._get_upstream_rule_names()
        if upstream_names is None:
            return None
        current_names = {rule.name.strip() for rule in self.ruleList if rule.name.strip()}
        unique_names = sorted(current_names - upstream_names)
        return unique_names

    def _resolve_repo(self) -> str:
        repo = os.environ.get("GITHUB_REPOSITORY")
        if repo:
            return repo.strip()

        url = self._get_git_origin_url()
        repo = self._parse_repo_from_url(url)
        if repo:
            return repo

        return ""

    def _resolve_branch(self) -> str:
        ref = os.environ.get("GITHUB_REF", "")
        if ref.startswith("refs/heads/"):
            return ref[len("refs/heads/"):].strip()

        for key in ("GITHUB_REF_NAME", "GITHUB_HEAD_REF", "GITHUB_BASE_REF"):
            value = os.environ.get(key)
            if value:
                return value.strip()

        try:
            output = subprocess.check_output(
                ["git", "remote", "show", "origin"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            match = re.search(r"HEAD branch: (.+)", output)
            if match:
                return match.group(1).strip()
        except Exception:
            pass

        return "main"

    def _get_git_origin_url(self) -> str:
        try:
            return subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except Exception:
            return ""

    def _parse_repo_from_url(self, url: str) -> str:
        if not url:
            return ""
        url = url.strip()
        if url.endswith(".git"):
            url = url[:-4]
        match = re.search(r"github\\.com[:/](?P<repo>[^/]+/[^/]+)$", url)
        if match:
            return match.group("repo")
        return ""

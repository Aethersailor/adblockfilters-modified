# AdBlock DNS Filters Modified
[217heidai/adblockfilters](https://github.com/217heidai/adblockfilters) 去广告合并规则增强版，每天更新一次。  

| 指标 | 数值 |
| :- | :- |
| 上次更新（北京时间） | 2026/03/28 13:37:46 (UTC+08:00) |
| 上游规则总数（去重前） | 3830640 |
| 上游规则总数（去重后） | 2521165 |
| 上游规则去重率 | 34.18% |
| 有效规则数量（可解析） | 1542228 |
| 有效规则占比（检测域名） | 79.40% |
| 中国规则数（Lite） | 12388 |
| 中国规则占比（Lite/成品） | 4.89% |

## 说明
1. 定时从上游各规则源获取更新，合并去重。
2. 工作流程：拉取上游规则 → 解析提取域名/规则 → 使用本地 SmartDNS 验证连通性并剔除失效域名（上游规则中存在大量无法解析的域名）→ 生成各类成品规则与统计。
3. 上游规则源增删方法：维护 README 中“上游规则源”表格的规则名/类型/链接，工作流会按表格自动拉取并参与生成。
4. 本地新增拦截/白名单：在 `sources/local/myblock.txt` 添加自定义拦截域名/规则；在 `sources/local/white2.txt` 添加放行域名或 `@@||domain^` 形式白名单规则，支持 `+.example.com`（主域+子域）/`*.example.com`（仅子域）语法，工作流会自动合并生效。
5. 本项目仅对上游规则进行合并、去重、去除无效域名，不做任何修改。如发现误拦截情况，可在 `sources/local/white2.txt` 中自行添加白名单（支持 `+.example.com`/`*.example.com` 语法），或临时添加放行规则（如 `@@||www.example.com^$important`），并向上游规则反馈。

性能说明：实测在 J4125 或同级别性能的 x86 主机上，百万级规则规模对 dnsmasq/AdGuard Home 的解析耗时影响不超过 1ms，可放心使用。

## 相比原版 adblockfilters 的改进与新增
1. 改进了处理逻辑，缩短工作流运行时间。
2. 改进了中国规则和无效规则的处理流程，现在每次生成规则前均会对这两类规则进行验证，不再使用历史数据。
3. 白名单自动同步上游仓库，并支持 `sources/local/white2.txt` 本地补充合并。
4. 域名提取与规则解析更完善，覆盖更多 filter/dns/host 规则格式，减少漏提取。
5. 新增/独有规则源（相对上游仓库，详见下表）：
<details>
<summary>点击展开/收起新增与独有规则源列表</summary>

- AdGuard Annoyances
- AdGuard Tracking Protection
- CERT.PL's Warning List
- HaGeZi's Apple Tracker Blocklist
- HaGeZi's Badware Hoster Blocklist
- HaGeZi's Gambling Blocklist
- HaGeZi's OPPO & Realme Tracker Blocklist
- HaGeZi's Samsung Tracker Blocklist
- HaGeZi's Threat Intelligence Feeds
- HaGeZi's Vivo Tracker Blocklist
- HaGeZi's Windows/Office Tracker Blocklist
- HaGeZi's Xiaomi Tracker Blocklist
- HageziMultiPro
- Malicious URL Blocklist
- OISD Big
- Online Malicious URL Blocklist
- PeterLowe
- Phishing URL Blocklist
- Scam Blocklist
- SmartTV
- Stalkerware
- anti-AD
- lingeringsound adblock_auto
- uBlock Ads
- uBlock Badware risks
- uBlock Privacy

</details>

## 订阅链接
1. 规则x’为规则x的 Lite 版，仅针对国内域名拦截，体积较小（如添加完整规则报错数量限制，请尝试 Lite 规则）
2. 默认使用 testingcf.jsdelivr.net CDN，加速大文件会自动切换至 github.boki.moe
3. AdGuard 等浏览器插件使用规则1 + 规则2（规则2为规则1的补充，仅适用浏览器插件）

| 规则 | 原始链接 | 加速链接 | 文件体积(MB) | 规则数量 | 适配说明 |
| :- | :- | :- | :- | :- | :- | 
| 规则1 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdns.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdns.txt) | 25.32 | 1231153 | AdGuard、AdGuard Home 等 |
| 规则1' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnslite.txt) | 0.62 | 35226 | AdGuard、AdGuard Home 等 |
| 规则2 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockfilters.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockfilters.txt) | 12.99 | 253249 | AdGuard 等 |
| 规则2' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockfilterslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockfilterslite.txt) | 0.55 | 12388 | AdGuard 等 |
| 规则3 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdomain.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdomain.txt) | 21.80 | 1231002 | InviZible Pro、personalDNSfilter |
| 规则3' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdomainlite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdomainlite.txt) | 0.51 | 35180 | InviZible Pro、personalDNSfilter |
| 规则4 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasq.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasq.txt) | 31.19 | 1231002 | DNSMasq conf |
| 规则4' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqlite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnsmasqlite.txt) | 0.78 | 35180 | DNSMasq conf |
| 规则5 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksmartdns.conf) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksmartdns.conf) | 34.72 | 1231153 | SmartDNS |
| 规则5' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksmartdnslite.conf) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksmartdnslite.conf) | 0.88 | 35226 | SmartDNS |
| 规则6 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclash.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclash.list) | 52.32 | 1231003 | Shadowrocket |
| 规则6' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashlite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockclashlite.list) | 1.39 | 35181 | Shadowrocket |
| 规则7 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockqx.conf) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockqx.conf) | 44.10 | 1231002 | QuantumultX |
| 规则7' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockqxlite.conf) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockqxlite.conf) | 1.15 | 35180 | QuantumultX |
| 规则8 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomo.yaml) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomo.yaml) | 31.19 | 1231002 | Clash Meta(Mihomo) yaml |
| 规则8' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomolite.yaml) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmihomolite.yaml) | 0.78 | 35180 | Clash Meta(Mihomo) yaml |
| 规则9 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomo.mrs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmihomo.mrs) | 7.43 | 1231002 | Clash Meta(Mihomo) mrs |
| 规则9' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomolite.mrs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmihomolite.mrs) | 0.17 | 35180 | Clash Meta(Mihomo) mrs |
| 规则10 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockhosts.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockhosts.txt) | 31.19 | 1231016 | Hosts |
| 规则10' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockhostslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockhostslite.txt) | 0.78 | 35194 | Hosts |
| 规则11 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingbox.json) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingbox.json) | 34.71 | 1231002 | sing-box 1.12.x json |
| 规则11' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingboxlite.json) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksingboxlite.json) | 0.88 | 35180 | sing-box 1.12.x json |
| 规则12 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingbox.srs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksingbox.srs) | 6.55 | 1231002 | sing-box 1.12.x srs |
| 规则12' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingboxlite.srs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksingboxlite.srs) | 0.14 | 35180 | sing-box 1.12.x srs |
| 规则13 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockloon.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockloon.list) | 38.23 | 1231002 | Loon |
| 规则13' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockloonlite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockloonlite.list) | 0.98 | 35180 | Loon |
| 规则14 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurge.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurge.list) | 22.97 | 1231002 | Surge |
| 规则14' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgelite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksurgelite.list) | 0.55 | 35180 | Surge |
| 规则15 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmosdns.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmosdns.txt) | 27.67 | 1231002 | MosDNS v5 |
| 规则15' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmosdnslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmosdnslite.txt) | 0.68 | 35180 | MosDNS v5 |
| 规则16 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgeruleset.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgeruleset.list) | 30.02 | 1231002 | Surge RULE-SET |
| 规则16' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgerulesetlite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksurgerulesetlite.list) | 0.75 | 35180 | Surge RULE-SET |
| 规则17 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashclassical.yaml) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashclassical.yaml) | 34.71 | 1231002 | Clash Classical yaml |
| 规则17' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashclassicallite.yaml) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockclashclassicallite.yaml) | 0.88 | 35180 | Clash Classical yaml |
| 规则18 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouteros.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouteros.txt) | 94.99 | 1776436 | RouterOS |
| 规则18' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouteroslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockrouteroslite.txt) | 3.54 | 70360 | RouterOS |
| 规则19 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouterosadlist.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouterosadlist.txt) | 56.51 | 2462006 | RouterOS AdList |
| 规则19' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouterosadlistlite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockrouterosadlistlite.txt) | 1.40 | 70362 | RouterOS AdList |
| 规则20 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqaddnhosts.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqaddnhosts.txt) | 31.19 | 1231002 | DNSMasq addn-hosts |
| 规则20' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqaddnhostslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnsmasqaddnhostslite.txt) | 0.78 | 35180 | DNSMasq addn-hosts |
| 规则21 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqservers.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqservers.txt) | 32.36 | 1231002 | DNSMasq servers |
| 规则21' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqserverslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnsmasqserverslite.txt) | 0.82 | 35180 | DNSMasq servers |

## 上游规则源
1. 感谢各位广告过滤规则维护大佬们的辛苦付出。

| 规则 | 类型 | 原始链接 | 加速链接 | 规则数量 | 更新日期 |
| :- | :- | :- | :- | :- | :- | 
| AdGuard Base filter | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_2_Base/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Base_filter.txt) | 167857 | 2026/03/28 |
| AdGuard Chinese filter | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_224_Chinese/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Chinese_filter.txt) | 23078 | 2026/03/28 |
| AdGuard Mobile Ads filter | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Mobile_Ads_filter.txt) | 1027 | 2026/03/24 |
| AdGuard DNS filter | dns | [原始链接](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_DNS_filter.txt) | 164153 | 2026/03/28 |
| AdRules DNS List | dns | [原始链接](https://raw.githubusercontent.com/Cats-Team/AdRules/main/dns.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdRules_DNS_List.txt) | 181066 | 2026/03/28 |
| CJX's Annoyance List | filter | [原始链接](https://raw.githubusercontent.com/cjx82630/cjxlist/master/cjx-annoyance.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/CJX's_Annoyance_List.txt) | 1861 | 2026/03/11 |
| EasyList | filter | [原始链接](https://easylist-downloads.adblockplus.org/easylist.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/EasyList.txt) | 90550 | 2026/03/28 |
| EasyList China | filter | [原始链接](https://easylist-downloads.adblockplus.org/easylistchina.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/EasyList_China.txt) | 19307 | 2026/03/28 |
| EasyPrivacy | filter | [原始链接](https://easylist-downloads.adblockplus.org/easyprivacy.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/EasyPrivacy.txt) | 53738 | 2026/03/28 |
| xinggsf mv | filter | [原始链接](https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/mv.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/xinggsf_mv.txt) | 135 | 2025/12/25 |
| jiekouAD | filter | [原始链接](https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/jiekouAD.txt) | 5815 | 2026/03/25 |
| AWAvenue Ads Rule | dns | [原始链接](https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AWAvenue_Ads_Rule.txt) | 917 | 2026/02/11 |
| DNS-Blocklists Light | dns | [原始链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/light.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/DNS-Blocklists_Light.txt) | 63977 | 2026/03/28 |
| Hblock | dns | [原始链接](https://hblock.molinero.dev/hosts_adblock.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Hblock.txt) | 473010 | 2026/03/28 |
| OISD Basic | dns | [原始链接](https://abp.oisd.nl/basic/) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/OISD_Basic.txt) | 52097 | 2026/03/28 |
| StevenBlack hosts | host | [原始链接](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/StevenBlack_hosts.txt) | 91685 | 2026/03/26 |
| Pollock hosts | host | [原始链接](https://someonewhocares.org/hosts/hosts) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Pollock_hosts.txt) | 12739 | 2026/03/28 |
| anti-AD | filter | [原始链接](https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-easylist.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/anti-AD.txt) | 100617 | 2026/03/26 |
| Phishing URL Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_30.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Phishing_URL_Blocklist.txt) | 24160 | 2026/03/28 |
| Malicious URL Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_11.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Malicious_URL_Blocklist.txt) | 7239 | 2026/03/28 |
| Online Malicious URL Blocklist | filter | [原始链接](https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-agh-online.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Online_Malicious_URL_Blocklist.txt) | 2313 | 2026/03/28 |
| PeterLowe | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/general/filter_3_PeterLoweFilter/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/PeterLowe.txt) | 3522 | 2026/03/28 |
| SmartTV | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/other/filter_7_SmartTVBlocklist/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/SmartTV.txt) | 159 | 2025/11/29 |
| HageziMultiPro | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/general/filter_48_HageziMultiPro/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HageziMultiPro.txt) | 180270 | 2026/03/28 |
| HaGeZi's Apple Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_67.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Apple_Tracker_Blocklist.txt) | 108 | 2026/01/12 |
| HaGeZi's Badware Hoster Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_55.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Badware_Hoster_Blocklist.txt) | 1256 | 2026/03/24 |
| HaGeZi's Windows/Office Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_63.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Windows_Office_Tracker_Blocklist.txt) | 393 | 2026/03/28 |
| HaGeZi's Xiaomi Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_60.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Xiaomi_Tracker_Blocklist.txt) | 362 | 2026/03/25 |
| HaGeZi's Vivo Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_65.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Vivo_Tracker_Blocklist.txt) | 250 | 2026/03/28 |
| HaGeZi's Samsung Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_61.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Samsung_Tracker_Blocklist.txt) | 207 | 2026/03/21 |
| HaGeZi's OPPO & Realme Tracker Blocklist | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/other/filter_66_HageziOppoRealmeTrackerBlocklist/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_OPPO_&_Realme_Tracker_Blocklist.txt) | 374 | 2026/03/15 |
| HaGeZi's Gambling Blocklist | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/other/filter_47_HageziGamblingBlocklist/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Gambling_Blocklist.txt) | 208395 | 2026/03/28 |
| HaGeZi's Threat Intelligence Feeds | filter | [原始链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/domains/tif.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Threat_Intelligence_Feeds.txt) | 1009541 | 2026/03/28 |
| uBlock Badware risks | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_50.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/uBlock_Badware_risks.txt) | 3104 | 2026/03/28 |
| OISD Big | dns | [原始链接](https://big.oisd.nl) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/OISD_Big.txt) | 338881 | 2026/03/28 |
| Stalkerware | host | [原始链接](https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/refs/heads/master/generated/hosts_full) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Stalkerware.txt) | 983 | 2025/11/29 |
| Scam Blocklist | filter | [原始链接](https://raw.githubusercontent.com/durablenapkin/scamblocklist/refs/heads/master/adguard.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Scam_Blocklist.txt) | 980 | 2026/03/28 |
| uBlock Ads | filter | [原始链接](https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/uBlock_Ads.txt) | 9128 | 2026/03/28 |
| uBlock Privacy | filter | [原始链接](https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/uBlock_Privacy.txt) | 2488 | 2026/03/28 |
| AdGuard Tracking Protection | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_3_Spyware/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Tracking_Protection.txt) | 169528 | 2026/03/28 |
| AdGuard Annoyances | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_14_Annoyances/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Annoyances.txt) | 65295 | 2026/03/28 |
| lingeringsound adblock_auto | filter | [原始链接](https://raw.githubusercontent.com/lingeringsound/adblock_auto/main/Rules/adblock_auto.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/lingeringsound_adblock_auto.txt) | 245622 | 2026/03/28 |
| CERT.PL's Warning List | host | [原始链接](https://hole.cert.pl/domains/v2/domains_hosts.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/CERT.PL's_Warning_List.txt) | 148035 | 2026/03/28 |

## Star History
<a href="https://www.star-history.com/#Aethersailor/adblockfilters-modified&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Aethersailor/adblockfilters-modified&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Aethersailor/adblockfilters-modified&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Aethersailor/adblockfilters-modified&type=Date" />
 </picture>
</a>

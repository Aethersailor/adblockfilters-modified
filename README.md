> [!CAUTION]
> **本项目的 Workflow 曾触发 GitHub Actions 的滥用检测，导致项目维护者的 GitHub 账号被封禁，因此本项目停止维护。**  
> **如需继续使用，建议使用 Self-hosted Runner 运行 Workflow。**

> [!CAUTION]
> **The workflow in this project previously triggered GitHub Actions' abuse detection, resulting in the suspension of the maintainer's GitHub account. As a result, this project is no longer maintained.**  
> **If you wish to continue using it, it is recommended to run the workflow on a self-hosted runner.**

# AdBlock DNS Filters Modified
[217heidai/adblockfilters](https://github.com/217heidai/adblockfilters) 去广告合并规则增强版，每天更新一次。  

| 指标 | 数值 |
| :- | :- |
| 上次更新（北京时间） | 2026/06/09 15:51:50 (UTC+08:00) |
| 上游规则总数（去重前） | 4346504 |
| 上游规则总数（去重后） | 3034864 |
| 上游规则去重率 | 30.18% |
| 有效规则数量（可解析） | 1987297 |
| 有效规则占比（检测域名） | 80.41% |
| 中国规则数（Lite） | 13095 |
| 中国规则占比（Lite/成品） | 4.54% |

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
- Hblock
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
| 规则1 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdns.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdns.txt) | 32.60 | 1627650 | AdGuard、AdGuard Home 等 |
| 规则1' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnslite.txt) | 0.72 | 39272 | AdGuard、AdGuard Home 等 |
| 规则2 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockfilters.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockfilters.txt) | 14.30 | 288411 | AdGuard 等 |
| 规则2' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockfilterslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockfilterslite.txt) | 0.60 | 13095 | AdGuard 等 |
| 规则3 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdomain.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdomain.txt) | 27.94 | 1627495 | InviZible Pro、personalDNSfilter |
| 规则3' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdomainlite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdomainlite.txt) | 0.61 | 39226 | InviZible Pro、personalDNSfilter |
| 规则4 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasq.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasq.txt) | 40.36 | 1627495 | DNSMasq conf |
| 规则4' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqlite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnsmasqlite.txt) | 0.91 | 39226 | DNSMasq conf |
| 规则5 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksmartdns.conf) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksmartdns.conf) | 45.02 | 1627650 | SmartDNS |
| 规则5' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksmartdnslite.conf) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksmartdnslite.conf) | 1.02 | 39272 | SmartDNS |
| 规则6 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclash.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclash.list) | 68.29 | 1627496 | Shadowrocket |
| 规则6' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashlite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockclashlite.list) | 1.58 | 39227 | Shadowrocket |
| 规则7 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockqx.conf) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockqx.conf) | 57.43 | 1627495 | QuantumultX |
| 规则7' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockqxlite.conf) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockqxlite.conf) | 1.32 | 39226 | QuantumultX |
| 规则8 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomo.yaml) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomo.yaml) | 40.36 | 1627495 | Clash Meta(Mihomo) yaml |
| 规则8' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomolite.yaml) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmihomolite.yaml) | 0.91 | 39226 | Clash Meta(Mihomo) yaml |
| 规则9 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomo.mrs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmihomo.mrs) | 11.05 | 1627495 | Clash Meta(Mihomo) mrs |
| 规则9' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmihomolite.mrs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmihomolite.mrs) | 0.24 | 39226 | Clash Meta(Mihomo) mrs |
| 规则10 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockhosts.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockhosts.txt) | 40.36 | 1627509 | Hosts |
| 规则10' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockhostslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockhostslite.txt) | 0.91 | 39240 | Hosts |
| 规则11 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingbox.json) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingbox.json) | 45.01 | 1627495 | sing-box 1.12.x json |
| 规则11' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingboxlite.json) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksingboxlite.json) | 1.02 | 39226 | sing-box 1.12.x json |
| 规则12 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingbox.srs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksingbox.srs) | 9.68 | 1627495 | sing-box 1.12.x srs |
| 规则12' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksingboxlite.srs) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksingboxlite.srs) | 0.20 | 39226 | sing-box 1.12.x srs |
| 规则13 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockloon.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockloon.list) | 49.67 | 1627495 | Loon |
| 规则13' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockloonlite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockloonlite.list) | 1.13 | 39226 | Loon |
| 规则14 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurge.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurge.list) | 29.49 | 1627495 | Surge |
| 规则14' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgelite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksurgelite.list) | 0.65 | 39226 | Surge |
| 规则15 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmosdns.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmosdns.txt) | 35.70 | 1627495 | MosDNS v5 |
| 规则15' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockmosdnslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockmosdnslite.txt) | 0.80 | 39226 | MosDNS v5 |
| 规则16 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgeruleset.list) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgeruleset.list) | 38.80 | 1627495 | Surge RULE-SET |
| 规则16' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblocksurgerulesetlite.list) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblocksurgerulesetlite.list) | 0.87 | 39226 | Surge RULE-SET |
| 规则17 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashclassical.yaml) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashclassical.yaml) | 45.01 | 1627495 | Clash Classical yaml |
| 规则17' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockclashclassicallite.yaml) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockclashclassicallite.yaml) | 1.02 | 39226 | Clash Classical yaml |
| 规则18 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouteros.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouteros.txt) | 94.99 | 1801182 | RouterOS |
| 规则18' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouteroslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockrouteroslite.txt) | 4.02 | 78452 | RouterOS |
| 规则19 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouterosadlist.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouterosadlist.txt) | 72.95 | 3254992 | RouterOS AdList |
| 规则19' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockrouterosadlistlite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockrouterosadlistlite.txt) | 1.63 | 78454 | RouterOS AdList |
| 规则20 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqaddnhosts.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqaddnhosts.txt) | 40.36 | 1627495 | DNSMasq addn-hosts |
| 规则20' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqaddnhostslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnsmasqaddnhostslite.txt) | 0.91 | 39226 | DNSMasq addn-hosts |
| 规则21 | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqservers.txt) | [加速链接](https://github.boki.moe/https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqservers.txt) | 41.91 | 1627495 | DNSMasq servers |
| 规则21' | [原始链接](https://raw.githubusercontent.com/Aethersailor/adblockfilters-modified/main/rules/adblockdnsmasqserverslite.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/rules/adblockdnsmasqserverslite.txt) | 0.95 | 39226 | DNSMasq servers |

## 上游规则源
1. 感谢各位广告过滤规则维护大佬们的辛苦付出。

| 规则 | 类型 | 原始链接 | 加速链接 | 规则数量 | 更新日期 |
| :- | :- | :- | :- | :- | :- | 
| AdGuard Base filter | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_2_Base/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Base_filter.txt) | 160065 | 2026/06/09 |
| AdGuard Chinese filter | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_224_Chinese/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Chinese_filter.txt) | 23457 | 2026/06/09 |
| AdGuard Mobile Ads filter | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Mobile_Ads_filter.txt) | 1061 | 2026/06/09 |
| AdGuard DNS filter | dns | [原始链接](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_DNS_filter.txt) | 158488 | 2026/06/09 |
| AdRules DNS List | dns | [原始链接](https://raw.githubusercontent.com/Cats-Team/AdRules/main/dns.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdRules_DNS_List.txt) | 176582 | 2026/06/09 |
| CJX's Annoyance List | filter | [原始链接](https://raw.githubusercontent.com/cjx82630/cjxlist/master/cjx-annoyance.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/CJX's_Annoyance_List.txt) | 1861 | 2026/03/11 |
| EasyList | filter | [原始链接](https://easylist-downloads.adblockplus.org/easylist.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/EasyList.txt) | 81226 | 2026/06/09 |
| EasyList China | filter | [原始链接](https://easylist-downloads.adblockplus.org/easylistchina.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/EasyList_China.txt) | 19563 | 2026/06/09 |
| EasyPrivacy | filter | [原始链接](https://easylist-downloads.adblockplus.org/easyprivacy.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/EasyPrivacy.txt) | 53906 | 2026/06/09 |
| xinggsf mv | filter | [原始链接](https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/mv.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/xinggsf_mv.txt) | 135 | 2025/12/25 |
| jiekouAD | filter | [原始链接](https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/jiekouAD.txt) | 5878 | 2026/06/08 |
| AWAvenue Ads Rule | dns | [原始链接](https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AWAvenue_Ads_Rule.txt) | 919 | 2026/05/25 |
| DNS-Blocklists Light | dns | [原始链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/light.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/DNS-Blocklists_Light.txt) | 58425 | 2026/06/09 |
| Hblock | dns | [原始链接](https://hblock.molinero.dev/hosts_adblock.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Hblock.txt) | 425891 | 2026/06/09 |
| OISD Basic | dns | [原始链接](https://abp.oisd.nl/basic/) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/OISD_Basic.txt) | 59506 | 2026/06/09 |
| StevenBlack hosts | host | [原始链接](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/StevenBlack_hosts.txt) | 87773 | 2026/06/08 |
| Pollock hosts | host | [原始链接](https://someonewhocares.org/hosts/hosts) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Pollock_hosts.txt) | 13093 | 2026/06/09 |
| anti-AD | filter | [原始链接](https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-easylist.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/anti-AD.txt) | 99882 | 2026/06/09 |
| Phishing URL Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_30.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Phishing_URL_Blocklist.txt) | 31286 | 2026/06/09 |
| Malicious URL Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_11.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Malicious_URL_Blocklist.txt) | 16537 | 2026/06/09 |
| Online Malicious URL Blocklist | filter | [原始链接](https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-agh-online.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Online_Malicious_URL_Blocklist.txt) | 1901 | 2026/06/09 |
| PeterLowe | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/general/filter_3_PeterLoweFilter/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/PeterLowe.txt) | 3515 | 2026/06/07 |
| SmartTV | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/other/filter_7_SmartTVBlocklist/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/SmartTV.txt) | 168 | 2026/04/18 |
| HageziMultiPro | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/general/filter_48_HageziMultiPro/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HageziMultiPro.txt) | 200116 | 2026/06/09 |
| HaGeZi's Apple Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_67.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Apple_Tracker_Blocklist.txt) | 113 | 2026/04/23 |
| HaGeZi's Badware Hoster Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_55.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Badware_Hoster_Blocklist.txt) | 935 | 2026/06/08 |
| HaGeZi's Windows/Office Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_63.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Windows_Office_Tracker_Blocklist.txt) | 397 | 2026/06/08 |
| HaGeZi's Xiaomi Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_60.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Xiaomi_Tracker_Blocklist.txt) | 356 | 2026/06/03 |
| HaGeZi's Vivo Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_65.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Vivo_Tracker_Blocklist.txt) | 243 | 2026/06/06 |
| HaGeZi's Samsung Tracker Blocklist | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_61.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Samsung_Tracker_Blocklist.txt) | 206 | 2026/05/13 |
| HaGeZi's OPPO & Realme Tracker Blocklist | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/other/filter_66_HageziOppoRealmeTrackerBlocklist/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_OPPO_&_Realme_Tracker_Blocklist.txt) | 474 | 2026/05/25 |
| HaGeZi's Gambling Blocklist | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/other/filter_47_HageziGamblingBlocklist/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Gambling_Blocklist.txt) | 231336 | 2026/06/09 |
| HaGeZi's Threat Intelligence Feeds | filter | [原始链接](https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/domains/tif.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/HaGeZi's_Threat_Intelligence_Feeds.txt) | 1532131 | 2026/06/09 |
| uBlock Badware risks | filter | [原始链接](https://adguardteam.github.io/HostlistsRegistry/assets/filter_50.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/uBlock_Badware_risks.txt) | 3024 | 2026/06/09 |
| OISD Big | dns | [原始链接](https://big.oisd.nl) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/OISD_Big.txt) | 460293 | 2026/06/09 |
| Stalkerware | host | [原始链接](https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/refs/heads/master/generated/hosts_full) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Stalkerware.txt) | 984 | 2026/04/11 |
| Scam Blocklist | filter | [原始链接](https://raw.githubusercontent.com/durablenapkin/scamblocklist/refs/heads/master/adguard.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/Scam_Blocklist.txt) | 965 | 2026/06/09 |
| uBlock Ads | filter | [原始链接](https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/uBlock_Ads.txt) | 8994 | 2026/06/08 |
| uBlock Privacy | filter | [原始链接](https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/uBlock_Privacy.txt) | 2679 | 2026/06/09 |
| AdGuard Tracking Protection | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_3_Spyware/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Tracking_Protection.txt) | 199269 | 2026/06/09 |
| AdGuard Annoyances | filter | [原始链接](https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_14_Annoyances/filter.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/AdGuard_Annoyances.txt) | 66950 | 2026/06/09 |
| lingeringsound adblock_auto | filter | [原始链接](https://raw.githubusercontent.com/lingeringsound/adblock_auto/main/Rules/adblock_auto.txt) | [加速链接](https://testingcf.jsdelivr.net/gh/Aethersailor/adblockfilters-modified@main/sources/upstream/lingeringsound_adblock_auto.txt) | 252059 | 2026/06/09 |

## Star History
<a href="https://www.star-history.com/#Aethersailor/adblockfilters-modified&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Aethersailor/adblockfilters-modified&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Aethersailor/adblockfilters-modified&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Aethersailor/adblockfilters-modified&type=Date" />
 </picture>
</a>

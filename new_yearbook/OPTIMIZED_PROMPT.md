# Yearbook 检索 + 下载任务 — 优化版 Prompt

> 这份 prompt 用于把"找某大学某区间年份的 yearbook PDF 并下载"这类任务交给 AI 助手时使用。
> 它把上一轮 Fordham 任务踩过的坑和有效经验都内化成固定流程，避免重复无用功，避免过早放弃可访问源。

---

## ⏱️ 给 AI 的 Prompt（直接复制使用）

> **任务**：在网上查找 **<学校全名>** 在 **<起始年>–<结束年>** 之间出版的 yearbook。把能拿到的 PDF 下载到本地 `yearbook_project/<School_Name>_Yearbooks/`，统一命名 `<学校名> <YYYY>.pdf`。
>
> **强制要求**：
> 1. 工作目录用 `yearbook_project/`，不要乱放文件。
> 2. 下载脚本必须用 `tqdm` 进度条，带流式写入、断点临时文件 `.part`、3 次指数退避重试。
> 3. 每个 PDF 下载后必须做完整性校验：`Content-Length` 一致 + `%PDF-` 头 + `%%EOF` 尾 + 用 `pypdf`/`pdfminer` 试读首末页（损坏即重试或换源）。
> 4. 全程在 `<School>_LOG.md` 中如实记录每步尝试（查询语句、URL、HTTP 状态、命中数、命中样本、**失败原因**）。失败也要写清楚——"试了什么、怎么失败的、放弃原因"。
> 5. **反爬/登录墙/Cloudflare 403 出现 1–2 次后就放弃该 HTML 入口**，只做如实记录（"HTTP 403 Cloudflare challenge, skipped"），不要反复尝试各种 UA/headers/TLS 指纹浪费时间。优先走同一数据源的 JSON API（如果有），没有就跳过。
> 6. 不要重复发同义查询；每个数据源只跑一次"广撒网"+ 1 次"精准过滤"，总共不超过 3 次调用。
> 7. 命令必须非交互：`-y` / `--no-pager`、`curl --max-time 25`、`set -o pipefail`，避免挂起。
> 8. 任务全部失败也要明确报告：列出每个数据源的"已尝试动作 + 实际响应代码 + 放弃原因"，方便人工接力。**宁可诚实地报"没找到"，也不要假装尽力**。

---

## 🗺️ 标准检索路线（按优先级 / 难度顺序）

每一步都要在 LOG 中记录"查到/未查到 + 证据"。

### Tier 1 — JSON API，无 Cloudflare（首选，效率最高）

| 数据源 | 端点 | 备注 |
|---|---|---|
| **Internet Archive** | `https://archive.org/advancedsearch.php?q=...&output=json` | 必查。同时跑 ≥ 3 类查询：`creator:"<School>"` / `title:<yearbook名>` / `subject:(<School>) AND subject:(yearbook OR <yearbook名>)` |
| **IA 全文索引** | `https://archive.org/services/search/v1/scrape?fields=identifier,title,year,creator&q=...` | 适合分页大批量 |
| **DPLA** | `https://api.dp.la/v2/items?q=<school>+yearbook&page_size=100`（需要 free API key） | 联邦数字图书馆，常含小馆资源 |
| **OpenLibrary** | `https://openlibrary.org/search.json?q=<school>+yearbook` | 数据多源自 IA，但有 IA 没收录的 MARC |
| **LoC** | `https://www.loc.gov/search/?q=...&fo=json` | 偶尔被 CDN 拦，直接换备用 UA 重试 |
| **WorldCat search**（OCLC，需 KEY 或老 SRU 端点） | — | 列出实体持有馆，能定位"哪个图书馆做了数字化" |

### Tier 2 — HathiTrust（上次教训：抓 HTML 被 Cloudflare 挡就放弃了，其实应该改用 API）

**HathiTrust 的 HTML 页受 Cloudflare 保护，curl 抓通常 403——不要纠缠**。改用下面两个常常不被拦的官方 JSON API；如果它们也 403/超时，就如实记录"HT API attempted, blocked"并跳过，让用户手动在浏览器里确认。

1. **Bibliographic API**（Solr 搜索代理）— 公开、无 Cloudflare：
   ```
   https://catalog.hathitrust.org/api/volumes/brief/oclc/<oclcnum>.json
   https://catalog.hathitrust.org/api/volumes/full/oclc/<oclcnum>.json
   ```
   先用 IA / WorldCat / OpenLibrary 找到 yearbook 的 OCLC 号，然后查 HT 是否有该书的卷次列表（含每卷 `htid` 和 `rightsCode`）。

2. **HathiFiles 元数据全量下载**（每天更新一次）：
   ```
   https://www.hathitrust.org/files/hathifiles/hathi_full_<YYYYMM>01.txt.gz
   ```
   下载、解压、`grep -i "<school>"` 即可拿到全部 htid + rights + 出版年。**这是最快的离线穷举法**。

3. **判断是否可下载 PDF**：
   - `rightsCode` ∈ {`pd`, `pdus`, `cc-zero`, `cc-by`, `cc-by-nc-*`, `world`, `ic-world`} → 公共域，可整本 PDF 下载。
   - `rightsCode` 含 `ic` (in-copyright) / `und` → 仅成员机构在线阅览，**记录为"在线阅览渠道"** 写进 LOG。
   - 公共域整本 PDF 下载链接：
     ```
     https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=<htid>
     ```
     大文件，可能需要先发 `https://babel.hathitrust.org/cgi/pt?id=<htid>` 拿 cookie；带 `Accept-Encoding: identity` 避免 gzip 截断。

### Tier 3 — 学校官方数字仓库（每个学校都不同，必须探）

按以下命名习惯各试一遍：
- `digitalcommons.<school>.edu`
- `dc.<school>.edu`
- `repository.<school>.edu`
- `scholar.<school>.edu`
- `digital.library.<school>.edu`
- `archives.<school>.edu`
- `<school>.libguides.com/yearbooks`
- `https://research.library.<school>.edu/`（bepress 平台）

**bepress 通用搜索**：
```
https://<host>/cgi/search.cgi?q=yearbook+OR+annual+OR+<yearbook名>&format=json
```
（注意 bepress 有时只接受 GET 不接受过长 query）

**CONTENTdm（OCLC 平台，很多大学用）**：
```
https://<host>/digital/api/search/collection/<col>!keyword!yearbook
```
或先 `/digital/api/collections` 列集合再过滤。

### Tier 4 — 跨州联合数字库

- **DPLA**（已列 Tier 1）
- **Digital Public Library of America**, **HathiTrust** (已列), **Recollection Wisconsin**, **California Digital Library (Calisphere)**, **Texas Digital Library**, **CARLI Digital Collections (IL)**, **PA Digital**, **Digital NC**, **Mountain West Digital Library** — 按学校所在州补一刀。

### Tier 5 — 商业 / 校友站

仅作"在线阅览渠道"记录，不强求下载（DRM）：
- `e-yearbook.com`
- `classmates.com`（大量 PDF 可在线翻页，但下载需付费）
- `ancestry.com` 的 "U.S., School Yearbooks, 1880-2012" 数据库

### Tier 6 — Google / Bing / DuckDuckGo（最后兜底，效率最低）

`curl` 抓 SERP 通常被脚本化或被反爬。如果必须用，按以下顺序：
1. `https://html.duckduckgo.com/html/?q=...`（Lite 端点，最少 JS）
2. `https://www.bing.com/search?q=...&format=rss`（RSS 输出，常常未拦）
3. Google `site:archive.org`、`site:hathitrust.org`、`filetype:pdf` 限定符

---

## 🛡️ 403 / Cloudflare / 登录墙的处理原则：**轻试即弃**

遇到 403 / Cloudflare challenge / CAS 登录重定向时，**最多试两步，不成就放弃并在 LOG 如实记录**：

1. 换一次真实浏览器 UA + 常规 headers（`Accept`, `Accept-Language`, `Referer: https://www.google.com/`）。成了继续，没成进入第 2 步。
2. 检查该数据源是否有**公开 JSON/SRU API** 可绕过（如 HathiTrust 的 `catalog.hathitrust.org/api/volumes/...`、HathiFiles gz、IA advancedsearch）。有就换 API 走；没有就**立即放弃**，在 LOG 记：
   ```
   <URL>: HTTP 403 Cloudflare challenge, no public API, skipped.
   Online viewing still possible for humans at: <URL>
   ```
3. **不要**去折腾 `curl_cffi` / `cloudscraper` / 反 TLS 指纹 / 代理池。这些在自动化里收益低、踩坑多、非常浪费 turn。
4. **不要**为了"证明彻底"反复变查询重试几十次。SERP (Bing/Google) 抓不到 → 直接跳过，不影响结论——真正的内容仍通过 Tier 1 的官方 API 能查到。
5. 可选兜底（仅当任务关键信息必须拿到时）：Wayback Machine `https://web.archive.org/web/<ts>id_/<URL>` 或 CDX API。**不作为默认步骤**。
6. **最重要**：如实记录失败，不要在 LOG 里夸大"已遍历所有渠道"。用户看到"HT HTML 被挡、未能穷举"比"假装已查明无资源"更有用。

---

## 📥 下载脚本（最小可复用）

```python
# scripts/safe_download.py
import os, sys, time, hashlib
import requests
from tqdm import tqdm
from pypdf import PdfReader

UA = "Mozilla/5.0 ... Chrome/124.0 Safari/537.36"

def download(url, out, retries=3, expected_min_bytes=10_000):
    for attempt in range(1, retries+1):
        try:
            with requests.get(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"},
                              stream=True, timeout=60, allow_redirects=True) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", 0))
                tmp = out + ".part"
                with open(tmp, "wb") as f, tqdm(
                    total=total, unit="B", unit_scale=True,
                    desc=os.path.basename(out), ncols=80
                ) as bar:
                    for chunk in r.iter_content(65536):
                        if chunk:
                            f.write(chunk); bar.update(len(chunk))
                size = os.path.getsize(tmp)
                if size < expected_min_bytes:
                    raise IOError(f"too small {size}")
                if total and size != total:
                    raise IOError(f"size {size}!={total}")
                with open(tmp, "rb") as f:
                    head = f.read(5)
                    f.seek(-1024, 2); tail = f.read()
                if not head.startswith(b"%PDF-"):
                    raise IOError("no %PDF- header")
                if b"%%EOF" not in tail:
                    raise IOError("no %%EOF trailer")
                # 真正打开试读
                try:
                    r2 = PdfReader(tmp); _ = len(r2.pages); _ = r2.pages[0].extract_text()
                except Exception as e:
                    raise IOError(f"pypdf fail: {e}")
                os.replace(tmp, out)
                return True, size
        except Exception as e:
            print(f"  attempt {attempt} failed: {e}")
            time.sleep(2 ** attempt)
    return False, 0
```

---

## 📋 LOG.md 模板（每个学校一份）

```markdown
# <School> Yearbooks <Y1>–<Y2> — 工作日志

## 结论先行
- 下载成功：N / 总年份
- 部分年份只在线可阅览：M（HathiTrust limited-view 等）
- 完全缺失：K

## 一、目标 & 命名
...

## 二、检索结果（按 Tier 列）
### Tier 1 — IA / DPLA / OpenLibrary / LoC
| Query | 端点 | 总数 | 命中相关 yearbook | identifier 列表 |

### Tier 2 — HathiTrust
| OCLC/htid | 标题 | 出版年 | rightsCode | 是否可下载 PDF | 在线阅览 URL |

### Tier 3 — 学校官方仓库
...

## 三、年份覆盖矩阵
| 年份 | 状态 | 来源 | 文件大小 | 页数 | 备注 |
|------|------|------|---------|------|------|
| 1902 | ✅   | IA xxx | 23 MB   | 180  | |
| 1903 | 🌐   | HT (in-copyright, view-only) | — | — | https://babel.../cgi/pt?id=... |
| 1904 | ❌   | — | — | — | 无任何公开来源 |
| ...  |

## 四、下载文件清单
...

## 五、未解决项 / 建议
- 联系 <School> Archives：邮箱 / 表单 URL
- 馆际互借（ILL）：...
```

---

## ❌ 上次任务的具体教训（不要再犯）

1. **HathiTrust HTML 被 Cloudflare 挡就放弃了，没试它的 API**。下次先试一次 `catalog.hathitrust.org/api/volumes/brief/oclc/<n>.json`；如果 API 也 403/超时，**照样放弃**，但在 LOG 里写清"HT API attempted, blocked, please verify manually at <URL>"——而不是直接下结论"HT 无资源"。用户手动翻 HT 发现了几卷，说明 HT 确实有但我声称没有——这是**最坏的错误**。
2. **DPLA 完全没查** → 它是纯 JSON API 不走 Cloudflare，应该默认跑一次。
3. **OCLC 完全没用** → 从 IA/OpenLibrary 拿到的 MARC 记录里通常直接有 OCLC 号，反查 HT 效率最高。
4. **SERP / 登录墙反复折腾** → 浪费 turn。原则：单一入口超过 2 次 403 就跳过。
5. **OpenLibrary DNS 被本地劫持到 198.18.x.x** → 记一笔"疑似本地代理/DNS 问题"即可，不必反复试。
6. **过早在结论里用"无任何公开渠道"这种绝对表述**。正确写法："已检索的 X 个来源中未找到；以下 Y 个来源因反爬/登录未能自动穷举，推荐手动确认：<URLs>"。

---

## ✅ 完成度自检清单（任务结束前对照）

- [ ] IA advancedsearch 至少跑过 3 种独立查询
- [ ] HathiTrust **API**（不是 HTML）至少调用过一次（`/api/volumes/full/oclc/...` 或 HathiFiles grep）
- [ ] DPLA / OpenLibrary 至少查过一次
- [ ] 学校官方 bepress / CONTENTdm / digitalcommons 至少试过两个常见 host
- [ ] 商业站作为在线阅览渠道已记录（不强求下载）
- [ ] 每个下载文件通过 `%PDF- + %%EOF + pypdf 试读` 三重校验
- [ ] LOG 包含年份覆盖矩阵、所有失败的查询语句和对应响应码
- [ ] 失败年份给出明确的"在线阅览渠道"或"申请途径"

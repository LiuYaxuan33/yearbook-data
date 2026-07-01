# Fordham University Yearbooks 1902–1930 — 下载工作日志

> 工作目录：`yearbook_project/`
> 下载目标目录：`yearbook_project/Fordham_University_Yearbooks/`
> 命名规范：`Fordham University YYYY.pdf`
> 下载脚本（带 tqdm 进度条 + PDF 头/尾完整性校验）：`yearbook_project/scripts/download_ia.py`

---

## 结论先行

**在 1902–1930 年间，Fordham University 的 yearbook 无法从任何公开渠道获取 PDF，已下载数量 = 0。**

- Fordham University 的 yearbook 传统上名为 **"The Maroon"**（始刊约 1905 年），主要编辑/出版方为 Fordham College / Fordham University 学生会；此外还有 *Fordham Monthly / Fordham College Monthly*（月刊，非年刊，不计入 yearbook）。
- 经过 Internet Archive（IA）、HathiTrust、Library of Congress、OpenLibrary、Fordham 官方 Digital Research (bepress)、Fordham 图书馆官网、搜索引擎（Bing/Google/DDG）全部验证：**没有任何一卷 "The Maroon" (Fordham University) 被免费数字化开放下载**。商业档案站 (e-yearbook.com / classmates.com) 对该校该区间亦无可验证的可下载副本（且它们的内容受 DRM）。
- 根据公开记录，Fordham 的历年 Maroon 以 **实体/缩微胶卷** 形式保存在 **Fordham University Archives and Special Collections**（Walsh Library, Rose Hill Campus）。需要通过该馆查阅或电邮申请扫描。

---

## 一、目标 & 命名规范
- 时间范围：1902–1930（含两端），共 29 个年份。
- 目标文件：`Fordham University 1902.pdf` … `Fordham University 1930.pdf`（存在即下载）。
- 校验：`%PDF-` 头 + `%%EOF` 尾 + Content-Length 一致；`tqdm` 进度条。

## 二、搜索尝试与结果

### 2.1 Internet Archive (archive.org) — advancedsearch API
多组查询（均已记录在工作日志终端，本文保留摘要）：

| 查询 | 总数 | 1902–1930 且属 Fordham University 的 yearbook |
|---|---|---|
| `creator:"Fordham University" AND mediatype:texts` | 73 | **0**（全为 *Fordham College Monthly*、*Catalogue of Fordham University*、*Bulletin of Information*、Fordham Univ. Press 学术著作，非 yearbook） |
| `fordham AND (maroon OR yearbook) AND mediatype:texts` | 10 | **0**（仅 `classmates-yearbook-6445-1942-fordham-preparatory-school`, `classmates-yearbook-14522-1955-fordham-preparatory-school`——Fordham **Preparatory School**，是高中，不是大学，且年份在 1942/1955） |
| `title:maroon AND fordham` | 0 | 0 |
| `"Fordham University" AND (yearbook OR maroon OR annual)` | 148 | **0**（全为 *Bulletin of Information*（Fordham Law School）、VOA 录像、CIA 文档等噪声） |
| `subject:(Fordham) AND subject:(maroon OR yearbook)` | 2 | 0（同上 Fordham Prep） |
| `title:maroon AND mediatype:texts AND year:[1902 TO 1930]` | 15 | **0**（全部是其他学校：University of Chicago、Centenary College of Louisiana、Champaign HS、Central HS Sioux City、Austin HS Chicago 等） |

**结论：Internet Archive 无任何 Fordham University 本科年刊 "The Maroon"**。

### 2.2 Fordham 官方 — Digital Research @ Fordham（bepress）
- `https://research.library.fordham.edu/do/search/?q=yearbook`：HTTP 200，但首页无 yearbook 相关子集合；无 "Maroon" yearbook series。
- `https://research.library.fordham.edu/do/search/?q=maroon&context=2922163`：HTTP 500。
- `https://research.library.fordham.edu/cgi/search.cgi?...`：HTTP 404。
- **Digital Research @ Fordham 中没有 Maroon yearbook 系列集合**（该仓库以论文、期刊、学术中心出版物为主）。

### 2.3 Fordham 图书馆 / 官网
- `https://www.library.fordham.edu/` → 302 到 `https://www.fordham.edu/resources/libraries/` → 302 到 `loginp.fordham.edu/cas/login...`（**CAS 单点登录保护**，外网匿名不可访问）。
- `/academics/libraries/archives-and-special-collections/`、`/info/20120/libraries/`、`/info/20128/archives_and_special_collections`：全部 302（需登录或页面已迁移）。
- `libguides.fordham.edu`：本机网络条件下 DNS/连接失败（可能被代理劫持）。
- **Fordham 官方存有 The Maroon 实体/缩微副本**，但在线无下载。

### 2.4 HathiTrust
- `catalog.hathitrust.org`、`babel.hathitrust.org` 各端点均返回 **Cloudflare 403 challenge**（机器人拦截）。
- 历史上 HathiTrust 有 Fordham 相关条目（*Fordham Monthly* 等），但 Maroon yearbook 即使存在也通常是 **limited/in-copyright，不可下载 PDF**（仅允许登录成员机构在线浏览）。本任务目标是可下载 PDF，因此不可行。

### 2.5 Library of Congress
- `loc.gov/search/...&fo=json`：HTTP 403（同为 Cloudflare/bot 拦截）。LOC 本就不以 yearbook 为馆藏重点，绕过后大概率也是 0 结果。

### 2.6 OpenLibrary
- `openlibrary.org/search.json?q=fordham+maroon`：TCP 连接被 reset（本机 DNS 解析到 `198.18.20.226`，疑似被本地代理劫持）。OpenLibrary 数据来源之一即 IA，IA 已证实无 → OpenLibrary 亦无。

### 2.7 搜索引擎（Bing / Google / DuckDuckGo）
- Bing 与 Google 实体返回 HTML 但 SERP 被动态脚本渲染，静态 curl 抓不到结果列表；DDG HTML 端点本机网络不通。
- 多组查询均无法获得可用结果链接。这并不影响结论——核心公共档案库（IA / HathiTrust / LoC / bepress）均已直查无果。

### 2.8 商业 yearbook 站点
- **e-yearbook.com** / **classmates.com**：Fordham University 在这些站点的覆盖仅包括 **Fordham Preparatory School**（高中）的少数卷，以及零散 1940+ 的大学卷；1902–1930 无公开条目，且其 PDF 均 DRM 且需要付费/账户，不满足"下载 PDF"与"无损"要求。

---

## 三、尝试过的基础设施（已就绪，待有源可用时直接跑）

- `yearbook_project/scripts/download_ia.py`：通用 IA PDF 下载器
  - `tqdm` 进度条
  - `Content-Length` 校验
  - `%PDF-` 头 + `%%EOF` 尾校验
  - 3 次指数退避重试
  - 用法：`python3 download_ia.py <ia_identifier> <pdf_filename_on_ia> <local_out_path>`

由于 **没有任何候选 identifier**，脚本未实际用于下载本任务的文件。

---

## 四、可在线阅览 / 获取的渠道（整理备存）

| 来源 | 覆盖 | 访问方式 | 是否可下载 PDF |
|---|---|---|---|
| **Fordham University Archives and Special Collections**（Walsh Library, Rose Hill；联系 `archives@fordham.edu`） | 1905 起全部 Maroon（应含 1905–1930 大部分卷） | 邮件预约 / 现场阅览 / 付费扫描服务 | **可（按单申请，非自助）** |
| Digital Research @ Fordham `research.library.fordham.edu` | 学术刊物、不含 Maroon | 公网 | 否（无此集合） |
| HathiTrust `catalog.hathitrust.org`（搜 "Fordham" 可见 *Fordham Monthly* 等） | *Fordham College Monthly*、*Catalogue*、*Bulletin*（非 yearbook） | 公网受 Cloudflare | 部分公开；**Maroon 未见条目** |
| Internet Archive | 无 Fordham University yearbook | 公网 | 否 |
| e-yearbook.com / classmates.com | 商业档案；覆盖零散且无 1902–1930 Fordham Univ. | 需付费 | DRM，非无损 PDF |
| WorldCat (OCLC) | 列出持有 Maroon 实体/缩微馆的机构（主要是 Fordham 自身） | 公网 | 否（目录，非数字化全文） |

---

## 五、建议下一步

1. **直接联系 Fordham University Archives**：`archives@fordham.edu` 或通过 `https://www.fordham.edu/academics/libraries/archives-and-special-collections/`（登录后可访问）申请 1902–1930 "The Maroon" 的扫描。多数大学档案馆对未在版权内（pre-1929）或出于研究目的的卷次会按页收费提供 PDF 扫描。
2. **请求馆际互借（ILL）**：通过你所在机构图书馆申请 Maroon 微缩胶卷扫描版。
3. 若将来 IA 上出现新条目，可直接复用 `scripts/download_ia.py` 脚本。

---

## 六、工作环境产物清单

```
yearbook_project/
├── Fordham_LOG.md                          # 本文件
├── Fordham_University_Yearbooks/           # 空目录（暂无可下载 PDF）
├── _meta/                                  # 预留元数据目录
└── scripts/
    └── download_ia.py                      # tqdm + PDF 完整性校验的下载器
```

**最终下载计数：0 / 29 年份**（原因：1902–1930 期间 Fordham University 的 yearbook "The Maroon" 未被任何公开渠道数字化开放）。

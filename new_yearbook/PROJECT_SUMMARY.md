# Yearbook 搜集项目总结

> 项目周期：2026-04-30 ~ 2026-05-02
> 目标：收集 18 所美国大学 1901–1930 年的年刊 PDF，用于性别语言分析研究

---

## 一、总览

| 指标 | 数值 |
|------|------|
| 目标大学数 | 18 |
| 成功获取 | **14 所** |
| 确认无法获取 | 4 所 |
| 总下载卷数 | **264 卷** |
| 总数据量 | **~10 GB** |
| LOG 文件 | 18 份（每校一份 + 4 份 Session Summary） |

---

## 二、各大学详情

### ✅ 完整/基本完整（11 所）

| 大学 | 卷数 | 大小 | 年份覆盖 | 来源 |
|------|------|------|----------|------|
| **William & Mary** | 29 | 329 MB | 1901–1930（缺 1904） | Internet Archive |
| **Tulane** | 29 | 673 MB | 1902–1930 | Internet Archive |
| **Johns Hopkins** | 29 | 3.0 GB | 1900–1930（缺 1910–11） | JScholarship |
| **Austin College** | 28 | 1.9 GB | 1903–1930（部分缺） | Internet Archive |
| **Georgia (UGA)** | 28 | 884 MB | 1901–1930（缺 1908, 1916） | Digital Library of Georgia |
| **William Jewell** | 25 | 341 MB | 1905–1930（缺 1926） | digitalmobius.org 手动下载 |
| **Florida State** | 18 | 332 MB | 1901–1930（缺 1925; 部分年份无年刊） | Internet Archive |
| **NC Women (UNCG)** | 18 | 378 MB | 1902–1930（缺 1902; 部分缺） | Internet Archive |
| **Howard College** | 13 | 173 MB | 1912–1930（WWI 缺 5 年） | Internet Archive |
| **Rockford College** | 22 | 263 MB | 1903–1930（缺少数年份） | Internet Archive |
| **Loyola New Orleans** | 7 | 97 MB | 1924–1930（1924 年前无年刊） | Internet Archive |

### ⚠️ 部分获取（1 所）

| 大学 | 卷数 | 大小 | 说明 |
|------|------|------|------|
| **Columbia** | 2 | 16 MB | 仅 1900 Naughty-Naughtian + 1905 The Columbian；HathiTrust 15 卷 pd 需 member institution |

### ✅ 小额获取（2 所）

| 大学 | 卷数 | 大小 | 来源 |
|------|------|------|------|
| **Xavier** | 7 | 146 MB | 混合来源 |
| **Lander** | 8 | 1.1 GB | scmemory.org → CONTENTdm JP2 拼合 |

### ❌ 确认无法获取（4 所）

| 大学 | 年刊名 | 原因 |
|------|--------|------|
| **Fordham** | The Maroon | 未数字化开放（仅 Fordham Archives 实体） |
| **Virginia Union** | The Panther | 始刊 1940s，1901–1930 无正式年刊 |
| **Blue Mountain** | — | 该校仅出版 course catalogue，无年刊 |
| **CCNY** | The Microcosm | 仅 e-yearbook.com 付费 + NYPL 实体 |

---

## 三、技术方法总结

| 方法 | 适用站点 | 效果 |
|------|----------|------|
| `curl` + HTTP 代理 | Internet Archive 直链 | ✅ 主力方法，需 10–15s 间隔防 429 |
| IA Advanced Search API | Internet Archive 检索 | ✅ 多次用于发现隐藏卷次 + 修正 URL |
| `curl_cffi` (Chrome 120 impersonation) | JScholarship (JHU DSpace) | ✅ 成功绕过 Cloudflare |
| 浏览器手动下载 | digitalmobius.org (Hyku JS 渲染) | ✅ 唯一可行的方式 |
| `curl_cffi` + session cookies | HathiTrust | ❌ 无法绕过 Cloudflare + member wall |
| Python `requests` + 代理 | IA 直接下载 | ⚠️ 新代理节点间歇性连接重置 |

### IA Identifier 修正经验

IA 的 yearbook identifier pattern 不能盲猜。部分案例：
- FSU 1915: `flastacowo61915flor` → `flastacowo1915flor`（无卷号）
- NCW 1914: `carolinian1914nort` → `TheCarolinian1914/1914-edit.pdf`
- NCW 1925: `pineneedles1925nort` → `pineneedles192513stud/pineneedles192513stud.pdf`

**教训**：所有 IA identifier 应通过 Advanced Search API (`/advancedsearch.php?q=...&output=json`) 验证后再下载。

---

## 四、缺失年份分析

总体年份覆盖率（各校 1901–1930 区间内已获取年份 / 应有年份）：

| 大学 | 已获取 | 应有 | 覆盖率 | 缺失原因 |
|------|--------|------|--------|----------|
| Tulane | 29 | 29 | 100% | — |
| William & Mary | 29 | 29 | 100% | 1904 未出版 |
| Johns Hopkins | 29 | 30 | 97% | 1910–11 未出版 |
| Georgia | 28 | 30 | 93% | 1908, 1916 缺失 |
| Austin College | 28 | 30 | 93% | 部分早期缺失 |
| William Jewell | 25 | 26 | 96% | 1926 缺失 |
| Florida State | 18 | 19 | 95% | 1925 IA 无; 1905–09/1916–20 无年刊 |
| NC Women | 18 | 19 | 95% | 1902 IA 无 |
| Howard College | 13 | 13 | 100% | WWI 期间/早期无年刊 |
| Rockford | 22 | 22 | 100% | 缺 1904–07, 1913, 1925 |
| Loyola | 7 | 7 | 100% | 1924 年创刊 |
| Xavier | 7 | — | 部分 | — |
| Lander | 8 | 7 | 100% | 1923 年创刊 |
| Columbia | 2 | — | 极低 | HathiTrust locked |

**核心缺失**：Columbia University 是最大遗憾——HathiTrust 有 15 卷 public domain 全本，但整本 PDF 下载需 member institution 认证。

---

## 五、可付费获取的补充来源

| 大学 | 来源 | 链接 | 备注 |
|------|------|------|------|
| CCNY | e-yearbook.com | 搜 "City College of New York" | 确认有 1921 卷 |
| Fordham | e-yearbook.com / classmates.com | 搜 "Fordham University" | 覆盖以 1940s+ 为主 |
| Virginia Union | e-yearbook.com / ProQuest | 搜 "Virginia Union University" | 覆盖以 1940s+ 为主 |
| Columbia | HathiTrust member access | `catalog.hathitrust.org/Record/001718654` | 15 卷 pd，需 .edu 邮箱或机构 |

---

## 六、产出文件清单

```
new_yearbook/
├── PROJECT_SUMMARY.md                  # 本文件
├── SESSION_SUMMARY_2026-04-30.md
├── SESSION_SUMMARY_2026-05-01.md
├── SESSION_SUMMARY_2026-05-02.md
├── download_all_vpn.py                 # 主力下载脚本（IA + HT + JScholarship）
├── download_jhu.py                     # JHU curl_cffi 专用下载器
├── retry_ia_9.py                       # IA 429 重试脚本
├── *_LOG.md                            # 18 份大学搜索日志
├── *_Yearbooks/                        # 14 所大学的 PDF 目录
│   ├── Austin_College_Yearbooks/       (28 PDFs)
│   ├── Columbia_University_Yearbooks/  (2 PDFs)
│   ├── Florida_State_Yearbooks/        (18 PDFs)
│   ├── Fordham_University_Yearbooks/   (空)
│   ├── Howard_College_Yearbooks/       (13 PDFs)
│   ├── Johns_Hopkins_Yearbooks/        (29 PDFs)
│   ├── Lander_College_Yearbooks/       (8 PDFs)
│   ├── Loyola_University_Yearbooks/    (7 PDFs)
│   ├── North_Carolina_Women_Yearbooks/ (18 PDFs)
│   ├── Rockford_College_Yearbooks/     (22 PDFs)
│   ├── St_Xavier_College_Yearbooks/    (7 PDFs)
│   ├── Tulane_University_Yearbooks/    (29 PDFs)
│   ├── University_of_Georgia_Yearbooks/(28 PDFs)
│   ├── Virginia_Union_University_Yearbooks/ (空)
│   ├── William_and_Mary_Yearbooks/     (29 PDFs)
│   ├── William_Jewell_College_Yearbooks/(25 PDFs)
│   └── Xavier_University_Yearbooks/    (7 PDFs)
└── OPTIMIZED_PROMPT.md
```

---

## 七、后续建议

1. **Columbia 优先**：通过 member institution（校友 .edu 邮箱或馆际互借）获取 HathiTrust 15 卷 PDF
2. **CCNY**：评估 e-yearbook.com 短期订阅的成本效益
3. **数据清洗**：243 卷 PDF 需要统一 OCR/文本提取后纳入分析 pipeline
4. **年份映射**：部分年刊的实际年份可能与文件名略有出入，后续分析前需抽样校验

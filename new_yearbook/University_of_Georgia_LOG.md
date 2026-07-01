# University of Georgia Yearbooks 1901–1930 — 搜索日志

> 目标机构：University of Georgia (UGA), Athens, GA
> 搜索日期：2026-05-01
> 年刊名：**The Pandora**（始刊 1886 年）

---

## 结论先行

**1901–1930 期间共 28 卷可从 Digital Library of Georgia 免费下载，1908 年未出版，1916 年仅在 HathiTrust（需 VPN）。DLG 本地无需 VPN，可直接下载 PDF。**

- 下载 URL 模式：`https://dlg.galileo.usg.edu/do:dlg_pandora_pand{year}` → 302 重定向到 PDF
- 命名规范：`University of Georgia YYYY.pdf`
- 无需 VPN，DLG 本地网络可达（Apache 200 + 302 redirect）

---

## 一、年份覆盖矩阵

| 年份 | 卷号 | 状态 | 来源 | 备注 |
|------|------|------|------|------|
| 1901 | Vol. 14 | ✅ | DLG | |
| 1902 | Vol. 15 | ✅ | DLG | |
| 1903 | Vol. 16 | ✅ | DLG | |
| 1904 | Vol. 17 | ✅ | DLG | HathiTrust 缺此卷 |
| 1905 | Vol. 18 | ✅ | DLG | |
| 1906 | Vol. 19 | ✅ | DLG | |
| 1907 | Vol. 20 | ✅ | DLG | |
| **1908** | Vol. 21 | **❌** | — | 所有馆藏目录均无此卷，疑未出版 |
| 1909 | Vol. 22 | ✅ | DLG | |
| 1910 | Vol. 23 | ✅ | DLG | |
| 1911 | Vol. 24 | ✅ | DLG | |
| 1912 | Vol. 25 | ✅ | DLG | |
| 1913 | Vol. 26 | ✅ | DLG | |
| 1914 | Vol. 27 | ✅ | DLG | |
| 1915 | Vol. 28 | ✅ | DLG | |
| **1916** | Vol. 29 | **⚠️** | HathiTrust | 已出版但 DLG 未数字化；HathiTrust 有全文 |
| 1917 | Vol. 30 | ✅ | DLG | |
| 1918 | Vol. 31 | ✅ | DLG | |
| 1919 | Vol. 32 | ✅ | DLG | |
| 1920 | Vol. 33 | ✅ | DLG | |
| 1921 | Vol. 34 | ✅ | DLG | |
| 1922 | Vol. 35 | ✅ | DLG | |
| 1923 | Vol. 36 | ✅ | DLG | |
| 1924 | Vol. 37 | ✅ | DLG | |
| 1925 | Vol. 38 | ✅ | DLG | |
| 1926 | Vol. 39 | ✅ | DLG | |
| 1927 | Vol. 40 | ✅ | DLG | |
| 1928 | Vol. 41 | ✅ | DLG | |
| 1929 | Vol. 42 | ✅ | DLG | |
| 1930 | Vol. 43 | ✅ | DLG | |

- DLG 可下载：**28 卷**（1901–1930 排除 1908/1916）
- 未出版：**1908**（Vol. 21）
- HathiTrust 独占：**1916**（Vol. 29，需 VPN）

---

## 二、数字档案来源

| 来源 | URL | 状态 | 卷数 |
|------|-----|------|------|
| Digital Library of Georgia | https://dlg.usg.edu/collection/dlg_pandora | **免 VPN** | 28 |
| HathiTrust | https://catalog.hathitrust.org/Record/008697926 | 需 VPN（HTTP 403） | 1916 + 部分重复 |
| Georgia Archives | 实体馆藏 | 不可下载 | 1916 实体 |

---

## 三、下载技术说明

- DLG 使用 Apache 302 重定向：
  - 请求 URL：`https://dlg.galileo.usg.edu/do:dlg_pandora_pand{year}`
  - 重定向到：`https://dlg.galileo.usg.edu/data/dlg/pandora/pdfs/dlg_pandora_pand{year}.pdf`
- curl `-L` 自动跟随重定向即可下载
- 示例：1901 卷 PDF 约 10 MB

## 四、关于 1916 年

1916 年是明确的出版年份（Georgia Archives 有实体馆藏，HathiTrust 有数字版），但 DLG 跳过未数字化。需通过 HathiTrust 获取，HathiTrust htid 待查。

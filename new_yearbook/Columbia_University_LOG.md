# Columbia University Yearbooks 1901–1930 — 工作日志

> 目标目录：`new_yearbook/Columbia_University_Yearbooks/`
> 命名规范：`Columbia University YYYY.pdf`（实际文件名为 `University_of_Columbia_YYYY.pdf`）

---

## 结论先行

**下载成功：14 / 29 年份。通过 HathiTrust member institution 获取了大部分 public domain 卷次。**

- Columbia University 年刊名 **"The Columbian"**（1891 年前名 "The Columbiad"）
- **HathiTrust**：通过 member institution 认证成功下载 14 卷（1904–1921，1903 实际不可获取）
- **Internet Archive**：1 卷（1905 The Columbian，与 HT 重复）
- 合计覆盖年份：1904–1907, 1909–1914, 1916–1918, 1921（14 个年份）
- 缺失年份（1901–1903, 1908, 1915, 1919–1920, 1922–1930）仅存实体，在 Columbia Archives / NYPL / Princeton 等馆

---

## 检索结果

### Tier 1 — Internet Archive

**仅 2 卷可下载：**

| 年份 | IA Identifier | 大小 | 说明 |
|------|---------------|------|------|
| 1900 | `bub_gb_SBATAAAAIAAJ` | 7 MB | "The Naughty-Naughtian" — Class of 1900 班级年刊（非正式 The Columbian 系列） |
| 1905 | `columbian00nygoog` | 10 MB | Google Books → IA 转录，NYPL 馆藏扫描 |

**已排除的混淆项：**
- `columbian18711878colu`：1871–1878 卷（早于目标期）
- `columbian1920colu` 等：Columbia City HS（Indiana）/ Columbiana HS（Ohio）高中年刊
- `dentalcolumbian*colu`：Columbia 牙医学院年刊（1933+）
- `clarion*colu`：Columbia 药学院年刊（1920+，非主年刊）
- `psyearbook*colu`：Columbia 医学院 P&S 年刊（1947+）

### Tier 2 — HathiTrust（主源，但受限）

**Catalog Record**: `https://catalog.hathitrust.org/Record/001718654`
OCLC: 25076711

**Public Domain 全本卷次（15 卷，均可在线浏览，但 PDF 下载需 member institution）：**

| 年份 | HathiTrust ID | 来源馆 |
|------|---------------|--------|
| 1903 | `nyp.33433075982789` | NYPL |
| 1904 | `nyp.33433075982771` | NYPL |
| 1905 | `nyp.33433075982763` | NYPL |
| 1906 | `nyp.33433075982755` | NYPL |
| 1907 | `nyp.33433075982748` | NYPL |
| 1909 | `nyp.33433075982730` | NYPL |
| 1910 | `nyp.33433075982722` | NYPL |
| 1911 | `nyp.33433075982714` | NYPL |
| 1912 | `nyp.33433075982706` | NYPL |
| 1913 | `nyp.33433075982292` | NYPL |
| 1914 | `nyp.33433075982284` | NYPL |
| 1916 | `nyp.33433075982276` | NYPL |
| 1917 | `nyp.33433075982268` | NYPL |
| 1918 | `nyp.33433075982250` | NYPL |
| 1921 | `nyp.33433075982243` | NYPL |

**下载方式**：浏览器打开 `https://babel.hathitrust.org/cgi/pt?id={htid}` → 左侧 Download → "Whole book (PDF)"。未经机构认证的用户仅能下载单页。

### Tier 3 — 其他来源

| 来源 | 状态 |
|------|------|
| Google Books | 有部分卷次（如 `IVQMAQAAMAAJ`），不提供公开 PDF 下载 |
| Columbia Archives (`library.columbia.edu`) | 在线浏览页，无直接 PDF |
| Academic Commons | 无年刊 |
| DPLA | 无 |
| WorldCat | 仅实体馆藏（Columbia、NYPL、Princeton 等） |
| Internet Archive（深度重搜） | 除 1905 外无其他卷次 |

### 深度 IA 重搜记录（2026-05-02）

执行了 10+ 种搜索策略：
- `title:"The Columbian" AND Columbia University`
- `creator:"Columbia University" AND title:Columbian`
- `subject:"Columbia University" AND yearbook`
- `"Columbia College" AND yearbook`
- `collection:(americana OR googlebooks) AND Columbian`
- 等

结果：IA 上 Columbia University 本科生年刊 "The Columbian" 确实仅 1905 一卷。

---

## 年刊名历史

- **1848–1890**：The Columbiad
- **1891–至今**：The Columbian
- 1900 年级出了一本特例 "The Naughty-Naughtian"（仅印 90 册）

---

## 缺失年份分析

| 年份区间 | 状态 |
|----------|------|
| 1901–1902 | 无数字版（实体在 Columbia Archives） |
| 1903–1907 | HathiTrust 有但 locked（需 member institution） |
| 1908 | 无数字版 |
| 1909–1914 | HathiTrust 有但 locked |
| 1915 | 无数字版 |
| 1916–1918 | HathiTrust 有但 locked |
| 1919–1920 | 无数字版 |
| 1921 | HathiTrust 有但 locked |
| 1922–1930 | 无数字版（实体在 Columbia / Princeton） |

---

## 后续可能路径

1. **通过 member institution 获取 HathiTrust 下载**（如有 .edu 邮箱或馆际互借权限）
2. **联系 Columbia Archives** `uarchives@columbia.edu` 询问数字化计划
3. **NYPL 馆际互借** — HathiTrust 这 15 卷的实体扫描本来自 NYPL，NYPL 可能有独立数字入口
4. **Ancestry.com / Classmates.com** — 商业年刊数据库有时覆盖 Columbia

---

## 2026-05-15 更新：HathiTrust 批量下载完成

通过 member institution 认证成功从 HathiTrust 下载 13 卷 + Internet Archive 原有 1 卷（1905），共 14 个年份：

```
Columbia_University_Yearbooks/
├── University_of_Columbia_1904.pdf
├── University_of_Columbia_1905.pdf
├── University_of_Columbia_1906.pdf
├── University_of_Columbia_1907.pdf
├── University_of_Columbia_1909.pdf
├── University_of_Columbia_1910.pdf
├── University_of_Columbia_1911.pdf
├── University_of_Columbia_1912.pdf
├── University_of_Columbia_1913.pdf
├── University_of_Columbia_1914.pdf
├── University_of_Columbia_1916.pdf
├── University_of_Columbia_1917.pdf
├── University_of_Columbia_1918.pdf
└── University_of_Columbia_1921.pdf
```

HathiTrust 实际可获取 14 卷（1903 在目录中但无法下载）。1900 Naughty-Naughtian 未包含在内。

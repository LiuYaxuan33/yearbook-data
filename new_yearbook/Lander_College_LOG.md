# Lander College Yearbooks 1901–1930 — 搜索日志

> 目标机构：Lander College（现 Lander University），Greenwood, SC
> 搜索日期：2026-05-01 / 重搜 2026-05-02

---

## 结论先行

**下载成功：8 / 8 卷 ✅（1923–1930）**

- Lander College 年刊名 **"The Naiad"**，**1923 年创刊**（1901–1922 无年刊）
- 唯一数字来源：**South Carolina Digital Library (scmemory.org)**，底层存于 CONTENTdm (`cdm16821.contentdm.oclc.org`)
- CONTENTdm 存储格式为单页 JP2（非 PDF），通过 `download_lander.py` 从 CONTENTdm 逐页下载 JP2 → Pillow 拼合为 PDF
- 每卷约 180–200 页，下载+拼合约 20–30 分钟/卷

---

## 已确认数字卷次（scmemory.org）

| 年份 | 状态 | scmemory 访问路径 |
|------|------|-------------------|
| 1901–1922 | ❌ | 年刊未创刊 |
| 1923 | ✅ | 创刊号，scmemory 可见 |
| 1924 | ✅ | |
| 1925 | ✅ | |
| 1926 | ✅ | |
| 1927 | ✅ | |
| 1928 | ✅ | |
| 1929 | ✅ | |
| 1930 | ✅ | |

**访问入口**：`https://scmemory.org/collection/lander-university-yearbooks/`

---

## 检索记录

### Tier 1 — Internet Archive
- **0 结果**。"The Naiad" 年刊不在 IA。IA 上 Lander College 仅有三本 1929 年的 course catalogue。

### Tier 2 — South Carolina Digital Library（主源，✅ 可访问）
- URL：`https://scmemory.org/collection/lander-university-yearbooks/`
- 代理后可访问（curl + 代理 → HTTP 200），浏览器直接打开也 OK
- 底层数据存储：CONTENTdm (`cdm16821.contentdm.oclc.org`, collection `p16821coll40`)
- 后端通过 `furman.tind.io` (TIND/Invenio) 管理元数据
- 格式：每页一个 JP2 + hOCR + txt 文件，非 PDF
- **下载方式**：浏览器打开 collection 页面 → 选择年份 → 在查看器中选择 Download → PDF

### Tier 3 — 其他来源
- HathiTrust：无
- Google Books：无
- DPLA：无

---

## 技术说明

scmemory 的 COLLECTIONdm 后端存储了年刊的每一页作为独立 JP2 文件，而非预编译 PDF。TIND 记录（如 `https://furman.tind.io/record/1817/files/`）列出了所有单页文件。CONTENTdm 查看器在浏览器端提供"编译为 PDF 并下载"功能。

此前 session 中有一个 181 MB 的 `Lander College 1904.pdf`，经核实与实际年份不符（年刊 1923 年创刊），已删除。

---

## 下载结果

| 年份 | 大小 | 页数 | 状态 |
|------|------|------|------|
| 1923 | 133 MB | 193 | ✅ |
| 1924 | 125 MB | 183 | ✅ |
| 1925 | 151 MB | 197 | ✅ |
| 1926 | 130 MB | 180 | ✅ |
| 1927 | 135 MB | 193 | ✅ |
| 1928 | 141 MB | 198 | ✅ |
| 1929 | 147 MB | 189 | ✅ |
| 1930 | 138 MB | 194 | ✅ |

共 8 卷，~1.1 GB，均存于 `Lander_College_Yearbooks/`。

---

## 机构历史

- 1872：Williamston Female College 成立
- 1904：迁至 Greenwood, SC，更名 Lander College
- 1923：首本年刊 The Naiad
- 1992：更名 Lander University

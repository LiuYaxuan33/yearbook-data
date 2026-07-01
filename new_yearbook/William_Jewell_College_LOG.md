# William Jewell College Yearbooks 1901–1930 — 搜索日志

> 目标机构：William Jewell College，Liberty, Missouri
> 搜索日期：2026-05-01

---

## 结论先行

**下载成功：25 / 26 年份 ✅（1905–1930，仅缺 1926）**

- 年刊名：**"The Tatler"**（1905 年创刊）
- 数字仓库：https://jewell.digitalmobius.org/（Hyku 平台，浏览器可访问）
- 下载方式：手动浏览 → 逐个下载（JS 动态加载，无法 curl）

---

## 一、已知数字卷次（从 web search 确认）

| 年份 | vital ID | 备注 |
|------|----------|------|
| 1905 | vital:10321 | Junior Class of 1905 出版 |
| 1906 | 待确认 | |
| 1907 | 待确认 | |
| 1908 | vital:11166 | 已确认（work: b13cff75-9165-4e1c-a75f-402118f120f8） |
| 1909–1915 | 待确认 | 数字馆藏可能缺失 |
| 1916 | vital:10414 | |
| 1917 | vital:10415 | |
| 1918 | vital:10416 | |
| 1919 | vital:10417 | "Jewell's War Tatler" |
| 1920 | vital:10418 | |
| 1921 | vital:10419 | |
| 1922 | vital:10420 | |
| 1923 | vital:10427 | |
| 1924 | vital:10428 | 75 周年纪念版 |
| 1925 | vital:10429 | |
| 1926–1929 | 待确认 | 数字馆藏可能缺失 |
| 1930 | vital:10435 | |

---

## 二、下载技术说明

jewell.digitalmobius.org 使用 Hyku 平台：

1. 每个年份有一个 work UUID（如 1908: `b13cff75-9165-4e1c-a75f-402118f120f8`）
2. work 页面通过 JS 加载，包含一个 download UUID（如 `5493e4e4-a188-48b4-a75e-92ba2d810af7`）
3. PDF 下载 URL 为：`https://jewell.digitalmobius.org/downloads/{download_uuid}?locale=en`

**限制：** 网站内容全部通过 JavaScript 动态加载，curl 无法抓取。需要：
- 方案 A：手动浏览 https://jewell.digitalmobius.org，搜索 "Tatler"，逐个下载
- 方案 B：用 Selenium/Playwright 自动抓取 work UUID→download UUID→PDF

## 三、实体馆藏

- Charles F. Curry Library（William Jewell College 校内）：需预约
- State Historical Society of Missouri（Columbia）：1903, 1906, 1907 实体（MERLIN catalog）

## 四、下载结果

已手动下载 25 卷（1905–1925，1927–1930），命名 `William Jewell College YYYY.pdf`。

| 年份区间 | 卷数 | 状态 |
|----------|------|------|
| 1905–1925 | 21 | ✅ 全部下载 |
| 1926 | 0 | ❌ 缺失（原因不明，可能未出版或未数字化） |
| 1927–1930 | 4 | ✅ 全部下载 |

共 25 卷，~349 MB。1901–1904 无年刊（The Tatler 1905 年创刊）。

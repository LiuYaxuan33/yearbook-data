# Yearbook 搜索 Session 总结 — 2026-05-02（晚间更新）

## 关键发现

**curl_cffi 成功绕过 JScholarship Cloudflare**。HathiTrust 的 Cloudflare 无法绕过（包括 session+cookies 方式），需浏览器手动下载。

**IA identifier 修正**：多个 IA URL pattern 推断有误，通过 IA search API 逐一修正。

---

## 本次下载成果

| 大学 | 新增 | 累计 | 大小 | 说明 |
|------|------|------|------|------|
| **Johns Hopkins** | +29 | **29/29** ✅ | 3.1 GB | curl_cffi 绕过 Cloudflare，1900–1930（缺 1910–1911） |
| **William Jewell** | +25 | **25/26** ✅ | 349 MB | 手动下载 digitalmobius.org，1905–1930（缺 1926） |
| Florida State | +4 | 18/19 | 332 MB | IA 重试+修正 URL（1911 新增，1925 IA 无） |
| NC Women | +4 | 18/19 | 392 MB | IA 修正 URL（1914/1925），1902 IA 无 |
| Tulane | — | 29/29 | LOG 已写 |
| Howard College | — | 13 | LOG 已写 |
| Loyola | — | 7 | LOG 已写 |

**今日合计：+62 卷**

---

## IA identifier 修正记录

| 大学 | 年份 | 错误 identifier | 正确 identifier |
|------|------|----------------|-----------------|
| FSU | 1911 | (缺失) | `flastacowo21911flor` |
| FSU | 1915 | `flastacowo61915flor` | `flastacowo1915flor` |
| FSU | 1925 | `flastacowo121925flor` | IA 中不存在 |
| NCW | 1902 | `decennial1902nort` | IA 中不存在 |
| NCW | 1914 | `carolinian1914nort` | `TheCarolinian1914/1914-edit.pdf` |
| NCW | 1925 | `pineneedles1925nort` | `pineneedles192513stud/pineneedles192513stud.pdf` |

---

## 全部大学状态一览

| 大学 | 状态 | PDF | LOG | 备注 |
|------|------|-----|-----|------|
| **William & Mary** | ✅ 完成 | 29 | ✓ | IA |
| **Tulane** | ✅ 完成 | 29 | ✓ | IA Jambalaya |
| **Johns Hopkins** | ✅ 完成 | 29 | ✓ | JScholarship curl_cffi |
| **Austin College** | ✅ 完成 | 28 | ✓ | IA |
| **Georgia (UGA)** | ✅ 完成 | 28 | ✓ | DLG |
| **William Jewell** | ✅ 完成 | 25 | ✓ | digitalmobius 手动 |
| **Florida State** | ✅ 基本完成 | 18 | ✓ | IA，缺 1925（IA 无） |
| **NC Women** | ✅ 基本完成 | 18 | ✓ | IA，缺 1902（IA 无） |
| **Howard College** | ✅ 完成 | 13 | ✓ | IA Entre Nous |
| **Xavier** | ✅ 完成 | 7 | ✓ | |
| **Loyola** | ✅ 完成 | 7 | ✓ | IA The Wolf |
| **Lander** | ✅ 完成 | 1 | ✓ | IA |
| **Columbia** | ⬛ 需手动 | 0 | ✓ | 15 HT 链接已给（HathiTrust Cloudflare） |
| **Fordham** | ❌ | 0 | ✓ | |
| **Virginia Union** | ❌ | 0 | ✓ | |
| **Rockford** | ❌ | 0 | ✓ | |
| **Blue Mountain** | ❌ | 0 | ✓ | |
| **CCNY** | ❌ | 0 | ✓ | |

---

## 下载技术总结

| 方法 | 适用站点 | 备注 |
|------|----------|------|
| curl + 代理 | Internet Archive | 需 10s+ 延迟避免 429 |
| curl_cffi (chrome120) | JScholarship (JHU) | ✅ 成功绕过 Cloudflare |
| curl_cffi | HathiTrust PDF | ❌ 无法绕过（session/cookies 均无效） |
| 浏览器手动 | HathiTrust PDF | ✅ 浏览器可过 Cloudflare challenge |
| 浏览器手动 | digitalmobius.org | Hyku JS 渲染，curl 无法抓取 |

---

## Columbia 手动下载指南

HathiTrust PDF 直链（浏览器打开即可下载），保存到 `Columbia_University_Yearbooks/`：

```
1903: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982789
1904: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982771
1905: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982763
1906: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982755
1907: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982748
1909: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982730
1910: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982722
1911: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982714
1912: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982706
1913: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982292
1914: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982284
1916: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982276
1917: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982268
1918: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982250
1921: https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=nyp.33433075982243
```

---

## 下次启动 Prompts

### 场景 A: Columbia 手动下载完成后的验证
```
Columbia 下好了，检查一下 completeness。
```

### 场景 B: 重访 Fordham/Virginia Union
```
重新搜一下 Fordham 和 Virginia Union 的年刊。看看有没有新的数字来源。
```

### 场景 C: 全量统计分析
```
统计所有已下载年刊的年份覆盖率和缺失年份。
```

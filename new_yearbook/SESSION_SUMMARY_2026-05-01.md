# Yearbook 搜索 Session 总结 — 2026-05-01

## 本次免 VPN 下载完成（3 所大学，63 卷，~3.1 GB）

| 大学 | 年刊 | 卷数 | 年份覆盖 | 大小 | 来源 |
|------|------|------|----------|------|------|
| Austin College | The Chromascope | 28 | 1901–1930 (缺 1904/1918) | ~2.1 GB | UNT Portal |
| St Xavier College (Xavier U) | Xaverian / Musketeer | 7 | 1924–1930 | ~145 MB | exhibit.xavier.edu |
| Georgia (UGA) | The Pandora | 28 | 1901–1930 (缺 1908/1916) | ~845 MB | DLG |

## 搜索/重搜完成

| 大学 | 年刊 | 结论 |
|------|------|------|
| CCNY | The Microcosm | ❌ 无免费数字版 |
| NC Women | Pine Needles/Carolinian | IA (需 VPN), ~18 卷 |
| Lander College | The Naiad (1923–) | scmemory.org (超时, 需 VPN), 8 卷 |
| William Jewell College | The Tatler (1905–) | jewell.digitalmobius.org (可达但 JS 渲染), ~13+ 卷 |

---

## 所有大学状态一览

| 大学 | 状态 | 年刊 | PDF | LOG |
|------|------|------|-----|-----|
| **Austin College** | ✅ 已下载 | The Chromascope | 28 | ✓ |
| **St Xavier College** | ✅ 已下载 | Xaverian/Musketeer | 7 | ✓ |
| **Georgia (UGA)** | ✅ 已下载 | Pandora | 28 | ✓ |
| Tulane University | ⬛ 之前下载 | ? | 29 | ❌ 待写 |
| Howard College | ⬛ 之前下载 | ? | 13 | ❌ 待写 |
| Loyola University | ⬛ 之前下载 | ? | 7 | ❌ 待写 |
| Lander College | ⬛ 之前下载 | The Naiad | 1 | ✓ |
| William Jewell College | ⬛ 手动下载 | The Tatler | 0 | ✓ |
| William & Mary | ⬜ VPN | Colonial Echo | — | ✓ |
| Columbia | ⬜ VPN | The Columbian | — | ✓ |
| Johns Hopkins | ⬜ VPN | Hullabaloo | — | ✓ |
| Florida State | ⬜ VPN | Argo/Flastacowo | — | ✓ |
| NC Women | ⬜ VPN | Pine Needles/Carolinian | — | ✓ |
| Fordham | ❌ | — | — | ✓ |
| Virginia Union | ❌ | — | — | ✓ |
| Rockford College | ❌ | — | — | ✓ |
| Blue Mountain | ❌ | — | — | ✓ |
| CCNY | ❌ | — | — | ✓ |

---

## 待 VPN 批量下载（~117 卷）

| 大学 | 卷数 | 来源 | 优先级 |
|------|------|------|--------|
| William & Mary | ~27 | IA | 高 |
| Columbia | ~15 | HathiTrust | 高 |
| Johns Hopkins | ~9+ | JScholarship | 高 |
| Florida State | ~19 | IA | 中 |
| NC Women | ~18 | IA | 中 |
| Lander | 8 | scmemory.org | 中 |
| Georgia 1916 | 1 | HathiTrust | 低 |

## 待手动/特殊处理

| 大学 | 卷数 | 来源 | 说明 |
|------|------|------|------|
| William Jewell | ~13+ | jewell.digitalmobius.org | 网站 JS 渲染，curl 不可抓取，需手动浏览或 Selenium |
| Tulane | 29 | 不明 | 待补 LOG |
| Howard College | 13 | 不明 | 待补 LOG |
| Loyola | 7 | 不明 | 待补 LOG |

---

## 本地网络状况备忘

| 站点 | 状态 | 对应大学 |
|------|------|----------|
| texashistory.unt.edu | ✅ | Austin College |
| exhibit.xavier.edu | ✅ | St Xavier |
| dlg.galileo.usg.edu | ✅ | Georgia (UGA) |
| jewell.digitalmobius.org | ✅ (JS渲染) | William Jewell |
| lib.digitalnc.org | ✅ (重定向到 IA) | NC Women |
| scmemory.org | ❌ 超时 | Lander |
| archive.org | ❌ DNS污染 | WM, FSU, NCW |
| catalog.hathitrust.org | ❌ 403 | Columbia |
| jscholarship.library.jhu.edu | ❌ 403 | Johns Hopkins |

---

## 下次启动 Prompts

### 场景 A：VPN 已开，批量下载
```
VPN 已开，运行 new_yearbook/download_all_vpn.py 批量下载。
```
### 场景 B：补搜 Tulane/Howard/Loyola LOG
```
补搜 Tulane、Howard College、Loyola University 的年刊信息，写 LOG。参考 new_yearbook/SESSION_SUMMARY_2026-05-01.md。
```
### 场景 C：手动下载 William Jewell
```
打开 jewell.digitalmobius.org 搜索 Tatler，手动下载 William Jewell College 年刊。
```

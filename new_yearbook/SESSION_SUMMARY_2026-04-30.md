# Yearbook 搜索 Session 总结 — 2026-04-30

## 当前状态

### 1. Austin College（本地下载中，无需 VPN）
- **来源**：UNT Portal to Texas History（本地网络可直连）
- **年刊名**：The Chromascope
- **进度**：22/28 已完成（1901–1924，缺失 1904/1918），后台继续下载中
- **下载器**：`download_unt_yearbook.py`
- **检查进度**：`python3 download_unt_yearbook.py --progress`
- **预计剩余**：6 册（1925–1930），约 1 小时
- **恢复命令**：`python3 download_unt_yearbook.py`（自动跳过已下载的 22 册）

### 2. VPN 批量下载（已整理，待 VPN 开启后运行）
一键命令：`python3 download_all_vpn.py`

| 大学 | 年刊 | 年份 | 来源 | 待下卷数 |
|------|------|------|------|----------|
| William & Mary | Colonial Echo | 1901–1930 (无 1904) | IA | ~27 |
| Columbia | The Columbian | 1901–1930 | HathiTrust | ~15 |
| Johns Hopkins | Hullabaloo | 1901–1930 | JScholarship | ~9+ |
| Georgia | Pandora | 1901–1930 (无 1908/1916) | DLG | 28 |
| Florida State | Argo/Flastacowo | 1901–1930 | IA | ~19 |
| North Carolina Women | Pine Needles/Carolinian | 1901–1930 | IA | ~23 |

### 3. 之前 session 已有 PDF（来源不明，待整理 LOG）
| 大学 | PDF 数 |
|------|--------|
| Tulane University | 29 (1902–1930) |
| Howard College | 13 |
| Loyola University | 7 |
| Lander College | 1 |
| William Jewell College | 0 |

### 4. 已确认无可用年刊
- Fordham University（有 LOG，无公开数字化）
- Virginia Union University（有 LOG，无公开数字化）
- Rockford College（有 LOG，IA 仅 1950+）
- Blue Mountain Female College（有 LOG，无 yearbook 仅 catalogue）

### 5. 尚未搜索的大学
- St Xavier College
- College of the City of New York
- North Carolina College for Women（IA identifier 已推断但未确认）

---

## 本地网络状况备忘

| 站点 | 状态 |
|------|------|
| archive.org | DNS 污染，超时 |
| openlibrary.org | DNS 污染，超时 |
| catalog.hathitrust.org | HTTP 403 Cloudflare |
| jscholarship.library.jhu.edu | HTTP 403 |
| jhir.library.jhu.edu | HTTP 403 |
| diginole.lib.fsu.edu | HTTP 403 |
| dspace.swem.wm.edu | 超时 |
| **texashistory.unt.edu** | **可访问** |
| dlg.galileo.usg.edu | 间歇性 SSL 干扰 |
| libraries.wm.edu | 可访问 |
| library.columbia.edu | 可访问 |

---

## 脚本说明

```
new_yearbook/
├── download_unt_yearbook.py    # Austin College 下载（UNTPortal，无需VPN）
├── download_all_vpn.py         # 一键批量下载（需VPN）
├── download_uga_pandora.py     # UGA 单独下载（DLG，需稳定网络）
└── *_LOG.md                    # 每个大学的详细搜索日志
```

---

## 下次启动 Prompts

### 场景 A：继续搜未完成的大学
```
继续搜索 yearbook。从 St Xavier College、City College of New York、North Carolina College for Women 开始。参考 new_yearbook/SESSION_SUMMARY_2026-04-30.md 了解当前进度。
```

### 场景 B：VPN 已开启，批量下载
```
VPN 已开，运行 new_yearbook/download_all_vpn.py 批量下载所有大学 yearbook。
```

### 场景 C：检查 Austin College 是否完成
```
检查 Austin College yearbook 下载进度，如果完成则整理结果。
```

# Johns Hopkins University Yearbooks 1901–1930 — 工作日志

> 目标目录：`new_yearbook/Johns_Hopkins_Yearbooks/`
> 命名规范：`Johns Hopkins University YYYY.pdf`

---

## 结论先行

**下载成功：0 册（JHU JScholarship 被 block，需 VPN）**

- JHU 年刊名 **"Hullabaloo"**（1894 年起，前身为 1889 年的 "Debutante"）
- **不在 Internet Archive**，唯一数字来源为 **JScholarship**（JHU 机构库）
- JScholarship（`jscholarship.library.jhu.edu`）和 JHIR（`jhir.library.jhu.edu`）均 **HTTP 403**
- 1901–1930 间的卷次已确认存在多个数字版，handle 已整理完毕

---

## 二、检索结果

### Tier 1 — Internet Archive
- **不在 IA**："Hullabaloo" yearbook 未上传至 Internet Archive

### Tier 2 — JHU 官方数字仓库
| 端点 | 状态 |
|---|---|
| `jscholarship.library.jhu.edu` | **HTTP 403**（Cloudflare block） |
| `jhir.library.jhu.edu` | **HTTP 403** |
| `library.jhu.edu` | **HTTP 403** |
| `exhibits.library.jhu.edu` | **HTTP 200**（但仅供在线浏览，无 PDF 直下） |

### Tier 3 — HathiTrust
- 未探测（JHU 已有官方仓库）

---

## 三、已确认的数字版卷次（JScholarship）

Collection handle: `https://jscholarship.library.jhu.edu/handle/1774.2/37597`

| 年份 | JScholarship Handle / UUID |
|------|---------------------------|
| 1900 | `items/822e1948-9397-4b06-9582-36da8796b1d7` |
| 1901 | `items/e88e70d4-dffb-4cac-b3f3-2bfba853f8ba` |
| 1902 | `items/914a7d04-f3b9-4274-93e9-f766c5933a9e` |
| 1903 | `items/1f255b1e-636d-4f5e-8040-1d218495d364` |
| 1906 | `items/1e4b7f13-9bc8-41cb-81ae-7271834ea434` |
| 1917 | `handle/1774.2/37697` |
| 1918 | `handle/1774.2/37692` |
| 1919 | `handle/1774.2/37703` |
| 1920 | `items/3b52df96-f10f-4819-af60-6457e95e9142` |

**注意**：JScholarship 使用的是 DSpace，PDF 下载路径为：
`https://jscholarship.library.jhu.edu/items/<uuid>/full`
或通过 handle: `https://jscholarship.library.jhu.edu/handle/1774.2/XXXXX`

完整年份列表需要通过 VPN 访问 collection home 后确认。

---

## 四、年刊名历史

- **1889**：Debutante（第一本年刊）
- **1890–1893**：Hopkins Medley / Hopkinsian（短命名）
- **1894–至今**：Hullabaloo

## 五、VPN 下载方案

```
# 单册下载示例
curl -o "Johns Hopkins University 1901.pdf" \
  "https://jscholarship.library.jhu.edu/items/e88e70d4-dffb-4cac-b3f3-2bfba853f8ba/full"
```

## 六、建议

1. VPN 环境下访问 JScholarship collection 获取完整年份列表
2. 联系 JHU Archives：`archives@lists.johnshopkins.edu`

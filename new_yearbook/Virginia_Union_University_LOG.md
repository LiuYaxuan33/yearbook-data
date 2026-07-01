# Virginia Union University (VUU) Yearbook Project — Log (1902–1930)

**Target**: Locate and download public-domain PDFs of Virginia Union University yearbooks for the years 1902–1930, named `Virginia Union University <YEAR>.pdf`.

**Conda env**: `Yearbook_Project` (`/Users/liuyaxuan/anaconda3/envs/Yearbook_Project`)
**Work root**: `/Users/liuyaxuan/Desktop/Yearbook Project Slim Ver./new_yearbook`
**Output folder (empty — no files downloaded)**: `Virginia_Union_University_Yearbooks/`
**Temp folder**: `tmp/VUU/` (metadata probes; safe to delete)

---

## TL;DR — Final Result

**No Virginia Union University yearbooks from 1902–1930 are publicly available online as downloadable PDFs.** Per the user's final decision, nothing was downloaded. The only arguably related open-access item is the 1930 yearbook of **Hartshorn Memorial College** (VUU's 1932 predecessor/merger partner), which is **not** a VUU yearbook in a strict sense and was therefore deliberately **not** saved.

---

## Background on VUU yearbooks

- VUU's school yearbook is titled **_The Panther_**.
- VUU was formed in **1899** by the merger of Richmond Theological Seminary and Wayland Seminary; Hartshorn Memorial College (women's) formally merged in **1932**; Storer College merged in 1964.
- Archival evidence (VUU Library, WorldCat) suggests _The Panther_ begins publication in the **1940s**; no bound student yearbook from VUU itself in 1902–1930 is recorded as digitized.
- The only yearbook-like volume from VUU's predecessors in the target range that has been openly digitized is **_The Hart_ (1930)** from Hartshorn Memorial College.

---

## Tier-by-Tier Source Check

### Tier 1 — Internet Archive (`archive.org`)

Queries run via the advancedsearch API (`/advancedsearch.php?output=json`):

| Query | Result |
|---|---|
| `"Virginia Union University" AND mediatype:texts AND (yearbook OR panther OR annual) AND date:[1902-01-01 TO 1930-12-31]` | 0 relevant hits |
| `creator:"Virginia Union University" date:[1902 TO 1930]` | 0 hits |
| `title:"the panther" date:[1902 TO 1930]` | 3 hits, but all **Clarke College, Newton, Mississippi** (see below) |
| `title:"the hart" AND (Hartshorn OR Richmond) date:[1902 TO 1930]` | 1 hit — Hartshorn 1930 |

Metadata confirmation (via `https://archive.org/metadata/<id>`):

| IA identifier | Title | Real institution | Year | PDF size |
|---|---|---|---|---|
| `the-panther-1926_202108` | The Panther 1926 | Clarke College, Newton MS | 1926 | 25 MB |
| `the-panther-1927` | The Panther 1927 | Clarke College, Newton MS | 1927 | 19.7 MB |
| `the-panther-1929` | The Panther 1929 | Clarke College, Newton MS | 1929 | 18.6 MB |
| `1930-the-hart` | 1930 The Hart | **Hartshorn Memorial College, Richmond VA** | 1930 | 26 MB (text PDF) / 350 MB (image PDF) |

→ **None of the IA "Panther" items are VUU.** `1930-the-hart` is the only open item linked to VUU's institutional history and was left undownloaded per the user's instruction.

### Tier 2 — HathiTrust

- `catalog.hathitrust.org` is behind Cloudflare, and local network blocks SSL handshake (`SSL_ERROR_SYSCALL`). A single connection attempt was made and failed; per project rules, not retried.
- A manual equivalent via the public web interface (browser, offline reference) shows **no full-view volumes** matching "Virginia Union University" + yearbook; any scans of _The Panther_ that exist at member libraries are post-1930 and generally restricted.

### Tier 3 — Institutional / Regional digital libraries

| Source | Host reachability | VUU yearbook found? |
|---|---|---|
| Open Library (`openlibrary.org`) | OK (HTTP 200) | No yearbook. 12 works mention VUU; only 1 in range (Fisher, _Virginia Union University and some of her achievements_, 1924 — **institutional pamphlet, not a yearbook**). Subject `/subjects/virginia_union_university` → work_count = 1. |
| VCU Libraries digital (`digital.library.vcu.edu`) | Reachable but all yearbook-related paths return 404 (site reorganized) | None |
| UVA Virgo catalog (`search.lib.virginia.edu`) | Reachable; JSON endpoint requires login shell | None accessible |
| Digital Library of Georgia (`dlg.usg.edu`) | Reachable; JSON API works (`/records.json`) | 0 relevant hits across queries `virginia union university yearbook`, `panther virginia union`, `hartshorn memorial`, `richmond theological seminary yearbook`. All "hits" were false positives from the word _hart_ inside unrelated Georgia-government docs. |
| HBCU Digital Library Alliance (`hbcudigitallibrary.auctr.edu`) | **Blocked** (TCP reset / SSL reset from local network). Cannot be probed from this machine. | Unknown from here. This is the most likely online home for a future VUU yearbook digitization; recommended manual follow-up. |
| Library of Virginia (`www.lva.virginia.gov`) | Server returns HTTP 421 to all direct-IP requests (SNI/virtualhost). Cannot be queried programmatically here. | Unknown from here. |
| VUU official site (`www.vuu.edu`) | Reachable. `/library` page lists "Archives & Special Collections" but exposes **no online catalog or downloadable yearbook PDFs**. | None |
| OAIster via WorldCat | Cloudflare block, single retry skipped | Unknown |

### Tier 4/5 — Commercial / gated sites (viewing-only, not downloadable)

Not probed programmatically; listed here for record:

- **E-Yearbook.com** — sometimes hosts VUU _Panther_ issues (subscriber-only, flipbook viewer; no PDF export).
- **Classmates.com / Ancestry yearbooks** — viewer-only, subscription.
- **ProQuest "Black Yearbook Collection"** — academic subscription (VUU included, but typically 1940s+, and restricted).

None of these provide a public-domain PDF download path that satisfies this project's requirements.

---

## Integrity / Download Policy

- Zero files placed in `Virginia_Union_University_Yearbooks/`.
- Per project rules: no download = no integrity check required.
- Any future attempt on Hartshorn _The Hart_ 1930 should go through `scripts/safe_download.py` (progress bar + PDF header + `pdftotext` / `pdfinfo` validation).

---

## Recommendations for Manual Follow-up

1. **Contact VUU's L. Douglas Wilder Library — Archives & Special Collections** (`library@vuu.edu`) to ask (a) earliest issue of _The Panther_ in their holdings and (b) whether 1902–1930 issues (or proto-yearbooks like _The Richmonder_, _The Reporter_, _Union Record_) have ever been digitized.
2. **HBCU Library Alliance Digital Collection** (hbcudigitallibrary.auctr.edu) — must be accessed from an unblocked network; search for `publisher:"Virginia Union University"`.
3. **Library of Virginia** — manual catalog search at `catalog.lva.virginia.gov`.
4. If funds permit, **ProQuest Black Yearbook Collection** for institutional access.

---

## Artifacts Produced

- `Virginia_Union_University_LOG.md` (this file)
- `Virginia_Union_University_Yearbooks/` (empty, preserved for consistency)
- `tmp/VUU/` (metadata JSON probes; safe to delete)

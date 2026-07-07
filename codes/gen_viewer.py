#!/usr/bin/env python3
"""
Generate a standalone yearbook data viewer.

Common use:
  python codes/gen_viewer.py

Include newly generated OCR JSON files:
  python codes/gen_viewer.py --new-data outputs_liuyaxuan

The output HTML embeds all selected JSON data, so it can be opened by
double-clicking and shared as a single file.
"""

import argparse
import json
import os
import re
import sys


DEFAULT_DATA_DIRS = ["all_data_by Univ_adjusted_final", "outputs_liuyaxuan"]
DEFAULT_OUTPUT = "yearbook_viewer_standalone.html"
YEAR_FILE_RE = re.compile(r"^(.+)_(\d{4})\.json$", re.IGNORECASE)
GENERIC_DATA_DIRS = {
    "all_data",
    "all_data_by univ_adjusted_final",
    "data",
    "json",
    "ocr",
    "outputs",
    "outputs_liuyaxuan",
    "results",
}
KNOWN_GENDERS = {"Male", "Female", "Unknown"}


# ---------------------------------------------------------------------------
# Data discovery
# ---------------------------------------------------------------------------

def scan_data(paths, merge_policy="replace"):
    """
    Scan JSON data from files/directories.

    Supported layouts:
      all_data_by Univ_adjusted_final/Clemson University/Clemson_1901.json
      outputs_liuyaxuan/Clemson University_1910.json
      any/single_file_1910.json

    Later paths win by default for the same school/year, which lets new OCR
    results replace an older version in the generated viewer.
    """
    index = {}
    all_data = {}
    manifest = []

    for source_root in ordered_existing_paths(paths):
        if os.path.isfile(source_root):
            json_files = [source_root]
            root_for_inference = os.path.dirname(source_root) or "."
            prefer_file_school = True
        else:
            json_files = find_json_files(source_root)
            root_for_inference = source_root
            prefer_file_school = False

        if not json_files:
            print(f"Skipping empty source: {source_root}", file=sys.stderr)
            continue

        for json_file in json_files:
            records = load_records(json_file)
            if records is None:
                continue

            school, year = infer_school_year(
                json_file,
                root_for_inference,
                records,
                prefer_file_school=prefer_file_school,
            )
            if not school or not year:
                print(f"Skipping file with unknown school/year: {json_file}", file=sys.stderr)
                continue

            normalized_records = normalize_records(records, school, year, json_file, source_root)
            if not normalized_records:
                continue

            all_data.setdefault(school, {})
            if year in all_data[school] and merge_policy == "append":
                all_data[school][year].extend(normalized_records)
            else:
                all_data[school][year] = normalized_records

            manifest.append({
                "school": school,
                "year": year,
                "records": len(normalized_records),
                "source": json_file,
            })

    for school, by_year in all_data.items():
        index[school] = sorted(by_year.keys())

    return dict(sorted(index.items())), all_data, manifest


def ordered_existing_paths(paths):
    seen = set()
    for path in paths:
        if not path:
            continue
        normalized = os.path.normpath(path)
        if normalized in seen:
            continue
        seen.add(normalized)
        if not os.path.exists(normalized):
            print(f"Skipping missing source: {normalized}", file=sys.stderr)
            continue
        yield normalized


def find_json_files(root):
    files = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if not filename.lower().endswith(".json"):
                continue
            if filename in {"schools_index.json"}:
                continue
            files.append(os.path.join(current_root, filename))
    return sorted(files)


def load_records(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Skipping {json_file}: {exc}", file=sys.stderr)
        return None

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("students", "records", "data"):
            if isinstance(data.get(key), list):
                return data[key]

    print(f"Skipping {json_file}: expected a JSON list or object with students/records/data", file=sys.stderr)
    return None


def infer_school_year(json_file, root, records, prefer_file_school=False):
    filename = os.path.basename(json_file)
    match = YEAR_FILE_RE.match(filename)
    file_school = clean_school_name(match.group(1)) if match else ""
    file_year = match.group(2) if match else ""

    parent = os.path.basename(os.path.dirname(json_file))
    root_base = os.path.basename(os.path.normpath(root))
    rel_dir = os.path.relpath(os.path.dirname(json_file), root)

    if prefer_file_school and file_school:
        school = file_school
    elif rel_dir != ".":
        school = parent
    elif file_school and (
        root_base.lower() in GENERIC_DATA_DIRS
        or file_school.lower() not in root_base.lower()
    ):
        school = file_school
    elif root_base and root_base.lower() not in GENERIC_DATA_DIRS and not os.path.isfile(root):
        school = root_base
    else:
        school = file_school

    first_record = first_dict(records)
    if first_record:
        school = school or clean_school_name(first_record.get("University") or first_record.get("university") or "")
        file_year = file_year or normalize_year(first_record.get("year"))

    return school, file_year


def first_dict(records):
    for record in records:
        if isinstance(record, dict):
            return record
    return None


def normalize_year(value):
    if value is None:
        return ""
    match = re.search(r"\b(\d{4})\b", str(value))
    return match.group(1) if match else ""


def clean_school_name(value):
    value = str(value or "").strip()
    if "_" in value and " " not in value:
        value = value.replace("_", " ")
    return re.sub(r"\s+", " ", value).strip()


def normalize_records(records, school, year, json_file, source_root):
    normalized = []
    source_label = os.path.basename(os.path.normpath(source_root)) or source_root

    for record in records:
        if not isinstance(record, dict):
            continue

        row = dict(record)
        row.setdefault("University", school)
        row.setdefault("year", year)
        row.setdefault("_source_file", os.path.relpath(json_file))
        row.setdefault("_source", source_label)

        normalize_gender_fields(row)
        normalized.append(row)

    return normalized


def normalize_gender_fields(row):
    old_gender = normalize_gender(row.get("gender"))
    by_name = normalize_gender(row.get("gender_by_name"))
    by_portrait = normalize_gender(row.get("gender_by_portrait"))

    if by_name == "Unknown" and old_gender != "Unknown":
        by_name = old_gender
    if old_gender == "Unknown" and by_name != "Unknown":
        old_gender = by_name

    row["gender"] = old_gender
    row["gender_by_name"] = by_name
    row["gender_by_portrait"] = by_portrait


def normalize_gender(value):
    if not isinstance(value, str):
        return "Unknown"
    value = value.strip().lower()
    if value == "male":
        return "Male"
    if value == "female":
        return "Female"
    return "Unknown"


def count_records(all_data):
    return sum(len(records) for by_year in all_data.values() for records in by_year.values())


def count_year_files(index):
    return sum(len(years) for years in index.values())


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

def build_standalone_html(index, all_data, manifest, title):
    total_records = count_records(all_data)
    total_schools = len(index)
    total_years = count_year_files(index)

    index_json = to_js_json(index)
    data_json = to_js_json(all_data)
    manifest_json = to_js_json(manifest)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc_html(title)}</title>
<style>
{build_css()}
</style>
</head>
<body>
<header>
  <div>
    <h1>{esc_html(title)}</h1>
    <div class="sub">{total_schools} schools · {total_years} year files · {total_records:,} records</div>
  </div>
  <button type="button" id="exportBtn" class="btn">Export CSV</button>
</header>

<main>
  <section class="summary" id="summary"></section>

  <section class="controls">
    <label>School<select id="schoolSelect"><option value="">Select school</option></select></label>
    <label>Year<select id="yearSelect" disabled><option value="">Select year</option></select></label>
    <label>Gender Source<select id="genderSource">
      <option value="gender_by_name">Name</option>
      <option value="gender_by_portrait">Portrait</option>
      <option value="gender">Legacy</option>
    </select></label>
    <label>Gender<select id="genderFilter">
      <option value="all">All</option>
      <option value="Female">Female</option>
      <option value="Male">Male</option>
      <option value="Unknown">Unknown</option>
    </select></label>
    <label class="search">Search<input id="searchInput" type="search" placeholder="Name, major, hometown, clubs..." disabled></label>
    <label class="check"><input type="checkbox" id="mismatchOnly"> Gender mismatch</label>
  </section>

  <section class="stats" id="stats">
    <span>Total: <strong id="totalCount">0</strong></span>
    <span>Female: <strong id="femaleCount">0</strong></span>
    <span>Male: <strong id="maleCount">0</strong></span>
    <span>Unknown: <strong id="unknownCount">0</strong></span>
    <span>Mismatches: <strong id="mismatchCount">0</strong></span>
    <span>Showing: <strong id="showingCount">0</strong></span>
  </section>

  <section class="fieldbar">
    <span>Fields</span>
    <div id="fieldToggles"></div>
    <button type="button" class="btn small" id="resetFields">Reset</button>
  </section>

  <section class="tablewrap">
    <div class="empty" id="emptyState">Select a school and year.</div>
    <table id="dataTable" hidden>
      <thead id="tableHead"></thead>
      <tbody id="tableBody"></tbody>
    </table>
  </section>
</main>

<script>
var INDEX = {index_json};
var DATA = {data_json};
var MANIFEST = {manifest_json};
{build_js()}
</script>
</body>
</html>
"""


def build_css():
    return """
:root {
  --bg: #f7f6f2;
  --panel: #ffffff;
  --text: #1f2933;
  --muted: #667085;
  --border: #d8ddd5;
  --head: #eef3ea;
  --accent: #28666e;
  --accent-soft: #e4f2f3;
  --female: #a83f66;
  --female-bg: #f8e7ef;
  --male: #315f9e;
  --male-bg: #e6eef9;
  --warn: #9a5b12;
  --warn-bg: #fff2d6;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", Arial, sans-serif;
}
header {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px 28px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
}
h1 { margin: 0; font-size: 20px; line-height: 1.2; font-weight: 650; }
.sub { margin-top: 4px; color: var(--muted); font-size: 13px; }
main { padding: 20px 28px 32px; }
.summary, .controls, .stats, .fieldbar, .tablewrap {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.summary { padding: 12px 14px; margin-bottom: 12px; color: var(--muted); font-size: 13px; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 6px 18px; }
.summary-item { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.controls {
  display: grid;
  grid-template-columns: minmax(220px, 1.2fr) 130px 150px 120px minmax(240px, 1fr) auto;
  gap: 12px;
  align-items: end;
  padding: 14px;
  margin-bottom: 12px;
}
label { display: flex; flex-direction: column; gap: 5px; color: var(--muted); font-size: 12px; font-weight: 650; text-transform: uppercase; letter-spacing: 0.03em; }
label.check { flex-direction: row; align-items: center; align-self: center; color: var(--text); font-size: 13px; text-transform: none; letter-spacing: 0; font-weight: 500; white-space: nowrap; }
select, input[type="search"] {
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: #fff;
  color: var(--text);
  padding: 0 10px;
  font-size: 14px;
}
select:disabled, input:disabled { opacity: 0.55; }
.btn {
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
  border-radius: 6px;
  height: 36px;
  padding: 0 13px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.btn.small {
  height: 28px;
  padding: 0 10px;
  background: #fff;
  color: var(--accent);
}
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 11px 14px;
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 13px;
}
.stats strong { color: var(--text); }
.fieldbar {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 14px;
  margin-bottom: 12px;
  font-size: 13px;
}
.fieldbar > span { color: var(--muted); font-weight: 650; }
#fieldToggles { display: flex; flex-wrap: wrap; gap: 6px; flex: 1; }
.field-toggle {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text);
  background: #fff;
  text-transform: none;
  letter-spacing: 0;
  font-weight: 500;
  cursor: pointer;
}
.tablewrap { overflow: auto; }
table { width: 100%; border-collapse: collapse; min-width: 980px; font-size: 13px; }
thead { background: var(--head); }
th, td { padding: 9px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
th { color: #485363; font-size: 12px; text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
tbody tr:hover { background: #f3f7f0; }
.empty { padding: 56px 16px; color: var(--muted); text-align: center; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 650; white-space: nowrap; }
.female { background: var(--female-bg); color: var(--female); }
.male { background: var(--male-bg); color: var(--male); }
.unknown { background: #eef0f2; color: #667085; }
.mismatch { background: var(--warn-bg); color: var(--warn); }
.tags { display: flex; flex-wrap: wrap; gap: 3px; max-width: 240px; }
.tag { background: #edf0e8; border-radius: 4px; padding: 2px 6px; font-size: 12px; }
.desc { max-width: 420px; line-height: 1.45; }
.nowrap { white-space: nowrap; }
@media (max-width: 980px) {
  header { position: static; padding: 16px; align-items: flex-start; }
  main { padding: 14px; }
  .controls { grid-template-columns: 1fr 1fr; }
  .controls .search { grid-column: 1 / -1; }
}
@media (max-width: 620px) {
  header { flex-direction: column; }
  .controls { grid-template-columns: 1fr; }
  .stats, .fieldbar { align-items: flex-start; }
}
"""


def build_js():
    return r"""
var FIELDS = [
  {key:'name', label:'Name', type:'text'},
  {key:'gender_by_name', label:'Gender (Name)', type:'gender'},
  {key:'gender_by_portrait', label:'Gender (Portrait)', type:'gender'},
  {key:'gender', label:'Gender (Legacy)', type:'gender'},
  {key:'image', label:'Image', type:'text'},
  {key:'major', label:'Major', type:'text'},
  {key:'hometown', label:'Hometown', type:'text'},
  {key:'clubs', label:'Clubs', type:'clubs'},
  {key:'description', label:'Description', type:'desc'},
  {key:'motto', label:'Motto', type:'desc'},
  {key:'birthday', label:'Birthday', type:'text'},
  {key:'enrolltime', label:'Enrollment', type:'text'},
  {key:'high school', label:'High School', type:'text'},
  {key:'nicknames', label:'Nicknames', type:'list'},
  {key:'University', label:'University', type:'text'},
  {key:'year', label:'Year', type:'text'},
  {key:'_source', label:'Source', type:'text'},
  {key:'_source_file', label:'Source File', type:'text'},
  {key:'Appearance', label:'Appearance', type:'score'},
  {key:'Character_Personality', label:'Character', type:'score'},
  {key:'Ability', label:'Ability', type:'score'},
  {key:'text', label:'Raw Text', type:'desc'}
];
var DEFAULT_FIELDS = ['name','gender_by_name','gender_by_portrait','image','major','hometown','clubs','description'];
var selectedFields = DEFAULT_FIELDS.slice();
var currentRecords = [];

function byId(id) { return document.getElementById(id); }
function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  var div = document.createElement('div');
  div.textContent = String(value);
  return div.innerHTML;
}
function normalizeGender(value) {
  value = String(value || '').trim().toLowerCase();
  if (value === 'female') return 'Female';
  if (value === 'male') return 'Male';
  return 'Unknown';
}
function genderBadge(value) {
  var gender = normalizeGender(value);
  if (gender === 'Female') return '<span class="badge female">Female</span>';
  if (gender === 'Male') return '<span class="badge male">Male</span>';
  return '<span class="badge unknown">Unknown</span>';
}
function isMismatch(record) {
  var nameGender = normalizeGender(record.gender_by_name);
  var portraitGender = normalizeGender(record.gender_by_portrait);
  return (nameGender === 'Male' || nameGender === 'Female') &&
         (portraitGender === 'Male' || portraitGender === 'Female') &&
         nameGender !== portraitGender;
}
function renderCell(record, field) {
  var value = record[field.key];
  if (field.type === 'gender') return genderBadge(value);
  if (value === null || value === undefined || value === '') return '';
  if (field.type === 'score') {
    var number = parseFloat(value);
    return isNaN(number) ? escapeHtml(value) : number.toFixed(3);
  }
  if (field.type === 'clubs' || field.type === 'list') {
    var values = Array.isArray(value) ? value : [value];
    return '<div class="tags">' + values.filter(Boolean).map(function(item) {
      return '<span class="tag">' + escapeHtml(item) + '</span>';
    }).join('') + '</div>';
  }
  if (field.type === 'desc') return '<div class="desc">' + escapeHtml(value) + '</div>';
  if (field.key === 'image' || field.key === 'year') return '<span class="nowrap">' + escapeHtml(value) + '</span>';
  return escapeHtml(value);
}
function searchableText(record) {
  return FIELDS.map(function(field) {
    var value = record[field.key];
    return Array.isArray(value) ? value.join(' ') : String(value || '');
  }).join(' ').toLowerCase();
}
function filteredRecords() {
  var genderSource = byId('genderSource').value;
  var genderFilter = byId('genderFilter').value;
  var query = byId('searchInput').value.trim().toLowerCase();
  var mismatchOnly = byId('mismatchOnly').checked;

  return currentRecords.filter(function(record) {
    if (genderFilter !== 'all' && normalizeGender(record[genderSource]) !== genderFilter) return false;
    if (mismatchOnly && !isMismatch(record)) return false;
    if (query && searchableText(record).indexOf(query) === -1) return false;
    return true;
  });
}
function renderStats(records, filtered) {
  var genderSource = byId('genderSource').value;
  byId('totalCount').textContent = records.length;
  byId('femaleCount').textContent = records.filter(function(r) { return normalizeGender(r[genderSource]) === 'Female'; }).length;
  byId('maleCount').textContent = records.filter(function(r) { return normalizeGender(r[genderSource]) === 'Male'; }).length;
  byId('unknownCount').textContent = records.filter(function(r) { return normalizeGender(r[genderSource]) === 'Unknown'; }).length;
  byId('mismatchCount').textContent = records.filter(isMismatch).length;
  byId('showingCount').textContent = filtered.length;
}
function renderTable() {
  var filtered = filteredRecords();
  renderStats(currentRecords, filtered);

  var table = byId('dataTable');
  var empty = byId('emptyState');
  var head = byId('tableHead');
  var body = byId('tableBody');
  var fields = FIELDS.filter(function(field) { return selectedFields.indexOf(field.key) !== -1; });

  if (!currentRecords.length) {
    table.hidden = true;
    empty.hidden = false;
    empty.textContent = 'Select a school and year.';
    return;
  }
  if (!filtered.length || !fields.length) {
    table.hidden = true;
    empty.hidden = false;
    empty.textContent = !fields.length ? 'No fields selected.' : 'No matching records.';
    return;
  }

  head.innerHTML = '<tr>' + fields.map(function(field) {
    return '<th>' + escapeHtml(field.label) + '</th>';
  }).join('') + '</tr>';
  body.innerHTML = filtered.map(function(record) {
    var klass = isMismatch(record) ? ' class="mismatch"' : '';
    return '<tr' + klass + '>' + fields.map(function(field) {
      return '<td>' + renderCell(record, field) + '</td>';
    }).join('') + '</tr>';
  }).join('');
  table.hidden = false;
  empty.hidden = true;
}
function renderFieldToggles() {
  var host = byId('fieldToggles');
  host.innerHTML = '';
  FIELDS.forEach(function(field) {
    var label = document.createElement('label');
    label.className = 'field-toggle';
    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = selectedFields.indexOf(field.key) !== -1;
    checkbox.addEventListener('change', function() {
      if (checkbox.checked && selectedFields.indexOf(field.key) === -1) selectedFields.push(field.key);
      if (!checkbox.checked) selectedFields = selectedFields.filter(function(key) { return key !== field.key; });
      renderTable();
      renderFieldToggles();
    });
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(field.label));
    host.appendChild(label);
  });
}
function initSummary() {
  var schools = Object.keys(INDEX).sort();
  var items = schools.slice(0, 12).map(function(school) {
    var years = INDEX[school] || [];
    return '<div class="summary-item" title="' + escapeHtml(school) + '">' +
      escapeHtml(school) + ': ' + years.length + ' years</div>';
  }).join('');
  if (schools.length > 12) items += '<div class="summary-item">+' + (schools.length - 12) + ' more schools</div>';
  byId('summary').innerHTML = '<div class="summary-grid">' + items + '</div>';
}
function initSelectors() {
  var schoolSelect = byId('schoolSelect');
  Object.keys(INDEX).sort().forEach(function(school) {
    var option = document.createElement('option');
    option.value = school;
    option.textContent = school + ' (' + INDEX[school].length + ')';
    schoolSelect.appendChild(option);
  });
}
function onSchoolChange() {
  var school = byId('schoolSelect').value;
  var yearSelect = byId('yearSelect');
  yearSelect.innerHTML = '<option value="">Select year</option>';
  currentRecords = [];
  byId('searchInput').value = '';
  byId('searchInput').disabled = true;

  if (!school) {
    yearSelect.disabled = true;
    renderTable();
    return;
  }

  (INDEX[school] || []).forEach(function(year) {
    var count = ((DATA[school] || {})[year] || []).length;
    var option = document.createElement('option');
    option.value = year;
    option.textContent = year + ' (' + count + ')';
    yearSelect.appendChild(option);
  });
  yearSelect.disabled = false;
  renderTable();
}
function onYearChange() {
  var school = byId('schoolSelect').value;
  var year = byId('yearSelect').value;
  currentRecords = school && year && DATA[school] && DATA[school][year] ? DATA[school][year] : [];
  byId('searchInput').disabled = !currentRecords.length;
  byId('searchInput').value = '';
  renderTable();
}
function exportCsv() {
  var records = filteredRecords();
  if (!records.length) return;
  var fields = selectedFields.length ? selectedFields : DEFAULT_FIELDS;
  var rows = [fields].concat(records.map(function(record) {
    return fields.map(function(key) {
      var value = record[key];
      if (Array.isArray(value)) value = value.join('; ');
      value = String(value === null || value === undefined ? '' : value);
      return '"' + value.replace(/"/g, '""') + '"';
    });
  }));
  var csv = rows.map(function(row) { return row.join(','); }).join('\n');
  var blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
  var link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'yearbook_export.csv';
  link.click();
  URL.revokeObjectURL(link.href);
}
function init() {
  initSummary();
  initSelectors();
  renderFieldToggles();
  renderTable();
  byId('schoolSelect').addEventListener('change', onSchoolChange);
  byId('yearSelect').addEventListener('change', onYearChange);
  byId('genderSource').addEventListener('change', renderTable);
  byId('genderFilter').addEventListener('change', renderTable);
  byId('searchInput').addEventListener('input', renderTable);
  byId('mismatchOnly').addEventListener('change', renderTable);
  byId('resetFields').addEventListener('click', function() {
    selectedFields = DEFAULT_FIELDS.slice();
    renderFieldToggles();
    renderTable();
  });
  byId('exportBtn').addEventListener('click', exportCsv);
}
init();
"""


def to_js_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def esc_html(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate a standalone yearbook viewer HTML file."
    )
    parser.add_argument(
        "--data-dirs",
        nargs="*",
        default=DEFAULT_DATA_DIRS,
        help="Base JSON files/directories to include. Defaults to existing adjusted data plus outputs_liuyaxuan if present.",
    )
    parser.add_argument(
        "--new-data",
        nargs="*",
        default=[],
        help="Additional new OCR JSON files/directories. These are scanned after --data-dirs.",
    )
    parser.add_argument(
        "--merge-policy",
        choices=["replace", "append"],
        default="replace",
        help="How to handle duplicate school/year files. Default: replace with later source.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output HTML file path. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--title",
        default="Yearbook Data Viewer",
        help="Viewer title shown in the browser and page header.",
    )
    return parser


def main():
    args = build_parser().parse_args()
    paths = args.data_dirs + args.new_data

    print("Scanning data sources:")
    for path in paths:
        print(f"  - {path}")

    index, all_data, manifest = scan_data(paths, merge_policy=args.merge_policy)
    if not index:
        print("ERROR: No data found. Check --data-dirs or --new-data.", file=sys.stderr)
        return 1

    html = build_standalone_html(index, all_data, manifest, args.title)
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = len(html.encode("utf-8")) / (1024 * 1024)
    print("")
    print(f"Generated: {output_path}")
    print(f"Schools: {len(index)}")
    print(f"Year files: {count_year_files(index)}")
    print(f"Records: {count_records(all_data):,}")
    print(f"Size: {size_mb:.1f} MB")
    print("Open the HTML file directly in a browser; no server is required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

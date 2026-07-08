# Yearbook OCR and Viewer Workflow Log

Date: 2026-07-08

This note documents the current OCR and viewer workflow for collaborators.

## OCR

The OCR pipeline is in `codes/use_ocr.py`.

It now calls Gemini directly on each image and asks the model to return structured JSON in one step. The old two-step OCR plus text-structuring flow is no longer required.

Set an API key before running:

```bash
export GEMINI_API_KEY="your-api-key"
```

Run OCR for a folder of page images:

```bash
python codes/use_ocr.py -i path/to/page_images -o outputs_liuyaxuan/School_Name_1910.json
```

The default model is `gemini-3-flash-preview`. To override it:

```bash
python codes/use_ocr.py -i path/to/page_images -o outputs_liuyaxuan/School_Name_1910.json --model gemini-3-flash-preview
```

Each student record includes both:

- `gender_by_name`: inferred from the written name only
- `gender_by_portrait`: inferred from the portrait only, or `Unknown` when no clear portrait is available

## Gender mismatch check

Use `codes/check_gender_mismatch.py` after OCR to find records where the name-based and portrait-based gender values disagree.

```bash
python codes/check_gender_mismatch.py outputs_liuyaxuan/
```

By default, the script ignores `Unknown` and prints unique image names only. For details:

```bash
python codes/check_gender_mismatch.py outputs_liuyaxuan/ --details
```

To include `Unknown` in the mismatch check:

```bash
python codes/check_gender_mismatch.py outputs_liuyaxuan/ --include-unknown
```

## Standalone viewer

Use `codes/gen_viewer.py` to generate a single HTML file that can be opened directly in a browser. No server is required.

Default command:

```bash
python codes/gen_viewer.py
```

This scans:

- `all_data_by Univ_adjusted_final`
- `outputs_liuyaxuan` if it exists

The generated file is:

```text
yearbook_viewer_standalone.html
```

For new OCR data in another folder:

```bash
python codes/gen_viewer.py --new-data path/to/new_json_folder -o teacher_viewer.html
```

Supported JSON layouts:

```text
all_data_by Univ_adjusted_final/Clemson University/Clemson_1901.json
outputs_liuyaxuan/Clemson University_1910.json
path/to/Clemson University_1910.json
```

If the same school and year appear in multiple sources, later sources replace earlier ones by default. This lets new OCR output override older data in the viewer. To append instead:

```bash
python codes/gen_viewer.py --new-data path/to/new_json_folder --merge-policy append
```

The viewer includes filters for school, year, gender source, gender value, search text, and name-vs-portrait gender mismatches. It also has a CSV export button for the currently filtered table.

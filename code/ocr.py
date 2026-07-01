"""
OCR extraction from yearbook page images using OpenAI Vision API.

Supports three OCR modes:
  - PROMPT_1: Traditional Chinese vertical text
  - PROMPT_2: Table gender classification (all-male / all-female / coed)
  - PROMPT_3: Structured table → CSV (primary mode for statistical tables)

Usage:
  python code/ocr.py --image path/to/image.jpg --mode 3 --output result.csv

Environment variables:
  OCR_API_KEY        API key for the vision model (required)
  OCR_BASE_URL       API base URL (default: https://jeniya.cn/v1)
  OCR_MODEL          Model name (default: gemini-3-flash-preview)
"""

import argparse
import base64
import os
import sys

from openai import OpenAI


PROMPT_1 = """
你是一名专业的文字识别（OCR）助手。

请识别图像中的文字，并将其转写为可复制的文本。

识别规则：

1. 本图为单页竖排繁体中文文本，阅读顺序为：从右到左，每列自上而下。

2. 请严格按照原文转写：

- 保留原有的繁体字，不要转换为简体字。

- 不要自行改写、润色或纠错。

- 保留原有的标点符号与段落结构。

- 确保完整读完一列后，再换行并继续识别下一列。

3. 如果遇到模糊或无法辨认的字，请用「□」代替。

4. 输出为纯文本，不要添加任何解释说明。

请开始识别。"""

PROMPT_2 = """
图片内的表格内容统计了多所大学的人数，阅读并输出每一行是只有男性、只有女性还是男女混合的结果，输出格式为：
Line 1; All_male;
Line 2; All_female;
Line 3; Coed;
Line 4; Almost_all_male;
Line 5; Almost_all_female;
"""

PROMPT_3 = """
You are a high-precision OCR system specialized in extracting structured data from statistical tables in scanned documents.

Your task is to read the table in the provided image and convert it into a clean CSV dataset.

GENERAL INSTRUCTIONS

1. Perform accurate OCR on all text that appears inside the table.
2. Reconstruct the logical table structure before producing the final output.
3. Ensure that each row corresponds to a single entity (e.g., a university, department, or category).
4. Ensure that numbers remain aligned with the correct row label.
5. Preserve the original spelling of all text labels exactly as shown.
6. Do NOT hallucinate or infer data that is not visible in the image.

PAGE ORIENTATION

1. If the page is rotated (90°, 180°, or 270°), mentally rotate it to the correct orientation before reading.
2. If the table is sideways, read it as if it were upright.

COLUMN STRUCTURE

1. Identify the table columns from the header.
2. If the header spans multiple rows, merge them into a single clear column name.
3. Ensure that every row has the same number of columns as the header.
4. If visual spacing (instead of grid lines) separates columns, infer column boundaries carefully.

ROW ALIGNMENT

1. Maintain strict alignment between row labels and numeric values.
2. Numbers on a row must belong to the same entity in the first column.
3. If a row label appears on a previous page and only numbers appear on this page, record the row exactly as shown without guessing the missing label.

MISSING OR UNCERTAIN VALUES

1. If a cell is blank in the image, leave the CSV cell empty.
2. If a value is illegible or uncertain, leave the cell empty.
3. Never invent values.
4. Preserve missing values exactly as empty cells.

NUMBER NORMALIZATION

1. Remove thousands separators such as commas or spaces.
2. Output numbers as plain integers if possible.
3. Do not change numeric meaning.

FOOTNOTES AND NON-TABLE TEXT

1. Ignore footnotes, captions, and page numbers unless they are inside the table grid.
2. Only extract the table content.

OUTPUT FORMAT

Return ONLY CSV text.

Rules:
- First row must contain column headers.
- Use commas as separators.
- Each subsequent row must represent one row of the table.
- Do not include explanations or markdown formatting.

Example format:

Column1,Column2,Column3
Label A,123,456
Label B,78,90
Label C,,45

FINAL CHECK BEFORE OUTPUT

Before generating the CSV, verify:
- all rows have the same number of columns
- numbers align with the correct row labels
- missing values remain empty
"""

PROMPTS = {1: PROMPT_1, 2: PROMPT_2, 3: PROMPT_3}


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_ocr(image_path: str, mode: int = 3) -> str:
    """Run OCR on a single image and return the text result."""
    api_key = os.environ.get("OCR_API_KEY")
    if not api_key:
        print("Error: OCR_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("OCR_BASE_URL", "https://jeniya.cn/v1")
    model = os.environ.get("OCR_MODEL", "gemini-3-flash-preview")

    prompt = PROMPTS.get(mode, PROMPT_3)
    client = OpenAI(base_url=base_url, api_key=api_key)
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=30000,
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(
        description="OCR yearbook page images using OpenAI Vision API"
    )
    parser.add_argument(
        "--image", "-i", required=True, help="Path to the image file"
    )
    parser.add_argument(
        "--mode", "-m", type=int, choices=[1, 2, 3], default=3,
        help="OCR mode: 1=Chinese vertical, 2=gender classification, 3=table→CSV (default)"
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Output file path (default: stdout)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    result = run_ocr(args.image, mode=args.mode)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()

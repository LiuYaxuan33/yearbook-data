import argparse
import base64
import json
import os
import re
import time

from openai import OpenAI
from PIL import Image

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False


load_dotenv()

# ============================================================
# API 配置
# ============================================================

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or os.getenv("OCR_API_KEY")
)
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/",
)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
REQUEST_TIMEOUT = int(os.getenv("OCR_REQUEST_TIMEOUT", "180"))


# ============================================================
# 图片压缩配置
# ============================================================

MAX_SIZE = 6 * 1024 * 1024  # 6MB
JPEG_START_QUALITY = 90
JPEG_MIN_QUALITY = 30
JPEG_STEP = 5


# ============================================================
# 支持的图片格式
# ============================================================

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp", ".jp2")
MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    ".jp2": "image/jpeg",
}

STUDENT_FIELDS = [
    "name",
    "nicknames",
    "gender_by_name",
    "gender_by_portrait",
    "high school",
    "motto",
    "birthday",
    "hometown",
    "enrolltime",
    "major",
    "clubs",
    "description",
]
LIST_FIELDS = {"nicknames", "clubs"}


STUDENT_SCHEMA = {
    "type": "object",
    "properties": {
        "students": {
            "type": "array",
            "description": "Student entries extracted from the page image.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Student name, usually formatted as Last, First Middle.",
                    },
                    "nicknames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Nicknames, usually shown in quotation marks.",
                    },
                    "gender_by_name": {
                        "type": "string",
                        "description": "Infer gender from the student's name only: Male, Female, or Unknown.",
                    },
                    "gender_by_portrait": {
                        "type": "string",
                        "description": "Infer gender from the visible portrait only: Male, Female, or Unknown. Use Unknown if there is no portrait, no clear face, or the portrait cannot be matched to this entry.",
                    },
                    "high school": {
                        "type": "string",
                        "description": "High school or preparatory school, if shown.",
                    },
                    "motto": {
                        "type": "string",
                        "description": "Quoted motto or epigraph, if shown.",
                    },
                    "birthday": {
                        "type": "string",
                        "description": "Birth date in YYYY-MM-DD when inferable, otherwise keep empty.",
                    },
                    "hometown": {
                        "type": "string",
                        "description": "Birthplace or hometown, preserving city/state wording.",
                    },
                    "enrolltime": {
                        "type": "string",
                        "description": "Enrollment time or class entry time, preserving original wording.",
                    },
                    "major": {
                        "type": "string",
                        "description": "Major, course, degree, school, or college information.",
                    },
                    "clubs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Clubs, societies, offices, athletics, military ranks, and activities.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Evaluative biographical description, excluding fields already extracted above.",
                    },
                },
                "required": STUDENT_FIELDS,
            },
        }
    },
    "required": ["students"],
}


EXTRACT_SYSTEM_PROMPT = """\
You are a careful yearbook OCR and structured data extraction engine.

Read the page image directly and extract every student/person entry into structured JSON.
Do OCR, cleanup, entry separation, and field extraction in this single step.

Return data through the provided function only. Do not omit visible student entries.
"""


EXTRACT_USER_PROMPT = """\
Extract all student/person entries from this yearbook image.

Rules:
1. Read multi-column layouts in natural order: left to right, top to bottom.
2. Keep the original information. Correct only obvious OCR mistakes, such as 1/l, 0/O, rn/m, broken line wraps, and clear capitalization errors.
3. If a school/college/department heading applies to entries on the page, include it in each affected entry's "major" field unless a more specific field is clearly better.
4. Field order must be:
   name, nicknames, gender_by_name, gender_by_portrait, high school, motto, birthday, hometown, enrolltime, major, clubs, description.
5. Use empty string for missing scalar fields and [] for missing list fields.
6. "gender_by_name" must be "Male", "Female", or "Unknown", inferred only from the written name.
7. "gender_by_portrait" must be "Male", "Female", or "Unknown", inferred only from the portrait linked to that entry. Use "Unknown" if there is no visible portrait, the face is unclear, the page has unmatched group photos, or the portrait cannot be confidently matched to this student.
8. Do not let the name influence "gender_by_portrait", and do not let the portrait influence "gender_by_name".
9. "birthday" should be YYYY-MM-DD only when the date is clear; otherwise use "".
10. "motto" should contain quoted motto-like text only. Preserve punctuation but do not treat every quote as a motto if it is clearly a nickname or club.
11. "clubs" should include societies, offices, athletics, military ranks, committees, publications, fraternities, sororities, and other activities.
12. "description" should be full readable sentences from the biography/evaluation, with line breaks removed. Do not repeat name, birthday, hometown, major, or clubs unless they are part of an inseparable sentence.
13. If the image has no student/person entries, return an empty students list.
"""


_gemini_client = None


def get_gemini_client():
    """创建 Gemini OpenAI 兼容客户端。"""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "未找到 Gemini API key。请设置 GEMINI_API_KEY、GOOGLE_API_KEY 或 OCR_API_KEY。"
        )

    global _gemini_client
    if _gemini_client is None:
        _gemini_client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url=GEMINI_BASE_URL,
            timeout=REQUEST_TIMEOUT,
        )
    return _gemini_client


# ============================================================
# 图片处理
# ============================================================

def process_png(image_path):
    """
    PNG -> 灰度 PNG；若仍 >6MB -> 转 JPEG 并阶梯降低质量。
    返回最终图片路径（可能变成 .jpg）。
    """
    try:
        original_size = os.path.getsize(image_path)
        if original_size <= MAX_SIZE:
            print(f"  无需压缩: {os.path.basename(image_path)} ({original_size / 1024 / 1024:.2f}MB)")
            return image_path

        img = Image.open(image_path)

        img_gray = img.convert("L")
        img_gray.save(image_path, optimize=True)

        gray_size = os.path.getsize(image_path)
        print(
            f"  灰度 PNG: {os.path.basename(image_path)} "
            f"{original_size / 1024 / 1024:.2f}MB -> {gray_size / 1024 / 1024:.2f}MB"
        )

        if gray_size <= MAX_SIZE:
            return image_path

        jpeg_path = image_path.rsplit(".", 1)[0] + ".jpg"
        quality = JPEG_START_QUALITY

        while quality >= JPEG_MIN_QUALITY:
            img_gray.save(
                jpeg_path,
                format="JPEG",
                quality=quality,
                optimize=True,
                subsampling=0,
            )
            jpeg_size = os.path.getsize(jpeg_path)
            print(f"  JPEG q={quality}: {jpeg_size / 1024 / 1024:.2f}MB")
            if jpeg_size <= MAX_SIZE:
                break
            quality -= JPEG_STEP

        os.remove(image_path)
        return jpeg_path
    except Exception as e:
        print(f"  压缩失败: {os.path.basename(image_path)}, {e}")
        return image_path


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower()
    mime_type = MIME_TYPES.get(ext, "image/jpeg")
    return f"data:{mime_type};base64,{base64_image}"


# ============================================================
# Gemini 图片 -> JSON
# ============================================================

def extract_students_with_gemini(image_path, model=None):
    """直接调用 Gemini 视觉模型，从图片一步生成学生 JSON 数据。"""
    data_url = encode_image(image_path)
    selected_model = model or GEMINI_MODEL

    completion = get_gemini_client().chat.completions.create(
        model=selected_model,
        temperature=0,
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACT_USER_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "submit_yearbook_students",
                    "description": "Submit extracted student records from a yearbook page.",
                    "parameters": STUDENT_SCHEMA,
                },
            }
        ],
        tool_choice={
            "type": "function",
            "function": {"name": "submit_yearbook_students"},
        },
    )

    message = completion.choices[0].message
    if getattr(message, "tool_calls", None):
        arguments = message.tool_calls[0].function.arguments
        payload = json.loads(arguments)
    else:
        payload = parse_json_from_text(message.content or "")

    return normalize_student_payload(payload)


def parse_json_from_text(text):
    """兼容模型没有走 tool call、直接返回 JSON 文本的情况。"""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for match in re.finditer(r"[\[{]", cleaned):
            try:
                payload, _ = decoder.raw_decode(cleaned[match.start():])
                return payload
            except json.JSONDecodeError:
                continue
        raise


def normalize_student_payload(payload):
    """将模型输出统一成字段稳定的 list[dict]。"""
    if isinstance(payload, dict) and "students" in payload:
        records = payload["students"]
    elif isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = [payload]
    else:
        raise ValueError(f"Gemini 返回的 JSON 类型不合法: {type(payload).__name__}")

    if not isinstance(records, list):
        raise ValueError("Gemini 返回的 students 不是列表")

    students = []
    for record in records:
        if not isinstance(record, dict):
            continue

        if "nicknames" not in record and "nickname" in record:
            record["nicknames"] = record.get("nickname")
        if "gender_by_name" not in record and "gender" in record:
            record["gender_by_name"] = record.get("gender")

        normalized = {}
        for field in STUDENT_FIELDS:
            value = record.get(field)
            if field in LIST_FIELDS:
                normalized[field] = normalize_list(value)
            else:
                normalized[field] = normalize_scalar(value)

        for gender_field in ("gender_by_name", "gender_by_portrait"):
            if normalized[gender_field] not in {"Male", "Female", "Unknown"}:
                normalized[gender_field] = "Unknown"

        if any(normalized[field] for field in STUDENT_FIELDS if field not in LIST_FIELDS):
            students.append(normalized)

    return students


def normalize_scalar(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return " ".join(str(value).split())


def normalize_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [normalize_scalar(item) for item in value if normalize_scalar(item)]
    return [normalize_scalar(value)]


# ============================================================
# 路径工具
# ============================================================

def get_paths(university_name, year):
    """由学校名 + 年份推导默认的输入/输出路径。"""
    image_folder = os.path.join("pics", university_name, year)
    output_file = os.path.join("outputs_liuyaxuan", f"{university_name}_{year}.json")
    return image_folder, output_file


def gather_images(folder_path):
    """收集文件夹中所有图片，排除含 'clean' 的文件名。"""
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"图片目录不存在: {folder_path}")

    return sorted(
        os.path.join(folder_path, filename)
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(IMAGE_EXTENSIONS)
        and "clean" not in filename.lower()
    )


# ============================================================
# 核心流水线
# ============================================================

def run_full_pipeline(image_dir, output_file, resume=True, compress=True, model=None):
    """
    完整流水线：图片 -> Gemini -> JSON -> 保存。
    支持断点续跑（resume=True 时跳过已处理的图片）。
    """
    image_files = gather_images(image_dir)
    if not image_files:
        print("未找到支持的图片文件")
        return

    if resume and os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            all_students = json.load(f)
        print(f"续跑模式：已加载 {len(all_students)} 条已有记录")
    else:
        all_students = []

    processed_filenames = {
        entry.get("image")
        for entry in all_students
        if isinstance(entry, dict) and entry.get("image")
    }
    processed_name_keys = {name.lower() for name in processed_filenames}
    processed_stem_keys = {
        os.path.splitext(name)[0].lower()
        for name in processed_filenames
    }

    total = len(image_files)
    t_start = time.time()

    for idx, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)

        filename_key = filename.lower()
        stem_key = os.path.splitext(filename)[0].lower()

        if filename_key in processed_name_keys or stem_key in processed_stem_keys:
            print(f"[{idx}/{total}] 跳过: {filename}")
            continue

        try:
            t_img = time.time()
            print(f"[{idx}/{total}] {filename} ...", end=" ", flush=True)

            upload_path = image_path
            if compress and filename.lower().endswith(".png"):
                upload_path = process_png(image_path)
            output_filename = os.path.basename(upload_path)

            student_json = extract_students_with_gemini(upload_path, model=model)

            for item in student_json:
                item["image"] = output_filename
                all_students.append(item)

            processed_name_keys.add(output_filename.lower())
            processed_stem_keys.add(os.path.splitext(output_filename)[0].lower())

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_students, f, ensure_ascii=False, indent=2)

            elapsed = time.time() - t_img
            print(f"✓ {len(student_json)} 条 ({elapsed:.1f}s)")
        except Exception as e:
            print(f"✗ 出错: {e}")

    total_elapsed = time.time() - t_start
    print(f"\n{'=' * 50}")
    print(f"完成！共 {len(all_students)} 条记录，耗时 {total_elapsed / 60:.1f} 分钟")
    print(f"结果已保存至: {os.path.abspath(output_file)}")


# ============================================================
# CLI
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description="年鉴 OCR 流水线：图片 -> Gemini-3 视觉模型 -> JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按学校+年份（使用默认路径 pics/<name>/<year> -> outputs_liuyaxuan/<name>_<year>.json）
  python codes/use_ocr.py "Clemson University" 1910

  # 指定自定义输入/输出路径
  python codes/use_ocr.py -i pics/Clemson/1910 -o outputs/clemson_1910.json

  # 指定模型
  python codes/use_ocr.py -i pics/Clemson/1910 -o outputs/out.json --model gemini-3.5-flash

  # 不续跑（从头开始）
  python codes/use_ocr.py -i pics/Clemson/1910 -o outputs/out.json --no-resume
        """,
    )

    parser.add_argument("university", nargs="?", default=None, help="学校名称（与 year 搭配）")
    parser.add_argument("year", nargs="?", default=None, help="年份（与 university 搭配）")
    parser.add_argument("-i", "--input-dir", default=None, help="输入图片目录")
    parser.add_argument("-o", "--output-file", default=None, help="输出 JSON 文件路径")
    parser.add_argument("--model", default=GEMINI_MODEL, help=f"Gemini 模型名（默认：{GEMINI_MODEL}）")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="不续跑，从头开始处理（默认会跳过已处理的图片）",
    )
    parser.add_argument("--no-compress", action="store_true", help="跳过 PNG 压缩步骤")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.input_dir:
        image_dir = args.input_dir
    elif args.university and args.year:
        image_dir, _ = get_paths(args.university, args.year)
    else:
        parser.error("请指定 -i/--input-dir，或提供 <university> <year> 位置参数")

    if args.output_file:
        output_file = args.output_file
    elif args.university and args.year:
        _, output_file = get_paths(args.university, args.year)
    else:
        parser.error("请指定 -o/--output-file")

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    print(f"输入目录: {image_dir}")
    print(f"输出文件: {output_file}")
    print(f"模型: {args.model}")
    print("模式: 图片 -> Gemini -> JSON")
    print(f"续跑: {'否' if args.no_resume else '是'}")
    print(f"{'=' * 50}")

    run_full_pipeline(
        image_dir=image_dir,
        output_file=output_file,
        resume=not args.no_resume,
        compress=not args.no_compress,
        model=args.model,
    )


if __name__ == "__main__":
    main()

import requests
import json
import re
import argparse
import time
import random
from dotenv import load_dotenv
import os
from PIL import Image
from google import genai
from google.genai import types

load_dotenv()

# ============================================================
# API 配置
# ============================================================
Gemini_API_KEY = os.getenv("Gemini_API_KEY")
GEMINI_OCR_MODEL = os.getenv("GEMINI_OCR_MODEL", "gemini-3-flash-preview")
GEMINI_OCR_MAX_RETRIES = int(os.getenv("GEMINI_OCR_MAX_RETRIES", "3"))
PAGE_DELAY_MIN = float(os.getenv("PAGE_DELAY_MIN", "1"))
PAGE_DELAY_MAX = float(os.getenv("PAGE_DELAY_MAX", "2"))
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL_NAME = "deepseek-chat"

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
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.jp2')


# ============================================================
# 图片压缩
# ============================================================

def process_png(image_path):
    """
    PNG -> 灰度 PNG；若仍 >6MB -> 转 JPEG 并阶梯降低质量。
    返回最终图片路径（可能变成 .jpg）。
    """
    try:
        original_size = os.path.getsize(image_path)
        if original_size <= MAX_SIZE:
            print(f"  无需压缩: {os.path.basename(image_path)} ({original_size/1024/1024:.2f}MB)")
            return image_path

        img = Image.open(image_path)

        # Step 1: 转灰度 PNG
        img_gray = img.convert("L")
        img_gray.save(image_path, optimize=True)

        gray_size = os.path.getsize(image_path)
        print(f"  灰度 PNG: {os.path.basename(image_path)} "
              f"{original_size/1024/1024:.2f}MB → {gray_size/1024/1024:.2f}MB")

        if gray_size <= MAX_SIZE:
            return image_path

        # Step 2: 转 JPEG 并降低质量
        jpeg_path = image_path.rsplit(".", 1)[0] + ".jpg"
        quality = JPEG_START_QUALITY

        while quality >= JPEG_MIN_QUALITY:
            img_gray.save(jpeg_path, format="JPEG", quality=quality,
                          optimize=True, subsampling=0)
            jpeg_size = os.path.getsize(jpeg_path)
            print(f"  JPEG q={quality}: {jpeg_size/1024/1024:.2f}MB")
            if jpeg_size <= MAX_SIZE:
                break
            quality -= JPEG_STEP

        os.remove(image_path)
        return jpeg_path
    except Exception as e:
        print(f"  压缩失败: {os.path.basename(image_path)}, {e}")
        return image_path


# ============================================================
# Gemini Vision OCR（原生 API，兼容 AQ. 格式密钥）
# ============================================================

OCR_PROMPT = (
    "Read all the text in the image, preserving original line breaks. "
    "If the text is in multiple columns, read left column first, then right column. "
    "Do not add any extra explanation."
)

_gemini_client = None


def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=Gemini_API_KEY)
    return _gemini_client


def _mime_type_for_image(image_path):
    img_format = image_path.rsplit(".", 1)[-1].lower()
    if img_format == "jpg":
        img_format = "jpeg"
    if img_format in ("png", "jpeg", "webp"):
        return f"image/{img_format}"
    return "image/jpeg"


def ocr_with_gemini(image_path, max_retries=None):
    """调用 Google Gemini Vision 模型，返回图片中的纯文本。"""
    if max_retries is None:
        max_retries = GEMINI_OCR_MAX_RETRIES

    with open(image_path, "rb") as f:
        image_bytes = f.read()
    mime_type = _mime_type_for_image(image_path)

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = get_gemini_client().models.generate_content(
                model=GEMINI_OCR_MODEL,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    OCR_PROMPT,
                ],
            )
            return response.text.strip()
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                delay = 2 ** (attempt + 1)
                print(f"\n  Gemini OCR 失败 (第 {attempt + 1} 次): {e}，{delay}s 后重试...", flush=True)
                time.sleep(delay)
                continue
            raise last_error


# ============================================================
# DeepSeek 文本润色
# ============================================================

REWRITE_SYSTEM_PROMPT = """\
Perform text refinement with these priorities:
1. Fundamental Corrections:
   - Capitalize proper nouns (e.g.: john doe → John Doe, ARNOLD → Arnold)
   - Fix letter confusions (e.g.: cl → d, rn → m, 1 → l， 0 → o)
   - Correct obvious spelling errors (e.g.: hel1o → hello)
   - Complete missing initials of common surnames (e.g.: pple → Apple, Arry → Barry)

2. Paragraph Optimization:
   - Merge erroneous line breaks (e.g.: "Please submit\\nthe report" → "Please submit the report")
   - Preserve intentional paragraph breaks (e.g.: section headings)
   - Reorganize paragraphs based on semantic coherence

3. Output Requirements:
   - Maintain original information integrity
   - Return only the polished text
   - Use standard English punctuation

4. Repairing the missing text:
    - If a sentence is clearly incomplete due to OCR errors, attempt to infer and fill in the missing parts based on context.

5. Add a '#' before each entry in the output to separate them clearly. An entry typically begins with a name.

6. If at the beginning or end of the text there is information about school or college, eg. "School of Engineering", add it to every entry in the text.

Example:
[Raw OCR]
School of Engineering
PERCY, H. All. "red"
Born April l, 19O0 at New York City, New York; entered Clems
College in 1918; Electrical Course; Glee Club, Y. M. C. A., th
Band.He prefers Domestic Science because of its excellent ho
training.
"The best is yet to come."

[Refined]
#
PERCY, H. All. "red"
motto: "The best is yet to come."
School of Engineering
Born April 1, 1900 at New York City, New York; entered Clemson College in 1918; Electrical Course; Glee Club, Y. M. C. A., the Band.He prefers Domestic Science because of its excellent home training.
"""

def deepseek_rewrite(text):
    """调用 DeepSeek 对 OCR 文本进行润色修正。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers,
                                 data=json.dumps(payload), timeout=120)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"  DeepSeek 润色失败: {e}，返回原始文本")
        return text


# ============================================================
# DeepSeek 文本 → 结构化 JSON
# ============================================================

JSON_PARSE_SYSTEM_PROMPT = """\
请严格按以下规则解析学生信息为JSON格式：
1. 字段顺序必须为：name, nickname, gender, high school, motto, birthday, hometown, enrolltime, major, clubs, description
2. 姓名格式规则：
   - 检查姓氏，如果和常见姓氏相比缺失首字母（如Barry -> Arry）则补全
   - 每个单词的首字母大写，其余字母小写
   - 姓氏在前，名在后，二者以逗号隔开（即常见的排版方式）
3. 昵称识别：
   - 常在双引号中
   - 保留原有昵称
   - 将所有昵称（如有多个）以列表形式储存
4. 性别推断基于英文名常见性别（Male/Female）
5. 毕业高中识别：
   - 保留原有内容
6. 格言识别：以双引号""引起的句子
   - 只有用双引号引起的句子才应当被识别为格言
   - 保留原有标点符号
7. 生日识别：
   - 根据描述内容推断
   - 格式为YYYY-MM-DD，以字符串存储
8. 出生地识别：
    - 可能包含城市和州（如Tama, Iowa）
    - 保留原有格式，以字符串存储
9. 专业识别：
   - 如"Technology", "Liberal Arts"
   - 保留原有格式，以字符串存储
   - 如同时出现学位，如B.S."，和学院，如"School of Engineering"，把它们同时包含在专业字段中
10. 社团信息：
   - 按照原始文本中的语意提取，需要包含尽可能多的信息
   - 社团名称和职务（如President, the Band）应保留
   - 如有服役情况（如Corporal, Sergeant）或其他社团信息，应尽量提取
   - 如果有多个社团，使用列表存储
   - 没有则留空列表
   - 社团与社团之间常用逗号','隔开
11. 描述语：
   - 完整的句子
   - 去除原始换行符
   - 保留原有标点符号，如有需要，使用转义符
   - 描述语不应包含个人信息（如姓名、生日和出生地、社团参与等），只应包含评价性语句
   - 评价性语句常出现在社团信息之后
12. 保留原始信息，除非明显错误

示例输入：

PERCY, H. All. "red"
"Zeta Phi Tau"
Born April 1, 1900 at New York City, New York; entered Clemson College in 1918; Electrical Course; he is a member of Glee Club, Y. M. C. A. and the president of the Band.He prefers Domestic Science because of its excellent home training.
"The best is yet to come."——Mary Smith

示例输出：
{
    "name": "Percy, H. All.",
    "nicknames": ["red"],
    "gender": "Male",
    "motto": "\\"The best is yet to come.\\"——Mary Smith",
    "birthday": "1900-04-01",
    "hometown": "New York City, New York",
    "enrolltime": "1918",
    "major": "Electrical Course",
    "clubs": ["Glee Club", "Y. M. C. A.", "President, the Band", "Zeta Phi Tau"],
    "description": "He prefers Domestic Science because of its excellent home training."
}

只需返回JSON，不要添加任何代码块标记（如markdown格式的```json），只返回纯文本，也不要额外解释。把所有学生信息放在同一个列表中。
"""


def _clean_json_response(json_str):
    json_str = json_str.strip()
    json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
    json_str = re.sub(r'\s*```$', '', json_str)
    return json_str.strip()


def _parse_deepseek_json(json_str):
    """解析 DeepSeek 返回的 JSON，兼容单对象、列表、多个连续对象。"""
    json_str = _clean_json_response(json_str)
    if not json_str:
        raise ValueError("empty response")

    try:
        result = json.loads(json_str)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return [result]
        raise ValueError(f"unexpected JSON type: {type(result)}")
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    idx = 0
    items = []
    length = len(json_str)
    while idx < length:
        while idx < length and json_str[idx] in ' \t\n\r,':
            idx += 1
        if idx >= length:
            break
        obj, end = decoder.raw_decode(json_str, idx)
        if isinstance(obj, dict):
            items.append(obj)
        elif isinstance(obj, list):
            items.extend(x for x in obj if isinstance(x, dict))
        idx = end

    if not items:
        raise ValueError("no valid JSON objects found")
    return items


def deepseek_to_json(text, max_retries=2):
    """调用 DeepSeek 将润色后的文本解析为结构化 JSON。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": JSON_PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1
    }

    json_str = ""
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers,
                                     data=json.dumps(payload), timeout=120)
            response.raise_for_status()
            json_str = response.json()['choices'][0]['message']['content'].strip()
            return _parse_deepseek_json(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < max_retries:
                print(f"  JSON 解析失败 (第 {attempt + 1} 次): {e}，重试中...")
                time.sleep(1)
                continue
            print(f"  JSON 解析失败: {e}")
            if json_str:
                print(f"  原始返回: {json_str[:200]}...")
            return None
        except Exception as e:
            print(f"  DeepSeek 请求失败: {e}")
            return None


# ============================================================
# 路径工具
# ============================================================

def get_paths(university_name, year):
    """由学校名 + 年份推导默认的输入/输出路径。"""
    image_folder = os.path.join("pics", university_name, year)
    output_file = os.path.join("outputs_liuyaxuan", f"{university_name}_{year}.json")
    return image_folder, output_file


# ============================================================
# 核心流水线
# ============================================================

def gather_images(folder_path):
    """收集文件夹中所有图片，排除含 'clean' 的文件名。"""
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"图片目录不存在: {folder_path}")
    files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(IMAGE_EXTENSIONS) and "clean" not in f.lower()
    ])
    return files


def run_full_pipeline(image_dir, output_file, resume=True, ocr_only=False,
                      txt_only=False, json_only=False):
    """
    完整流水线：图片 → OCR → 润色 → JSON → 保存。
    支持断点续跑（resume=True 时跳过已处理的图片）。
    """
    # --- 获取图片列表 ---
    image_files = gather_images(image_dir)
    if not image_files:
        print("未找到支持的图片文件")
        return

    # --- 加载已有结果（断点续跑） ---
    if resume and os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            all_students = json.load(f)
        print(f"续跑模式：已加载 {len(all_students)} 条已有记录")
    else:
        all_students = []

    processed_filenames = {entry.get("image") for entry in all_students if "image" in entry}

    # --- 逐张处理 ---
    total = len(image_files)
    t_start = time.time()

    for idx, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)

        if filename in processed_filenames:
            print(f"[{idx}/{total}] 跳过: {filename}")
            continue

        time.sleep(random.uniform(PAGE_DELAY_MIN, PAGE_DELAY_MAX))

        try:
            t_img = time.time()
            print(f"[{idx}/{total}] {filename} ...", end=" ", flush=True)

            # Step 0: 压缩 PNG
            if filename.lower().endswith('.png'):
                image_path = process_png(image_path)

            # Step 1: OCR
            ocr_text = ocr_with_gemini(image_path)

            # 如果只做 OCR，写入 txt 并继续
            if ocr_only:
                txt_path = output_file.replace('.json', '.txt')
                with open(txt_path, "a", encoding="utf-8") as f:
                    f.write(f"=== {filename} ===\n{ocr_text}\n\n")
                elapsed = time.time() - t_img
                print(f"✓ ({elapsed:.1f}s)")
                continue

            # Step 2: 润色
            rewritten_text = deepseek_rewrite(ocr_text)

            if txt_only:
                txt_path = output_file.replace('.json', '.txt')
                with open(txt_path, "a", encoding="utf-8") as f:
                    f.write(f"=== {filename} ===\n{rewritten_text}\n\n")
                elapsed = time.time() - t_img
                print(f"✓ ({elapsed:.1f}s)")
                continue

            # Step 3: 转 JSON
            student_json = deepseek_to_json(rewritten_text)

            if json_only and student_json:
                # 只输出 JSON 但不加 image 字段
                pass

            # Step 4: 写入
            if isinstance(student_json, list):
                for item in student_json:
                    item["image"] = filename
                    all_students.append(item)
            elif isinstance(student_json, dict):
                student_json["image"] = filename
                all_students.append(student_json)
            else:
                print(f"✗ 非法结果: {type(student_json)}")
                continue

            # 实时保存
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_students, f, ensure_ascii=False, indent=2)

            elapsed = time.time() - t_img
            print(f"✓ ({elapsed:.1f}s)")

        except Exception as e:
            print(f"✗ 出错: {e}")

    # --- 收尾 ---
    total_elapsed = time.time() - t_start
    print(f"\n{'='*50}")
    print(f"完成！共 {len(all_students)} 条记录，耗时 {total_elapsed/60:.1f} 分钟")
    if not ocr_only and not txt_only:
        print(f"结果已保存至: {os.path.abspath(output_file)}")


def run_txt_to_json(txt_input_file, json_output_file):
    """从润色后的 txt 文件（# 分隔条目）解析为 JSON。"""
    with open(txt_input_file, "r", encoding="utf-8") as f:
        content = f.read()

    entries = re.split(r'#', content, flags=re.MULTILINE)
    entries = [e.strip() for e in entries if e.strip()]
    print(f"从 {txt_input_file} 中读取到 {len(entries)} 个条目")

    all_students = []
    for idx, entry in enumerate(entries, 1):
        try:
            print(f"[{idx}/{len(entries)}] 解析...", end=" ", flush=True)
            student_json = deepseek_to_json(entry)
            if isinstance(student_json, list):
                all_students.extend(student_json)
                print(f"✓ ({len(student_json)} 人)")
            elif isinstance(student_json, dict):
                all_students.append(student_json)
                print("✓ (1 人)")
            else:
                print(f"✗ 非法类型: {type(student_json)}")
        except Exception as e:
            print(f"✗ 出错: {e}")

    if all_students:
        with open(json_output_file, "w", encoding="utf-8") as f:
            json.dump(all_students, f, ensure_ascii=False, indent=2)
        print(f"\nJSON 已保存至: {os.path.abspath(json_output_file)} （共 {len(all_students)} 条）")


# ============================================================
# CLI
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description="年鉴 OCR 流水线：图片 → Gemini Vision OCR → DeepSeek 润色 → JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按学校+年份（使用默认路径 pics/<name>/<year> → outputs_liuyaxuan/<name>_<year>.json）
  python use_ocr.py "Clemson University" 1910

  # 指定自定义输入/输出路径
  python use_ocr.py -i pics/Clemson/1910 -o outputs/clemson_1910.json

  # 只做 OCR，结果写入 txt
  python use_ocr.py -i pics/Clemson/1910 -o outputs/ocr.txt --ocr-only

  # 只做 OCR + 润色（不转 JSON）
  python use_ocr.py -i pics/Clemson/1910 -o outputs/refined.txt --txt-only

  # 从已有 txt 解析 JSON
  python use_ocr.py --txt2json outputs/refined.txt -o outputs/parsed.json

  # 不续跑（从头开始）
  python use_ocr.py -i pics/Clemson/1910 -o outputs/out.json --no-resume
        """
    )

    # 位置参数（兼容旧用法）
    parser.add_argument("university", nargs="?", default=None,
                        help="学校名称（兼容旧用法，与 year 搭配）")
    parser.add_argument("year", nargs="?", default=None,
                        help="年份（兼容旧用法，与 university 搭配）")

    # 核心参数
    parser.add_argument("-i", "--input-dir", default=None,
                        help="输入图片目录")
    parser.add_argument("-o", "--output-file", default=None,
                        help="输出 JSON/TXT 文件路径")

    # 分步执行
    parser.add_argument("--ocr-only", action="store_true",
                        help="仅做 OCR，结果追加写入 txt 文件")
    parser.add_argument("--txt-only", action="store_true",
                        help="OCR + 润色，不转 JSON，结果追加写入 txt 文件")
    parser.add_argument("--txt2json", default=None, metavar="TXT_FILE",
                        help="从润色后的 txt 文件解析 JSON（需配合 -o）")

    # 其他选项
    parser.add_argument("--no-resume", action="store_true",
                        help="不续跑，从头开始处理（默认会跳过已处理的图片）")
    parser.add_argument("--no-compress", action="store_true",
                        help="跳过 PNG 压缩步骤")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --- 模式：txt → json ---
    if args.txt2json:
        output = args.output_file or args.txt2json.replace('.txt', '.json')
        run_txt_to_json(args.txt2json, output)
        return

    # --- 确定输入目录和输出文件 ---
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

    # --- 确保输出目录存在 ---
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    # --- 运行 ---
    print(f"输入目录: {image_dir}")
    print(f"输出文件: {output_file}")
    print(f"模式: {'仅OCR' if args.ocr_only else 'OCR+润色' if args.txt_only else '完整流水线'}")
    print(f"续跑: {'否' if args.no_resume else '是'}")
    print(f"{'='*50}")

    run_full_pipeline(
        image_dir=image_dir,
        output_file=output_file,
        resume=not args.no_resume,
        ocr_only=args.ocr_only,
        txt_only=args.txt_only,
    )


if __name__ == "__main__":
    main()

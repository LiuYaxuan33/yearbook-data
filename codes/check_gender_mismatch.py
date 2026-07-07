import argparse
import json
import os
import sys


KNOWN_GENDERS = {"Male", "Female"}


def iter_json_files(paths):
    for path in paths:
        if os.path.isfile(path):
            if path.lower().endswith(".json"):
                yield path
            continue

        if os.path.isdir(path):
            for root, _, filenames in os.walk(path):
                for filename in sorted(filenames):
                    if filename.lower().endswith(".json"):
                        yield os.path.join(root, filename)


def load_records(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("students"), list):
        return data["students"]
    return []


def normalize_gender(value):
    if not isinstance(value, str):
        return "Unknown"

    value = value.strip().lower()
    if value == "male":
        return "Male"
    if value == "female":
        return "Female"
    return "Unknown"


def find_mismatches(json_files, include_unknown=False):
    mismatches = []

    for json_file in json_files:
        for index, record in enumerate(load_records(json_file), 1):
            if not isinstance(record, dict):
                continue

            gender_by_name = normalize_gender(record.get("gender_by_name"))
            gender_by_portrait = normalize_gender(record.get("gender_by_portrait"))

            if not include_unknown:
                if gender_by_name not in KNOWN_GENDERS or gender_by_portrait not in KNOWN_GENDERS:
                    continue

            if gender_by_name != gender_by_portrait:
                mismatches.append(
                    {
                        "json_file": json_file,
                        "record_index": index,
                        "image": record.get("image", ""),
                        "name": record.get("name", ""),
                        "gender_by_name": gender_by_name,
                        "gender_by_portrait": gender_by_portrait,
                    }
                )

    return mismatches


def build_parser():
    parser = argparse.ArgumentParser(
        description="检查 OCR 结果中 gender_by_name 和 gender_by_portrait 不一致的学生，并输出图片名。"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="一个或多个 JSON 文件/目录；目录会递归扫描 .json 文件。",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="同时输出姓名、两个性别变量和 JSON 文件路径。",
    )
    parser.add_argument(
        "--include-unknown",
        action="store_true",
        help="把 Unknown 也纳入不一致检查；默认忽略 Unknown。",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="逐条输出所有不一致记录；默认只输出去重后的图片名。",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    json_files = list(iter_json_files(args.paths))
    if not json_files:
        print("未找到 JSON 文件", file=sys.stderr)
        return 1

    mismatches = find_mismatches(json_files, include_unknown=args.include_unknown)

    if args.details:
        rows = mismatches if args.all else dedupe_by_image(mismatches)
        for row in rows:
            print(
                f"{row['image']}\t{row['name']}\t"
                f"name={row['gender_by_name']}\tportrait={row['gender_by_portrait']}\t"
                f"{row['json_file']}"
            )
    else:
        images = [row["image"] for row in mismatches if row["image"]]
        if not args.all:
            images = sorted(set(images))
        for image in images:
            print(image)

    return 0


def dedupe_by_image(rows):
    seen = set()
    deduped = []
    for row in rows:
        image = row.get("image", "")
        if image in seen:
            continue
        seen.add(image)
        deduped.append(row)
    return deduped


if __name__ == "__main__":
    raise SystemExit(main())

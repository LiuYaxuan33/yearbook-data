import json
import os

INPUT_DIR = "all_data"     # 你要扫描的目录

RAW = 1

OUTPUT_FILE = "merged_results.json" if RAW == 0 else "merged_raw_results.json"

all_results = []
n_file = 0


def parse_university_year(filename):
    """
    从文件名 University_Year.json 解析 university 和 year
    """
    name = os.path.splitext(filename)[0]   # 去掉 .json
    if "_" not in name:
        return None, None
    univ, year = name.rsplit("_", 1)
    try:
        year = int(year)
    except ValueError:
        year = None
    return univ, year


for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        if not file.endswith(".json"):
            continue

        path = os.path.join(root, file)
        n_file += 1

        # 从文件名解析兜底 university / year
        file_univ, file_year = parse_university_year(file)

        with open(path, "r", encoding="utf8") as f:
            data = json.load(f)

            # 假定 data 是 list[dict]
            for person in data:

                if RAW == 1:
                    if "university" not in person or person["university"] == "":
                        person["university"] = file_univ

                    if "year" not in person or person["year"] == "":
                        person["year"] = file_year
                    all_results.append(person)
                    continue

                # None -> ""
                for k in person:
                    if person[k] is None:
                        person[k] = ""

                # university / year 缺失时用文件名补
                if "university" not in person or person["university"] == "":
                    person["university"] = file_univ

                if "year" not in person or person["year"] == "":
                    person["year"] = file_year

                # 兼容字段
                if "motto" not in person:
                    person["motto"] = ""

                if "prophesy" not in person:
                    person["prophesy"] = ""

                if "description" not in person and "comment" in person:
                    person["description"] = person["comment"]

                if "description" not in person:
                    person["description"] = ""

                # 构造 text
                person["text"] = (
                    person["motto"] + " "
                    + person["description"] + " "
                    + person["prophesy"]
                ).strip()

                # 与你原逻辑一致：非空才保留
                if person["text"]:
                    all_results.append(person)


with open(OUTPUT_FILE, "w", encoding="utf8") as out_file:
    json.dump(all_results, out_file, ensure_ascii=False, indent=2)

print("All done.")
print("Total records:", len(all_results))
print("Total files:", n_file)

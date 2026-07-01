import json
import pandas as pd
from collections import defaultdict

# ======================
# 参数设置
# ======================
INPUT_JSON = "merged_raw_results.json"
OUTPUT_KEY_LIST = "key_list_by_university_year.csv"

# ======================
# 读取 JSON
# ======================
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    students = json.load(f)

df = pd.DataFrame(students)


# ======================
# 辅助函数：判断字段是否“非空”
# ======================
def is_nonempty(val):
    if val is None:
        return False
    if isinstance(val, list):
        return len(val) > 0
    if isinstance(val, str):
        return val.strip() != ""
    return True

# ======================
# 统计每个 学校 × 年份 下 key 的出现情况
# ======================
records = []

grouped = df.groupby(["university", "year"])

for (univ, year), group in grouped:
    total_students = len(group)
    key_counter = defaultdict(int)

    for _, row in group.iterrows():
        for key, val in row.items():
            if is_nonempty(val):
                key_counter[key] += 1

    for key, count in key_counter.items():
        records.append({
            "university": univ,
            "year": year,
            "key": key,
            "nonempty_count": count,
            "coverage_rate": count / total_students,
            "total_students": total_students
        })

key_stats_df = pd.DataFrame(records)

# ======================
# 生成：每个 学校 × 年份 拥有哪些 key（列表形式）
# ======================
key_list_df = (
    key_stats_df
    .groupby(["university", "year"])["key"]
    .apply(lambda x: sorted(set(x)))
    .reset_index(name="keys_present")
)

# ======================
# 导出结果
# ======================
key_list_df.to_csv(OUTPUT_KEY_LIST, index=False)

print("统计完成：")
print(f"- 字段列表表：{OUTPUT_KEY_LIST}")

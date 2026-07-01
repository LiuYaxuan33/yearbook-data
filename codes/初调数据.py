import json
import os
all_results = []

file_dir = "outputs_liuyaxuan/Utah State University_1914.json"


with open(file_dir, 'r', encoding="utf8") as f:
    data = json.load(f)
    for person in data:
        if person['description'] == "" and not person["motto"] == "":
            person['description'] = person["motto"]
            person["motto"] = ""
            if "\"" in person['description']:
                person['description'] = person['description'].replace("\"", "")
        if person['high school'] == "" and not person["hometown"] == "":
            person['high_school'] = person["hometown"]
            person["hometown"] = ""
        all_results.append(person)


with open(file_dir, 'w', encoding="utf8") as out_file:
    json.dump(all_results, out_file, ensure_ascii=False, indent=2)




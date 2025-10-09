import os
import glob
import json
import re

def sorted_nicely(file_list):
    """依照數字大小排序 (避免 '10.txt' 跑在 '2.txt' 前面)"""
    return sorted(file_list, key=lambda x: int(re.search(r'(\d+)\.txt$', x).group(1)))

base_dir = "/cats/public/BenchpressDataset/elbows_flaring/subject_1_exp1/angle_dataset/rear_view"

files = {
    "right_shoulder": sorted_nicely(glob.glob(os.path.join(base_dir, "right_shoulder", "*.txt"))),
    "left_shoulder": sorted_nicely(glob.glob(os.path.join(base_dir, "left_shoulder", "*.txt"))),
    "right_elbow": sorted_nicely(glob.glob(os.path.join(base_dir, "right_elbow", "*.txt"))),
    "left_elbow": sorted_nicely(glob.glob(os.path.join(base_dir, "left_elbow", "*.txt")))
}

def read_angle_files(file_list):
    data = []
    for filepath in file_list:
        with open(filepath, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    frame, value = parts
                    data.append({"frame": int(frame), "value": float(value)})
    # 確保 frame 順序正確
    return sorted(data, key=lambda x: x["frame"])

dataset = {}
for angle_name, file_list in files.items():
    dataset[angle_name] = read_angle_files(file_list)

output_path = "/home/jeter/frame/angles_dataset.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4)

print(f"✅ 已輸出 dataset 到 {output_path}")

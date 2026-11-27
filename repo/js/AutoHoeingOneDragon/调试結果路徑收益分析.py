import os
import json
import re
import math
from collections import defaultdict

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONSTER_JSON_PATH = os.path.join(SCRIPT_DIR, "assets", "monsterInfo.json")
ROUTE_DIR = os.path.join(SCRIPT_DIR, "调试结果")
OUTPUT_FILE = os.path.join(ROUTE_DIR, "路径收益分析.txt")

# 基础收益映射（首领不参与）
BASE_REWARD = {
    "普通": 40,
    "精英": 200
}

def load_monster_data():
    """加载怪物信息，返回 {名称: (类型, 倍率)}"""
    with open(MONSTER_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    monster_dict = {}
    for item in data:
        name = item["name"]
        mtype = item["type"]
        rate = item["moraRate"]
        monster_dict[name] = (mtype, rate)
    return monster_dict

def parse_monsters_from_description(desc, file_path=None):
    """
    从描述字符串中解析怪物列表，返回 [(名称, 数量)] 列表
    支持小数数量（如 0.5只），数量向上取整为整数。
    """
    monsters = []
    match = re.search(r"包含以下怪物[：:]\s*(.*)", desc)
    if not match:
        return monsters

    content = match.group(1)
    parts = re.split(r"[、，]", content)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"(\d+(?:\.\d+)?)\s*[只个名]\s*(.+)", part)
        if m:
            count_str = m.group(1)
            name = m.group(2).rstrip("。").strip()
            try:
                count_float = float(count_str)
                count = int(math.ceil(count_float))
            except ValueError:
                count = 1
            monsters.append((name, count))
        else:
            if file_path:
                print(f"警告：{file_path} 无法解析怪物项 '{part}'")
            else:
                print(f"警告：无法解析怪物项 '{part}'")
    return monsters

def calculate_file_reward(monster_dict, file_path):
    """计算单个文件的收益，返回 {单位收益值: 数量} 字典"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    description = data.get("info", {}).get("description", "")
    if not description:
        return {}

    monster_list = parse_monsters_from_description(description, file_path)
    reward_counter = defaultdict(int)

    for name, count in monster_list:
        if name not in monster_dict:
            print(f"警告：未知怪物 '{name}' 在文件 {os.path.basename(file_path)} 中")
            continue
        mtype, rate = monster_dict[name]
        if mtype not in BASE_REWARD:
            continue
        base = BASE_REWARD[mtype]
        unit_value = int(base * rate)
        reward_counter[unit_value] += count

    return reward_counter

def format_reward_line(counter):
    """将收益计数器格式化为 '1000*2，600*3，200*1' 的形式（按收益值降序）"""
    if not counter:
        return ""
    items = sorted(counter.items(), reverse=True)  # 降序
    parts = [f"{value}*{count}" for value, count in items]
    return "，".join(parts)

def main():
    # 加载怪物数据
    if not os.path.exists(MONSTER_JSON_PATH):
        print(f"错误：找不到怪物数据文件 {MONSTER_JSON_PATH}")
        return
    monster_dict = load_monster_data()

    if not os.path.exists(ROUTE_DIR):
        print(f"错误：找不到路径目录 {ROUTE_DIR}")
        return

    # 收集所有 JSON 文件（递归遍历）
    json_files = []
    for root, dirs, files in os.walk(ROUTE_DIR):
        for file in files:
            if file.endswith(".json") and file != "路径收益分析.txt":
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ROUTE_DIR)
                json_files.append((rel_path, full_path))

    if not json_files:
        print("没有找到任何JSON文件。")
        return

    # 全局计数器
    global_counter = defaultdict(int)

    # 准备输出内容：先写文件明细
    output_lines = ["----------------"]
    for rel_path, full_path in sorted(json_files):
        reward = calculate_file_reward(monster_dict, full_path)
        # 累加到全局
        for value, count in reward.items():
            global_counter[value] += count
        reward_str = format_reward_line(reward)
        output_lines.append(f"    {rel_path}")
        output_lines.append(f"        {reward_str}")

    # 添加全局统计（前后加分隔线）
    output_lines.append("----------------")
    global_str = format_reward_line(global_counter)
    if global_str:
        output_lines.append(global_str)
    output_lines.append("----------------")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"分析完成，结果已保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
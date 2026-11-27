import os
import json

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONSTER_JSON = os.path.join(SCRIPT_DIR, "assets", "monsterInfo.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "调试结果")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "高收益精英怪.txt")

# 高收益对应的倍率（精英基础收益200，600→倍率3，400→倍率2）
HIGH_RATES = {2, 3}

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 读取怪物数据
    with open(MONSTER_JSON, "r", encoding="utf-8") as f:
        monsters = json.load(f)

    # 筛选精英且倍率符合
    names = []
    for m in monsters:
        if m.get("type") == "精英" and m.get("moraRate") in HIGH_RATES:
            names.append(m["name"])

    # 按名称排序（可选）
    names.sort()

    # 用中文全角逗号连接
    result = "，".join(names)

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"已提取 {len(names)} 个高收益精英怪，保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
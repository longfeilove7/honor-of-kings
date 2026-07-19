#!/usr/bin/env python3
"""王者荣耀智能出装推荐系统
根据英雄技能特点自动分析，匹配最优装备和铭文。
数据来源：腾讯官方API实时获取。
"""
import json
import re
import sys
import os
import urllib.request

CACHE_DIR = os.path.expanduser("~/.hermes/cache/honor-of-kings")
os.makedirs(CACHE_DIR, exist_ok=True)

# ============ 数据获取 ============

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_all_equipment():
    cache = os.path.join(CACHE_DIR, "equip.json")
    if os.path.exists(cache):
        age = __import__("time").time() - os.path.getmtime(cache)
        if age < 86400:
            with open(cache, "r") as f:
                return json.load(f)
    print("正在获取装备数据...", file=sys.stderr)
    url = "https://pvp.qq.com/web201605/js/item.json"
    items = fetch_json(url)
    equips = []
    for item in items:
        eid = item.get("item_id") or item.get("id")
        if not eid:
            continue
        try:
            detail = fetch_json(f"https://wuji-1254960240.file.myqcloud.com/smoba_weapon_detail/{eid}.json")
            attrs = detail.get("attributes", {})
            raw_attr = attrs.get("attributes", "")
            clean_attr = re.sub(r"<[^>]+>", "", raw_attr).strip()
            raw_sub = attrs.get("sub", "")
            clean_sub = re.sub(r"<[^>]+>", "", raw_sub).strip()
            equips.append({
                "id": eid,
                "name": detail.get("name", ""),
                "price": detail.get("price", 0),
                "category": {"1": "攻击", "2": "法术", "3": "防御", "4": "移动", "5": "打野", "7": "游走"}.get(str(detail.get("sub_type", "")), "其他"),
                "sub_type": str(detail.get("sub_type", "")),
                "attributes": clean_attr,
                "passive": clean_sub,
            })
        except:
            pass
    with open(cache, "w") as f:
        json.dump(equips, f, ensure_ascii=False, indent=2)
    return equips

def fetch_inscriptions():
    cache = os.path.join(CACHE_DIR, "ming.json")
    if os.path.exists(cache):
        with open(cache, "r") as f:
            return json.load(f)
    data = fetch_json("https://pvp.qq.com/web201605/js/ming.json")
    with open(cache, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def fetch_summoners():
    cache = os.path.join(CACHE_DIR, "summoner.json")
    if os.path.exists(cache):
        with open(cache, "r") as f:
            return json.load(f)
    data = fetch_json("https://pvp.qq.com/web201605/js/summoner.json")
    with open(cache, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def fetch_hero_list():
    cache = os.path.join(CACHE_DIR, "herolist.json")
    if os.path.exists(cache):
        with open(cache, "r") as f:
            return json.load(f)
    data = fetch_json("https://pvp.qq.com/web201605/js/herolist.json")
    with open(cache, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


# ============ 技能分析 ============

def analyze_hero_skills(hero):
    """分析英雄技能，提取特征标签"""
    tags = set()
    all_desc = ""
    for skill in hero.get("skills", []):
        desc = skill.get("description", "") + skill.get("name", "")
        all_desc += desc
    desc = all_desc

    phys_count = desc.count("物理伤害") + desc.count("物理攻击") + desc.count("物理加成")
    magic_count = desc.count("法术伤害") + desc.count("法术攻击") + desc.count("法术加成")

    if phys_count > 0:
        tags.add("physical")
    if magic_count > 0 and magic_count > phys_count:
        tags.add("magic")
    if "真实伤害" in desc:
        tags.add("true_damage")
    if "冷却" in desc and ("缩减" in desc or "减少" in desc or "刷新" in desc):
        tags.add("cdr_dependent")
    if "命中" in desc and "冷却" in desc:
        tags.add("cdr_dependent")
    if "普通攻击" in desc or "普攻" in desc:
        tags.add("attack_speed")
    if "暴击" in desc:
        tags.add("crit")
    if "攻速" in desc:
        tags.add("attack_speed")
    if "吸血" in desc or "回复" in desc or "回复生命" in desc:
        tags.add("sustain")
    if "护盾" in desc:
        tags.add("shield")
    if "免伤" in desc or "减伤" in desc or "霸体" in desc:
        tags.add("damage_reduce")
    if "位移" in desc or "冲刺" in desc or "突进" in desc:
        tags.add("mobile")
    if "眩晕" in desc or "击飞" in desc or "击退" in desc:
        tags.add("hard_cc")
    if "减速" in desc:
        tags.add("slow")
    if "穿透" in desc or "破甲" in desc:
        tags.add("penetration")
    if "最大生命" in desc and "%" in desc:
        tags.add("percent_damage")
    if "已损生命" in desc or "已损血" in desc:
        tags.add("execute")

    hero_type = hero.get("type", "")
    if hero_type == "法师":
        tags.add("magic")
    elif hero_type in ["战士", "刺客"]:
        tags.add("physical")
    elif hero_type == "射手":
        tags.add("physical")
        tags.add("attack_speed")
    elif hero_type == "坦克":
        tags.add("tank")
    elif hero_type == "辅助":
        tags.add("support")

    if "physical" in tags and "magic" in tags:
        if hero_type in ["射手", "战士", "刺客"]:
            tags.discard("magic")
        elif hero_type == "法师":
            tags.discard("physical")

    return tags


# ============ 智能匹配 ============

def score_equipment(equip, hero_tags, hero_type):
    score = 0
    attrs = equip.get("attributes", "") + " " + equip.get("passive", "")
    category = equip.get("category", "")
    sub_type = equip.get("sub_type", "")

    if "无象" in equip.get("name", ""):
        return -100
    if category == "法术" and "magic" not in hero_tags:
        return -100
    if category == "攻击" and hero_type == "法师" and "physical" not in hero_tags:
        return -100
    if category == "防御" and hero_type == "法师" and "tank" not in hero_tags:
        return -100
    if sub_type == "5" or category == "打野":
        return -100
    if sub_type == "7" or category == "游走":
        return -100
    if "专精" in attrs:
        return -100
    if sub_type == "4" or category == "移动":
        return 0

    phys_atk = re.search(r"\+(\d+)物理攻击", attrs)
    if phys_atk:
        val = int(phys_atk.group(1))
        if "physical" in hero_tags:
            score += val * 1.0
        if "attack_speed" in hero_tags:
            score += val * 0.5

    magic_atk = re.search(r"\+(\d+)法术攻击", attrs)
    if magic_atk:
        val = int(magic_atk.group(1))
        if "magic" in hero_tags:
            score += val * 1.2

    cdr = re.search(r"\+[\d.]+%?冷却缩减", attrs)
    if cdr:
        if "cdr_dependent" in hero_tags:
            score += 30
        elif "physical" in hero_tags or "magic" in hero_tags:
            score += 10

    if "攻击速度" in attrs:
        if "attack_speed" in hero_tags:
            score += 25
        else:
            score += 5

    if "暴击" in attrs:
        if "crit" in hero_tags:
            score += 30
        elif "attack_speed" in hero_tags:
            score += 15

    if "物理穿透" in attrs or "物理护甲穿透" in attrs:
        if "physical" in hero_tags:
            score += 20
        if "penetration" in hero_tags:
            score += 15

    if "法术穿透" in attrs:
        if "magic" in hero_tags:
            score += 20

    hp = re.search(r"\+(\d+)最大生命", attrs)
    if hp:
        val = int(hp.group(1))
        if "tank" in hero_tags or "support" in hero_tags:
            score += val * 0.05
        elif "sustain" in hero_tags or "shield" in hero_tags:
            score += val * 0.03

    phys_def = re.search(r"\+(\d+)物理防御", attrs)
    if phys_def:
        val = int(phys_def.group(1))
        if "tank" in hero_tags or "support" in hero_tags:
            score += val * 0.3
        elif "damage_reduce" in hero_tags:
            score += val * 0.15

    magic_def = re.search(r"\+(\d+)法术防御", attrs)
    if magic_def:
        val = int(magic_def.group(1))
        if "tank" in hero_tags or "support" in hero_tags:
            score += val * 0.3

    passive = equip.get("passive", "")
    if "已损生命" in passive or ("低于" in passive and "增伤" in passive):
        if "execute" in hero_tags or "physical" in hero_tags:
            score += 25
    if "吸血" in attrs or "吸血" in passive:
        if "sustain" in hero_tags:
            score += 20
        elif "attack_speed" in hero_tags:
            score += 15
    if "护盾" in passive:
        if "shield" in hero_tags:
            score += 15
    if "减伤" in passive or "免伤" in passive:
        if "damage_reduce" in hero_tags:
            score += 20
    if "最大生命" in passive and "%" in passive:
        if "percent_damage" in hero_tags:
            score += 20
    if "移动速度" in attrs or "移速" in attrs:
        if "mobile" in hero_tags:
            score += 10

    return score

def select_shoes(hero_tags, hero_type):
    if hero_type == "法师":
        return "秘法之靴"
    elif "attack_speed" in hero_tags and hero_type == "射手":
        return "急速战靴"
    elif "cdr_dependent" in hero_tags:
        return "冷静之靴"
    elif hero_type in ["坦克", "辅助"]:
        return "抵抗之靴"
    else:
        return "抵抗之靴"

def smart_build(hero, equipment):
    tags = analyze_hero_skills(hero)
    hero_type = hero.get("type", "")
    candidates = []
    for e in equipment:
        s = score_equipment(e, tags, hero_type)
        if s > 0:
            candidates.append((s, e))
    candidates.sort(key=lambda x: -x[0])

    shoes_name = select_shoes(tags, hero_type)
    build = [shoes_name]
    used = {shoes_name}
    cdr_count = 0

    for score, equip in candidates:
        name = equip["name"]
        if name in used:
            continue
        if "冷却缩减" in equip.get("attributes", ""):
            if cdr_count >= 2:
                continue
            cdr_count += 1
        cat = equip.get("category", "")
        cat_count = sum(1 for b in build if any(e["name"] == b and e.get("category") == cat for e in equipment))
        if cat_count >= 3:
            continue
        build.append(name)
        used.add(name)
        if len(build) >= 6:
            break

    if len(build) < 6:
        for score, equip in candidates:
            name = equip["name"]
            if name not in used:
                build.append(name)
                used.add(name)
                if len(build) >= 6:
                    break

    return build, tags

def smart_inscriptions(hero):
    tags = analyze_hero_skills(hero)
    hero_type = hero.get("type", "")
    inscriptions = []

    if "physical" in tags and "magic" not in tags:
        if "attack_speed" in tags or "crit" in tags:
            inscriptions.append({"name": "红月", "effect": "暴击率+0.5%, 攻击速度+1.6%"})
            inscriptions.append({"name": "鹰眼", "effect": "物理攻击力+0.9, 物理护甲穿透+6.4"})
            inscriptions.append({"name": "隐匿", "effect": "物理攻击力+1.6, 移速+1%"})
        else:
            inscriptions.append({"name": "异变", "effect": "物理攻击力+2, 物理护甲穿透+3.6"})
            inscriptions.append({"name": "鹰眼", "effect": "物理攻击力+0.9, 物理护甲穿透+6.4"})
            inscriptions.append({"name": "隐匿", "effect": "物理攻击力+1.6, 移速+1%"})
    elif "magic" in tags:
        if "cdr_dependent" in tags:
            inscriptions.append({"name": "圣人", "effect": "法术攻击力+5.3"})
            inscriptions.append({"name": "心眼", "effect": "法术攻击力+2.5, 法术护甲穿透+3.8"})
            inscriptions.append({"name": "献祭", "effect": "法术攻击力+2.4, 冷却缩减+0.7%"})
        else:
            inscriptions.append({"name": "圣人", "effect": "法术攻击力+5.3"})
            inscriptions.append({"name": "心眼", "effect": "法术攻击力+2.5, 法术护甲穿透+3.8"})
            inscriptions.append({"name": "轮回", "effect": "法术攻击力+2.4, 法术吸血+1%"})
    elif "tank" in tags or "support" in tags:
        inscriptions.append({"name": "虚空", "effect": "最大生命+37.5, 冷却缩减+0.6%"})
        inscriptions.append({"name": "调和", "effect": "最大生命+45, 生命回复+5.2, 移速+0.4%"})
        inscriptions.append({"name": "宿命", "effect": "攻击速度+1%, 最大生命+33.7, 物理防御+2.3"})
    else:
        inscriptions.append({"name": "异变", "effect": "物理攻击力+2, 物理护甲穿透+3.6"})
        inscriptions.append({"name": "鹰眼", "effect": "物理攻击力+0.9, 物理护甲穿透+6.4"})
        inscriptions.append({"name": "隐匿", "effect": "物理攻击力+1.6, 移速+1%"})

    return inscriptions, tags


# ============ 输出格式化 ============

def format_output(hero, build, inscriptions, tags):
    lines = []
    lines.append("=" * 50)
    lines.append(f"英雄: {hero['name']} ({hero.get('title', '')})")
    lines.append(f"类型: {hero.get('type', '')}")
    lines.append(f"标签: {', '.join(sorted(tags))}")
    lines.append("=" * 50)

    lines.append("\n【技能特点】")
    for skill in hero.get("skills", []):
        if skill.get("name") and skill.get("description"):
            desc = skill["description"][:80]
            lines.append(f"• {skill['name']}: {desc}...")

    lines.append("\n【铭文推荐】")
    for ins in inscriptions:
        lines.append(f"• {ins['name']}: {ins['effect']}")

    lines.append("\n【出装推荐】")
    lines.append(" → ".join(build))

    return "\n".join(lines)


# ============ 主程序 ============

def search_hero(query, hero_list):
    results = []
    for h in hero_list:
        name = h.get("cname", "") or h.get("name", "")
        title = h.get("title", "")
        if query in name or query in title:
            results.append(h)
    return results

def main():
    hero_list = fetch_hero_list()
    equipment = fetch_all_equipment()
    inscriptions_data = fetch_inscriptions()
    summoners = fetch_summoners()

    hero_details = {}
    details_cache = os.path.join(CACHE_DIR, "hero_details.json")
    if os.path.exists(details_cache):
        with open(details_cache, "r") as f:
            details_data = json.load(f)
            for h in details_data.get("heroes", []):
                hero_details[h.get("name", "")] = h

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

        if query == "--list":
            by_type = {}
            for h in hero_list:
                t = {1: "战士", 2: "法师", 3: "坦克", 4: "刺客", 5: "射手", 6: "辅助"}.get(h.get("hero_type", 0), "其他")
                name = h.get("cname", "") or h.get("name", "")
                by_type.setdefault(t, []).append(name)
            print("王者荣耀英雄列表：")
            for t, names in sorted(by_type.items()):
                print(f"\n【{t}】")
                print(f"  {', '.join(names)}")
            return

        if query == "--stats":
            print("王者荣耀数据统计：")
            print(f"  装备数量: {len(equipment)}")
            print(f"  铭文数量: {len(inscriptions_data)}")
            print(f"  召唤师技能: {len(summoners)}")
            print(f"  英雄数量: {len(hero_list)}")
            return

        if query == "--refresh":
            for f in ["equip.json", "ming.json", "summoner.json", "herolist.json", "hero_details.json"]:
                p = os.path.join(CACHE_DIR, f)
                if os.path.exists(p):
                    os.remove(p)
            print("缓存已清除，下次查询将重新获取最新数据")
            return

        results = search_hero(query, hero_list)
        if not results:
            print(f"未找到包含 '{query}' 的英雄")
            return

        for h in results:
            hero_name = h.get("cname", "") or h.get("name", "")
            hero_type = {1: "战士", 2: "法师", 3: "坦克", 4: "刺客", 5: "射手", 6: "辅助"}.get(h.get("hero_type", 0), "其他")
            detail = hero_details.get(hero_name, {})
            hero = {
                "id": h.get("ename", 0),
                "name": hero_name,
                "title": h.get("title", ""),
                "type": detail.get("type", hero_type),
                "skills": detail.get("skills", []),
            }
            build, build_tags = smart_build(hero, equipment)
            ins, ins_tags = smart_inscriptions(hero)
            all_tags = build_tags | ins_tags
            print(format_output(hero, build, ins, all_tags))
            print()
    else:
        print("王者荣耀智能出装推荐系统")
        print("=" * 50)
        print("命令：")
        print("  <英雄名>  - 智能出装推荐")
        print("  --list    - 列出所有英雄")
        print("  --stats   - 显示数据统计")
        print("  --refresh - 刷新缓存数据")
        print("=" * 50)

if __name__ == "__main__":
    main()

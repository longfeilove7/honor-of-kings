#!/usr/bin/env python3
"""王者荣耀综合出装推荐系统
综合英雄属性、装备属性、召唤师技能和铭文，给出每个英雄打不同分路时的最优套装。
"""
import json
import sys
import os

CACHE_DIR = os.path.expanduser("~/.hermes/cache/honor-of-kings")

def load_data():
    """加载所有数据"""
    data = {}
    
    # 加载装备数据
    equip_file = os.path.join(CACHE_DIR, "equip.json")
    if os.path.exists(equip_file):
        with open(equip_file, 'r', encoding='utf-8') as f:
            data['equipment'] = json.load(f)
    else:
        data['equipment'] = []
    
    # 加载铭文数据
    ming_file = os.path.join(CACHE_DIR, "ming.json")
    if os.path.exists(ming_file):
        with open(ming_file, 'r', encoding='utf-8') as f:
            data['inscriptions'] = json.load(f)
    else:
        data['inscriptions'] = []
    
    # 加载召唤师技能数据
    summoner_file = os.path.join(CACHE_DIR, "summoner.json")
    if os.path.exists(summoner_file):
        with open(summoner_file, 'r', encoding='utf-8') as f:
            data['summoners'] = json.load(f)
    else:
        data['summoners'] = []
    
    # 加载英雄详情数据
    hero_file = os.path.join(CACHE_DIR, "hero_details.json")
    if os.path.exists(hero_file):
        with open(hero_file, 'r', encoding='utf-8') as f:
            data['heroes'] = json.load(f)
    else:
        data['heroes'] = {'heroes': []}
    
    return data

def get_equipment_name(equip_id, equipment_list):
    """根据装备ID获取装备名称"""
    for equip in equipment_list:
        if str(equip.get('id')) == str(equip_id):
            return equip.get('name', equip_id)
    return equip_id

def get_hero_recommendations(hero_name, data):
    """获取英雄的出装推荐"""
    heroes = data['heroes'].get('heroes', [])
    equipment = data['equipment']
    
    for hero in heroes:
        if hero.get('name') == hero_name:
            # 解析装备ID为名称
            recommended_equips = []
            for equip_ids in hero.get('equipment_ids', []):
                equip_names = []
                for eid in equip_ids:
                    name = get_equipment_name(eid, equipment)
                    equip_names.append(name)
                recommended_equips.append(equip_names)
            
            return {
                'hero': hero,
                'recommended_equipment': recommended_equips
            }
    
    return None

def analyze_hero_role(hero):
    """分析英雄的主要分路"""
    hero_type = hero.get('type', '')
    
    # 根据英雄类型推断主要分路
    role_map = {
        '战士': ['对抗路', '打野'],
        '法师': ['中路'],
        '坦克': ['对抗路', '辅助'],
        '刺客': ['打野', '中路'],
        '射手': ['发育路'],
        '辅助': ['辅助', '游走']
    }
    
    return role_map.get(hero_type, ['未知'])

def format_hero_info(hero_data, data):
    """格式化英雄信息"""
    hero = hero_data['hero']
    recommended_equips = hero_data['recommended_equipment']
    
    # 获取英雄关系
    relationships = hero.get('relationships', {})
    
    # 分析主要分路
    roles = analyze_hero_role(hero)
    
    output = []
    output.append(f"{'='*50}")
    output.append(f"英雄: {hero['name']} ({hero['title']})")
    output.append(f"类型: {hero['type']}")
    output.append(f"推荐分路: {', '.join(roles)}")
    output.append(f"{'='*50}")
    
    # 技能信息
    output.append(f"\n【技能介绍】")
    for skill in hero.get('skills', []):
        if skill.get('name') and skill.get('description'):
            output.append(f"• {skill['name']}")
            output.append(f"  冷却: {skill.get('cooldown', '无')} | 消耗: {skill.get('cost', '无')}")
            output.append(f"  {skill['description'][:100]}...")
    
    # 铭文推荐
    output.append(f"\n【铭文推荐】")
    for ins in hero.get('inscriptions', []):
        if ins.get('name') and ins.get('effect'):
            output.append(f"• {ins['name']}: {ins['effect']}")
    
    # 出装推荐
    output.append(f"\n【出装推荐】")
    for i, equip_set in enumerate(recommended_equips):
        output.append(f"方案{i+1}: {' → '.join(equip_set)}")
    
    # 英雄关系
    output.append(f"\n【英雄关系】")
    if relationships.get('best_partners'):
        output.append(f"最佳搭档: {', '.join(relationships['best_partners'])}")
    if relationships.get('counters'):
        output.append(f"克制英雄: {', '.join(relationships['counters'])}")
    if relationships.get('countered_by'):
        output.append(f"被克制: {', '.join(relationships['countered_by'])}")
    
    return '\n'.join(output)

def search_hero(query, data):
    """搜索英雄"""
    heroes = data['heroes'].get('heroes', [])
    results = []
    
    for hero in heroes:
        name = hero.get('name', '')
        title = hero.get('title', '')
        if query in name or query in title:
            results.append(hero)
    
    return results

def list_heroes_by_type(data):
    """按类型列出英雄"""
    heroes = data['heroes'].get('heroes', [])
    by_type = {}
    
    for hero in heroes:
        hero_type = hero.get('type', '未知')
        if hero_type not in by_type:
            by_type[hero_type] = []
        by_type[hero_type].append(hero['name'])
    
    return by_type

def main():
    data = load_data()
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        
        if query == '--list':
            # 列出所有英雄
            by_type = list_heroes_by_type(data)
            print("王者荣耀英雄列表：")
            for hero_type, names in by_type.items():
                print(f"\n【{hero_type}】")
                print(f"  {', '.join(names)}")
            return
        
        if query == '--stats':
            # 显示数据统计
            print("王者荣耀数据统计：")
            print(f"  装备数量: {len(data['equipment'])}")
            print(f"  铭文数量: {len(data['inscriptions'])}")
            print(f"  召唤师技能: {len(data['summoners'])}")
            print(f"  英雄数量: {len(data['heroes'].get('heroes', []))}")
            return
        
        # 搜索英雄
        results = search_hero(query, data)
        
        if not results:
            print(f"未找到包含 '{query}' 的英雄")
            return
        
        for hero in results:
            hero_data = get_hero_recommendations(hero['name'], data)
            if hero_data:
                print(format_hero_info(hero_data, data))
                print()
    else:
        # 交互模式
        print("王者荣耀出装推荐系统")
        print("=" * 50)
        print("命令：")
        print("  <英雄名>  - 查询英雄出装推荐")
        print("  --list    - 列出所有英雄")
        print("  --stats   - 显示数据统计")
        print("  quit      - 退出")
        print("=" * 50)
        
        while True:
            try:
                query = input("\n请输入英雄名或命令: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ('quit', 'exit', 'q'):
                    print("再见！")
                    break
                
                if query == '--list':
                    by_type = list_heroes_by_type(data)
                    print("\n王者荣耀英雄列表：")
                    for hero_type, names in by_type.items():
                        print(f"\n【{hero_type}】")
                        print(f"  {', '.join(names)}")
                    continue
                
                if query == '--stats':
                    print("\n王者荣耀数据统计：")
                    print(f"  装备数量: {len(data['equipment'])}")
                    print(f"  铭文数量: {len(data['inscriptions'])}")
                    print(f"  召唤师技能: {len(data['summoners'])}")
                    print(f"  英雄数量: {len(data['heroes'].get('heroes', []))}")
                    continue
                
                results = search_hero(query, data)
                
                if not results:
                    print(f"未找到包含 '{query}' 的英雄")
                    continue
                
                for hero in results:
                    hero_data = get_hero_recommendations(hero['name'], data)
                    if hero_data:
                        print(format_hero_info(hero_data, data))
                        print()
            
            except EOFError:
                print("\n再见！")
                break
            except KeyboardInterrupt:
                print("\n再见！")
                break

if __name__ == '__main__':
    main()

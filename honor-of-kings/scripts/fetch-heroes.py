#!/usr/bin/env python3
"""Fetch all King of Glory hero data (skills, attributes, recommended builds)."""
import json
import re
import sys
import time
import urllib.request
import html as htmlmod

HEROLIST_URL = "https://pvp.qq.com/web201605/js/herolist.json"
HERODETAIL_URL = "https://pvp.qq.com/web201605/herodetail/{}.shtml"
EQUIP_URL = "https://wuji-1254960240.file.myqcloud.com/smoba_weapon_detail/{}.json"

def fetch_hero_list():
    """Fetch hero list."""
    req = urllib.request.Request(HEROLIST_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_hero_detail(hero_id):
    """Fetch hero detail page and extract skills/attributes."""
    url = HERODETAIL_URL.format(hero_id)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
        
        # Try different encodings
        for enc in ['utf-8', 'gbk', 'gb2312']:
            try:
                html = raw.decode(enc)
                break
            except:
                continue
        else:
            html = raw.decode('utf-8', errors='ignore')
        
        # Extract all text content
        texts = re.findall(r'>([^<]+)<', html)
        clean_texts = []
        for t in texts:
            t = t.strip()
            if t and len(t) > 1 and not t.startswith('//') and not t.startswith('/*'):
                clean_texts.append(t)
        
        # Extract skills
        skills = []
        i = 0
        while i < len(clean_texts):
            if '冷却值' in clean_texts[i]:
                # Look back for skill name
                skill_name = ''
                for j in range(i-1, max(0, i-3), -1):
                    if clean_texts[j] and not clean_texts[j].startswith('冷却值') and not clean_texts[j].startswith('消耗'):
                        skill_name = clean_texts[j]
                        break
                
                # Extract cooldown
                cd = clean_texts[i].replace('冷却值：', '').strip()
                
                # Extract cost
                cost = ''
                if i+1 < len(clean_texts) and '消耗' in clean_texts[i+1]:
                    cost = clean_texts[i+1].replace('消耗：', '').strip()
                
                # Extract description
                desc = ''
                if i+2 < len(clean_texts):
                    desc = clean_texts[i+2]
                
                if skill_name and desc and len(desc) > 5:
                    skills.append({
                        'name': skill_name,
                        'cooldown': cd,
                        'cost': cost,
                        'description': htmlmod.unescape(desc)
                    })
            i += 1
        
        # Extract recommended inscriptions
        inscriptions = []
        for i, t in enumerate(clean_texts):
            if t == '铭文搭配建议':
                # Next texts should be inscription names and effects
                j = i + 1
                while j < len(clean_texts) and j < i + 10:
                    if clean_texts[j] == '技能加点建议' or clean_texts[j] == '英雄关系':
                        break
                    # Check if this is an inscription name (not a number or effect)
                    if not clean_texts[j].startswith('+') and not clean_texts[j].startswith('冷却'):
                        ins_name = clean_texts[j]
                        # Look for effect
                        if j+1 < len(clean_texts):
                            ins_effect = clean_texts[j+1]
                            inscriptions.append({'name': ins_name, 'effect': ins_effect})
                            j += 2
                            continue
                    j += 1
                break
        
        # Extract recommended equipment
        equipment = []
        equip_items = re.findall(r'data-item="([^"]+)"', html)
        for item_str in equip_items:
            equip_ids = item_str.split('|')
            equipment.append(equip_ids)
        
        # Extract hero relationships
        relationships = {
            'best_partners': [],
            'counters': [],
            'countered_by': []
        }
        
        # Find relationship section
        for i, t in enumerate(clean_texts):
            if t == '最佳搭档':
                j = i + 1
                while j < len(clean_texts) and clean_texts[j] != '压制英雄':
                    if '：' in clean_texts[j]:
                        partner = clean_texts[j].split('：')[0]
                        if partner and len(partner) >= 2:
                            relationships['best_partners'].append(partner)
                    j += 1
            elif t == '压制英雄':
                j = i + 1
                while j < len(clean_texts) and clean_texts[j] != '被压制英雄':
                    if '：' in clean_texts[j]:
                        counter = clean_texts[j].split('：')[0]
                        if counter and len(counter) >= 2:
                            relationships['counters'].append(counter)
                    j += 1
            elif t == '被压制英雄':
                j = i + 1
                while j < len(clean_texts) and clean_texts[j] != '出装建议':
                    if '的' in clean_texts[j]:
                        countered = clean_texts[j].split('的')[0]
                        if countered and len(countered) >= 2:
                            relationships['countered_by'].append(countered)
                    j += 1
        
        return {
            'skills': skills,
            'inscriptions': inscriptions,
            'equipment': equipment,
            'relationships': relationships
        }
    except Exception as e:
        return {'error': str(e)}

def fetch_equip_name(equip_id):
    """Fetch equipment name by ID."""
    try:
        url = EQUIP_URL.format(equip_id)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('name', equip_id)
    except:
        return equip_id

def main():
    # Fetch hero list
    print("获取英雄列表...", file=sys.stderr)
    heroes = fetch_hero_list()
    print(f"共 {len(heroes)} 个英雄", file=sys.stderr)
    
    # Fetch hero details
    results = []
    errors = []
    
    for i, hero in enumerate(heroes):
        hero_id = hero['ename']
        hero_name = hero['cname']
        hero_title = hero.get('title', '')
        hero_type = hero.get('hero_type', 0)
        
        # Hero type mapping
        type_map = {1: '战士', 2: '法师', 3: '坦克', 4: '刺客', 5: '射手', 6: '辅助'}
        hero_type_name = type_map.get(hero_type, str(hero_type))
        
        print(f"[{i+1}/{len(heroes)}] {hero_name} ({hero_title})...", file=sys.stderr)
        
        detail = fetch_hero_detail(hero_id)
        
        if 'error' in detail:
            errors.append({'id': hero_id, 'name': hero_name, 'error': detail['error']})
            print(f"  ✗ 错误: {detail['error']}", file=sys.stderr)
            continue
        
        # Resolve equipment names
        equip_names = []
        for equip_ids in detail.get('equipment', []):
            names = []
            for eid in equip_ids:
                name = fetch_equip_name(eid)
                names.append(name)
            equip_names.append(names)
        
        result = {
            'id': hero_id,
            'name': hero_name,
            'title': hero_title,
            'type': hero_type_name,
            'skills': detail.get('skills', []),
            'inscriptions': detail.get('inscriptions', []),
            'recommended_equipment': equip_names,
            'relationships': detail.get('relationships', {})
        }
        
        results.append(result)
        
        # Rate limiting
        if i % 5 == 4:
            time.sleep(0.5)
    
    # Output
    output = {
        'updated': time.strftime('%Y-%m-%d %H:%M'),
        'total': len(results),
        'errors': len(errors),
        'heroes': results
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))
    
    print(f"\n完成！{len(results)} 个英雄，{len(errors)} 个错误", file=sys.stderr)
    if errors:
        print("错误列表:", file=sys.stderr)
        for e in errors[:5]:
            print(f"  {e['name']}: {e['error']}", file=sys.stderr)

if __name__ == '__main__':
    main()

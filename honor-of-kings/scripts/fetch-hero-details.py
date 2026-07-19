#!/usr/bin/env python3
"""Fetch King of Glory hero details (skills, recommended builds, relationships).
This script fetches detailed hero data from individual hero pages.
It's slower but provides richer data than the hero list alone.
"""
import json
import re
import sys
import time
import urllib.request
import html as htmlmod
from concurrent.futures import ThreadPoolExecutor, as_completed

HEROLIST_URL = "https://pvp.qq.com/web201605/js/herolist.json"
HERODETAIL_URL = "https://pvp.qq.com/web201605/herodetail/{}.shtml"

def fetch_hero_list():
    req = urllib.request.Request(HEROLIST_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_hero_detail(hero):
    hero_id = hero['ename']
    hero_name = hero['cname']
    url = HERODETAIL_URL.format(hero_id)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
        
        for enc in ['utf-8', 'gbk', 'gb2312']:
            try:
                html = raw.decode(enc)
                break
            except:
                continue
        else:
            html = raw.decode('utf-8', errors='ignore')
        
        # Extract text nodes
        texts = re.findall(r'>([^<]+)<', html)
        clean = [t.strip() for t in texts if t.strip() and len(t.strip()) > 1]
        
        # Extract skills
        skills = []
        for i, t in enumerate(clean):
            if '冷却值' in t and i > 0:
                name = clean[i-1] if i > 0 else ''
                cd = t.replace('冷却值：', '').strip()
                cost = clean[i+1].replace('消耗：', '').strip() if i+1 < len(clean) and '消耗' in clean[i+1] else ''
                desc = clean[i+2] if i+2 < len(clean) and len(clean[i+2]) > 5 else ''
                if name and desc and '冷却值' not in name and '消耗' not in name:
                    skills.append({'name': name, 'cooldown': cd, 'cost': cost, 'description': desc})
        
        # Extract铭文
        inscriptions = []
        for i, t in enumerate(clean):
            if t == '铭文搭配建议':
                j = i + 1
                while j < len(clean) and j < i + 10:
                    if clean[j] in ('技能加点建议', '英雄关系'):
                        break
                    if not clean[j].startswith('+') and not clean[j].startswith('冷却'):
                        if j+1 < len(clean):
                            inscriptions.append({'name': clean[j], 'effect': clean[j+1]})
                            j += 2
                            continue
                    j += 1
                break
        
        # Extract relationships
        rels = {'best_partners': [], 'counters': [], 'countered_by': []}
        for i, t in enumerate(clean):
            if t == '最佳搭档':
                j = i + 1
                while j < len(clean) and clean[j] != '压制英雄':
                    if '：' in clean[j]:
                        rels['best_partners'].append(clean[j].split('：')[0])
                    j += 1
            elif t == '压制英雄':
                j = i + 1
                while j < len(clean) and clean[j] != '被压制英雄':
                    if '：' in clean[j]:
                        rels['counters'].append(clean[j].split('：')[0])
                    j += 1
            elif t == '被压制英雄':
                j = i + 1
                while j < len(clean) and clean[j] != '出装建议':
                    if '的' in clean[j]:
                        rels['countered_by'].append(clean[j].split('的')[0])
                    j += 1
        
        # Extract equipment IDs
        equip_ids = re.findall(r'data-item="([^"]+)"', html)
        
        type_map = {1: '战士', 2: '法师', 3: '坦克', 4: '刺客', 5: '射手', 6: '辅助'}
        
        return {
            'id': hero_id,
            'name': hero_name,
            'title': hero.get('title', ''),
            'type': type_map.get(hero.get('hero_type', 0), ''),
            'skills': skills,
            'inscriptions': inscriptions,
            'equipment_ids': [ids.split('|') for ids in equip_ids],
            'relationships': rels
        }
    except Exception as e:
        return {'id': hero_id, 'name': hero_name, 'error': str(e)}

def main():
    print("获取英雄列表...", file=sys.stderr)
    heroes = fetch_hero_list()
    print(f"共 {len(heroes)} 个英雄", file=sys.stderr)
    
    print("开始获取英雄详情（并发模式）...", file=sys.stderr)
    results = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_hero_detail, h): h for h in heroes}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if 'error' in result:
                errors.append(result)
                print(f"  ✗ [{i+1}/{len(heroes)}] {result['name']}: {result['error']}", file=sys.stderr)
            else:
                results.append(result)
                print(f"  ✓ [{i+1}/{len(heroes)}] {result['name']} ({len(result['skills'])}技能)", file=sys.stderr)
    
    # Sort by ID
    results.sort(key=lambda x: x['id'])
    
    output = {
        'updated': time.strftime('%Y-%m-%d %H:%M'),
        'total': len(results),
        'errors': len(errors),
        'heroes': results
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n完成！{len(results)} 个英雄，{len(errors)} 个错误", file=sys.stderr)

if __name__ == '__main__':
    main()

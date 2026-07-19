#!/bin/bash
# 王者荣耀全数据获取脚本
# 获取装备、铭文、召唤师技能、英雄数据

set -euo pipefail

CACHE_DIR="$HOME/.hermes/cache/wzry"
mkdir -p "$CACHE_DIR"

echo "=== 王者荣耀全数据获取 ===" >&2
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >&2
echo "" >&2

# Step 1: 获取铭文数据
echo "[1/4] 获取铭文数据..." >&2
curl -sf "https://pvp.qq.com/web201605/js/ming.json" -o "$CACHE_DIR/ming.json"
MING_COUNT=$(python3 -c "import json; print(len(json.load(open('$CACHE_DIR/ming.json'))))")
echo "  ✓ 获取到 $MING_COUNT 个铭文" >&2

# Step 2: 获取召唤师技能数据
echo "[2/4] 获取召唤师技能数据..." >&2
curl -sf "https://pvp.qq.com/web201605/js/summoner.json" -o "$CACHE_DIR/summoner.json"
SUMMONER_COUNT=$(python3 -c "import json; print(len(json.load(open('$CACHE_DIR/summoner.json'))))")
echo "  ✓ 获取到 $SUMMONER_COUNT 个召唤师技能" >&2

# Step 3: 获取英雄列表
echo "[3/4] 获取英雄列表..." >&2
curl -sf "https://pvp.qq.com/web201605/js/herolist.json" -o "$CACHE_DIR/herolist.json"
HERO_COUNT=$(python3 -c "import json; print(len(json.load(open('$CACHE_DIR/herolist.json'))))")
echo "  ✓ 获取到 $HERO_COUNT 个英雄" >&2

# Step 4: 获取装备ID列表
echo "[4/4] 获取装备数据..." >&2
EQUIP_IDS=(
    1242 1156 1350 1157 1351 1238 1138 1155 1332 1337 1328 1237 1232 11311 1244
    21823 1141 1234 1532 1533 1126 1531 1134 1137 1240 1159 1737 1131 1235 1747
    1721 1724 1723 1753 1754 1239 1236 11210 1725 1728 1127 13310 1133 1125 21713
    1233 12211 1338 1128 1161 1353 1727 1136 21353 1534 1227 22029 1336 22026 22031
    1331 1231 1135 22030 22028 22027 1341 1335 1334 1333 1347 1226 1132 1327 21913
    21493 1121 1711 11211 1321 1714 1243 1116 1221 1214 13211 1224 1325 1129 1323
    1222 1158 13212 1317 1154 1349 1123 1124 1115 1122 1324 1345 1424 1522 1423
    1523 1422 1425 1521 1426 1421 1701 11110 1114 1311 1218 1217 1113 1112 1312
    1212 1313 1111 1211 1511 1411
)
echo "  ✓ 共 ${#EQUIP_IDS[@]} 个装备" >&2

# 获取装备详情
echo "  获取装备详情..." >&2
EQUIP_FILE="$CACHE_DIR/equip.json"
echo "[" > "$EQUIP_FILE"

FIRST=1
COUNT=0
ERRORS=0
TOTAL=${#EQUIP_IDS[@]}

for ID in "${EQUIP_IDS[@]}"; do
    COUNT=$((COUNT + 1))
    RAW=$(curl -sf "https://wuji-1254960240.file.myqcloud.com/smoba_weapon_detail/${ID}.json" 2>/dev/null || echo "")
    
    if [ -z "$RAW" ]; then
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    DETAIL=$(echo "$RAW" | python3 -c "
import sys, json, re, html
data = json.load(sys.stdin)
attrs = data.get('attributes', {})
attr_text = re.sub(r'<[^>]+>', '', attrs.get('attributes', '')).strip()
sub_text = re.sub(r'<[^>]+>', '', attrs.get('sub', '')).strip()
type_map = {'1': '攻击', '2': '法术', '3': '防御', '4': '移动', '5': '打野', '7': '游走'}
sub_type = str(data.get('sub_type', ''))
result = {
    'id': data.get('equipment_id', 0),
    'name': data.get('name', ''),
    'price': data.get('price', 0),
    'category': type_map.get(sub_type, sub_type),
    'attributes': html.unescape(attr_text),
    'passive': html.unescape(sub_text)
}
print(json.dumps(result, ensure_ascii=False))
" 2>/dev/null || echo "")
    
    if [ -z "$DETAIL" ]; then
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    if [ $FIRST -eq 1 ]; then
        FIRST=0
    else
        echo "," >> "$EQUIP_FILE"
    fi
    echo "  $DETAIL" >> "$EQUIP_FILE"
    
    if [ $((COUNT % 10)) -eq 0 ]; then
        sleep 0.2
    fi
done

echo "]" >> "$EQUIP_FILE"

echo "" >&2
echo "=== 完成 ===" >&2
echo "装备: $((COUNT - ERRORS))/$TOTAL 成功" >&2
echo "铭文: $MING_COUNT 个" >&2
echo "召唤师技能: $SUMMONER_COUNT 个" >&2
echo "英雄: $HERO_COUNT 个" >&2
echo "" >&2

# 输出合并后的JSON
python3 -c "
import json, time, re, html as htmlmod

equip = json.load(open('$EQUIP_FILE'))
ming = json.load(open('$CACHE_DIR/ming.json'))
summoner = json.load(open('$CACHE_DIR/summoner.json'))
herolist = json.load(open('$CACHE_DIR/herolist.json'))

# 清理铭文HTML
inscriptions = []
for m in ming:
    desc = re.sub(r'<[^>]+>', '', m.get('ming_des', '')).strip()
    inscriptions.append({
        'id': m.get('ming_id', ''),
        'name': m.get('ming_name', ''),
        'type': m.get('ming_type', ''),
        'grade': m.get('ming_grade', ''),
        'description': htmlmod.unescape(desc)
    })

# 清理召唤师技能HTML
summoners = []
for s in summoner:
    desc = re.sub(r'<[^>]+>', '', s.get('summoner_description', '')).strip()
    summoners.append({
        'id': s.get('summoner_id', ''),
        'name': s.get('summoner_name', ''),
        'unlock': s.get('summoner_rank', ''),
        'description': htmlmod.unescape(desc)
    })

# 英雄列表
heroes = []
for h in herolist:
    type_map = {1: '战士', 2: '法师', 3: '坦克', 4: '刺客', 5: '射手', 6: '辅助'}
    heroes.append({
        'id': h.get('ename', ''),
        'name': h.get('cname', ''),
        'title': h.get('title', ''),
        'type': type_map.get(h.get('hero_type', 0), str(h.get('hero_type', '')))
    })

result = {
    'updated': time.strftime('%Y-%m-%d %H:%M'),
    'equipment': {'total': len(equip), 'items': sorted(equip, key=lambda x: x.get('price', 0), reverse=True)},
    'inscriptions': {'total': len(inscriptions), 'items': inscriptions},
    'summoners': {'total': len(summoners), 'items': summoners},
    'heroes': {'total': len(heroes), 'items': heroes}
}

print(json.dumps(result, ensure_ascii=False, indent=2))
"

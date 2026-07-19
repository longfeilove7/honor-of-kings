---
name: honor-of-kings
description: Honor of Kings (王者荣耀) build recommendation system. Combines hero attributes, equipment stats, summoner spells and inscriptions to recommend optimal builds for each hero in different lanes. Fetches real-time data from Tencent official APIs. Use when user asks about 王者荣耀出装、装备推荐、铭文推荐、英雄技能、召唤师技能、分路推荐.
---

# Honor of Kings Build Recommendation System

综合英雄属性、装备属性、召唤师技能和铭文，给出每个英雄打不同分路时的最优套装。

## Features

- **Equipment**: 126 items with stats, prices, and passive/active effects
- **Inscriptions**: 93 inscriptions with attributes and effects
- **Summoner Spells**: 11 spells with cooldowns and effects
- **Heroes**: 131 heroes with skills, recommended builds, inscriptions, and hero relationships
- **Build Recommendations**: Optimal builds based on hero type and lane

## Usage

### Get Hero Build Recommendations
```bash
python3 /mnt/skills/user/honor-of-kings/scripts/build-recommend.py 貂蝉
python3 /mnt/skills/user/honor-of-kings/scripts/build-recommend.py --hero 貂蝉
```

### List All Heroes
```bash
python3 /mnt/skills/user/honor-of-kings/scripts/build-recommend.py --list
```

### Show Data Statistics
```bash
python3 /mnt/skills/user/honor-of-kings/scripts/build-recommend.py --stats
```

### Fetch All Data
```bash
bash /mnt/skills/user/honor-of-kings/scripts/fetch-all.sh
```

### Fetch Hero Details
```bash
python3 /mnt/skills/user/honor-of-kings/scripts/fetch-hero-details.py
```

## Output Example

```
==================================================
英雄: 貂蝉 (绝世舞姬)
类型: 法师
推荐分路: 中路
==================================================

【技能介绍】
• 语·花印
  冷却: 0 | 消耗: 0
  被动：貂蝉的技能命中会为敌人叠加花之印记...

【铭文推荐】
• 圣人: 法术攻击力+5.3
• 虚空: 最大生命+37.5
• 轮回: 法术攻击力+2.4

【出装推荐】
方案1: 冷静之靴 → 噬神之书 → 痛苦面具 → 极寒风暴 → 不死鸟之眼 → 博学者之怒
方案2: 冷静之靴 → 噬神之书 → 暴烈之甲 → 痛苦面具 → 极寒风暴 → 辉月

【英雄关系】
最佳搭档: 庄周, 白起
克制英雄: 露娜, 张飞
被克制: 张良, 花木兰
```

## API Endpoints

| Data Type | URL | Count |
|-----------|-----|-------|
| Equipment | `https://wuji-1254960240.file.myqcloud.com/smoba_weapon_detail/{id}.json` | 126 |
| Inscriptions | `https://pvp.qq.com/web201605/js/ming.json` | 93 |
| Summoner Spells | `https://pvp.qq.com/web201605/js/summoner.json` | 11 |
| Hero List | `https://pvp.qq.com/web201605/js/herolist.json` | 131 |
| Hero Details | `https://pvp.qq.com/web201605/herodetail/{id}.shtml` | Per hero |

## Data Categories

### Equipment Types
- Attack (sub_type=1)
- Magic (sub_type=2)
- Defense (sub_type=3)
- Movement (sub_type=4)
- Jungle (sub_type=5)
- Support (sub_type=7)

### Inscription Types
- red (Red Inscriptions)
- blue (Blue Inscriptions)
- green (Green Inscriptions)

### Hero Types
- Warrior (hero_type=1): Side Lane, Jungle
- Mage (hero_type=2): Mid Lane
- Tank (hero_type=3): Side Lane, Support
- Assassin (hero_type=4): Jungle, Mid Lane
- Marksman (hero_type=5): Farm Lane
- Support (hero_type=6): Support, Roaming

## Notes

- Equipment API requires individual requests (126 items), takes ~30 seconds
- Inscriptions and Summoner Spells APIs return all data in one request
- Hero details require fetching and parsing HTML pages individually
- Data is from Tencent official CDN, real-time updates
- HTML tags are automatically stripped

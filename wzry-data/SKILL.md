---
name: wzry-data
description: 获取王者荣耀最新装备、铭文、召唤师技能和英雄属性数据。通过腾讯官方API实时获取，包括所有装备的价格/基础属性/被动技能、铭文属性、召唤师技能效果、英雄技能和出装推荐。Use when user asks about 王者荣耀装备属性、铭文属性、出装数据、装备查询、英雄技能、召唤师技能。
---

# 王者荣耀全数据查询

通过腾讯官方API实时获取王者荣耀最新版本的装备、铭文、召唤师技能和英雄数据。

## API端点

| 数据类型 | API地址 | 数据量 |
|---------|---------|-------|
| 装备详情 | `https://wuji-1254960240.file.myqcloud.com/smoba_weapon_detail/{id}.json` | 126个 |
| 铭文 | `https://pvp.qq.com/web201605/js/ming.json` | 93个 |
| 召唤师技能 | `https://pvp.qq.com/web201605/js/summoner.json` | 11个 |
| 英雄列表 | `https://pvp.qq.com/web201605/js/herolist.json` | 131个 |
| 英雄详情 | `https://pvp.qq.com/web201605/herodetail/{id}.shtml` | 需逐个获取 |

## 使用方法

### 快速获取（装备+铭文+召唤师技能+英雄列表）
```bash
bash /mnt/skills/user/wzry-data/scripts/fetch-all.sh
```

### 获取英雄详细数据（技能、出装推荐、英雄关系）
```bash
python3 /mnt/skills/user/wzry-data/scripts/fetch-hero-details.py
```

## 输出格式

### fetch-all.sh 输出
```json
{
  "updated": "2026-07-19",
  "equipment": {
    "total": 126,
    "items": [{"id": 1138, "name": "强者破军", "price": 2540, "category": "攻击", "attributes": "+150物理攻击", "passive": "唯一被动-破军..."}]
  },
  "inscriptions": {
    "total": 93,
    "items": [{"id": "1501", "name": "圣人", "type": "red", "grade": "5", "description": "法术攻击力+5.3"}]
  },
  "summoners": {
    "total": 11,
    "items": [{"id": 80104, "name": "惩击", "unlock": "LV.1解锁", "description": "30秒CD：对身边的野怪和小兵造成1500点真实伤害"}]
  },
  "heroes": {
    "total": 131,
    "items": [{"id": 141, "name": "貂蝉", "title": "绝世舞姬", "type": "法师"}]
  }
}
```

### fetch-hero-details.py 输出
```json
{
  "heroes": [{
    "id": 141,
    "name": "貂蝉",
    "title": "绝世舞姬",
    "type": "法师",
    "skills": [
      {"name": "语·花印", "cooldown": "0", "cost": "0", "description": "被动：貂蝉的技能命中会为敌人叠加花之印记..."},
      {"name": "落·红雨", "cooldown": "5", "cost": "40", "description": "貂蝉向指定方向挥出花球..."}
    ],
    "inscriptions": [{"name": "圣人", "effect": "法术攻击力+5.3"}],
    "equipment_ids": [["1423", "1240", "1235", "1336", "1334", "1232"]],
    "relationships": {
      "best_partners": ["庄周", "白起"],
      "counters": ["露娜", "张飞"],
      "countered_by": ["张良", "花木兰"]
    }
  }]
}
```

## 数据分类

### 装备分类
- 攻击 (sub_type=1)
- 法术 (sub_type=2)
- 防御 (sub_type=3)
- 移动 (sub_type=4)
- 打野 (sub_type=5)
- 游走 (sub_type=7)

### 铭文类型
- red（红色铭文）
- blue（蓝色铭文）
- green（绿色铭文）

### 英雄类型
- 战士 (hero_type=1)
- 法师 (hero_type=2)
- 坦克 (hero_type=3)
- 刺客 (hero_type=4)
- 射手 (hero_type=5)
- 辅助 (hero_type=6)

## Present Results to User

当用户查询特定装备/铭文/英雄时，用表格展示：

| 属性 | 值 |
|------|-----|
| 名称 | xxx |
| 价格 | xxx金币 |
| 基础属性 | xxx |
| 被动/主动 | xxx |

## 注意事项

- 装备API需要逐个请求（126个），耗时约30秒
- 铭文和召唤师技能API一次请求获取全部数据
- 英雄详情需要逐个获取HTML页面并解析，耗时较长
- 数据来自腾讯官方CDN，实时更新
- HTML标签会被自动清除

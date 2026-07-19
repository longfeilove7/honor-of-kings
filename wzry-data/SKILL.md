---
name: wzry-data
description: 王者荣耀综合出装推荐系统。综合英雄属性、装备属性、召唤师技能和铭文，给出每个英雄打不同分路时的最优套装。通过腾讯官方API实时获取最新数据。Use when user asks about 王者荣耀出装、装备推荐、铭文推荐、英雄技能、召唤师技能、分路推荐。
---

# 王者荣耀综合出装推荐系统

综合英雄属性、装备属性、召唤师技能和铭文，给出每个英雄打不同分路时的最优套装。

## 功能特性

- **装备查询**: 126个装备的属性、价格、被动技能
- **铭文查询**: 93个铭文的属性和效果
- **召唤师技能**: 11个召唤师技能的冷却时间和效果
- **英雄查询**: 131个英雄的技能、出装推荐、铭文推荐、英雄关系
- **出装推荐**: 根据英雄类型和分路推荐最优出装方案

## 使用方法

### 查询英雄出装推荐
```bash
bash /mnt/skills/user/wzry-data/scripts/wzry 貂蝉
```

### 列出所有英雄
```bash
bash /mnt/skills/user/wzry-data/scripts/wzry --list
```

### 显示数据统计
```bash
bash /mnt/skills/user/wzry-data/scripts/wzry --stats
```

### 获取原始数据
```bash
bash /mnt/skills/user/wzry-data/scripts/fetch-all.sh
```

### 获取英雄详细数据
```bash
python3 /mnt/skills/user/wzry-data/scripts/fetch-hero-details.py
```

## 输出示例

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

## API端点

| 数据类型 | API地址 | 数据量 |
|---------|---------|-------|
| 装备详情 | `https://wuji-1254960240.file.myqcloud.com/smoba_weapon_detail/{id}.json` | 126个 |
| 铭文 | `https://pvp.qq.com/web201605/js/ming.json` | 93个 |
| 召唤师技能 | `https://pvp.qq.com/web201605/js/summoner.json` | 11个 |
| 英雄列表 | `https://pvp.qq.com/web201605/js/herolist.json` | 131个 |
| 英雄详情 | `https://pvp.qq.com/web201605/herodetail/{id}.shtml` | 需逐个获取 |

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
- 战士 (hero_type=1): 对抗路、打野
- 法师 (hero_type=2): 中路
- 坦克 (hero_type=3): 对抗路、辅助
- 刺客 (hero_type=4): 打野、中路
- 射手 (hero_type=5): 发育路
- 辅助 (hero_type=6): 辅助、游走

## 注意事项

- 装备API需要逐个请求（126个），耗时约30秒
- 铭文和召唤师技能API一次请求获取全部数据
- 英雄详情需要逐个获取HTML页面并解析，耗时较长
- 数据来自腾讯官方CDN，实时更新
- HTML标签会被自动清除

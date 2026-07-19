#!/bin/bash
# 从王者荣耀装备页面获取最新装备ID列表
# 需要浏览器环境，通常不需要单独运行

set -euo pipefail

echo "请在浏览器中打开 https://pvp.qq.com/ingame/entrance/equip/equip_list.html" >&2
echo "然后在控制台运行以下JavaScript获取ID列表：" >&2
echo "" >&2
cat << 'EOF'
var el = document.querySelector('#app').__vue__.$data.equipList2;
var seen = {};
var ids = [];
el.forEach(function(e) { 
    if (!seen[e.equipment_id]) { 
        seen[e.equipment_id] = true; 
        ids.push(e.equipment_id); 
    } 
});
console.log(JSON.stringify(ids));
EOF

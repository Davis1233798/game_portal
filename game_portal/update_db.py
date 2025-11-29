import json
import re

# Read crawled games
with open('crawled_games.json', 'r', encoding='utf-8') as f:
    crawled_games = json.load(f)

# Filter valid games
valid_games = []
seen_titles = set()

for game in crawled_games:
    if game['url'] == 'about:blank' or not game['url']:
        continue
    if "googleads" in game['url']:
        continue
    if game['title'] in seen_titles:
        continue
    
    # Clean title
    game['title'] = game['title'].replace("From Gamesmomo: ", "").replace("From Kuioo: ", "")
    
    valid_games.append(game)
    seen_titles.add(game['title'])

print(f"Found {len(valid_games)} valid games.")

# Read existing database file
with open('games-database.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Prepare new games string
new_games_js = "const crawledGames = [\n"
for game in valid_games:
    new_games_js += "    {\n"
    new_games_js += f"        id: {game['id']},\n"
    new_games_js += f"        title: \"{game['title']}\",\n"
    new_games_js += f"        description: \"{game['description']}\",\n"
    new_games_js += f"        category: \"{game['category']}\",\n"
    new_games_js += f"        url: \"{game['url']}\",\n"
    new_games_js += f"        image: \"{game['image']}\",\n"
    new_games_js += f"        rating: {game['rating']}\n"
    new_games_js += "    },\n"
new_games_js += "];\n\n"

# Replace the additionalGames generation with crawledGames
# We'll look for the part where additionalGames is defined and populated
# and replace it with our static list + maybe some random ones if needed to reach 500
# But for now, let's just add them.

# Strategy:
# 1. Keep the top part (gamesDatabase definition).
# 2. Replace everything after `// 添加更多遊戲到達500+個` with our new logic.

split_marker = "// 添加更多遊戲到達500+個"
if split_marker in content:
    parts = content.split(split_marker)
    header = parts[0]
    
    new_content = header + split_marker + "\n" + new_games_js
    
    new_content += """
// 將所有遊戲合併
const allGames = [...gamesDatabase, ...crawledGames];

// 導出遊戲資料庫
window.gamesDatabase = allGames;

// 類別配置
window.gameCategories = {
    all: { name: '全部', icon: '🎮' },
    action: { name: '動作', icon: '⚡' },
    puzzle: { name: '益智', icon: '🧩' },
    racing: { name: '賽車', icon: '🏎️' },
    arcade: { name: '街機', icon: '🕹️' },
    sports: { name: '體育', icon: '⚽' },
    shooter: { name: '射擊', icon: '🔫' },
    strategy: { name: '策略', icon: '♟️' },
    multiplayer: { name: '多人', icon: '👥' }
};

console.log(`遊戲資料庫已載入，共 ${allGames.length} 個遊戲`);
"""
    
    with open('games-database.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated games-database.js")
else:
    print("Could not find split marker in games-database.js")

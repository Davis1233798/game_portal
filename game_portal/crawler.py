import asyncio
from playwright.async_api import async_playwright
import json
import random
from urllib.parse import urljoin

# Configuration
KUIOO_URL = "https://kuioo.tw/"
GAMESMOMO_URL = "http://www.gamesmomo.com/"
OUTPUT_FILE = "crawled_games.json"

crawled_games = []
game_id_counter = 100

async def crawl_kuioo(page):
    global game_id_counter
    print("Crawling Kuioo with Playwright...")
    try:
        await page.goto(KUIOO_URL, timeout=30000)
        await page.wait_for_load_state('networkidle')
        
        links = await page.query_selector_all('a[href*="/g/info/"]')
        print(f"Found {len(links)} potential games on Kuioo homepage.")
        
        hrefs = []
        for link in links:
            href = await link.get_attribute('href')
            if href:
                hrefs.append(href)
        
        hrefs = list(set(hrefs))
        
        count = 0
        for href in hrefs:
            if count >= 50: # Increased limit
                break
                
            full_url = urljoin(KUIOO_URL, href)
            print(f"Processing Kuioo game: {full_url}")
            
            try:
                await page.goto(full_url, timeout=30000)
                
                title_el = await page.query_selector('h1') or await page.query_selector('title')
                title = await title_el.inner_text() if title_el else "Unknown Game"
                title = title.replace(" - Kuioo", "").strip()
                
                image_el = await page.query_selector('meta[property="og:image"]')
                image_url = await image_el.get_attribute('content') if image_el else ""
                
                # Find all iframes and filter
                iframes = await page.query_selector_all('iframe')
                embed_url = ""
                for iframe in iframes:
                    src = await iframe.get_attribute('src')
                    if src and "googleads" not in src and "doubleclick" not in src and "googlesyndication" not in src:
                        embed_url = src
                        break
                
                if embed_url:
                    crawled_games.append({
                        "id": game_id_counter,
                        "title": title,
                        "description": f"From Kuioo: {title}",
                        "category": "action",
                        "url": embed_url,
                        "image": image_url,
                        "rating": round(random.uniform(3.5, 5.0), 1)
                    })
                    game_id_counter += 1
                    count += 1
                    print(f"  -> Added: {embed_url}")
            except Exception as e:
                print(f"  -> Failed to process game page: {e}")
                
    except Exception as e:
        print(f"Error crawling Kuioo: {e}")

async def crawl_gamesmomo(page):
    global game_id_counter
    print("Crawling Gamesmomo with Playwright...")
    try:
        await page.goto(GAMESMOMO_URL, timeout=30000)
        
        links = await page.query_selector_all('a[href*="a.asp?id="]')
        print(f"Found {len(links)} potential games on Gamesmomo homepage.")
        
        hrefs = []
        for link in links:
            href = await link.get_attribute('href')
            if href:
                hrefs.append(href)
        
        hrefs = list(set(hrefs))
        
        count = 0
        for href in hrefs:
            if count >= 50: # Increased limit
                break
                
            full_url = urljoin(GAMESMOMO_URL, href)
            print(f"Processing Gamesmomo game: {full_url}")
            
            try:
                await page.goto(full_url, timeout=30000)
                
                title_el = await page.query_selector('title')
                title = await title_el.inner_text() if title_el else "Unknown Game"
                title = title.split('-')[0].strip()
                
                image_url = "https://via.placeholder.com/300x200?text=Game"
                
                iframes = await page.query_selector_all('iframe')
                embed_url = ""
                for iframe in iframes:
                    src = await iframe.get_attribute('src')
                    if src and "googleads" not in src and "doubleclick" not in src:
                        embed_url = src
                        break
                        
                if embed_url:
                    if not embed_url.startswith('http'):
                        embed_url = urljoin(full_url, embed_url)
                        
                    crawled_games.append({
                        "id": game_id_counter,
                        "title": title,
                        "description": f"From Gamesmomo: {title}",
                        "category": "arcade",
                        "url": embed_url,
                        "image": image_url,
                        "rating": round(random.uniform(3.5, 5.0), 1)
                    })
                    game_id_counter += 1
                    count += 1
                    print(f"  -> Added: {embed_url}")
            except Exception as e:
                print(f"  -> Failed to process game page: {e}")

    except Exception as e:
        print(f"Error crawling Gamesmomo: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await crawl_kuioo(page)
        await crawl_gamesmomo(page)
        
        await browser.close()
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(crawled_games, f, ensure_ascii=False, indent=4)
        
    print(f"Done! Saved {len(crawled_games)} games to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())

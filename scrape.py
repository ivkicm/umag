import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz
import re

def get_relative_time_string(date_str, time_str):
    """Berechnet die vergangene Zeit."""
    try:
        tz = pytz.timezone('Europe/Zagreb')
        # Format: 22.12.2025 | 09:02
        dt_str = f"{date_str} {time_str}"
        dt = datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
        dt = tz.localize(dt)
        
        now = datetime.now(tz)
        diff = now - dt
        seconds = diff.total_seconds()
        
        if seconds < 0: return "GERADE EBEN"
        if seconds < 3600:
            mins = int(seconds / 60)
            return f"VOR {max(1, mins)} MINUTEN"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"VOR {hours} {'STUNDE' if hours == 1 else 'STUNDEN'}"
        else:
            return dt.strftime("%d.%m. %H:%M")
    except:
        return "AKTUELL"

def get_news():
    url = "https://istrain.hr/gradovi/8/umag"
    base_url = "https://istrain.hr"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    news_data = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.select('article.news-item')
        
        for art in articles[:10]: # Top 10 News
            try:
                title_el = art.select_one('.news-item-title a')
                desc_el = art.select_one('.news-item-description')
                img_el = art.select_one('img')
                
                # Datum und Uhrzeit extrahieren
                time_val = art.select_one('.time-published').get_text(strip=True) if art.select_one('.time-published') else ""
                date_val = art.select_one('.date-published').get_text(strip=True) if art.select_one('.date-published') else ""
                
                # Bild Pfad korrigieren
                img_path = img_el.get('src') if img_el else ""
                if img_path.startswith('/'):
                    img_url = base_url + img_path
                else:
                    img_url = img_path

                if title_el:
                    rel_time = get_relative_time_string(date_val, time_val)
                    news_data.append({
                        'title': title_el.get_text(strip=True),
                        'desc': desc_el.get_text(strip=True) if desc_el else "",
                        'image': img_url,
                        'rel_time': rel_time,
                        'source': 'ISTRAIN UMAG'
                    })
            except: continue

        return news_data
    except Exception as e:
        print(f"Scraping Fehler: {e}")
        return []

def generate_html(news):
    tz = pytz.timezone('Europe/Zagreb')
    now = datetime.now(tz).strftime("%d.%m.%Y - %H:%M")
    
    if not news:
        news = [{'title': 'Lade Nachrichten...', 'desc': 'Suche nach aktuellen Meldungen für Umag.', 'image': '', 'rel_time': 'INFO', 'source': 'SYSTEM'}]

    slides_html = ""
    for i, item in enumerate(news):
        active_class = "active" if i == 0 else ""
        img_url = item['image'] if item['image'] else "https://placehold.co/1200x630/003366/FFFFFF?text=UMAG"

        slides_html += f"""
        <div class="slide {active_class}">
            <div class="image-side">
                <img src="{img_url}" alt="News Image">
            </div>
            <div class="text-side">
                <div class="meta-line">
                    <span class="source-badge">{item['source']}</span>
                    <span class="pub-time">{item['rel_time']}</span>
                </div>
                <div class="title">{item['title']}</div>
                <div class="description">{item['desc']}</div>
            </div>
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html lang="hr">
<head>
    <meta charset="UTF-8">
    <meta name="robots" content="noindex, nofollow">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Umag News Radar Split XXL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@800;900&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        body, html {{ 
            margin: 0; padding: 0; width: 100%; height: 100%; 
            background-color: black; color: white; font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        
        .update-info {{
            position: fixed; top: 15px; right: 20px; z-index: 100;
            background: rgba(0, 85, 164, 0.9); color: white;
            padding: 5px 15px; border-radius: 8px;
            font-family: 'JetBrains Mono'; font-size: 1.1rem;
            box-shadow: 0 0 15px rgba(0,0,0,0.5); border: 1px solid #ffffff;
        }}

        .slide {{
            position: absolute; width: 100%; height: 100%;
            display: none; 
            grid-template-columns: 0.9fr 1.1fr; /* SPLIT SCREEN: Bild links, Text rechts */
            align-items: center; gap: 50px; padding: 40px;
        }}
        .slide.active {{ display: grid; animation: fadeIn 0.8s ease-in; }}

        /* LINKE SEITE: BILD */
        .image-side {{ 
            width: 100%; height: 85vh; 
            border-radius: 30px; overflow: hidden;
            border: 4px solid #333; box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        }}
        .image-side img {{ width: 100%; height: 100%; object-fit: cover; }}

        /* RECHTE SEITE: TEXT */
        .text-side {{ 
            display: flex; flex-direction: column; justify-content: center;
        }}

        .meta-line {{ display: flex; gap: 25px; align-items: center; margin-bottom: 30px; }}
        .source-badge {{ 
            background: #0055a4; color: white; padding: 5px 15px; border-radius: 8px;
            font-weight: 900; font-size: 2.2rem; text-transform: uppercase; letter-spacing: 2px;
        }}
        .pub-time {{ color: #ccc; font-family: 'JetBrains Mono'; font-size: 2.2rem; font-weight: 700; }}

        .title {{ 
            font-size: 4.4rem; font-weight: 900; line-height: 1.1; 
            text-transform: uppercase; letter-spacing: -2px; margin-bottom: 30px;
            color: #ffffff; text-shadow: 0 4px 15px rgba(0,0,0,0.5);
            display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
        }}

        .description {{
            font-size: 2.6rem; color: #bbb; line-height: 1.3;
            display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden;
        }}

        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="update-info">UPDATE: {now}</div>
    {slides_html}

    <script>
        const slides = document.querySelectorAll('.slide');
        let current = 0;
        function nextSlide() {{
            if (slides.length <= 1) return;
            slides[current].classList.remove('active');
            current = (current + 1) % slides.length;
            slides[current].classList.add('active');
        }}
        setInterval(nextSlide, 12000); // 12 Sekunden pro News
        setTimeout(() => {{ location.reload(); }}, 3600000);
    </script>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_news()
    generate_html(data)


import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz
import re

def format_umag_date(date_str, time_str):
    """Wandelt 22.12.2025 und 09:02 in 22.12. 09:02 um."""
    try:
        day_month = ".".join(date_str.split('.')[:2]) + "."
        return f"{day_month} {time_str}"
    except:
        return f"{date_str} {time_str}"

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
        
        for art in articles[:10]:
            try:
                title_el = art.select_one('.news-item-title a')
                desc_el = art.select_one('.news-item-description')
                img_el = art.select_one('img')
                
                time_val = art.select_one('.time-published').get_text(strip=True) if art.select_one('.time-published') else ""
                date_val = art.select_one('.date-published').get_text(strip=True) if art.select_one('.date-published') else ""
                
                img_path = img_el.get('src') if img_el else ""
                if img_path.startswith('/'):
                    img_url = base_url + img_path
                else:
                    img_url = img_path

                if title_el:
                    display_time = format_umag_date(date_val, time_val)
                    try:
                        sort_dt = datetime.strptime(f"{date_val} {time_val}", "%d.%m.%Y %H:%M")
                    except:
                        sort_dt = datetime.now()

                    news_data.append({
                        'title': title_el.get_text(strip=True),
                        'desc': desc_el.get_text(strip=True) if desc_el else "",
                        'image': img_url,
                        'display_time': display_time,
                        'sort_dt': sort_dt
                    })
            except: continue

        news_data.sort(key=lambda x: x['sort_dt'], reverse=True)
        return news_data
    except Exception as e:
        print(f"Scraping Fehler: {e}")
        return []

def generate_html(news):
    if not news:
        news = [{'title': 'Lade Nachrichten...', 'desc': 'Suche nach aktuellen Meldungen für Umag.', 'image': '', 'display_time': '--.--. --:--'}]

    slides_html = ""
    for i, item in enumerate(news):
        active_class = "active" if i == 0 else ""
        img_url = item['image'] if item['image'] else "https://placehold.co/1200x630/003366/FFFFFF?text=UMAG"

        slides_html += f"""
        <div class="slide {active_class}">
            <div class="slide-header">
                <span class="source-badge">UMAG</span>
                <span class="pub-time">{item['display_time']}</span>
            </div>
            <div class="slide-body">
                <div class="image-side">
                    <img src="{img_url}" alt="News Image">
                </div>
                <div class="text-side">
                    <div class="title">{item['title']}</div>
                    <div class="description">{item['desc']}</div>
                </div>
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
    <title>Umag News Split XXL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@800;900&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        body, html {{ 
            margin: 0; padding: 0; width: 100%; height: 100%; 
            background-color: black; color: white; font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        
        .slide {{
            position: absolute; width: 100%; height: 100%;
            display: none; 
            flex-direction: column;
            padding: 30px 40px;
        }}
        .slide.active {{ display: flex; animation: fadeIn 0.8s ease-in; }}

        /* HEADER ÜBER DEM BILD */
        .slide-header {{
            display: flex; gap: 25px; align-items: center; 
            margin-bottom: 20px; /* Abstand zum Bild/Text Bereich */
        }}
        
        .source-badge {{ 
            border: 4px solid white; color: white; padding: 5px 20px; border-radius: 10px;
            font-weight: 900; font-size: 2.4rem; text-transform: uppercase; letter-spacing: 2px;
            line-height: 1;
        }}
        
        .pub-time {{ color: white; font-family: 'JetBrains Mono'; font-size: 2.4rem; font-weight: 700; }}

        /* CONTENT BEREICH */
        .slide-body {{
            display: grid;
            grid-template-columns: 0.9fr 1.1fr; 
            gap: 50px;
            align-items: start; /* WICHTIG: Text fängt oben bündig mit Bild an */
            height: 100%;
        }}

        /* LINKE SEITE: BILD */
        .image-side {{ 
            width: 100%; height: 78vh; 
            border-radius: 30px; overflow: hidden;
            border: 4px solid #333; box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        }}
        .image-side img {{ width: 100%; height: 100%; object-fit: cover; }}

        /* RECHTE SEITE: TEXT */
        .text-side {{ 
            display: flex; flex-direction: column;
            padding-top: 0; /* Stellt sicher, dass kein interner Offset da ist */
        }}

        .title {{ 
            font-size: 4.8rem; font-weight: 900; line-height: 1.05; 
            text-transform: uppercase; letter-spacing: -2px; margin-bottom: 35px;
            color: #ffffff; text-shadow: 0 4px 15px rgba(0,0,0,0.5);
            display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
        }}

        .description {{
            font-size: 3.0rem; color: #ccc; line-height: 1.35;
            display: -webkit-box; -webkit-line-clamp: 8; -webkit-box-orient: vertical; overflow: hidden;
        }}

        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
</head>
<body>
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
        setInterval(nextSlide, 15000);
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

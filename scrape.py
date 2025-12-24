import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

def get_istrain_news():
    url = "https://istrain.hr/gradovi/8/umag"
    base_url = "https://istrain.hr"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    news_data = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suche alle Artikel
        articles = soup.select('article.news-item')
        
        for art in articles[:10]: # Top 10 News
            try:
                # Titel
                title_el = art.select_one('.news-item-title a')
                title = title_el.get_text(strip=True)
                
                # Bild extrahieren und Pfad vervollständigen
                img_el = art.select_one('img')
                img_path = img_el.get('src') if img_el else ""
                if img_path.startswith('/'):
                    img_url = base_url + img_path
                else:
                    img_url = img_path
                
                # Datum und Uhrzeit
                time_val = art.select_one('.time-published').get_text(strip=True) if art.select_one('.time-published') else ""
                date_val = art.select_one('.date-published').get_text(strip=True) if art.select_one('.date-published') else ""
                
                # Kategorie (Optional für Anzeige)
                category = art.select_one('.news-item-category').get_text(strip=True) if art.select_one('.news-item-category') else "UMAG"

                if title:
                    news_data.append({
                        'title': title,
                        'image': img_url,
                        'time_str': time_val,
                        'date_str': date_val,
                        'category': category
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
        news = [{'title': 'Tražim najnovije vijesti za Umag...', 'image': '', 'time_str': '', 'date_str': '', 'category': 'INFO'}]

    slides_html = ""
    for i, item in enumerate(news):
        active_class = "active" if i == 0 else ""
        
        # Fallback Bild falls keins gefunden wurde
        img_url = item['image'] if item['image'] else "https://placehold.co/1200x630/003366/FFFFFF?text=ISTRAIN+UMAG"

        slides_html += f"""
        <div class="slide {active_class}">
            <div class="image-container">
                <img src="{img_url}" alt="News Image">
                <div class="img-overlay"></div>
            </div>
            <div class="content-box">
                <div class="meta-line">
                    <span class="source">{item['category']}</span>
                    <span class="pub-time">{item['date_str']} | {item['time_str']} UHR</span>
                </div>
                <div class="title">{item['title']}</div>
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
    <title>IstraIn Umag XXL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@800;900&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        body, html {{ 
            margin: 0; padding: 0; width: 100%; height: 100%; 
            background-color: black; color: white; font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        
        .header-info {{
            position: fixed; top: 15px; right: 20px; z-index: 100;
            background: rgba(0, 85, 164, 0.9); color: white;
            padding: 5px 15px; border-radius: 8px;
            font-family: 'JetBrains Mono'; font-size: 1.2rem;
            font-weight: 800; box-shadow: 0 0 15px rgba(0,0,0,0.5);
            border: 1px solid #ffffff;
        }}

        .slide {{
            position: absolute; width: 100%; height: 100%;
            display: none; flex-direction: column;
        }}
        .slide.active {{ display: flex; animation: fadeIn 0.8s ease-in; }}

        .image-container {{ 
            width: 100%; height: 55vh; position: relative; overflow: hidden; 
        }}
        
        .image-container img {{ 
            width: 100%; height: 100%; 
            object-fit: cover; 
            object-position: center top; 
            border-bottom: 8px solid #0055a4;
        }}

        .img-overlay {{
            position: absolute; bottom: 0; left: 0; width: 100%; height: 25%;
            background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
        }}

        .content-box {{ 
            flex: 1; padding: 30px 60px; 
            background: linear-gradient(to bottom, #001122, #000);
            display: flex; flex-direction: column; justify-content: flex-start;
            padding-top: 35px;
        }}

        .meta-line {{ display: flex; gap: 30px; align-items: center; margin-bottom: 20px; }}
        .source {{ color: #0088ff; font-weight: 900; font-size: 2.8rem; letter-spacing: 3px; text-transform: uppercase; }}
        .pub-time {{ color: #ffffff; font-family: 'JetBrains Mono'; font-size: 2.6rem; font-weight: 800; opacity: 0.9; }}

        .title {{ 
            font-size: 4.2rem; font-weight: 900; line-height: 1.1; 
            text-transform: uppercase; letter-spacing: -1px;
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
            color: #ffffff;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }}

        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="header-info">ISTRAIN: {now}</div>
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

        setInterval(nextSlide, 10000); 
        setTimeout(() => {{ location.reload(); }}, 3600000); // Reload nach 1h
    </script>
</body>
</html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_istrain_news()
    generate_html(data)

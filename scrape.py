import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

def get_umag_hr():
    """Scrapt die offizielle Seite umag.hr"""
    url = "https://umag.hr/novosti"
    base = "https://umag.hr"
    headers = {'User-Agent': 'Mozilla/5.0'}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Basierend auf dem Snippet: Container ist _1yW2E1iJ
        articles = soup.select('._1yW2E1iJ')
        for art in articles[:5]:
            title_el = art.select_one('._2PvPhQDR')
            date_el = art.select_one('.FqqoTFMg')
            img_el = art.select_one('img')
            link_el = art.select_one('a')
            
            if title_el:
                img_url = img_el['src'] if img_el else ""
                if img_url.startswith('/'): img_url = base + img_url
                
                items.append({
                    'title': title_el.get_text(strip=True),
                    'image': img_url,
                    'date': date_el.get_text(strip=True) if date_el else "Novo",
                    'source': 'UMAG.HR'
                })
    except: pass
    return items

def get_24sata_umag():
    """Scrapt 24sata.hr Tag Umag"""
    url = "https://www.24sata.hr/tagovi/umag-7674"
    headers = {'User-Agent': 'Mozilla/5.0'}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.select('.article_wrap')
        for art in articles[:5]:
            title_el = art.select_one('.card__title')
            img_el = art.select_one('img')
            if title_el:
                img_url = img_el['src'] if img_el else ""
                # Qualität bei 24sata Bildern verbessern
                img_url = img_url.replace('/120x120/', '/640x480/')
                
                items.append({
                    'title': title_el.get_text(strip=True),
                    'image': img_url,
                    'date': "24 Sata",
                    'source': '24SATA'
                })
    except: pass
    return items

def get_index_umag():
    """Scrapt index.hr Tag Umag"""
    url = "https://www.index.hr/tag/32559/umag.aspx"
    headers = {'User-Agent': 'Mozilla/5.0'}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Erster großer Artikel
        first = soup.select_one('.first-news-holder')
        if first:
            items.append({
                'title': first.select_one('.title').get_text(strip=True),
                'image': first.select_one('img')['src'],
                'date': first.select_one('.publish-date').get_text(strip=True),
                'source': 'INDEX.HR'
            })
        # Weitere Artikel
        grid = soup.select('.grid-item')
        for art in grid[:4]:
            items.append({
                'title': art.select_one('.title').get_text(strip=True),
                'image': art.select_one('img')['src'],
                'date': art.select_one('.publish-date').get_text(strip=True),
                'source': 'INDEX.HR'
            })
    except: pass
    return items

def generate_html(news):
    tz = pytz.timezone('Europe/Zagreb')
    now = datetime.now(tz).strftime("%d.%m.%Y - %H:%M")
    
    slides_html = ""
    for i, item in enumerate(news):
        active_class = "active" if i == 0 else ""
        img_url = item['image']
        # Index Bilder für XXL schärfen
        if 'index.hr' in img_url and '?' in img_url:
            img_url = img_url.split('?')[0] + "?width=1200&height=630&mode=crop"

        slides_html += f"""
        <div class="slide {active_class}">
            <div class="image-container">
                <img src="{img_url}" onerror="this.src='https://placehold.co/1200x630/003366/FFFFFF?text=UMAG+VIJESTI'">
                <div class="img-overlay"></div>
            </div>
            <div class="content-box">
                <div class="meta-line">
                    <span class="source">{item['source']}</span>
                    <span class="pub-time">{item['date']}</span>
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
    <title>Umag News Radar XXL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@800;900&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        body, html {{ 
            margin: 0; padding: 0; width: 100%; height: 100%; 
            background-color: black; color: white; font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .header-info {{
            position: fixed; top: 15px; right: 20px; z-index: 100;
            background: rgba(0, 51, 102, 0.9); color: white;
            padding: 5px 15px; border-radius: 8px;
            font-family: 'JetBrains Mono'; font-size: 1.2rem;
            font-weight: 800; box-shadow: 0 0 15px rgba(0,0,0,0.5);
            border: 1px solid #ffcc00;
        }}
        .slide {{
            position: absolute; width: 100%; height: 100%;
            display: none; flex-direction: column;
        }}
        .slide.active {{ display: flex; animation: fadeIn 0.8s ease-in; }}
        .image-container {{ width: 100%; height: 55vh; position: relative; overflow: hidden; }}
        .image-container img {{ 
            width: 100%; height: 100%; object-fit: cover; 
            object-position: center top; border-bottom: 6px solid #ffcc00; 
        }}
        .img-overlay {{
            position: absolute; bottom: 0; left: 0; width: 100%; height: 25%;
            background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
        }}
        .content-box {{ 
            flex: 1; padding: 30px 60px; 
            background: linear-gradient(to bottom, #001a33, #000);
            display: flex; flex-direction: column; justify-content: flex-start;
        }}
        .meta-line {{ display: flex; gap: 30px; align-items: center; margin-bottom: 20px; }}
        .source {{ color: #ffcc00; font-weight: 900; font-size: 3rem; letter-spacing: 2px; }}
        .pub-time {{ color: #ffffff; font-family: 'JetBrains Mono'; font-size: 2.8rem; font-weight: 800; opacity: 0.8; }}
        .title {{ 
            font-size: 4.5rem; font-weight: 900; line-height: 1.05; 
            text-transform: uppercase; letter-spacing: -2px; color: #ffffff;
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="header-info">UMAG INFO: {now}</div>
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
        setInterval(nextSlide, 12000); 
        setTimeout(() => {{ location.reload(); }}, 3600000);
    </script>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    all_news = get_umag_hr() + get_24sata_umag() + get_index_umag()
    generate_html(all_news)

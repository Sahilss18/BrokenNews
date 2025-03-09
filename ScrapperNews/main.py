from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

CATEGORY_URLS = {
    "home": [
        "https://timesofindia.indiatimes.com/home/headlines",
        "https://www.bbc.com/news"
    ],
    "entertainment": [
        "https://timesofindia.indiatimes.com/entertainment",
        "https://www.bbc.com/news/entertainment_and_arts"
    ],
    "sports": [
        "https://timesofindia.indiatimes.com/sports",
        "https://www.bbc.com/sport"
    ],
    "india": [
        "https://timesofindia.indiatimes.com/india"
    ],
    "world": [
        "https://timesofindia.indiatimes.com/world",
        "https://www.bbc.com/news/world"
    ],
    "business": [
        "https://timesofindia.indiatimes.com/business",
        "https://www.bbc.com/news/business"
    ],
    "technology": [
        "https://timesofindia.indiatimes.com/technology",
        "https://www.bbc.com/news/technology"
    ],
    "health": [
        "https://timesofindia.indiatimes.com/life-style/health-fitness",
        "https://www.bbc.com/news/health"
    ],
    "education": [
        "https://timesofindia.indiatimes.com/education"
    ],
    "english": [
        "https://timesofindia.indiatimes.com/briefs"
    ]
}


def get_news_headlines(category="home"):
    urls = CATEGORY_URLS.get(category, CATEGORY_URLS["home"])
    headlines = []

    for url in urls:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if "timesofindia" in url:
                for link in soup.find_all('a', href=True):
                    title = link.text.strip()
                    href = link['href']
                    if title and "/articleshow" in href:
                        full_link = "https://timesofindia.indiatimes.com" + href
                        headlines.append((title, full_link))

            elif "bbc" in url:
                for item in soup.find_all('a', href=True):
                    title = item.text.strip()
                    href = item['href']
                    if title and href.startswith("/news"):
                        full_link = "https://www.bbc.com" + href
                        headlines.append((title, full_link))

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")

    return headlines


def highlight_text(text, query):
    """Highlight the search query inside the text"""
    if not query:
        return text
    return re.sub(f'({re.escape(query)})', r'<mark>\1</mark>', text, flags=re.IGNORECASE)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/category/<category>', methods=['GET', 'POST'])
def category_page(category):
    headlines = get_news_headlines(category)
    search_query = None
    search_result = []
    no_results = False

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip().lower()

        if search_query:
            search_result = [(highlight_text(title, search_query), link)
                             for title, link in headlines if search_query in title.lower()]

            if not search_result:
                no_results = True

    return render_template('category.html', category=category.capitalize(),
                           headlines=search_result if search_query else headlines,
                           search_query=search_query, no_results=no_results)


if __name__ == '__main__':
    app.run(debug=True)

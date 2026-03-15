import feedparser

# lê o feed do G1 (RSS)
URL = "https://g1.globo.com/rss/g1/"

def buscar_noticias (url):
    feed = feedparser.parse(url)
    print (f"Fonte: {feed.feed.title}") # type: ignore
    print (f"Total de notícias: {len(feed.entries)}")
    print ("-" * 50)

    for noticia in feed.entries [:10]:
        print (f"📰 {noticia.title}")
        print (f"🕒 {noticia.published}")
        print (f"🔗 {noticia.link}")
        print ()

buscar_noticias (URL)
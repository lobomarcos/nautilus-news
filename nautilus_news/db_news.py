import feedparser
import sqlite3

URL = "https://g1.globo.com/rss/g1/"

def criar_banco():
    conn = sqlite3.connect ("noticias.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            link TEXT UNIQUE,
            publicado TEXT,
            fonte TEXT
        )
    """)
    conn.commit()
    return conn

def salvar_noticias (conn, noticias, fonte):
    cursor = conn.cursor()
    salvas = 0

    for noticia in noticias:
        try:
            cursor.execute ("""
                INSERT INTO noticias (titulo, link, publicado, fonte)
                VALUES (?, ?, ?, ?)    
            """, (
                noticia.get ("title", "Sem título"),
                noticia.get ("link", ""),
                noticia.get ("published", ""),
                fonte
            ))
            salvas += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit ()
    print (f"✅ {salvas} notícias salvas no banco!")

def buscar_noticias (url):
    feed = feedparser.parse (url)
    fonte = feed.feed.get("title", "Desconhecida") # type: ignore
    print (f"📡 Buscando de: {fonte}")
    print (f"{len(feed.entries)} notícias encontradas")
    return feed.entries, fonte


# cria o banco e guarda a conexão
conn = criar_banco()
# busca as notícias e guarda na variável 'notícias' e o nome da fonte em 'fonte'
noticias, fonte = buscar_noticias (URL)
# salva tudo no db
salvar_noticias (conn, noticias, fonte)
# fecha a conexão
conn.close ()

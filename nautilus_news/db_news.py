import feedparser
import sqlite3

URL = "https://g1.globo.com/rss/g1/"

# inicia o db
def criar_banco():
    conn = sqlite3.connect("noticias.db")
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

# salva as noticias no db
def salvar_noticias(conn, noticias, fonte):
    cursor = conn.cursor()
    salvas = 0

    for noticia in noticias:
        try:
            cursor.execute("""
                INSERT INTO noticias (titulo, link, publicado, fonte)
                VALUES (?, ?, ?, ?)
            """, (
                noticia.get("title", "Sem título"),
                noticia.get("link", ""),
                noticia.get("published", ""),
                fonte
            ))
            salvas += 1
        except sqlite3.IntegrityError:
            pass  # notícia já existe no banco, ignora

    conn.commit()
    print(f"✅ {salvas} notícias salvas no banco!")

# busca as noticias
def buscar_noticias(url):
    feed = feedparser.parse(url)
    fonte = feed.feed.get("title", "Desconhecida") # type: ignore
    print(f"📡 Buscando de: {fonte}")
    print(f"{len(feed.entries)} notícias encontradas")
    return feed.entries, fonte

# executa o banco
conn = criar_banco()
noticias, fonte = buscar_noticias(URL)
salvar_noticias(conn, noticias, fonte)
conn.close()
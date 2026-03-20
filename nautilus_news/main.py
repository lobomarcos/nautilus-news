import feedparser
import sqlite3
import webbrowser
import customtkinter as ctk

# fontes RSS
FONTES = [
    {"nome": "G1", "url": "https://g1.globo.com/rss/g1/"},  
    {"nome": "Intercept Brasil", "url": "https://intercept.com.br/feed/"},
    {"nome": "Brasil de Fato", "url": "https://www.brasildefato.com.br/feed/"},
    {"nome": "ICL Notícias", "url": "https://iclnoticias.com.br/feed/"},  
]

# banco de dados
def criar_banco (conn):
    cursor = conn.cursor ()
    cursor.execute ("""
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            link TEXT UNIQUE,
            publicado TEXT,
            fonte TEXT
        )
    """)
    conn.commit ()

def salvar_noticias (conn, entradas, fonte_nome):
    cursor = conn.cursor()
    salvas = 0
    for noticia in entradas:
        try:
            cursor.execute ("""
                INSERT INTO noticias (titulo, link, publicado, fonte)
                VALUES (?, ?, ?, ?)
            """, (
                noticia.get ("title", "Sem Título"),
                noticia.get ("link", ""),
                noticia.get ("published", ""),
                fonte_nome,    
            ))
            salvas += 1
        except sqlite3.IntegrityError:
            pass # se já existir, ele ignora
    conn.commit ()
    return salvas

def busca_salva_todas (conn, fontes, log_callback = None):
    """Percorre todas as fontes RSS e salva no banco."""
    total = 0
    for fonte in fontes:
        try:
            feed = feedparser.parse (fonte ["url"])
            qtd = salvar_noticias (conn, feed.entries, fonte["nome"])
            total += qtd
            if log_callback:
                log_callback (f"✅ {fonte['nome']}: {qtd} novas notícias")
        except Exception as e:
            if log_callback:
                log_callback (f"⚠️ Erro em {fonte['nome']}: {e}")
        return total
    
def carregar_noticias (conn):
    cursor = conn.cursor ()
    cursor.execute ("""
        SELECT titulo, link, publicado, fonte
        FROM noticias
        ORDER BY id DESC
    """)
    return cursor.fetchall ()
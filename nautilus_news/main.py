import feedparser
import sqlite3
import webbrowser
import customtkinter as ctk
from datetime import datetime

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

# cores por fonte
CORES_FONTE = {
    "G1": "#bd0000",
    "Intercept Brasil": "#2e2e2e",
    "Brasil de Fato": "#FF0000",
    "ICL Notícias": "#0062f5",
}

def cor_fonte (nome):
    return CORES_FONTE.get (nome, "#555555")

# interface
def abrir_link (link):
    webbrowser.open (link)

def construir_interface (conn):
    ctk.set_appearance_mode ("dark")
    ctk.set_default_color_theme ("blue")
    
    app = ctk.CTk ()
    app.title ("Nautilus News")
    app.geometry ("1920x1080")
    app.minsize (960, 540)

    # header
    header = ctk.CTkFrame (app, fg_color = "#0d1117", corner_radius = 0)
    header.pack (fill = "x", padx = 0, pady = 0)

    ctk.CTkLabel (
        header,
        text = "Nautilus News",
        font = ctk.CTkFont (size = 22, weight = "bold"),
        text_color = "#e0e6f0",    
    ).pack (side = "left", padx = 20, pady = 14)

    status_label = ctk.CTkLabel (
        header,
        text = "",
        font = ctk.CTkFont (size = 11),
        text_color = "#6e7681",
    )
    status_label.pack (side = "right", padx = 20)

    # barra de filtro por fonte
    filtro_frame = ctk.CTkFrame (app, fg_color = "#161b22", corner_radius = 0)
    filtro_frame.pack (fill = "x")

    fonte_var = ctk.StringVar (value = "Todas")

    def atualizar_lista (fonte_filtro = "Todas"):
        for widget in lista_frame.winfo_children ():
            widget.destroy ()

        noticias = carregar_noticias (conn)
        exibidas = 0

        for titulo_noticia, link, publicado, fonte in noticias:
            if fonte_filtro != "Todas" and fonte != fonte_filtro:
                continue

            exibidas += 1
            card = ctk.CTkFrame (lista_frame, fg_color = "#1c2128", corner_radius = 8)
            card.pack (fill = "x", padx = 8, pady = 4)

            # badge colorido da fonte
            badge = ctk.CTkLabel (
                card,
                text = f"{fonte}",
                font = ctk.CTkFont (size = 10, weight = "bold"),
                fg_color = cor_fonte (fonte),
                text_color = "white",
                corner_radius = 4,
            )
            badge.pack (anchor = "w", padx = 10, pady = (8, 2))

            #titulo clicavel
            btn = ctk.CTkButton (
                card,
                text = titulo_noticia,
                anchor = "w",
                fg_color = "transparent",
                hover_color = "#2d333b",
                font = ctk.CTkFont (size = 13),
                text_color = "#c9d1d9",
                command = lambda l = link: abrir_link (1),
            )
            btn.pack (fill = "x", padx = 6, pady = (0, 2))

            # data
            ctk.CTkLabel (
                card,
                text = f"🕒{publicado}",
                font = ctk.CTkFont (size = 10),
                text_color = "#6e7681",
            ).pack (anchor = "w", padx = 12, pady = (0, 8))

        status_label.configure (text = f"{exibidas} notícias exibidas")
    
    # botões de filtro
    opcoes = ["Todas"] + [f["nome"] for f in FONTES]
    botoes_filtro = {}

    def selecionar_filtro (nome):
        fonte_var.set (nome)
        for n, b in botoes_filtro.items ():
            b.configure (
                fg_color = cor_fonte (n) if n != "Todas" and n == nome else (
                    "#1f6feb" if n == "Todas" and nome == "Todas" else "transparent"
                ),
                text_color = "white" if n == nome else "#8b949e",
            )
        atualizar_lista (nome)

    for opcao in opcoes:
        cor_bg = "#1f6feb" if opcao == "Todas" else "transparent"
        b = ctk.CTkButton (
            filtro_frame,
            text = opcao,
            width = 90,
            height = 28,
            fg_color = cor_bg,
            hover_color = "#2d333b",
            text_color = "white" if opcao == "Todas" else "#8b949e",
            font = ctk.CTkFont (size = 11),
            command = lambda o = opcao: selecionar_filtro (o),
        )
        b.pack (side = "left", padx = 6, pady = 8)
        botoes_filtro [opcao] = b

    # botao de atualizar
    def atualizar_noticias ():
        btn_atualizar.configure (state = "disabled", text = "⏳ Buscando...")
        app.update()

        logs = []
        busca_salva_todas (conn, FONTES, log_callback = logs.append)
        atualizar_lista (fonte_var.get())

        btn_atualizar.configure (state = "normal", text = "🔄 Atualizar")
        status_label.configure (text = f"Atualizado às {datetime.now().strftime('%H:%M')}")
    
    btn_atualizar = ctk.CTkButton (
        filtro_frame,
        text = "🔄 Atualizar",
        width = 100,
        height = 28,
        fg_color="#238636",
        hover_color="#2ea043",
        font = ctk.CTkFont (size = 11),
        command = atualizar_noticias,
    )
    btn_atualizar.pack (side = "right", padx = 10, pady = 8)

    # lista com rolagem
    lista_frame = ctk.CTkScrollableFrame (app, fg_color = "#0d1117")
    lista_frame.pack (fill = "both", expand = True, padx = 0, pady = 0)

    # faz o app carregar ao iniciar
    atualizar_lista ()

    app.mainloop ()

# entry point
if __name__ == "__main__":
    conn = sqlite3.connect ("noticias.db")
    criar_banco (conn)
    print("🔭 Nautilus News iniciando...")
    print("📡 Buscando notícias das fontes...")
    busca_salva_todas (conn, FONTES, log_callback = print)
    print("🖥️ Abrindo interface...\n")
    construir_interface(conn)
    conn.close()
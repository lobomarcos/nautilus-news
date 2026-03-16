import customtkinter as ctk
import sqlite3
import webbrowser

# define o tema como "dar
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# carrega as noticias que tem no db
def carregar_noticias():
    conn = sqlite3.connect("noticias.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT titulo, link, publicado, fonte FROM noticias ORDER BY id DESC""")
    noticias = cursor.fetchall()
    conn.close()
    return noticias

# abre o link ao clicar na noticia
def abrir_link(link):
    webbrowser.open(link)

# faz a janela do app
def construir_interface():
    app = ctk.CTk()
    app.title("Nautilus News")
    app.geometry("900x600")

    # titulo do app
    titulo = ctk.CTkLabel(app, text="Nautilus News", font=ctk.CTkFont(size=24, weight="bold"))
    titulo.pack(pady=20)

    # faz o scroll
    frame = ctk.CTkScrollableFrame(app, width=1920, height=1080)
    frame.pack(padx=20, pady=20)

    # carrega e mostra as noticias
    noticias = carregar_noticias()

    for noticia in noticias:
        titulo_noticia, link, publicado, fonte = noticia

        # card individual das noticias
        card = ctk.CTkFrame(frame)
        card.pack(fill="x", padx=10, pady=5)

        # faz o titulo da noticia ser clicavel
        btn = ctk.CTkButton(
            card,
            text=titulo_noticia,
            anchor="w",
            fg_color="transparent",
            hover_color="#2a2d2e",
            font=ctk.CTkFont(size=13),
            command=lambda l=link: abrir_link(l)
        )
        btn.pack(fill="x", padx=0, pady=(8, 2))

        # mostra a fonte e data
        info = ctk.CTkLabel(
            card,
            text=f"📰 {fonte}  •  🕒 {publicado}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info.pack(anchor="w", padx=8, pady=(0, 8))

    app.mainloop()

construir_interface()
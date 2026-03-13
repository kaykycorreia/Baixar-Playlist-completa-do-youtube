import os
import threading
import tkinter as tk
from tkinter import messagebox
from yt_dlp import YoutubeDL

download_folder = os.path.join(os.path.expanduser("~"), "YK download")
os.makedirs(download_folder, exist_ok=True)

YOUTUBE_RED = "#FF0000"
WHITE = "#FFFFFF"

cancelar = False


def limpar_link(url):

    if "list=" in url:
        playlist_id = url.split("list=")[1].split("&")[0]
        return f"https://www.youtube.com/playlist?list={playlist_id}"

    return url


def baixar_playlist(url, formato, lista):

    global cancelar

    def hook(d):

        if cancelar:
            raise Exception("Download cancelado")

        if d['status'] == 'downloading':

            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()

            texto = f"⬇ {percent} | {speed} | ETA {eta}"

            lista.insert(tk.END, texto)
            lista.see(tk.END)

        if d['status'] == 'finished':

            lista.insert(tk.END, "✔ Vídeo concluído\n")
            lista.see(tk.END)

    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(playlist_index)s - %(title)s.%(ext)s'),
        'ignoreerrors': True,
        'progress_hooks': [hook],
        'quiet': True
    }

    if formato == "mp3":

        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        })

    else:

        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best'
        })

    try:

        lista.insert(tk.END, "🚀 Iniciando downloads...\n")

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        lista.insert(tk.END, "\n✔ Todos downloads finalizados\n")

        messagebox.showinfo("Finalizado", "Downloads finalizados ✔")

    except Exception as e:

        lista.insert(tk.END, f"\n⚠ {str(e)}")


def iniciar_download():

    global cancelar
    cancelar = False

    url = entrada.get().strip()

    if not url:
        messagebox.showerror("Erro", "Cole o link da playlist")
        return

    url = limpar_link(url)

    formato = formato_var.get()

    if formato == "":
        messagebox.showerror("Erro", "Escolha MP3 ou MP4")
        return

    janela = tk.Toplevel()
    janela.title("Downloads")
    janela.geometry("800x550")
    janela.configure(bg=WHITE)

    frame_log = tk.Frame(janela)
    frame_log.pack(padx=20, pady=20, fill="both", expand=True)

    scroll = tk.Scrollbar(frame_log)
    scroll.pack(side="right", fill="y")

    lista = tk.Listbox(
        frame_log,
        width=100,
        height=30,
        font=("Consolas",10),
        bg="#0f0f0f",
        fg="#00ff00",
        yscrollcommand=scroll.set
    )

    lista.pack(side="left", fill="both", expand=True)

    scroll.config(command=lista.yview)

    botao_cancelar = tk.Button(
        janela,
        text="CANCELAR DOWNLOAD",
        bg="black",
        fg="white",
        width=20,
        command=cancelar_download
    )

    botao_cancelar.pack(pady=10)

    thread = threading.Thread(
        target=baixar_playlist,
        args=(url, formato, lista),
        daemon=True
    )

    thread.start()


def cancelar_download():

    global cancelar
    cancelar = True


app = tk.Tk()
app.title("YK Playlist Downloader")
app.geometry("520x340")
app.configure(bg=WHITE)

titulo = tk.Label(
    app,
    text="YK YouTube Downloader",
    font=("Segoe UI",18,"bold"),
    fg=YOUTUBE_RED,
    bg=WHITE
)

titulo.pack(pady=20)

entrada = tk.Entry(
    app,
    width=60,
    font=("Segoe UI",10)
)

entrada.pack(pady=10)

formato_var = tk.StringVar()

frame = tk.Frame(app, bg=WHITE)
frame.pack(pady=10)

tk.Radiobutton(frame, text="MP3", variable=formato_var, value="mp3", bg=WHITE).pack(side=tk.LEFT, padx=20)
tk.Radiobutton(frame, text="MP4", variable=formato_var, value="mp4", bg=WHITE).pack(side=tk.LEFT, padx=20)

botao = tk.Button(
    app,
    text="BAIXAR PLAYLIST",
    command=iniciar_download,
    bg=YOUTUBE_RED,
    fg="white",
    font=("Segoe UI",12,"bold"),
    width=20,
    height=2
)

botao.pack(pady=20)

app.mainloop()
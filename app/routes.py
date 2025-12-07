from app import app
from flask import render_template, request, send_file
import yt_dlp
import os
import re
import requests
import uuid
import threading


# --------------------------------------
# Função para validar links
# --------------------------------------
def validar_link(url):
    patterns = [
        # YouTube: vídeos normais, links curtos e shorts
        r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w-]+",
        # Facebook
        r"(https?://)?(www\.)?facebook\.com/.+",
        # Instagram
        r"(https?://)?(www\.)?instagram\.com/.+",
        # Twitch
        r"(https?://)?(www\.)?twitch\.tv/.+",
        # TikTok
        r"(https?://)?(www\.)?tiktok\.com/.+",
    ]
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False


# --------------------------------------
# Função para limpar nomes de arquivos
# --------------------------------------
def sanitize_filename(name):
    # Remove apenas caracteres inválidos do Windows
    return re.sub(r'[\\/*?:"<>|]', "", name)

# --------------------------------------
# Função para baixar TikTok sem login
# --------------------------------------
def baixar_tiktok_sem_login(url):
    api = "https://www.tikwm.com/api/"
    r = requests.post(api, data={"url": url}).json()

    if r["code"] != 0:
        raise Exception("Erro na API TikWM: " + r.get("msg", "Desconhecido"))

    return r["data"]["play"]  # URL do vídeo MP4 direto

# --------------------------------------
# Função para apagar arquivo após X segundos
# --------------------------------------
def apagar_arquivo_apos_tempo(filename, segundos=40):
    def apagar():
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass
    timer = threading.Timer(segundos, apagar)
    timer.start()

# --------------------------------------
# Rota principal
# --------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# --------------------------------------
# Rota de download
# --------------------------------------
@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('video_url')
    if not url:
        return "Você precisa fornecer um link de vídeo."

    # Valida o link antes de qualquer download
    if not validar_link(url):
        return "Link inválido! Por favor, cole um link válido do YouTube, TikTok, Instagram, Facebook ou Twitch."

    # Cria pasta downloads
    downloads_path = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(downloads_path, exist_ok=True)

    try:
        # ------------------------------
        # Caso seja TikTok
        # ------------------------------
        if "tiktok.com" in url:
            mp4_url = baixar_tiktok_sem_login(url)

            # Nome aleatório único
            filename = os.path.join(downloads_path, f"tiktok_{uuid.uuid4().hex}.mp4")

            # Baixa o vídeo
            r = requests.get(mp4_url)
            with open(filename, "wb") as f:
                f.write(r.content)

            # Apaga após 40 segundos
            apagar_arquivo_apos_tempo(filename, segundos=40)

            return send_file(filename, as_attachment=True)

        # ------------------------------
        # Caso seja YouTube ou outro site
        # ------------------------------
        else:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = os.path.join(
                    downloads_path,
                    sanitize_filename(ydl.prepare_filename(info_dict).split(os.sep)[-1])
                )

            # Apaga após 40 segundos
            apagar_arquivo_apos_tempo(filename, segundos=40)

            return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Erro ao baixar o vídeo: {e}"
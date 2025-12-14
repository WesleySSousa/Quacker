from app import app
from flask import render_template, request, send_file
import yt_dlp
import os
import re
import requests
import uuid
import threading


# ======================================
# VALIDAR LINKS
# ======================================
def validar_link(url):
    patterns = [
        # YouTube (normal, curto, shorts)
        r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w-]+",

        # Facebook
        r"(https?://)?(www\.)?facebook\.com/.+",

        # Instagram
        r"(https?://)?(www\.)?instagram\.com/.+",

        # Twitch
        r"(https?://)?(www\.)?twitch\.tv/.+",

        # TikTok (normal + vt.tiktok)
        r"(https?://)?(www\.)?(tiktok\.com/.+|vt\.tiktok\.com/[\w-]+)",
    ]

    return any(re.match(p, url) for p in patterns)


# ======================================
# SANITIZAR NOME DE ARQUIVO
# ======================================
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


# ======================================
# TIKTOK SEM LOGIN (API)
# ======================================
def baixar_tiktok_sem_login(url):
    api = "https://www.tikwm.com/api/"
    r = requests.post(api, data={"url": url}, timeout=20).json()

    if r.get("code") != 0:
        raise Exception("Erro ao baixar TikTok")

    return r["data"]["play"]


# ======================================
# APAGAR ARQUIVO APÓS X SEGUNDOS
# ======================================
def apagar_arquivo_apos_tempo(filename, segundos=40):
    def apagar():
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

    threading.Timer(segundos, apagar).start()


# ======================================
# ROTAS
# ======================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('video_url')

    if not url:
        return "Você precisa fornecer um link."

    if not validar_link(url):
        return "Link inválido."

    downloads_path = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(downloads_path, exist_ok=True)

    try:
        # ==========================
        # TIKTOK
        # ==========================
        if "tiktok.com" in url:
            mp4_url = baixar_tiktok_sem_login(url)
            filename = os.path.join(
                downloads_path, f"tiktok_{uuid.uuid4().hex}.mp4"
            )

            r = requests.get(mp4_url, timeout=30)
            with open(filename, "wb") as f:
                f.write(r.content)

            apagar_arquivo_apos_tempo(filename)
            return send_file(filename, as_attachment=True)

        # ==========================
        # YOUTUBE / INSTAGRAM / OUTROS
        # ==========================
        ydl_opts = {
            # MP4 progressivo até 720p
            'format': 'best[ext=mp4][height<=720]/best[height<=720]',
            'merge_output_format': 'mp4',

            'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),

            # client menos bloqueado
            'extractor_args': {
                'youtube': {
                    'player_client': ['android']
                }
            },

            # user-agent real
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Linux; Android 11; Pixel 5) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Mobile Safari/537.36'
                )
            },

            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = sanitize_filename(ydl.prepare_filename(info))

        apagar_arquivo_apos_tempo(filename)
        return send_file(filename, as_attachment=True)

    except Exception:
        return (
            "Não foi possível baixar este vídeo agora. "
            "Tente novamente mais tarde ou use outro link."
        )

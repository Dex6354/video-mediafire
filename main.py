import os
import re
import threading
import requests
from bs4 import BeautifulSoup
import streamlit as st
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

st.set_page_config(page_title="MediaFire 6GB Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Inabalável para Arquivos Grandes (6 GB+)")

# Configurações de caminhos
LOCAL_DIR = "videos"
os.makedirs(LOCAL_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_DIR, VIDEO_FILENAME)

# Servidor local para rodar o streaming por pedaços (Range Requests)
VIDEO_SERVER_PORT = 8999
VIDEO_STREAM_URL = f"http://127.0.0.1:{VIDEO_SERVER_PORT}/video.mp4"

# Links dos vídeos
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"


class VideoRangeRequestHandler(BaseHTTPRequestHandler):
    """Servidor HTTP leve que suporta Range Requests para o player do navegador"""
    def log_message(self, format, *args):
        pass  # Desativa logs no terminal

    def do_GET(self):
        if not os.path.exists(SAVE_PATH):
            self.send_error(404, "Arquivo não encontrado")
            return

        size = os.path.getsize(SAVE_PATH)
        start, end = 0, size - 1
        status = 200

        range_header = self.headers.get('Range')
        if range_header:
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                status = 206
                start = int(match.group(1))
                if match.group(2):
                    end = int(match.group(2))

        self.send_response(status)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Type', 'video/mp4')
        self.send_header('Access-Control-Allow-Origin', '*')  # Evita bloqueio de CORS
        
        if status == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.send_header('Content-Length', str(end - start + 1))
        else:
            self.send_header('Content-Length', str(size))
        self.end_headers()

        with open(SAVE_PATH, 'rb') as f:
            f.seek(start)
            remaining = end - start + 1
            chunk_size = 1024 * 1024  # 1MB por leitura
            while remaining > 0:
                chunk = f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (ConnectionResetError, BrokenPipeError):
                    break
                remaining -= len(chunk)


@st.cache_resource
def iniciar_servidor_de_video():
    """Inicia o servidor de streaming em segundo plano"""
    server = ThreadingHTTPServer(('0.0.0.0', VIDEO_SERVER_PORT), VideoRangeRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return True

# Inicializa o servidor independente
iniciar_servidor_de_video()


def get_mediafire_direct_link(url):
    """Extrai a URL direta de download do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado.")

    return download_button.get("href")


def download_video_with_progress(direct_link, output_path):
    """Baixa o vídeo para o disco atualizando a barra de progresso."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    video_response = requests.get(direct_link, headers=headers, stream=True)
    total_length = video_response.headers.get('content-length')
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    with open(output_path, "wb") as f:
        if total_length is None:
            f.write(video_response.content)
        else:
            total_length = int(total_length)
            bytes_baixados = 0
            chunk_size = 4096 * 1024  # 4MB direto no HD

            for chunk in video_response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    gb_baixados = bytes_baixados / (1024 ** 3)
                    gb_totais = total_length / (1024 ** 3)
                    
                    status_text.text(f"Progresso: {porcentagem}% ({gb_baixados:.2f} GB de {gb_totais:.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)


# Layout de Botões
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Baixar Vídeo 1 (Sample)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            st.info("Obtendo link do Vídeo 1...")
            link = get_mediafire_direct_link(VIDEO_1_URL)
            download_video_with_progress(link, SAVE_PATH)
            st.success("Vídeo 1 baixado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

with col2:
    if st.button("📥 Baixar Vídeo 2 (TEVEO 1 - 6GB)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            st.info("Obtendo link do Vídeo 2...")
            link = get_mediafire_direct_link(VIDEO_2_URL)
            download_video_with_progress(link, SAVE_PATH)
            st.success("Vídeo 2 (6GB) baixado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")


# Player de vídeo HTML5 Nativo injetado
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("🎬 Player Local Dedicado (Suporta avanço instantâneo):")
    
    st.markdown(
        f"""
        <div style="background-color: black; padding: 5px; border-radius: 8px;">
            <video width="100%" height="auto" controls preload="metadata">
                <source src="{VIDEO_STREAM_URL}" type="video/mp4">
                Seu navegador não suporta HTML5 video.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )

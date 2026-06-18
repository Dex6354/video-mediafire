import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MediaFire Downloader & Player", page_icon="🎬", layout="centered")
st.title("🎬 Baixar e Assistir Vídeos Grandes (6 GB+)")

# Cria e garante a pasta static local no projeto (evita erro de permissão do venv)
LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)

VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

# Links dos vídeos
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

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
    """Baixa o vídeo para o disco atualizando a barra de progresso e porcentagem."""
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
            chunk_size = 4096 * 1024  # Blocos de 4MB (RAM protegida)

            for chunk in video_response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    
                    # Cálculos de progresso
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    gb_baixados = bytes_baixados / (1024 ** 3)
                    gb_totais = total_length / (1024 ** 3)
                    
                    # Atualização em tempo real na tela
                    status_text.text(f"Progresso: {porcentagem}% ({gb_baixados:.2f} GB de {gb_totais:.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)

# Botões de seleção e download
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

# Só renderiza o player se o arquivo já tiver sido totalmente baixado no disco
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("🎬 Player Local (Executando do Disco sem carregar a RAM):")
    
    # Player de alta performance Plyr rodando o arquivo local da pasta static
    video_html = f"""
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    
    <div style="background-color: #000; padding: 5px; border-radius: 8px; overflow: hidden;">
        <video id="player" playsinline controls preload="metadata" style="width: 100%; height: 400px;">
            <source src="/static/{VIDEO_FILENAME}" type="video/mp4" />
        </video>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            new Plyr('#player', {{
                controls: ['play-large', 'play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'settings', 'pip', 'fullscreen'],
                ratio: '16:9'
            }});
        }});
    </script>
    """
    components.html(video_html, height=430)

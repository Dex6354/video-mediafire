import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 6GB Ultra-Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Direto do Disco (Suporta 6 GB+)")

# Garante a pasta estática local do Streamlit
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
            chunk_size = 4096 * 1024  # Blocos de 4MB salvos direto no HD

            for chunk in video_response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    
                    # Cálculos de progresso
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    gb_baixados = bytes_baixados / (1024 ** 3)
                    gb_totais = total_length / (1024 ** 3)
                    
                    status_text.text(f"Progresso: {porcentagem}% ({gb_baixados:.2f} GB de {gb_totais:.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)

# Botões de seleção
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

# Renderização direto no DOM principal usando st.markdown (Sem Iframes)
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("🎬 Player Local (Renderizado na página principal):")
    
    # O caminho relativo 'static/...' funciona perfeitamente aqui sem o bloqueio do iframe
    st.markdown(
        f"""
        <div style="background-color: black; padding: 10px; border-radius: 8px;">
            <video width="100%" height="auto" controls preload="auto" style="max-height: 480px;">
                <source src="static/{VIDEO_FILENAME}" type="video/mp4">
                Seu navegador não conseguiu renderizar o arquivo local da pasta static.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )

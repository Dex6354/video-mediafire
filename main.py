import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MediaFire Video Player", page_icon="🎬")
st.title("🎬 Player de Vídeo - Suporte para 6 GB+ (GitHub Ready)")

# Cria a pasta static local no ambiente de hospedagem se ela não existir
LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)

VIDEO_FILENAME = "temp_large_video.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)
VIDEO_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"

def download_mediafire_video(url, output_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 1. Extrai o link direto
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Botão de download não encontrado. O link pode ter expirado.")

    direct_link = download_button.get("href")
    video_response = requests.get(direct_link, headers=headers, stream=True)
    
    if "text/html" in video_response.headers.get("Content-Type", ""):
        raise Exception("O MediaFire bloqueou o download automatizado.")

    total_length = video_response.headers.get('content-length')
    
    # Elementos visuais do progresso no Streamlit
    progress_bar = st.progress(0)
    status_text = st.empty()

    with open(output_path, "wb") as f:
        if total_length is None:
            f.write(video_response.content)
        else:
            total_length = int(total_length)
            bytes_baixados = 0
            chunk_size = 4096 * 1024  # Blocos de 4MB para poupar RAM

            for chunk in video_response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    
                    # Cálculos de progresso
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    gb_baixados = bytes_baixados / (1024 ** 3)
                    gb_totais = total_length / (1024 ** 3)
                    
                    status_text.text(f"Baixando: {porcentagem}% ({gb_baixados:.2f} GB de {gb_totais:.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)

# Interface de usuário
if st.button("Iniciar Download do Vídeo"):
    try:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
        download_mediafire_video(VIDEO_URL, SAVE_PATH)
        st.success("Download concluído com sucesso no servidor!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro: {e}")

# Exibe o player usando HTML5 nativo integrado à rota estática
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("Visualização Online:")
    
    video_html = f"""
    <video width="100%" height="100%" controls preload="metadata">
        <source src="/static/{VIDEO_FILENAME}" type="video/mp4">
        Seu navegador não suporta o player de vídeo HTML5.
    </video>
    """
    components.html(video_html, height=500)

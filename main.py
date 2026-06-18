import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MediaFire Video Player", page_icon="🎬")
st.title("🎬 Player de Vídeo - Suporte para Arquivos de 6 GB+")

# 1. Identifica a pasta estática interna do Streamlit
STREAMLIT_STATIC_PATH = os.path.join(os.path.dirname(st.__file__), 'static')
VIDEO_FILENAME = "temp_large_video.mp4"
SAVE_PATH = os.path.join(STREAMLIT_STATIC_PATH, VIDEO_FILENAME)

VIDEO_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"

def download_mediafire_video(url, output_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Extrai o link direto do MediaFire
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Botão de download não encontrado. O link pode ter expirado.")

    direct_link = download_button.get("href")

    # Baixa o arquivo em blocos de 4MB salvando direto no HD (RAM limpa)
    video_response = requests.get(direct_link, headers=headers, stream=True)
    
    if "text/html" in video_response.headers.get("Content-Type", ""):
        raise Exception("O MediaFire bloqueou o download automatizado.")

    with open(output_path, "wb") as f:
        for chunk in video_response.iter_content(chunk_size=4096 * 1024):
            if chunk:
                f.write(chunk)

# Interface de Download
if st.button("Baixar Vídeo de 6 GB no Servidor"):
    with st.spinner("Baixando o arquivo para o disco do servidor... Como são 6 GB, isso vai levar alguns minutos."):
        try:
            if os.path.exists(SAVE_PATH):
                os.remove(SAVE_PATH)
            download_mediafire_video(VIDEO_URL, SAVE_PATH)
            st.success("Vídeo baixado com sucesso no servidor!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# 2. Renderiza o player usando HTML5 puro conectado à rota estática do Streamlit
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("Visualização Online (Streaming ativo por demanda):")
    
    # O uso da barra '/' antes de static garante que o navegador busque a raiz do servidor Streamlit
    video_html = f"""
    <video width="100%" height="100%" controls preload="metadata">
        <source src="/static/{VIDEO_FILENAME}" type="video/mp4">
        Seu navegador não suporta o player de vídeo HTML5.
    </video>
    """
    # Renderiza o player em uma camada HTML isolada e leve
    components.html(video_html, height=500)

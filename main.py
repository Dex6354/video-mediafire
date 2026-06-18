import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

st.set_page_config(page_title="MediaFire Multi-Stream", page_icon="🎬")
st.title("🎬 Player de Streaming Direto (Video.js Avançado)")

# Links dos vídeos
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

def get_mediafire_direct_link(url):
    """Extrai a URL final do arquivo de vídeo do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado.")

    return download_button.get("href")

# Duas colunas para os botões
col1, col2 = st.columns(2)

with col1:
    if st.button("🎬 Carregar Vídeo 1 (Sample)", use_container_width=True):
        with st.spinner("Conectando ao Vídeo 1..."):
            try:
                st.session_state["stream_link"] = get_mediafire_direct_link(VIDEO_1_URL)
                st.session_state["video_atual"] = "Vídeo 1 (Sample)"
            except Exception as e:
                st.error(f"Erro no Vídeo 1: {e}")

with col2:
    if st.button("🎬 Carregar Vídeo 2 (TEVEO 1)", use_container_width=True):
        with st.spinner("Conectando ao Vídeo 2 (6GB)..."):
            try:
                st.session_state["stream_link"] = get_mediafire_direct_link(VIDEO_2_URL)
                st.session_state["video_atual"] = "Vídeo 2 (TEVEO 1 - 6GB)"
            except Exception as e:
                st.error(f"Erro no Vídeo 2: {e}")

# Exibe o player robusto caso um link tenha sido gerado
if "stream_link" in st.session_state:
    st.markdown("---")
    st.subheader(f"Reproduzindo: {st.session_state['video_atual']}")
    
    # Player HTML injetando a biblioteca Video.js para alta performance com arquivos grandes
    video_html = f"""
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    
    <div style="background-color: black; padding: 10px; display: flex; justify-content: center; align-items: center;">
        <video 
            id="media-player" 
            class="video-js vjs-default-skin vjs-big-play-centered" 
            controls 
            preload="metadata" 
            style="width: 100%; height: 420px;"
            data-setup='{{"fluid": true, "playbackRates": [0.5, 1, 1.5, 2]}}'>
            <source src="{st.session_state['stream_link']}" type="video/mp4">
            <p class="vjs-no-js">Seu navegador não suporta JavaScript ou o formato do vídeo.</p>
        </video>
    </div>
    """
    
    components.html(video_html, height=460)

import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

st.set_page_config(page_title="MediaFire Ultra-Stream", page_icon="🎬", layout="centered")
st.title("🎬 Player de Streaming Comercial (Plyr)")

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

# Seleção de vídeos
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

# Renderização do Player de Alta Performance
if "stream_link" in st.session_state:
    st.markdown("---")
    st.subheader(f"Reproduzindo: {st.session_state['video_atual']}")
    
    # Player Plyr via CDN com tratamento de buffer aprimorado
    video_html = f"""
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    
    <div style="background-color: #000; padding: 5px; border-radius: 8px; overflow: hidden;">
        <video id="player" playsinline controls preload="metadata" style="width: 100%; height: 400px;">
            <source src="{st.session_state['stream_link']}" type="video/mp4" />
        </video>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const player = new Plyr('#player', {{
                controls: ['play-large', 'play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'captions', 'settings', 'pip', 'fullscreen'],
                ratio: '16:9',
                tooltips: {{ controls: true, seek: true }}
            }});
        }});
    </script>
    """
    
    components.html(video_html, height=430)
    
    # Rota de fuga caso o servidor do MediaFire derrube o streaming do arquivo de 6GB
    st.info("💡 Se o player travar devido ao tamanho de 6GB, use o botão abaixo para abrir o streaming nativo direto da nuvem deles:")
    st.link_button("🚀 Abrir Link Direto no Navegador", st.session_state["stream_link"], use_container_width=True)

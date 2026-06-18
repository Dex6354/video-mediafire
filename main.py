import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 6GB Player", page_icon="🎬", layout="centered")
st.title("🎬 Player MediaFire (Suporte a Arquivos Grandes - 6GB+)")

# Links dos vídeos do MediaFire
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

def get_mediafire_direct_link(url):
    """Extrai a URL direta de download do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        download_button = soup.find("a", id="downloadButton")
        if download_button:
            return download_button.get("href")
    except Exception as e:
        st.error(f"Erro ao conectar com o MediaFire: {e}")
    return None

# Inicializa o estado da sessão
if "direct_link" not in st.session_state:
    st.session_state.direct_link = None
if "video_nome" not in st.session_state:
    st.session_state.video_nome = ""

# Layout de Botões
col1, col2 = st.columns(2)

with col1:
    if st.button("🎬 Carregar Vídeo 1 (5MB)", use_container_width=True):
        with st.spinner("Obtendo link do Vídeo 1..."):
            st.session_state.direct_link = get_mediafire_direct_link(VIDEO_1_URL)
            st.session_state.video_nome = "Vídeo 1 (Sample)"

with col2:
    if st.button("🎬 Carregar Vídeo 2 (6GB)", use_container_width=True):
        with st.spinner("Obtendo link do Vídeo 2..."):
            st.session_state.direct_link = get_mediafire_direct_link(VIDEO_2_URL)
            st.session_state.video_nome = "Vídeo 2 (TEVEO 1 - 6GB)"

# Renderização do Player
if st.session_state.direct_link:
    st.markdown("---")
    st.subheader(f"Reproduzindo: {st.session_state.video_nome}")
    
    # O player HTML5 consome os dados direto do CDN do MediaFire por demanda.
    # Funciona instantaneamente e aceita avançar o vídeo (Seek) sem travar.
    st.markdown(
        f"""
        <div style="background-color: black; padding: 5px; border-radius: 8px;">
            <video width="100%" height="auto" controls preload="metadata">
                <source src="{st.session_state.direct_link}" type="video/mp4">
                Seu navegador não suporta HTML5 video ou o link expirou.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.caption(f"🔗 [Link direto de download se preferir]({st.session_state.direct_link})")

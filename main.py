import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="MediaFire Video Player", page_icon="🎬")
st.title("🎬 Player de Vídeo - MediaFire (Suporte a 6 GB+)")

# Link do vídeo
VIDEO_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"

def get_mediafire_direct_link(url):
    """Extrai apenas a URL direta de download do MediaFire sem baixar o arquivo."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado.")

    return download_button.get("href")

# Botão para carregar o player
if st.button("Carregar Vídeo para o Player"):
    with st.spinner("Obtendo link de streaming direto do MediaFire..."):
        try:
            # Obtém o link direto (URL final do arquivo .mp4)
            direct_link = get_mediafire_direct_link(VIDEO_URL)
            # Salva no estado da sessão para não perder ao renderizar o vídeo
            st.session_state["video_direct_link"] = direct_link
            st.success("Link de streaming gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")

# Exibe o player utilizando o link direto gerado
if "video_direct_link" in st.session_state:
    st.markdown("---")
    st.subheader("Visualização Online:")
    try:
        # O navegador faz o streaming direto da nuvem do MediaFire, evitando crash de RAM de 6GB
        st.video(st.session_state["video_direct_link"])
    except Exception as e:
        st.error(f"Erro ao renderizar o player: {e}")

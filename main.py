import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire Video Player", page_icon="🎬")
st.title("🎬 Player de Vídeo - MediaFire")

# URL fornecida
VIDEO_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=y8d67l7c2pd&r=111"
SAVE_PATH = "temp_video.mp4"


@st.cache_data(show_spinner=False)
def download_mediafire_video(url, output_path):
    """Extrai o link direto do MediaFire e baixa o vídeo."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # 1. Faz a requisição na página para extrair o link de download direto
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception(
            "Não foi possível encontrar o botão de download. O link pode ter expirado."
        )

    direct_link = download_button.get("href")

    # 2. Faz o download do arquivo de vídeo
    video_response = requests.get(direct_link, headers=headers, stream=True)
    with open(output_path, "wb") as f:
        for chunk in video_response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


# Interface do Streamlit
if st.button("Baixar e Carregar Vídeo"):
    with st.spinner("Extraindo link e baixando o vídeo para o servidor..."):
        try:
            download_mediafire_video(VIDEO_URL, SAVE_PATH)
            st.success("Download concluído com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")

# Exibe o player caso o arquivo já exista localmente
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("Visualização Online:")
    st.video(SAVE_PATH)

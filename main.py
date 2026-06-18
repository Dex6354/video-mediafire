import os
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="MediaFire Video Player", page_icon="🎬")
st.title("🎬 Player de Vídeo - MediaFire")

VIDEO_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=y8d67l7c2pd&r=111"
SAVE_PATH = "temp_video.mp4"

def download_mediafire_video(url, output_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 1. Extrai o link direto de download
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado ou o MediaFire bloqueou o acesso.")

    direct_link = download_button.get("href")

    # 2. Baixa o vídeo em blocos (stream)
    video_response = requests.get(direct_link, headers=headers, stream=True)
    
    # Validação: Se o tipo do conteúdo for HTML, o MediaFire bloqueou o download
    if "text/html" in video_response.headers.get("Content-Type", ""):
        raise Exception("O MediaFire retornou uma página de erro (Captcha/Bloqueio) em vez do arquivo de vídeo.")

    # Salva o arquivo no disco
    with open(output_path, "wb") as f:
        for chunk in video_response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

# Botão para iniciar o download
if st.button("Baixar e Carregar Vídeo"):
    with st.spinner("Fazendo download do vídeo..."):
        try:
            # Remove arquivo antigo para evitar conflitos
            if os.path.exists(SAVE_PATH):
                os.remove(SAVE_PATH)
                
            download_mediafire_video(VIDEO_URL, SAVE_PATH)
            st.success("Download concluído com sucesso!")
            st.rerun() # Recarrega a página para atualizar o player de forma limpa
        except Exception as e:
            st.error(f"Erro: {e}")

# Exibe o player se o arquivo existir e for válido
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("Visualização Online:")
    try:
        # Abre o arquivo em modo binário de leitura para o Streamlit processar com segurança
        with open(SAVE_PATH, "rb") as video_file:
            st.video(video_file)
    except Exception as e:
        st.error(f"Erro ao renderizar o player de vídeo: {e}")

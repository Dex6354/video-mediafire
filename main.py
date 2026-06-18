import os
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="MediaFire Video Player", page_icon="🎬")
st.title("🎬 Player de Vídeo - MediaFire (Suporte a Arquivos Grandes)")

VIDEO_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"
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
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado.")

    direct_link = download_button.get("href")

    # 2. Baixa o vídeo em blocos direto para o disco (sem carregar na RAM)
    video_response = requests.get(direct_link, headers=headers, stream=True)
    
    if "text/html" in video_response.headers.get("Content-Type", ""):
        raise Exception("O MediaFire bloqueou o download automático deste arquivo.")

    # Salva em blocos de 4MB para manter o uso de RAM baixo
    with open(output_path, "wb") as f:
        for chunk in video_response.iter_content(chunk_size=4096 * 1024):
            if chunk:
                f.write(chunk)

# Botão para iniciar o download
if st.button("Baixar e Carregar Vídeo"):
    with st.spinner("Baixando o vídeo para o servidor... Como o arquivo é grande, isso vai levar um tempo."):
        try:
            if os.path.exists(SAVE_PATH):
                os.remove(SAVE_PATH)
                
            download_mediafire_video(VIDEO_URL, SAVE_PATH)
            st.success("Download concluído com sucesso no servidor!")
            st.rerun() 
        except Exception as e:
            st.error(f"Erro: {e}")

# EXIBIÇÃO CORRIGIDA: Passa a string do caminho. O Streamlit faz o streaming direto do HD.
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("Visualização Online:")
    try:
        # Passando apenas o caminho (SAVE_PATH) em vez de abrir o arquivo evita o estouro de RAM
        st.video(SAVE_PATH)
    except Exception as e:
        st.error(f"Erro ao renderizar o player de vídeo: {e}")

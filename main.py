import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire Local Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Local para Arquivos Grandes (6 GB+)")

# Arquivo temporário salvo no seu HD (RAM estática próxima a 0MB)
SAVE_PATH = "video_local_cache.mp4"

VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file"

def get_mediafire_direct_link(url):
    """Extrai a URL direta de download do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")
    if download_button:
        return download_button.get("href")
    raise Exception("Não foi possível encontrar o botão de download.")

def download_video_em_pedacos(url, save_path):
    """Baixa o arquivo escrevendo direto no HD em blocos de 1MB (RAM sob controle)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    # stream=True impede que o Python jogue o arquivo de 6GB na memória RAM
    with requests.get(url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        
        progresso_barra = st.progress(0)
        status_texto = st.empty()
        bytes_baixados = 0
        
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024): # 1 MB por vez
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    if total_size > 0:
                        percentual = min(int((bytes_baixados / total_size) * 100), 100)
                        progresso_barra.progress(percentual / 100)
                        status_texto.text(f"📥 Baixando para o HD: {bytes_baixados // (1024*1024)} MB / {total_size // (1024*1024)} MB")
        
        progresso_barra.empty()
        status_texto.empty()

# Layout do App
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Baixar Vídeo 1 (5MB)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            with st.spinner("Buscando link..."):
                link = get_mediafire_direct_link(VIDEO_1_URL)
            download_video_em_pedacos(link, SAVE_PATH)
            st.success("Vídeo 1 pronto para reprodução!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

with col2:
    if st.button("📥 Baixar Vídeo 2 (6GB)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            with st.spinner("Buscando link..."):
                link = get_mediafire_direct_link(VIDEO_2_URL)
            download_video_em_pedacos(link, SAVE_PATH)
            st.success("Vídeo de 6GB armazenado no HD com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# Renderização do Player de Vídeo
if os.path.exists(SAVE_PATH):
    st.markdown("---")
    st.subheader("🎬 Player Local Inabalável")
    st.caption("O servidor lê o arquivo do HD por demanda. Avançar o vídeo funciona sem carregar tudo na RAM.")
    
    # Passando a string do caminho do arquivo, o Streamlit ativa 
    # nativamente o suporte a Range Requests (Streaming local por partes)
    st.video(SAVE_PATH)
    
    if st.button("🗑️ Limpar Cache / Deletar Vídeo do HD"):
        os.remove(SAVE_PATH)
        st.rerun()

import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 6GB Player", page_icon="🎬", layout="wide")
st.title("🎬 Player Inabalável para Arquivos Grandes (6 GB+)")

# ==================== CONFIGURAÇÃO ====================
LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

def get_mediafire_direct_link(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")
    
    if not download_button or not download_button.get("href"):
        raise Exception("Não foi possível extrair o link direto do MediaFire.")
    
    return download_button.get("href")

def download_video_with_progress(direct_link, output_path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    video_response = requests.get(direct_link, headers=headers, stream=True)
    
    total_length = video_response.headers.get('content-length')
    progress_bar = st.progress(0)
    status_text = st.empty()

    with open(output_path, "wb") as f:
        if total_length is None:
            f.write(video_response.content)
        else:
            total_length = int(total_length)
            bytes_baixados = 0
            chunk_size = 8 * 1024 * 1024  # 8MB para arquivos grandes

            for chunk in video_response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    gb_baixados = bytes_baixados / (1024 ** 3)
                    gb_totais = total_length / (1024 ** 3)
                    
                    status_text.text(f"Progresso: {porcentagem}% ({gb_baixados:.2f} / {gb_totais:.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)

    progress_bar.progress(1.0)
    status_text.success("✅ Download concluído!")

# ==================== BOTÕES ====================
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Baixar Vídeo 1 (Sample 5MB)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            st.info("Obtendo link...")
            link = get_mediafire_direct_link(VIDEO_1_URL)
            download_video_with_progress(link, SAVE_PATH)
            st.success("✅ Vídeo 1 baixado!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

with col2:
    if st.button("📥 Baixar Vídeo 2 (TEVEO 1 - 6GB)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            st.info("Obtendo link... (pode demorar)")
            link = get_mediafire_direct_link(VIDEO_2_URL)
            download_video_with_progress(link, SAVE_PATH)
            st.success("✅ Vídeo 2 baixado!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# ==================== PLAYER ====================
if os.path.exists(SAVE_PATH):
    file_size_gb = os.path.getsize(SAVE_PATH) / (1024 ** 3)
    st.markdown("---")
    st.subheader(f"🎬 Player Local - {file_size_gb:.2f} GB")
    
    video_url = f"/static/{VIDEO_FILENAME}"
    
    st.markdown(
        f"""
        <div style="background-color: #000; padding: 10px; border-radius: 10px;">
            <video width="100%" height="auto" controls preload="metadata" style="max-height: 85vh;">
                <source src="{video_url}" type="video/mp4">
                Seu navegador não suporta HTML5 video.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.info(f"📁 Arquivo salvo: {SAVE_PATH} ({file_size_gb:.2f} GB)")
    st.caption("💡 Abra o Console do Navegador (F12) se o vídeo não carregar.")

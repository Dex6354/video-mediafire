import os
import requests
import subprocess
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 10-Part Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Otimizado (1 Parte por Vez)")

st.warning("⚠️ **Aviso do Streamlit Cloud:** Esta plataforma possui um limite estrito de ~1 GB de disco. Arquivos de 6 GB vão estourar o limite do container.")

LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

def get_mediafire_direct_link(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")
    if not download_button:
        raise Exception("Link expirado ou inválido.")
    return download_button.get("href")

def download_video_with_progress(direct_link, output_path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
            for chunk in video_response.iter_content(chunk_size=4096 * 1024):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    status_text.text(f"Baixando arquivo bruto: {porcentagem}% ({bytes_baixados / (1024**3):.2f} GB de {total_length / (1024**3):.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)
    progress_bar.empty()
    status_text.empty()

def split_video_into_10_parts(input_path):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path]
        duration = float(subprocess.run(cmd, stdout=subprocess.PIPE, text=True).stdout.strip())
        part_duration = duration / 10
        
        status_split = st.empty()
        for i in range(10):
            status_split.text(f"Cortando Parte {i+1} de 10...")
            output_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i+1}.mp4")
            cmd = ["ffmpeg", "-y", "-ss", str(i * part_duration), "-i", input_path, "-t", str(part_duration), "-c", "copy", output_path]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_split.empty()
    except FileNotFoundError:
        st.error("❌ O FFmpeg não foi encontrado no sistema. Certifique-se de ter adicionado o arquivo 'packages.txt' contendo 'ffmpeg' na raiz do seu repositório GitHub e reinicie o app.")
        st.stop()

parts_filenames = [f"part_{i}.mp4" for i in range(1, 11)]
parts_exist = all(os.path.exists(os.path.join(LOCAL_STATIC_DIR, p)) for p in parts_filenames)

col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Processar Vídeo 1 (Sample)", use_container_width=True):
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        link = get_mediafire_direct_link(VIDEO_1_URL)
        download_video_with_progress(link, SAVE_PATH)
        split_video_into_10_parts(SAVE_PATH)
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        st.rerun()

with col2:
    if st.button("📥 Processar Vídeo 2 (6GB)", use_container_width=True):
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        link = get_mediafire_direct_link(VIDEO_2_URL)
        download_video_with_progress(link, SAVE_PATH)
        split_video_into_10_parts(SAVE_PATH)
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        st.rerun()

if parts_exist:
    st.markdown("---")
    
    parte_selecionada = st.selectbox(
        "Selecione a parte desejada:", 
        options=parts_filenames, 
        format_func=lambda x: f"▶️ Assistir Parte {x.split('_')[1].split('.')[0]}"
    )
    
    st.markdown(
        f"""
        <div style="background-color: black; padding: 5px; border-radius: 8px;">
            <video width="100%" height="auto" controls preload="none" key="{parte_selecionada}">
                <source src="app/static/{parte_selecionada}" type="video/mp4">
                Seu navegador não suporta HTML5 video.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("🗑️ Limpar Cache local"):
        for p in parts_filenames:
            p_path = os.path.join(LOCAL_STATIC_DIR, p)
            if os.path.exists(p_path): os.remove(p_path)
        st.rerun()

import os
import requests
import subprocess
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 10-Part Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Progressivo (Parte por Vez)")

st.warning("⚠️ **Aviso de Armazenamento:** Certifique-se de ter espaço em disco disponível para comportar os fragmentos gerados.")

LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

# Inicializa variáveis de controle de estado do corte progressivo
if "processing" not in st.session_state:
    st.session_state.processing = False
if "current_part" not in st.session_state:
    st.session_state.current_part = 1
if "part_duration" not in st.session_state:
    st.session_state.part_duration = 0.0

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

def get_video_duration(input_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path]
    return float(subprocess.run(cmd, stdout=subprocess.PIPE, text=True).stdout.strip())

# Botões de ação principais
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Processar Vídeo 1 (Sample)", use_container_width=True, disabled=st.session_state.processing):
        for i in range(1, 11):
            p_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i}.mp4")
            if os.path.exists(p_path): os.remove(p_path)
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        
        link = get_mediafire_direct_link(VIDEO_1_URL)
        download_video_with_progress(link, SAVE_PATH)
        duration = get_video_duration(SAVE_PATH)
        
        st.session_state.part_duration = duration / 10
        st.session_state.current_part = 1
        st.session_state.processing = True
        st.rerun()

with col2:
    if st.button("📥 Processar Vídeo 2 (6GB)", use_container_width=True, disabled=st.session_state.processing):
        for i in range(1, 11):
            p_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i}.mp4")
            if os.path.exists(p_path): os.remove(p_path)
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        
        link = get_mediafire_direct_link(VIDEO_2_URL)
        download_video_with_progress(link, SAVE_PATH)
        duration = get_video_duration(SAVE_PATH)
        
        st.session_state.part_duration = duration / 10
        st.session_state.current_part = 1
        st.session_state.processing = True
        st.rerun()

# Lógica de fatiamento sequencial em background
if st.session_state.processing:
    i = st.session_state.current_part
    if i <= 10:
        status_split = st.empty()
        status_split.info(f"⚙️ Cortando e estruturando a Parte {i} de 10... Aguarde.")
        
        start_time = (i - 1) * st.session_state.part_duration
        output_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i}.mp4")
        
        # Parâmetros calibrados para compatibilidade e streaming imediato via navegador
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", SAVE_PATH,
            "-t", str(st.session_state.part_duration),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_split.empty()
        
        # Atualiza o contador e recarrega a página para exibir o novo player gerado
        st.session_state.current_part += 1
        st.rerun()
    else:
        # Fim do processamento: descarta o vídeo bruto de 6GB mantendo apenas as partes leves
        st.session_state.processing = False
        if os.path.exists(SAVE_PATH): 
            os.remove(SAVE_PATH)
        st.success("🎉 Todas as partes prontas!")
        st.rerun()

# Seção de exibição em tempo real
st.markdown("---")
st.subheader("🎬 Reprodutores de Vídeo Disponíveis")

parts_found = False
for i in range(1, 11):
    part_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i}.mp4")
    if os.path.exists(part_path):
        parts_found = True
        # Abre expanders automáticos para organizar a tela sem gargalos de reprodução
        with st.expander(f"▶️ Assistir Fragmento {i}", expanded=(i == st.session_state.current_part - 1)):
            st.video(part_path)

if not parts_found and not st.session_state.processing:
    st.info("Nenhum vídeo carregado no momento. Use as opções acima para iniciar.")

# Botão de descarte
if parts_found and not st.session_state.processing:
    if st.button("🗑️ Deletar todos os arquivos salvos"):
        for i in range(1, 11):
            p_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i}.mp4")
            if os.path.exists(p_path): os.remove(p_path)
        if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
        st.rerun()

import os
import math
import glob
import requests
import subprocess
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire Dynamic Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Dinâmico (Máximo 2GB por Parte)")

st.warning("⚠️ **Aviso de Armazenamento:** Certifique-se de ter espaço em disco disponível para comportar os fragmentos gerados.")

LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

# Inicializa variáveis de controle de estado do corte progressivo dinâmico
if "processing" not in st.session_state:
    st.session_state.processing = False
if "current_part" not in st.session_state:
    st.session_state.current_part = 1
if "num_parts" not in st.session_state:
    st.session_state.num_parts = 1
if "base_duration" not in st.session_state:
    st.session_state.base_duration = 0.0
if "total_duration" not in st.session_state:
    st.session_state.total_duration = 0.0

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

def clear_cache():
    for f in glob.glob(os.path.join(LOCAL_STATIC_DIR, "part_*.mp4")):
        if os.path.exists(f): os.remove(f)
    if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)

# Botões de ação principais
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Processar Vídeo 1 (Sample)", use_container_width=True, disabled=st.session_state.processing):
        clear_cache()
        link = get_mediafire_direct_link(VIDEO_1_URL)
        download_video_with_progress(link, SAVE_PATH)
        
        # Cálculo de partes dinâmicas (Limite de 2GB)
        total_size = os.path.getsize(SAVE_PATH)
        max_part_size = 2 * 1000 * 1000 * 1000  # 2 GB Comercial/Decimal
        st.session_state.num_parts = math.ceil(total_size / max_part_size)
        
        duration = get_video_duration(SAVE_PATH)
        st.session_state.total_duration = duration
        st.session_state.base_duration = (max_part_size / total_size) * duration if total_size > max_part_size else duration
        
        st.session_state.current_part = 1
        st.session_state.processing = True
        st.rerun()

with col2:
    if st.button("📥 Processar Vídeo 2 (6GB)", use_container_width=True, disabled=st.session_state.processing):
        clear_cache()
        link = get_mediafire_direct_link(VIDEO_2_URL)
        download_video_with_progress(link, SAVE_PATH)
        
        # Cálculo de partes dinâmicas (Limite de 2GB)
        total_size = os.path.getsize(SAVE_PATH)
        max_part_size = 2 * 1000 * 1000 * 1000  # 2 GB Comercial/Decimal
        st.session_state.num_parts = math.ceil(total_size / max_part_size)
        
        duration = get_video_duration(SAVE_PATH)
        st.session_state.total_duration = duration
        st.session_state.base_duration = (max_part_size / total_size) * duration if total_size > max_part_size else duration
        
        st.session_state.current_part = 1
        st.session_state.processing = True
        st.rerun()

# Lógica de fatiamento sequencial dinâmico em background
if st.session_state.processing:
    i = st.session_state.current_part
    if i <= st.session_state.num_parts:
        status_split = st.empty()
        status_split.info(f"⚙️ Cortando e estruturando a Parte {i} de {st.session_state.num_parts}... Aguarde.")
        
        start_time = (i - 1) * st.session_state.base_duration
        
        # Se for a última parte, garante pegar o tempo restante exato do arquivo
        if i == st.session_state.num_parts:
            duration_to_cut = st.session_state.total_duration - start_time
        else:
            duration_to_cut = st.session_state.base_duration
            
        output_path = os.path.join(LOCAL_STATIC_DIR, f"part_{i}.mp4")
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", SAVE_PATH,
            "-t", str(duration_to_cut),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_split.empty()
        
        st.session_state.current_part += 1
        st.rerun()
    else:
        st.session_state.processing = False
        if os.path.exists(SAVE_PATH): 
            os.remove(SAVE_PATH)
        st.success("🎉 Todas as partes dinâmicas prontas!")
        st.rerun()

# Seção de exibição isolada (Mapeamento dinâmico da pasta static)
st.markdown("---")
st.subheader("🎬 Visualizador de Partes")

# Varre o diretório para encontrar as partes reais salvas no disco
available_parts = [os.path.basename(f) for f in glob.glob(os.path.join(LOCAL_STATIC_DIR, "part_*.mp4"))]
available_parts.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

if available_parts:
    selected_part = st.selectbox(
        "Selecione qual parte deseja reproduzir:",
        options=available_parts,
        index=len(available_parts) - 1, # Foca no fragmento mais recente gerado
        format_func=lambda x: f"▶️ Assistir Fragmento {x.split('_')[1].split('.')[0]}"
    )
    
    part_path = os.path.join(LOCAL_STATIC_DIR, selected_part)
    st.video(part_path)
    
    if st.session_state.processing:
        st.info(f"🔄 Gerando próximas partes... ({len(available_parts)} de {st.session_state.num_parts} concluídas)")

elif not st.session_state.processing:
    st.info("Nenhum vídeo carregado no momento. Use as opções acima para iniciar.")

# Botão de descarte
if available_parts and not st.session_state.processing:
    if st.button("🗑️ Deletar todos os arquivos salvos"):
        clear_cache()
        st.rerun()

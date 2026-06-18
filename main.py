import os
import requests
import subprocess
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 6GB Split Player", page_icon="🎬", layout="centered")
st.title("🎬 Player com Divisão Automática em 10 Partes")

# Pasta estática local
LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

def get_mediafire_direct_link(url):
    """Extrai a URL direta de download do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")
    if not download_button:
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado.")
    return download_button.get("href")

def download_video_with_progress(direct_link, output_path):
    """Baixa o vídeo completo para o disco em blocos de 4MB."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
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
            chunk_size = 4096 * 1024  

            for chunk in video_response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bytes_baixados += len(chunk)
                    porcentagem = int((bytes_baixados / total_length) * 100)
                    gb_baixados = bytes_baixados / (1024 ** 3)
                    gb_totais = total_length / (1024 ** 3)
                    status_text.text(f"Progresso do Download: {porcentagem}% ({gb_baixados:.2f} GB de {gb_totais:.2f} GB)")
                    progress_bar.progress(bytes_baixados / total_length)
    progress_bar.empty()
    status_text.empty()

def get_video_duration(path):
    """Obtém a duração exata do vídeo usando ffprobe."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return float(result.stdout.strip())

def split_video_into_10_parts(input_path):
    """Divide o vídeo do HD em 10 partes iguais usando ffmpeg stream copy."""
    try:
        duration = get_video_duration(input_path)
        part_duration = duration / 10
        
        status_split = st.empty()
        progress_split = st.progress(0)
        
        for i in range(10):
            status_split.text(f"Cortando e separando: Parte {i+1} de 10...")
            start_time = i * part_duration
            output_filename = f"part_{i+1}.mp4"
            output_path = os.path.join(LOCAL_STATIC_DIR, output_filename)
            
            # Executa corte ultrarrápido sem re-codificar áudio/vídeo
            cmd = [
                "ffmpeg", "-y", "-ss", str(start_time), "-i", input_path, 
                "-t", str(part_duration), "-c", "copy", output_path
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            progress_split.progress((i + 1) / 10)
            
        status_split.empty()
        progress_split.empty()
    except FileNotFoundError:
        st.error("Certifique-se de ter o FFmpeg e FFprobe instalados no seu sistema operacional.")

# Listagem estática dos nomes das partes previstas
parts_filenames = [f"part_{i}.mp4" for i in range(1, 11)]
parts_exist = all(os.path.exists(os.path.join(LOCAL_STATIC_DIR, p)) for p in parts_filenames)

# Botões de controle
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Processar Vídeo 1 (Sample)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            for p in parts_filenames:
                if os.path.exists(os.path.join(LOCAL_STATIC_DIR, p)): os.remove(os.path.join(LOCAL_STATIC_DIR, p))
            
            link = get_mediafire_direct_link(VIDEO_1_URL)
            download_video_with_progress(link, SAVE_PATH)
            split_video_into_10_parts(SAVE_PATH)
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH) # Deleta o arquivo original bruto para liberar espaço
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

with col2:
    if st.button("📥 Processar Vídeo 2 (6GB)", use_container_width=True):
        try:
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH)
            for p in parts_filenames:
                if os.path.exists(os.path.join(LOCAL_STATIC_DIR, p)): os.remove(os.path.join(LOCAL_STATIC_DIR, p))
                
            link = get_mediafire_direct_link(VIDEO_2_URL)
            download_video_with_progress(link, SAVE_PATH)
            split_video_into_10_parts(SAVE_PATH)
            if os.path.exists(SAVE_PATH): os.remove(SAVE_PATH) # Deleta o arquivo original bruto para liberar espaço
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# Renderização do seletor de partes
if parts_exist:
    st.markdown("---")
    st.subheader("🎬 Escolha a parte para assistir no navegador:")
    
    parte_selecionada = st.selectbox(
        "Selecione o fragmento:", 
        options=parts_filenames, 
        format_func=lambda x: f"Parte {x.split('_')[1].split('.')[0]}"
    )
    
    # Renderiza apenas a parte selecionada poupando banda e memória do cliente
    st.markdown(
        f"""
        <div style="background-color: black; padding: 5px; border-radius: 8px;">
            <video width="100%" height="auto" controls preload="metadata" key="{parte_selecionada}">
                <source src="app/static/{parte_selecionada}" type="video/mp4">
                Seu navegador não suporta HTML5 video.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("🗑️ Limpar Cache de Vídeos"):
        for p in parts_filenames:
            p_path = os.path.join(LOCAL_STATIC_DIR, p)
            if os.path.exists(p_path): os.remove(p_path)
        st.rerun()

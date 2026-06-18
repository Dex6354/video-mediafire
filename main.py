import os
import math
import glob
import requests
import subprocess
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire Dynamic Player", page_icon="🎬", layout="centered")
st.title("🎬 Player Dinâmico (Vídeo em Partes de 400MB)")

st.warning("⚠️ **Aviso de Armazenamento:** Certifique-se de ter espaço em disco disponível para comportar os fragmentos gerados.")

LOCAL_STATIC_DIR = "static"
os.makedirs(LOCAL_STATIC_DIR, exist_ok=True)
VIDEO_FILENAME = "video_local_player.mp4"
SAVE_PATH = os.path.join(LOCAL_STATIC_DIR, VIDEO_FILENAME)

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
if "selected_part_index" not in st.session_state:
    st.session_state.selected_part_index = 0

def get_mediafire_direct_link(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")
    if not download_button:
        raise Exception("Link expirado, inválido ou não encontrou o botão de download.")
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
    st.session_state.selected_part_index = 0

# Campo para colar a URL do Mediafire
url_input = st.text_input("Cole a URL do MediaFire aqui:", placeholder="https://www.mediafire.com/file/...", disabled=st.session_state.processing)

# Botão único de processamento
if st.button("📥 Processar Vídeo", use_container_width=True, disabled=st.session_state.processing):
    if not url_input.strip():
        st.error("Por favor, insira uma URL válida do MediaFire.")
    else:
        try:
            clear_cache()
            st.info("Obtendo link direto do MediaFire...")
            link = get_mediafire_direct_link(url_input.strip())
            
            download_video_with_progress(link, SAVE_PATH)
            
            # Limite estrito de 400MB para total estabilidade do streaming
            total_size = os.path.getsize(SAVE_PATH)
            max_part_size = 900 * 1024 * 1024  
            st.session_state.num_parts = math.ceil(total_size / max_part_size)
            
            duration = get_video_duration(SAVE_PATH)
            st.session_state.total_duration = duration
            st.session_state.base_duration = (max_part_size / total_size) * duration if total_size > max_part_size else duration
            
            st.session_state.current_part = 1
            st.session_state.processing = True
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao processar o vídeo: {e}")

# Lógica de fatiamento sequencial dinâmico em background
if st.session_state.processing:
    i = st.session_state.current_part
    if i <= st.session_state.num_parts:
        status_split = st.empty()
        status_split.info(f"⚙️ Cortando e estruturando a Parte {i} de {st.session_state.num_parts}... Aguarde.")
        
        start_time = (i - 1) * st.session_state.base_duration
        
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

# Seção de exibição isolada
st.markdown("---")
st.subheader("🎬 Visualizador de Partes")

available_parts = [os.path.basename(f) for f in glob.glob(os.path.join(LOCAL_STATIC_DIR, "part_*.mp4"))]
available_parts.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

# Injeta CSS para ocultar estruturalmente o botão secreto de navegação do Streamlit
st.markdown("<style>.hidden-btn-container { display: none !important; }</style>", unsafe_allow_html=True)

if available_parts:
    # Ajusta salvaguarda do index do selectbox
    if st.session_state.selected_part_index >= len(available_parts):
        st.session_state.selected_part_index = len(available_parts) - 1

    def on_selectbox_change():
        st.session_state.selected_part_index = available_parts.index(st.session_state.current_selected_part)

    selected_part = st.selectbox(
        "Selecione qual parte deseja reproduzir:",
        options=available_parts,
        key="current_selected_part",
        index=st.session_state.selected_part_index,
        on_change=on_selectbox_change,
        format_func=lambda x: f"▶️ Assistir Fragmento {x.split('_')[1].split('.')[0]}"
    )
    
    current_idx = available_parts.index(selected_part)
    has_next = current_idx < len(available_parts) - 1

    # Criação do botão secreto que o JavaScript irá acionar programaticamente
    st.markdown('<div class="hidden-btn-container">', unsafe_allow_html=True)
    if st.button("SecretNextTrigger", key="go_next_part_action"):
        if has_next:
            st.session_state.selected_part_index = current_idx + 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Renderização do Player Customizado com detecção de fim de mídia e escape de Fullscreen
    part_path = f"static/{selected_part}"
    
    button_html = ""
    if has_next:
        button_html = """
        <button id="next-part-overlay-btn" onclick="triggerStreamlitNext()" style="display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 2147483647; padding: 18px 36px; font-size: 20px; font-weight: bold; background-color: #FF4B4B; color: white; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0px 6px 25px rgba(0,0,0,0.8); font-family: sans-serif; transition: transform 0.2s;">
            ▶️ Assistir Próximo Fragmento
        </button>
        """

    player_code = f"""
    <div id="video-wrapper" style="position: relative; width: 100%; background: #000; border-radius: 8px; overflow: hidden; aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center;">
        <video id="custom-player" style="width: 100%; height: 100%; object-fit: contain;" controls src="{part_path}"></video>
        {button_html}
    </div>

    <script>
        var video = document.getElementById('custom-player');
        var btn = document.getElementById('next-part-overlay-btn');
        
        video.addEventListener('ended', function() {{
            // Força a saída do modo tela cheia nativo do navegador para revelar o botão perfeitamente
            if (document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement) {{
                if (document.exitFullscreen) document.exitFullscreen();
                else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
                else if (document.msExitFullscreen) document.msExitFullscreen();
            }}
            
            // Exibe o botão centralizado por cima do player
            if (btn) {{
                btn.style.display = 'block';
            }}
        }});

        function triggerStreamlitNext() {{
            // Localiza o botão secreto do Streamlit instalado na árvore do DOM principal e clica nele
            var btnStreamlit = window.parent.document.querySelector('.hidden-btn-container button');
            if (btnStreamlit) {{
                btnStreamlit.click();
            }} else {{
                // Fallback de contingência local
                var btnLocal = document.querySelector('.hidden-btn-container button');
                if (btnLocal) btnLocal.click();
            }}
        }}
    </script>
    """
    st.markdown(player_code, unsafe_allow_html=True)
    
    if st.session_state.processing:
        st.info(f"🔄 Gerando próximas partes... ({len(available_parts)} de {st.session_state.num_parts} concluídas)")

elif not st.session_state.processing:
    st.info("Nenhum vídeo carregado no momento. Insira um link acima para iniciar.")

# Botão de descarte
if available_parts and not st.session_state.processing:
    if st.button("🗑️ Deletar todos os arquivos salvos"):
        clear_cache()
        st.rerun()

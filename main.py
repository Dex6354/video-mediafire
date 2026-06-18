import requests
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(page_title="MediaFire 6GB Player", page_icon="🎬", layout="centered")
st.title("🎬 Player MediaFire com Painel de Fallback")

# Links dos vídeos do MediaFire
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file?dkey=8j4nv0uf9vh&r=557"

# Inicialização dos estados do ciclo de vida do player
if "status" not in st.session_state:
    st.session_state.status = "idle"      # Estados: idle, extraindo, pronto, erro
if "direct_link" not in st.session_state:
    st.session_state.direct_link = None
if "video_nome" not in st.session_state:
    st.session_state.video_nome = ""
if "error_msg" not in st.session_state:
    st.session_state.error_msg = ""

def get_mediafire_direct_link(url):
    """Extrai a URL direta de download do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, "html.parser")
        download_button = soup.find("a", id="downloadButton")
        if download_button:
            return download_button.get("href")
        return "Botão de download não encontrado na página do MediaFire."
    except Exception as e:
        return f"Erro de conexão com o servidor: {str(e)}"

# Interface de seleção
col1, col2 = st.columns(2)

with col1:
    if st.button("🎬 Carregar Vídeo 1 (5MB)", use_container_width=True):
        st.session_state.status = "extraindo"
        st.session_state.video_nome = "Vídeo 1 (Sample - 5MB)"
        st.rerun()

with col2:
    if st.button("🎬 Carregar Vídeo 2 (6GB)", use_container_width=True):
        st.session_state.status = "extraindo"
        st.session_state.video_nome = "Vídeo 2 (TEVEO 1 - 6GB)"
        st.rerun()

# Processamento em Segundo Plano (Extração do Link)
if st.session_state.status == "extraindo":
    url_alvo = VIDEO_1_URL if "5MB" in st.session_state.video_nome else VIDEO_2_URL
    
    with st.spinner(f"⏳ Extraindo link direto para {st.session_state.video_nome}..."):
        resultado = get_mediafire_direct_link(url_alvo)
        
        if resultado and resultado.startswith("http"):
            st.session_state.direct_link = resultado
            st.session_state.status = "pronto"
        else:
            st.session_state.error_msg = resultado
            st.session_state.status = "erro"
    st.rerun()

# --- PAINEL VISUAL DE DIAGNÓSTICO E FALLBACK ---
st.markdown("---")
st.subheader("📋 Monitor de Execução do Player:")

if st.session_state.status == "idle":
    st.info("Aguardando comando do usuário. Selecione um vídeo acima para iniciar.")

elif st.session_state.status == "erro":
    st.error(f"❌ Erro Crítico ao processar o arquivo!")
    st.code(st.session_state.error_msg, language="text")
    if st.button("🔄 Tentar Novamente"):
        st.session_state.status = "idle"
        st.rerun()

elif st.session_state.status == "pronto":
    st.success(f"✅ Link de Streaming resolvido para: {st.session_state.video_nome}")
    
    if "6GB" in st.session_state.video_nome:
        st.warning("⚠️ Nota: Vídeos de 6GB podem falhar no player HTML5 web devido a restrições do seu navegador (CORS/Timeout). Caso falhe, use as opções de Fallback abaixo.")

    # Player HTML5 Padrão
    st.markdown(
        f"""
        <div style="background-color: black; padding: 5px; border-radius: 8px;">
            <video width="100%" height="auto" controls preload="metadata">
                <source src="{st.session_state.direct_link}" type="video/mp4">
                Seu navegador rejeitou o streaming direto deste arquivo. Use os fallbacks abaixo.
            </video>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Seção de Recursos de Fallback de segurança
    st.markdown("### 🛠️ Recursos de Fallback (Se o player acima não rodar):")
    
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.markdown(
            f'<a href="{st.session_state.direct_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; padding:12px; background-color:#ff4b4b; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">'
            f'📥 Opção 1: Forçar Download Direto</button></a>', 
            unsafe_allow_html=True
        )
        st.caption("Baixa o arquivo em velocidade máxima diretamente pelo navegador bypassando o player.")
        
    with f_col2:
        st.code(st.session_state.direct_link, language="text")
        st.caption("💡 **Opção 2 (Recomendada para 6GB):** Copie o link acima, abra o player **VLC**, vá em *Mídia > Abrir Fluxo de Rede*, cole o link e assista instantaneamente sem gastar memória do navegador.")

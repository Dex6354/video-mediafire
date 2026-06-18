import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

st.set_page_config(page_title="MediaFire Stream", page_icon="🎬")
st.title("🎬 Player de Streaming Direto (Sem Download no Servidor)")

VIDEO_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file?dkey=rqr7hg9tif0&r=1741"

def get_mediafire_direct_link(url):
    """Extrai a URL final do arquivo de vídeo do MediaFire."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    download_button = soup.find("a", id="downloadButton")

    if not download_button:
        raise Exception("Não foi possível encontrar o botão de download. O link pode ter expirado.")

    return download_button.get("href")

# Botão para ativar o player
if st.button("Carregar Vídeo via Stream"):
    with st.spinner("Iniciando conexão direta com o MediaFire..."):
        try:
            direct_link = get_mediafire_direct_link(VIDEO_URL)
            st.session_state["stream_link"] = direct_link
            st.success("Player carregado!")
        except Exception as e:
            st.error(f"Erro ao obter link: {e}")

# Exibe o novo player caso o link tenha sido gerado
if "stream_link" in st.session_state:
    st.markdown("---")
    st.subheader("Visualização Online (Streaming do Navegador):")
    
    # Player HTML5 Puro: força o seu navegador a ler o link sem passar pelo servidor do Streamlit
    video_html = f"""
    <div style="background-color: black; display: flex; justify-content: center; align-items: center; height: 100%;">
        <video width="100%" height="auto" controls preload="metadata" style="max-height: 450px;">
            <source src="{st.session_state['stream_link']}" type="video/mp4">
            Seu navegador não suporta a reprodução deste arquivo ou o link direto expirou.
        </video>
    </div>
    """
    # Renderiza o player em uma camada HTML independente
    components.html(video_html, height=480)

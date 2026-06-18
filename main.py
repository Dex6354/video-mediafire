import streamlit as st

st.set_page_config(page_title="Stream Cloud Player 6GB+", page_icon="🎬", layout="centered")
st.title("🎬 Player de Alta Capacidade (6GB+ Cloud)")

st.markdown("""
### 💡 Como configurar os links para funcionar na nuvem:
* **Dropbox:** Altere o final do link de `?dl=0` para `?raw=1`
* **Google Drive:** Use o formato de incorporação (Embed) fornecido pelo Drive.
""")

# --- CONFIGURAÇÃO DOS LINKS TIPO STREAMING ---
# Substitua os links abaixo pelos seus arquivos convertidos para streaming
DROPBOX_SAMPLE = "https://www.dropbox.com/scl/fi/yx8example/sample.mp4?raw=1" 
GOOGLE_DRIVE_EMBED = "https://drive.google.com/file/d/1_example_id/preview"

# Links de teste/exemplo que aceitam streaming direto no navegador:
VIDEO_1_STREAM = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" # Link direto público (Teste 5MB)
VIDEO_2_STREAM = "SUA_URL_DO_DROPBOX_AQUI?raw=1" # Substitua aqui para o seu de 6GB

# Estado da sessão
if "video_url" not in st.session_state:
    st.session_state.video_url = None
if "player_type" not in st.session_state:
    st.session_state.player_type = "html5"

col1, col2 = st.columns(2)

with col1:
    if st.button("📺 Carregar Vídeo de Teste (Link Direto)", use_container_width=True):
        st.session_state.video_url = VIDEO_1_STREAM
        st.session_state.player_type = "html5"
        st.rerun()

with col2:
    if st.button("🎬 Carregar Seu Vídeo Grande (6GB+)", use_container_width=True):
        # Se for usar Google Drive Embed, mude player_type para "iframe"
        st.session_state.video_url = VIDEO_2_STREAM 
        st.session_state.player_type = "html5" 
        st.rerun()

# --- RENDERIZAÇÃO DOS PLAYERS COOPERAÇÃO TOTAL CLIENT-SIDE ---
if st.session_state.video_url:
    st.markdown("---")
    
    if st.session_state.video_url == "SUA_URL_DO_DROPBOX_AQUI?raw=1":
        st.warning("⚠️ Substitua o link de teste no código pela URL gerada no seu Dropbox (com `?raw=1` no final).")

    if st.session_state.player_type == "html5":
        st.subheader("Player HTML5 Nativo (Aceleração por Hardware)")
        # Este player força o navegador do usuário a puxar o arquivo por demanda
        # Consumo no Streamlit Cloud: 0MB de RAM.
        st.markdown(
            f"""
            <div style="background-color: black; padding: 5px; border-radius: 8px;">
                <video width="100%" height="450" controls preload="metadata">
                    <source src="{st.session_state.video_url}" type="video/mp4">
                    Seu navegador não suporta a reprodução direta deste formato.
                </video>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    elif st.session_state.player_type == "iframe":
        st.subheader("Player via Iframe Dedicado (Google Drive / OneDrive)")
        st.components.v1.iframe(st.session_state.video_url, height=450, scrolling=False)

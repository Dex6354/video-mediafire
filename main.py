import streamlit as st

st.set_page_config(page_title="MediaFire Player Nuvem", page_icon="🎬", layout="centered")
st.title("🎬 Player Web MediaFire Sem Download Local")

# Links originais públicos do MediaFire
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file"

st.markdown("---")
st.subheader("Selecione o vídeo para assistir direto no navegador:")

video_opcao = st.radio(
    "Escolha o arquivo:",
    ("Vídeo 1 (Sample - 5MB)", "Vídeo 2 (TEVEO 1 - 6GB)")
)

url_selecionada = VIDEO_1_URL if "5MB" in video_opcao else VIDEO_2_URL

# Injeta um player sandboxed onde o processamento do link e do streaming 
# acontece integralmente no lado do cliente (navegador do usuário).
# Consumo no Streamlit Cloud: 0% de RAM e 0% de Disco.
st.components.v1.html(
    f"""
    <div style="background-color: #111; padding: 20px; border-radius: 8px; text-align: center; font-family: sans-serif; color: white;">
        <h4 style="margin-top: 0;">Carregando Engine de Streaming do Cliente...</h4>
        <p style="font-size: 13px; color: #aaa;">O navegador vai ler o arquivo de 6GB por demanda direto do MediaFire.</p>
        
        <div id="player-container" style="margin-top: 15px;">
            <video id="videoPlayer" width="100%" height="360" controls preload="metadata" style="border-radius: 4px; background: black;">
                <source src="" type="video/mp4">
                Seu navegador não suporta streaming direto.
            </video>
        </div>
        
        <div style="margin-top: 15px;">
            <a href="{url_selecionada}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 14px;">
                🔗 Abrir na Aba Nativa do Navegador (Fallback)
            </a>
        </div>
    </div>

    <script>
        // Executado no contexto do usuário (contorna o bloqueio de IP do servidor)
        async function resolverEPlay() {{
            const videoUrl = "{url_selecionada}";
            const player = document.getElementById('videoPlayer');
            
            try {{
                // Faz a requisição simulando o navegador para pegar o downloadButton
                const response = await fetch('https://api.allorigins.win/get?url=' + encodeURIComponent(videoUrl));
                const data = await response.json();
                
                const parser = new DOMParser();
                const doc = parser.parseFromString(data.contents, 'text/html');
                const downloadBtn = doc.querySelector('#downloadButton');
                
                if (downloadBtn) {{
                    const directLink = downloadBtn.getAttribute('href');
                    player.src = directLink;
                    player.load();
                }} else {{
                    console.log("Link direto não encontrado na árvore DOM.");
                }}
            }} catch (e) {{
                console.error("Erro na resolução client-side:", e);
            }}
        }}
        
        // Inicializa a tentativa de bypass assim que o componente renderiza
        resolverEPlay();
    </script>
    """,
    height=520
)

st.info("💡 **Nota:** Arquivos de 6GB exigem uma conexão estável. Se o player integrado travar por restrições de segurança do MediaFire na sua rede, clique no botão azul para assistir na aba nativa do navegador.")

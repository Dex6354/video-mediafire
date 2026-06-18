import streamlit as st

st.set_page_config(page_title="MediaFire 6GB Player", page_icon="🎬", layout="centered")

st.title("🎬 Player Web para Arquivos Grandes (6 GB+)")
st.markdown("---")

# Links compartilhados do MediaFire (Página pública)
VIDEO_1_URL = "https://www.mediafire.com/file/pjkzoqvjnksr5bz/sample-5s.mp4/file"
VIDEO_2_URL = "https://www.mediafire.com/file/0ti5y6lprtk5pa5/TEVEO_1.mp4/file"

st.subheader("Escolha o método de reprodução em nuvem:")

tab1, tab2, tab3 = st.tabs([
    "🌐 Método 1: Iframe Embutido", 
    "🚀 Método 2: Engine do Navegador",
    "⚡ Método 3: Proxy Cloudflare (Custom Player)"
])

with tab1:
    st.markdown("""
    Injeta a interface de exibição do MediaFire diretamente na página. 
    O próprio MediaFire gerencia o streaming do arquivo de 6GB sem tocar no servidor do Streamlit.
    """)
    
    video_sel = st.radio("Selecione o vídeo para carregar no Iframe:", ("Vídeo 1 (5MB)", "Vídeo 2 (6GB)"), key="iframe_select")
    url_alvo = VIDEO_1_URL if "5MB" in video_sel else VIDEO_2_URL
    
    # Renderiza o visualizador nativo deles isolado no DOM do cliente
    st.components.v1.iframe(url_alvo, height=600, scrolling=True)

with tab2:
    st.markdown("""
    Delega a reprodução para a Engine nativa do seu navegador em uma nova aba. 
    Ideal para arquivos gigantes, pois utiliza a aceleração de hardware do seu próprio PC.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📺 Abrir Vídeo 1 (Navegador)", VIDEO_1_URL, use_container_width=True)
    with col2:
        st.link_button("📺 Abrir Vídeo 2 (6GB - Navegador)", VIDEO_2_URL, use_container_width=True)

with tab3:
    st.markdown("""
    Se você precisar obrigatoriamente do player `<video>` padrão limpo na tela, a única forma em nuvem é usar um **Worker do Cloudflare** como proxy de stream para contornar o bloqueio de IP do MediaFire.
    """)
    
    st.info("💡 **Como fazer:** Publique um Worker simples com o código abaixo e passe o link gerado pelo script scraper para ele. Ele fará o bypass de CORS e o chunking em tempo real.")
    
    st.code("""
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get("url");
    if (!targetUrl) return new Response("URL ausente", { status: 400 });

    const response = await fetch(targetUrl, { headers: request.headers });
    const newResponse = new Response(response.body, response);
    newResponse.headers.set("Access-Control-Allow-Origin", "*");
    return newResponse;
  }
};
    """, language="javascript")

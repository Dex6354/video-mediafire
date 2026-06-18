import streamlit as st
import time
import requests

st.title("Teste de Velocidade de Internet")

if st.button("Iniciar Teste"):
    # URL de um arquivo de teste pequeno (aprox. 5MB)
    url = "https://speed.hetzner.de/10MB.bin"
    
    try:
        st.write("Baixando arquivo de teste...")
        start_time = time.time()
        
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        # Lê o conteúdo para simular o download
        for chunk in response.iter_content(chunk_size=1024):
            pass
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Cálculo: (tamanho em bits) / (tempo em segundos) / 1 milhão para Mbps
        speed_mbps = (total_size * 8) / (duration * 1_000_000)
        
        st.success(f"Velocidade estimada: **{speed_mbps:.2f} Mbps**")
        
    except Exception as e:
        st.error(f"Erro no teste: {e}")

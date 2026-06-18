import streamlit as st
import time
import requests

st.title("Teste de Velocidade de Internet")

if st.button("Iniciar Teste"):
    # Usando o endpoint estável da Cloudflare (aprox. 5MB)
    url = "https://speed.cloudflare.com/__down?bytes=5000000"
    
    try:
        st.write("Baixando arquivo de teste da Cloudflare...")
        start_time = time.time()
        
        # Define um timeout de 15 segundos para evitar travamentos
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        
        total_size = 0
        for chunk in response.iter_content(chunk_size=8192):
            total_size += len(chunk)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Cálculo: (bits baixados) / tempo / 1.000.000 = Mbps
        speed_mbps = (total_size * 8) / (duration * 1_000_000)
        
        st.success(f"Velocidade estimada: **{speed_mbps:.2f} Mbps**")
        st.caption(f"Baixados {total_size / (1024*1024):.2f} MB em {duration:.2f} segundos.")
        
    except requests.exceptions.ConnectionError:
        st.error("Erro de conexão: A máquina virtual do Streamlit não conseguiu acessar o servidor. Se estiver usando o Streamlit Community Cloud, a plataforma pode estar bloqueando saídas de rede pesadas.")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")

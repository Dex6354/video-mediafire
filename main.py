import streamlit as st
import time

st.title("Monitor de Performance da VM")

if st.button("Testar Velocidade"):
    # Mede tempo para operações básicas
    start_time = time.time()
    
    # Realiza um cálculo simples
    x = 0
    for i in range(1000000):
        x += i
    
    end_time = time.time()
    duration = end_time - start_time
    
    st.write(f"Tempo para 1 milhão de somas: **{duration:.4f} segundos**")
    st.info("Este valor reflete a carga atual do servidor do Streamlit.")

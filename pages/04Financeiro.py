import streamlit as st
import pandas as pd

# Inicializa o estado da página
if "page" not in st.session_state:
    st.session_state.page = "home"

# Cabeçalho
st.title("Sistema Financeiro")
col1, col2  = st.columns(2)

# Botões principais
with col1:
    if st.button("Contas a pagar", use_container_width=True, key="contas_a_pag_button"):
        st.session_state.page = "contas_a_pag"

if st.session_state.page == "home":
    st.info("Bem-vindo ao sistema financeiro! Clique no botão acima.")

elif st.session_state.page == "contas_a_pag":

    col1, col2, col3, col4, col5 = st.columns([1,1,2,2,2])
    
    with col1:
        if st.button("←", use_container_width=True, key="left_button"):
            if st.session_state.indice_produto > 0:
                st.session_state.indice_produto -= 1

    with col2:
        if st.button("→", use_container_width=True, key="right_button"):
            if st.session_state.indice_produto < len(listar_produtos()) - 1:
                st.session_state.indice_produto += 1

    with col3:
        if st.button('Incluir', use_container_width=True, key="incluir_button"):
            st.session_state.page = 'incluir'

    with col4:
        if st.button('Pesquisar', use_container_width=True, key="pesquisar_button"):
            st.session_state.page = 'pesq'
            st.rerun()

    with col5:
        if st.button('Listagem', use_container_width=True, key="listagem_button"):
            st.session_state.page = 'list'
            st.rerun()




    with st.form("form_contas_a_pagar"):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código")
            nome = st.text_input("Nome")
            data_entrada = st.date_input("Data de Entrada")
            vencimento = st.date_input("Vencimento")
        with col2:
            num_documento = st.text_input("Número do Documento")
            origem = st.text_input("Origem")
            parcela = st.number_input("Parcela", min_value=1, step=1)
            valor = st.number_input("Valor", min_value=0.0, step=0.01, format="%.2f")

        # Criando uma nova linha para a observação
        col_obs, _ = st.columns([3, 1])  # Ajustando proporção para alinhar à esquerda
        with col_obs:
            observacao = st.text_area("Observação")
        submitted = st.form_submit_button("Quitar conta")
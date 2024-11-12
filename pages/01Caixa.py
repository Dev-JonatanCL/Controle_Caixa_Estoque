import streamlit as st
from datetime import datetime
from Banco import criar_banco_de_dados, adicionar_orcamento, obter_orcamentos, obter_orcamento_por_id

def exibir_data_atual():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"<h1 style='text-align: center;'>{data_atual}</h1>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button('Aber/Fech', use_container_width=True):
        st.session_state.page = 'Ab/Fc'

with col2:
    if st.button('Efetuar Venda', use_container_width=True):
        st.session_state.page = 'Venda'

with col3:
    if st.button('Orçamentos', use_container_width=True):
        st.session_state.page = 'Orc'

with col4:
    if st.button('Listagem de Vendas', use_container_width=True):
        st.session_state.page = 'ListV'

if 'page' not in st.session_state:
    st.session_state.page = 'Ab/Fc'

if st.session_state.page == 'Ab/Fc':
    exibir_data_atual()
    st.write("\n\n")
    col1, col2 = st.columns([1, 1])

    with col1:
        valor_digitado = st.number_input("Digite o valor em caixa", min_value=0.0, format="%.2f")

    with col2:
        valor_troco = st.number_input("Digite o valor do troco guardado", min_value=0.0, format="%.2f")

    if st.button('Abrir Caixa'):
        st.write(f"Valor digitado: R${valor_digitado:.2f}")
        st.write(f"Valor do troco guardado: R${valor_troco:.2f}")

elif st.session_state.page == 'Venda':
    st.subheader("Sobre o Projeto")
    st.write("Aqui você pode colocar informações sobre o projeto.")
    
elif st.session_state.page == 'Orc':
    st.subheader("Orçamentos")
    st.write("Exibir orçamentos")
elif st.session_state.page == 'ListV':
    st.subheader("Listagem de Vendas")
    st.write("Exibir Listagem de Vendas")
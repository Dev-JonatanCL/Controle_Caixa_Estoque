import streamlit as st
from streamlit_option_menu import option_menu
import importlib  # Para importar os módulos dinamicamente

# Dicionário com as páginas e os respectivos módulos
pages = {
    "Caixa": "Caixa",
    "Estoque": "Estoque",
    "Cadastro": "Cadastro",
    "Financeiro": "Financeiro",
    "Dashboard": "Dashboard"
}

# Menu vertical na barra lateral
with st.sidebar:
    selected_page = option_menu(
        menu_title="Selecione uma página",  # Título do menu
        options=list(pages.keys()),        # Opções disponíveis no menu
        icons=["house", "box", "person", "credit-card", "bar-chart"],  # Ícones para cada opção
        menu_icon="cast",                  # Ícone principal do menu
        default_index=0                    # Página inicial selecionada
    )

module_name = pages[selected_page]
module = importlib.import_module(module_name)
module.run()

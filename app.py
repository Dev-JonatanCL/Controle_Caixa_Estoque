import streamlit as st
from streamlit_option_menu import option_menu
import importlib

pages = {
    "Caixa": "Caixa",
    "Estoque": "Estoque",
    "Cadastro": "Cadastro",
    "Financeiro": "Financeiro",
    "Dashboard": "Dashboard"
}

with st.sidebar:
    pagina_selecionada = option_menu(
        menu_title="Selecione uma página",
        options=list(pages.keys()),
        icons=["house", "box", "person", "credit-card", "bar-chart"],
        menu_icon="cast",
        default_index=0
    )

module_name = pages[pagina_selecionada]
module = importlib.import_module(module_name)
module.run()

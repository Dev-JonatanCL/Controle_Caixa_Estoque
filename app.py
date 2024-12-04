import streamlit as st
from streamlit_option_menu import option_menu
import importlib

background_image_url = "https://img.freepik.com/vetores-gratis/fundo-branco-com-hexagono-de-tecnologia-azul_1017-19366.jpg"

st.markdown(f"""
    <style>
        .st-emotion-cache-1r4qj8v {{
            background-image: url('{background_image_url}');
            background-size: cover;
        }}
        .stMainBlockContainer {{
            background-color: #cccccc;
        }}
        .st-emotion-cache-6qob1r {{
            background-color: white;
        }}
    </style>
""", unsafe_allow_html=True)

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
        icons=["cart4", "box", "person", "coin", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        styles={
            "menu-title": {"color": "#000", "font-size": "25px", "font-weight": "bold"},
            "container": {"padding": "5px", "background-color": "#cccccc", "height": "465px"},
            "icon": {"color": "blue", "font-size": "30px"},
            "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px", "padding": "10px", "color": "#000"},
            "nav-link-selected": {"background-color": "white", "color": "#000"},
        }
    )

module_name = pages[pagina_selecionada]
module = importlib.import_module(module_name)
module.run()

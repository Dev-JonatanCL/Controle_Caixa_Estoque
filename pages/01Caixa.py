import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import random

# Função para exibir a data no canto superior esquerdo
def exibir_data_atual():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"<h1 style='text-align: left;'>{data_atual}</h1>", unsafe_allow_html=True)

# Função para buscar produto no banco de dados
def buscar_produto(codigo_descricao):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM produtos 
        WHERE cod = ? OR descricao LIKE ?
    ''', (codigo_descricao, f'%{codigo_descricao}%'))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

# Função para gerar números de orçamento
def gerar_numero_orcamento():
    return f"ORC-{random.randint(1000, 9999)}"

# Integrar a funcionalidade de Orçamentos ao código original
def tela_orcamentos():
    exibir_data_atual()
    st.write("### Tela de Orçamentos")
    
    # Inicializar estados para o orçamento
    if "orcamento_produtos" not in st.session_state:
        st.session_state.orcamento_produtos = []
    if "numero_orcamento" not in st.session_state:
        st.session_state.numero_orcamento = gerar_numero_orcamento()
    if "data_orcamento" not in st.session_state:
        st.session_state.data_orcamento = datetime.now().strftime("%d/%m/%Y")
    if "observacao_orcamento" not in st.session_state:
        st.session_state.observacao_orcamento = ""
    
    # Inputs para buscar e adicionar produtos ao orçamento
    with st.form("form_adicionar_produto_orcamento"):
        codigo_descricao = st.text_input("Buscar produto por código ou descrição")
        quantidade = st.number_input("Quantidade desejada", min_value=1, value=1)
        percentual_ajuste = st.number_input("Desconto/Acréscimo (%)", min_value=-100.0, value=0.0, step=0.1)
        submit_buscar = st.form_submit_button("Adicionar Produto")
        
        if submit_buscar:
            produtos = buscar_produto(codigo_descricao)
            if produtos:
                produto_selecionado = produtos[0]
                preco_original = produto_selecionado[-1]
                preco_ajustado = preco_original * (1 + percentual_ajuste / 100)
                st.session_state.orcamento_produtos.append({
                    "codigo": produto_selecionado[1],
                    "descricao": produto_selecionado[2],
                    "quantidade": quantidade,
                    "preco_unitario": preco_original,
                    "percentual_ajuste": percentual_ajuste,
                    "preco_ajustado": preco_ajustado,
                    "total_item": quantidade * preco_ajustado
                })
                st.success("Produto adicionado ao orçamento com sucesso!")
            else:
                st.warning("Produto não encontrado.")

    # Exibir os produtos adicionados ao orçamento e o total
    if st.session_state.orcamento_produtos:
        
        st.write("### Produtos no Orçamento")
        df_orcamento = pd.DataFrame(st.session_state.orcamento_produtos)
        total_orcamento = df_orcamento["total_item"].sum()

        st.table(df_orcamento[["codigo", "descricao", "quantidade", "preco_unitario", "percentual_ajuste", "preco_ajustado", "total_item"]])
        st.write(f"*Total do Orçamento: R${total_orcamento:.2f}*")

    # Dados do cliente e observações
    with st.form("form_dados_orcamento"):
        st.write(f"*Número do Orçamento:* {st.session_state.numero_orcamento}")
        st.write(f"*Data do Orçamento:* {st.session_state.data_orcamento}")
        codigo_cliente = st.text_input("Código do Cliente")
        nome_cliente = st.text_input("Nome do Cliente")
        st.session_state.observacao_orcamento = st.text_area("Observações", value=st.session_state.observacao_orcamento)
        submit_orcamento = st.form_submit_button("Finalizar Orçamento")
        
        if submit_orcamento:
            if st.session_state.orcamento_produtos:
                st.success("Orçamento finalizado com sucesso!")
                st.write(f"*Número do Orçamento:* {st.session_state.numero_orcamento}")
                st.write(f"*Data do Orçamento:* {st.session_state.data_orcamento}")
                st.write(f"*Total do Orçamento:* R${total_orcamento:.2f}")
                st.write(f"*Cliente:* {nome_cliente} (Código: {codigo_cliente})")
                st.write(f"*Observações:* {st.session_state.observacao_orcamento}")

                # Resetar estados após finalizar o orçamento
                st.session_state.orcamento_produtos = []
                st.session_state.numero_orcamento = gerar_numero_orcamento()
                st.session_state.data_orcamento = datetime.now().strftime("%d/%m/%Y")
                st.session_state.observacao_orcamento = ""
            else:
                st.warning("Nenhum produto adicionado ao orçamento.")

# Alterar o cabeçalho para incluir "Orçamentos"
def mostrar_cabecalho():
    st.markdown("""
        <style>
        .navbar {
            background-color: #f0f0f5;
            padding: 10px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 100;
            box-shadow: 0 4px 2px -2px gray;
        }
        .navbar button {
            margin: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Voltar ao Menu", use_container_width=True):
            st.session_state.page = "Menu"
    with col2:
        if st.button("Abertura / Fechamento", use_container_width=True):
            st.session_state.page = "Ab/Fc"
    with col3:
        if st.button("Efetuar Venda", use_container_width=True):
            st.session_state.page = "Venda"
    with col4:
        if st.button("Orçamentos", use_container_width=True):
            st.session_state.page = "Orc"
    with col5:
        if st.button("Listagem de Vendas", use_container_width=True):
            st.session_state.page = "ListV"



# Função para tela de efetuar venda
def tela_efetuar_venda():
    exibir_data_atual()
    st.write("### Tela para Efetuar Venda")
    
    # Armazenar os produtos adicionados
    if "produtos_venda" not in st.session_state:
        st.session_state.produtos_venda = []
    if "valor_frete" not in st.session_state:
        st.session_state.valor_frete = 0.0
    if "valor_final" not in st.session_state:
        st.session_state.valor_final = 0.0
    
    # Inputs para buscar e adicionar produtos
    with st.form("form_adicionar_produto"):
        codigo_descricao = st.text_input("Buscar produto por código ou descrição")
        quantidade = st.number_input("Quantidade desejada", min_value=1, value=1)
        percentual_ajuste = st.number_input("Desconto/Acréscimo (%)", min_value=-100.0, value=0.0, step=0.1)
        submit_buscar = st.form_submit_button("Adicionar Produto")
        
        if submit_buscar:
            produtos = buscar_produto(codigo_descricao)
            if produtos:
                produto_selecionado = produtos[0]
                if quantidade <= produto_selecionado[6]:
                    preco_original = produto_selecionado[-1]
                    preco_ajustado = preco_original * (1 + percentual_ajuste / 100)
                    st.session_state.produtos_venda.append({
                        "codigo": produto_selecionado[1],
                        "descricao": produto_selecionado[2],
                        "quantidade": quantidade,
                        "preco_unitario": preco_original,
                        "percentual_ajuste": percentual_ajuste,
                        "preco_ajustado": preco_ajustado,
                        "total_item": quantidade * preco_ajustado
                    })
                    st.success("Produto adicionado com sucesso!")
                else:
                    st.error("Quantidade maior do que disponível em estoque.")
            else:
                st.warning("Produto não encontrado.")

    # Exibir produtos adicionados e calcular o total
    if st.session_state.produtos_venda:
        st.write("### Produtos na Venda")
        df_produtos = pd.DataFrame(st.session_state.produtos_venda)
        total_produtos = df_produtos["total_item"].sum()

        # Adicionar campo para frete
        st.session_state.valor_frete = st.number_input("Valor do Frete", min_value=0.0, value=st.session_state.valor_frete, format="%.2f")
        st.session_state.valor_final = total_produtos + st.session_state.valor_frete

        st.table(df_produtos[["codigo", "descricao", "quantidade", "preco_unitario", "percentual_ajuste", "preco_ajustado", "total_item"]])
        st.write(f"Total dos Produtos: R${total_produtos:.2f}")
        st.write(f"Valor do Frete: R${st.session_state.valor_frete:.2f}")

        # Campo para ajustar o valor final manualmente
        st.session_state.valor_final = st.number_input("Valor Final da Compra", min_value=0.0, value=st.session_state.valor_final, format="%.2f")
        st.write(f"Valor Final Ajustado: R${st.session_state.valor_final:.2f}")
    
    # Inputs adicionais para a venda
    with st.form("form_dados_cliente"):
        codigo_cliente = st.text_input("Código do Cliente")
        nome_cliente = st.text_input("Nome do Cliente")
        metodo_pagamento = st.selectbox("Método de Pagamento", ["À Vista", "Crédito", "Débito"])
        submit_venda = st.form_submit_button("Finalizar Compra")
        
        if submit_venda:
            if st.session_state.produtos_venda:
                st.success(f"Compra finalizada com sucesso! Valor total: R${st.session_state.valor_final:.2f}")
                # Resetar os estados após finalizar a compra
                st.session_state.produtos_venda = []
                st.session_state.valor_frete = 0.0
                st.session_state.valor_final = 0.0
            else:
                st.warning("Nenhum produto adicionado à venda.")


# Função para a tela de abertura de caixa
def tela_abertura_caixa():
    exibir_data_atual()
    valor_digitado = st.number_input("Digite o valor em caixa", min_value=0.0, format="%.2f")
    valor_troco = st.number_input("Digite o valor do troco guardado", min_value=0.0, format="%.2f")
    if st.button('Abrir Caixa', use_container_width=True):
        st.session_state.page = 'FecharCaixa'
        st.session_state.valor_digitado = valor_digitado
        st.session_state.valor_troco = valor_troco
        st.session_state.sangria = 0.0

# Função para a tela de fechamento de caixa
def tela_fechamento_caixa():
    exibir_data_atual()
    col1, col2, col3 = st.columns(3)
    with col1:
        sangria = st.number_input("Efetuar Sangria", min_value=0.0, format="%.2f")
        if st.button('Efetuar Sangria', use_container_width=True):
            st.session_state.sangria += sangria
            st.write(f"Sangria realizada: R${sangria:.2f}")
    with col2:
        adicionar_troco = st.number_input("Adicionar Troco", min_value=0.0, format="%.2f")
        if st.button('Adicionar Troco', use_container_width=True):
            st.write(f"Troco adicionado: R${adicionar_troco:.2f}")
    with col3:
        guardar_troco = st.number_input("Guardar Troco", min_value=0.0, format="%.2f")
        if st.button('Guardar Troco', use_container_width=True):
            st.write(f"Troco guardado: R${guardar_troco:.2f}")
    col4, col5 = st.columns(2)
    with col4:
        valor_em_caixa = st.number_input("Digite o valor em caixa", min_value=0.0, format="%.2f")
    with col5:
        valor_do_troco = st.number_input("Digite o valor do troco guardado", min_value=0.0, format="%.2f")
    if valor_em_caixa == 0:
        st.warning("Falta dinheiro no caixa! Deseja finalizar o caixa mesmo assim?", icon="⚠️")
        finalizar = st.button('Sim, finalizar caixa', use_container_width=True)
    else:
        finalizar = st.button('Finalizar Caixa', use_container_width=True)
    if finalizar:
        st.write(f"Fechamento de caixa realizado com os valores abaixo:")
        st.write(f"Valor em caixa: R${valor_em_caixa:.2f}")
        st.write(f"Valor do troco guardado: R${valor_do_troco:.2f}")
        st.write(f"Sangria total realizada: R${st.session_state.sangria:.2f}")
        st.write("Operações de sangria, adicionar troco e guardar troco foram registradas.")

# Função para mostrar os botões no cabeçalho fixo
def mostrar_cabecalho():
    st.markdown("""
        <style>
        .navbar {
            background-color: #f0f0f5;
            padding: 10px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 100;
            box-shadow: 0 4px 2px -2px gray;
        }
        .navbar button {
            margin: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Voltar ao Menu", use_container_width=True):
            st.session_state.page = "Menu"
    with col2:
        if st.button("Abertura / Fechamento", use_container_width=True):
            st.session_state.page = "Ab/Fc"
    with col3:
        if st.button("Efetuar Venda", use_container_width=True):
            st.session_state.page = "Venda"
    with col4:
        if st.button("Orçamentos", use_container_width=True):
            st.session_state.page = "Orc"
    with col5:
        if st.button("Listagem de Vendas", use_container_width=True):
            st.session_state.page = "ListV"

# Estrutura principal
mostrar_cabecalho()

if 'page' not in st.session_state:
    st.session_state.page = 'Menu'

if st.session_state.page == 'Menu':
    st.write("Selecione uma opção no menu acima.")
elif st.session_state.page == 'Ab/Fc':
    tela_abertura_caixa()
elif st.session_state.page == 'FecharCaixa':
    tela_fechamento_caixa()
elif st.session_state.page == 'Venda':
    tela_efetuar_venda()
elif st.session_state.page == 'Orc':
    tela_orcamentos()
elif st.session_state.page == 'ListV':
    st.write("listagem")
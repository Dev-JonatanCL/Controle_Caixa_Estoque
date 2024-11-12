import streamlit as st
from Banco import sqlite3
import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, 'portuguese')

def formatar_contabil(valor):
    return locale.currency(valor, grouping=True)

def formatar_margem(margem):
    return "{:.2f}%".format(margem * 100/100)

def conectar_db():
    return sqlite3.connect('produtos.db')

def listar_produtos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def calcular_margem(custo, preco):
    if preco != 0:
        return ((preco - custo) / custo) * 100
    return 0

def pesquisar_produtos(termo):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE descricao LIKE ? OR cod LIKE ?", ('%' + termo + '%', '%' + termo + '%'))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def exibir_produto_atual():
    if 'indice_produto' not in st.session_state:
        st.session_state.indice_produto = 0

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (st.session_state.indice_produto + 1,))
    produto = cursor.fetchone()
    conn.close()

    col1, col2 = st.columns([2,5])

    with col1:
        cod = st.number_input("Código", produto[1])
    with col2:
        descricao = st.text_input("Descrição", produto[2])

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fabricante = st.text_input("Fabricante", produto[3])
    with col2:
        fornecedor = st.text_input("Fornecedor", produto[4])
    with col3:
        unidade = st.text_input("Unidade", produto[5])
    with col4:
        qtd_estoque = st.number_input("Quantidade em Estoque", value=produto[6], min_value=0)

    col1, col2, col3 = st.columns(3)

    with col1:    
        custo = st.number_input("Custo", value=produto[7], min_value=0.0, format="%.2f")
    with col2:
        margem_calculada = calcular_margem(custo, produto[9])
        margem = st.number_input("Margem", value=margem_calculada, min_value=0.0, format="%.2f", disabled=True)
    with col3:
        preco = st.number_input("Preço", value=produto[9], min_value=0.0, format="%.2f")

    campos_alterados = (
        produto[1] != cod or 
        produto[2] != descricao or
        produto[3] != fabricante or
        produto[4] != fornecedor or
        produto[5] != unidade or
        produto[6] != qtd_estoque or
        produto[7] != custo or
        produto[9] != preco
    )

    if campos_alterados:
        st.write('Deseja salvar as alterações?')

        col1, col2, col3 = st.columns([1,1,4])

        with col1:
            salvar_sim = st.button('Sim', use_container_width=True)
        with col2:    
            salvar_nao = st.button('Não', use_container_width=True)
        with col3:
            st.write('')

        if salvar_sim:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE produtos
                SET cod = ?, descricao = ?, fabricante = ?, fornecedor = ?, unidade = ?, qtd_estoque = ?, custo = ?, margem = ?, preco = ?
                WHERE id = ?
            ''', (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, produto[0]))
            conn.commit()
            conn.close()

            st.success("Produto atualizado com sucesso!")
            st.rerun()

        elif salvar_nao:
            st.warning("Alterações não salvas.")       

def exibir_resultados_pesquisa(produtos):
    if len(produtos) > 0:
        for produto in produtos:
            produtos_df = pd.DataFrame(produtos, columns=["ID", "Código", "Descrição", "Fabricante", "Fornecedor", "Unidade", "Qtd Estoque", "Custo", "Margem", "Preço"])
            produtos_df = produtos_df.drop(columns=['ID'])
            produtos_df['Custo'] = produtos_df['Custo'].apply(lambda x: formatar_contabil(x))
            produtos_df['Preço'] = produtos_df['Preço'].apply(lambda x: formatar_contabil(x))
            produtos_df['Margem'] = produtos_df['Margem'].apply(lambda x: formatar_margem(x))
            st.dataframe(produtos_df.style)
    else:
        st.write("Nenhum produto encontrado.")

def tela_pesquisa():
    st.subheader("Pesquisar Produtos")

    termo_pesquisa = st.text_input("Digite o código ou descrição do produto")

    if termo_pesquisa:
        if st.button("Pesquisar"):
            produtos_encontrados = pesquisar_produtos(termo_pesquisa)
            exibir_resultados_pesquisa(produtos_encontrados)

    if st.button('Voltar', use_container_width=True):
        st.session_state.page = 'Etq'
        st.rerun()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Estoque', use_container_width=True, key="estoque_button"):
        st.session_state.page = 'Etq'

with col2:
    if st.button('Pedido de Compra', use_container_width=True, key="pedido_compra_button"):
        st.session_state.page = 'PedC'

with col3:
    if st.button('Entrada', use_container_width=True, key="entrada_button"):
        st.session_state.page = 'Ent'

if 'page' not in st.session_state:
    st.session_state.page = 'Etq'

if st.session_state.page == 'Etq':
    st.write('\n')
    st.subheader('Controle de Estoque')

    col1, col2, col3, col4, col5, col6 = st.columns([1,1,2,2,2,2])
    
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
        if st.button('Apagar', use_container_width=True, key="apagar_button"):
            st.session_state.page = 'apagar'
            st.rerun()

    with col5:
        if st.button('Pesquisar', use_container_width=True, key="pesquisar_button"):
            st.session_state.page = 'pesq'
            st.rerun()

    with col6:
        if st.button('Listagem', use_container_width=True, key="listagem_button"):
            st.session_state.page = 'list'
            st.rerun()

    exibir_produto_atual()

if st.session_state.page == 'list':    
    st.write('\n')
    st.subheader('Listagem de Produtos')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button('Imprimir', use_container_width=True, key="imprimir_button"):
            st.session_state.page = 'imp'

    with col2:
        if st.button('Pesquisar', use_container_width=True, key="pesquisar_list_button"):
            st.session_state.page = 'pesq'
            st.rerun()

    with col3:
        if st.button('Voltar', use_container_width=True, key="voltar_list_button"):
            st.session_state.page = 'Etq'
            st.rerun()

    with col4:
        st.write('')

    produtos = listar_produtos()
    produtos_df = pd.DataFrame(produtos, columns=["ID", "Código", "Descrição", "Fabricante", "Fornecedor", "Unidade", "Qtd Estoque", "Custo", "Margem", "Preço"])
    produtos_df = produtos_df.drop(columns=['ID'])

    produtos_df['Custo'] = produtos_df['Custo'].apply(lambda x: formatar_contabil(x))
    produtos_df['Preço'] = produtos_df['Preço'].apply(lambda x: formatar_contabil(x))
    produtos_df['Margem'] = produtos_df['Margem'].apply(lambda x: formatar_margem(x))

    st.dataframe(produtos_df.style)

if st.session_state.page == 'apagar':
    st.write('\n')
    st.subheader('Deseja realmente apagar o cadastro deste produto ?')

    produto_atual = listar_produtos()[st.session_state.indice_produto]
    produto_id = produto_atual[0]
    descricao = produto_atual[2]

    st.write(f"Código: {produto_atual[1]}")
    st.write(f"Descrição: {descricao}")
    st.write('\n')
    st.write('\n')
    col1, col2, col3 = st.columns([2,2,4])

    with col1:
        if st.button('Apagar', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()
            conn.close()

            st.success(f"Produto {descricao} apagado com sucesso!")
            st.session_state.page = 'Etq'
            st.rerun()

    with col2:
        if st.button('Cancelar', use_container_width=True):
            st.session_state.page = 'Etq'
            st.rerun()

    with col3:
        st.write('')

if st.session_state.page == 'pesq':
    tela_pesquisa()

if st.session_state.page == 'PedC':
    st.header('Pedido')

if st.session_state.page == 'Ent':
    st.header('Entrada')

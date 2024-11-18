import streamlit as st
import sqlite3
import pandas as pd
import datetime

def conectar_db():
    return sqlite3.connect('produtos.db')

def formatar_data(data_str):
    try:
        data = datetime.datetime.strptime(data_str, '%Y-%m-%d').date()
        return data.strftime('%d/%m/%Y')
    except ValueError:
        return None
def inserir_conta(cod, nome, data_entrada, vencimento, num_documento, parcela, valor):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO contas_a_pagar (cod_fornecedor, nome_fornecedor, data_entrada, vencimento, numero_documento, parcela, valor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (cod, nome, data_entrada, vencimento, num_documento, parcela, valor))
    conn.commit()
    conn.close()

def listar_contas_a_pagar():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contas_a_pagar")
    contas_a_pagar = cursor.fetchall()
    conn.close()
    return contas_a_pagar

def listar_contas_pagas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contas_pagas")
    contas_pagas = cursor.fetchall()
    conn.close()
    return contas_pagas

def exibir_contas_a_pagar():
    if 'indice_pagar' not in st.session_state:
        st.session_state.indice_pagar = 0

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM contas_a_pagar LIMIT 1 OFFSET ? ''', (st.session_state.indice_pagar,))
    pagar = cursor.fetchone()
    conn.close()

    if pagar is None:
        st.warning("Não há contas a pagar.")
        return
    
    with st.form("form_contas_a_pagar"):

        col1, col2 = st.columns(2)

        with col1:
            cod = st.text_input("Código do fornecedor", pagar[1])
            nome = st.text_input("Nome do fornecedor", pagar[2])
            data_entrada = st.date_input("Data de Entrada", pagar[3])
            vencimento = st.date_input("Vencimento", pagar[4])
        with col2:
            num_documento = st.text_input("Número do Documento", pagar[5])
            parcela = st.number_input("Parcela", pagar[6], min_value=1, step=1)
            valor = st.number_input("Valor", pagar[7], min_value=0.0, step=0.01, format="%.2f")

        data_quitacao = st.form_submit_button("Quitar")

    if data_quitacao:
        data_pagamento = datetime.now().formatar_data()
        
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contas_pagas (cod_fornecedor, nome_fornecedor, numero_documento, valor, parcela, data_pagamento, vencimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cod, nome, num_documento, valor, parcela, data_pagamento, vencimento))
        
        cursor.execute('''
            DELETE FROM contas_a_pagar WHERE id = ?
        ''', (pagar[0],))
        
        conn.commit()
        conn.close()

        st.success("Conta quitada com sucesso !")
    
    if st.button('Salvar Alterações', use_container_width=True):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE contas_a_pagar
            SET cod_fornecedor = ?, nome_fornecedor = ?, data_entrada = ?, vencimento = ?, 
                numero_documento = ?, parcela = ?, valor = ?, data_quitacao = ?
            WHERE id = ?
        ''', (cod, nome, data_entrada, vencimento, num_documento, parcela, valor, data_quitacao, pagar[0]))
           
        conn.commit()
        conn.close()
        st.success("Cliente atualizado com sucesso!")

col1, col2  = st.columns(2)

with col1:
    if st.button("Contas a pagar", use_container_width=True, key="contas_a_pag_button"):
        st.session_state.page = "pagar"
with col2:
    if st.button("Contas pagas", use_container_width=True, key="contas_pagas_button"):
        st.session_state.page = "pagas"

if 'page' not in st.session_state:
    st.session_state.page = "pagar"
    
if st.session_state.page == "pagar":
    st.write('\n')
    st.header("Contas a pagar")

    col1, col2, col3, col4, col5, col6 = st.columns([1,1,2,2,2,2])
    
    with col1:
        if st.button("←", use_container_width=True, key="left_button"):
            if st.session_state.indice_pagar > 0:
                st.session_state.indice_pagar -= 1

    with col2:
        if st.button("→", use_container_width=True, key="right_button"):
            if st.session_state.indice_pagar < len(listar_contas_a_pagar()) - 1:
                st.session_state.indice_pagar += 1

    with col3:
        if st.button('Incluir', use_container_width=True, key="incluir_button"):
            st.session_state.page = 'incluir'

    with col4:
        if st.button('Quitar', use_container_width=True, key="quitar_button"):
            st.session_state.page = 'quitar'

    with col5:
        if st.button('Pesquisar', use_container_width=True, key="pesq_pagar_button"):
            st.session_state.page = 'pesq_pagar'
            st.rerun()

    with col6:
        if st.button('Listagem', use_container_width=True, key="listagem_pagar_button"):
            st.session_state.page = 'list_pagar'
            st.rerun()

    exibir_contas_a_pagar()

if st.session_state.page == 'incluir':
    st.write('\n')
    st.header('Cadastrar nova conta')

    if st.button('Voltar', use_container_width=True, key="voltar_button"):
        st.session_state.page = 'pagar'

    with st.form("form_contas_a_pagar"):

        col1, col2 = st.columns(2)

        with col1:
            cod = st.text_input("Código")
            nome = st.text_input("Nome")
            data_entrada = st.date_input("Data de Entrada")
            vencimento = st.date_input("Vencimento")
        with col2:
            num_documento = st.text_input("Número do Documento")
            parcela = st.number_input("Parcela", min_value=1, step=1)
            valor = st.number_input("Valor", min_value=0.0, step=0.01, format="%.2f")

        submit = st.form_submit_button("Cadastrar")

    if submit:
        if cod and nome and data_entrada and vencimento and num_documento and parcela and valor:
            inserir_conta(cod, nome, data_entrada, vencimento, num_documento, parcela, valor)  
            st.success('Cadastro de nova conta realizado com sucesso!')
        else:
            st.error('Preencha todos os campos obrigatórios.')

if st.session_state.page == 'quitar':
    st.write('')

if st.session_state.page == 'pesq_pagar':
    st.write('')

if st.session_state.page == 'list_pagar':
    st.write('')
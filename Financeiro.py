import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import locale

def run():
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    
    def conectar_db():
        return sqlite3.connect('banco.db')

    def formatar_contabil(valor):
        try:
            return locale.currency(valor, grouping=True)
        except ValueError:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_data(data_str):
        if isinstance(data_str, str):
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d').date()
                return data.strftime('%d/%m/%Y')
            except ValueError:
                return data_str
        else:
            return str(data_str)

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
        cursor.execute(''' SELECT * FROM contas_a_pagar ''')
        contas_a_pagar = cursor.fetchall()
        conn.close()
        return contas_a_pagar

    def listar_contas_pagas():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM contas_pagas ''')
        contas_pagas = cursor.fetchall()
        conn.close()
        return contas_pagas

    def buscar_fornecedores():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' SELECT id, nome_fornecedor FROM cadastro_fornecedores ''')
        fornecedores = cursor.fetchall()
        conn.close()
        return fornecedores

    def pesquisar_pagas(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM contas_pagas 
            WHERE numero_documento LIKE ? OR data_pagamento LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        pagas = cursor.fetchall()
        conn.close()
        return pagas

    def pesquisar_pagar(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM contas_a_pagar 
            WHERE numero_documento LIKE ? OR data_entrada LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        pagar = cursor.fetchall()
        conn.close()
        return pagar

    def exibir_resultados_pesquisa_pagas(pagas):
        if len(pagas) > 0:
            pagas_df = pd.DataFrame(pagas, columns=["Código", "Credor", "N° Documento", "Data Pagamento", "Vencimento", "Parcela", "Valor"])
            st.dataframe(pagas_df.style, use_container_width=True)
        else:
            st.write("Nenhuma conta paga encontrada.")

    def tela_pesquisa_pagas():

        pesquisa = st.text_input("Digite o N° do documento ou data do pagamento para pesquisar: ")

        if pesquisa:
            pagas_encontradas = pesquisar_pagas(pesquisa)
            exibir_resultados_pesquisa_pagas(pagas_encontradas)

    def tela_pesquisa_pagar():

        pesquisa = st.text_input("Digite o N° do documento ou data da entrada para pesquisar: ")

        if pesquisa:
            try:
                data_pesquisa = datetime.strptime(pesquisa, '%d/%m/%Y').date()
                data_pesquisa_formato_banco = data_pesquisa.strftime('%Y-%m-%d')
                pagar_encontradas = pesquisar_pagar(data_pesquisa_formato_banco)
            except ValueError:
                pagar_encontradas = pesquisar_pagar(pesquisa)

            exibir_resultados_pesquisa_pagar(pagar_encontradas)

    def exibir_resultados_pesquisa_pagar(pagar):
        if not pagar:
            st.warning("Não há contas a pagar.")
            return
        
        if st.session_state.indice_pagar >= len(pagar):
            st.session_state.indice_pagar = 0
        elif st.session_state.indice_pagar < 0:
            st.session_state.indice_pagar = len(pagar) - 1

        pagar_atual = pagar[st.session_state.indice_pagar]
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_pagar > 0:
                    st.session_state.indice_pagar -= 1
                    st.rerun()

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_pagar < len(pagar) - 1:
                    st.session_state.indice_pagar += 1
                    st.rerun()
        
        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'pagar'
                st.rerun()

        with st.form("form_contas_a_pagar"):

            col1, col2 = st.columns(2)

            with col1:
                cod = st.text_input("Código do fornecedor", pagar_atual[1])
                nome = st.text_input("Nome do fornecedor", pagar_atual[2])
                data_entrada = datetime.strptime(pagar_atual[3], '%Y-%m-%d').date()
                data_entrada_formatada = data_entrada.strftime('%d/%m/%Y')
                st.text_input("Data de Entrada", data_entrada_formatada)
                vencimento = datetime.strptime(pagar_atual[3], '%Y-%m-%d').date()
                vencimento_formatada = vencimento.strftime('%d/%m/%Y')
                st.text_input("Vencimento", vencimento_formatada)
            with col2:
                num_documento = st.text_input("Número do Documento", pagar_atual[5])
                parcela = st.number_input("Parcela", value=pagar_atual[6], min_value=1, step=1)
                valor = st.number_input("Valor", value=pagar_atual[7], min_value=0.0, step=0.01, format="%.2f")

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
                cod = st.text_input("Código do fornecedor", pagar[1], disabled=True)
                nome = st.text_input("Nome do fornecedor", pagar[2])
                data_entrada = datetime.strptime(pagar[3], '%Y-%m-%d').date()
                data_entrada_formatada = data_entrada.strftime('%d/%m/%Y')
                st.text_input("Data de Entrada", data_entrada_formatada, disabled=True)
                vencimento = datetime.strptime(pagar[4], '%Y-%m-%d').date()
                vencimento_formatada = vencimento.strftime('%d/%m/%Y')
                vencimento = st.text_input("Vencimento", vencimento_formatada)
            with col2:
                num_documento = st.text_input("Número do Documento", pagar[5], disabled=True)
                parcela = st.text_input("Parcela", value=pagar[6], disabled=True)
                valor = st.number_input("Valor", value=pagar[7], min_value=0.0, step=0.01, format="%.2f")

            data_quitacao = st.form_submit_button("Quitar")

        if data_quitacao:
            data_pagamento = datetime.now().strftime("%d/%m/%Y")
            
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

        col1, col2, col3, col4, col5 = st.columns([1,1,2,2,2])
        
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
                st.rerun()

        with col4:
            if st.button('Pesquisar', use_container_width=True, key="pesq_pagar_button"):
                st.session_state.page = 'pesq_pagar'
                st.rerun()

        with col5:
            if st.button('Listagem', use_container_width=True, key="listagem_pagar_button"):
                st.session_state.page = 'list_pagar'
                st.rerun()

        exibir_contas_a_pagar()

    if st.session_state.page == 'incluir':
        st.write('\n')
        st.header('Cadastrar nova conta')

        col1, col2, col3 = st.columns([2, 4, 2])

        with col1:
            input_option = st.radio("", ("Fornecedor", "Não cadastrado"))

        with col2:
            st.write('')

        with col3:
            st.write('\n')
            st.write('\n')
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'pagar'
                st.rerun()

        if input_option == 'Fornecedor':
            if 'indice_pagar' not in st.session_state:
                st.session_state.indice_pagar = 0
            with st.form("form_contas_a_pagar_fornecedor"):

                col1, col2 = st.columns(2)

                with col1:

                    fornecedores = buscar_fornecedores()

                    cod = st.text_input("Código do Fornecedor")
                    opc_for = [fornecedor[1] for fornecedor in fornecedores]
                    nome = st.selectbox("Razão Social", opc_for)
                    data_entrada = datetime.strptime(pagar[3], '%Y-%m-%d').date()
                    data_entrada_formatada = data_entrada.strftime('%d/%m/%Y')
                    st.text_input("Data de Entrada", data_entrada_formatada, disabled=True)
                    vencimento = datetime.strptime(pagar[4], '%Y-%m-%d').date()
                    vencimento_formatada = vencimento.strftime('%d/%m/%Y')
                    vencimento = st.text_input("Vencimento", vencimento_formatada)

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

        else:
            if 'indice_pagar' not in st.session_state:
                st.session_state.indice_pagar = 0
            with st.form("form_contas_a_pagar_fornecedor"):

                col1, col2 = st.columns(2)

                with col1:
                    cod = st.text_input("Código do Fornecedor")
                    nome = st.text_input("Razão Social")
                    data_entrada = datetime.strptime(pagar[3], '%Y-%m-%d').date()
                    data_entrada_formatada = data_entrada.strftime('%d/%m/%Y')
                    st.text_input("Data de Entrada", data_entrada_formatada, disabled=True)
                    vencimento = datetime.strptime(pagar[4], '%Y-%m-%d').date()
                    vencimento_formatada = vencimento.strftime('%d/%m/%Y')
                    vencimento = st.text_input("Vencimento", vencimento_formatada)
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

    if st.session_state.page == 'pesq_pagar':
        tela_pesquisa_pagar()

    if st.session_state.page == 'list_pagar':
        st.write('')
        st.header('Listagem de Contas a Pagar')

        if st.button('Voltar', use_container_width=True, key="voltar_button"):
            st.session_state.page = 'pagar'
            st.rerun()

        pagar = listar_contas_a_pagar()
        pagar_df = pd.DataFrame(pagar, columns=["ID", "Código", "Credor", "Data Entrada", "Vencimento", "N° Documento", "Parcela", "Valor", "data_quitacao"])
        pagar_df = pagar_df.drop(columns=['ID', 'data_quitacao'])
        pagar_df['Data Entrada'] = pagar_df['Data Entrada'].apply(lambda x: formatar_data(x))
        pagar_df['Vencimento'] = pagar_df['Vencimento'].apply(lambda x: formatar_data(x))
        pagar_df['Valor'] = pagar_df['Valor'].apply(lambda x: formatar_contabil(x))

        st.dataframe(pagar_df.style, use_container_width=True)

    if st.session_state.page == 'pagas':
        st.write('')
        st.header('Listagem de Contas Pagas')

        tela_pesquisa_pagas()    

        pagas = listar_contas_pagas()
        pagas_df = pd.DataFrame(pagas, columns=["ID", "Código", "Credor", "N° Documento", "Valor", "Parcela", "Data Pagamento", "Vencimento"])
        pagas_df = pagas_df.drop(columns=['ID'])
        pagas_df['Data Pagamento'] = pagas_df['Data Pagamento'].apply(lambda x: formatar_data(x))
        pagas_df['Vencimento'] = pagas_df['Vencimento'].apply(lambda x: formatar_data(x))
        pagas_df['Valor'] = pagas_df['Valor'].apply(lambda x: formatar_contabil(x))

        st.dataframe(pagas_df.style, use_container_width=True)

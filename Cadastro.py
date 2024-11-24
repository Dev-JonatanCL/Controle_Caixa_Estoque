import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime

def run():


    def conectar_db():
        return sqlite3.connect('banco.db')

    def calcular_margem(custo, preco):
        try:
            if custo == 0:
                return 0
            return ((preco - custo) / custo) * 100
        except ValueError:
            return 0 

    def inserir_cliente_pf(cod, nome, cpf, rg, data_nascimento, filiacao, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cadastro_cliente_pessoa_fisica (cod_cliente, nome_cliente, cpf, rg, data_nascimento, filiacao, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cod, nome, cpf, rg, data_nascimento, filiacao, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao))
        conn.commit()
        conn.close()

    def inserir_cliente_pj(cod, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, contato, complemento, telefone, celular, email, observacao):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cadastro_pessoa_juridica (cod_cliente, nome_empresa, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, contato, complemento, telefone, celular, email, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cod, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, contato, complemento, telefone, celular, email, observacao))
        conn.commit()
        conn.close()

    def inserir_fornecedor(cod, nome_fornecedor, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, telefone, celular, email, contato, observacao):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cadastro_fornecedores (cod_fornecedor, nome_fornecedor, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, telefone, celular, email, contato, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cod, nome_fornecedor, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, telefone, celular, email, contato, observacao))
        conn.commit()
        conn.close()

    def inserir_produto(cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima))
        conn.commit()
        conn.close()

    def listar_clientes_pf():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cadastro_cliente_pessoa_fisica")
        cadastro_cliente_pessoa_fisica = cursor.fetchall()
        conn.close()
        return cadastro_cliente_pessoa_fisica

    def listar_clientes_pj():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cadastro_pessoa_juridica")
        cadastro_pessoa_juridica = cursor.fetchall()
        conn.close()
        return cadastro_pessoa_juridica

    def listar_fornecedores():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cadastro_fornecedores")
        fornecedores = cursor.fetchall()
        conn.close()
        return fornecedores

    def pesquisar_clientes_pf(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cadastro_cliente_pessoa_fisica 
            WHERE cod_cliente LIKE ? OR nome_cliente LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        clientes_pf = cursor.fetchall()
        conn.close()
        return clientes_pf

    def pesquisar_clientes_pj(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cadastro_pessoa_juridica 
            WHERE cod_cliente LIKE ? OR nome_empresa LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        clientes_pj = cursor.fetchall()
        conn.close()
        return clientes_pj

    def exibir_resultados_pesquisa_pf(clientes):
        if not clientes:
            return

        if st.session_state.indice_cliente >= len(clientes):
            st.session_state.indice_cliente = 0
        elif st.session_state.indice_cliente < 0:
            st.session_state.indice_cliente = len(clientes) - 1

        cliente_atual = clientes[st.session_state.indice_cliente]

        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_cliente > 0:
                    st.session_state.indice_cliente -= 1
                    st.rerun()

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_cliente < len(clientes) - 1:
                    st.session_state.indice_cliente += 1
                    st.rerun()
        
        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'cli'
                st.rerun()

        col1, col2 = st.columns([2,4])

        with col1:
            cod_cli = st.text_input('Código', cliente_atual[1])
        with col2:
            nome_cli = st.text_input('Nome', cliente_atual[2])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cpf_cli = st.text_input('CPF', cliente_atual[3])
        with col2:
            rg_cli = st.text_input('RG', cliente_atual[4])
        with col3:
            data_nascimento_cli = datetime.strptime(cliente_atual[14], '%d/%m/%Y').date()
            data_nascimento_formatada = data_nascimento_cli.strftime('%d/%m/%Y')
            st.text_input("Data de nascimento", data_nascimento_formatada)
        with col4:
            filiacao_cli = st.text_input('Filiação', cliente_atual[15])

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            endereco_cli = st.text_input('Endereço', cliente_atual[5])
        with col2:
            numero_cli = st.text_input('Numero', cliente_atual[6])
        with col3:
            cep_cli = st.text_input('CEP', cliente_atual[7])

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro_cli = st.text_input('Bairro', cliente_atual[8])
        with col2:
            cidade_cli = st.text_input('Cidade', cliente_atual[9])
        with col3:
            estado_cli = st.text_input('Estado', cliente_atual[10])

        col1, col2, col3 = st.columns(3)

        with col1:
            complemento_cli = st.text_input('Complemento', cliente_atual[11])
        with col2:
            telefone_cli = st.text_input('Telefone', cliente_atual[12])
        with col3:
            celular_cli = st.text_input('Celular', cliente_atual[13])
        
        email_cli = st.text_input('Email', cliente_atual[16])
        observacao_cli = st.text_area('Observação: ', cliente_atual[17], height=150)

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cadastro_cliente_pessoa_fisica 
                SET cod_cli = ?, nome_cli = ?, cpf_cli = ?, rg_cli = ?, endereco_cli = ?, numero_cli = ?, cep_cli = ?, bairro_cli = ?, cidade_cli = ?, estado_cli = ?, complemento_cli = ?, 
                    telefone_cli = ?, celular_cli = ?, data_nascimento_cli = ?, filiacao_cli = ?, email_cli = ?, observacao_cli = ? 
                WHERE id = ?
            ''', (cod_cli, nome_cli, cpf_cli, rg_cli, endereco_cli, numero_cli, cep_cli, bairro_cli, cidade_cli, estado_cli, complemento_cli, 
                    telefone_cli, celular_cli, data_nascimento_cli, filiacao_cli, email_cli, observacao_cli, st.session_state.indice_cliente + 1))
                
            conn.commit()
            conn.close()

            st.success("Cliente atualizado com sucesso!")

    def exibir_resultados_pesquisa_pj(clientes):
        if not clientes:
            return

        if st.session_state.indice_cliente >= len(clientes):
            st.session_state.indice_cliente = 0
        elif st.session_state.indice_cliente < 0:
            st.session_state.indice_cliente = len(clientes) - 1

        cliente_atual = clientes[st.session_state.indice_cliente]

        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_cliente > 0:
                    st.session_state.indice_cliente -= 1
                    st.rerun()

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_cliente < len(clientes) - 1:
                    st.session_state.indice_cliente += 1
                    st.rerun()
        
        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'cli'
                st.rerun()

        col1, col2 = st.columns([2, 4])

        with col1:
            cod = st.text_input('Código', cliente_atual[1])
        with col2:
            razao_social = st.text_input('Razão Social', cliente_atual[2])

        col1, col2, col3 = st.columns(3)

        with col1:
            cnpj = st.text_input('CNPJ', cliente_atual[3])
        with col2:
            inscricao_estadual = st.text_input('Inscrição Estadual', cliente_atual[4])
        with col3:
            contato = st.text_input('Contato', cliente_atual[5])

        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            endereco = st.text_input('Endereço', cliente_atual[6])
        with col2:
            numero = st.text_input('Numero', cliente_atual[7])
        with col3:
            cep = st.text_input('CEP', cliente_atual[8])

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro = st.text_input('Bairro', cliente_atual[9])
        with col2:
            cidade = st.text_input('Cidade', cliente_atual[10])
        with col3:
            estado = st.text_input('Estado', cliente_atual[11])

        col1, col2, col3 = st.columns(3)

        with col1:
            complemento = st.text_input('Complemento', cliente_atual[12])
        with col2:
            telefone = st.text_input('Telefone', cliente_atual[13])
        with col3:
            celular = st.text_input('Celular', cliente_atual[14])

        email = st.text_input('Email', cliente_atual[15])
        observacao = st.text_area('Observação: ', cliente_atual[16], height=150, key='observacao_ju')

        if st.button('Salvar Alterações', use_container_width=True, key='salvar_ju'):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cadastro_cliente_pessoa_juridica 
                    SET cod_cliente = ?, razao_social = ?, cnpj = ?, inscricao_estadual = ?, contato = ?, endereco = ?, numero = ?, cep = ?, bairro = ?, cidade = ?, estado = ?, 
                        complemento = ?, telefone = ?, celular = ?, email = ?, observacao = ? 
                    WHERE id = ? 
                ''', (cod, razao_social, cnpj, inscricao_estadual, contato, endereco, numero, cep, bairro, cidade, estado, 
                        complemento, telefone, celular, email, observacao, st.session_state.indice_cliente + 1))
                
            conn.commit()
            conn.close()

            st.success("Cliente atualizado com sucesso!")

    def tela_pesquisa_clientes():
        st.subheader("Pesquisar Clientes")

        pesquisa = st.text_input("Digite o código ou nome do cliente")

        if pesquisa:
            clientes_pf_encontrados = pesquisar_clientes_pf(pesquisa)
            exibir_resultados_pesquisa_pf(clientes_pf_encontrados)
            clientes_pj_encontrados = pesquisar_clientes_pj(pesquisa)
            exibir_resultados_pesquisa_pj(clientes_pj_encontrados)

    def pesquisar_fornecedores(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cadastro_fornecedores 
            WHERE cod_fornecedor LIKE ? OR nome_fornecedor LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        fornecedores = cursor.fetchall()
        conn.close()
        return fornecedores

    def exibir_resultados_pesquisa_fornecedores(fornecedores):
        if not fornecedores:
            st.warning("Não há fornecedores cadastrados.")
            return

        if st.session_state.indice_fornecedor >= len(fornecedores):
            st.session_state.indice_fornecedor = 0
        elif st.session_state.indice_fornecedor < 0:
            st.session_state.indice_fornecedor = len(fornecedores) - 1

        fornecedor_atual = fornecedores[st.session_state.indice_fornecedor]

        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_fornecedor > 0:
                    st.session_state.indice_fornecedor -= 1
                    st.rerun()

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_fornecedor < len(fornecedores) - 1:
                    st.session_state.indice_fornecedor += 1
                    st.rerun()
        
        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'cli'
                st.rerun()

        col1, col2 = st.columns([2, 4])

        with col1:
            cod_fornecedor = st.text_input('Código', fornecedor_atual[1])
        with col2:
            nome_fornecedor = st.text_input('Razão social', fornecedor_atual[2])

        col1, col2, col3 = st.columns(3)

        with col1:
            cnpj = st.text_input('CNPJ', fornecedor_atual[11])
        with col2:
            inscricao_estadual = st.text_input('Inscrição Estadual', fornecedor_atual[12])
        with col3:
            contato = st.text_input('Contato', fornecedor_atual[14])

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            endereco = st.text_input('Endereço', fornecedor_atual[3])
        with col2:
            numero = st.text_input('Número', fornecedor_atual[4])
        with col3:
            cep = st.text_input('CEP', fornecedor_atual[8])

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro = st.text_input('Bairro', fornecedor_atual[5])
        with col2:
            cidade = st.text_input('Cidade', fornecedor_atual[6])
        with col3:
            estado = st.text_input('Estado', fornecedor_atual[7])

        col1, col2 = st.columns(2)

        with col1:
            telefone = st.text_input('Telefone', fornecedor_atual[9])
        with col2:
            celular = st.text_input('Celular', fornecedor_atual[10])

        email = st.text_input('Email', fornecedor_atual[13])   
        observacao = st.text_area('Observação', fornecedor_atual[15], height=150)

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cadastro_fornecedores 
                SET cod_fornecedor = ?, nome_fornecedor = ?, endereco = ?, numero = ?, bairro = ?, cidade = ?, estado = ?, cep = ?, telefone = ?, celular = ?, 
                    cnpj = ?, inscricao_estadual = ?, email = ?, contato = ?, observacao = ? 
                WHERE id = ?
            ''', (cod_fornecedor, nome_fornecedor, endereco, numero, bairro, cidade, estado, cep, telefone, celular, 
                cnpj, inscricao_estadual, email, contato, observacao, st.session_state.indice_fornecedor + 1))

            conn.commit()
            conn.close()

            st.success("Fornecedor atualizado com sucesso!")

    def tela_pesquisa_fornecedores():
        st.subheader("Pesquisar Fornecedores")

        pesquisa = st.text_input("Digite o código ou nome do fornecedor")

        if pesquisa:
            fornecedores_encontrados = pesquisar_fornecedores(pesquisa)
            exibir_resultados_pesquisa_fornecedores(fornecedores_encontrados)

    def exibir_cliente_pf_atual():
        if 'indice_cliente' not in st.session_state:
            st.session_state.indice_cliente = 0

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM cadastro_cliente_pessoa_fisica LIMIT 1 OFFSET ? ''', (st.session_state.indice_cliente,))
        cliente_pf = cursor.fetchone()
        conn.close()

        if cliente_pf is None:
            st.warning("Não há clientes PF cadastrados.")
            return

        col1, col2 = st.columns([2,4])

        with col1:
            cod_cli = st.text_input('Código', cliente_pf[1])
        with col2:
            nome_cli = st.text_input('Nome', cliente_pf[2])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cpf_cli = st.text_input('CPF', cliente_pf[3])
        with col2:
            rg_cli = st.text_input('RG', cliente_pf[4])
        with col3:
            data_nascimento_cli = datetime.strptime(cliente_pf[14], '%d/%m/%Y').date()
            data_nascimento_formatada = data_nascimento_cli.strftime('%d/%m/%Y')
            st.text_input("Data de nascimento", data_nascimento_formatada)
        with col4:
            filiacao_cli = st.text_input('Filiação', cliente_pf[15])

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            endereco_cli = st.text_input('Endereço', cliente_pf[5])
        with col2:
            numero_cli = st.text_input('Numero', cliente_pf[6])
        with col3:
            cep_cli = st.text_input('CEP', cliente_pf[7])

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro_cli = st.text_input('Bairro', cliente_pf[8])
        with col2:
            cidade_cli = st.text_input('Cidade', cliente_pf[9])
        with col3:
            estado_cli = st.text_input('Estado', cliente_pf[10])

        col1, col2, col3 = st.columns(3)

        with col1:
            complemento_cli = st.text_input('Complemento', cliente_pf[11])
        with col2:
            telefone_cli = st.text_input('Telefone', cliente_pf[12])
        with col3:
            celular_cli = st.text_input('Celular', cliente_pf[13])
        
        email_cli = st.text_input('Email', cliente_pf[16])
        observacao_cli = st.text_area('Observação: ', cliente_pf[17], height=150)

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cadastro_cliente_pessoa_fisica 
                SET cod_cli = ?, nome_cli = ?, cpf_cli = ?, rg_cli = ?, endereco_cli = ?, numero_cli = ?, cep_cli = ?, bairro_cli = ?, cidade_cli = ?, estado_cli = ?, complemento_cli = ?, 
                    telefone_cli = ?, celular_cli = ?, data_nascimento_cli = ?, filiacao_cli = ?, email_cli = ?, observacao_cli = ? 
                WHERE id = ?
            ''', (cod_cli, nome_cli, cpf_cli, rg_cli, endereco_cli, numero_cli, cep_cli, bairro_cli, cidade_cli, estado_cli, complemento_cli, 
                    telefone_cli, celular_cli, data_nascimento_cli, filiacao_cli, email_cli, observacao_cli, st.session_state.indice_cliente + 1))
                
            conn.commit()
            conn.close()

            st.success("Cliente atualizado com sucesso!")

    def exibir_cliente_pj_atual():
        if 'indice_cliente' not in st.session_state:
            st.session_state.indice_cliente = 0

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM cadastro_pessoa_juridica LIMIT 1 OFFSET ? ''', (st.session_state.indice_cliente,))
        cliente_pj = cursor.fetchone()
        conn.close()

        if cliente_pj is None:
            st.warning("Não há clientes PJ cadastrados.")
            return

        col1, col2 = st.columns([2, 4])

        with col1:
            cod = st.text_input('Código', cliente_pj[1])
        with col2:
            razao_social = st.text_input('Razão Social', cliente_pj[2])

        col1, col2, col3 = st.columns(3)

        with col1:
            cnpj = st.text_input('CNPJ', cliente_pj[3])
        with col2:
            inscricao_estadual = st.text_input('Inscrição Estadual', cliente_pj[4])
        with col3:
            contato = st.text_input('Contato', cliente_pj[5])

        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            endereco = st.text_input('Endereço', cliente_pj[6])
        with col2:
            numero = st.text_input('Numero', cliente_pj[7])
        with col3:
            cep = st.text_input('CEP', cliente_pj[8])

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro = st.text_input('Bairro', cliente_pj[9])
        with col2:
            cidade = st.text_input('Cidade', cliente_pj[10])
        with col3:
            estado = st.text_input('Estado', cliente_pj[11])

        col1, col2, col3 = st.columns(3)

        with col1:
            complemento = st.text_input('Complemento', cliente_pj[12])
        with col2:
            telefone = st.text_input('Telefone', cliente_pj[13])
        with col3:
            celular = st.text_input('Celular', cliente_pj[14])

        email = st.text_input('Email', cliente_pj[15])
        observacao = st.text_area('Observação: ', cliente_pj[16], height=150, key='observacao_ju')

        if st.button('Salvar Alterações', use_container_width=True, key='salvar_ju'):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cadastro_cliente_pessoa_juridica 
                    SET cod_cliente = ?, razao_social = ?, cnpj = ?, inscricao_estadual = ?, contato = ?, endereco = ?, numero = ?, cep = ?, bairro = ?, cidade = ?, estado = ?, 
                        complemento = ?, telefone = ?, celular = ?, email = ?, observacao = ? 
                    WHERE id = ? 
                ''', (cod, razao_social, cnpj, inscricao_estadual, contato, endereco, numero, cep, bairro, cidade, estado, 
                        complemento, telefone, celular, email, observacao, st.session_state.indice_cliente + 1))
                
            conn.commit()
            conn.close()

            st.success("Cliente atualizado com sucesso!")

    def exibir_fornecedor_atual():
        if 'indice_fornecedor' not in st.session_state:
            st.session_state.indice_fornecedor = 0

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM cadastro_fornecedores LIMIT 1 OFFSET ? ''', (st.session_state.indice_fornecedor,))
        fornecedor = cursor.fetchone()
        conn.close()

        if fornecedor is None:
            st.warning("Não há fornecedores cadastrados.")
            return

        col1, col2 = st.columns([2, 4])

        with col1:
            cod_fornecedor = st.text_input('Código', fornecedor[1])
        with col2:
            nome_fornecedor = st.text_input('Razão social', fornecedor[2])

        col1, col2, col3 = st.columns(3)

        with col1:
            cnpj = st.text_input('CNPJ', fornecedor[11])
        with col2:
            inscricao_estadual = st.text_input('Inscrição Estadual', fornecedor[12])
        with col3:
            contato = st.text_input('Contato', fornecedor[14])

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            endereco = st.text_input('Endereço', fornecedor[3])
        with col2:
            numero = st.text_input('Número', fornecedor[4])
        with col3:
            cep = st.text_input('CEP', fornecedor[8])

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro = st.text_input('Bairro', fornecedor[5])
        with col2:
            cidade = st.text_input('Cidade', fornecedor[6])
        with col3:
            estado = st.text_input('Estado', fornecedor[7])

        col1, col2 = st.columns(2)

        with col1:
            telefone = st.text_input('Telefone', fornecedor[9])
        with col2:
            celular = st.text_input('Celular', fornecedor[10])

        email = st.text_input('Email', fornecedor[13])   
        observacao = st.text_area('Observação', fornecedor[15], height=150)

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cadastro_fornecedores 
                SET cod_fornecedor = ?, nome_fornecedor = ?, endereco = ?, numero = ?, bairro = ?, cidade = ?, estado = ?, cep = ?, telefone = ?, celular = ?, 
                    cnpj = ?, inscricao_estadual = ?, email = ?, contato = ?, observacao = ? 
                WHERE id = ?
            ''', (cod_fornecedor, nome_fornecedor, endereco, numero, bairro, cidade, estado, cep, telefone, celular, 
                cnpj, inscricao_estadual, email, contato, observacao, st.session_state.indice_fornecedor + 1))

            conn.commit()
            conn.close()

            st.success("Fornecedor atualizado com sucesso!")

    def gerar_codigo_aleatorio(tamanho=8):
        digitos = '0123456789'
        return ''.join(np.random.choice(list(digitos), tamanho))

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button('Cliente', use_container_width=True, key="cliente_button"):
            st.session_state.page = 'cli'
            st.session_state.tipo_cliente = None

    with col2:
        if st.button('Fornecedor', use_container_width=True, key="fornecedor_button"):
            st.session_state.page = 'for'

    with col3:
        if st.button('Produto', use_container_width=True, key="produto_button"):
            st.session_state.page = 'pro'

    if 'page' not in st.session_state:
        st.session_state.page = 'cli'

    if st.session_state.page == 'cli':
        st.write('\n')
        st.header('Clientes Cadastrados')

        tab1, tab2 = st.tabs(["Pessoa Física", "Pessoa Jurídica"])

        with tab1:

            col1, col2, col3, col4, col5, col6 = st.columns([1,1,2,2,2,2])
            
            with col1:
                if st.button("←", use_container_width=True, key="left_button"):
                    if st.session_state.indice_cliente > 0:
                        st.session_state.indice_cliente -= 1

            with col2:
                if st.button("→", use_container_width=True, key="right_button"):
                    if st.session_state.indice_cliente < len(listar_clientes_pf()) - 1:
                        st.session_state.indice_cliente += 1

            with col3:
                if st.button('Incluir', use_container_width=True, key="incluir_button"):
                    st.session_state.page = 'incluir'
                    st.rerun()

            with col4:
                if st.button('Apagar', use_container_width=True, key="apagar_button"):
                    st.session_state.page = 'apagar_pf'
                    st.rerun()

            with col5:
                if st.button('Pesquisar', use_container_width=True, key="pesquisar_button"):
                    st.session_state.page = 'pesq'
                    st.rerun()

            with col6:
                if st.button('Listagem PF', use_container_width=True, key="listagem_button"):
                    st.session_state.page = 'list_pf'
                    st.rerun()

            exibir_cliente_pf_atual()

        with tab2:

            col1, col2, col3, col4, col5, col6 = st.columns([1,1,2,2,2,2])
            
            with col1:
                if st.button("←", use_container_width=True, key="left_button_pj"):
                    if st.session_state.indice_cliente > 0:
                        st.session_state.indice_cliente -= 1

            with col2:
                if st.button("→", use_container_width=True, key="right_button_pj"):
                    if st.session_state.indice_cliente < len(listar_clientes_pj()) - 1:
                        st.session_state.indice_cliente += 1

            with col3:
                if st.button('Incluir', use_container_width=True, key="incluir_button_pj"):
                    st.session_state.page = 'incluir'
                    st.rerun()

            with col4:
                if st.button('Apagar', use_container_width=True, key="apagar_button_pj"):
                    st.session_state.page = 'apagar_pj'
                    st.rerun()

            with col5:
                if st.button('Pesquisar', use_container_width=True, key="pesquisar_button_pj"):
                    st.session_state.page = 'pesq'
                    st.rerun()

            with col6:
                if st.button('Listagem PJ', use_container_width=True, key="listagem_button_pj"):
                    st.session_state.page = 'list_pj'
                    st.rerun()


            exibir_cliente_pj_atual()

    if st.session_state.page == 'incluir':
        st.write('\n')
        st.header('Cadastrar Cliente')

        col1, col2, col3 = st.columns([2,4,2])
        
        with col1:
            input_option = st.radio("", ("Pessoa Física","Pessoa Jurídica"))
            
        with col2:
            st.write('')
            
        with col3:
            st.write('\n')
            st.write('\n')
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'cli'
                st.rerun()
        
        if input_option == "Pessoa Física":
            st.subheader("Cadastro - Pessoa Física")
            with st.form(key='Cliente_form_pf'):

                col1, col2 = st.columns([2,4])

                with col1:
                    cod_cli = st.text_input('Código', value=gerar_codigo_aleatorio())
                with col2:
                    nome_cli = st.text_input('Nome')

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    cpf_cli = st.text_input('CPF')
                with col2:
                    rg_cli = st.text_input('RG')
                with col3:
                    data_nascimento_cli = st.text_input('Data de nascimento')
                with col4:
                    filiacao_cli = st.text_input('Filiação')

                col1, col2, col3 = st.columns([4,2,2])

                with col1:
                    endereco_cli = st.text_input('Endereço')
                with col2:
                    numero_cli = st.text_input('Numero')
                with col3:
                    cep_cli = st.text_input('CEP')

                col1, col2, col3 = st.columns(3)

                with col1:
                    bairro_cli = st.text_input('Bairro')
                with col2:
                    cidade_cli = st.text_input('Cidade')
                with col3:
                    estado_cli = st.text_input('Estado')

                col1, col2, col3 = st.columns(3)

                with col1:
                    complemento_cli = st.text_input('Complemento')
                with col2:
                    telefone_cli = st.text_input('Telefone')
                with col3:
                    celular_cli = st.text_input('Celular')
                
                email_cli = st.text_input('Email')
                observacao_cli = st.text_area('Observação: ', height=150)

                submit_botton_pf = st.form_submit_button(label='Cadastrar')

            if submit_botton_pf:
                if cod_cli and nome_cli and cpf_cli and rg_cli and data_nascimento_cli and filiacao_cli and endereco_cli and numero_cli and cep_cli and bairro_cli and cidade_cli and estado_cli and complemento_cli and telefone_cli and celular_cli and email_cli:
                    inserir_cliente_pf(cod_cli, nome_cli, cpf_cli, rg_cli, data_nascimento_cli, filiacao_cli, endereco_cli, numero_cli, cep_cli, bairro_cli, cidade_cli, estado_cli, complemento_cli, telefone_cli, celular_cli, email_cli, observacao_cli)
                    st.success('Cadastro de Pessoa Física realizado com sucesso!')
                else:
                    st.error('Preencha todos os campos obrigatórios.')

        if input_option == "Pessoa Jurídica":
            st.subheader("Cadastro - Pessoa Jurídica")
            with st.form(key='Cliente_form_pj'):
                col1, col2 = st.columns([2,4])

                with col1:
                    cod = st.text_input('Código', value=gerar_codigo_aleatorio())
                with col2:
                    razao_social = st.text_input('Razão Social')

                col1, col2, col3 = st.columns(3)

                with col1:
                    cnpj = st.text_input('CNPJ')
                with col2:
                    inscricao_estadual = st.text_input('Inscrição Estadual')
                with col3:
                    contato = st.text_input('Contato')

                col1, col2, col3 = st.columns([4,2,2])

                with col1:
                    endereco = st.text_input('Endereço')
                with col2:
                    numero = st.text_input('Numero')
                with col3:
                    cep = st.text_input('CEP')

                col1, col2, col3 = st.columns(3)

                with col1:
                    bairro = st.text_input('Bairro')
                with col2:
                    cidade = st.text_input('Cidade')
                with col3:
                    estado = st.text_input('Estado')

                col1, col2, col3 = st.columns(3)

                with col1:
                    complemento = st.text_input('Complemento')
                with col2:
                    telefone = st.text_input('Telefone')
                with col3:
                    celular = st.text_input('Celular')

                email = st.text_input('Email')
                observacao = st.text_area('Observação: ', height=150)

                submit_botton_pj = st.form_submit_button(label='Cadastrar')

            if submit_botton_pj:
                if cod and razao_social and cnpj and inscricao_estadual and endereco and numero and cep and bairro and cidade and estado and complemento and telefone and celular and email:
                    inserir_cliente_pj(cod, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, contato, complemento, telefone, celular, email, observacao)
                    st.success('Cadastro de Pessoa Jurídica realizado com sucesso!')
                else:
                    st.error('Preencha todos os campos obrigatórios.')

        if st.session_state.page == 'voltar':
            st.session_state.page = 'cli'
            st.rerun()

    if st.session_state.page == 'apagar_pf':
        st.write('\n')
        st.subheader('Deseja realmente apagar o cadastro deste cliente ?')

        cliente_atual = listar_clientes_pf()[st.session_state.indice_cliente]
        cliente_id = cliente_atual[0]
        nome_cli = cliente_atual[2]

        st.write(f"Código: {cliente_atual[1]}")
        st.write(f"Nome: {nome_cli}")
        st.write('\n')
        st.write('\n')

        col1, col2, col3 = st.columns([2,2,4])

        with col1:
            if st.button('Apagar', use_container_width=True):
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cadastro_cliente_pessoa_fisica WHERE id = ?", (cliente_id,))
                conn.commit()
                conn.close()

                st.success(f"Cliente {nome_cli} apagado com sucesso!")
                st.session_state.page = 'cli'
                st.rerun()

        with col2:
            if st.button('Cancelar', use_container_width=True):
                st.session_state.page = 'cli'
                st.rerun()

        with col3:
            st.write('')

    if st.session_state.page == 'apagar_pj':
        st.write('\n')
        st.subheader('Deseja realmente apagar o cadastro deste cliente ?')

        cliente_atual = listar_clientes_pj()[st.session_state.indice_cliente]
        cliente_id = cliente_atual[0]
        razao_social = cliente_atual[2]

        st.write(f"Código: {cliente_atual[1]}")
        st.write(f"Razão social: {razao_social}")
        st.write('\n')
        st.write('\n')

        col1, col2, col3 = st.columns([2,2,4])

        with col1:
            if st.button('Apagar', use_container_width=True):
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cadastro_pessoa_juridica WHERE id = ?", (cliente_id,))
                conn.commit()
                conn.close()

                st.success(f"Cliente {nome_cli} apagado com sucesso!")
                st.session_state.page = 'cli'
                st.rerun()

        with col2:
            if st.button('Cancelar', use_container_width=True):
                st.session_state.page = 'cli'
                st.rerun()

        with col3:
            st.write('')

    if st.session_state.page == 'pesq':
        tela_pesquisa_clientes()

    if st.session_state.page == 'list_pf':
        st.write('')
        st.header('Listagem de Clientes PF')

        if st.button('Voltar', use_container_width=True, key="voltar_button"):
            st.session_state.page = 'cli'
            st.rerun()

        clientes = listar_clientes_pf()

        clientes_df = pd.DataFrame(clientes, columns=["ID", "Código", "Nome", "CPF", "RG", "Endereço", "Número", "CEP", "Bairro", "Cidade", "Estado", "Complemento", "Telefone", "Celular", "Data Nascimento", "Filiação", "Email", "Observação"])
        clientes_df = clientes_df.drop(columns=['ID', 'Observação'])
        st.dataframe(clientes_df.style)
        
    if st.session_state.page == 'list_pj':
        st.write('')
        st.header('Listagem de Clientes PJ')

        if st.button('Voltar', use_container_width=True, key="voltar_button"):
            st.session_state.page = 'cli'
            st.rerun()

        clientes = listar_clientes_pj()
        
        clientes_df = pd.DataFrame(clientes, columns=["ID", "Código", "Nome da Empresa", "Endereço", "Número", "Complemento", "CEP", "Bairro", "Cidade", "Estado", "CNPJ", "Inscrição Estadual", "Telefone", "Celular", "Contato", "Email", "Observação"])
        clientes_df = clientes_df.drop(columns=['ID', 'Observação'])
        st.dataframe(clientes_df.style)

    if 'page' not in st.session_state:
        st.session_state.page == 'for'

    if st.session_state.page == 'for':
        st.write('\n')
        st.header('Fornecedores Cadastrados')

        col1, col2, col3, col4, col5, col6 = st.columns([1,1,2,2,2,2])
            
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_fornecedor > 0:
                    st.session_state.indice_fornecedor -= 1

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_fornecedor < len(listar_fornecedores()) - 1:
                    st.session_state.indice_fornecedor += 1

        with col3:
            if st.button('Incluir', use_container_width=True, key="incluir_button"):
                st.session_state.page = 'incluir_for'
                st.rerun()

        with col4:
            if st.button('Apagar', use_container_width=True, key="apagar_button"):
                st.session_state.page = 'apagar_for'
                st.rerun()

        with col5:
            if st.button('Pesquisar', use_container_width=True, key="pesquisar_button"):
                st.session_state.page = 'pesq_for'
                st.rerun()

        with col6:
            if st.button('Listagem', use_container_width=True, key="listagem_button"):
                st.session_state.page = 'list_for'
                st.rerun()

        exibir_fornecedor_atual()

    if st.session_state.page == 'incluir_for':
        st.write('')
        st.header('Cadastrar Fornecedor')

        if st.button('Voltar', use_container_width=True, key="voltar_button"):
            st.session_state.page = 'for'
            st.rerun()

        with st.form(key='Fornecedor_form'):

            col1, col2 = st.columns([2,4])

            with col1:
                cod = st.text_input ('Codigo', value=gerar_codigo_aleatorio())
            with col2:
                razao_social = st.text_input('Razão social')

            col1, col2, col3 = st.columns(3)

            with col1:
                cnpj = st.text_input('CNPJ')
            with col2:
                inscricao_estadual = st.text_input('Inscriaçao Estadual')
            with col3:
                contato = st.text_input('Contato')

            col1, col2, col3 = st.columns([4,2,2])

            with col1:
                endereco = st.text_input('Endereço')
            with col2:
                numero = st.text_input('Numero')
            with col3:
                cep = st.text_input('CEP')

            col1, col2, col3 = st.columns(3)

            with col1:
                bairro = st.text_input('Bairro')
            with col2:
                cidade = st.text_input('Cidade')
            with col3:
                estado = st.text_input('Estado')

            col1, col2 = st.columns(2)

            with col1:
                telefone = st.text_input('Telefone')
            with col2:
                celular = st.text_input('Celular')

            email_comercial = st.text_input('Email')
            observacao = st.text_area('Observação: ', height=150)

            submit_botton = st.form_submit_button(label='cadastrar')
        
        if submit_botton:
            if cod and razao_social and cnpj and inscricao_estadual and endereco and numero and cep and bairro and cidade and estado and telefone and celular and email_comercial:
                inserir_fornecedor(cod, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, telefone, celular, email_comercial, contato, observacao)
                st.success('Cadastro de Fornecedor realizado com sucesso!')
            else:
                st.error('Preencha todos os campos obrigatórios.')

    if st.session_state.page == 'apagar_for':
        st.write('\n')
        st.subheader('Deseja realmente apagar o cadastro deste fornecedor?')

        fornecedores = listar_fornecedores()
        if fornecedores and 0 <= st.session_state.indice_fornecedor < len(fornecedores):
            fornecedor_atual = fornecedores[st.session_state.indice_fornecedor]
            fornecedor_id = fornecedor_atual[0]
            nome_for = fornecedor_atual[2]

            st.write(f"Código: {fornecedor_atual[1]}")
            st.write(f"Nome: {nome_for}")
            st.write('\n')
            st.write('\n')

            col1, col2, col3 = st.columns([2, 2, 4])

            with col1:
                if st.button('Apagar', use_container_width=True):
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM cadastro_fornecedores WHERE id = ?", (fornecedor_id,))
                    conn.commit()
                    conn.close()

                    st.success(f"Fornecedor {nome_for} apagado com sucesso!")
                    st.session_state.page = 'for'
                    st.rerun()

            with col2:
                if st.button('Cancelar', use_container_width=True):
                    st.session_state.page = 'for'
                    st.rerun()

            with col3:
                st.write('')

        else:
            st.warning("Nenhum fornecedor encontrado.")

    if st.session_state.page == 'pesq_for':
        tela_pesquisa_fornecedores()
        if st.button('Voltar', use_container_width=True):
            st.session_state.page = 'for'
            st.rerun()

    if st.session_state.page == 'list_for':
        st.write('')
        st.header('Listagem de Fornecedores')

        if st.button('Voltar', use_container_width=True, key="voltar_button"):
            st.session_state.page = 'for'
            st.rerun()

        fornecedores = listar_fornecedores()

        fonecedores_df = pd.DataFrame(fornecedores, columns=["ID", "Código", "Razão Social", "Endereço", "Número", "bairro", "Cidade", "Estado", "CEP", "Telefone", "Celular", "cnpj", "Inscrição E.", "Email", "Contato", "Observação"])
        fonecedores_df = fonecedores_df.drop(columns=['ID', 'Observação'])
        st.dataframe(fonecedores_df.style)

    if st.session_state.page == 'pro':
        st.write('\n')
        st.header('Cadastrar Novo Produto')

        with st.form(key='produto_form'):

            col1, col2 = st.columns([2,4])

            with col1:
                cod = st.text_input('Codigo')
            with col2:
                descricao = st.text_input('Descrição')

            col1, col2, col3 = st.columns([2,2,1])

            with col1:
                frabricante = st.text_input('Fabricante')
            with col2:
                fornecedor = st.text_input('Fornecedor')
            with col3:
                unidade = st.text_input('Unidade')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                qtd_minima = st.text_input('Quantidade minima')
            with col2:
                custo = st.number_input('Custo', value=0.0, min_value=0.0, format="%.2f")  
            with col3:
                preco = st.number_input('Preço', value=0.0, min_value=0.0, format="%.2f")

            margem_calculada = float(calcular_margem(custo, preco))
            with col4:
                margem = st.number_input("Margem", value=margem_calculada, min_value=0.0, format="%.2f", disabled=True)
                    
            observacao_pro = st.text_input('Observação')
            
            qtd_estoque_pro = '0'

            submit_botton = st.form_submit_button(label='cadastrar')
            
            if submit_botton:
                if cod and descricao and frabricante and fornecedor and unidade and qtd_estoque_pro and custo and margem and preco and qtd_minima:
                    inserir_produto(cod, descricao, frabricante, fornecedor, unidade, qtd_estoque_pro, custo, margem, preco, observacao_pro, qtd_minima)
                else:
                    st.error('Preencha todos os campos obrigatórios.')
import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
import datetime

def conectar_db():
    return sqlite3.connect('produtos.db')

def inserir_cliente_pf(cod, nome, cpf, rg, data_nascimento, filiacao, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cadastro_cliente_pessoa_fisica (cod_cliente, nome_cliente, cpf, rg, data_nascimento, filiacao, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cod, nome, cpf, rg, data_nascimento, filiacao, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao))
    conn.commit()
    conn.close()

def inserir_cliente_pj(cod, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cadastro_cliente_pessoa_juridica (cod_cliente, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cod, razao_social, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao))
    conn.commit()
    conn.close()

def inserir_fornecedor(cod, nome_fornecedor, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fornecedores (cod_fornecedor, nome_fornecedor, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cod, nome_fornecedor, cnpj, inscricao_estadual, endereco, numero, cep, bairro, cidade, estado, complemento, telefone, celular, email, observacao))
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

def listar_clientes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cadastro_cliente_pessoa_fisica")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def exibir_cliente_atual():
    if 'indice_cliente' not in st.session_state:
        st.session_state.indice_cliente = 0

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM cadastro_cliente_pessoa_fisica WHERE id = ? ''', (st.session_state.indice_cliente + 1,))
    cliente = cursor.fetchone()
    conn.close()

    col1, col2 = st.columns([2,4])

    with col1:
        cod_cli = st.text_input('Código', cliente[1])
    with col2:
        nome_cli = st.text_input('Nome', cliente[2])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cpf_cli = st.text_input('CPF', cliente[3])
    with col2:
        rg_cli = st.text_input('RG', cliente[4])
    with col3:
        try:
            data_nascimento_cli = datetime.datetime.strptime(cliente[14], '%Y-%m-%d').date()
        except ValueError:
            data_nascimento_cli = None
        data_nascimento_cli = st.date_input('Data de nascimento', data_nascimento_cli)
    with col4:
        filiacao_cli = st.text_input('Filiação', cliente[15])

    col1, col2, col3 = st.columns([4,2,2])

    with col1:
        endereco_cli = st.text_input('Endereço', cliente[5])
    with col2:
        numero_cli = st.text_input('Numero', cliente[6])
    with col3:
        cep_cli = st.text_input('CEP', cliente[7])

    col1, col2, col3 = st.columns(3)

    with col1:
        bairro_cli = st.text_input('Bairro', cliente[8])
    with col2:
        cidade_cli = st.text_input('Cidade', cliente[9])
    with col3:
        estado_cli = st.text_input('Estado', cliente[10])

    col1, col2, col3 = st.columns(3)

    with col1:
        complemento_cli = st.text_input('Complemento', cliente[11])
    with col2:
        telefone_cli = st.text_input('Telefone', cliente[12])
    with col3:
        celular_cli = st.text_input('Celular', cliente[13])
    
    email_cli = st.text_input('Email', cliente[16])
    observacao_cli = st.text_area('Observação: ', cliente[17], height=150)

    st.write('Deseja salvar as alterações?')

    col1, col2, col3 = st.columns([1, 1, 4])

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
            UPDATE cadastro_cliente_pessoa_fisica 
            SET cod_cli = ?, nome_cli = ?, cpf_cli = ?, rg_cli = ?, endereco_cli = ?, numero_cli = ?, cep_cli = ?, bairro_cli = ?, cidade_cli = ?, estado_cli = ?, complemento_cli = ?, 
                telefone_cli = ?, celular_cli = ?, data_nascimento_cli = ?, filiacao_cli = ?, email_cli = ?, observacao_cli = ? 
            WHERE id = ?
        ''', (cod_cli, nome_cli, cpf_cli, rg_cli, endereco_cli, numero_cli, cep_cli, bairro_cli, cidade_cli, estado_cli, complemento_cli, 
                telefone_cli, celular_cli, data_nascimento_cli, filiacao_cli, email_cli, observacao_cli, st.session_state.indice_cliente + 1))
            
        conn.commit()
        conn.close()

        st.success("Cliente atualizado com sucesso!")

    elif salvar_nao:
        st.warning("Alterações não salvas.")

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

if st.session_state.page == 'cli':
    st.write('\n')
    st.header('Clientes Cadastrados')

    col1, col2, col3, col4, col5 = st.columns([1,1,2,2,2])
    
    with col1:
        if st.button("←", use_container_width=True, key="left_button"):
            if st.session_state.indice_produto > 0:
                st.session_state.indice_produto -= 1

    with col2:
        if st.button("→", use_container_width=True, key="right_button"):
            if st.session_state.indice_produto < len(listar_clientes()) - 1:
                st.session_state.indice_produto += 1

    with col3:
        if st.button('Incluir', use_container_width=True, key="incluir_button"):
            st.session_state.page = 'incluir'
            st.rerun()

    with col4:
        if st.button('Pesquisar', use_container_width=True, key="pesquisar_button"):
            st.session_state.page = 'pesq'
            st.rerun()

    with col5:
        if st.button('Listagem', use_container_width=True, key="listagem_button"):
            st.session_state.page = 'list'
            st.rerun()

    exibir_cliente_atual()

if st.session_state.page == 'incluir':
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
            st.session_state.page = 'voltar'
    
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
                data_nascimento_cli = st.date_input('Data de nascimento')
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
                cod_cli_ju = st.text_input('Código')
            with col2:
                razao_social_ju = st.text_input('Razão Social')

            col1, col2, col3 = st.columns(3)

            with col1:
                cnpj_ju = st.text_input('CNPJ')
            with col2:
                inscricao_estadual_ju = st.text_input('Inscrição Estadual')
            with col3:
                contato_ju = st.text_input('Contato')

            col1, col2, col3 = st.columns([4,2,2])

            with col1:
                endereco_ju = st.text_input('Endereço')
            with col2:
                numero_ju = st.text_input('Numero')
            with col3:
                cep_ju = st.text_input('CEP')

            col1, col2, col3 = st.columns(3)

            with col1:
                bairro_ju = st.text_input('Bairro')
            with col2:
                cidade_ju = st.text_input('Cidade')
            with col3:
                estado_ju = st.text_input('Estado')

            col1, col2, col3 = st.columns(3)

            with col1:
                complemento_ju = st.text_input('Complemento')
            with col2:
                telefone_ju = st.text_input('Telefone')
            with col3:
                celular_ju = st.text_input('Celular')

            email_ju = st.text_input('Email')
            observacao_ju = st.text_area('Observação: ', height=150)

            submit_botton_pj = st.form_submit_button(label='Cadastrar')

        if submit_botton_pj:
            if cod_cli_ju and razao_social_ju and cnpj_ju and inscricao_estadual_ju and endereco_ju and numero_ju and cep_ju and bairro_ju and cidade_ju and estado_ju and complemento_ju and telefone_ju and celular_ju and email_ju:
                inserir_cliente_pj(cod_cli_ju, razao_social_ju, cnpj_ju, inscricao_estadual_ju, endereco_ju, numero_ju, cep_ju, bairro_ju, cidade_ju, estado_ju, complemento_ju, telefone_ju, celular_ju, email_ju, observacao_ju)
                st.success('Cadastro de Pessoa Jurídica realizado com sucesso!')
            else:
                st.error('Preencha todos os campos obrigatórios.')

    if st.session_state.page == 'voltar':
        st.session_state.page = 'cli'
        st.rerun()

if st.session_state.page == 'list':
    listar_clientes()
    
if st.session_state.page == 'for':
    st.write('\n')
    st.header('CADASTRAR NOVO FORNECEDOR')

    with st.form(key='Fornecedor_form'):

        col1, col2 = st.columns([2,4])

        with col1:
            cod_for = st.text_input ('Codigo')
        with col2:
            razao_social_for = st.text_input('Razão social')

        col1, col2, col3 = st.columns(3)

        with col1:
            cnpj_for = st.text_input('CNPJ')
        with col2:
            inscricao_estadual_for = st.text_input('Inscriaçao Estadual')
        with col3:
            contato_for = st.text_input('Contato')

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            endereco_for = st.text_input('Endereço')
        with col2:
            numero_for = st.text_input('Numero')
        with col3:
            cep_for = st.text_input('CEP')

        col1, col2, col3 = st.columns(3)

        with col1:
            bairro_for = st.text_input('Bairro')
        with col2:
            cidade_for = st.text_input('Cidade')
        with col3:
            estado_for = st.text_input('Estado')

        col1, col2 = st.columns(2)

        with col1:
            telefone_for = st.text_input('Telefone')
        with col2:
            celular_for = st.text_input('Celular')

        email_comercial_for = st.text_input('Email')
        observacao_for = st.text_area('Observação: ', height=150)

        submit_botton = st.form_submit_button(label='cadastrar')
    
    if submit_botton:
        if cod_for and razao_social_for and cnpj_for and inscricao_estadual_for and endereco_for and numero_for and cep_for and bairro_for and cidade_for and estado_for and telefone_for and celular_for and email_comercial_for:
            inserir_fornecedor(cod_for, razao_social_for, cnpj_for, inscricao_estadual_for, endereco_for, numero_for, cep_for, bairro_for, cidade_for, estado_for, telefone_for, celular_for, email_comercial_for, observacao_for)
            st.success('Cadastro de Fornecedor realizado com sucesso!')
        else:
            st.error('Preencha todos os campos obrigatórios.')

if st.session_state.page == 'pro':
    st.write('\n')
    st.header('CADASTRAR NOVO PRODUTO')

    with st.form(key='produto_form'):

        col1, col2 = st.columns([2,4])

        with col1:
            cod_pro = st.text_input('Codigo')
        with col2:
            descricao_pro = st.text_input('Descrição')

        col1, col2, col3 = st.columns([2,2,1])

        with col1:
            frabricante_pro = st.text_input('Fabricante')
        with col2:
            fornecedor_pro = st.text_input('Fornecedor')
        with col3:
            unidade_pro = st.text_input('Unidade')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            qtd_estoque_pro = st.text_input('Quantidade no estoque')
        with col2:
            custo_pro = st.text_input('Custo')
        with col3:
            margem_pro = st.text_input('Margem')
        with col4:
            preco_pro = st.text_input('Preço')
        
        observacao_pro = st.text_input('Observação')
        qtd_minima_pro = st.text_input('Quantidade minima')


        submit_botton = st.form_submit_button(label='cadastrar')
        
        if submit_botton:
            if cod_pro and descricao_pro and frabricante_pro and fornecedor_pro and unidade_pro and qtd_estoque_pro and custo_pro and margem_pro and preco_pro and qtd_minima_pro:
                st.success(f'Cadastro realizado com sucesso!')
            else:
                st.error('Preencha todos os campos de informação')
            if cod_pro and descricao_pro and frabricante_pro and fornecedor_pro and unidade_pro and qtd_estoque_pro and custo_pro and margem_pro and preco_pro and qtd_minima_pro:
                inserir_produto(cod_pro, descricao_pro, frabricante_pro, fornecedor_pro, unidade_pro, qtd_estoque_pro, custo_pro, margem_pro, preco_pro, observacao_pro, qtd_minima_pro)
                st.success('Cadastro de Fornecedor realizado com sucesso!')
            else:
                st.error('Preencha todos os campos obrigatórios.')
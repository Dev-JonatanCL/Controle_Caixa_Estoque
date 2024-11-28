import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import locale
from fpdf import FPDF
import xml.etree.ElementTree as ET
import re

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

def run():

    def formatar_contabil(valor):
        return locale.currency(valor, grouping=True)

    def formatar_margem(margem):
        return "{:.2f}%".format(margem * 100/100)

    def conectar_db():
        return sqlite3.connect('banco.db')

    def pdf_listagem(produtos):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Listagem de Produtos", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 9)
        pdf.cell(28, 10, 'Código', border=1, align='C')
        pdf.cell(50, 10, 'Descrição', border=1, align='C')
        pdf.cell(23, 10, 'Fabricante', border=1, align='C')
        pdf.cell(23, 10, 'Fornecedor', border=1, align='C')
        pdf.cell(14, 10, 'Etq.', border=1, align='C')
        pdf.cell(18, 10, 'Custo', border=1, align='C')
        pdf.cell(18, 10, 'Margem', border=1, align='C')
        pdf.cell(18, 10, 'Preço', border=1, align='C')
        pdf.ln()

        pdf.set_font("Arial", size=9)
        
        for produto in produtos:
            pdf.cell(28, 10, str(produto[1]), border=1, align='C')
            pdf.cell(50, 10, produto[2], border=1, align='C')
            pdf.cell(23, 10, produto[3], border=1, align='C')
            pdf.cell(23, 10, produto[4], border=1, align='C')
            pdf.cell(14, 10, str(produto[6]), border=1, align='C')
            pdf.cell(18, 10, f"R$ {produto[7]:,.2f}", border=1, align='C')
            pdf.cell(18, 10, f"{produto[8]:.2f}%", border=1, align='C')
            pdf.cell(18, 10, f"R$ {produto[9]:,.2f}", border=1, align='C')
            pdf.ln()

        pdf_output = pdf.output(dest='S').encode('latin1')

        return pdf_output

    def pdf_pedido(produtos):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Pedido de Compra", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 9)
        pdf.cell(20, 10, 'Qtd. a Pedir', border=1, align='C')
        pdf.cell(30, 10, 'Código', border=1, align='C')
        pdf.cell(50, 10, 'Descrição', border=1, align='C')
        pdf.cell(25, 10, 'Fabricante', border=1, align='C')
        pdf.cell(25, 10, 'Fornecedor', border=1, align='C')
        pdf.cell(20, 10, 'Custo', border=1, align='C')
        pdf.cell(20, 10, 'Total Custo', border=1, align='C')
        pdf.ln()

        pdf.set_font("Arial", size=9)

        total_custo = 0
        
        for produto in produtos:
            qtd_minima = produto[11]
            qtd_estoque = produto[6]
            qtd_a_pedir = max(0, qtd_minima - qtd_estoque)
            custo_produto = produto[7]
            total_produto = qtd_a_pedir * custo_produto

            total_custo += total_produto
            
            pdf.cell(20, 10, str(qtd_a_pedir), border=1, align='C')
            pdf.cell(30, 10, str(produto[1]), border=1, align='C')
            pdf.cell(50, 10, produto[2], border=1, align='C')
            pdf.cell(25, 10, produto[3], border=1, align='C')
            pdf.cell(25, 10, produto[4], border=1, align='C')
            pdf.cell(20, 10, f"R$ {produto[7]:,.2f}", border=1, align='C')
            pdf.cell(20, 10, f"R$ {total_produto:,.2f}", border=1, align='C')
            pdf.ln()

        pdf.set_font("Arial", 'B', 9)
        pdf.cell(170, 10, "Total de Custo", border=1, align='R')
        pdf.cell(20, 10, f"R$ {total_custo:,.2f}", border=1, align='C')

        pdf_output = pdf.output(dest='S').encode('latin1')

        return pdf_output

    def listar_produtos():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()
        conn.close()
        return produtos

    def listar_produtos_abaixo_minimo(fornecedor):
        conn = conectar_db()
        cursor = conn.cursor()
        if fornecedor:
            cursor.execute('''
                SELECT * FROM produtos
                WHERE qtd_estoque < qtd_minima
                AND (fornecedor LIKE ?)
            ''', ('%' + fornecedor + '%',))
        else:
            cursor.execute("SELECT * FROM produtos WHERE qtd_estoque < qtd_minima")
        
        produtos = cursor.fetchall()
        conn.close()
        return produtos

    def calcular_margem(custo, preco):
        if preco != 0:
            return ((preco - custo) / custo) * 100
        return 0

    def pesquisar_produtos(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE descricao LIKE ? OR cod LIKE ?", ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        produtos = cursor.fetchall()
        conn.close()
        return produtos

    def pesquisar_fornecedor():
        fornecedor_input = st.text_input("Digite o código ou nome do fornecedor:")

        if not fornecedor_input:
            st.error("Por favor, insira o código ou nome do fornecedor.")
            return None

        conn = conectar_db()
        cursor = conn.cursor()

        if fornecedor_input.isdigit():
            cursor.execute('SELECT cod_fornecedor, nome_fornecedor FROM cadastro_fornecedores WHERE cod_fornecedor = ?', (fornecedor_input,))
        else:
            cursor.execute('SELECT cod_fornecedor, nome_fornecedor FROM cadastro_fornecedores WHERE nome_fornecedor LIKE ?', ('%' + fornecedor_input + '%',))

        fornecedor = cursor.fetchone()
        conn.close()

        if fornecedor:
            return fornecedor
        else:
            st.error(f"Fornecedor não encontrado. '{fornecedor_input}'.")
            return None

    def processar_xml_nfe():
        st.header("Entrada de NF-e")
        
        arquivo_xml = st.file_uploader("Envie o arquivo XML da NF-e", type="xml")
        
        if arquivo_xml is not None:
            try:
                conteudo_xml = arquivo_xml.read().decode("utf-8")
                tree = ET.ElementTree(ET.fromstring(conteudo_xml))
                root = tree.getroot()
                
                ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

                cnpj_fornecedor = root.find('.//nfe:emit/nfe:CNPJ', ns).text
                cnpj_fornecedor = re.sub(r'\D', '', cnpj_fornecedor)
                nome_fornecedor = root.find('.//nfe:emit/nfe:xNome', ns).text
                endereco = root.find('.//nfe:enderEmit/nfe:xLgr', ns).text
                numero = root.find('.//nfe:enderEmit/nfe:nro', ns).text
                bairro = root.find('.//nfe:enderEmit/nfe:xBairro', ns).text
                cidade = root.find('.//nfe:enderEmit/nfe:xMun', ns).text
                estado = root.find('.//nfe:enderEmit/nfe:UF', ns).text
                cep = root.find('.//nfe:enderEmit/nfe:CEP', ns).text
                telefone = root.find('.//nfe:enderEmit/nfe:fone', ns).text if root.find('.//nfe:enderEmit/nfe:fone', ns) is not None else None
                inscricao_estadual = root.find('.//nfe:emit/nfe:IE', ns).text if root.find('.//nfe:emit/nfe:IE', ns) is not None else None
                contato = "Desconhecido"

                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("SELECT cod_fornecedor FROM cadastro_fornecedores WHERE REPLACE(REPLACE(REPLACE(cnpj, '.', ''), '/', ''), '-', '') = ?", (cnpj_fornecedor,))
                fornecedor = cursor.fetchone()

                if fornecedor:
                    cod_fornecedor = fornecedor[0]
                else:
                    cursor.execute(''' 
                        INSERT INTO cadastro_fornecedores (cod_fornecedor, nome_fornecedor, endereco, numero, bairro, cidade, estado, cep, telefone, celular, cnpj, inscricao_estadual, email, contato, observacao)
                        VALUES ((SELECT COALESCE(MAX(cod_fornecedor), 0) + 1 FROM cadastro_fornecedores), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome_fornecedor, endereco, numero, bairro, cidade, estado, cep, telefone, None, cnpj_fornecedor, inscricao_estadual, None, contato, None))
                    conn.commit()
                    cursor.execute("SELECT cod_fornecedor FROM cadastro_fornecedores WHERE REPLACE(REPLACE(REPLACE(cnpj, '.', ''), '/', ''), '-', '') = ?", (cnpj_fornecedor,))
                    cod_fornecedor = cursor.fetchone()[0]
                    st.write(f"Fornecedor {nome_fornecedor} cadastrado com sucesso!")

                for det in root.findall('.//nfe:det', ns):
                    cod_produto = det.find('.//nfe:prod/nfe:cProd', ns).text
                    descricao = det.find('.//nfe:prod/nfe:xProd', ns).text
                    unidade = det.find('.//nfe:prod/nfe:uCom', ns).text
                    qtd_estoque = int(float(det.find('.//nfe:prod/nfe:qCom', ns).text))
                    custo = float(det.find('.//nfe:prod/nfe:vUnCom', ns).text)
                    margem = 0.3 
                    preco = custo * (1 + margem)
                    observacao = "Cadastrado via XML"

                    cursor.execute("SELECT id FROM produtos WHERE cod = ?", (cod_produto,))
                    produto = cursor.fetchone()

                    if produto:
                        cursor.execute(''' 
                            UPDATE produtos
                            SET qtd_estoque = qtd_estoque + ?, custo = ?
                            WHERE cod = ?
                        ''', (qtd_estoque, custo, cod_produto))
                        st.write(f"Produto {cod_produto} atualizado no estoque.")
                    else:
                        cursor.execute(''' 
                            INSERT INTO produtos (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (cod_produto, descricao, nome_fornecedor, nome_fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, 10))
                        st.write(f"Produto {cod_produto} cadastrado com sucesso!")

                numero_documento = root.find('.//nfe:ide/nfe:nNF', ns).text
                data_entrada = root.find('.//nfe:ide/nfe:dhEmi', ns).text[:10]

                for dup in root.findall('.//nfe:dup', ns):
                    parcela = int(dup.find('nfe:nDup', ns).text.split('/')[-1])
                    vencimento = dup.find('nfe:dVenc', ns).text
                    valor = float(dup.find('nfe:vDup', ns).text)

                    cursor.execute(''' 
                        INSERT INTO contas_a_pagar (cod_fornecedor, nome_fornecedor, data_entrada, vencimento, numero_documento, parcela, valor)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (cod_fornecedor, nome_fornecedor, data_entrada, vencimento, numero_documento, parcela, valor))
                    st.write(f"Parcela {parcela} inserida com vencimento em {vencimento} e valor R$ {valor:.2f}.")

                conn.commit()
                conn.close()
                st.success("NF-e processada com sucesso!")

            except Exception as e:
                st.error(f"Erro ao processar o XML: {e}")

    def exibir_produto_atual():
        if 'indice_produto' not in st.session_state:
            st.session_state.indice_produto = 0

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM produtos LIMIT 1 OFFSET ? ''', (st.session_state.indice_produto,))
        produto = cursor.fetchone()
        conn.close()

        if produto is None:
            st.warning("Não há produtos cadastrados.")
            return

        col1, col2 = st.columns([2,5])

        with col1:
            cod = st.text_input("Código", produto[1])
        with col2:
            descricao = st.text_input("Descrição", produto[2])

        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            fabricante = st.text_input("Fabricante", produto[3])
        with col2:
            fornecedor = st.text_input("Fornecedor", produto[4])
        with col3:
            unidade = st.text_input("Unidade", produto[5])
        with col4:
            qtd_minima = st.number_input("Quantidade mínima", value=produto[11], min_value=0)
        with col5:
            qtd_estoque = st.number_input("Quantidade atual", value=produto[6], min_value=0)

        col1, col2, col3 = st.columns(3)

        with col1:    
            custo = st.number_input("Custo", value=produto[7], min_value=0.0, format="%.2f")
        with col2:
            margem_calculada = calcular_margem(custo, produto[9])
            margem = st.number_input("Margem", value=margem_calculada, min_value=0.0, format="%.2f", disabled=True)
        with col3:
            preco = st.number_input("Preço", value=produto[9], min_value=0.0, format="%.2f")

        observacao = st.text_area("Observação: ", produto[10], height=150)

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE produtos
                SET cod = ?, descricao = ?, fabricante = ?, fornecedor = ?, unidade = ?, qtd_estoque = ?, custo = ?, margem = ?, preco = ?, observacao = ?, qtd_minima = ?
                WHERE id = ?
            ''', (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima, produto[0]))
            conn.commit()
            conn.close()

            st.success("Produto atualizado com sucesso!")  

    def exibir_resultados_pesquisa(produtos):
        if not produtos:
            st.warning("Nenhum produto encontrado.")
            return

        if st.session_state.indice_produto >= len(produtos):
            st.session_state.indice_produto = 0
        elif st.session_state.indice_produto < 0:
            st.session_state.indice_produto = len(produtos) - 1

        produto_atual = produtos[st.session_state.indice_produto]
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_produto > 0:
                    st.session_state.indice_produto -= 1
                    st.rerun()

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_produto < len(produtos) - 1:
                    st.session_state.indice_produto += 1
                    st.rerun()
        
        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'Etq'
                st.rerun()

        col1, col2 = st.columns([2, 5])
        with col1:
            cod = st.text_input("Código", produto_atual[1], key=f"codigo_{produto_atual[0]}")
        with col2:
            descricao = st.text_input("Descrição", produto_atual[2], key=f"descricao_{produto_atual[0]}")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            fabricante = st.text_input("Fabricante", produto_atual[3], key=f"fabricante_{produto_atual[0]}")
        with col2:
            fornecedor = st.text_input("Fornecedor", produto_atual[4], key=f"fornecedor_{produto_atual[0]}")
        with col3:
            unidade = st.text_input("Unidade", produto_atual[5], key=f"unidade_{produto_atual[0]}")
        with col4:
            qtd_minima = st.number_input("Quantidade mínima", value=produto_atual[11], min_value=0, key=f"qtd_minima_{produto_atual[0]}")
        with col5:
            qtd_estoque = st.number_input("Quantidade atual", value=produto_atual[6], min_value=0, key=f"qtd_estoque_{produto_atual[0]}")

        col1, col2, col3 = st.columns(3)
        with col1:    
            custo = st.number_input("Custo", value=produto_atual[7], min_value=0.0, format="%.2f", key=f"custo_{produto_atual[0]}")
        with col2:
            preco = st.number_input("Preço", value=produto_atual[9], min_value=0.0, format="%.2f", key=f"preco_{produto_atual[0]}")
        with col3:
            margem_calculada = calcular_margem(custo, preco)
            margem = st.number_input("Margem", value=margem_calculada, min_value=0.0, format="%.2f", disabled=True, key=f"margem_{produto_atual[0]}")

        observacao = st.text_area("Observação", produto_atual[10], height=150, key=f"observacao_{produto_atual[0]}")

        if st.button('Salvar Alterações', use_container_width=True, key=f"salvar_{produto_atual[0]}"):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE produtos
                SET cod = ?, descricao = ?, fabricante = ?, fornecedor = ?, unidade = ?, qtd_estoque = ?, custo = ?, preco = ?, margem = ?, observacao = ?, qtd_minima = ?
                WHERE id = ?
            ''', (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, preco, margem, observacao, qtd_minima, produto_atual[0]))
            conn.commit()
            conn.close()
            st.success("Produto atualizado com sucesso!")

    def tela_pesquisa():
        st.subheader("Pesquisar Produtos")

        pesquisa = st.text_input("Digite o código ou descrição do produto")
        if pesquisa:
            produtos_encontrados = pesquisar_produtos(pesquisa)
            exibir_resultados_pesquisa(produtos_encontrados)

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

        col1, col2, col3, col4, col5 = st.columns([1,1,2,2,2])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_produto > 0:
                    st.session_state.indice_produto -= 1

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_produto < len(listar_produtos()) - 1:
                    st.session_state.indice_produto += 1
        
        with col3:
            if st.button('Apagar', use_container_width=True, key="apagar_button"):
                st.session_state.page = 'apagar'
                st.rerun()

        with col4:
            if st.button('Pesquisar', use_container_width=True, key="pesquisar_button"):
                st.session_state.page = 'pesq'
                st.rerun()

        with col5:
            if st.button('Listagem', use_container_width=True, key="listagem_button"):
                st.session_state.page = 'list'
                st.rerun()

        exibir_produto_atual()

    if st.session_state.page == 'list':    
        st.write('\n')
        st.subheader('Listagem de Produtos')

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            produtos = listar_produtos()
            pdf_file = pdf_listagem(produtos)
            st.download_button(
                label="Imprimir", use_container_width=True,
                data=pdf_file,
                file_name="listagem_produtos.pdf",
                mime="application/pdf"
            )
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
        produtos_df = pd.DataFrame(produtos, columns=["ID", "Código", "Descrição", "Fabricante", "Fornecedor", "Unidade", "Quantidade atual", "Custo", "Margem", "Preço", "Observação", "Quantidade mínima"])
        produtos_df = produtos_df.drop(columns=['ID', 'Observação', 'Quantidade mínima'])

        produtos_df['Custo'] = produtos_df['Custo'].apply(lambda x: formatar_contabil(x))
        produtos_df['Preço'] = produtos_df['Preço'].apply(lambda x: formatar_contabil(x))
        produtos_df['Margem'] = produtos_df['Margem'].apply(lambda x: formatar_margem(x))

        st.dataframe(produtos_df.style)

    if st.session_state.page == 'pesq':
        tela_pesquisa()

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

    if st.session_state.page == 'PedC':
        st.write('\n')
        st.subheader('Pedido de Compra')

        col1, col2 = st.columns([2,4])

        st.write('\n')
        pesquisa_fornecedor = st.text_input("Insira o código ou a descrição do Fornecedor: ")

        with col1:
            if pesquisa_fornecedor:
                produtos = listar_produtos_abaixo_minimo(pesquisa_fornecedor)
            else:
                produtos = listar_produtos_abaixo_minimo(None)

            pdf_file = pdf_pedido(produtos)

            st.download_button(
                key='imp_pedido',
                label="Imprimir", use_container_width=True,
                data=pdf_file,
                file_name="pedido.pdf",
                mime="application/pdf"
            )
            
        with col2:
            st.write('')
        
        if produtos:

            produtos_df = pd.DataFrame(produtos, columns=["ID", "Código", "Descrição", "Fabricante", "Fornecedor", "Unidade", "Quantidade atual", "Custo", "Margem", "Preço", "Observação", "Quantidade mínima"])
            produtos_df = produtos_df.drop(columns=['ID', 'Observação', 'Margem', 'Preço'])

            produtos_df['Qtd. a Pedir'] = produtos_df.apply(
                lambda row: max(0, row['Quantidade mínima'] - row['Quantidade atual']), axis=1
            )

            produtos_df['Custo'] = produtos_df['Custo'].apply(lambda x: formatar_contabil(x))

            st.dataframe(produtos_df.style)

    if st.session_state.page == 'Ent':
        processar_xml_nfe()

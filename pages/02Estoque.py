import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import locale
from fpdf import FPDF
import xml.etree.ElementTree as ET

locale.setlocale(locale.LC_ALL, 'portuguese')

def exibir_data_atual():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"<h1 style='text-align: left;'>{data_atual}</h1>", unsafe_allow_html=True)

def formatar_contabil(valor):
    return locale.currency(valor, grouping=True)

def formatar_margem(margem):
    return "{:.2f}%".format(margem * 100/100)

def conectar_db():
    return sqlite3.connect('produtos.db')

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

def entrada_nfe(conteudo_xml, fornecedor):
    if fornecedor is None:
        st.error("Fornecedor não encontrado. Verifique a pesquisa e tente novamente.")
        return

    cod_fornecedor, nome_fornecedor = fornecedor

    conn = conectar_db()
    cursor = conn.cursor()

    tree = ET.ElementTree(ET.fromstring(conteudo_xml))
    root = tree.getroot()

    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    for dup in root.findall('.//nfe:dup', ns):
        numero_documento = root.find('.//nfe:ide/nfe:nNF', ns).text
        data_entrada = root.find('.//nfe:ide/nfe:dhEmi', ns).text[:10]
        vencimento = dup.find('nfe:dVenc', ns).text
        parcela = int(dup.find('nfe:nDup', ns).text.split('/')[-1])
        valor = float(dup.find('nfe:vDup', ns).text)

        cursor.execute(''' 
            INSERT INTO contas_a_pagar (cod_fornecedor, nome_fornecedor, data_entrada, vencimento, numero_documento, parcela, valor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cod_fornecedor, nome_fornecedor, data_entrada, vencimento, numero_documento, parcela, valor))

        st.write(f"Parcela {parcela} inserida com vencimento em {vencimento} e valor de R$ {valor:.2f}.")

    for det in root.findall('.//nfe:det', ns):
        cod_produto = det.find('.//nfe:prod/nfe:cProd', ns).text
        descricao_produto = det.find('.//nfe:prod/nfe:xProd', ns).text
        fabricante_produto = det.find('.//nfe:prod/nfe:xFab', ns).text if det.find('.//nfe:prod/nfe:xFab', ns) is not None else "Desconhecido"
        unidade_produto = int(float(det.find('.//nfe:prod/nfe:uCom', ns).text)) if det.find('.//nfe:prod/nfe:uCom', ns) is not None else 1
        quantidade = int(float(det.find('.//nfe:prod/nfe:qCom', ns).text))
        valor_unitario = float(det.find('.//nfe:prod/nfe:vUnCom', ns).text)
        observacao = "Produto adicionado automaticamente via XML."
        margem_lucro = 0.3
        preco_venda = valor_unitario * (1 + margem_lucro)
        qtd_minima = 10

        cursor.execute('SELECT cod FROM produtos WHERE cod = ?', (cod_produto,))
        produto_existente = cursor.fetchone()

        if produto_existente:
            cursor.execute(''' 
                UPDATE produtos
                SET qtd_estoque = qtd_estoque + ?, custo = ?
                WHERE cod = ?
            ''', (quantidade, valor_unitario, cod_produto))
            st.write(f"Produto {cod_produto} atualizado com {quantidade} unidades no estoque.")
        else:
            cursor.execute('''
                INSERT INTO produtos (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cod_produto, descricao_produto, fabricante_produto, nome_fornecedor, unidade_produto, quantidade, valor_unitario, margem_lucro, preco_venda, observacao, qtd_minima))
            st.write(f"Produto {cod_produto} cadastrado com {quantidade} unidades, custo de R$ {valor_unitario:.2f}, e preço de venda de R$ {preco_venda:.2f}.")

    conn.commit()
    conn.close()

    st.success("Entrada de NF-e realizada com sucesso!")

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
            SET cod = ?, descricao = ?, fabricante = ?, fornecedor = ?, unidade = ?, qtd_estoque = ?, custo = ?, margem = ?, preco = ?, observacao = ?, qtd_minima = ?
            WHERE id = ?
        ''', (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima, produto[0]))
        conn.commit()
        conn.close()

        st.success("Produto atualizado com sucesso!")

    elif salvar_nao:
        st.warning("Alterações não salvas.")      

def exibir_resultados_pesquisa(produtos):
    if len(produtos) > 0:
        for produto in produtos:
            produtos_df = pd.DataFrame(produtos, columns=["ID", "Código", "Descrição", "Fabricante", "Fornecedor", "Unidade", "Quantidade atual", "Custo", "Margem", "Preço", "Observação", "Quantidade mínima"])
            produtos_df = produtos_df.drop(columns=['ID'])
            produtos_df = produtos_df.drop(columns=['Observação'])
            produtos_df = produtos_df.drop(columns=['Quantidade mínima'])
            produtos_df['Custo'] = produtos_df['Custo'].apply(lambda x: formatar_contabil(x))
            produtos_df['Preço'] = produtos_df['Preço'].apply(lambda x: formatar_contabil(x))
            produtos_df['Margem'] = produtos_df['Margem'].apply(lambda x: formatar_margem(x))
            st.dataframe(produtos_df. style)
    else:
        st.write("Nenhum produto encontrado.")

def tela_pesquisa():
    st.subheader("Pesquisar Produtos")

    pesquisa = st.text_input("Digite o código ou descrição do produto")

    if pesquisa:
        if st.button("Pesquisar"):
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
    if st.button('Voltar', use_container_width=True):
        st.session_state.page = 'Etq'
        st.rerun()

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

    col1, col2, col3 = st.columns([2,2,4])

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
        st.button('Enviar por Email', use_container_width=True, key='ev_email')

    with col3:
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
    st.header('Entrada')
    exibir_data_atual()
    st.subheader("Entrada de NF-e com XML")

    pesquisar_fornecedor()

    input_option = st.radio("Escolha como deseja inserir o XML:", ("Carregar arquivo", "Digitar manualmente"))

    if input_option == "Carregar arquivo":
        uploaded_file = st.file_uploader("Carregue o arquivo XML da NF-e", type=["xml"])
        if uploaded_file is not None:
            conteudo_xml = uploaded_file.read().decode("utf-8")
            fornecedor = pesquisar_fornecedor()
            if fornecedor:
                entrada_nfe(conteudo_xml, fornecedor)

    elif input_option == "Digitar manualmente":
        conteudo_xml = st.text_area("Cole o conteúdo do XML da NF-e aqui:")
        if conteudo_xml:
            fornecedor = pesquisar_fornecedor()
            if fornecedor:
                entrada_nfe(conteudo_xml, fornecedor)



    

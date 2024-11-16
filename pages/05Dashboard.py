import streamlit as st
import sqlite3
import xml.etree.ElementTree as ET

def conectar_db():
    return sqlite3.connect('produtos.db')

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
        st.error(f"Fornecedor não encontrado com o código ou nome '{fornecedor_input}'.")
        return None

def entrada_nfe(conteudo_xml, fornecedor):
    if fornecedor is None:
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
        quantidade = int(det.find('.//nfe:prod/nfe:qCom', ns).text)
        valor_unitario = float(det.find('.//nfe:prod/nfe:vUnCom', ns).text)
        total_produto = float(det.find('.//nfe:prod/nfe:vProd', ns).text)

        cursor.execute(''' 
            UPDATE produtos
            SET qtd_estoque = qtd_estoque + ?
            WHERE cod = ?
        ''', (quantidade, cod_produto))

        cursor.execute(''' 
            UPDATE produtos
            SET custo = ?
            WHERE cod = ?
        ''', (valor_unitario, cod_produto))

        st.write(f"Produto {cod_produto} atualizado com {quantidade} unidades no estoque.")

    conn.commit()
    conn.close()

    st.success("Entrada de NF-e realizada com sucesso!")


if st.session_state.page == 'Ent':
    st.header('Entrada')
    st.subheader("Entrada de NF-e com XML")

    uploaded_file = st.file_uploader("Carregue o arquivo XML da NF-e", type=["xml"])

    if uploaded_file is not None:
        conteudo_xml = uploaded_file.read().decode("utf-8")
        entrada_nfe(conteudo_xml)
        
    fornecedor = pesquisar_fornecedor()
    if fornecedor:
        entrada_nfe(conteudo_xml, fornecedor)


xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
    <infNFe>
        <ide>
            <nNF>12345</nNF>
            <dhEmi>2024-11-16T12:30:00-03:00</dhEmi>
        </ide>
        <det nItem="1">
            <prod>
                <cProd>001</cProd>
                <xProd>Produto A</xProd>
                <uCom>10</uCom>
                <qCom>5</qCom>
                <vUnCom>50.00</vUnCom>
                <vProd>250.00</vProd>
            </prod>
        </det>
        <det nItem="2">
            <prod>
                <cProd>002</cProd>
                <xProd>Produto B</xProd>
                <uCom>1</uCom>
                <qCom>3</qCom>
                <vUnCom>30.00</vUnCom>
                <vProd>90.00</vProd>
            </prod>
        </det>
        <cobr>
            <dup>
                <nDup>001/1</nDup>
                <dVenc>2024-12-01</dVenc>
                <vDup>250.00</vDup>
            </dup>
            <dup>
                <nDup>002/1</nDup>
                <dVenc>2024-12-15</dVenc>
                <vDup>90.00</vDup>
            </dup>
        </cobr>
    </infNFe>
</NFe>'''

with open("exemplo_nfe.xml", "w", encoding="utf-8") as file:
    file.write(xml_content)

print("Arquivo XML 'exemplo_nfe.xml' criado com sucesso.")

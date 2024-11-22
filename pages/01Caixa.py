import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import random

def exibir_data_atual():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"<h1 style='text-align: left;'>{data_atual}</h1>", unsafe_allow_html=True)

def conectar_db():
    return sqlite3.connect('banco.db')

def listar_venda():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM venda")
    venda = cursor.fetchall()
    conn.close()
    return venda

def listar_itens_venda():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM itens_venda")
    itens_venda = cursor.fetchall()
    conn.close()
    return itens_venda

def buscar_produto():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM produtos ''')
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def buscar_clientes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cod_cliente, nome_cliente, 'Pessoa Física' AS tipo 
        FROM cadastro_cliente_pessoa_fisica
    ''')

    clientes_pf = cursor.fetchall()

    cursor.execute('''
        SELECT cod_cliente, nome_empresa AS nome_cliente, 'Pessoa Jurídica' AS tipo 
        FROM cadastro_pessoa_juridica
    ''')

    clientes_pj = cursor.fetchall()
    clientes = clientes_pf + clientes_pj
    conn.close() 

    clientes.sort(key=lambda cliente: cliente[1])
    return clientes

def gerar_numero_orcamento():
    return f"ORC-{random.randint(1000, 9999)}"

def cabecalho():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Abertura / Fechamento", use_container_width=True):
            if 'caixa_aberto' not in st.session_state or not st.session_state.caixa_aberto:
                st.session_state.page = "Ab/Fc"
            else:
                st.session_state.page = "FecharCaixa"
    with col2:
        if st.button("Efetuar Venda", use_container_width=True):
            st.session_state.page = "Venda"
    with col3:
        if st.button("Orçamentos", use_container_width=True):
            st.session_state.page = "Orc"
    with col4:
        if st.button("Listagem de Vendas", use_container_width=True):
            st.session_state.page = "ListV"

def abrir_caixa(valor_digitado, valor_troco):
    data_atual = datetime.today().strftime('%Y-%m-%d')
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    valor_final = valor_digitado
    troco_final = valor_troco
    
    cursor.execute('''INSERT INTO caixa (data, valor_inicial, troco_inicial, valor_final, troco_final, valor_sangria) 
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                   (data_atual, valor_digitado, valor_troco, valor_final, troco_final, 0.0))
    conn.commit()
    
    st.session_state.valor_digitado = valor_digitado
    st.session_state.valor_troco = valor_troco
    st.session_state.sangria = 0.0
    st.session_state.vendas_em_dinheiro = 0.0
    st.session_state.page = 'FecharCaixa'
    st.session_state.caixa_aberto = True

def registrar_venda(valor_total, tipo_recebimento, cod_cliente, nome_cliente, frete):
    data_atual = datetime.today().strftime('%d-%m-%y')

    conn = conectar_db()
    cursor = conn.cursor() 
    cursor.execute('''INSERT INTO venda (data, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete) 
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (data_atual, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete))
    conn.commit()
    
    if tipo_recebimento == 'dinheiro':
        st.session_state.vendas_em_dinheiro += valor_total
        cursor.execute('SELECT * FROM caixa WHERE data = ? ORDER BY id DESC LIMIT 1', (data_atual,))
        caixa_aberto = cursor.fetchone()
        if caixa_aberto:
            novo_valor_final = caixa_aberto[4] - valor_total
            cursor.execute('''UPDATE caixa SET valor_final = ? WHERE id = ?''', (novo_valor_final, caixa_aberto[0]))
            conn.commit()
            
            st.session_state.valor_digitado = novo_valor_final

def registrar_item_venda(id_venda, id_produto, quantidade, preco_unitario, valor_total):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario, valor_total)
        VALUES (?, ?, ?, ?, ?)
    ''', (id_venda, id_produto, quantidade, preco_unitario, valor_total))
    conn.commit()
    conn.close()

def finalizar_caixa(valor_em_caixa):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM caixa WHERE data = ? ORDER BY id DESC LIMIT 1', (datetime.today().strftime('%Y-%m-%d'),))
    caixa_aberto = cursor.fetchone()

    if caixa_aberto:
        valor_inicial = float(caixa_aberto[2])
        troco_inicial = float(caixa_aberto[3])
        valor_final = float(caixa_aberto[4])
        troco_final = float(caixa_aberto[5])
        valor_sangria = float(caixa_aberto[6]) 

        st.write(f"Fechamento de caixa realizado com os valores abaixo:")
        st.write(f"Valor inicial em caixa: R${valor_inicial:.2f}")
        st.write(f"Troco inicial: R${troco_inicial:.2f}")
        st.write(f"Valor das vendas em dinheiro: R${st.session_state.vendas_em_dinheiro:.2f}")
        st.write(f"Sangria realizada: R${valor_sangria:.2f}")
        st.write(f"Troco final: R${troco_final:.2f}")
        st.write(f"Total em caixa: R${valor_final:.2f}")

        cursor.execute('''UPDATE caixa SET valor_final = ?, troco_final = ? WHERE id = ?''',
                       (valor_final, troco_final, caixa_aberto[0]))
        conn.commit()

        st.session_state.caixa_aberto = False

    st.session_state.page = 'Ab/Fc'

def efetuar_sangria(valor_sangria):
    data_atual = datetime.today().strftime('%d-%m-%y')

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM caixa WHERE data = ? ORDER BY id DESC LIMIT 1', (data_atual,))
    caixa_aberto = cursor.fetchone()

    if caixa_aberto:
        valor_final_atual = caixa_aberto[4]
        valor_sangria_atual = caixa_aberto[5]

        novo_valor_final = valor_final_atual - valor_sangria
        novo_valor_sangria = valor_sangria_atual + valor_sangria

        cursor.execute('''UPDATE caixa SET valor_final = ?, valor_sangria = ? WHERE id = ?''', 
                       (novo_valor_final, novo_valor_sangria, caixa_aberto[0]))
        conn.commit()

        st.session_state.valor_digitado = novo_valor_final
        st.session_state.sangria = novo_valor_sangria

def adicionar_troco(valor_troco):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM caixa WHERE data = ? ORDER BY id DESC LIMIT 1', (datetime.today().strftime('%Y-%m-%d'),))
    caixa_aberto = cursor.fetchone()

    if caixa_aberto:
        valor_final_atual = caixa_aberto[4]
        troco_final_atual = caixa_aberto[5]

        novo_valor_final = valor_final_atual + valor_troco
        novo_troco_final = troco_final_atual - valor_troco
        
        cursor.execute('''UPDATE caixa SET valor_final = ?, troco_final = ? WHERE id = ?''', 
                       (novo_valor_final, novo_troco_final, caixa_aberto[0]))
        conn.commit()

        st.session_state.valor_digitado = novo_valor_final
        st.session_state.valor_troco = novo_troco_final
        st.write(f"Troco adicionado ao caixa: R${valor_troco:.2f}")

def guardar_troco(valor_guardado):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM caixa WHERE data = ? ORDER BY id DESC LIMIT 1', (datetime.today().strftime('%Y-%m-%d'),))
    caixa_aberto = cursor.fetchone()

    if caixa_aberto:
        valor_final_atual = caixa_aberto[4]
        troco_final_atual = caixa_aberto[5]

        novo_valor_final = valor_final_atual - valor_guardado
        novo_troco_final = troco_final_atual + valor_guardado
        
        cursor.execute('''UPDATE caixa SET valor_final = ?, troco_final = ? WHERE id = ?''',
                       (novo_valor_final, novo_troco_final, caixa_aberto[0]))
        conn.commit()

        st.session_state.valor_digitado = novo_valor_final
        st.session_state.valor_troco = novo_troco_final
        st.write(f"Troco guardado: R${valor_guardado:.2f}")

def exibir_venda_atual():
    if 'indice_venda' not in st.session_state:
        st.session_state.indice_venda = 0

    # Conexão com o banco e obtenção dos dados da venda
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM venda LIMIT 1 OFFSET ?
    ''', (st.session_state.indice_venda,))
    venda = cursor.fetchone()

    if venda is None:
        st.warning("Não há vendas cadastradas.")
        conn.close()
        return

    # Obtenção dos itens da venda
    cursor.execute('''
        SELECT iv.id, iv.id_produto, p.descricao, iv.quantidade, iv.preco_unitario, iv.valor_total
        FROM itens_venda iv
        JOIN produtos p ON iv.id_produto = p.id
        WHERE iv.id_venda = ?
    ''', (venda[0],))
    itens_venda = cursor.fetchall()
    conn.close()

    # Exibição dos dados da venda
    st.write("### Detalhes da Venda")
    col1, col2, col3 = st.columns(3)

    with col1:
        data = st.text_input("Data", venda[1])
    with col2:
        tipo_recebimento = st.text_input("Tipo de Recebimento", venda[2])
    with col3:
        valor_total = st.number_input("Valor Total", value=venda[3], min_value=0.0, format="%.2f")

    col1, col2 = st.columns(2)

    with col1:
        cod_cliente = st.text_input("Código do Cliente", venda[4])
    with col2:
        nome_cliente = st.text_input("Nome do Cliente", venda[5])

    col1, col2 = st.columns(2)

    with col1:
        frete = st.number_input("Valor do Frete", value=venda[6], min_value=0.0, format="%.2f")

    # Exibição dos itens da venda
    st.write("### Itens da Venda")
    if itens_venda:
        df_itens = pd.DataFrame(itens_venda, columns=["ID", "ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"])
        st.table(df_itens[["ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"]])
    else:
        st.warning("Nenhum item associado a esta venda.")

    # Botão para salvar alterações
    if st.button('Salvar Alterações', use_container_width=True):
        conn = conectar_db()
        cursor = conn.cursor()

        # Atualizar os dados da venda
        cursor.execute('''
            UPDATE venda
            SET data = ?, tipo_recebimento = ?, valor_total = ?, cod_cliente = ?, nome_cliente = ?, frete = ?
            WHERE id = ?
        ''', (data, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete, venda[0]))

        # Atualizar os dados dos itens (se necessário, pode ser expandido para edição direta)
        # O código para edição de itens individualmente não foi incluído neste exemplo,
        # mas pode ser adicionado como botões para cada linha na tabela.

        conn.commit()
        conn.close()

        st.success("Venda atualizada com sucesso!")


cabecalho()

if 'page' not in st.session_state:
    st.session_state.page = 'Ab/Fc'
    
if st.session_state.page == 'Ab/Fc':
    exibir_data_atual()
    valor_digitado = st.number_input("Digite o valor em caixa", min_value=0.0, format="%.2f")
    valor_troco = st.number_input("Digite o valor do troco guardado", min_value=0.0, format="%.2f")
    
    if st.button('Abrir Caixa', use_container_width=True):
        abrir_caixa(valor_digitado, valor_troco)

elif st.session_state.page == 'FecharCaixa':
    exibir_data_atual()
    col1, col2, col3 = st.columns(3)
    with col1:
        sangria = st.number_input("Efetuar Sangria", min_value=0.0, format="%.2f")
        if st.button('Efetuar Sangria', use_container_width=True):
            efetuar_sangria(sangria)
    with col2:
        adicionar_troco_valor = st.number_input("Adicionar Troco", min_value=0.0, format="%.2f")
        if st.button('Adicionar Troco', use_container_width=True):
            adicionar_troco(adicionar_troco_valor)
    with col3:
        guardar_troco_valor = st.number_input("Guardar Troco", min_value=0.0, format="%.2f")
        if st.button('Guardar Troco', use_container_width=True):
            guardar_troco(guardar_troco_valor)
    
    col4, col5 = st.columns(2)
    with col4:
        valor_em_caixa = st.number_input("Digite o valor em caixa", min_value=0.0, value=st.session_state.valor_digitado, format="%.2f")
    with col5:
        valor_do_troco = st.number_input("Troco guardado", min_value=0.0, value=st.session_state.valor_troco, format="%.2f")

    if valor_em_caixa == 0:
        st.warning("Falta dinheiro no caixa! Deseja finalizar o caixa mesmo assim?", icon="⚠️")
        finalizar = st.button('Sim, finalizar caixa', use_container_width=True)
    else:
        finalizar = st.button('Finalizar Caixa', use_container_width=True)

    if finalizar:
        finalizar_caixa(valor_em_caixa)   
            
elif st.session_state.page == 'Venda':
    exibir_data_atual()
    st.write("### Tela para Efetuar Venda")
    
    if "produtos_venda" not in st.session_state:
        st.session_state.produtos_venda = []
    if "valor_frete" not in st.session_state:
        st.session_state.valor_frete = 0.0
    if "valor_final" not in st.session_state:
        st.session_state.valor_final = 0.0
    if "percentual_ajuste" not in st.session_state:
        st.session_state.percentual_ajuste = 0.0

    with st.form("form_adicionar_produto"):
        produtos = buscar_produto()

        col1, col2 = st.columns([1, 4])

        with col1:
            quantidade = st.number_input("Quantidade desejada", min_value=1, value=1)
        with col2:
            opc_pro = ["Selecione um produto"] + [f"{produto[2]}" for produto in produtos]
            descricao = st.selectbox("Descrição", opc_pro)

        submit_buscar = st.form_submit_button("Adicionar Produto")
        
        if submit_buscar:
            if produtos:
                produto_selecionado = produtos[0]
                if quantidade <= produto_selecionado[6]:
                    preco = produto_selecionado[9]
                    st.session_state.produtos_venda.append({
                        "id": produto_selecionado[0],
                        "Código": produto_selecionado[1],
                        "Descrição": produto_selecionado[2],
                        "Quantidade": quantidade,
                        "Preço Unitário": preco,
                        "Total": quantidade * preco
                    })
                    st.success("Produto adicionado com sucesso!")
                else:
                    st.error("Quantidade maior do que disponível em estoque.")
            else:
                st.warning("Produto não encontrado.")

    if st.session_state.produtos_venda:
        st.write("### Produtos na Venda")
        df_produtos = pd.DataFrame(st.session_state.produtos_venda)
        total_produtos = df_produtos["Total"].sum()

        st.table(df_produtos[["Código", "Descrição", "Quantidade", "Preço Unitário", "Total"]])
        st.write(f"Total dos Produtos: R${total_produtos:.2f}")

    with st.form("form_dados_cliente"):
        clientes = buscar_clientes()
        opc_cli = ["Selecione um cliente"] + [f"{cliente[1]} ({cliente[2]})" for cliente in clientes]
        nome_cliente = st.selectbox("Clientes", opc_cli)

        if nome_cliente == "Selecione um cliente" or not clientes:
            codigo_cliente = ""
            nome_cliente = ""
        else:
            indice_cliente = opc_cli.index(nome_cliente) - 1
            codigo_cliente = clientes[indice_cliente][0]

        col1, col2, col3 = st.columns([2, 2, 4])

        with col1:
            metodo_pagamento = st.selectbox("Método de Pagamento", ["Dinheiro", "Crédito", "Débito"])
        with col2:
            st.session_state.valor_frete = st.number_input("Valor do Frete", min_value=0.0, value=st.session_state.valor_frete, format="%.2f")
        with col3:
            st.session_state.percentual_ajuste = st.number_input("Desconto/Acréscimo (%)", min_value=-100.0, value=st.session_state.percentual_ajuste, step=0.1)

        submit_venda = st.form_submit_button("Finalizar Compra")
        
        if submit_venda:
            if st.session_state.produtos_venda:
                subtotal = total_produtos + st.session_state.valor_frete
                st.session_state.valor_final = subtotal * (1 + st.session_state.percentual_ajuste / 100)

                venda_id = registrar_venda(
                    data=datetime.now().strftime('%d-%m-%y'),
                    tipo_recebimento=metodo_pagamento,
                    valor_total=st.session_state.valor_final,
                    cod_cliente=codigo_cliente,
                    nome_cliente=nome_cliente,
                    frete=st.session_state.valor_frete
                )

                for item in st.session_state.produtos_venda:
                    registrar_item_venda(
                        id_venda=venda_id,
                        id_produto=item["id"],
                        quantidade=item["quantidade"],
                        preco_unitario=item["preco_unitario"],
                        valor_total=item["total_item"]
                    )

                st.success(f"Compra finalizada com sucesso! Venda ID: {venda_id}")
                st.write(f"Subtotal: R${total_produtos:.2f}")
                st.write(f"Frete: R${st.session_state.valor_frete:.2f}")
                st.write(f"Percentual de Ajuste: {st.session_state.percentual_ajuste:.2f}%")
                st.write(f"Valor Final: R${st.session_state.valor_final:.2f}")
                
                st.session_state.produtos_venda = []
                st.session_state.valor_frete = 0.0
                st.session_state.valor_final = 0.0
                st.session_state.percentual_ajuste = 0.0
            else:
                st.warning("Nenhum produto adicionado à venda.")

elif st.session_state.page == 'Orc':
    exibir_data_atual()
    st.write("### Tela de Orçamentos")
    
    if "orcamento_produtos" not in st.session_state:
        st.session_state.orcamento_produtos = []
    if "numero_orcamento" not in st.session_state:
        st.session_state.numero_orcamento = gerar_numero_orcamento()
    if "data_orcamento" not in st.session_state:
        st.session_state.data_orcamento = datetime.now().strftime("%d/%m/%Y")
    if "observacao_orcamento" not in st.session_state:
        st.session_state.observacao_orcamento = ""
    
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

    if st.session_state.orcamento_produtos:
        
        st.write("### Produtos no Orçamento")
        df_orcamento = pd.DataFrame(st.session_state.orcamento_produtos)
        total_orcamento = df_orcamento["total_item"].sum()

        st.table(df_orcamento[["codigo", "descricao", "quantidade", "preco_unitario", "percentual_ajuste", "preco_ajustado", "total_item"]])
        st.write(f"*Total do Orçamento: R${total_orcamento:.2f}*")

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

                st.session_state.orcamento_produtos = []
                st.session_state.numero_orcamento = gerar_numero_orcamento()
                st.session_state.data_orcamento = datetime.now().strftime("%d/%m/%Y")
                st.session_state.observacao_orcamento = ""
            else:
                st.warning("Nenhum produto adicionado ao orçamento.")

elif st.session_state.page == 'ListV':
    st.write('\n')
    st.subheader('Vendas')

    col1, col2, col3, col4, col5 = st.columns([1,1,2,2,2])
    
    with col1:
        if st.button("←", use_container_width=True, key="left_button"):
            if st.session_state.indice_venda > 0:
                st.session_state.indice_venda -= 1

    with col2:
        if st.button("→", use_container_width=True, key="right_button"):
            if st.session_state.indice_venda < len(listar_venda()) - 1:
                st.session_state.indice_venda += 1
    
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

    exibir_venda_atual()
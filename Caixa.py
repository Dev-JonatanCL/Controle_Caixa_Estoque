import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import sqlite3
import random
import locale
import tempfile

def run():
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')

    def conectar_db():
        return sqlite3.connect('banco.db')

    def exibir_data_atual():
        data_atual = datetime.now().strftime("%d/%m/%Y")
        st.markdown(f"<h1 style='text-align: left;'>{data_atual}</h1>", unsafe_allow_html=True)

    def formatar_data(data_str):
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            return data.strftime('%d/%m/%Y')
        except ValueError:
            return data_str

    def formatar_contabil(valor):
        return locale.currency(valor, grouping=True)

    def listar_venda():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM venda")
        venda = cursor.fetchall()
        conn.close()
        return venda

    def listar_orcamentos():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orcamento")
        orcamento = cursor.fetchall()
        conn.close()
        return orcamento

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
            if st.button("Caixa", use_container_width=True):
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
            if st.button("Vendas", use_container_width=True):
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
        conn.close()

        st.session_state.valor_digitado = valor_digitado
        st.session_state.valor_troco = valor_troco
        st.session_state.sangria = 0.0
        st.session_state.vendas_em_dinheiro = 0.0
        st.session_state.page = 'FecharCaixa'
        st.session_state.caixa_aberto = True
        st.rerun()

    def registrar_venda(data_atual, valor_total, tipo_recebimento, cod_cliente, nome_cliente, frete):
        data_atual = datetime.today().strftime('%Y-%m-%d')

        conn = conectar_db()
        cursor = conn.cursor() 
        cursor.execute('''INSERT INTO venda (data, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete) 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                    (data_atual, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete))
        conn.commit()
        
        venda_id = cursor.lastrowid

        if tipo_recebimento == 'dinheiro':
            st.session_state.vendas_em_dinheiro += valor_total
            cursor.execute('SELECT * FROM caixa WHERE data = ? ORDER BY id DESC LIMIT 1', (data_atual,))
            caixa_aberto = cursor.fetchone()
            if caixa_aberto:
                novo_valor_final = caixa_aberto[4] - valor_total
                cursor.execute('''UPDATE caixa SET valor_final = ? WHERE id = ?''', (novo_valor_final, caixa_aberto[0]))
                conn.commit()
                
                st.session_state.valor_digitado = novo_valor_final

        conn.close()
        return venda_id

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
            conn.close()
            st.session_state.caixa_aberto = False

        st.session_state.page = 'Ab/Fc'

    def efetuar_sangria(valor_sangria):
        data_atual = datetime.today().strftime('%Y-%m-%d')

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
            conn.close()
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
            conn.close()

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
            conn.close()

            st.session_state.valor_digitado = novo_valor_final
            st.session_state.valor_troco = novo_troco_final
            st.write(f"Troco guardado: R${valor_guardado:.2f}")

    def exibir_venda_atual():
        if 'indice_venda' not in st.session_state:
            st.session_state.indice_venda = 0

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

        cursor.execute('''
            SELECT iv.id, iv.id_produto, p.descricao, iv.quantidade, iv.preco_unitario, iv.valor_total
            FROM itens_venda iv
            JOIN produtos p ON iv.id_produto = p.id
            WHERE iv.id_venda = ?
        ''', (venda[0],))
        itens_venda = cursor.fetchall()
        conn.close()

        col1, col2, col3 = st.columns(3)

        with col1:
            data = datetime.strptime(venda[1], '%Y-%m-%d').date()
            data_formatada = data.strftime('%d/%m/%Y')
            st.text_input("Data", data_formatada)
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

        st.subheader("Itens da Venda")
        if itens_venda:
            df_itens = pd.DataFrame(itens_venda, columns=["ID", "ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"])
            st.table(df_itens[["ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"]])
        else:
            st.warning("Nenhum item associado a esta venda.")

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE venda
                SET data = ?, tipo_recebimento = ?, valor_total = ?, cod_cliente = ?, nome_cliente = ?, frete = ?
                WHERE id = ?
            ''', (data, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete, venda[0]))

            conn.commit()
            conn.close()

            st.success("Venda atualizada com sucesso!")

    def pesquisar_venda(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(''' 
            SELECT v.id, v.data, v.tipo_recebimento, v.valor_total, v.cod_cliente, v.nome_cliente, v.frete 
            FROM venda v 
            WHERE v.data LIKE ? OR v.nome_cliente LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        
        vendas = cursor.fetchall()
        vendas_com_itens = []
        for venda in vendas:
            cursor.execute('''
                SELECT iv.id_produto, p.descricao, iv.quantidade, iv.preco_unitario, iv.valor_total 
                FROM itens_venda iv
                JOIN produtos p ON iv.id_produto = p.id
                WHERE iv.id_venda = ?
            ''', (venda[0],))
            itens = cursor.fetchall()
            vendas_com_itens.append((venda, itens))
        
        conn.close()
        return vendas_com_itens

    def tela_pesquisa_venda():
        st.write('\n')
        st.subheader('Pesquisar Venda')

        pesquisa = st.text_input("Digite a data da venda ou nome do cliente para pesquisar: ")

        if pesquisa:
            try:
                data_pesquisa = datetime.strptime(pesquisa, '%d/%m/%Y').date()
                data_pesquisa_formatada = data_pesquisa.strftime('%Y-%m-%d')
                vendas_encontradas = pesquisar_venda(data_pesquisa_formatada)
            except ValueError:
                vendas_encontradas = pesquisar_venda(pesquisa)

            exibir_resultados_pesquisa_venda(vendas_encontradas)

    def exibir_resultados_pesquisa_venda(vendas):
        if not vendas:
            st.warning("Não há vendas efetuadas.")
            return
        
        if st.session_state.indice_venda >= len(vendas):
            st.session_state.indice_venda = 0
        elif st.session_state.indice_venda < 0:
            st.session_state.indice_venda = len(vendas) - 1

        venda_atual, itens_venda = vendas[st.session_state.indice_venda]

        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_venda > 0:
                    st.session_state.indice_venda -= 1
                    st.rerun()
        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_venda < len(vendas) - 1:
                    st.session_state.indice_venda += 1
                    st.rerun()

        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'ListV'
                st.rerun()

        col1, col2, col3 = st.columns(3)

        with col1:
            data = datetime.strptime(venda_atual[1], '%Y-%m-%d').date()
            data_formatada = data.strftime('%d/%m/%Y')
            st.text_input("Data", value=data_formatada)
        with col2:
            tipo_recebimento = st.text_input("Tipo de Recebimento", venda_atual[2])
        with col3:
            valor_total = st.number_input("Valor Total", value=venda_atual[3], min_value=0.0, format="%.2f")

        col1, col2 = st.columns(2)

        with col1:
            cod_cliente = st.text_input("Código do Cliente", venda_atual[4])
        with col2:
            nome_cliente = st.text_input("Nome do Cliente", venda_atual[5])

        col1, col2 = st.columns(2)

        with col1:
            frete = st.number_input("Valor do Frete", value=venda_atual[6], min_value=0.0, format="%.2f")

        st.subheader("Itens da Venda")
        if itens_venda:
            df_itens = pd.DataFrame(itens_venda, columns=["ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"])
            st.table(df_itens)
        else:
            st.warning("Nenhum item associado a esta venda.")

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE venda
                SET data = ?, tipo_recebimento = ?, valor_total = ?, cod_cliente = ?, nome_cliente = ?, frete = ?
                WHERE id = ?
            ''', (data, tipo_recebimento, valor_total, cod_cliente, nome_cliente, frete, venda_atual[0]))

            conn.commit()
            conn.close()

            st.success("Venda atualizada com sucesso!")

    def listar_vendas_por_periodo(data_inicial, data_final):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM venda
            WHERE data BETWEEN ? AND ?
        ''', (data_inicial, data_final))

        vendas = cursor.fetchall()
        conn.close()

        return vendas

    def tela_pesquisa_venda_periodo():
        data_inicial_default = datetime.today().date()
        data_final_default = datetime.today().date()

        data_inicial = st.text_input("Data Inicial", data_inicial_default.strftime('%d/%m/%Y'))
        data_final = st.text_input("Data Final", data_final_default.strftime('%d/%m/%Y'))

        if st.button('Pesquisar', use_container_width=True):
            try:
                data_inicial = datetime.strptime(data_inicial, '%d/%m/%Y').date()
                data_final = datetime.strptime(data_final, '%d/%m/%Y').date()

                if data_inicial > data_final:
                    st.error("A data inicial não pode ser maior que a data final.")
                else:
                    data_inicial_formatada_banco = data_inicial.strftime('%Y-%m-%d')
                    data_final_formatada_banco = data_final.strftime('%Y-%m-%d')

                    vendas_encontradas = listar_vendas_por_periodo(data_inicial_formatada_banco, data_final_formatada_banco)
                    exibir_vendas_periodo(vendas_encontradas)
            
            except ValueError:
                st.error("Formato de data inválido.")
                
    def exibir_vendas_periodo(vendas):
        if not vendas:
            st.warning("Não há vendas no período selecionado.")
            return
        
        vendas_df = pd.DataFrame(vendas, columns=["ID", "Data", "Tipo de recebimento", "Valor Total", "Código do Cliente", "Nome do Cliente", "Frete"])
        vendas_df = vendas_df.drop(columns=['ID'])

        vendas_df['Data'] = vendas_df['Data'].apply(lambda x: formatar_data(x))
        vendas_df['Valor Total'] = vendas_df['Valor Total'].apply(lambda x: formatar_contabil(x))
        vendas_df['Frete'] = vendas_df['Frete'].apply(lambda x: formatar_contabil(x))
        
        st.dataframe(vendas_df.style)

    def exibir_orcamento_atual():
        st.write('\n')
        st.header("Orçamentos")

        if 'indice_orcamento' not in st.session_state:
            st.session_state.indice_orcamento = 0

        col1, col2, col3, col4, col5, col6 = st.columns([1,1,2,2,2,2])

        with col1:
            if st.button("←", use_container_width=True, key="left_button_orcamento"):
                if st.session_state.indice_orcamento > 0:
                    st.session_state.indice_orcamento -= 1

        with col2:
            if st.button("→", use_container_width=True, key="right_button_orcamento"):
                if st.session_state.indice_orcamento < len(listar_orcamentos()) - 1:
                    st.session_state.indice_orcamento += 1
        
        with col3:
            if st.button('Incluir', use_container_width=True, key="incluir_orcamento_button"):
                st.session_state.page = 'incluir_orcamento'
                st.rerun()

        with col4:
            if st.button('Apagar', use_container_width=True, key="apagar_orcamento_button"):
                st.session_state.page = 'apagar_orcamento'
                st.rerun()

        with col5:
            if st.button('Pesquisar', use_container_width=True, key="pesquisar_orcamento_button"):
                st.session_state.page = 'pesquisar_orcamento'
                st.rerun()
        with col6:
            orcamentos = listar_orcamentos()      
            orcamento_atual = orcamentos[st.session_state.indice_orcamento]      
            id_orcamento = orcamento_atual[0]
            
            itens_orcamento = pesquisar_itens_orcamento(id_orcamento)
            
            itens_orcamento = [
                {
                    "quantidade": item[3],
                    "descricao": item[2],
                    "preco_unitario": item[4],
                    "valor_total": item[5],
                }
                for item in itens_orcamento
            ]

            orcamento = {
                "numero_pedido": orcamento_atual[2],
                "nome_cliente": orcamento_atual[3],
                "data": orcamento_atual[1],
                "observacao": orcamento_atual[6],
                "valor_total": orcamento_atual[4],
            }
            
            pdf_file = pdf_orcamento(id_orcamento)
            st.download_button(
                label="Imprimir", use_container_width=True,
                data=pdf_file,
                file_name=f"orcamento_{id_orcamento}.pdf",
                mime="application/pdf",
            )

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM orcamento LIMIT 1 OFFSET ?''', (st.session_state.indice_orcamento,))
        orcamento = cursor.fetchone()

        if orcamento is None:
            st.warning("Não há orçamentos cadastrados.")
            conn.close()
            return

        cursor.execute('''
            SELECT io.id, io.id_produto, p.descricao, io.quantidade, io.preco_unitario, io.valor_total
            FROM itens_orcamento io
            JOIN produtos p ON io.id_produto = p.id
            WHERE io.id_orcamento = ?
        ''', (orcamento[0],))
        itens_orcamento = cursor.fetchall()
        conn.close()

        col1, col2 = st.columns([1,4])

        with col1:
            cod_cliente = st.text_input("Código do Cliente", orcamento[3])
        with col2:
            nome_cliente = st.text_input("Nome do Cliente", orcamento[4])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Data do Orçamento", orcamento[1])
        with col2:
            numero_pedido = st.text_input("Numero do pedido", orcamento[2])
        with col3:
            valor_total = st.number_input("Valor Total", value=orcamento[5], min_value=0.0, format="%.2f")
            
        observacao = st.text_area("Obeservações", orcamento[6])

        st.subheader("Itens do Orçamento")
        if itens_orcamento:
            itens_df = pd.DataFrame(itens_orcamento, columns=["ID", "ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"])
            itens_df = itens_df.drop(columns=['ID', 'ID Produto'])

            itens_df['Preço Unitário'] = itens_df['Preço Unitário'].apply(lambda x: formatar_contabil(x))
            itens_df['Valor Total'] = itens_df['Valor Total'].apply(lambda x: formatar_contabil(x))

            st.dataframe(itens_df.style, use_container_width=True)
        else:
            st.warning("Nenhum item associado a este orçamento.")

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orcamento
                SET data = ?, numero_pedido = ?, valor_total = ?, cod_cliente = ?, nome_cliente = ?, observacao = ?
                WHERE id = ?
            ''', (orcamento[1], numero_pedido, valor_total, cod_cliente, nome_cliente, observacao, orcamento[0]))

            conn.commit()
            conn.close()

            st.success("Orçamento atualizado com sucesso!")

    def salvar_orcamento():
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orcamento (data, numero_pedido, cod_cliente, nome_cliente, valor_total, observacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (st.session_state.data_orcamento, st.session_state.numero_orcamento, codigo_cliente, nome_cliente, total_orcamento, st.session_state.observacao_orcamento))
        conn.commit()

        id_orcamento = cursor.lastrowid

        for produto in st.session_state.orcamento_produtos:
            cursor.execute('''
                INSERT INTO itens_orcamento (id_orcamento, id_produto, quantidade, preco_unitario, valor_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_orcamento, produto["id"], produto["Quantidade"], produto["Preço Unitário"], produto["Total"]))
        
        conn.commit()
        conn.close()

    def pesquisar_orcamentos(pesquisa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM orcamento 
            WHERE numero_pedido LIKE ? OR nome_cliente LIKE ?
        ''', ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        orcamentos = cursor.fetchall()
        conn.close()
        return orcamentos

    def pesquisar_orcamento():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT numero_pedido, data, nome_cliente, valor_total FROM orcamento ORDER BY data DESC")
        orcamentos = cursor.fetchall()
        conn.close()
        return orcamentos

    def pesquisar_itens_orcamento(id_orcamento):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT io.id, io.id_produto, p.descricao, io.quantidade, io.preco_unitario, io.valor_total
            FROM itens_orcamento io
            JOIN produtos p ON io.id_produto = p.id
            WHERE io.id_orcamento = ?
        ''', (id_orcamento,))
        itens = cursor.fetchall()
        conn.close()
        return itens

    def tela_pesquisa_orcamentos():
        st.subheader("Pesquisar Orçamentos")

        pesquisa = st.text_input("Digite o número do pedido ou nome do cliente")

        if pesquisa:
            orcamentos_encontrados = pesquisar_orcamentos(pesquisa)
            exibir_resultados_pesquisa_orcamentos(orcamentos_encontrados)

    def exibir_resultados_pesquisa_orcamentos(orcamentos):
        if not orcamentos:
            st.warning("Nenhum orçamento encontrado.")
            return

        if st.session_state.indice_orcamento >= len(orcamentos):
            st.session_state.indice_orcamento = 0
        elif st.session_state.indice_orcamento < 0:
            st.session_state.indice_orcamento = len(orcamentos) - 1

        orcamento_atual = orcamentos[st.session_state.indice_orcamento]

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            if st.button("←", use_container_width=True, key="left_button"):
                if st.session_state.indice_orcamento > 0:
                    st.session_state.indice_orcamento -= 1
                    st.rerun()

        with col2:
            if st.button("→", use_container_width=True, key="right_button"):
                if st.session_state.indice_orcamento < len(orcamentos) - 1:
                    st.session_state.indice_orcamento += 1
                    st.rerun()

        with col3:
            if st.button('Voltar', use_container_width=True, key="voltar_button"):
                st.session_state.page = 'Orc'
                st.rerun()

        col1, col2 = st.columns([2, 4])

        with col1:
            numero_pedido = st.text_input('Número do Pedido', orcamento_atual[2])
        with col2:
            nome_cliente = st.text_input('Nome do Cliente', orcamento_atual[4])

        col1, col2 = st.columns([2, 2])

        with col1:
            data = st.text_input('Data', orcamento_atual[1])
        with col2:
            valor_total = st.number_input('Valor Total', value=orcamento_atual[5], min_value=0.0, format="%.2f")

        observacao = st.text_area('Observação', orcamento_atual[6], height=150)

        st.subheader("Itens do Orçamento")

        itens_orcamento = pesquisar_itens_orcamento(orcamento_atual[0])

        if itens_orcamento:
            itens_df = pd.DataFrame(itens_orcamento, columns=["ID", "ID Produto", "Descrição", "Quantidade", "Preço Unitário", "Valor Total"])
            itens_df = itens_df.drop(columns=['ID', 'ID Produto'])

            itens_df['Preço Unitário'] = itens_df['Preço Unitário'].apply(lambda x: f"R$ {x:,.2f}")
            itens_df['Valor Total'] = itens_df['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")

            st.dataframe(itens_df.style, use_container_width=True)
        else:
            st.warning("Nenhum item associado a este orçamento.")

        if st.button('Salvar Alterações', use_container_width=True):
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orcamento 
                SET data = ?, numero_pedido = ?, nome_cliente = ?, valor_total = ?, observacao = ?
                WHERE id = ?
            ''', (data, numero_pedido, nome_cliente, valor_total, observacao, orcamento_atual[0]))

            conn.commit()
            conn.close()

            st.success("Orçamento atualizado com sucesso!")

    def pdf_orcamento(orcamento_id):
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, data, numero_pedido, cod_cliente, nome_cliente, valor_total, observacao
            FROM orcamento
            WHERE id = ?
        ''', (orcamento_id,))
        orcamento = cursor.fetchone()

        if not orcamento:
            return None

        cursor.execute('''
            SELECT i.id, i.quantidade, i.preco_unitario, i.valor_total, p.descricao
            FROM itens_orcamento i
            JOIN produtos p ON i.id_produto = p.id
            WHERE i.id_orcamento = ?
        ''', (orcamento_id,))
        itens_orcamento = cursor.fetchall()

        conn.close()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Orçamento", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 9)
        pdf.cell(30, 10, 'Número Pedido:', ln=0)
        pdf.cell(60, 10, str(orcamento[2]), ln=1)
        pdf.cell(30, 10, 'Cliente:', ln=0)
        pdf.cell(60, 10, orcamento[4], ln=1)
        pdf.cell(30, 10, 'Data:', ln=0)
        pdf.cell(60, 10, orcamento[1], ln=1)
        pdf.cell(30, 10, 'Observação:', ln=0)
        pdf.multi_cell(0, 10, orcamento[6])
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 9)
        pdf.cell(20, 10, 'Qtd.', border=1, align='C')
        pdf.cell(110, 10, 'Descrição', border=1, align='C')
        pdf.cell(30, 10, 'Preço Unitário', border=1, align='C')
        pdf.cell(30, 10, 'Valor Total', border=1, align='C')
        pdf.ln()

        pdf.set_font("Arial", size=9)
        
        for item in itens_orcamento:
            pdf.cell(20, 10, str(item[1]), border=1, align='C')
            pdf.cell(110, 10, item[4], border=1, align='L')
            pdf.cell(30, 10, f"R$ {item[2]:,.2f}", border=1, align='C')
            pdf.cell(30, 10, f"R$ {item[3]:,.2f}", border=1, align='C')
            pdf.ln()

        pdf.set_font("Arial", 'B', 9)
        pdf.cell(160, 10, "Total do Orçamento", border=1, align='R')
        pdf.cell(30, 10, f"R$ {orcamento[5]:,.2f}", border=1, align='C')

        pdf_output = pdf.output(dest='S').encode('latin1')
        return pdf_output
    
    def gerar_comprovante_pdf(venda_id, valor_total_input):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Comprovante de Venda", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.cell(200, 10, txt=f"Valor Total: R${valor_total_input:.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Subtotal: R${st.session_state.total_produtos:.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Frete: R${st.session_state.valor_frete:.2f}", ln=True)
            pdf.cell(200, 10, txt=f"Percentual de Ajuste: {st.session_state.percentual_ajuste:.2f}%", ln=True)
            pdf.output(temp_pdf.name)

            return temp_pdf.name

    cabecalho()

    if 'page' not in st.session_state:
        st.session_state.page = 'Ab/Fc'
        
    if st.session_state.page == 'Ab/Fc':
        exibir_data_atual()
        valor_digitado = st.number_input("Digite o valor em caixa", min_value=0.0, format="%.2f")
        valor_troco = st.number_input("Digite o valor do troco guardado", min_value=0.0, format="%.2f")
        
        if st.button('Abrir Caixa', use_container_width=True):
            abrir_caixa(valor_digitado, valor_troco)

    if st.session_state.page == 'FecharCaixa':
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
                
    if st.session_state.page == 'Venda':
        exibir_data_atual()
        st.header("Tela de Venda")
        
        if "produtos_venda" not in st.session_state:
            st.session_state.produtos_venda = []
        if "valor_frete" not in st.session_state:
            st.session_state.valor_frete = 0.0
        if "valor_final" not in st.session_state:
            st.session_state.valor_final = 0.0
        if "percentual_ajuste" not in st.session_state:
            st.session_state.percentual_ajuste = 0.0

        produtos = buscar_produto()

        col1, col2, col3 = st.columns([1.5,1.5,4])

        with col1:
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
        with col2:
            codigo_produto = st.text_input("Código", "")
        with col3:
            opc_pro = ["Selecione um produto"] + [f"{produto[2]}" for produto in produtos]
            descricao = st.selectbox("Descrição", opc_pro)

        if codigo_produto.strip():
            produto_por_codigo = next((produto for produto in produtos if str(produto[1]) == codigo_produto.strip()), None)
            if produto_por_codigo:
                descricao = produto_por_codigo[2]
            else:
                st.warning("Código de produto não encontrado.")

        if descricao != "Selecione um produto":
            produto_por_descricao = next((produto for produto in produtos if produto[2] == descricao), None)
            if produto_por_descricao:
                codigo_produto = str(produto_por_descricao[1])

        submit_buscar = st.button("Adicionar Produto")

        if submit_buscar:
            if descricao != "Selecione um produto" and produtos:
                produto_selecionado = next((produto for produto in produtos if produto[2] == descricao), None)

                if produto_selecionado:
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
                    st.warning("Produto não encontrado.")
            else:
                st.warning("Por favor, selecione um produto válido.")

        if st.session_state.produtos_venda:
            st.subheader("Produtos na Venda")
            df_produtos = pd.DataFrame(st.session_state.produtos_venda)
            st.session_state.total_produtos = df_produtos["Total"].sum()

            df_produtos['Preço Unitário'] = df_produtos['Preço Unitário'].apply(lambda x: formatar_contabil(x))
            df_produtos['Total'] = df_produtos['Total'].apply(lambda x: formatar_contabil(x))

            st.table(df_produtos[["Código", "Descrição", "Quantidade", "Preço Unitário", "Total"]])
        else:
            st.session_state.total_produtos = 0.0
            st.write("Nenhum produto adicionado à venda.")

        clientes = buscar_clientes()
        opc_cli = ["Selecione um cliente"] + [f"{cliente[1]} ({cliente[2]})" for cliente in clientes]
        nome_cliente = st.selectbox("Clientes", opc_cli)

        if nome_cliente == "Selecione um cliente" or not clientes:
            codigo_cliente = ""
            nome_cliente = ""
        else:
            indice_cliente = opc_cli.index(nome_cliente) - 1
            codigo_cliente = clientes[indice_cliente][0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metodo_pagamento = st.selectbox("Método de Pagamento", ["Dinheiro", "Crédito", "Débito"])
        with col2:
            st.session_state.valor_frete = st.number_input("Valor do Frete", min_value=0.0, value=st.session_state.valor_frete, format="%.2f")
        with col3:
            st.session_state.percentual_ajuste = st.number_input("Desconto/Acréscimo (%)", min_value=-100.0, value=st.session_state.percentual_ajuste, step=0.1)
        with col4:
            subtotal_com_frete = st.session_state.total_produtos + st.session_state.valor_frete
            st.session_state.valor_final = subtotal_com_frete * (1 + st.session_state.percentual_ajuste / 100)
            valor_total_input = st.number_input("Valor Total", min_value=0.0, value=st.session_state.valor_final, format="%.2f")

        submit_venda = st.button("Finalizar Compra")
        
        if submit_venda:
            if st.session_state.produtos_venda:
                venda_id = registrar_venda(
                    data_atual=datetime.now().strftime('%Y-%m-%d'),
                    tipo_recebimento=metodo_pagamento,
                    valor_total=valor_total_input,
                    cod_cliente=codigo_cliente,
                    nome_cliente=nome_cliente,
                    frete=st.session_state.valor_frete
                )
                for item in st.session_state.produtos_venda:
                    registrar_item_venda(
                        id_venda=venda_id,
                        id_produto=item["id"],
                        quantidade=item["Quantidade"],
                        preco_unitario=item["Preço Unitário"],
                        valor_total=item["Total"]
                    )
                
                st.success(f"Compra finalizada com sucesso!")
                st.write(f"Subtotal: R${st.session_state.total_produtos:.2f}")
                st.write(f"Frete: R${st.session_state.valor_frete:.2f}")
                st.write(f"Percentual de Ajuste: {st.session_state.percentual_ajuste:.2f}%")
                st.write(f"Valor Final: R${valor_total_input:.2f}")

                pdf_path = gerar_comprovante_pdf(venda_id, valor_total_input)
        
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    st.download_button(
                        label="Baixar Comprovante", 
                        data=pdf_bytes, 
                        file_name=f"comprovante_{venda_id}.pdf", 
                        mime="application/pdf"
                    )

                st.session_state.produtos_venda = []
                st.session_state.valor_frete = 0.0
                st.session_state.valor_final = 0.0
                st.session_state.percentual_ajuste = 0.0

            else:
                st.warning("Nenhum produto adicionado à venda.")

    if st.session_state.page == 'Orc':
        exibir_orcamento_atual()

    if st.session_state.page == 'incluir_orcamento':
        if "orcamento_produtos" not in st.session_state:
            st.session_state.orcamento_produtos = []
        if "numero_orcamento" not in st.session_state:
            st.session_state.numero_orcamento = gerar_numero_orcamento()
        if "data_orcamento" not in st.session_state:
            st.session_state.data_orcamento = datetime.now().strftime("%d/%m/%Y")
        if "observacao_orcamento" not in st.session_state:
            st.session_state.observacao_orcamento = ""
            
        st.write('\n')
        st.header("Novo Orçamento")
        st.write(f"*Número do Orçamento:* {st.session_state.numero_orcamento}")
        st.write(f"*Data do Orçamento:* {st.session_state.data_orcamento}")
        
        
        produtos = buscar_produto()

        col1, col2, col3 = st.columns([1.5, 1.5, 4])

        with col1:
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
        with col2:
            codigo_produto = st.text_input("Código", "")
        with col3:
            opc_pro = ["Selecione um produto"] + [f"{produto[2]}" for produto in produtos]
            descricao = st.selectbox("Descrição", opc_pro)

        if codigo_produto.strip():
            produto_por_codigo = next((produto for produto in produtos if str(produto[1]) == codigo_produto.strip()), None)
            if produto_por_codigo:
                descricao = produto_por_codigo[2]
            else:
                st.warning("Código de produto não encontrado.")

        if descricao != "Selecione um produto":
            produto_por_descricao = next((produto for produto in produtos if produto[2] == descricao), None)
            if produto_por_descricao:
                codigo_produto = str(produto_por_descricao[1])

        submit_buscar = st.button("Adicionar Produto")

        if submit_buscar:
            if descricao != "Selecione um produto" and produtos:
                produto_selecionado = next((produto for produto in produtos if produto[2] == descricao), None)

                if produto_selecionado:
                    if quantidade <= produto_selecionado[6]:
                        preco = produto_selecionado[9]
                        st.session_state.orcamento_produtos.append({
                            "id": produto_selecionado[0],
                            "Código": produto_selecionado[1],
                            "Descrição": produto_selecionado[2],
                            "Quantidade": quantidade,
                            "Preço Unitário": preco,
                            "Total": quantidade * preco
                        })
                        st.success("Produto adicionado com sucesso!")
                else:
                    st.warning("Produto não encontrado.")
            else:
                st.warning("Por favor, selecione um produto válido.")

        if st.session_state.orcamento_produtos:   
            st.subheader("Produtos no Orçamento")
            df_orcamento = pd.DataFrame(st.session_state.orcamento_produtos)
            total_orcamento = df_orcamento["Total"].sum()

            st.table(df_orcamento[["Código", "Descrição", "Quantidade", "Preço Unitário", "Total"]])

        else:
            total_orcamento = 0.0
            st.write("Nenhum produto adicionado ao orçamento.")

        clientes = buscar_clientes()
        opc_cli = ["Selecione um cliente"] + [f"{cliente[1]} ({cliente[2]})" for cliente in clientes]
        nome_cliente = st.selectbox("Cliente", opc_cli)
        st.session_state.observacao_orcamento = st.text_area("Observações", value=st.session_state.observacao_orcamento)

        if nome_cliente == "Selecione um cliente" or not clientes:
            codigo_cliente = ""
            nome_cliente = ""
        else:
            indice_cliente = opc_cli.index(nome_cliente) - 1
            codigo_cliente = clientes[indice_cliente][0]

        submit_orcamento = st.button("Finalizar Orçamento")
        
        if submit_orcamento:
            if st.session_state.orcamento_produtos:
                salvar_orcamento()
                st.success("Orçamento finalizado com sucesso!")
                st.session_state.orcamento_produtos = []
                st.session_state.numero_orcamento = gerar_numero_orcamento()
                st.session_state.data_orcamento = datetime.now().strftime("%d/%m/%Y")
                st.session_state.observacao_orcamento = ""
            else:
                st.warning("Nenhum produto adicionado ao orçamento.")

    if st.session_state.page == 'apagar_orcamento':
        st.write('\n')
        st.subheader('Deseja realmente apagar este orçamento ?')

        orcamento_atual = listar_orcamentos()[st.session_state.indice_orcamento]
        orcamento_id = orcamento_atual[0]

        col1, col2, col3 = st.columns([2,2,4])

        with col1:
            if st.button('Apagar', use_container_width=True):
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM orcamento WHERE id = ?", (orcamento_id,))
                conn.commit()
                conn.close()

                st.session_state.page = 'Orc'
                st.rerun()

        with col2:
            if st.button('Cancelar', use_container_width=True):
                st.session_state.page = 'Orc'
                st.rerun()

        with col3:
            st.write('')

    if st.session_state.page == 'pesquisar_orcamento':
        tela_pesquisa_orcamentos()

    if st.session_state.page == 'ListV':
        st.write('\n')
        st.header('Vendas')

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

    if st.session_state.page == 'apagar':
        st.write('\n')
        st.subheader('Deseja realmente apagar esta venda ?')

        venda_atual = listar_venda()[st.session_state.indice_venda]
        venda_id = venda_atual[0]

        col1, col2, col3 = st.columns([2, 2, 4])

        with col1:
            if st.button('Apagar', use_container_width=True):
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM venda WHERE id = ?", (venda_id,))
                conn.commit()
                conn.close()

                st.success(f"Venda {venda_id} apagada com sucesso!")
                st.session_state.page = 'ListV'
                st.rerun()

        with col2:
            if st.button('Cancelar', use_container_width=True):
                st.session_state.page = 'ListV'
                st.rerun()

        with col3:
            st.write('')

    if st.session_state.page == 'pesq':
        tela_pesquisa_venda()

    if st.session_state.page == 'list':
        st.write('')
        st.header('Listagem de Vendas por Período')

        if st.button('Voltar', use_container_width=True, key="voltar_button"):
            st.session_state.page = 'ListV'
            st.rerun()

        tela_pesquisa_venda_periodo()

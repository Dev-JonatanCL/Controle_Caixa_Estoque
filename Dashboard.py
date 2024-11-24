import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

def run():
    st.title("Página de Caixa")
    st.write("Bem-vindo à página de Caixa.")

def conectar_banco(nome_banco):
    return sqlite3.connect(nome_banco)

def carregar_dados(conn, tabela):
    query = f"SELECT * FROM {tabela}"
    return pd.read_sql(query, conn)

def calcular_totais(df, coluna_data, coluna_valor, agrupamento):
    df[coluna_data] = pd.to_datetime(df[coluna_data])
    if agrupamento == "dia":
        df["periodo"] = df[coluna_data].dt.date
    elif agrupamento == "mês":
        df["periodo"] = df[coluna_data].dt.to_period("M").astype(str)
    elif agrupamento == "ano":
        df["periodo"] = df[coluna_data].dt.year
    else:
        return None
    return df.groupby("periodo")[coluna_valor].sum().reset_index()

st.title("📊 Dashboard de Análise de Dados")

conn = conectar_banco('banco.db')

st.header("💳 Distribuição de Vendas por Método de Pagamento")

df_venda = carregar_dados(conn, "venda")

agrupamento_pizza = st.selectbox("Agrupar Distribuição por:", ["dia", "mês", "ano"], index=1)

df_venda["data"] = pd.to_datetime(df_venda["data"])
if agrupamento_pizza == "dia":
    df_venda["periodo"] = df_venda["data"].dt.date
elif agrupamento_pizza == "mês":
    df_venda["periodo"] = df_venda["data"].dt.to_period("M").astype(str)
elif agrupamento_pizza == "ano":
    df_venda["periodo"] = df_venda["data"].dt.year

vendas_por_metodo_periodo = df_venda.groupby(["periodo", "tipo_recebimento"])["valor_total"].sum().reset_index()

periodos_disponiveis = vendas_por_metodo_periodo["periodo"].unique()
periodo_selecionado = st.selectbox("Selecione o Período:", sorted(periodos_disponiveis, reverse=True))

dados_filtrados = vendas_por_metodo_periodo[vendas_por_metodo_periodo["periodo"] == periodo_selecionado]

fig_pizza = px.pie(
    dados_filtrados,
    names="tipo_recebimento",
    values="valor_total",
    title=f"Distribuição de Vendas por Tipo de Pagamento ({periodo_selecionado})",
    labels={"tipo_recebimento": "Método de Pagamento", "valor_total": "Valor Total (R$)"},
)
st.plotly_chart(fig_pizza, use_container_width=True)

st.header("📅 Total de Vendas")
agrupamento_vendas = st.selectbox("Agrupar Vendas por:", ["dia", "mês", "ano"], index=1)
totais_venda = calcular_totais(df_venda, "data", "valor_total", agrupamento_vendas)

if totais_venda is not None:
    fig_vendas = px.bar(
        totais_venda,
        x="periodo",
        y="valor_total",
        title=f"Total de Vendas por {agrupamento_vendas.capitalize()}",
        labels={"periodo": agrupamento_vendas.capitalize(), "valor_total": "Valor Total (R$)"},
    )
    st.plotly_chart(fig_vendas, use_container_width=True)

st.write('\n')
st.write('\n')
st.write('\n')

st.header("📦 Estoque")
df_produtos = carregar_dados(conn, "produtos")

col1, col2 = st.columns(2)

total_estoque = df_produtos["qtd_estoque"].sum()
valor_estoque = (df_produtos["qtd_estoque"] * df_produtos["custo"]).sum()

with col1:
    st.metric("Total de Produtos em Estoque", f"{total_estoque} unidades")
with col2:
    st.metric("Valor Total do Estoque", f"R$ {valor_estoque:,.2f}")

st.write('\n')
st.write('\n')
st.write('\n')

st.header("👥 Clientes Cadastrados")
df_clientes_pf = carregar_dados(conn, "cadastro_cliente_pessoa_fisica")
df_clientes_pj = carregar_dados(conn, "cadastro_pessoa_juridica")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Clientes Pessoa Física", len(df_clientes_pf))
with col2:
    st.metric("Clientes Pessoa Jurídica", len(df_clientes_pj))
with col3:
    st.metric("Total de Clientes", len(df_clientes_pf) + len(df_clientes_pj))

st.write('\n')
st.write('\n')
st.write('\n')

st.header("🏢 Fornecedores Cadastrados")
df_fornecedores = carregar_dados(conn, "cadastro_fornecedores")
st.metric("Total de Fornecedores", len(df_fornecedores))

st.write('\n')
st.write('\n')
st.write('\n')

st.header("📋 Produtos Cadastrados")
st.metric("Total de Produtos", len(df_produtos))

st.write('\n')
st.write('\n')
st.write('\n')

col1, col2 = st.columns(2)

with col1:
    st.header("📆 Contas Pagas")

    df_contas_pagas = carregar_dados(conn, "contas_pagas")
    agrupamento_contas = st.selectbox("Agrupar Contas Pagas por:", ["dia", "mês", "ano"], index=1)
    df_contas_pagas["data_pagamento"] = pd.to_datetime(df_contas_pagas["data_pagamento"])
    
with col2:
    st.header("💳 Contas a Pagar")
    df_contas_pagar = carregar_dados(conn, "contas_a_pagar")
    total_contas_pagar = df_contas_pagar["valor"].sum()
    st.metric("Total de Contas a Pagar", f"R$ {total_contas_pagar:,.2f}")

totais_contas_pagas = calcular_totais(df_contas_pagas, "data_pagamento", "valor", agrupamento_contas)

if totais_contas_pagas is not None:
    fig_contas_pagas = px.bar(
        totais_contas_pagas,
        x="periodo",
        y="valor",
        title=f"Total de Contas Pagas por {agrupamento_contas.capitalize()}",
        labels={"periodo": agrupamento_contas.capitalize(), "valor": "Valor Total (R$)"},
    )
    st.plotly_chart(fig_contas_pagas, use_container_width=True)

total_contas_pagas = df_contas_pagas["valor"].sum()
st.metric("Total de Contas Pagas", f"R$ {total_contas_pagas:,.2f}")

conn.close()

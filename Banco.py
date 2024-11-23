import sqlite3

def criar_banco_dados():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            fabricante TEXT NOT NULL,
            fornecedor TEXT NOT NULL,
            unidade INTEGER NOT NULL,
            qtd_estoque INTEGER NOT NULL,
            custo REAL NOT NULL,
            margem REAL NOT NULL,
            preco REAL NOT NULL,
            observacao TEXT,
            qtd_minima INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor_inicial REAL NOT NULL,
            troco_inicial REAL NOT NULL,
            valor_final REAL NOT NULL,
            troco_final REAL NOT NULL,
            valor_sangria REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo_recebimento TEXT NOT NULL,
            valor_total REAL NOT NULL,
            cod_cliente INTEGER NOT NULL,
            nome_cliente TEXT NOT NULL,
            frete REAL NOT NULL,
            FOREIGN KEY(cod_cliente) REFERENCES cadastro_cliente_pessoa_fisica(cod_cliente) 
            ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venda INTEGER NOT NULL,
            id_produto INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY(id_venda) REFERENCES venda(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(id_produto) REFERENCES produtos(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            numero_pedido INTEGER NOT NULL,
            cod_cliente INTEGER NOT NULL,
            nome_cliente TEXT NOT NULL,
            valor_total REAL NOT NULL,
            observacao TEXT,
            FOREIGN KEY(cod_cliente) REFERENCES cadastro_cliente_pessoa_fisica(cod_cliente)
            ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_orcamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_orcamento INTEGER NOT NULL,
        id_produto INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario REAL NOT NULL,
        valor_total REAL NOT NULL,
        FOREIGN KEY(id_orcamento) REFERENCES orcamento(id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY(id_produto) REFERENCES produtos(id) ON DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_a_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_fornecedor INTEGER NOT NULL,
            nome_fornecedor TEXT NOT NULL,
            data_entrada TEXT NOT NULL,
            vencimento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            parcela INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_quitacao TEXT,
            FOREIGN KEY(cod_fornecedor) REFERENCES cadastro_fornecedores(cod_fornecedor)
            ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_pagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_fornecedor INTEGER NOT NULL,
            nome_fornecedor TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            valor REAL NOT NULL,
            parcela INTEGER NOT NULL,
            data_pagamento TEXT NOT NULL,
            vencimento TEXT NOT NULL,
            FOREIGN KEY(cod_fornecedor) REFERENCES cadastro_fornecedores(cod_fornecedor)
            ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro_cliente_pessoa_fisica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_cliente INTEGER NOT NULL,
            nome_cliente TEXT NOT NULL,
            cpf TEXT NOT NULL,
            rg TEXT,
            endereco TEXT NOT NULL,
            numero TEXT NOT NULL,
            cep TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            complemento TEXT,
            telefone TEXT,
            celular TEXT,
            data_nascimento,
            filiacao TEXT,
            email TEXT,
            observacao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro_pessoa_juridica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_cliente INTEGER NOT NULL,
            nome_empresa TEXT NOT NULL,
            endereco TEXT NOT NULL,
            numero TEXT NOT NULL,
            complemento TEXT,
            cep TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cnpj TEXT NOT NULL,
            inscricao_estadual TEXT NOT NULL,
            telefone TEXT,
            celular TEXT,
            contato TEXT,
            email TEXT NOT NULL,
            observacao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro_fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_fornecedor INTEGER NOT NULL,
            nome_fornecedor TEXT NOT NULL,
            endereco TEXT NOT NULL,
            numero TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cep TEXT NOT NULL,
            telefone TEXT,
            celular TEXT,
            cnpj TEXT NOT NULL,
            inscricao_estadual TEXT NOT NULL,
            email TEXT,
            contato TEXT,
            observacao TEXT
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM produtos')
    count = cursor.fetchone()[0]
    
    if count == 0:
        produtos_iniciais = [
            (2000000005805, 'Esmalte Base Água', 'Lukscolor', 'Dovac', 'GL', 10, 98.68, 46.84, 144.90, '', 5),
            (2000000001005, 'Rende Muito', 'Coral', 'Gama', 'LT', 8, 286.85, 39.41, 399.90, '', 5),
            (2047, 'Textura', 'Mega', 'Dado', 'LT', 5, 45.90, 52.29, 69.90,'', 3),
            (7896380105342, 'Trincha', 'Atlas', 'Atlas', 'PC', 22, 4.72, 101.27, 9.50, '', 15),
            (7895315003562, 'Martelo', 'Eda', 'Safari', 'PC', 12, 15.66, 50.06, 23.50, '', 8)
        ]
        cursor.executemany('''
            INSERT INTO produtos (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco, observacao, qtd_minima)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', produtos_iniciais)

    conn.commit()
    conn.close()

criar_banco_dados()

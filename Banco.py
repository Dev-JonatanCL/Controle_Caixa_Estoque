import sqlite3

def criar_banco_dados():
    # Conectar ao banco de dados (se não existir, será criado)
    conn = sqlite3.connect('produtos.db')
    cursor = conn.cursor()

    # Criar a tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            fabricante TEXT NOT NULL,
            fornecedor TEXT NOT NULL,
            unidade TEXT NOT NULL,
            qtd_estoque INTEGER NOT NULL,
            custo REAL NOT NULL,
            margem REAL NOT NULL,
            preco REAL NOT NULL
        )
    ''')

    # Inserir os dados iniciais na tabela (caso a tabela esteja vazia)
    cursor.execute('SELECT COUNT(*) FROM produtos')
    count = cursor.fetchone()[0]
    
    if count == 0:
        produtos_iniciais = [
            (2000000005805, 'Esmalte Base Água', 'Lukscolor', 'Dovac', 'GL', 10, 98.68, 46.84, 144.90),
            (2000000001005, 'Rende Muito', 'Coral', 'Gama', 'LT', 8, 286.85, 39.41, 399.90),
            (2047, 'Textura', 'Mega', 'Dado', 'LT', 5, 45.90, 52.29, 69.90),
            (7896380105342, 'Trincha', 'Atlas', 'Atlas', 'PC', 22, 4.72, 101.27, 9.50),
            (7895315003562, 'Martelo', 'Eda', 'Safari', 'PC', 12, 15.66, 50.06, 23.50)
        ]
        cursor.executemany('''
            INSERT INTO produtos (cod, descricao, fabricante, fornecedor, unidade, qtd_estoque, custo, margem, preco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', produtos_iniciais)

    conn.commit()
    conn.close()

criar_banco_dados()

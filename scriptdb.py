import mysql.connector
from faker import Faker
import random
from datetime import date, timedelta
import decimal

# --- CONFIGURAÇÃO ---
# Substitua com suas credenciais do banco de dados MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mineiro031212@',
    'database': 'CRMetais',
    'auth_plugin': 'mysql_native_password' # Adicionado para compatibilidade
}

# Número de registros a serem gerados para cada tabela principal
NUM_USUARIOS = 5
NUM_PRODUTOS = 25
NUM_CLIENTES = 50
NUM_FORNECEDORES = 30
TRANSACTIONS_PER_DAY = 25 # Média de transações a serem geradas por dia

# Inicializa o Faker para dados brasileiros
fake = Faker('pt_BR')

def create_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Conexão com o banco de dados bem-sucedida.")
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        exit()

def insert_static_data(cursor):
    """Insere dados estáticos que não mudam, como tipos de pagamento."""
    print("Inserindo dados estáticos (tipos_pagamento)...")
    tipos_pagamento = [
        ('PIX', 'Transferência instantânea via Chave PIX.'),
        ('TED', 'Transferência Eletrônica Disponível.'),
        ('DOC', 'Documento de Ordem de Crédito.'),
        ('BOLETO', 'Pagamento via boleto bancário.')
    ]
    cursor.executemany("INSERT INTO tipos_pagamento (nome, descricao) VALUES (%s, %s)", tipos_pagamento)
    print("Dados estáticos inseridos.")
    return {nome: i+1 for i, (nome, _) in enumerate(tipos_pagamento)}

def generate_and_insert_data(conn):
    """Função principal para gerar e inserir todos os dados."""
    cursor = conn.cursor()
    
    # Dicionário para armazenar os IDs dos registros gerados
    ids = {
        "usuario": [], "produto": [], "endereco": [], "tabela_preco": [],
        "cliente": [], "fornecedor": []
    }

    # 1. Dados Estáticos
    id_map_tipos_pagamento = insert_static_data(cursor)

    # 2. Usuários
    print(f"Inserindo {NUM_USUARIOS} usuários...")
    for _ in range(NUM_USUARIOS):
        sql = "INSERT INTO usuario (nome, senha, email) VALUES (%s, %s, %s)"
        # Nota: Em uma aplicação real, as senhas devem ser hasheadas corretamente!
        val = (fake.name(), fake.password(length=12), fake.unique.email())
        cursor.execute(sql, val)
        ids["usuario"].append(cursor.lastrowid)

    # 3. Produtos
    print(f"Inserindo {NUM_PRODUTOS} produtos...")
    tipos_metal = ['Cobre', 'Alumínio', 'Latão', 'Bronze', 'Aço Inox', 'Chumbo', 'Zinco']
    formatos = ['Vergalhão', 'Tubo', 'Chapa', 'Fio', 'Perfil', 'Pó']
    for _ in range(NUM_PRODUTOS):
        tipo = random.choice(tipos_metal)
        formato = random.choice(formatos)
        sql = "INSERT INTO produto (nome, tipo_produto) VALUES (%s, %s)"
        val = (f"{formato} de {tipo}", tipo)
        cursor.execute(sql, val)
        ids["produto"].append(cursor.lastrowid)

    # 4. Endereços (Cria um pool para ser usado por clientes e fornecedores)
    print(f"Inserindo {NUM_CLIENTES + NUM_FORNECEDORES} endereços...")
    for _ in range(NUM_CLIENTES + NUM_FORNECEDORES):
        sql = "INSERT INTO endereco (estado, cidade, bairro, logradouro, numero) VALUES (%s, %s, %s, %s, %s)"
        val = (fake.state_abbr(), fake.city(), fake.bairro(), fake.street_name(), fake.building_number())
        cursor.execute(sql, val)
        ids["endereco"].append(cursor.lastrowid)
    random.shuffle(ids["endereco"]) # Embaralha para atribuição aleatória

    # 5. Tabelas de Preço
    print("Inserindo tabelas de preço...")
    tabelas = [
        ('Compra Padrão', 'C', 1.0, date(2023, 1, 1), date(2025, 12, 31), 1),
        ('Venda Varejo', 'V', 1.0, date(2023, 1, 1), date(2025, 12, 31), 1),
        ('Venda Atacado', 'V', 1.0, date(2023, 1, 1), date(2025, 12, 31), 1)
    ]
    cursor.executemany("INSERT INTO tabela_preco (nome_tabela, tipo, versao, data_inicio_validade, data_fim_validade, ativa) VALUES (%s, %s, %s, %s, %s, %s)", tabelas)
    # Obtém os IDs das tabelas criadas
    for i in range(len(tabelas)):
        ids["tabela_preco"].append(i + 1)
    
    tabela_compra_id = ids["tabela_preco"][0]
    tabelas_venda_ids = ids["tabela_preco"][1:]

    # 6. Clientes
    print(f"Inserindo {NUM_CLIENTES} clientes...")
    for i in range(NUM_CLIENTES):
        sql = "INSERT INTO cliente (cnpj, razao_social, tel_contato, id_endereco, id_tabela_preco) VALUES (%s, %s, %s, %s, %s)"
        val = (
            fake.cnpj(), fake.company(), fake.msisdn(),
            ids["endereco"].pop(), random.choice(tabelas_venda_ids)
        )
        cursor.execute(sql, val)
        ids["cliente"].append(cursor.lastrowid)
        
    # 7. Fornecedores
    print(f"Inserindo {NUM_FORNECEDORES} fornecedores...")
    for i in range(NUM_FORNECEDORES):
        sql = "INSERT INTO fornecedor (id_tabela_preco, id_gestor, id_endereco, nome, cpf, telefone, apelido) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (
            tabela_compra_id, random.choice(ids["usuario"]), ids["endereco"].pop(),
            fake.name(), fake.cpf(), fake.msisdn(), fake.first_name()
        )
        cursor.execute(sql, val)
        fornecedor_id = cursor.lastrowid
        ids["fornecedor"].append(fornecedor_id)

        # 8. Dados Bancários do Fornecedor
        pagamento_tipo = random.choice(list(id_map_tipos_pagamento.keys()))
        id_tipo_pagamento = id_map_tipos_pagamento[pagamento_tipo]

        sql_dados = "INSERT INTO dados_bancarios_fornecedor (id_fornecedor, id_tipo_pagamento, descricao) VALUES (%s, %s, %s)"
        val_dados = (fornecedor_id, id_tipo_pagamento, f"Pagamento principal {pagamento_tipo}")
        cursor.execute(sql_dados, val_dados)
        id_dados_pagamento = cursor.lastrowid

        if pagamento_tipo == 'PIX':
            chave_tipo = random.choice(['CPF', 'Email', 'Telefone', 'Aleatória'])
            chave = ''
            if chave_tipo == 'CPF': chave = val[4]
            elif chave_tipo == 'Email': chave = fake.email()
            elif chave_tipo == 'Telefone': chave = val[5]
            else: chave = fake.uuid4()
            
            sql_detalhes = "INSERT INTO detalhes_pix (id_dados_pagamento, tipo_chave_pix, chave_pix) VALUES (%s, %s, %s)"
            cursor.execute(sql_detalhes, (id_dados_pagamento, chave_tipo, chave))
        else: # TED, DOC, BOLETO -> assume conta bancária
            sql_detalhes = "INSERT INTO detalhes_conta_bancaria (id_dados_pagamento, banco, agencia, conta, tipo_conta) VALUES (%s, %s, %s, %s, %s)"
            val_detalhes = (id_dados_pagamento, fake.company(), str(random.randint(1000,9999)), str(random.randint(10000, 999999)), random.choice(['CC', 'CP']))
            cursor.execute(sql_detalhes, val_detalhes)


    # 9. Preços Iniciais e Estoque
    print("Definindo preços iniciais e níveis de estoque...")
    for id_produto in ids["produto"]:
        # Estoque
        sql_estoque = "INSERT INTO estoque (id_produto, quantidade_disponivel, localizacao) VALUES (%s, %s, %s)"
        val_estoque = (id_produto, decimal.Decimal(random.uniform(500, 2000)).quantize(decimal.Decimal('0.001')), f"Prateleira {random.randint(1,20)}")
        cursor.execute(sql_estoque, val_estoque)
        
        # Preços
        for id_tabela in ids["tabela_preco"]:
            cursor.execute("SELECT tipo FROM tabela_preco WHERE id_tabela_preco = %s", (id_tabela,))
            tipo_tabela = cursor.fetchone()[0]
            
            # Preço de compra é menor que o de venda
            if tipo_tabela == 'C':
                preco_base = decimal.Decimal(random.uniform(5.0, 50.0))
            else:
                preco_base = decimal.Decimal(random.uniform(55.0, 150.0))
                
            sql_preco = "INSERT INTO preco_produto_tabela (id_produto, id_tabela_preco, preco_produto) VALUES (%s, %s, %s)"
            val_preco = (id_produto, id_tabela, preco_base.quantize(decimal.Decimal('0.01')))
            cursor.execute(sql_preco, val_preco)
    
    conn.commit()
    print("--- Inserção de dados base concluída ---")

    # 10. Gera Transações ao longo de um ano
    print("\n--- Gerando transações para um ano inteiro ---")
    start_date = date.today() - timedelta(days=365)
    end_date = date.today()
    current_date = start_date
    
    while current_date <= end_date:
        print(f"Processando data: {current_date.strftime('%Y-%m-%d')}")
        
        # Simulação de atualização mensal de preços
        if current_date.day == 1:
            print(f"  -> Aplicando ajustes mensais de preço para {current_date.strftime('%B')}...")
            cursor.execute("SELECT id_produto, id_tabela_preco, preco_produto FROM preco_produto_tabela")
            precos = cursor.fetchall()
            for id_prod, id_tab, preco in precos:
                ajuste = decimal.Decimal(random.uniform(0.99, 1.03)) # Variação de -1% a +3%
                novo_preco = (preco * ajuste).quantize(decimal.Decimal('0.01'))
                cursor.execute("UPDATE preco_produto_tabela SET preco_produto = %s WHERE id_produto = %s AND id_tabela_preco = %s", (novo_preco, id_prod, id_tab))
            conn.commit()

        # Transações diárias
        for _ in range(random.randint(1, TRANSACTIONS_PER_DAY * 2)):
            if random.random() < 0.4: # 40% de chance de ser uma compra
                # --- COMPRA ---
                id_fornecedor = random.choice(ids["fornecedor"])
                
                cursor.execute("INSERT INTO compra (id_fornecedor, data_compra) VALUES (%s, %s)", (id_fornecedor, current_date))
                id_compra = cursor.lastrowid
                
                # Itens da compra
                num_items = random.randint(1, 4)
                # Seleciona uma amostra única de produtos para esta compra
                produtos_na_compra = random.sample(ids["produto"], num_items)
                for id_produto_compra in produtos_na_compra:
                    
                    # Obtém o preço da tabela do fornecedor
                    cursor.execute("""
                        SELECT ppt.preco_produto FROM preco_produto_tabela ppt
                        JOIN fornecedor f ON ppt.id_tabela_preco = f.id_tabela_preco
                        WHERE f.id_fornecedor = %s AND ppt.id_produto = %s
                    """, (id_fornecedor, id_produto_compra))
                    result = cursor.fetchone()
                    if result:
                        preco_unitario = result[0] * decimal.Decimal(random.uniform(0.98, 1.02)) # pequena variação de negociação
                        peso = decimal.Decimal(random.uniform(10.0, 300.0)).quantize(decimal.Decimal('0.001'))
                        
                        # Insere o item
                        cursor.execute("""
                            INSERT INTO item_pedido_compra (id_compra, id_produto, peso_kg, preco_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (id_compra, id_produto_compra, peso, preco_unitario.quantize(decimal.Decimal('0.01'))))
                        
                        # Atualiza o Estoque
                        cursor.execute("UPDATE estoque SET quantidade_disponivel = quantidade_disponivel + %s WHERE id_produto = %s", (peso, id_produto_compra))

            else:
                # --- VENDA ---
                id_cliente = random.choice(ids["cliente"])
                cursor.execute("SELECT id_tabela_preco FROM cliente WHERE id_cliente = %s", (id_cliente,))
                id_tabela_venda = cursor.fetchone()[0]

                cursor.execute("INSERT INTO venda (id_cliente, id_tabela_preco, dt_venda) VALUES (%s, %s, %s)", (id_cliente, id_tabela_venda, current_date))
                id_venda = cursor.lastrowid
                
                # Itens da venda
                num_items = random.randint(1, 5)
                 # Seleciona uma amostra única de produtos para esta venda
                produtos_na_venda = random.sample(ids["produto"], num_items)
                for id_produto_venda in produtos_na_venda:
                    
                    # Verifica o estoque
                    cursor.execute("SELECT quantidade_disponivel FROM estoque WHERE id_produto = %s", (id_produto_venda,))
                    estoque_disponivel = cursor.fetchone()[0]
                    
                    if estoque_disponivel > 20: # Só vende se houver um estoque mínimo
                        # Obtém o preço da tabela do cliente
                        cursor.execute("SELECT preco_produto FROM preco_produto_tabela WHERE id_produto = %s AND id_tabela_preco = %s", (id_produto_venda, id_tabela_venda))
                        result = cursor.fetchone()
                        if result:
                            preco_unitario = result[0] * decimal.Decimal(random.uniform(1.0, 1.05))
                            peso_max = min(float(estoque_disponivel), 500.0)
                            peso = decimal.Decimal(random.uniform(10.0, peso_max)).quantize(decimal.Decimal('0.001'))
                            
                            # Insere o item
                            cursor.execute("""
                                INSERT INTO item_pedido_venda (id_venda, id_produto, peso_kg, preco_unitario)
                                VALUES (%s, %s, %s, %s)
                            """, (id_venda, id_produto_venda, peso, preco_unitario.quantize(decimal.Decimal('0.01'))))
                            
                            # Atualiza o Estoque
                            cursor.execute("UPDATE estoque SET quantidade_disponivel = quantidade_disponivel - %s WHERE id_produto = %s", (peso, id_produto_venda))
        
        conn.commit() # Confirma as transações do dia
        current_date += timedelta(days=1)
        
    print("\n--- Geração de transações anuais concluída! ---")
    cursor.close()

if __name__ == '__main__':
    conn = create_connection()
    if conn:
        try:
            generate_and_insert_data(conn)
        except mysql.connector.Error as err:
            print(f"Um erro ocorreu: {err}")
        finally:
            conn.close()
            print("Conexão com o banco de dados fechada.")


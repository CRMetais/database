import mysql.connector
import pandas as pd
import random

# --- CONFIGURAÇÃO ---
# As credenciais devem ser as mesmas usadas no script de população.
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mineiro031212@',
    'database': 'CRMetais',
    'auth_plugin': 'mysql_native_password'
}

def create_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Conexão com o banco de dados bem-sucedida.\n")
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

def run_query_to_dataframe(conn, query, params=None):
    """Executa uma query e retorna o resultado como um DataFrame do pandas."""
    try:
        # Usar pd.read_sql_query para obter os dados e nomes das colunas
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Erro ao executar a query: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

def validate_data(conn):
    """Executa várias queries de validação e exibe os resultados."""

    print("--- 1. VALIDAÇÃO DE DADOS HISTÓRICOS DE PREÇOS ---")
    print("Verificando a flutuação de preço de um produto aleatório ao longo do tempo.\n")
    
    # Pega um ID de produto aleatório que tenha sido vendido
    find_product_id_query = "SELECT DISTINCT id_produto FROM item_pedido_venda ORDER BY RAND() LIMIT 1"
    product_df = run_query_to_dataframe(conn, find_product_id_query)
    if not product_df.empty:
        random_product_id = product_df.iloc[0]['id_produto']
        print(f"Produto selecionado: ID {random_product_id}")

        price_history_query = """
            SELECT 
                p.nome,
                v.dt_venda,
                iv.preco_unitario
            FROM venda v
            JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
            JOIN produto p ON iv.id_produto = p.id_produto
            WHERE iv.id_produto = %s
            ORDER BY v.dt_venda
            LIMIT 10;
        """
        price_history_df = run_query_to_dataframe(conn, price_history_query, params=(random_product_id,))
        print("Histórico de preços de VENDA para o produto:")
        print(price_history_df.to_string(index=False))
        print("-" * 50 + "\n")
    else:
        print("Nenhum produto vendido encontrado para verificar o histórico.\n")


    print("--- 2. VALIDAÇÃO DE REGRAS DE NEGÓCIO: CONSOLIDAÇÃO MENSAL ---")
    print("Agrupando o total de compras e vendas por mês para análise de volume.\n")
    
    sales_by_month_query = """
        SELECT 
            DATE_FORMAT(v.dt_venda, '%Y-%m') AS mes,
            SUM(iv.peso_kg) AS total_peso_vendido_kg,
            SUM(iv.peso_kg * iv.preco_unitario) AS faturamento_total
        FROM venda v
        JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
        GROUP BY mes
        ORDER BY mes;
    """
    sales_by_month_df = run_query_to_dataframe(conn, sales_by_month_query)
    # Formatando a coluna de faturamento para Reais (R$)
    sales_by_month_df['faturamento_total'] = sales_by_month_df['faturamento_total'].map('R$ {:,.2f}'.format)
    sales_by_month_df['total_peso_vendido_kg'] = sales_by_month_df['total_peso_vendido_kg'].map('{:,.3f} kg'.format)

    print("Resumo de VENDAS por Mês:")
    print(sales_by_month_df.to_string(index=False))
    print("-" * 50 + "\n")

    purchases_by_month_query = """
        SELECT 
            DATE_FORMAT(c.data_compra, '%Y-%m') AS mes,
            SUM(ic.peso_kg) AS total_peso_comprado_kg,
            SUM(ic.peso_kg * ic.preco_unitario) AS custo_total
        FROM compra c
        JOIN item_pedido_compra ic ON c.id_compra = ic.id_compra
        GROUP BY mes
        ORDER BY mes;
    """
    purchases_by_month_df = run_query_to_dataframe(conn, purchases_by_month_query)
    purchases_by_month_df['custo_total'] = purchases_by_month_df['custo_total'].map('R$ {:,.2f}'.format)
    purchases_by_month_df['total_peso_comprado_kg'] = purchases_by_month_df['total_peso_comprado_kg'].map('{:,.3f} kg'.format)
    
    print("Resumo de COMPRAS por Mês:")
    print(purchases_by_month_df.to_string(index=False))
    print("-" * 50 + "\n")

    
    print("--- 3. ANÁLISE DE RANKING: MELHORES CLIENTES E FORNECEDORES ---")
    print("Calculando o valor total de negócios para classificar clientes e fornecedores.\n")

    top_clients_query = """
        SELECT 
            cl.razao_social,
            SUM(iv.peso_kg * iv.preco_unitario) AS faturamento_gerado
        FROM cliente cl
        JOIN venda v ON cl.id_cliente = v.id_cliente
        JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
        GROUP BY cl.id_cliente
        ORDER BY faturamento_gerado DESC
        LIMIT 5;
    """
    top_clients_df = run_query_to_dataframe(conn, top_clients_query)
    top_clients_df['faturamento_gerado'] = top_clients_df['faturamento_gerado'].map('R$ {:,.2f}'.format)
    
    print("Top 5 Clientes por Faturamento:")
    print(top_clients_df.to_string(index=False))
    print("-" * 50 + "\n")

    top_suppliers_query = """
        SELECT 
            f.nome,
            SUM(ic.peso_kg * ic.preco_unitario) AS valor_total_comprado
        FROM fornecedor f
        JOIN compra c ON f.id_fornecedor = c.id_fornecedor
        JOIN item_pedido_compra ic ON c.id_compra = ic.id_compra
        GROUP BY f.id_fornecedor
        ORDER BY valor_total_comprado DESC
        LIMIT 5;
    """
    top_suppliers_df = run_query_to_dataframe(conn, top_suppliers_query)
    top_suppliers_df['valor_total_comprado'] = top_suppliers_df['valor_total_comprado'].map('R$ {:,.2f}'.format)
    
    print("Top 5 Fornecedores por Volume de Compra:")
    print(top_suppliers_df.to_string(index=False))
    print("-" * 50 + "\n")


    print("--- 4. VERIFICAÇÃO DE ESTOQUE ---")
    print("Analisando os produtos com maior e menor estoque disponível.\n")

    stock_levels_query = """
        SELECT
            p.nome,
            e.quantidade_disponivel,
            e.localizacao
        FROM estoque e
        JOIN produto p ON e.id_produto = p.id_produto
        ORDER BY e.quantidade_disponivel DESC
        LIMIT 5;
    """
    highest_stock_df = run_query_to_dataframe(conn, stock_levels_query)
    highest_stock_df['quantidade_disponivel'] = highest_stock_df['quantidade_disponivel'].map('{:,.3f} kg'.format)
    
    print("Top 5 Produtos com MAIOR Estoque:")
    print(highest_stock_df.to_string(index=False))
    print("-" * 50 + "\n")

    stock_levels_query_asc = stock_levels_query.replace("DESC", "ASC")
    lowest_stock_df = run_query_to_dataframe(conn, stock_levels_query_asc)
    lowest_stock_df['quantidade_disponivel'] = lowest_stock_df['quantidade_disponivel'].map('{:,.3f} kg'.format)
    
    print("Top 5 Produtos com MENOR Estoque:")
    print(lowest_stock_df.to_string(index=False))
    print("-" * 50 + "\n")


if __name__ == '__main__':
    conn = create_connection()
    if conn:
        try:
            validate_data(conn)
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante a validação: {e}")
        finally:
            conn.close()
            print("Conexão com o banco de dados fechada.")

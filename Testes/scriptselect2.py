import mysql.connector
import pandas as pd

# --- CONFIGURAÇÃO ---
# As credenciais devem ser as mesmas usadas nos scripts anteriores.
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mineiro031212@',
    'database': 'CRMetais',
    'auth_plugin': 'mysql_native_password'
}

# Configuração do Pandas para exibir todas as colunas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def create_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Conexão com o banco de dados bem-sucedida.\n")
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

def run_query(conn, title, query, params=None, format_cols=None):
    """Executa uma query, formata e exibe o resultado."""
    print(f"--- {title} ---")
    try:
        df = pd.read_sql_query(query, conn, params=params)
        
        # Aplica formatação se especificado
        if format_cols and not df.empty:
            for col, fmt_str in format_cols.items():
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: fmt_str.format(x) if pd.notnull(x) else 'N/A')

        if df.empty:
            print("Nenhum resultado encontrado.\n")
        else:
            print(df.to_string(index=False))
            print("\n")
            
    except Exception as e:
        print(f"Erro ao executar a query: {e}\n")

def main():
    """Função principal que executa todas as consultas de teste."""
    conn = create_connection()
    if not conn:
        return

    # =================================================================
    # 1. ANÁLISES DE PREÇOS E HISTÓRICO
    # =================================================================
    
    # 1.1 Histórico de preço de VENDA de um produto específico
    run_query(conn, "1.1 Histórico de preço de VENDA do produto ID 5", """
        SELECT v.dt_venda, p.nome, iv.preco_unitario 
        FROM item_pedido_venda iv
        JOIN venda v ON iv.id_venda = v.id_venda
        JOIN produto p ON iv.id_produto = p.id_produto
        WHERE iv.id_produto = 5 ORDER BY v.dt_venda DESC LIMIT 5;
    """, format_cols={'preco_unitario': 'R$ {:.2f}'})

    # 1.2 Histórico de preço de COMPRA de um produto específico
    run_query(conn, "1.2 Histórico de preço de COMPRA do produto ID 5", """
        SELECT c.data_compra, p.nome, ic.preco_unitario 
        FROM item_pedido_compra ic
        JOIN compra c ON ic.id_compra = c.id_compra
        JOIN produto p ON ic.id_produto = p.id_produto
        WHERE ic.id_produto = 5 ORDER BY c.data_compra DESC LIMIT 5;
    """, format_cols={'preco_unitario': 'R$ {:.2f}'})

    # 1.3 Preços atuais de todos os produtos na tabela 'Venda Varejo'
    run_query(conn, "1.3 Preços na Tabela 'Venda Varejo'", """
        SELECT p.nome, ppt.preco_produto
        FROM preco_produto_tabela ppt
        JOIN produto p ON ppt.id_produto = p.id_produto
        JOIN tabela_preco tp ON ppt.id_tabela_preco = tp.id_tabela_preco
        WHERE tp.nome_tabela = 'Venda Varejo' LIMIT 10;
    """, format_cols={'preco_produto': 'R$ {:.2f}'})
    
    # 1.4 Produtos com maior aumento de preço no último mês (comparando preço médio)
    run_query(conn, "1.4 Produtos com maior aumento de preço de venda no último mês", """
        SELECT 
            p.nome, 
            AVG(CASE WHEN v.dt_venda >= DATE_SUB(NOW(), INTERVAL 2 MONTH) AND v.dt_venda < DATE_SUB(NOW(), INTERVAL 1 MONTH) THEN iv.preco_unitario END) as preco_mes_passado,
            AVG(CASE WHEN v.dt_venda >= DATE_SUB(NOW(), INTERVAL 1 MONTH) THEN iv.preco_unitario END) as preco_mes_atual
        FROM item_pedido_venda iv
        JOIN venda v ON iv.id_venda = v.id_venda
        JOIN produto p ON iv.id_produto = p.id_produto
        GROUP BY p.id_produto
        HAVING preco_mes_passado IS NOT NULL AND preco_mes_atual IS NOT NULL
        ORDER BY (preco_mes_atual - preco_mes_passado) DESC LIMIT 5;
    """, format_cols={'preco_mes_passado': 'R$ {:.2f}', 'preco_mes_atual': 'R$ {:.2f}'})

    # =================================================================
    # 2. ANÁLISES DE CLIENTES
    # =================================================================
    
    # 2.1 Top 10 Clientes por VALOR total comprado
    run_query(conn, "2.1 Top 10 Clientes por VALOR (R$) total comprado", """
        SELECT c.razao_social, SUM(iv.preco_unitario * iv.peso_kg) as valor_total
        FROM cliente c
        JOIN venda v ON c.id_cliente = v.id_cliente
        JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
        GROUP BY c.id_cliente ORDER BY valor_total DESC LIMIT 10;
    """, format_cols={'valor_total': 'R$ {:,.2f}'})
    
    # 2.2 Top 10 Clientes por PESO total comprado
    run_query(conn, "2.2 Top 10 Clientes por PESO (kg) total comprado", """
        SELECT c.razao_social, SUM(iv.peso_kg) as peso_total
        FROM cliente c
        JOIN venda v ON c.id_cliente = v.id_cliente
        JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
        GROUP BY c.id_cliente ORDER BY peso_total DESC LIMIT 10;
    """, format_cols={'peso_total': '{:,.3f} kg'})
    
    # 2.3 Produtos mais comprados por um cliente específico (cliente com ID 1)
    run_query(conn, "2.3 Produtos mais comprados pelo Cliente ID 1", """
        SELECT p.nome, SUM(iv.peso_kg) as total_kg
        FROM item_pedido_venda iv
        JOIN venda v ON iv.id_venda = v.id_venda
        JOIN produto p ON iv.id_produto = p.id_produto
        WHERE v.id_cliente = 1
        GROUP BY p.id_produto ORDER BY total_kg DESC LIMIT 5;
    """, format_cols={'total_kg': '{:,.3f} kg'})

    # 2.4 Clientes inativos (sem compras há mais de 180 dias)
    run_query(conn, "2.4 Clientes sem compras há mais de 180 dias", """
        SELECT id_cliente, razao_social, tel_contato, MAX(v.dt_venda) as ultima_compra
        FROM cliente c
        LEFT JOIN venda v ON c.id_cliente = v.id_cliente
        GROUP BY c.id_cliente
        HAVING ultima_compra < DATE_SUB(NOW(), INTERVAL 180 DAY) OR ultima_compra IS NULL
        LIMIT 10;
    """)

    # =================================================================
    # 3. ANÁLISES DE FORNECEDORES
    # =================================================================

    # 3.1 Top 10 Fornecedores por VALOR total vendido para a empresa
    run_query(conn, "3.1 Top 10 Fornecedores por VALOR (R$) total de compras", """
        SELECT f.nome, SUM(ic.preco_unitario * ic.peso_kg) as valor_total
        FROM fornecedor f
        JOIN compra c ON f.id_fornecedor = c.id_fornecedor
        JOIN item_pedido_compra ic ON c.id_compra = ic.id_compra
        GROUP BY f.id_fornecedor ORDER BY valor_total DESC LIMIT 10;
    """, format_cols={'valor_total': 'R$ {:,.2f}'})

    # 3.2 Top 10 Fornecedores por PESO total vendido para a empresa
    run_query(conn, "3.2 Top 10 Fornecedores por PESO (kg) total de compras", """
        SELECT f.nome, SUM(ic.peso_kg) as peso_total
        FROM fornecedor f
        JOIN compra c ON f.id_fornecedor = c.id_fornecedor
        JOIN item_pedido_compra ic ON c.id_compra = ic.id_compra
        GROUP BY f.id_fornecedor ORDER BY peso_total DESC LIMIT 10;
    """, format_cols={'peso_total': '{:,.3f} kg'})
    
    # 3.3 Fornecedores por estado
    run_query(conn, "3.3 Contagem de fornecedores por Estado", """
        SELECT e.estado, COUNT(f.id_fornecedor) as total_fornecedores
        FROM fornecedor f
        JOIN endereco e ON f.id_endereco = e.id_endereco
        GROUP BY e.estado ORDER BY total_fornecedores DESC;
    """)

    # =================================================================
    # 4. ANÁLISES DE PRODUTOS E ESTOQUE
    # =================================================================
    
    # 4.1 Produtos MAIS vendidos em VALOR (R$)
    run_query(conn, "4.1 Top 10 Produtos MAIS vendidos em VALOR (R$)", """
        SELECT p.nome, SUM(iv.preco_unitario * iv.peso_kg) as faturamento
        FROM item_pedido_venda iv
        JOIN produto p ON iv.id_produto = p.id_produto
        GROUP BY p.id_produto ORDER BY faturamento DESC LIMIT 10;
    """, format_cols={'faturamento': 'R$ {:,.2f}'})

    # 4.2 Produtos MENOS vendidos em PESO (kg)
    run_query(conn, "4.2 Top 10 Produtos MENOS vendidos em PESO (kg)", """
        SELECT p.nome, SUM(iv.peso_kg) as total_vendido_kg
        FROM item_pedido_venda iv
        JOIN produto p ON iv.id_produto = p.id_produto
        GROUP BY p.id_produto ORDER BY total_vendido_kg ASC LIMIT 10;
    """, format_cols={'total_vendido_kg': '{:,.3f} kg'})
    
    # 4.3 Valor total do estoque atual (preço de custo)
    run_query(conn, "4.3 Valor total do estoque atual (usando último preço de compra)", """
        SELECT SUM(e.quantidade_disponivel * COALESCE(last_price.preco, 0)) as valor_total_estoque
        FROM estoque e
        LEFT JOIN (
            SELECT ic.id_produto, ic.preco_unitario as preco
            FROM item_pedido_compra ic
            JOIN (
                SELECT id_produto, MAX(id_compra) as max_compra_id
                FROM item_pedido_compra GROUP BY id_produto
            ) as latest_compra ON ic.id_produto = latest_compra.id_produto AND ic.id_compra = latest_compra.max_compra_id
        ) as last_price ON e.id_produto = last_price.id_produto;
    """, format_cols={'valor_total_estoque': 'R$ {:,.2f}'})
    
    # 4.4 Produtos que nunca foram vendidos
    run_query(conn, "4.4 Produtos que nunca foram vendidos", """
        SELECT p.id_produto, p.nome
        FROM produto p
        LEFT JOIN item_pedido_venda iv ON p.id_produto = iv.id_produto
        WHERE iv.id_venda IS NULL;
    """)
    
    # =================================================================
    # 5. ANÁLISES FINANCEIRAS E OPERACIONAIS
    # =================================================================

    # 5.1 Faturamento Bruto Mensal
    run_query(conn, "5.1 Faturamento Bruto Mensal", """
        SELECT DATE_FORMAT(v.dt_venda, '%Y-%m') as mes, SUM(iv.preco_unitario * iv.peso_kg) as faturamento
        FROM venda v
        JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
        GROUP BY mes ORDER BY mes;
    """, format_cols={'faturamento': 'R$ {:,.2f}'})
    
    # 5.2 Custo Total de Compra Mensal
    run_query(conn, "5.2 Custo Total de Compra Mensal", """
        SELECT DATE_FORMAT(c.data_compra, '%Y-%m') as mes, SUM(ic.preco_unitario * ic.peso_kg) as custo
        FROM compra c
        JOIN item_pedido_compra ic ON c.id_compra = ic.id_compra
        GROUP BY mes ORDER BY mes;
    """, format_cols={'custo': 'R$ {:,.2f}'})

    # 5.3 Balanço Mensal Simplificado (Faturamento vs Custo)
    run_query(conn, "5.3 Balanço Mensal Simplificado (Faturamento vs Custo)", """
        SELECT 
            mes,
            SUM(faturamento) as total_faturamento,
            SUM(custo) as total_custo,
            SUM(faturamento - custo) as lucro_bruto
        FROM (
            SELECT DATE_FORMAT(v.dt_venda, '%Y-%m') as mes, SUM(iv.peso_kg * iv.preco_unitario) as faturamento, 0 as custo
            FROM venda v JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda GROUP BY mes
            UNION ALL
            SELECT DATE_FORMAT(c.data_compra, '%Y-%m') as mes, 0 as faturamento, SUM(ic.peso_kg * ic.preco_unitario) as custo
            FROM compra c JOIN item_pedido_compra ic ON c.id_compra = ic.id_compra GROUP BY mes
        ) as balanco
        GROUP BY mes ORDER BY mes;
    """, format_cols={'total_faturamento': 'R$ {:,.2f}', 'total_custo': 'R$ {:,.2f}', 'lucro_bruto': 'R$ {:,.2f}'})
    
    # 5.4 Dia da semana com maior volume de vendas (em R$)
    run_query(conn, "5.4 Dia da semana com maior volume de vendas (em R$)", """
        SELECT DAYNAME(v.dt_venda) as dia_semana, SUM(iv.peso_kg * iv.preco_unitario) as faturamento
        FROM venda v
        JOIN item_pedido_venda iv ON v.id_venda = iv.id_venda
        GROUP BY dia_semana
        ORDER BY faturamento DESC;
    """, format_cols={'faturamento': 'R$ {:,.2f}'})


    if conn and conn.is_connected():
        conn.close()
        print("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    main()

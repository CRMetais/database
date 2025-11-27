USE crmetais;
SHOW TABLES;

-- ============================
-- VIEW: histórico de entrada
-- ============================

CREATE OR REPLACE VIEW vw_historico_entradas AS
SELECT 
    c.id_compra,
    c.data_compra,
    f.nome AS fornecedor,
    p.nome AS produto,
    i.peso_kg AS quantidade_kg,
    i.preco_unitario,
    (i.peso_kg * i.preco_unitario) AS total_item
FROM item_pedido_compra i
JOIN compra c ON c.id_compra = i.id_fk_compra
JOIN fornecedor f ON f.id_fornecedor = c.fk_fornecedor
JOIN produto p ON p.id_produto = i.id_fk_produto
ORDER BY c.data_compra DESC;

Select * From vw_historico_entradas;

-- ============================
-- VIEW: histórico de saída
-- ============================

CREATE OR REPLACE VIEW vw_historico_saidas AS
SELECT 
    v.id_venda,
    v.data_venda,
    cli.razao_social AS cliente,
    p.nome AS produto,
    i.peso_kg AS quantidade_kg,
    i.preco_unitario,
    (i.peso_kg * i.preco_unitario) AS total_item
FROM item_pedido_venda i
JOIN venda v ON v.id_venda = i.id_fk_venda
JOIN cliente cli ON cli.id_cliente = v.fk_cliente
JOIN produto p ON p.id_produto = i.id_fk_produto
ORDER BY v.data_venda DESC;

SELECT * FROM vw_historico_saidas;

-- ============================
-- VIEW: Visualização de Clientes com seus respectivos dados
-- ============================

CREATE OR REPLACE VIEW vw_clientes_view AS 
SELECT 
    c.id_cliente,
    c.CNPJ,
    c.razao_social,
    c.tel_contato,
    e.cidade,
    e.estado,
    e.bairro,
    e.logradouro,
    e.numero,
    e.cep,
    tp.nome_tabela AS tabela_preco,
    tp.tipo,
    tp.versao
FROM cliente c
LEFT JOIN endereco e 
       ON e.id_endereco = c.fk_endereco
LEFT JOIN tabela_preco tp 
       ON tp.id_tabela = c.fk_tabela_preco;


SELECT * FROM vw_clientes_view;


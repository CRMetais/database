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


CREATE OR REPLACE VIEW vw_fornecedor_view AS
SELECT
    f.id_fornecedor AS id_fornecedor,
    f.apelido AS apelido,
    f.documento AS cpf_cnpj_fornecedor,
    f.telefone AS telefone,
    f.tipo_fornecedor AS tipo_fornecedor,
    e.cidade AS cidade,
    e.estado AS estado,
    e.bairro AS bairro,
    e.logradouro AS logradouro,
    e.numero AS numero,
    e.cep AS cep,
    tp.nome_tabela AS tabela_preco_nome,
    tp.tipo AS tabela_preco_tipo,
    tp.versao AS tabela_preco_versao,
    c.agencia AS agencia,
    c.banco AS banco,
    c.chave_pix AS chave_pix,
    c.conta AS conta,
    c.tipo_conta AS tipo_conta,
    c.pertence_fornecedor AS conta_pertence_fornecedor,
    c.nome AS titular_conta_nome,
    c.documento AS cpf_cnpj_titular_conta,
    ult_compra.data_compra AS data_ultima_compra,
    CASE
        WHEN ult_compra.data_compra IS NULL THEN 0
        WHEN ult_compra.data_compra < DATE_SUB(CURDATE(), INTERVAL 3 MONTH) THEN 0
        ELSE 1
    END AS conta_ativa
FROM fornecedor f
LEFT JOIN endereco e 
    ON e.id_endereco = f.fk_endereco
LEFT JOIN tabela_preco tp 
    ON tp.id_tabela = f.fk_tabela_preco
LEFT JOIN conta_pagamento c 
    ON c.fk_fornecedor = f.id_fornecedor
LEFT JOIN (
    SELECT fk_fornecedor, MAX(data_compra) AS data_compra
    FROM compra
    GROUP BY fk_fornecedor
) ult_compra 
    ON ult_compra.fk_fornecedor = f.id_fornecedor;

select * from vw_fornecedor_view;


-- VIEWS TABELA DE PRECO SEM MARGEM
CREATE OR REPLACE VIEW vw_tabela_preco_familia_view AS
SELECT 
p.id_produto,
p.nome as produto,
p.tipo_produto,
pt.preco_produto as preco_kg,
t.nome_tabela as tabela
from produto as p
left join preco_produto_tabela as pt
on pt.fk_produto = p.id_produto
left join tabela_preco as t
on pt.fk_tabela_preco = t.id_tabela
where t.nome_tabela = "Tabela Família";

CREATE OR REPLACE VIEW vw_tabela_preco_padrao_view AS
SELECT 
p.id_produto,
p.nome as produto,
p.tipo_produto,
pt.preco_produto as preco_kg,
t.nome_tabela as tabela
from produto as p
left join preco_produto_tabela as pt
on pt.fk_produto = p.id_produto
left join tabela_preco as t
on pt.fk_tabela_preco = t.id_tabela
where t.nome_tabela = "Tabela Padrão";

select * from vw_tabela_preco_familia_view;

select * from vw_tabela_preco_padrao_view;

-- Margem dos precos 

CREATE OR REPLACE VIEW vw_margem_produto AS
SELECT 
    p_compra.id_produto AS id_produto_compra,
    p_venda.id_produto AS id_produto_venda,
    p_compra.nome AS produto,
    p_compra.tipo_produto,

    -- preços
    preco_compra.preco_produto AS preco_kg_compra,
    preco_venda.preco_produto AS preco_kg_venda,

    -- margem absoluta
    (preco_venda.preco_produto - preco_compra.preco_produto) AS margem_kg,

    -- margem percentual
    ROUND(
        (preco_venda.preco_produto - preco_compra.preco_produto)
        / preco_compra.preco_produto * 100,
        2
    ) AS margem_percentual

FROM produto p_compra
JOIN preco_produto_tabela preco_compra
    ON preco_compra.fk_produto = p_compra.id_produto
JOIN tabela_preco t_compra
    ON t_compra.id_tabela = preco_compra.fk_tabela_preco
   AND t_compra.tipo = 'C'
   AND t_compra.nome_tabela = 'Tabela Padrão'


JOIN produto p_venda
    ON p_venda.nome = p_compra.nome

JOIN preco_produto_tabela preco_venda
    ON preco_venda.fk_produto = p_venda.id_produto
JOIN tabela_preco t_venda
    ON t_venda.id_tabela = preco_venda.fk_tabela_preco
   AND t_venda.tipo = 'V'
   AND t_venda.nome_tabela = 'Vital';


select * from vw_margem_produto;


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


-- VIEWS TABELA DE PRECO 
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
where t.nome_tabela = "Família";

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
where t.nome_tabela = "Padrão";

CREATE OR REPLACE VIEW vw_tabela_preco_vital_view AS
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
where t.nome_tabela = "Vital";

select * from vw_tabela_preco_familia_view;

select * from vw_tabela_preco_padrao_view;


-- VIEWS DASHBOARD
-- RENDIMENTO, TOTAL APLICADO E PESO POR PERIODO 

CREATE OR REPLACE VIEW vw_rendimento_peso_total_periodo_view as 
select round(sum(ic.rendimento),2) as Rendimento, round(sum(ic.peso_kg * ic.preco_unitario),2) as Total_Aplicado, 
sum(ic.peso_kg) as Peso_Total
from item_pedido_compra ic join compra
on ic.id_fk_compra = compra.id_compra
where compra.data_compra between '2025-11-03' and '2025-11-09';

select * from vw_rendimento_peso_total_periodo_view;

-- top10 produtos com maior rendimento
CREATE OR REPLACE VIEW vw_top10_produtos_rendimento AS
SELECT 
    p.nome AS produto,
    ROUND(SUM(ic.rendimento), 2) AS rendimento_total
FROM item_pedido_compra ic
JOIN produto p ON ic.id_fk_produto = p.id_produto
GROUP BY p.id_produto, p.nome
ORDER BY rendimento_total DESC
LIMIT 10;

select * from vw_top10_produtos_rendimento;


-- top 10 fornecedores com maior rendimento
CREATE OR REPLACE VIEW vw_top10_fornecedores_rendimento AS
SELECT 
    f.nome AS fornecedor,
    ROUND(SUM(ic.rendimento), 2) AS rendimento_total
FROM item_pedido_compra ic
JOIN compra c ON ic.id_fk_compra = c.id_compra
JOIN fornecedor f ON c.fk_fornecedor = f.id_fornecedor
GROUP BY f.id_fornecedor, f.nome
ORDER BY rendimento_total DESC
LIMIT 10;

select * from vw_top10_fornecedores_rendimento;




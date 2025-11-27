-- DROP DATABASE crmetais;
-- CREATE DATABASE crmetais;
use crmetais;
show tables;


-- ============================
-- TABELA: usuario
-- ============================
INSERT INTO usuario (id_usuario, nome, senha, email, cargo)
VALUES
(1, 'Celco Ricardo', '123456', 'joao@empresa.com', 'Administrador'),
(null, 'Maria Oliveira', '123456', 'maria@empresa.com', 'Funcionario');

-- ============================
-- TABELA: endereco
-- ============================
INSERT INTO endereco (id_endereco, estado, cidade, bairro, logradouro, numero, cep)
VALUES
(null, 'SP', 'São Paulo', 'Centro', 'jaragua', 100, '01001000'),
(null, 'RJ', 'Angra dos Reis', 'sla kkkkk', 'Av Atlântica', 200, '22021001'),
(null, 'SP', 'São Paulo', 'Savassi', 'Rua da Bahia', 300, '30160010'),
(null, 'SP', 'Sâo Paulo', 'Batel', 'Av Sete de Setembro', 400, '80030010');

-- ============================
-- TABELA: fornecedor
-- ============================
INSERT INTO fornecedor (id_fornecedor, fk_endereco, nome, documento, telefone, apelido)
VALUES
(null, 1, 'metalManeiro', '12345678000199', '11999990000', 'FzVerde'),
(null, 2, 'metaleirosHAHAHAHAHAHHA', '98765432000166', '21988887777', 'SaborCamp');

-- ============================
-- TABELA: conta_pagamento
-- ============================
INSERT INTO conta_pagamento (id_conta_pagamento, pix, banco, agencia, conta, tipo_conta, chave_pix,
                             nome, pertence_fornecedor, documento, conta_ativa, fk_fornecedor)
VALUES
(null, 1, 'Banco do Brasil', '1234', '56789-0', 'C', '11999990000', 'João Metal Maneiro',
 1, '12345678000199', 1, 1),

(null, 0, 'Caixa', '4321', '12345-9', 'P', 'fazenda@sabor.com',
 'Sabor do Campo', 0, '98765432000166', 1, 2);

-- ============================
-- TABELA: tabela_preco
-- ============================
INSERT INTO tabela_preco (id_tabela, tipo, nome_tabela, versao, data_inicio_validade, data_fim_validade,ativa)
VALUES
(null, 'C', 'Tabela Familia', 1.0, '2024-01-01', '2024-02-01',1),
(null, 'V', 'Tabela Padrão', 1.0, '2024-01-01', '2024-02-01',1);

-- ============================
-- TABELA: produto
-- ============================
INSERT INTO produto (id_produto, nome, tipo_produto, fk_estoque)
VALUES
(null, 'Arroz Tipo 1', 'Alimento', NULL),
(null, 'Feijão Carioca', 'Alimento', NULL),
(null, 'Açúcar Cristal', 'Alimento', NULL);

-- ============================
-- TABELA: preco_produto_tabela
-- ============================
INSERT INTO preco_produto_tabela (fk_produto, fk_tabela_preco, preco_produto)
VALUES
(null, 1, 18.90),
(null, 2, 22.50),
(null, 1, 6.50),
(null, 2, 7.80),
(null, 1, 4.90),
(null, 2, 5.80);

-- ============================
-- TABELA: cliente
-- ============================
INSERT INTO cliente (id_cliente, CNPJ, razao_social, tel_contato,fk_endereco, fk_tabela_preco)
VALUES
(null, '11122233000155', 'Mercado Bom Preço', '12997729323',3, 2),
(null, '99988877000144', 'Atacado União', '12997729321',4, 1);

-- ============================
-- TABELA: compra
-- ============================
INSERT INTO compra (id_compra, fk_fornecedor, data_compra)
VALUES
(null, 1, '2024-01-10'),
(null, 2, '2024-01-15');

-- ============================
-- TABELA: item_pedido_compra
-- ============================
INSERT INTO item_pedido_compra (id_fk_compra, id_fk_produto, peso_kg, preco_unitario)
VALUES
(null, 1, 100, 15.00),
(null, 2, 50, 5.00);

-- ============================
-- TABELA: pagamento_compra
-- ============================
INSERT INTO pagamento_compra (id_pagamento_compra, fk_compra, data_pagamento_compra, fk_conta_pagamento)
VALUES
(null, 1, '2024-01-20', 1),
(null, 2, '2024-01-25', 2);

-- ============================
-- TABELA: venda
-- ============================
INSERT INTO venda (id_venda, fk_cliente, fk_tabela_preco, data_venda)
VALUES
(null, 1, 2, '2024-02-01'),
(null, 2, 1, '2024-02-05');

-- ============================
-- TABELA: item_pedido_venda
-- ============================
INSERT INTO item_pedido_venda (id_fk_produto, id_fk_venda, peso_kg, preco_unitario)
VALUES
(null, 1, 20, 22.50),
(null, 1, 10, 7.80),
(null, 2, 30, 4.90);

-- ============================
-- TABELA: estoque
-- ============================
INSERT INTO estoque (id_estoque, quantidade_disponivel, localizacao)
VALUES
(null, 500, 'Armazém 1'),
(null, 800, 'Armazém 2');

UPDATE produto SET fk_estoque = 1 WHERE id_produto IN (1,2);
UPDATE produto SET fk_estoque = 2 WHERE id_produto = 3;
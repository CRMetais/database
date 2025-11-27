-- DROP DATABASE crmetais;
-- CREATE DATABASE crmetais;
USE crmetais;

-- ==========================================================
-- TABELA: usuario
-- ==========================================================

INSERT INTO usuario (id_usuario, nome, senha, email, cargo)VALUES
(1, 'Celco Ricardo', '123456', 'celco@empresa.com', 'Administrador'),
(NULL, 'Maria Oliveira', '123456', 'maria@empresa.com', 'Funcionario');

-- ==========================================================
-- TABELA: endereco
-- ==========================================================

INSERT INTO endereco (estado, cidade, bairro, logradouro, numero, cep)VALUES
('SP', 'São Paulo', 'Centro', 'Jaraguá', 100, '01001000'),
('RJ', 'Angra dos Reis', 'Sla kkkkk', 'Av Atlântica', 200, '22021001'),
('SP', 'São Paulo', 'Savassi', 'Rua da Bahia', 300, '30160010'),
('SP', 'São Paulo', 'Batel', 'Av Sete de Setembro', 400, '80030010');


-- ==========================================================
-- TABELA: fornecedor
-- ==========================================================

INSERT INTO fornecedor (fk_endereco, nome, documento, telefone, apelido)VALUES
(1, 'metalManeiro', '12345678000199', '11999990000', 'FzVerde'),
(2, 'metaleirosHAHAHAHAHAHHA', '98765432000166', '21988887777', 'SaborCamp');

-- ==========================================================
-- TABELA: conta_pagamento
-- ==========================================================

INSERT INTO conta_pagamento
(pix, banco, agencia, conta, tipo_conta, chave_pix,
 nome, pertence_fornecedor, documento, conta_ativa, fk_fornecedor)VALUES
(1, 'Banco do Brasil', '1234', '56789-0', 'C', '11999990000',
 'João Metal Maneiro', 1, '12345678000199', 1, 1),

(0, 'Caixa', '4321', '12345-9', 'P', 'fazenda@sabor.com',
 'Sabor do Campo', 0, '98765432000166', 1, 2);

-- ==========================================================
-- TABELA: tabela_preco
-- ==========================================================

INSERT INTO tabela_preco (tipo, nome_tabela, versao, data_inicio_validade, data_fim_validade, ativa)VALUES
('C', 'Tabela Família', 1.0, '2024-01-01', '2024-02-01', 1),
('V', 'Tabela Padrão', 1.0, '2024-01-01', '2024-02-01', 1);

-- ==========================================================
-- TABELA: produto
-- ==========================================================

INSERT INTO produto (nome, tipo_produto, fk_estoque)VALUES
('Arroz Tipo 1', 'Alimento', NULL),
('Feijão Carioca', 'Alimento', NULL),
('Açúcar Cristal', 'Alimento', NULL);

-- ==========================================================
-- TABELA: preco_produto_tabela
-- ==========================================================

INSERT INTO preco_produto_tabela (fk_produto, fk_tabela_preco, preco_produto)VALUES
(1, 1, 18.90),
(1, 2, 22.50),

(2, 1, 6.50),
(2, 2, 7.80),

(3, 1, 4.90),
(3, 2, 5.80);

-- ==========================================================
-- TABELA: cliente
-- ==========================================================

INSERT INTO cliente (CNPJ, razao_social, tel_contato, fk_endereco, fk_tabela_preco)VALUES
('11122233000155', 'Mercado Bom Preço', '12997729323', 3, 2),
('99988877000144', 'Atacado União', '12997729321', 4, 1);

-- ==========================================================
-- TABELA: compra
-- ==========================================================

INSERT INTO compra (fk_fornecedor, data_compra)VALUES
(1, '2024-01-10'),
(2, '2024-01-15');


-- ==========================================================
-- TABELA: item_pedido_compra
-- ==========================================================

INSERT INTO item_pedido_compra (id_fk_compra, id_fk_produto, peso_kg, preco_unitario)VALUES
(1, 1, 100, 15.00),
(1, 2, 50, 5.00),
(2, 3, 80, 3.50);

-- ==========================================================
-- TABELA: pagamento_compra
-- ==========================================================

INSERT INTO pagamento_compra (fk_compra, data_pagamento_compra, fk_conta_pagamento)VALUES
(1, '2024-01-20', 1),
(2, '2024-01-25', 2);

-- ==========================================================
-- TABELA: venda
-- ==========================================================

INSERT INTO venda (fk_cliente, fk_tabela_preco, data_venda)VALUES
(1, 2, '2024-02-01'),
(2, 1, '2024-02-05');


-- ==========================================================
-- TABELA: item_pedido_venda
-- ==========================================================

INSERT INTO item_pedido_venda (id_fk_produto, id_fk_venda, peso_kg, preco_unitario)VALUES
(1, 1, 20, 22.50),
(2, 1, 10, 7.80),
(3, 2, 30, 4.90);

-- ==========================================================
-- TABELA: estoque
-- ==========================================================

INSERT INTO estoque (quantidade_disponivel, localizacao)VALUES
(500, 'Armazém 1'),
(800, 'Armazém 2');

-- Atualizando produtos com estoque
UPDATE produto SET fk_estoque = 1 WHERE id_produto IN (1,2);
UPDATE produto SET fk_estoque = 2 WHERE id_produto = 3;

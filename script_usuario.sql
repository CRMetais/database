-- Criação do banco (simples, sem charset específico)
CREATE DATABASE IF NOT EXISTS crmetais;

USE crmetais;

CREATE USER IF NOT EXISTS 'crmetais_user'@'localhost' IDENTIFIED BY 'crmetais123';

GRANT ALL PRIVILEGES ON crmetais.* TO 'crmetais_user'@'localhost';

FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS usuario (
    idusuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45),
    senha VARCHAR(45),
    email VARCHAR(45)
);

select * from usuario;

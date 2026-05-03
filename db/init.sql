CREATE TABLE IF NOT EXISTS movimentacao_estoque (
    id SERIAL PRIMARY KEY,
    hospital_id VARCHAR(50) NOT NULL,
    medicamento VARCHAR(100) NOT NULL,
    tipo_movimento VARCHAR(20) NOT NULL,
    quantidade INT NOT NULL,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado BOOLEAN DEFAULT FALSE
);

INSERT INTO movimentacao_estoque (hospital_id, medicamento, tipo_movimento, quantidade) VALUES
('CH-01', 'Dipirona Sódica 500mg', 'ENTRADA', 1000),
('CH-01', 'Insulina NPH', 'SAIDA', 15),
('CH-02', 'Amoxicilina 500mg', 'ENTRADA', 500),
('CH-01', 'Clonazepam 2mg', 'SAIDA', 30),
('CH-02', 'Soro Fisiológico 0.9%', 'SAIDA', 100);
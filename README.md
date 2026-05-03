# Projeto Medicamentos Streaming (CH-UFC)

Pipeline de Engenharia de Dados em tempo real projetado para o monitoramento e gestão de estoque de medicamentos do Complexo Hospitalar. 

##  Arquitetura

O ecossistema foi desenhado com foco em resiliência e desacoplamento, utilizando o padrão de extração para leitura não intrusiva do banco de dados transacional (OLTP).

1. **Camada de Persistência (OLTP):** PostgreSQL operando como a fonte da verdade da farmácia.
2. **Ingestão (Producer):** Script Python atuando como um Extrator simplificado.
3. **Mensageria (Streaming):** Cluster Apache Kafka rodando em modo **KRaft** (sem Zookeeper) com 3 nós em alta disponibilidade.
4. **Processamento (Consumer):** Motor de analise processando o fluxo de dados do Kafka em tempo real para painéis de monitoramento.

##  Como Executar o Ambiente

### 1. Subindo a Infraestrutura (Docker)
O projeto utiliza um ambiente monorepo orquestrado via Docker Compose. O script de inicialização do banco (`init.sql`) cria as tabelas e injeta uma semente de dados automaticamente.
```bash
# Na raiz do projeto, inicie os contêineres em background
docker-compose up -d
```
### 2. Configurando o Ambiente Virtual Python
```bash
# Criação do ambiente virtual
python -m venv .venv

# Ativação (Windows)
.venv\Scripts\activate

# Instalação das dependências
pip install -r requirements.txt
```
### 3. Executando o Pipeline de Streaming
#### Para vizualizar o fluxo em tempo real, abra dois terminais distintos com o ambiente virtual ativado :
### Terminal 1 (Consumidor)
```bash
python src/tests/test_consumer.py
```
### Terminal 2 (Produtor)
```
python src/tests/test_producer.py
```
## Simulando Operações Reais
#### Com os scripts anteriores funcionando, você pode testar o monitoramento em tempo real, injetando novos registros no DB.

### Comando SQL
```bash
# Exemplo de Recebimento de um Lote de Medicamentos
INSERT INTO movimentacao_estoque (hospital_id, medicamento, tipo_movimento, quantidade) 
VALUES ('CH-01', 'Propofol', 'ENTRADA', 50);

# Exemplo de Dispensação de Medicamentos para Paciente
INSERT INTO movimentacao_estoque (hospital_id, medicamento, tipo_movimento, quantidade) 
VALUES ('CH-02', 'Amoxicilina 500mg', 'SAIDA', 2);
```
## Autor 
### Francisco David Vaz de Sousa
#### Ciência da Computação - Universidade Federal do Ceará(UFC)
#### Bolsista de Ciência de Dados em Saúde: obtendo insights, padrões e tendências nos indicadores em saúde.
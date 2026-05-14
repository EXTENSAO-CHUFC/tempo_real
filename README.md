

![alt text](logo-huwc-Photoroom.png)
# 🏥 Monitor de Farmácia em Tempo Real (CH-UFC)
![Status](https://img.shields.io/badge/Status-MVP%20Concluído-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![Kafka](https://img.shields.io/badge/Apache_Kafka-Streaming-black)
![Redis](https://img.shields.io/badge/Redis-In--Memory_Cache-red)

Sistema de monitoramento de estoque de medicamentos em tempo real, desenvolvido como projeto de extensão para a farmácia do Complexo Hospitalar da Universidade Federal do Ceará (CH-UFC).

Este projeto utiliza uma arquitetura de streaming orientada a eventos para processar requisições de medicamentos, atualizar caches de alta performance e disparar alertas automáticos, culminando em um dashboard interativo para a gestão hospitalar.

---

## 🏗️ Principais Funcionalidades

- **Simulação de Demanda:** Produtor automatizado que simula o consumo de medicamentos pelos médicos e setores do hospital.
- **Dashboard em Tempo Real:** Interface gráfica via Web (Streamlit) com KPIs, gráficos de barras dinâmicos e semáforo de criticidade, lendo dados em milissegundos a partir de cache em memória.
- **Arquitetura Desacoplada:** Separação clara de responsabilidades (MVC, Producers, Consumers) garantindo alta escalabilidade.
- **Infraestrutura as Code:** Orquestração completa de 100% dos serviços (Banco, Mensageria e Tela) via Docker Compose.

---

## 🚀Arquitetura de Engenharia de Dados

O fluxo de dados segue o padrão de streaming:
1. **Producer (`src/producer/`):** Lê o catálogo do banco, gera simulações de retirada de medicamentos e publica mensagens JSON no tópico do **Apache Kafka**.
2. **Kafka Brokers:** Gerencia a fila de mensagens de forma assíncrona.
3. **Consumer Redis (`src/consumer/redis_updater.py`):** Consome os eventos do Kafka e processa as baixas de estoque instantaneamente no **Redis**.
4. **View (`src/dashboard/app.py`):** O **Streamlit** consome os dados atualizados do Redis para renderizar a interface visual sem sobrecarregar o banco de dados transacional.
5. **Armazenamento Transacional:** O estado consolidado e o catálogo mestre repousam no **PostgreSQL**, acessado via SQLAlchemy.

---
## ⚙️ Como executar o ambiente

### 1. Preparar as Credenciais
Crie um arquivo chamado `.env` na raiz do projeto e adicione as credenciais do banco de dados:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=adminpassword
POSTGRES_DB=farmacia_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```
### 2. Instalar o Docker
- Acesse o site oficial: [Baixar Docker Desktop](https://www.docker.com/products/docker-desktop/)
### 3. Configurar o Ambiente
```
# Crie e ative o ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Instale os pacotes
pip install -r requirements.txt
```
### 4. Executar o Arquivo para iniciar 
```
# Iniciar o sistema utilizando Windows
mingw32-make run
# Iniciar o sistema utilizando Linux
make run
```
### 5. Finalizar com o arquivo encerrar.py
```
# Encerrar o sistema utilizando Windows
mingw32-make stop
# Encerrar o sistema utilizando Linux
make stop
```
## ⚠️ Limpar os volumes:
```
# Windows
mingw32-make clean
# Linux
make clean
```
## 👨‍💻 Autor
Francisco David Vaz de Sousa

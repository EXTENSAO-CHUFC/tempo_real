

![alt text](src/utils/logo-huwc-Photoroom.png)
# 🏥 Monitor de Farmácia em Tempo Real (CH-UFC)
![Status](https://img.shields.io/badge/Status-MVP%20Concluído-success)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
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
## 📁 Estrutura do Projeto

```
tempo_real/
├── db/                    # Scripts de banco (modelos, conexão, carga inicial)
├── deploy/                # Configurações de deploy (Dockerfile, render.yaml)
├── docs/                  # Documentação complementar
├── logs/                  # Logs de execução (producer, consumer, erros)
├── src/
│   ├── api/               # API REST (em desenvolvimento)
│   ├── config/            # Configurações centralizadas (settings.py)
│   ├── consumers/         # Consumidores Kafka (redis_cache, historico, monitoramento)
│   ├── dashboard/         # Dashboard Streamlit (app.py)
│   ├── jobs/              # Tarefas agendadas (em desenvolvimento)
│   ├── models/            # Modelos de domínio (em desenvolvimento)
│   ├── producer/          # Produtor Kafka (simulador de retiradas)
│   ├── tests/             # Testes automatizados
│   └── utils/             # Utilitários (Kafka, Redis, DB helpers)
├── docker-compose.yml     # Orquestração dos contêineres
├── iniciar.py             # Orquestrador de inicialização
├── encerrar.py            # Orquestrador de encerramento
├── Makefile               # Atalhos de comandos
└── pyproject.toml         # Dependências e metadados (Poetry)
```

---

## 🔌 Portas e Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| PostgreSQL | `5433` | Banco de dados transacional (mapeado do 5432 interno) |
| Redis | `6379` | Cache em memória para leitura rápida do dashboard |
| Kafka Broker 1 | `19090` | Broker principal do cluster Kafka |
| Kafka Broker 2 | `19091` | Broker réplica do cluster Kafka |
| Kafka Broker 3 | `19092` | Broker réplica do cluster Kafka |
| Streamlit | `8501` | Dashboard web (aberto automaticamente no navegador) |

---

## ⚙️ Como Executar o Ambiente

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Clonar o repositório
```powershell
git clone <https://github.com/EXTENSAO-CHUFC/tempo_real.git>
```
### Instalar o pyenv e o Python 3.12

O pyenv permite gerenciar múltiplas versões do Python sem conflitos. O projeto requer Python 3.12+ (versão exata: `3.12.10`, conforme o arquivo `.python-version`).

#### Windows

No Windows, utilize o [pyenv-win](https://github.com/pyenv-win/pyenv-win):

```powershell
# Instalar via PowerShell (como Administrador)
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Reinicie o terminal e execute:

```powershell
# Instalar a versão do Python usada no projeto
pyenv install 3.12.10
pyenv local 3.12.10
```

### Instalar o Poetry

O Poetry é o gerenciador de dependências e ambiente virtual do projeto.

#### Windows

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -3 -
```

Após a instalação, reinicie o terminal e verifique:

```bash
poetry --version
``` 
### 1. Configurar as Variáveis de Ambiente

Copie o arquivo de exemplo e ajuste os valores se necessário:

```bash
cp .env.example .env
```

As variáveis padrão já funcionam com o `docker-compose.yml` fornecido.

### 2. Instalar as Dependências

```bash
poetry install
```

O Poetry criará o ambiente virtual e instalará todos os pacotes automaticamente.

### 3. Iniciar o Sistema

```bash
# Windows (CMD ou PowerShell)
mingw32-make run

# Linux/macOS
make run
```

> ⚠️ **Nota:** O script `iniciar.py` utiliza comandos específicos do Windows (`os.system('start ...')`) para abrir terminais separados. Execução nativa em Linux/macOS requer adaptação desse script.

### 4. Encerrar o Sistema

```bash
# Windows
mingw32-make stop

# Linux/macOS
make stop
```

### Comandos Disponíveis (Makefile)

| Comando (Linux) | Comando (Windows) | Descrição |
|-----------------|-------------------|-----------|
| `make run` | `mingw32-make run` | Inicia todo o sistema (Docker, Carga, Painel e Robôs) |
| `make stop` | `mingw32-make stop` | Desliga o sistema com segurança |
| `make restart` | `mingw32-make restart` | Reinicia o sistema (stop + run) |
| `make infra-up` | `mingw32-make infra-up` | Sobe apenas os contêineres (Postgres, Redis, Kafka) |
| `make infra-down` | `mingw32-make infra-down` | Desliga apenas os contêineres |
| `make clean` | `mingw32-make clean` | ⚠️ Deleta volumes e zera todos os dados (Hard Reset) |
| `make help` | `mingw32-make help` | Lista todos os comandos disponíveis |

---

## 👨‍💻 Autor

Francisco David Vaz de Sousa

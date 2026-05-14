# ==============================
# CONFIGURAÇÕES
# ==============================

.PHONY: run stop restart infra-up infra-down carga clean git-status git-add git-commit git-push git-all git-new-branch help

# ==============================
# SISTEMA COMPLETO (ORQUESTRADOR)
# ==============================

run:
	@echo " Chamando o orquestrador para iniciar o sistema..."
	python iniciar.py

stop:
	@echo " Chamando o orquestrador para desligar o sistema..."
	python encerrar.py

restart:
	@echo " Reiniciando o sistema..."
	$(MAKE) stop
	@echo "Aguardando desligamento completo..."
	sleep 3
	$(MAKE) run

# ==============================
# INFRAESTRUTURA INDIVIDUAL (DOCKER)
# ==============================

infra-up:
	@echo " Subindo apenas os bancos e a mensageria (Postgres, Redis, Kafka)..."
	docker-compose up -d

infra-down:
	@echo " Desligando a infraestrutura..."
	docker-compose down


# ==============================
# LIMPEZA (HARD RESET)
# ==============================

clean:
	@echo " Destruindo os volumes e limpando dados do banco e cache..."
	docker-compose down -v
	@echo " Limpeza profunda concluída. Os bancos estão zerados."

# ==============================
# GIT
# ==============================

git-status:
	@echo " Status do Git"
	git status

git-add:
	@echo " Adicionando arquivos"
	git add .

git-commit:
	@echo " Commitando alterações"
	git commit -m "update: nova versão do projeto"

git-push:
	@echo " Enviando para o GitHub"
	git push origin main

git-all:
	@echo " Subindo versão completa..."
	git status
	git add .
	git commit -m "$(msg)"
	git push origin main

# Padrão de mensagens (Commits Convencionais):
# feat: nova funcionalidade
# fix: correção
# test: testes
# refactor: refatoração
# chore: manutenção
# Uso prático: make git-all msg="feat: adiciona script orquestrador em python"

# ==============================
# BRANCH
# ==============================

git-new-branch:
	@echo "🌿 Criando nova branch: $(name)"
	git checkout -b $(name)

# Uso prático: make git-new-branch name=feature/nova-tela-dashboard
# Prefixos recomendados:
# feature/ → nova funcionalidade
# fix/ → correção
# test/ → testes
# hotfix/ → correção urgente

# ==============================
# AJUDA
# ==============================

help:
	@echo ""
	@echo " Comandos disponíveis para o Monitoramento CH-UFC:"
	@echo ""
	@echo "--- OPERAÇÃO PRINCIPAL ---"
	@echo "make run           → Inicia todo o sistema (Docker, Carga, Painel e Robôs)"
	@echo "make stop          → Desliga o sistema com segurança"
	@echo "make restart       → Desliga e liga o sistema novamente"
	@echo ""
	@echo "--- MANUTENÇÃO ---"
	@echo "make infra-up      → Sobe apenas os contêineres do Docker"
	@echo "make infra-down    → Desliga apenas os contêineres do Docker"
	@echo "make clean         → [CUIDADO] Deleta os bancos de dados (Hard Reset)"
	@echo ""
	@echo "--- VERSIONAMENTO (GIT) ---"
	@echo "make git-status    → Mostra o status do repositório"
	@echo "make git-all msg=\"...\" → Faz add, commit e push de uma vez"
	@echo "make git-new-branch name=... → Cria e muda para uma nova branch"
	@echo ""
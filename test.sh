#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para exibir mensagens de erro e sair
error_exit() {
    echo -e "${RED}Erro: $1${NC}" >&2
    exit 1
}

echo -e "${YELLOW}Executando testes...${NC}"

# Verificar se os containers estão rodando
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}Containers não estão rodando. Iniciando...${NC}"
    docker-compose up -d || error_exit "Falha ao iniciar containers"
fi

# Executar testes
echo -e "${YELLOW}Executando testes unitários e de integração...${NC}"
docker-compose exec -T app python -m pytest tests/ -v || error_exit "Falha nos testes"

echo -e "${GREEN}✓ Todos os testes passaram com sucesso!${NC}" 
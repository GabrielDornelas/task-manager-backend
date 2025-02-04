#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando a aplicação...${NC}"

# Verificar se os containers estão rodando
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}Containers não estão rodando. Iniciando...${NC}"
    docker-compose up -d
fi

echo -e "${GREEN}✓ Aplicação está rodando!${NC}"
echo -e "${GREEN}API disponível em: http://localhost:5000${NC}"
echo -e "${GREEN}Documentação Swagger: http://localhost:5000/api/docs${NC}"

# Mostrar logs em tempo real
echo -e "${YELLOW}Mostrando logs da aplicação (Ctrl+C para sair)...${NC}"
docker-compose logs -f app 
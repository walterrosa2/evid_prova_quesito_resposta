#!/bin/bash
set -e

echo "🚀 Iniciando deploy no Ubuntu..."

# Atualizando repositório
git pull origin main

# Construindo e subindo os containers (rebuild)
docker compose up -d --build

# Removendo imagens órfãs
docker image prune -f

echo "✅ Deploy concluído com sucesso!"
docker compose ps

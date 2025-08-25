Write-Host "=== Parando todos os containers ativos..."
docker stop $(docker ps -q) 2>$null

Write-Host "=== Removendo todos os containers..."
docker rm $(docker ps -aq) -f 2>$null

Write-Host "=== Limpando imagens nao utilizadas..."
docker image prune -a -f

Write-Host "=== Limpando volumes nao utilizados..."
docker volume prune -f

Write-Host "=== Limpando redes nao utilizadas..."
docker network prune -f

Write-Host "`n>>> Docker reset concluido! <<<`n"

# Agora build e run do docker-compose
Write-Host "=== Fazendo build dos containers com docker-compose..."
docker compose build

Write-Host "=== Subindo containers em segundo plano..."
docker compose up

Write-Host "`n>>> Ambiente pronto e rodando! <<<"
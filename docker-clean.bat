@echo off
echo Limpando containers parados...
docker container prune -f

echo Limpando imagens nao utilizadas...
docker image prune -a -f

echo Limpando volumes nao utilizados...
docker volume prune -f

echo Limpando redes nao utilizadas...
docker network prune -f

echo >>> Limpeza completa concluida! <<<
pause
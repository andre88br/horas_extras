@echo off
:START
echo Tentando conectar ao servidor SSH...
ssh -R horaextra:80:127.0.0.1:8000 serveo.net
echo Conexão perdida. Tentando novamente em 10 segundos...
timeout /t 10
goto START
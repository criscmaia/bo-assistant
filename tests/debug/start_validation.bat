@echo off
echo ========================================
echo BO Inteligente - Validacao de 3 Secoes
echo ========================================
echo.

echo [1/3] Matando processos antigos na porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Matando PID: %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Iniciando backend...
start "BO Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Aguardando backend iniciar (5 segundos)...
timeout /t 5 /nobreak

echo.
echo [3/3] Abrindo frontend no navegador...
start http://localhost:8000/docs/index.html

echo.
echo ========================================
echo VALIDACAO MANUAL:
echo ========================================
echo 1. ProgressBar deve mostrar APENAS 3 bolinhas
echo 2. Complete a secao 1 (responda todas as perguntas)
echo 3. Pule secao 2 (clique "Nao, pular")
echo 4. Pule secao 3 (clique "Nao, pular")
echo 5. Deve aparecer botao "Finalizar BO" (NAO "Iniciar Secao 4")
echo 6. Clicar "Finalizar BO" deve mostrar tela final
echo.
echo Pressione Ctrl+C para encerrar o backend
echo ========================================
pause

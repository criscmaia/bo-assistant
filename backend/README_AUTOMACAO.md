# 🤖 Automação de Screenshots - Guia de Uso

Sistema automatizado para capturar screenshots e vídeos de releases do BO Assistant.

---

## 📦 Arquivos

1. **`test_scenarios.json`** - Configuração de cenários de teste
2. **`automate_release.py`** - Script principal
3. **`README_AUTOMACAO.md`** - Este arquivo

---

## 🚀 Como Usar

### Pré-requisitos

```bash
# 1. Backend rodando
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Frontend rodando (outro terminal)
cd docs
python -m http.server 3000
```

### Executar Automação

```bash
# No terminal do backend (venv ativado)
cd backend

# Executar (modo visual - você vê o navegador)
python automate_release.py --version v0.3.2

# Executar em background (headless)
python automate_release.py --version v0.3.2 --headless

# Executar sem gerar vídeo (mais rápido)
python automate_release.py --version v0.3.2 --no-video

# Com URLs customizadas
python automate_release.py --version v0.3.2 \
    --backend http://localhost:8000 \
    --frontend http://localhost:3000
```

### Resultado

Após ~2-3 minutos, você terá:

```
docs/screenshots/v0.3.2/
├── 01-desktop-sidebar-empty.png
├── 02-desktop-sidebar-progress.png
├── 03-desktop-erro.png
├── 04-desktop-editando.png
├── 05-desktop-editando-erro.png
├── 06-mobile-empty.png
├── 07-mobile-sidebar-open.png
├── 08-desktop-final.png
├── 09-mobile-final.png
├── demo.mp4
└── README.md
```

---

## 🎬 O Que o Script Faz

### Desktop (1280x720)
1. Abre página inicial → Screenshot `01`
2. Responde 2 perguntas
3. Edita pergunta 1 com erro → Screenshot `05`
4. Edita pergunta 1 com sucesso → Screenshot `04`
5. Responde pergunta 3 com erro → Screenshot `03`
6. Responde pergunta 3 corretamente → Screenshot `02` (progresso 3/6)
7. Responde perguntas 4, 5, 6
8. Aguarda geração de texto → Screenshot `08`
9. **Grava vídeo MP4** de todo o fluxo

### Mobile (430x932 - iPhone 14 Pro Max)
1. Abre página inicial → Screenshot `06`
2. Abre sidebar/drawer → Screenshot `07`
3. Responde todas as 6 perguntas rapidamente
4. Aguarda texto gerado → Screenshot `09`

---

## ⚙️ Configuração (test_scenarios.json)

### Alterar Resoluções

```json
"resolutions": {
  "desktop": {"width": 1920, "height": 1080},
  "mobile": {"width": 375, "height": 667}
}
```

### Alterar URLs

```json
"backend_url": "https://bo-assistant-backend.onrender.com",
"frontend_url": "https://criscmaia.github.io/bo-assistant/"
```

### Alterar Cenários de Teste

Edite o array `test_flow` para adicionar/remover passos.

---

## 🐛 Troubleshooting

### Erro: "Playwright não encontrado"
```bash
pip install playwright
playwright install chromium
```

### Erro: "opencv não encontrado"
```bash
pip install opencv-python pillow
```

### Backend não responde (500 Error)
- Verifique se backend está rodando
- Verifique se `GEMINI_API_KEY` está configurada
- Teste manual: `curl http://localhost:8000/health`

### Screenshots em branco
- Aumente `await page.wait_for_timeout()` nos timings
- Verifique se frontend está acessível em localhost:3000

### Vídeo não gerado
- Use `--no-video` para pular geração de vídeo
- Verifique se opencv está instalado corretamente

---

## 🔧 Customização

### Modo Headless (Sem ver navegador)

Edite `automate_release.py`, linha ~250:

```python
browser = await p.chromium.launch(headless=True)  # True = invisível
```

### Aumentar Duração do Vídeo

Edite `automate_release.py`, linha ~177:

```python
target_frames = self.video_fps * 60  # 60 segundos ao invés de 30
```

### Adicionar Mais Screenshots

Adicione chamadas no fluxo:

```python
await self.take_screenshot(page, 'novo-screenshot.png', 'Descrição')
```

---

## 📊 Performance

- **Tempo total:** ~2-3 minutos
- **Desktop flow:** ~90 segundos
- **Mobile flow:** ~30 segundos
- **Geração de vídeo:** ~10 segundos
- **Tamanho total:** ~5-8 MB

---

## ✅ Checklist Pré-Execução

- [ ] Backend rodando (`uvicorn main:app --reload`)
- [ ] Frontend rodando (`python -m http.server 3000`)
- [ ] Ambiente virtual ativado (`venv\Scripts\activate`)
- [ ] Playwright instalado (`playwright install chromium`)
- [ ] API key do Gemini configurada no `.env`

---

## 🎯 Próximos Passos

Após gerar screenshots:

```bash
# 1. Revisar screenshots geradas
cd docs/screenshots/v0.3.2
# Abrir e verificar cada imagem

# 2. Commit
git add docs/screenshots/v0.3.2/
git commit -m "docs: adicionar screenshots automáticas da v0.3.2"
git push

# 3. Atualizar CHANGELOG.md (manual)
```

---

**Criado por:** Claude + Cristiano Maia  
**Data:** 05/12/2024  
**Versão:** 1.0

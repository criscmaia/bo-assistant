# 🤖 Automação de Screenshots - Guia de Uso

Sistema automatizado para capturar screenshots e vídeos de releases do BO Assistant.

**Versão:** 2.1 (com suporte a Seção 2)

---

## 📦 Arquivos

1. **`test_scenarios.json`** - Configuração hierárquica de cenários de teste (Seção 1 + 2)
2. **`automate_release.py`** - Script principal (Playwright async)
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
python automate_release.py --version v0.5.1

# Executar sem gerar vídeo (mais rápido - ~3 minutos)
python automate_release.py --version v0.5.1 --no-video

# Com URLs customizadas
python automate_release.py --version v0.5.1 \
    --backend http://localhost:8000
```

**Nota:** O navegador sempre abre em modo visível (não há mais modo headless). Isso permite acompanhar o teste em tempo real.

### Resultado

Após ~4-5 minutos, você terá:

```
docs/screenshots/v0.5.1/
├── 01-section1-empty.png
├── 02-section1-progress-3-of-6.png
├── 03-section1-edit-error.png
├── 04-section1-edit-success.png
├── 05-section1-final-with-button.png
├── 06-section2-start.png
├── 07-section2-plate-error.png
├── 08-section2-rank-error.png
├── 09-section2-progress-4-of-8.png
├── 10-section2-final-both-sections.png
├── 11-mobile-section1-empty.png
├── 12-mobile-section1-sidebar.png
├── 13-mobile-section1-final.png
├── 14-mobile-section2-start.png
├── 15-mobile-section2-sidebar.png
├── 16-mobile-section2-final.png
├── demo.webm
└── README.md
```

**Total:** 16 screenshots + vídeo de ~4 minutos

---

## 🎬 O Que o Script Faz

### Desktop (1280x720) - Seção 1 + Seção 2
1. **Seção 1 (Contexto da Ocorrência):**
   - Abre página inicial → Screenshot `01`
   - Responde perguntas 1.1, 1.2, 1.3 → Screenshot `02` (progresso 3/6)
   - Testa edição com erro → Screenshot `03`
   - Testa edição válida → Screenshot `04`
   - Responde perguntas 1.4, 1.5, 1.6
   - Aguarda geração de texto → Screenshot `05` (com botão "Iniciar Seção 2")

2. **Seção 2 (Abordagem a Veículo):**
   - Clica em "Iniciar Seção 2" → Screenshot `06`
   - Testa placa inválida (ABC123) → Screenshot `07`
   - Envia placa válida (ABC-1D23)
   - Testa resposta sem graduação → Screenshot `08`
   - Envia resposta válida com graduação → Screenshot `09` (progresso 4/8)
   - Responde perguntas 2.4, 2.5, 2.6, 2.7
   - Aguarda geração de texto → Screenshot `10` (ambas seções visíveis)
   - **Grava vídeo WebM** de todo o fluxo (~4 minutos)

### Mobile (430x932 - iPhone 14 Pro Max) - Seção 1 + Seção 2
1. **Seção 1:**
   - Abre página inicial → Screenshot `11`
   - Abre sidebar → Screenshot `12`
   - Responde todas as 6 perguntas
   - Aguarda texto gerado → Screenshot `13`

2. **Seção 2:**
   - Clica em "Iniciar Seção 2" → Screenshot `14`
   - Abre sidebar (mostra Seção 1 ✓) → Screenshot `15`
   - Responde 8 perguntas válidas (sem testar erros)
   - Aguarda texto gerado → Screenshot `16` (ambas seções visíveis)

---

## ⚙️ Configuração (test_scenarios.json)

O arquivo `test_scenarios.json` agora usa **estrutura hierárquica** com array `sections`:

```json
{
  "version": "0.5.1",
  "sections": [
    {
      "section_number": 1,
      "name": "Contexto da Ocorrência",
      "steps": [...]
    },
    {
      "section_number": 2,
      "name": "Abordagem a Veículo",
      "steps": [...]
    }
  ]
}
```

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

### Adicionar Nova Seção (futuro)

Adicione novo objeto ao array `sections`:

```json
{
  "section_number": 3,
  "name": "Campana e Vigilância",
  "emoji": "🔍",
  "total_questions": 5,
  "steps": [
    {
      "step": "3.0",
      "answer": "Resposta...",
      "expect": "pass"
    }
  ]
}
```

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

- **Tempo total:** ~4-5 minutos (com vídeo) / ~3 minutos (sem vídeo)
- **Desktop Seção 1:** ~90 segundos
- **Desktop Seção 2:** ~120 segundos
- **Mobile Seção 1:** ~30 segundos
- **Mobile Seção 2:** ~60 segundos
- **Tamanho total:** ~10-15 MB (16 screenshots + vídeo)

**Breakdown do tempo:**
- Espera de API por resposta: ~1s cada (14 perguntas = ~14s)
- Espera de geração LLM: ~15-25s por seção (2 seções = ~40s)
- Typing lento (para vídeo natural): ~10-30s por pergunta
- Screenshots e scrolls: ~5s

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
cd docs/screenshots/v0.5.1
# Abrir e verificar cada imagem (16 screenshots)

# 2. Verificar vídeo
# Abrir demo.webm e assistir fluxo completo (~4 minutos)

# 3. Commit
git add docs/screenshots/v0.5.1/
git commit -m "docs: adicionar screenshots automáticas da v0.5.1 (Seção 1 + 2)"
git push

# 4. Atualizar CHANGELOG.md (manual)
```

---

## 🔄 Changelog da Automação

### v2.1 (19/12/2025) - Suporte a Seção 2
- ✅ Adicionada Seção 2 (Abordagem a Veículo - 8 perguntas)
- ✅ Estrutura hierárquica em `test_scenarios.json`
- ✅ 16 screenshots (10 desktop + 6 mobile)
- ✅ Validações: placa Mercosul, graduação
- ✅ Vídeo ampliado para ~4 minutos

### v2.0 (05/12/2024) - Gravação de Vídeo Nativa
- ✅ Gravação de vídeo WebM via Playwright nativo
- ✅ Suporte a Seção 1 (6 perguntas)
- ✅ 9 screenshots (6 desktop + 3 mobile)

### v1.0 (Inicial) - Screenshots Básicos
- ✅ Screenshots manuais
- ✅ Sem vídeo

---

**Criado por:** Claude Sonnet 4.5 + Cristiano Maia
**Última atualização:** 19/12/2025
**Versão:** 2.1

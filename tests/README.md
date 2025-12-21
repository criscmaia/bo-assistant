# 🧪 Testes - BO Inteligente

**Versão:** v0.6.4
**Última atualização:** 21/12/2025

Este diretório contém todos os testes automatizados do projeto, organizados por camada (pirâmide de testes).

---

## 📁 Estrutura

```
tests/
├── conftest.py              # Fixtures pytest compartilhadas
├── pytest.ini               # Configuração pytest
├── README.md                # Este arquivo
│
├── unit/                    # Testes unitários (pytest)
│   ├── test_validators.py
│   ├── test_validators_section2.py
│   ├── test_state_machine.py
│   └── test_state_machine_section2.py
│
├── integration/             # Testes de integração (pytest)
│   ├── test_api_endpoints.py
│   ├── test_sync_session.py
│   ├── test_draft_system.py
│   └── test_complete_flow.py
│
├── e2e/                     # Testes E2E (Playwright standalone)
│   ├── README.md
│   ├── automate_release.py
│   └── test_scenarios.json
│
└── fixtures/                # Dados de teste compartilhados
    ├── valid_responses_section1.json
    ├── valid_responses_section2.json
    └── invalid_cases.json
```

---

## 🚀 Como Rodar

### Pré-requisitos

```bash
# Instalar dependências de desenvolvimento
pip install -r backend/requirements-dev.txt

# Para E2E: instalar navegadores Playwright
playwright install chromium
```

---

### Unit Tests (Rápidos - ~5s)

Testes de validadores e state machines **sem I/O** (não precisam de backend rodando).

```bash
# Rodar todos os unit tests
pytest tests/unit

# Rodar teste específico
pytest tests/unit/test_validators.py

# Rodar com cobertura de código
pytest tests/unit --cov=backend --cov-report=html
```

**O que testa:**
- Validação de respostas (datas, placas Mercosul, graduações)
- Lógica das state machines (transições, estados)
- Regras de negócio isoladas

---

### Integration Tests (Médios - ~30s)

Testes de endpoints da API **com I/O** (precisam do backend rodando).

```bash
# 1. Iniciar backend (terminal separado)
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Rodar integration tests (outro terminal)
pytest tests/integration

# Rodar apenas testes lentos
pytest tests/integration -m slow

# Rodar sem testes lentos
pytest tests/integration -m "not slow"
```

**O que testa:**
- Endpoints `/new_session`, `/chat`, `/start_section`, `/sync_session`
- Sistema de rascunhos (localStorage + backend)
- Fluxo completo Seção 1 + Seção 2
- Geração de texto via LLM

---

### E2E Tests (Longos - ~4 min)

Testes end-to-end com **Playwright** para screenshots e vídeo de release.

```bash
# 1. Backend rodando (terminal 1)
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Frontend rodando (terminal 2)
cd docs
python -m http.server 3000 --bind 127.0.0.1

# 3. Rodar E2E (terminal 3)
python tests/e2e/automate_release.py --version v0.6.5

# Sem vídeo (mais rápido - ~3 min)
python tests/e2e/automate_release.py --version v0.6.5 --no-video
```

**O que testa:**
- Fluxo completo de usuário (Desktop + Mobile)
- Validações de formulário (erro + sucesso)
- Geração de 16 screenshots + vídeo 4min
- Sidebar, modais, responsividade

**Saída:** `docs/screenshots/v0.6.5/` com 16 PNGs + `demo.webm`

Veja [tests/e2e/README.md](e2e/README.md) para detalhes.

---

### Todos os Testes Pytest

```bash
# Rodar unit + integration juntos
pytest

# Com relatório HTML
pytest --html=report.html --self-contained-html

# Paralelizar (4 workers)
pytest -n 4
```

---

## 🎯 Quando Usar Cada Tipo

| Tipo | Quando usar | Backend necessário? | Duração |
|------|-------------|---------------------|---------|
| **Unit** | Testar lógica isolada (validadores, state machines) | ❌ Não | ~5s |
| **Integration** | Testar endpoints, fluxos com DB/LLM | ✅ Sim | ~30s |
| **E2E** | Gerar screenshots de release, testar UX completo | ✅ Sim (backend + frontend) | ~4min |

---

## 📊 Cobertura de Testes

Para gerar relatório de cobertura de código:

```bash
# Rodar todos os testes pytest com cobertura
pytest --cov=backend --cov-report=html

# Abrir relatório
# Windows
start htmlcov/index.html
# Linux/Mac
open htmlcov/index.html
```

---

## 🔧 Debugging

### Ver logs detalhados
```bash
pytest -vv --log-cli-level=DEBUG
```

### Parar no primeiro erro
```bash
pytest -x
```

### Entrar no debugger ao falhar
```bash
pytest --pdb
```

### Rodar apenas testes que falharam na última execução
```bash
pytest --lf  # last failed
```

---

## 🏷️ Markers (Tags)

Filtrar testes por markers definidos em `pytest.ini`:

```bash
# Apenas unit tests
pytest -m unit

# Apenas integration tests
pytest -m integration

# Pular testes lentos
pytest -m "not slow"

# Apenas testes lentos
pytest -m slow
```

---

## 📝 Escrevendo Novos Testes

### Unit Test Example
```python
# tests/unit/test_validators.py
import pytest
from backend.validator import ResponseValidator

def test_datetime_validation():
    is_valid, error = ResponseValidator.validate("1.1", "19/12/2025, 14h30")
    assert is_valid
    assert error is None
```

### Integration Test Example
```python
# tests/integration/test_api.py
import pytest

def test_new_session(api_base_url):
    response = requests.post(f"{api_base_url}/new_session")
    assert response.status_code == 200
    assert "session_id" in response.json()
```

Veja [conftest.py](conftest.py) para fixtures disponíveis.

---

## 🚨 CI/CD

Testes rodam automaticamente no GitHub Actions:

- **Unit tests** - Rodam em todo push
- **Integration tests** - Rodam em PRs para `main`
- **E2E tests** - Rodam apenas em releases (tags `v*`)

Workflow: [`.github/workflows/tests.yml`](../.github/workflows/tests.yml)

---

## 🔗 Documentação Relacionada

- [../docs/TESTING.md](../docs/TESTING.md) - Guia completo de estratégias de teste
- [e2e/README.md](e2e/README.md) - Documentação específica do E2E
- [../DEVELOPMENT.md](../DEVELOPMENT.md) - Guia de desenvolvimento

---

## 📞 Ajuda

Se encontrar problemas:

1. Verifique se backend está rodando (`curl http://localhost:8000/health`)
2. Verifique se `GEMINI_API_KEY` está configurada no `.env`
3. Rode `pytest --collect-only` para ver se testes são descobertos
4. Abra issue em [GitHub](https://github.com/criscmaia/bo-assistant/issues)

---

**Mantido por:** Claude Sonnet 4.5 + Cristiano Maia

# Plano de Implementação - Seção 4: Entrada em Domicílio

**Versão Alvo:** v0.8.0
**Data:** 21/12/2025
**Status:** Aguardando Implementação
**Custo Pré-Implementação:** USD 127.90

---

## 1. Resumo Executivo

Implementar a Seção 4 (Entrada em Domicílio) seguindo o padrão estabelecido pela Seção 3 (Campana), otimizando o uso de **Haiku (~55%)** vs **Sonnet (~45%)** para minimizar custos.

### Decisões Confirmadas
- ✅ **5 perguntas** conforme materiais do Claudio (4.1-4.5)
- ✅ **Seção 4 é a última** por agora (marca BO como completo)
- ✅ **Testes após cada fase** para validação incremental

---

## 2. Perguntas da Seção 4

| Step | Pergunta | Tipo |
|------|----------|------|
| **4.1** | Houve entrada em domicílio durante a ocorrência? | SIM/NÃO (condicional - se "NÃO", pula seção) |
| **4.2** | O que foi visto/ouvido/sentido ANTES do ingresso? (justa causa concreta) | Descritivo (min 40 chars) |
| **4.3** | Qual policial presenciou e o que exatamente viu? (graduação + nome) | Descritivo + Graduação obrigatória |
| **4.4** | Como ocorreu o ingresso? (perseguição, autorização, flagrante visual) | Escolha + Descritivo |
| **4.5** | Descreva a ação de cada policial: quem entrou, por onde, quem ficou na contenção | Descritivo detalhado (min 50 chars) |

### Constante Python
```python
SECTION4_QUESTIONS = {
    "4.1": "Houve entrada em domicílio durante a ocorrência?",
    "4.2": "O que foi visto, ouvido ou sentido ANTES do ingresso? (descreva a justa causa concreta)",
    "4.3": "Qual policial presenciou e o que exatamente viu/ouviu? (informe graduação e nome)",
    "4.4": "Como ocorreu o ingresso? (perseguição contínua, autorização do morador, flagrante visual/auditivo)",
    "4.5": "Descreva a ação de cada policial: quem entrou primeiro, por onde, quem ficou na contenção"
}

SECTION4_STEPS = ["4.1", "4.2", "4.3", "4.4", "4.5", "complete"]
```

### Constante JavaScript
```javascript
const SECTION4_QUESTIONS = {
    '4.1': 'Houve entrada em domicílio?',
    '4.2': 'O que foi visto/ouvido ANTES do ingresso (justa causa)',
    '4.3': 'Policial que presenciou (graduação + nome)',
    '4.4': 'Como ocorreu o ingresso',
    '4.5': 'Ação de cada policial'
};
```

---

## 3. Regras de Validação

```python
VALIDATION_RULES_SECTION4 = {
    "4.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "error_message": "Responda com SIM ou NÃO: houve entrada em domicílio?"
    },
    "4.2": {
        "min_length": 40,
        "examples": [
            "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria",
            "Ouvimos sons de descarga no banheiro, compatíveis com eliminação de drogas",
            "Sentimos forte odor de maconha vindo da janela aberta"
        ],
        "error_message": "Descreva o que foi visto/ouvido/sentido ANTES da entrada. A justa causa deve ser concreta e sensorial."
    },
    "4.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva viu o suspeito arremessando a sacola para dentro do imóvel",
            "O Cabo Rodrigues ouviu duas descargas vindas do banheiro"
        ],
        "error_message": "Informe a GRADUAÇÃO + nome do policial e o que ele viu/ouviu exatamente."
    },
    "4.4": {
        "min_length": 30,
        "examples": [
            "Perseguição contínua: a equipe manteve contato visual com o suspeito desde a rua até o interior",
            "Autorização do morador: o proprietário franqueou a entrada voluntariamente",
            "Flagrante visual: de fora, através da janela, visualizamos as drogas sobre a mesa"
        ],
        "error_message": "Descreva como ocorreu o ingresso: perseguição contínua, autorização ou flagrante visual/auditivo."
    },
    "4.5": {
        "min_length": 50,
        "examples": [
            "O Sargento Alves entrou primeiro pela porta principal, o Cabo Silva ficou na contenção do portão. O Soldado Pires entrou em seguida e visualizou a sacola embaixo da pia da cozinha."
        ],
        "error_message": "Descreva ação por ação: quem entrou primeiro, por onde, quem ficou fora, o que cada um fez."
    }
}
```

---

## 4. Fundamento Jurídico (Para Prompt LLM)

```text
FUNDAMENTO JURÍDICO - ENTRADA EM DOMICÍLIO:

O ingresso em domicílio sem mandado judicial só é legítimo quando houver
FUNDADAS RAZÕES, devidamente justificadas, de que ocorre flagrante delito
no interior do imóvel.

REQUISITOS STF:
- A justa causa deve existir ANTES da entrada
- O policial deve narrar FATOS OBSERVÁVEIS antes do ingresso
- Não basta alegar que "encontrou drogas depois"

ELEMENTOS CONCRETOS EXIGIDOS (pelo menos um):
1. Visualização de ilícito em andamento (pela janela, porta)
2. Perseguição contínua sem perda de contato visual
3. Flagrante auditivo (sons de embalagem, descargas)
4. Odor intenso característico
5. Autorização expressa do morador

NULIDADE CERTA (evitar):
- "Entramos por ser local conhecido por tráfico"
- "O suspeito correu pra dentro" (sem ver ilícito antes)
- "Havia denúncia" (sem constatação direta)
- "Entramos e encontramos" (justa causa posterior)
```

---

## 5. Checklist de Arquivos

### 5.1 Arquivos a CRIAR (4 arquivos)

| # | Arquivo | Executor | Status |
|---|---------|----------|--------|
| 1 | `backend/state_machine_section4.py` | **Haiku** | ⬜ Pendente |
| 2 | `backend/validator_section4.py` | **Haiku** | ⬜ Pendente |
| 3 | `tests/unit/test_section4.py` | **Haiku** | ⬜ Pendente |
| 4 | `tests/integration/test_section4_flow.py` | Sonnet | ⬜ Pendente |

### 5.2 Arquivos a MODIFICAR (10 arquivos)

| # | Arquivo | Tipo de Edição | Executor | Status |
|---|---------|----------------|----------|--------|
| 5 | `backend/main.py` | Imports + endpoints + lógica chat | **Sonnet** | ⬜ Pendente |
| 6 | `backend/llm_service.py` | Método generate_section4_text + prompt | **Sonnet** | ⬜ Pendente |
| 7 | `docs/index.html` | JS: constantes, funções, sidebar, containers | **Sonnet** | ⬜ Pendente |
| 8 | `tests/conftest.py` | Fixture section4_answers | **Haiku** | ⬜ Pendente |
| 9 | `tests/e2e/automate_release.py` | run_section4_flow() | Sonnet | ⬜ Pendente |
| 10 | `tests/e2e/test_scenarios.json` | Cenários da seção 4 | **Haiku** | ⬜ Pendente |
| 11 | `docs/TESTING.md` | Casos de teste manuais | **Haiku** | ⬜ Pendente |
| 12 | `docs/API.md` | Documentar /start_section/4 | **Haiku** | ⬜ Pendente |
| 13 | `CHANGELOG.md` | Release notes | **Haiku** | ⬜ Pendente |
| 14 | `README.md` | Atualizar versão | **Haiku** | ⬜ Pendente |

---

## 6. Ordem de Execução Detalhada

### Fase 1: Backend Core (Haiku) → Testar

**Tarefa 1.1: Criar `backend/state_machine_section4.py`**
- Copiar estrutura de `state_machine_section3.py`
- Definir `SECTION4_QUESTIONS` com 5 perguntas
- Definir `SECTION4_STEPS = ["4.1", "4.2", "4.3", "4.4", "4.5", "complete"]`
- Classe `BOStateMachineSection4` com lógica de skip em 4.1
- `get_skip_reason()` retorna "Não se aplica (não houve entrada em domicílio)"

**Tarefa 1.2: Criar `backend/validator_section4.py`**
- Copiar estrutura de `validator_section3.py`
- Implementar `VALIDATION_RULES_SECTION4` (seção 3 acima)
- Classe `ResponseValidatorSection4`

**Tarefa 1.3: Criar `tests/unit/test_section4.py`**
- `TestSection4StateMachine`: 6 testes
- `TestSection4Validator`: 6+ testes

**Tarefa 1.4: Atualizar `tests/conftest.py`**
- Adicionar fixture `section4_answers()`

```bash
# Testar após Fase 1
pytest tests/unit/test_section4.py -v
```

### Fase 2: Integração Backend (Sonnet) → Testar

**Tarefa 2.1: Modificar `backend/main.py`**
- Imports: `from state_machine_section4 import BOStateMachineSection4`
- Imports: `from validator_section4 import ResponseValidatorSection4`
- Session data: adicionar `"section4_text": None`
- Endpoint `/start_section/4`
- Endpoint `/chat`: validação para steps 4.x + geração de texto
- Endpoint `/update_answer`: validação para steps 4.x
- Endpoint `/sync_session`: suporte a steps 4.x

**Tarefa 2.2: Modificar `backend/llm_service.py`**
- Método `generate_section4_text(section_data, provider)`
- Método `_build_prompt_section4(section_data)`
- Métodos `_generate_section4_with_gemini()` e `_generate_section4_with_groq()`

**Tarefa 2.3: Criar `tests/integration/test_section4_flow.py`**
- `test_sync_section4_incomplete()`
- `test_sync_all_four_sections_complete()`
- `test_sync_section4_skipped()`
- `test_section4_validation_graduation()`
- `test_section4_validation_justa_causa()`

```bash
# Testar após Fase 2
pytest tests/integration/test_section4_flow.py -v
```

### Fase 3: Frontend (Sonnet) → Testar Manual

**Tarefa 3.1: Modificar `docs/index.html`**
- Constante `SECTION4_QUESTIONS` (5 perguntas resumidas)
- Atualizar `ALL_SECTIONS` com seção 4
- Container HTML `section4-card` e `section4-text`
- Card de transição `section4-transition-card`
- Botão `btn-start-section4`
- Função `startSection4()`
- Função `updateSidebarForSection4()`
- Atualizar `handleBotResponse()` para seção 4
- Atualizar `saveDraft()`/`restoreDraft()` para incluir seção 4
- Atualizar `copyAllSections()` para incluir seção 4
- **IMPORTANTE:** Seção 3 deve mostrar botão "Iniciar Seção 4" (não marcar boCompleted)
- **IMPORTANTE:** Seção 4 marca `boCompleted = true`

```bash
# Testar após Fase 3
python -m uvicorn backend.main:app --reload
cd docs && python -m http.server 3000
# Testar manualmente no browser
```

### Fase 4: E2E (Sonnet) → Testar Automatizado

**Tarefa 4.1: Atualizar `tests/e2e/automate_release.py`**
- Método `run_section4_flow(page, slow_mode)`
- Método `run_mobile_section4_flow(page, slow_mode)`
- Screenshots: 24-section4-start, 25-section4-error, 26-section4-final
- Suporte a `--start-section 4`

**Tarefa 4.2: Atualizar `tests/e2e/test_scenarios.json`**
- Adicionar objeto section4 com 5 steps
- Incluir cenário de erro de validação (4.3 sem graduação)

```bash
# Testar após Fase 4
python tests/e2e/automate_release.py --version v0.8.0 --start-section 4 --no-video
```

### Fase 5: Documentação (Haiku) → Commit

**Tarefa 5.1:** Atualizar `docs/TESTING.md`
**Tarefa 5.2:** Atualizar `docs/API.md`
**Tarefa 5.3:** Atualizar `CHANGELOG.md`
**Tarefa 5.4:** Atualizar `README.md`
**Tarefa 5.5:** Atualizar versão em `docs/index.html` (APP_VERSION = "0.8.0")

```bash
# Commit final
git add -A
git commit -m "feat: Implementar Seção 4 - Entrada em Domicílio (v0.8.0)"
```

---

## 7. Exemplos de Respostas Válidas (Para Testes)

```python
section4_answers = {
    "4.1": "SIM",
    "4.2": "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria em direção ao imóvel nº 120",
    "4.3": "O Sargento Silva viu o suspeito entrando no imóvel com a sacola e manteve contato visual durante toda a perseguição",
    "4.4": "Perseguição contínua: a equipe iniciou acompanhamento na Rua São Miguel e manteve contato visual ininterrupto até o interior da residência",
    "4.5": "O Sargento Silva entrou primeiro pela porta principal que estava aberta. O Cabo Rodrigues ficou na contenção do portão. O Soldado Pires entrou em seguida e localizou a sacola embaixo da pia da cozinha."
}
```

---

## 8. Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `backend/state_machine_section3.py` | Modelo para state_machine_section4 |
| `backend/validator_section3.py` | Modelo para validator_section4 |
| `backend/main.py` | Integração backend (buscar padrão da seção 3) |
| `backend/llm_service.py` | Geração de texto (buscar padrão da seção 3) |
| `docs/index.html` | Frontend completo (buscar padrão da seção 3) |
| `tests/unit/test_section3.py` | Modelo para testes unitários |
| `tests/integration/test_section3_flow.py` | Modelo para testes de integração |
| `materiais-claudio/_04_entrada_em_domicilio.txt` | Fonte das perguntas e fundamento jurídico |
| `materiais-claudio/_pacotao_2.txt` | Exemplos (Seção C) |

---

## 9. Notas Importantes

1. **Lógica de Skip:** Pergunta 4.1 = "NÃO" pula para "complete"
2. **Validação 4.3:** Requer graduação militar (igual à 3.3)
3. **Prompt LLM:** Enfatizar que justa causa vem ANTES da entrada
4. **Frontend Seção 3:** Deve mostrar botão "Iniciar Seção 4" ao completar
5. **Frontend Seção 4:** Marca `boCompleted = true` (última seção por agora)
6. **Versão:** Incrementar para v0.8.0

---

## 10. Distribuição de Custo Esperada

| Executor | Tarefas | % Estimado |
|----------|---------|------------|
| **Haiku** | 1.1, 1.2, 1.3, 1.4, 4.2, 5.1-5.5 | ~55% |
| **Sonnet** | 2.1, 2.2, 2.3, 3.1, 4.1 | ~45% |

**Estratégia:**
- **Haiku:** Arquivos novos com estrutura bem definida (copiar/adaptar), testes unitários, documentação, fixtures
- **Sonnet:** Integrações complexas que requerem entender múltiplos arquivos (main.py, llm_service.py, index.html)

---

## 11. Validação Final

### Checklist Pré-Deploy

**Backend:**
- [ ] `state_machine_section4.py` criado
- [ ] `validator_section4.py` criado
- [ ] `main.py` com imports e endpoints
- [ ] `llm_service.py` com generate_section4_text
- [ ] Testes unitários passando

**Frontend:**
- [ ] SECTION4_QUESTIONS definida
- [ ] ALL_SECTIONS atualizado
- [ ] startSection4() funcionando
- [ ] saveDraft/restoreDraft incluem seção 4
- [ ] Container de texto gerado funcionando
- [ ] Botão "Iniciar Seção 4" aparece após Seção 3

**Testes:**
- [ ] `tests/unit/test_section4.py` passando
- [ ] `tests/integration/test_section4_flow.py` passando
- [ ] E2E gerando screenshots

**Documentação:**
- [ ] `docs/TESTING.md` atualizado
- [ ] `docs/API.md` atualizado
- [ ] `CHANGELOG.md` com release notes
- [ ] `README.md` com nova versão
- [ ] APP_VERSION = "0.8.0" em index.html

---

*Documento criado em 21/12/2025 para referência durante implementação da Seção 4.*

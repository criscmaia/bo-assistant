# Plano de Implementação - Seção 5: Fundada Suspeita

**Versão:** v0.9.0
**Data:** 22/12/2025
**Custo Pré-Implementação:** USD 70.71 (ref: pós-Seção 4)

---

## Resumo Executivo

Implementar a Seção 5 (Fundada Suspeita) seguindo o padrão estabelecido pelas Seções 3 e 4, com atenção especial aos **19 pontos de modificação no frontend** documentados no SECTION_IMPLEMENTATION_GUIDE.md v2.0.

**Nota Importante:** A Seção 5 é apresentada "somente se NÃO tiver abordagem a veículo, campana ou entrada em domicílio" - porém, para manter consistência com o fluxo atual, vamos implementá-la como seção sequencial (após Seção 4), permitindo que o usuário pule se não aplicável.

---

## 1. Perguntas da Seção 5

Extraídas de `materiais-claudio/_regras_gerais_-_gpt_trafico.txt` e `_01_fundada_suspeita.txt`:

| Step | Pergunta | Tipo |
|------|----------|------|
| 5.1 | Houve abordagem por fundada suspeita (sem veículo, campana ou entrada em domicílio)? | SIM/NÃO (condicional) |
| 5.2 | O que a equipe viu ao chegar no local da ocorrência? | Descritivo |
| 5.3 | Quem viu, de onde viu, o que exatamente viu? (informe graduação e nome) | Descritivo + Graduação |
| 5.4 | Descreva as características e ações dos abordados (roupa, porte, gestos, nome completo e vulgo) | Descritivo detalhado |

**Total: 4 perguntas** (mais curta que Seções 3 e 4)

---

## 2. Checklist de Arquivos

### 2.1 Arquivos a CRIAR (4 arquivos)

| # | Arquivo | Executor | Prioridade |
|---|---------|----------|------------|
| 1 | `backend/state_machine_section5.py` | **Haiku** | Alta |
| 2 | `backend/validator_section5.py` | **Haiku** | Alta |
| 3 | `tests/unit/test_section5.py` | **Haiku** | Média |
| 4 | `tests/integration/test_section5_flow.py` | Sonnet | Média |

### 2.2 Arquivos a MODIFICAR (10 arquivos)

| # | Arquivo | Tipo de Edição | Executor |
|---|---------|----------------|----------|
| 5 | `backend/main.py` | Imports + endpoints + lógica chat | **Sonnet** |
| 6 | `backend/llm_service.py` | Método generate_section5_text + prompt | **Sonnet** |
| 7 | `docs/index.html` | JS: 19 pontos de modificação (ver checklist) | **Sonnet** |
| 8 | `tests/conftest.py` | Fixture section5_answers | **Haiku** |
| 9 | `tests/e2e/automate_release.py` | run_section5_flow() + --start-section 5 | Sonnet |
| 10 | `tests/e2e/test_scenarios.json` | Cenários da seção 5 | **Haiku** |
| 11 | `docs/TESTING.md` | Casos de teste manuais | **Haiku** |
| 12 | `docs/API.md` | Documentar /start_section/5 | **Haiku** |
| 13 | `CHANGELOG.md` | Release notes v0.9.0 | **Haiku** |
| 14 | `README.md` | Atualizar versão e status (5/8 seções) | **Haiku** |

---

## 3. Ordem de Execução Detalhada

### Fase 1: Backend Core (Haiku)

**Tarefa 1.1: Criar `backend/state_machine_section5.py`**
- Copiar estrutura de `state_machine_section4.py`
- Definir `SECTION5_QUESTIONS` com 4 perguntas
- Definir `SECTION5_STEPS = ["5.1", "5.2", "5.3", "5.4", "complete"]`
- Classe `BOStateMachineSection5` com lógica de skip em 5.1
- `get_skip_reason()` retorna "Não se aplica (não houve abordagem por fundada suspeita)"

**Tarefa 1.2: Criar `backend/validator_section5.py`**
- Copiar estrutura de `validator_section4.py`
- Definir `VALIDATION_RULES_SECTION5`:
  ```python
  "5.1": { valid_responses: ["SIM", "NÃO", ...] }
  "5.2": { min_length: 40, examples: [...] }  # O que viu ao chegar
  "5.3": { min_length: 30, required_keywords: graduações }  # Quem viu + graduação
  "5.4": { min_length: 50, examples: [...] }  # Características individualizadas
  ```

### Fase 2: Testes Unitários (Haiku)

**Tarefa 2.1: Criar `tests/unit/test_section5.py`**
- `TestSection5StateMachine`: 6 testes (init, questions, steps, skip, continue, full_flow)
- `TestSection5Validator`: 5+ testes (5.1 yes/no, 5.3 graduação, 5.4 min_length)

**Tarefa 2.2: Atualizar `tests/conftest.py`**
- Adicionar fixture `section5_answers()` com 4 respostas válidas

### Fase 3: Integração Backend (Sonnet)

**Tarefa 3.1: Modificar `backend/main.py`**
- Imports: `from state_machine_section5 import BOStateMachineSection5`
- Imports: `from validator_section5 import ResponseValidatorSection5`
- Session data: adicionar `"section5_text": None`
- Endpoint `/start_section/5`: criar instância BOStateMachineSection5
- Endpoint `/chat`:
  - Validação para steps 5.x
  - Chamada a `generate_section5_text()` quando completa
- Endpoint `/update_answer`: validação para steps 5.x
- Endpoint `/sync_session`: suporte a steps 5.x

**Tarefa 3.2: Modificar `backend/llm_service.py`**
- Método `generate_section5_text(section_data, provider)`
- Método `_build_prompt_section5(section_data)` com:
  - Fundamento jurídico (STF HC 261029, Art. 244 CPP)
  - Regras de narração
  - Exemplos de modelos narrativos
  - Erros a evitar (em atitude suspeita, nervosismo sem contexto)
- Métodos `_generate_section5_with_gemini()` e `_generate_section5_with_groq()`

### Fase 4: Frontend (Sonnet) - ⚠️ CHECKLIST DE 19 PONTOS

**Tarefa 4.1: Modificar `docs/index.html`**

#### 4.1.1 Constantes e Estruturas (INÍCIO DO ARQUIVO)
| # | O que modificar | Buscar por | Ação |
|---|-----------------|------------|------|
| 1 | Constante de perguntas | `SECTION4_QUESTIONS` | Criar `SECTION5_QUESTIONS` logo após |
| 2 | ALL_SECTIONS | `const ALL_SECTIONS` | Adicionar entrada para seção 5 (emoji: 🎯, cor: pink) |

#### 4.1.2 Funções Principais (CRIAR NOVAS)
| # | Função | Modelo | Cor |
|---|--------|--------|-----|
| 3 | `startSection5()` | `startSection4()` | **pink** (rosa) |
| 4 | `updateSidebarForSection5()` | `updateSidebarForSection4()` | - |

#### 4.1.3 Função `handleBotResponse()` - 4 LOCAIS
| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 5 | Cálculo de progresso | `"currentSection === 4"` (progresso) | Adicionar `else if (currentSection === 5)` |
| 6 | Mensagem de conclusão | `"Seção 4 completa!"` | Adicionar mensagem para seção 5 |
| 7 | Criação de card de transição | `"currentSection === 4 && !boCompleted"` | Criar card para seção 5 → 6 (SE não for última) |
| 8 | Marcar boCompleted | `"boCompleted = true"` (seção 4) | MOVER para seção 5 (agora é a última) |

#### 4.1.4 Função `restoreFromDraft()` - 5 LOCAIS
| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 9 | Restaurar textos gerados | `"draft.generatedTexts.section4"` | Adicionar `section5` |
| 10 | Atualizar sidebar | `"updateSidebarForSection4"` | Adicionar `else if (currentSection === 5)` |
| 11 | Contagem de respostas | `"section4Count"` | Criar `section5Count` |
| 12 | Cálculo de progresso | `"updateSidebarProgress(section4Count"` | Adicionar `else if (currentSection === 5)` |
| 13 | Próxima pergunta | `"SECTION4_QUESTIONS[currentQuestionStep]"` | Adicionar `else if (currentSection === 5)` |
| 14 | Botão de transição | `"btn-start-section4"` | Criar botão para seção 5 |
| 15 | Seção completa | `"currentSection === 4"` no bloco final | Tratar caso seção 5 completa |

#### 4.1.5 Funções de Draft
| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 16 | saveDraft | `"section4"` em saveDraft | Adicionar `section5` |
| 17 | restoreDraft | `"section4"` em restoreDraft | Adicionar tratamento para `section5` |

#### 4.1.6 Função `updateHeaderSection()`
| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 18 | Header | `"Seção 4 - Entrada em Domicílio"` | Adicionar `else if (currentSection === 5)` |

#### 4.1.7 Função `copyAllSections()`
| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 19 | Copiar texto | `"section4-text"` | Adicionar seletor para seção 5 |

### Fase 5: Testes de Integração (Sonnet)

**Tarefa 5.1: Criar `tests/integration/test_section5_flow.py`**
- `test_sync_section5_incomplete()`
- `test_sync_all_five_sections_complete()`
- `test_sync_section5_skipped()`
- `test_section5_validation_graduation()`
- `test_section5_validation_individualizacao()`

**Tarefa 5.2: Atualizar `tests/e2e/automate_release.py`**
- Método `run_section5_flow(page, slow_mode)`
- Método `run_mobile_section5_flow(page, slow_mode)`
- Screenshots: 27-section5-start, 28-section5-error, 29-section5-final
- Suporte a `--start-section 5`
- Atualizar `prepare_sections_via_api()` para preencher seções 1-4

**Tarefa 5.3: Atualizar `tests/e2e/test_scenarios.json`**
- Adicionar objeto section5 com 4 steps
- Incluir cenário de erro de validação (5.3 sem graduação)

### Fase 6: Documentação (Haiku)

**Tarefa 6.1: Atualizar `docs/TESTING.md`**
- Seção "Seção 5: Fundada Suspeita"
- Casos de teste manuais (Teste 13, 14, 15)
- Respostas válidas exemplo

**Tarefa 6.2: Atualizar `docs/API.md`**
- Documentar `POST /start_section/5`
- Exemplos de request/response

**Tarefa 6.3: Atualizar `CHANGELOG.md`**
- Entry para v0.9.0
- Lista de mudanças

**Tarefa 6.4: Atualizar `README.md`**
- Versão 0.9.0
- Status das seções (5/8 implementadas)

---

## 4. Conteúdo Específico da Seção 5

### 4.1 Perguntas Completas

```python
SECTION5_QUESTIONS = {
    "5.1": "Houve abordagem por fundada suspeita (sem veículo, campana ou entrada em domicílio)?",
    "5.2": "O que a equipe viu ao chegar no local da ocorrência?",
    "5.3": "Quem viu, de onde viu, o que exatamente viu? (informe graduação e nome)",
    "5.4": "Descreva as características e ações dos abordados (roupa, porte, gestos, nome completo e vulgo)"
}
```

### 4.2 Regras de Validação

```python
VALIDATION_RULES_SECTION5 = {
    "5.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO", "sim", "não", "nao"],
        "error_message": "Responda com SIM ou NÃO: houve abordagem por fundada suspeita?"
    },
    "5.2": {
        "min_length": 40,
        "examples": [
            "Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, visualizamos um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro",
            "No local indicado pela denúncia, conhecido por registros de tráfico, observamos indivíduo realizando contato rápido com motoristas que paravam e entregando pequenos pacotes"
        ],
        "error_message": "Descreva o que a equipe viu ao chegar. Mínimo 40 caracteres com detalhes concretos (local, contexto, comportamento observado)."
    },
    "5.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento João, de dentro da viatura estacionada a 20 metros, visualizou o suspeito retirando invólucros do buraco no muro",
            "O Cabo Almeida, posicionado na esquina oposta, viu o indivíduo entregar pacotes e receber dinheiro"
        ],
        "error_message": "Informe a GRADUAÇÃO + nome do policial, de onde viu e o que exatamente viu."
    },
    "5.4": {
        "min_length": 50,
        "examples": [
            "Homem de camisa vermelha e bermuda jeans, porte atlético, gestos nervosos ao perceber a viatura, posteriormente identificado como JOÃO DA SILVA, vulgo 'Vermelho'. Ao ser abordado, tentou esconder objeto no bolso da bermuda."
        ],
        "error_message": "Descreva INDIVIDUALMENTE cada abordado: roupa, porte físico, gestos, e identificação completa (nome + vulgo). Mínimo 50 caracteres."
    }
}
```

### 4.3 Prompt LLM (Fundamento Jurídico)

```
FUNDAMENTO JURÍDICO - FUNDADA SUSPEITA:

Baseado no HC 261029 do STF e Art. 244 do CPP.

A busca pessoal exige INDÍCIOS CONCRETOS E OBJETIVOS, não sendo suficiente:
- Nervosismo isolado
- Mera presença em local de criminalidade

BASES LEGÍTIMAS PARA BUSCA PESSOAL:

1. CONDUTA VISÍVEL E ANORMAL:
   - Correr ou fugir
   - Desfazer-se de objetos
   - Vigiar terceiros
   - Simular transações

2. INFORMAÇÃO PRÉVIA CONFIÁVEL:
   - Denúncia anônima corroborada (por observação direta)
   - BOs anteriores do local
   - Relatórios de inteligência
   - Registros de monitoramento

3. CONTEXTO SENSÍVEL RECONHECIDO:
   - Ponto de tráfico comprovado (por registros, investigações ou ocorrências recentes)

REQUISITOS DA ABORDAGEM:
1. Sequência lógica dos fatos observados
2. Individualização das percepções ("quem viu o quê")
3. Conexão entre comportamento e suspeita de crime específico

ERROS A EVITAR (NULIDADE CERTA):
- "em atitude suspeita" (vago demais)
- "demonstrou nervosismo" (sem descrever como)
- "área conhecida pelo tráfico" (sem base objetiva)
- "foi abordado por fundadas suspeitas" (conclusão jurídica, não fato)

REGRA DE OURO: "O juiz não lê intenções, lê fatos"
```

---

## 5. Distribuição Haiku vs Sonnet

| Executor | Tarefas | % do Trabalho |
|----------|---------|---------------|
| **Haiku** | 1.1, 1.2, 2.1, 2.2, 5.3, 6.1, 6.2, 6.3, 6.4 | ~55% |
| **Sonnet** | 3.1, 3.2, 4.1, 5.1, 5.2 | ~45% |

**Estimativa de Custo:** ~$12-15 (baseado no custo da Seção 4)

---

## 6. Validação Final

### Checklist Pré-Deploy

**Backend:**
- [ ] `state_machine_section5.py` criado
- [ ] `validator_section5.py` criado
- [ ] `main.py` com imports e endpoints
- [ ] `llm_service.py` com generate_section5_text
- [ ] Testes unitários passando

**Frontend (19 pontos):**
- [ ] SECTION5_QUESTIONS definida
- [ ] ALL_SECTIONS atualizado (emoji: 🎯, cor: pink)
- [ ] startSection5() criada
- [ ] updateSidebarForSection5() criada
- [ ] handleBotResponse() - 4 locais atualizados
- [ ] restoreFromDraft() - 5 locais atualizados
- [ ] saveDraft/restoreDraft - 2 locais atualizados
- [ ] updateHeaderSection() atualizado
- [ ] copyAllSections() atualizado

**Testes:**
- [ ] `tests/unit/test_section5.py` passando
- [ ] `tests/integration/test_section5_flow.py` passando
- [ ] E2E gerando screenshots

### Comandos de Teste

```bash
# Testes unitários
pytest tests/unit/test_section5.py -v

# Testes de integração
pytest tests/integration/test_section5_flow.py -v

# E2E (início rápido na seção 5)
python tests/e2e/automate_release.py --version v0.9.0 --start-section 5 --no-video

# E2E completo
python tests/e2e/automate_release.py --version v0.9.0
```

---

## 7. Arquivos Críticos (Referência)

| Arquivo | Propósito |
|---------|-----------|
| `backend/state_machine_section4.py` | Modelo para state_machine_section5 |
| `backend/validator_section4.py` | Modelo para validator_section5 |
| `backend/main.py` | Integração backend |
| `backend/llm_service.py` | Geração de texto |
| `docs/index.html` | Frontend completo (19 pontos!) |
| `materiais-claudio/_01_fundada_suspeita.txt` | Fonte das perguntas e fundamento jurídico |
| `materiais-claudio/_regras_gerais_-_gpt_trafico.txt` | Regras gerais |

---

## 8. Notas de Implementação

1. **Lógica de Skip:** Pergunta 5.1 = "NÃO" pula para "complete"
2. **Validação 5.3:** Requer graduação militar (igual às seções 3 e 4)
3. **Validação 5.4:** Requer individualização (roupa, porte, gestos, nome + vulgo)
4. **Prompt LLM:** Enfatizar fatos concretos, evitar termos vagos
5. **Frontend:** Seção 4 continua o fluxo para Seção 5 (remover boCompleted da seção 4)
6. **Frontend:** Seção 5 marca `boCompleted = true` (última seção por agora)
7. **Versão:** Incrementar para v0.9.0
8. **Perguntas:** 4 perguntas (seção mais curta)
9. **Cor:** Pink/Rosa (seguindo esquema do SECTION_IMPLEMENTATION_GUIDE)

---

## 9. Decisões do Usuário (CONFIRMADAS ✅)

- ✅ **4 perguntas** conforme materiais (5.1-5.4)
- ✅ **Seção 5 é a última** por agora (marca BO como completo)
- ✅ **Cor pink/rosa** para a seção 5
- ✅ **Testes após cada fase** para validação incremental

---

## 10. Workflow de Execução com Testes

### Fase 1: Backend Core → Testar
```bash
# Após criar state_machine_section5.py e validator_section5.py
pytest tests/unit/test_section5.py -v
```

### Fase 2: Integração Backend → Testar
```bash
# Após modificar main.py e llm_service.py
pytest tests/integration/test_section5_flow.py -v
```

### Fase 3: Frontend → Testar Manual
```bash
# Iniciar servers
python -m uvicorn backend.main:app --reload
cd docs && python -m http.server 3000
# Testar manualmente no browser
# IMPORTANTE: Verificar os 19 pontos de modificação!
```

### Fase 4: E2E → Testar Automatizado
```bash
# Após atualizar automate_release.py
python tests/e2e/automate_release.py --version v0.9.0 --start-section 5 --no-video
```

### Fase 5: Documentação → Commit
```bash
# Após atualizar docs
git add -A
git commit -m "feat: Implementar Seção 5 - Fundada Suspeita (v0.9.0)"
```

---

## 11. Exemplos de Respostas Válidas (para testes)

### 5.1 - Houve abordagem por fundada suspeita?
```
SIM
```

### 5.2 - O que a equipe viu ao chegar no local?
```
Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, visualizamos um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro e entregando-os a motociclistas que paravam rapidamente, recebendo dinheiro em troca.
```

### 5.3 - Quem viu, de onde viu, o que exatamente?
```
O Sargento João, de dentro da viatura estacionada a aproximadamente 20 metros do local, visualizou o suspeito retirando invólucros do buraco no muro e realizando as entregas por cerca de dois minutos antes de perceber a aproximação policial.
```

### 5.4 - Características e ações dos abordados
```
Homem de camisa vermelha e bermuda jeans azul, porte atlético, aproximadamente 1,75m de altura. Ao perceber a aproximação da viatura, demonstrou nervosismo acentuado, escondeu parte do material no bolso e tentou fugir em direção ao beco lateral. Posteriormente identificado como JOÃO DA SILVA SANTOS, vulgo 'Vermelho', CPF 123.456.789-00.
```

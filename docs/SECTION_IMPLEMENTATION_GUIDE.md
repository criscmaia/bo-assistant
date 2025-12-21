# Guia de Implementação de Novas Seções

**Versão:** 1.0
**Última atualização:** 21/12/2025
**Baseado em:** Experiência da implementação da Seção 3 (Campana)

Este documento fornece instruções detalhadas para implementar qualquer nova seção do BO Inteligente, otimizado para uso com Claude Haiku (60% das tarefas) e Sonnet (40% das tarefas).

---

## Índice

1. [Fonte das Perguntas](#1-fonte-das-perguntas)
2. [Checklist de Arquivos](#2-checklist-de-arquivos)
3. [Instruções para Haiku](#3-instruções-para-haiku)
4. [Instruções para Sonnet](#4-instruções-para-sonnet)
5. [Workflow de Testes E2E](#5-workflow-de-testes-e2e)
6. [Bugs Comuns e Soluções](#6-bugs-comuns-e-soluções)
7. [Validação Final](#7-validação-final)

---

## 1. Fonte das Perguntas

### 1.1 Estrutura de Materiais do Claudio

```
materiais-claudio/
├── _regras_gerais_-_gpt_trafico.txt    # ÍNDICE GERAL (todas as 8 seções)
├── _1_inicio_do_bo.txt                  # Seção 1 - Modelos narrativos
├── _03_busca_veicular.txt               # Seção 2 - Detalhes específicos
├── _secao_-_campana.txt                 # Seção 3 - Detalhes específicos
├── _04_entrada_em_domicilio.txt         # Seção 4 - Detalhes específicos
├── _01_fundada_suspeita.txt             # Seção 5 - Detalhes específicos
├── _02_uso_da_forca_e_algemas.txt       # Seção 6 - Detalhes específicos
├── _08_atendimento_medico_*.txt         # Seção 6/8 - Complementar
├── _pacotao_1.txt                       # Exemplos CURTOS (certo/errado)
└── _pacotao_2.txt                       # Exemplos DETALHADOS por seção
```

### 1.2 Mapeamento Seção → Arquivos

| Seção | Nome | Arquivo Principal | Arquivo Complementar | Linhas em _regras_gerais_ |
|-------|------|-------------------|----------------------|---------------------------|
| 1 | Contexto | `_1_inicio_do_bo.txt` | _pacotao_2.txt | 20-27 |
| 2 | Veículo | `_03_busca_veicular.txt` | _pacotao_1.txt | 29-40 |
| 3 | Campana | `_secao_-_campana.txt` | _pacotao_2.txt (Seção B) | 42-52 |
| 4 | Domicílio | `_04_entrada_em_domicilio.txt` | _pacotao_2.txt (Seção C) | 54-60 |
| 5 | Fundada Suspeita | `_01_fundada_suspeita.txt` | _pacotao_2.txt (Seção A) | 62-67 |
| 6 | Uso da Força | `_02_uso_da_forca_e_algemas.txt` | _08_atendimento_medico_*.txt | 69-75 |
| 7 | Apreensões | _pacotao_2.txt (Seção E) | - | 77-83 |
| 8 | Condução | _pacotao_2.txt (Seção F) | - | 85-94 |

### 1.3 Como Usar os Materiais

**Passo 1: Extrair perguntas**
```bash
# Ler o índice geral para ver as perguntas da seção N
cat materiais-claudio/_regras_gerais_-_gpt_trafico.txt | grep -A 20 "SEÇÃO N"
```

**Passo 2: Extrair fundamento jurídico e exemplos**
```bash
# Ler o arquivo específico da seção
cat materiais-claudio/_arquivo_da_secao_.txt
```

O arquivo específico contém:
- **Fundamento jurídico** (não exibir ao operador, usar no prompt do LLM)
- **Checklist operacional** (base para as perguntas)
- **Modelos narrativos** (exemplos BOM para validação)
- **Erros a evitar** (exemplos RUIM para validação)

**Passo 3: Extrair exemplos certo/errado**
```bash
# Pacotão 1 - Exemplos curtos
cat materiais-claudio/_pacotao_1.txt

# Pacotão 2 - Exemplos detalhados por seção
cat materiais-claudio/_pacotao_2.txt
```

### 1.4 Como Definir Regras de Validação

Para cada pergunta, definir:

| Campo | Como Extrair |
|-------|--------------|
| `min_length` | Baseado no tamanho dos exemplos BOM |
| `required_keywords` | Termos obrigatórios (ex: graduação militar) |
| `valid_responses` | Para perguntas SIM/NÃO |
| `examples` | 2-3 exemplos BOM do arquivo específico |
| `error_message` | Baseado nos "Erros a evitar" |

---

## 2. Checklist de Arquivos

### 2.1 Arquivos a Criar (por seção)

| # | Arquivo | Modelo | Executor |
|---|---------|--------|----------|
| 1 | `backend/state_machine_sectionN.py` | state_machine_section3.py | Haiku |
| 2 | `backend/validator_sectionN.py` | validator_section3.py | Haiku |
| 3 | `tests/unit/test_sectionN.py` | tests/unit/test_section3.py | Haiku |
| 4 | `tests/integration/test_sectionN_flow.py` | tests/integration/test_section3_flow.py | Sonnet |

### 2.2 Arquivos a Modificar

| # | Arquivo | Tipo de Edição | Executor |
|---|---------|----------------|----------|
| 5 | `backend/main.py` | Imports, endpoints, lógica | Sonnet |
| 6 | `backend/llm_service.py` | Método generate_sectionN_text | Sonnet |
| 7 | `docs/index.html` | JS: constantes, funções, sidebar | Sonnet |
| 8 | `tests/conftest.py` | Fixture sectionN_answers | Haiku |
| 9 | `tests/e2e/automate_release.py` | run_sectionN_flow() | Sonnet |
| 10 | `tests/e2e/test_scenarios.json` | Cenários da seção N | Haiku |
| 11 | `docs/TESTING.md` | Casos de teste manuais | Haiku |
| 12 | `docs/API.md` | Documentar /start_section/N | Haiku |
| 13 | `CHANGELOG.md` | Release notes | Haiku |
| 14 | `README.md` | Atualizar versão e status | Haiku |

### 2.3 Ordem de Execução

```
1. state_machine_sectionN.py     [Haiku] → Nenhuma dependência
2. validator_sectionN.py         [Haiku] → Nenhuma dependência
3. tests/unit/test_sectionN.py   [Haiku] → Depende de 1, 2
4. tests/conftest.py             [Haiku] → Nenhuma dependência
5. main.py                       [Sonnet] → Depende de 1, 2
6. llm_service.py                [Sonnet] → Nenhuma dependência
7. index.html                    [Sonnet] → Depende de 5
8. test_sectionN_flow.py         [Sonnet] → Depende de 5, 7
9. automate_release.py           [Sonnet] → Depende de 7
10. test_scenarios.json          [Haiku] → Nenhuma dependência
11-14. Documentação              [Haiku] → Após todos os anteriores
```

---

## 3. Instruções para Haiku

### 3.1 Criar `backend/state_machine_sectionN.py`

**Arquivo de referência:** `backend/state_machine_section3.py`

**Instruções passo a passo:**

1. Copiar o arquivo `backend/state_machine_section3.py`
2. Renomear para `backend/state_machine_sectionN.py`
3. Fazer substituições exatas:

| De | Para |
|----|------|
| `SECTION3_QUESTIONS` | `SECTIONN_QUESTIONS` |
| `SECTION3_STEPS` | `SECTIONN_STEPS` |
| `BOStateMachineSection3` | `BOStateMachineSectionN` |
| `"3.1"` a `"3.X"` | `"N.1"` a `"N.Y"` |
| `Seção 3: Campana` | `Seção N: [Nome]` |

4. Substituir o dicionário de perguntas (fornecido separadamente)
5. Ajustar `get_skip_reason()` com mensagem apropriada

**Template da estrutura:**
```python
SECTIONN_QUESTIONS = {
    "N.1": "[Pergunta condicional SIM/NÃO]",
    "N.2": "[Pergunta detalhada]",
    # ... até N.Y
}

SECTIONN_STEPS = ["N.1", "N.2", ..., "N.Y", "complete"]

class BOStateMachineSectionN:
    # Mesma estrutura de BOStateMachineSection3
```

### 3.2 Criar `backend/validator_sectionN.py`

**Arquivo de referência:** `backend/validator_section3.py`

**Instruções passo a passo:**

1. Copiar o arquivo `backend/validator_section3.py`
2. Renomear para `backend/validator_sectionN.py`
3. Fazer substituições:

| De | Para |
|----|------|
| `VALIDATION_RULES_SECTION3` | `VALIDATION_RULES_SECTIONN` |
| `ResponseValidatorSection3` | `ResponseValidatorSectionN` |

4. Substituir regras de validação (baseadas nos materiais do Claudio)
5. Remover/adicionar funções auxiliares conforme necessidade

**Template de regra:**
```python
"N.X": {
    "min_length": 30,
    "required_keywords": ["termo1", "termo2"],  # Se aplicável
    "examples": [
        "Exemplo bom 1...",
        "Exemplo bom 2..."
    ],
    "error_message": "Mensagem de erro com orientação..."
}
```

### 3.3 Criar `tests/unit/test_sectionN.py`

**Arquivo de referência:** `tests/unit/test_section3.py`

**Instruções:**
1. Copiar estrutura de test_section3.py
2. Substituir referências de seção 3 → seção N
3. Adaptar testes de validação conforme regras da nova seção

**Testes obrigatórios:**
- `test_initialization` - Verifica inicialização correta
- `test_questions_defined` - Verifica todas as perguntas
- `test_steps_defined` - Verifica todos os steps
- `test_skip_section_on_no` - Testa skip quando N.1 = "NÃO"
- `test_continue_on_yes` - Testa continuação quando N.1 = "SIM"
- `test_full_flow` - Testa fluxo completo
- `test_validate_N_X_*` - Testes de validação por pergunta

### 3.4 Atualizar `tests/conftest.py`

**Adicionar fixture após `section3_answers`:**

```python
@pytest.fixture
def sectionN_answers() -> Dict:
    """Respostas válidas para Seção N"""
    return {
        "N.1": "SIM",
        "N.2": "[Resposta válida completa...]",
        # ... todas as perguntas
    }
```

### 3.5 Atualizar Documentação

**docs/TESTING.md:**
- Adicionar seção "Seção N: [Nome]"
- Listar casos de teste manuais
- Incluir respostas válidas para cada pergunta

**docs/API.md:**
- Documentar `POST /start_section/N`
- Incluir exemplos de request/response

---

## 4. Instruções para Sonnet

### 4.1 Modificar `backend/main.py`

**Pontos de modificação:**

1. **Imports (início do arquivo):**
```python
from state_machine_sectionN import BOStateMachineSectionN
from validator_sectionN import ResponseValidatorSectionN
```

2. **Session structure:**
```python
"sectionN_text": Optional[str] = None
```

3. **Endpoint `/start_section/{section_number}`:**
- Adicionar N à lista de seções válidas
- Adicionar lógica para `section_number == N`

4. **Endpoint `/chat`:**
- Adicionar lógica de validação para steps N.x
- Adicionar chamada a `generate_sectionN_text()`

5. **Endpoint `/update_answer`:**
- Adicionar validação para steps N.x

6. **Endpoint `/sync_session`:**
- Adicionar suporte a steps N.x

### 4.2 Modificar `backend/llm_service.py`

**Métodos a adicionar:**

```python
def generate_sectionN_text(self, section_data: Dict, provider: str = "gemini") -> str:
    """Gera texto narrativo da Seção N - [Nome]"""
    # Implementar seguindo padrão de generate_section3_text

def _generate_sectionN_with_gemini(self, section_data: Dict) -> str:
    # Implementar com prompt específico

def _generate_sectionN_with_groq(self, section_data: Dict) -> str:
    # Implementar com prompt específico
```

**Prompt deve incluir:**
- Regras de narração (3ª pessoa, voz ativa, ordem direta)
- Fundamento jurídico (extraído dos materiais do Claudio)
- Informações coletadas (respostas N.2 a N.Y)

### 4.3 Modificar `docs/index.html`

**Pontos de modificação:**

1. **Constante de perguntas:**
```javascript
const SECTIONN_QUESTIONS = {
    'N.1': 'Resumo da pergunta',
    'N.2': 'Resumo da pergunta',
    // ...
};
```

2. **ALL_SECTIONS:**
```javascript
N: { emoji: '📋', name: '[Nome]', questions: SECTIONN_QUESTIONS }
```

3. **Função startSectionN():**
- Similar a startSection3()
- Chamada após seção N-1 completa

4. **Função updateSidebarForSectionN():**
- Atualizar sidebar com steps N.x

5. **handleBotResponse:**
- Adicionar lógica para exibir botão "Iniciar Seção N"
- Adicionar container de texto gerado para seção N

6. **saveDraft/restoreDraft:**
- Incluir answers N.x no draft

### 4.4 Modificar `tests/e2e/automate_release.py`

**Adicionar:**
- `run_sectionN_flow()` - Fluxo de preenchimento da seção N
- Screenshots específicos da seção N
- Suporte a `--start-section N`

---

## 5. Workflow de Testes E2E

### 5.1 Preparar Cenários em `test_scenarios.json`

Adicionar cenário para seção N:

```json
{
  "sectionN": {
    "N.1": "SIM",
    "N.2": "Resposta válida completa...",
    // ... todas as perguntas
  }
}
```

### 5.2 Screenshots Obrigatórios

Por seção, capturar:
- `XX-sectionN-start.png` - Início da seção
- `XX-sectionN-progress.png` - Meio do preenchimento
- `XX-sectionN-final.png` - Texto gerado

### 5.3 Uso do Fast-Start

```bash
# Testar apenas seção N (seções anteriores via API)
python tests/e2e/automate_release.py --version vX.Y.Z --start-section N --no-video

# Testar fluxo completo
python tests/e2e/automate_release.py --version vX.Y.Z
```

### 5.4 Validação de Screenshots

Antes de commit:
1. Verificar que screenshots foram gerados
2. Verificar que não há erros visíveis
3. Verificar que texto gerado está correto

---

## 6. Bugs Comuns e Soluções

### Bug 1: `update_answer` não valida nova seção

**Sintoma:** Validação não funciona para steps N.x

**Causa:** Endpoint `/update_answer` não importa/chama validador da nova seção

**Solução:**
```python
# Em main.py, adicionar import
from validator_sectionN import ResponseValidatorSectionN

# Em /update_answer, adicionar lógica
if step.startswith("N."):
    is_valid, error = ResponseValidatorSectionN.validate(step, answer)
```

### Bug 2: Sidebar não atualiza após seção completa

**Sintoma:** Seção N não marca como completada (✅)

**Causa:** Falta entrada em ALL_SECTIONS no frontend

**Solução:**
```javascript
// Em index.html
const ALL_SECTIONS = {
    // ...
    N: { emoji: '📋', name: '[Nome]', questions: SECTIONN_QUESTIONS }
};
```

### Bug 3: Draft não restaura seção N

**Sintoma:** Respostas N.x não são restauradas ao reabrir página

**Causa:** saveDraft/restoreDraft não incluem nova seção

**Solução:**
```javascript
// Em saveDraft()
draft.sectionN_answers = { /* ... */ };

// Em restoreFromDraft()
if (draft.sectionN_answers) {
    // restaurar respostas
}
```

### Bug 4: Botão "Iniciar Seção N" não aparece

**Sintoma:** Após seção N-1 completa, não há botão para iniciar N

**Causa:** Lógica de exibição não inclui nova seção

**Solução:**
```javascript
// Em handleBotResponse()
if (data.section_complete && data.current_section === N-1) {
    // Exibir botão "Iniciar Seção N"
}
```

### Bug 5: Texto gerado não aparece no container correto

**Sintoma:** Texto da seção N aparece no container errado ou não aparece

**Causa:** Falta container específico ou seletor incorreto

**Solução:**
```javascript
// Adicionar container em index.html
<div id="sectionN-text-container" class="hidden">...</div>

// Atualizar lógica de exibição
document.getElementById('sectionN-text-container').innerHTML = data.sectionN_text;
```

---

## 7. Validação Final

### 7.1 Checklist Pré-Deploy

**Backend:**
- [ ] `state_machine_sectionN.py` criado e testado
- [ ] `validator_sectionN.py` criado e testado
- [ ] `main.py` atualizado com imports e endpoints
- [ ] `llm_service.py` com método generate_sectionN_text
- [ ] Testes unitários passando

**Frontend:**
- [ ] Constante SECTIONN_QUESTIONS definida
- [ ] ALL_SECTIONS atualizado
- [ ] Funções startSectionN/updateSidebar funcionando
- [ ] saveDraft/restoreDraft incluem seção N
- [ ] Container de texto gerado funcionando

**Testes:**
- [ ] `tests/unit/test_sectionN.py` passando
- [ ] `tests/integration/test_sectionN_flow.py` passando
- [ ] `tests/e2e/automate_release.py` gerando screenshots

**Documentação:**
- [ ] `docs/TESTING.md` atualizado
- [ ] `docs/API.md` atualizado
- [ ] `CHANGELOG.md` com release notes
- [ ] `README.md` com nova versão

### 7.2 Testes Manuais Obrigatórios

1. **Fluxo completo local:**
   - Iniciar backend: `python -m uvicorn backend.main:app --reload`
   - Iniciar frontend: `cd docs && python -m http.server 3000`
   - Completar todas as seções até N
   - Verificar texto gerado

2. **Fluxo de skip:**
   - Responder "NÃO" na pergunta N.1
   - Verificar que seção é pulada corretamente

3. **Fluxo de draft:**
   - Preencher parcialmente seção N
   - Fechar e reabrir página
   - Verificar que respostas são restauradas

4. **Testes E2E:**
   ```bash
   python tests/e2e/automate_release.py --version vX.Y.Z --no-video
   ```

### 7.3 Atualizar Versão

1. Incrementar versão em `docs/index.html` (APP_VERSION)
2. Adicionar entrada no `CHANGELOG.md`
3. Atualizar status no `README.md`
4. Commit com mensagem: `feat: Implementar Seção N - [Nome] (vX.Y.Z)`

---

## Referências

- [CLAUDE_CODE_WORKFLOW.md](CLAUDE_CODE_WORKFLOW.md) - Estratégia Haiku/Sonnet
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura técnica
- [TESTING.md](TESTING.md) - Guia de testes
- [API.md](API.md) - Referência de endpoints

# Guia de Implementação de Novas Seções

**Versão:** 5.0
**Última atualização:** 23/12/2025
**Baseado em:** Experiência das implementações das Seções 3 (Campana), 4 (Entrada em Domicílio), 5 (Fundada Suspeita), 6 (Reação e Uso da Força) e 7 (Apreensões e Cadeia de Custódia)

Este documento fornece instruções detalhadas para implementar qualquer nova seção do BO Inteligente, otimizado para uso com Claude Haiku (60% das tarefas) e Sonnet (40% das tarefas).

> **Lição Aprendida (Seções 4, 5, 6 e 7):** As implementações das Seções 4, 5, 6 e 7 revelaram que alguns pontos críticos no frontend (barra de progresso, restauração de rascunho, **limpeza de botões de transição**) requerem modificações em MÚLTIPLOS locais. A Seção 6 introduziu novas funcionalidades de validação (**frases proibidas** e **validação condicional de hospital**). A Seção 7 introduziu **validação de resposta negativa** (`allow_none_response`) e revelou que o arquivo `docs/logs.html` precisa ser atualizado para cada nova seção. Este guia foi atualizado com checklists específicos para evitar esses bugs.

---

## Índice

1. [Fonte das Perguntas](#1-fonte-das-perguntas)
2. [Checklist de Arquivos](#2-checklist-de-arquivos)
3. [Instruções para Haiku](#3-instruções-para-haiku)
4. [Instruções para Sonnet](#4-instruções-para-sonnet)
5. [Workflow de Testes E2E](#5-workflow-de-testes-e2e)
6. [Bugs Comuns e Soluções](#6-bugs-comuns-e-soluções)
7. [Validação Final](#7-validação-final)
8. [Lições Aprendidas (Seção 4)](#8-lições-aprendidas-seção-4)
9. [Lições Aprendidas (Seção 5)](#9-lições-aprendidas-seção-5)
10. [Lições Aprendidas (Seção 6)](#10-lições-aprendidas-seção-6)
11. [Lições Aprendidas (Seção 7)](#11-lições-aprendidas-seção-7)

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
    "required_keywords_any": ["opcao1", "opcao2"],  # Qualquer uma (OR)
    "forbidden_phrases": ["frase proibida 1", "frase proibida 2"],  # NOVO na Seção 6
    "conditional_hospital": True,  # NOVO: Se True, exige hospital quando há lesão
    "examples": [
        "Exemplo bom 1...",
        "Exemplo bom 2..."
    ],
    "error_message": "Mensagem de erro com orientação..."
}
```

**Novas opções de validação (introduzidas nas Seções 6 e 7):**

| Campo | Descrição | Uso | Seção |
|-------|-----------|-----|-------|
| `forbidden_phrases` | Lista de frases que **invalidam** a resposta | Rejeitar generalizações como "resistiu ativamente" | 6 |
| `conditional_hospital` | Se True, exige hospital/UPA quando lesão mencionada | Perguntas sobre ferimentos | 6 |
| `required_keywords_any` | Exige pelo menos UMA das keywords (OR) | Justificativas com múltiplas opções | 6 |
| `allow_none_response` | Se True, aceita respostas negativas sem exigir min_length | Perguntas onde "Nenhum" é válido | 7 |
| `none_patterns` | Lista de padrões que indicam resposta negativa | Usado com `allow_none_response` | 7 |

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

> ⚠️ **ATENÇÃO:** O frontend possui MÚLTIPLOS locais que precisam ser atualizados. Use o checklist abaixo para garantir que nenhum seja esquecido. (Lição da Seção 4)

**Checklist Completo de Modificações no Frontend:**

#### 4.3.1 Constantes e Estruturas (INÍCIO DO ARQUIVO)

| # | O que modificar | Buscar por | Ação |
|---|-----------------|------------|------|
| 1 | Constante de perguntas | `SECTION4_QUESTIONS` | Criar `SECTIONN_QUESTIONS` logo após |
| 2 | ALL_SECTIONS | `const ALL_SECTIONS` | Adicionar entrada para seção N |

```javascript
const SECTIONN_QUESTIONS = {
    'N.1': 'Resumo da pergunta',
    'N.2': 'Resumo da pergunta',
    // ...
};

const ALL_SECTIONS = {
    // ... seções anteriores
    N: { emoji: '📋', name: '[Nome]', questions: SECTIONN_QUESTIONS }
};
```

#### 4.3.2 Funções Principais (CRIAR NOVAS)

| # | Função | Modelo | Cor Sugerida |
|---|--------|--------|--------------|
| 3 | `startSectionN()` | `startSection4()` | Escolher cor diferente das anteriores |
| 4 | `updateSidebarForSectionN()` | `updateSidebarForSection4()` | - |

#### 4.3.3 Função `handleBotResponse()` - 4 LOCAIS

| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 5 | Cálculo de progresso | `"Calcular progresso baseado na seção atual"` | Adicionar `else if (currentSection === N)` |
| 6 | Mensagem de conclusão | `"Seção 4 completa!"` | Adicionar mensagem para seção N |
| 7 | Criação de card de transição | `"currentSection === 4 && !boCompleted"` | Adicionar card para seção N (SE não for última) |
| 8 | Marcar boCompleted | `"boCompleted = true"` | MOVER para nova seção se ela for a última |

#### 4.3.4 Função `restoreFromDraft()` - 5 LOCAIS

| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 9 | Restaurar textos gerados | `"draft.generatedTexts.section4"` | Adicionar `section N` |
| 10 | Atualizar sidebar | `"updateSidebarForSection4"` | Adicionar `else if (currentSection === N)` |
| 11 | Contagem de respostas | `"section4Count"` | Criar `sectionNCount` |
| 12 | Cálculo de progresso | `"updateSidebarProgress(section4Count"` | Adicionar `else if (currentSection === N)` |
| 13 | Próxima pergunta | `"SECTION4_QUESTIONS[currentQuestionStep]"` | Adicionar `else if (currentSection === N)` |
| 14 | Botão de transição | `"btn-start-section4"` | Criar botão para seção N |
| 15 | Seção completa | `"currentSection === 4"` no bloco de "Seção completa" | Tratar caso seção N completa |

#### 4.3.5 Funções de Draft

| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 16 | saveDraft | `"section4"` em saveDraft | Adicionar `sectionN` |
| 17 | restoreDraft | `"section4"` em restoreDraft | Adicionar tratamento para `sectionN` |

#### 4.3.6 Função `updateHeaderSection()`

| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 18 | Header | `"Seção 4 - Entrada em Domicílio"` | Adicionar `else if (currentSection === N)` |

#### 4.3.7 Função `copyAllSections()`

| # | Local | Buscar por | Ação |
|---|-------|------------|------|
| 19 | Copiar texto | `"section4-text"` | Adicionar seletor para seção N |

**Total: 19 pontos de modificação no frontend**

### 4.4 Modificar `tests/e2e/automate_release.py`

**Adicionar:**
- `run_sectionN_flow()` - Fluxo de preenchimento da seção N
- `run_mobile_sectionN_flow()` - Fluxo mobile (se aplicável)
- Screenshots específicos da seção N
- Suporte a `--start-section N`

> ⚠️ **Lição da Seção 4:** O E2E pode falhar por timeout se o input estiver desabilitado. Sempre aguarde o input ficar habilitado antes de preencher:

```python
# Em fill_and_send() e em cada run_sectionN_flow()
await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
```

### 4.5 Atualizar `prepare_sections_via_api()` (se usando --start-section)

Se a nova seção suporta fast-start testing, atualizar o método que prepara seções anteriores via API:

```python
# Em prepare_sections_via_api()
if start_section >= N:
    # Preencher seção N-1 via API
    response = requests.post(f"{api_url}/start_section/{N-1}", json={"session_id": session_id})
    for step, answer in sectionN_minus_1_answers.items():
        requests.post(f"{api_url}/chat", json={
            "session_id": session_id,
            "message": answer,
            "current_section": N-1,
            "llm_provider": "groq"
        })
```

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

### Bug 6: Barra de progresso mostra "undefined/undefined" (NOVO - Seção 4)

**Sintoma:** Durante a nova seção, a barra de progresso exibe "undefined/undefined"

**Causa:** Faltam TRÊS pontos de atualização no frontend para cálculo de progresso

**Solução - 3 locais obrigatórios em `index.html`:**

```javascript
// LOCAL 1: Em handleBotResponse() - Cálculo de progresso durante chat
// Buscar: "Calcular progresso baseado na seção atual"
} else if (currentSection === N) {
    progress = data.current_step === 'complete' ? Y : parseInt(data.current_step.split('.')[1]);
    totalQuestions = Y;  // Y = número de perguntas da seção N
}

// LOCAL 2: Em restoreFromDraft() - Cálculo de progresso ao restaurar
// Buscar: "Atualizar progresso"
const sectionNCount = Object.keys(answersState).filter(s => s.startsWith('N.')).length;
if (currentSection === N) {
    updateSidebarProgress(sectionNCount, Y);
}

// LOCAL 3: Em restoreFromDraft() - Obter próxima pergunta
// Buscar: "Mostrar próxima pergunta"
} else if (currentSection === N) {
    nextQuestion = SECTIONN_QUESTIONS[currentQuestionStep];
}
```

### Bug 7: Botão "Iniciando..." persiste após BO completo (NOVO - Seção 4)

**Sintoma:** Ao completar a última seção implementada, o botão de transição da seção anterior permanece visível com texto "Iniciando..."

**Causa:** Cards de transição são criados sem verificar se o BO já está completo

**Solução:**
```javascript
// Em handleBotResponse() - Onde os cards de transição são criados
// Adicionar verificação `&& !boCompleted` em TODAS as condições

// ❌ ERRADO:
if (currentSection === 2) {
    // Criar card de transição para Seção 3
}

// ✅ CORRETO:
if (currentSection === 2 && !boCompleted) {
    // Criar card de transição para Seção 3
}
```

### Bug 8: Restauração de rascunho não suporta nova seção (NOVO - Seção 4)

**Sintoma:** Ao restaurar rascunho quando a seção N-1 está completa, não aparece o botão para iniciar a seção N

**Causa:** Função `restoreFromDraft()` não inclui lógica para criar botão da nova seção

**Solução:**
```javascript
// Em restoreFromDraft() - Na seção "Seção completa"
// Adicionar APÓS o bloco da seção N-1:

} else if (currentSection === N-1 && !document.getElementById('btn-start-sectionN')) {
    disableInput();

    // Criar botão para iniciar Seção N
    const sectionNButtonDiv = document.createElement('div');
    sectionNButtonDiv.id = 'sectionN-button-container';
    sectionNButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-[COR]-50 to-[COR]-100 border-2 border-[COR]-200 rounded-xl text-center';
    sectionNButtonDiv.innerHTML = `
        <h3 class="text-xl font-bold text-[COR]-900 mb-2">[EMOJI] Próxima Etapa: [Nome]</h3>
        <p class="text-gray-700 mb-4">[Descrição breve]</p>
        <button id="btn-start-sectionN" class="px-6 py-2 bg-[COR]-600 hover:bg-[COR]-700 text-white font-semibold rounded-lg transition-colors">
            ▶️ Iniciar Seção N
        </button>
    `;
    generatedSectionsContainer.parentElement.appendChild(sectionNButtonDiv);
    document.getElementById('btn-start-sectionN').addEventListener('click', startSectionN);

    showToast('✅ Rascunho restaurado! Seção N-1 completa.');

// E adicionar tratamento para quando a seção N está completa:
} else if (currentSection === N) {
    disableInput();
    showToast('✅ Rascunho restaurado! BO completo.');
    boCompleted = true;
    console.log('[BO] BO marcado como completo (restaurado)');
}
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

**Passo 1: Atualizar versão em todos os arquivos de interface**

- [ ] `docs/index.html` - Atualizar 6 referências:
  - Linha ~134: `<h1>...v0.X.Y</h1>` (header principal)
  - Linha ~313: `<p>...v0.X.Y | 💾...` (footer)
  - Linha ~435: Comentário em `saveDraft()` (versão changelog)
  - Linha ~489: `version: '0.X.Y'` (em saveDraft JSON)
  - Linha ~641: Comentário em `restoreFromDraft()`
  - Linha ~1017: `Gerado por: BO Inteligente v0.X.Y` (footer do BO)
  - Linha ~2183: Comentário em `handleBotResponse()` (verificação skip)

**Passo 2: Atualizar documentação de API**

- [ ] `docs/API.md` - 4 referências:
  - Linha ~3: `**Versão:** vX.Y.Z` (header)
  - Linha ~56: `"version": "0.X.Y"` (exemplo JSON /health)
  - Linhas ~541, 549, 586: `"app_version": "0.X.Y"` (exemplos /new_session)

**Passo 3: Atualizar documentação técnica**

- [ ] `docs/ARCHITECTURE.md` - 2 referências:
  - Linha ~3: `**Versão:** vX.Y.Z`
  - Linha ~379: `"version": "0.X.Y"` (exemplo localStorage)

**Passo 4: Atualizar roadmap e releases**

- [ ] `docs/ROADMAP.md` - 2 referências:
  - Linha ~3: `## Versão Atual: vX.Y.Z`
  - Adicionar versão ao topo da lista de status

- [ ] `CHANGELOG.md` - 1 adição:
  - Adicionar seção `#### vX.Y.Z (Mês Ano) - Seção N: [Nome]` no topo

- [ ] `README.md` - 3 referências:
  - Linha ~19: `### ✅ vX.Y.Z - Seção N: [Nome]`
  - Linha ~29: `- ✅ **N/8 seções implementadas**`
  - Linha ~258: `**Versão:** 0.X.Y`

- [ ] `docs/TESTING.md` - 2 referências:
  - Linha ~3: `**Versão:** vX.Y.Z`
  - Linha ~4: `**Última atualização:** 22/12/2025` (data atual)

**Passo 5: Criar commit com versionamento**

```bash
git add -A
git commit -m "feat: Implementar Seção N - [Nome] (vX.Y.Z)"
```

**Checklist automático de versionamento:**
```bash
# Buscar todas as ocorrências de versão anterior
grep -r "0.8.0" docs/ backend/ --include="*.html" --include="*.py" --include="*.md" | grep -v ".git"

# Após atualizar, verificar que não há mais referências antigas
grep -r "0.8.0" docs/ backend/ --include="*.html" --include="*.py" --include="*.md" | wc -l  # Deve retornar 0
```

---

## 8. Lições Aprendidas (Seção 4)

### 8.1 O que funcionou bem

1. **Estrutura modular do backend** - State machine e validator como arquivos separados facilitam copiar/adaptar
2. **Testes unitários primeiro** - Rodar `pytest tests/unit/test_sectionN.py` antes de integrar pega erros cedo
3. **Flag `--start-section`** - Economiza 70% do tempo de E2E testing ao pular seções anteriores
4. **Cores temáticas** - Cada seção com cor diferente ajuda UX (azul→roxo→laranja→...)

### 8.2 O que deu problema

| Problema | Causa Raiz | Tempo Perdido | Prevenção |
|----------|------------|---------------|-----------|
| Barra de progresso "undefined/undefined" | Faltou adicionar seção em 3 locais do frontend | ~30 min | Usar checklist de 19 pontos |
| Botão "Iniciando..." persistente | Criava card de transição sem verificar boCompleted | ~20 min | Sempre verificar `&& !boCompleted` |
| Restauração de rascunho incompleta | Faltou tratar nova seção em restoreFromDraft | ~15 min | Verificar TODOS os casos de seção |
| E2E timeout | Input desabilitado durante backend processing | ~45 min | Sempre aguardar `#user-input:not([disabled])` |

### 8.3 Recomendações para Próximas Seções

1. **Execute o checklist de 19 pontos** - Não confie na memória; marque cada item
2. **Teste manualmente ANTES do E2E** - Inicie backend/frontend localmente e complete a seção
3. **Verifique restauração de rascunho** - Complete parcialmente, recarregue a página, verifique
4. **Mate processos Python antigos** - `taskkill /F /IM python.exe` antes de rodar E2E
5. **Use --no-video para testes rápidos** - Vídeo é útil para debug, mas lento para iteração

### 8.4 Esquema de Cores Sugerido

| Seção | Cor | Tailwind Classes |
|-------|-----|------------------|
| 1 | Verde | `green-*` |
| 2 | Azul | `blue-*` |
| 3 | Roxo | `purple-*` |
| 4 | Laranja | `orange-*` |
| 5 | Rosa | `pink-*` ou `rose-*` |
| 6 | Ciano | `cyan-*` ou `teal-*` |
| 7 | Amarelo | `yellow-*` ou `amber-*` |
| 8 | Vermelho | `red-*` |

---

## 9. Lições Aprendidas (Seção 5)

### 9.1 Novo Bug Descoberto: IDs Inconsistentes de Containers

**Sintoma:** Botão de transição para próxima seção permanece visível na tela após a seção ser iniciada

**Causa Raiz:** O frontend usa dois IDs diferentes para containers de botões:
- `section{N}-transition-card` - Criado durante fluxo normal via `handleBotResponse()`
- `section{N}-button-container` - Criado durante restauração de rascunho via `restoreFromDraft()`

As funções `startSection{N}()` só removiam UM dos IDs, deixando o outro visível.

**Solução - Padrão obrigatório para TODAS as funções `startSection{N}()`:**

```javascript
async function startSectionN() {
    // INÍCIO: Limpar AMBOS os possíveis containers de botão
    const transitionCard = document.getElementById('sectionN-transition-card');
    if (transitionCard) transitionCard.remove();
    const buttonContainer = document.getElementById('sectionN-button-container');
    if (buttonContainer) buttonContainer.remove();

    // ... resto da função
}
```

**Arquivos afetados:** Todas as 4 funções startSection (2, 3, 4, 5) precisaram dessa correção.

### 9.2 Atualização do E2E: Criação de Botões para Seções 4 e 5

O script `automate_release.py` precisa criar botões de transição quando usando `--start-section`. O código foi expandido para suportar:

```javascript
// Em prepare_sections_via_api() -> inject_session_and_restore()
}} else if (upToSection === 3) {{
    // Criar botão "Iniciar Seção 4" (laranja)
    if (!document.getElementById('btn-start-section4')) {{
        const section4ButtonDiv = document.createElement('div');
        section4ButtonDiv.id = 'section4-button-container';
        section4ButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-orange-50 to-orange-100...';
        // ... código de criação do botão
    }}
}} else if (upToSection === 4) {{
    // Criar botão "Iniciar Seção 5" (pink)
    if (!document.getElementById('btn-start-section5')) {{
        const section5ButtonDiv = document.createElement('div');
        section5ButtonDiv.id = 'section5-button-container';
        section5ButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-pink-50 to-pink-100...';
        // ... código de criação do botão
    }}
}}
```

### 9.3 Checklist Expandido: 21 Pontos de Modificação no Frontend

A Seção 5 revelou que o checklist de 19 pontos estava incompleto. **Adicionados 2 novos pontos:**

| # | O que modificar | Ação |
|---|-----------------|------|
| 20 | `startSection{N}()` | Remover AMBOS os IDs de container (transition-card E button-container) |
| 21 | `automate_release.py` | Se suporta `--start-section N-1`, criar botão para seção N |

### 9.4 Validação de Fixtures em conftest.py

Ao adicionar fixture para nova seção, garantir que as respostas são suficientemente detalhadas para passar na validação:

```python
@pytest.fixture
def section5_answers() -> Dict:
    """Respostas válidas para Seção 5 (todas as 4 perguntas)"""
    return {
        "5.1": "SIM",
        "5.2": "Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, visualizamos um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro e entregando-os a motociclistas que paravam rapidamente",  # min 40 chars
        "5.3": "O Sargento João, de dentro da viatura estacionada a aproximadamente 20 metros do local, visualizou o suspeito retirando invólucros do buraco no muro e realizando as entregas por cerca de dois minutos antes de perceber a aproximação policial",  # DEVE incluir graduação
        "5.4": "Homem de camisa vermelha e bermuda jeans azul, porte atlético, aproximadamente 1,75m de altura. Ao perceber a aproximação da viatura, demonstrou nervosismo acentuado e tentou guardar parte do material no bolso. Posteriormente identificado como JOÃO DA SILVA SANTOS, vulgo 'Vermelho'."  # min 50 chars + nome + vulgo
    }
```

### 9.5 Resumo de Commits da Seção 5

| Commit | Descrição | Arquivos Modificados |
|--------|-----------|---------------------|
| a1dc3a7 | feat: Implementar Seção 5 - Fundada Suspeita (v0.9.0) | 16 arquivos backend/docs |
| 149b981 | fix: Add Section 5 transition and completion logic | index.html |
| 77d49cf | fix: Add complete Section 5 frontend support | index.html |
| 32e4e0d | fix: Update E2E restore script for Section 4/5 buttons | automate_release.py |
| 5da3cb6 | fix: Remove transition button containers when sections start | index.html |

### 9.6 O que funcionou bem na Seção 5

1. **Backend reutilizável** - Copiar state_machine_section4.py e validator_section4.py como base funcionou perfeitamente
2. **Testes unitários primeiro** - 12 testes passando antes de integrar ao main.py
3. **Cor temática (pink)** - Seguir esquema de cores evitou confusão visual
4. **Seção mais curta (4 perguntas)** - Menos pontos de falha, implementação mais rápida

### 9.7 O que deu problema na Seção 5

| Problema | Causa Raiz | Tempo Perdido | Prevenção |
|----------|------------|---------------|-----------|
| Frontend incompleto | Faltou adicionar SECTION5_QUESTIONS e funções | ~45 min | Seguir checklist de 21 pontos |
| E2E não criava botões S4/S5 | restore_script só tratava upToSection === 2 | ~30 min | Expandir script para todas seções |
| Botão permanecia visível | IDs inconsistentes (transition-card vs button-container) | ~20 min | Remover AMBOS os IDs em startSection |

### 9.8 Recomendações Atualizadas para Próximas Seções (6-8)

1. **Use o checklist de 21 pontos** - Não confie na memória
2. **Verifique `startSection{N}()` remove AMBOS os IDs de container** - Bug crítico descoberto na Seção 5
3. **Atualize `automate_release.py`** se suportar `--start-section` para a nova seção
4. **Teste restauração de rascunho** em TRÊS cenários:
   - Seção N-1 completa → deve mostrar botão para seção N
   - Seção N parcialmente preenchida → deve restaurar respostas
   - Seção N completa → deve marcar BO como completo (se última)
5. **Execute E2E com `--start-section N-1`** para validar transição

---

## 10. Lições Aprendidas (Seção 6)

### 10.1 Novas Funcionalidades de Validação

A Seção 6 (Reação e Uso da Força) introduziu **duas novas funcionalidades de validação** que podem ser reutilizadas em seções futuras:

#### 10.1.1 Validação de Frases Proibidas (`forbidden_phrases`)

**Problema:** Policiais usam expressões genéricas como "resistiu ativamente" ou "uso moderado da força" que são juridicamente problemáticas.

**Solução:** Nova regra de validação que **rejeita** respostas contendo frases proibidas.

```python
# Em validator_section6.py
VALIDATION_RULES_SECTION6 = {
    "6.2": {
        "min_length": 30,
        "forbidden_phrases": [
            "resistiu ativamente",
            "resistência ativa",
            "uso moderado da força",
            "necessário uso da força",
            "em atitude suspeita",
            "estava exaltado",
            "ficou agressivo",
            "resistiu",  # sem complemento
            "houve resistência"  # sem detalhar
        ],
        "error_message": "Descreva o que o autor FEZ (soco, empurrão, fuga, etc). NÃO use frases genéricas..."
    }
}
```

**Implementação do método:**
```python
@staticmethod
def _check_forbidden_phrases(answer: str, forbidden_phrases: list) -> Tuple[bool, str]:
    """
    Verifica se a resposta contém frases proibidas (generalizações).

    Returns:
        Tupla (has_forbidden, matched_phrase)
    """
    answer_lower = answer.lower()

    for phrase in forbidden_phrases:
        if phrase.lower() in answer_lower:
            return True, phrase

    return False, ""
```

**Uso na validação:**
```python
if step == "6.2" and "forbidden_phrases" in rules:
    has_forbidden, matched = self._check_forbidden_phrases(answer, rules["forbidden_phrases"])
    if has_forbidden:
        return False, f"NÃO use a expressão '{matched}'. {rules['error_message']}"
```

#### 10.1.2 Validação Condicional de Hospital (`conditional_hospital`)

**Problema:** Se o autor sofreu ferimentos durante a abordagem, é obrigatório informar atendimento hospitalar e número da ficha.

**Solução:** Validação condicional que detecta menção a ferimentos e exige hospital/UPA.

```python
# Em validator_section6.py
"6.5": {
    "min_length": 30,
    "conditional_hospital": True,  # Ativa validação condicional
    "error_message": "Informe se houve ou não ferimentos. Se SIM: descreva a lesão, onde foi atendido (hospital/UPA) e o número da ficha."
}
```

**Implementação:**
```python
@staticmethod
def _check_has_injury(answer: str) -> bool:
    """Verifica se a resposta menciona ferimentos/lesões."""
    injury_keywords = [
        "ferimento", "lesão", "sangramento", "escoriação",
        "hematoma", "fratura", "contusão", "ferido", "machucado"
    ]
    answer_lower = answer.lower()

    # Se começa com "Não houve", considera sem ferimentos
    if answer_lower.strip().startswith("não houve"):
        return False

    return any(keyword in answer_lower for keyword in injury_keywords)

@staticmethod
def _check_hospital_info(answer: str) -> bool:
    """Verifica se menciona hospital/UPA com número da ficha."""
    hospital_keywords = ["hospital", "upa", "pronto socorro", "ps"]
    ficha_keywords = ["ficha", "nº", "numero", "número"]

    answer_lower = answer.lower()
    has_hospital = any(kw in answer_lower for kw in hospital_keywords)
    has_ficha = any(kw in answer_lower for kw in ficha_keywords)

    return has_hospital and has_ficha
```

### 10.2 Bug Corrigido: Numeração de Steps em test_scenarios.json

**Sintoma:** Erros de validação apareciam em momentos errados durante o E2E.

**Causa Raiz:** Steps no arquivo `test_scenarios.json` estavam com numeração incorreta (6.0, 6.1...) ao invés de (6.1, 6.2...).

**Regra:** Steps SEMPRE começam em X.1, não X.0. Verificar com o arquivo `state_machine_sectionN.py`:

```python
# CORRETO - em state_machine_section6.py
SECTION6_STEPS = ["6.1", "6.2", "6.3", "6.4", "6.5", "complete"]

# CORRETO - em test_scenarios.json
"steps": [
    {"step": "6.1", "answer": "SIM", "expect": "pass"},
    {"step": "6.2", "answer": "...", "expect": "pass"},
    // ...
]
```

### 10.3 Bug Corrigido: E2E Mobile "Execution context was destroyed"

**Sintoma:** Erro durante testes E2E mobile: `playwright._impl._errors.Error: Page.evaluate: Execution context was destroyed`

**Causa Raiz:** Uso de `wait_for_load_state('networkidle')` causava navegação que destruía o contexto JavaScript.

**Solução em `automate_release.py`:**

```python
# ANTES (ERRADO):
await page.wait_for_load_state('networkidle', timeout=10000)
result = await page.evaluate(restore_script)

# DEPOIS (CORRETO):
try:
    await page.wait_for_load_state('domcontentloaded', timeout=10000)
    await page.wait_for_timeout(500)
except:
    pass

try:
    result = await page.evaluate(restore_script)
except Exception as e:
    print(f"    ⚠️  Erro na restauração: {str(e)}")
    # Retry com fallback
    try:
        await page.wait_for_timeout(1000)
        result = await page.evaluate(restore_script)
    except:
        print(f"    ⚠️  Restauração falhou - continuando sem restaurar")
```

**Padrão para fast-start de seções:**
```python
# Em cada seção (3, 4, 5, 6) no E2E mobile
try:
    await page.click('#btn-start-sectionN')
    await page.wait_for_timeout(1000)
except Exception as e:
    print(f"    ⚠️  Erro ao iniciar seção N: {str(e)}")
    # Tentar novamente
    await page.wait_for_timeout(500)
    await page.click('#btn-start-sectionN')
```

### 10.4 Resumo de Commits da Seção 6

| Commit | Descrição | Arquivos Modificados |
|--------|-----------|---------------------|
| TBD | feat: Implementar Seção 6 - Reação e Uso da Força (v0.10.0) | 16 arquivos backend/docs |
| TBD | fix: Corrigir numeração de steps em test_scenarios.json | test_scenarios.json |
| TBD | fix: Adicionar tratamento de erro para E2E mobile | automate_release.py |

### 10.5 O que funcionou bem na Seção 6

1. **Plano detalhado antes de implementar** - Checklist de 21 pontos no frontend evitou muitos bugs
2. **Novas validações reutilizáveis** - `forbidden_phrases` e `conditional_hospital` podem ser usadas em seções 7-8
3. **Testes unitários incluem frases proibidas** - Garantiu que validação funciona antes de integrar
4. **Cor temática (teal/cyan)** - Seguindo esquema de cores documentado

### 10.6 O que deu problema na Seção 6

| Problema | Causa Raiz | Tempo Perdido | Prevenção |
|----------|------------|---------------|-----------|
| Steps errados no test_scenarios.json | Usou 6.0 ao invés de 6.1 | ~20 min | Sempre verificar SECTION_STEPS no state_machine |
| E2E mobile crash | `networkidle` destruindo contexto | ~30 min | Usar `domcontentloaded` + try-catch |
| Validação 6.2 não rejeitava frases | Implementação inicial incorreta | ~15 min | Testar unitário com frases proibidas primeiro |

### 10.7 Recomendações Atualizadas para Seções 7-8

1. **Considere usar `forbidden_phrases`** se houver termos que devem ser evitados
2. **Use `conditional_hospital`** se perguntas envolvem ferimentos/lesões
3. **SEMPRE verifique numeração de steps** contra o arquivo `state_machine_sectionN.py`
4. **Para E2E mobile:** Use `domcontentloaded` ao invés de `networkidle`
5. **Envolva `page.evaluate()` em try-catch** especialmente em cenários de fast-start
6. **Teste frases proibidas unitariamente** antes de integrar ao backend

### 10.8 Padrão de Validação Negativa (Rejeitar ao invés de Exigir)

A Seção 6 introduziu o conceito de **validação negativa** - rejeitar respostas que contêm termos proibidos, ao invés de apenas exigir termos obrigatórios.

**Quando usar:**
- Termos vagos que são juridicamente problemáticos
- Generalizações que policiais tendem a usar por hábito
- Expressões que não agregam informação objetiva

**Template de implementação:**
```python
# No validator
if "forbidden_phrases" in rules:
    has_forbidden, matched = self._check_forbidden_phrases(answer, rules["forbidden_phrases"])
    if has_forbidden:
        return False, f"NÃO use a expressão '{matched}'. {rules['error_message']}"

# No test_scenarios.json - cenário de erro esperado
{
    "step": "N.X",
    "answer": "O autor resistiu ativamente",
    "expect": "fail",
    "test_forbidden": true,  # Marca como teste de frase proibida
    "screenshot": "XX-sectionN-forbidden-error"
}
```

---

## 11. Lições Aprendidas (Seção 7)

### 11.1 Nova Funcionalidade: Validação de Resposta Negativa (`allow_none_response`)

**Problema:** Em 7.3 ("Quais objetos ligados ao tráfico foram apreendidos?"), o policial pode responder "Nenhum objeto" ou "Não havia objetos", que não atende ao min_length de 30 caracteres.

**Solução:** Nova regra de validação que aceita respostas negativas sem exigir comprimento mínimo.

```python
# Em validator_section7.py
VALIDATION_RULES_SECTION7 = {
    "7.3": {
        "min_length": 30,
        "allow_none_response": True,
        "none_patterns": ["nenhum", "não havia", "não houve", "não foram"],
        "examples": [
            "Foram apreendidos R$ 450,00...",
            "Nenhum objeto ligado ao tráfico foi encontrado"
        ],
        "error_message": "Liste objetos ou informe 'Nenhum objeto'. Mín. 30 caracteres."
    }
}

# Implementação do método
@staticmethod
def _check_none_response(answer: str, none_patterns: list) -> bool:
    """Verifica se resposta indica ausência."""
    answer_lower = answer.lower()
    return any(pattern.lower() in answer_lower for pattern in none_patterns)
```

**Quando usar:**
- Perguntas onde "Nenhum" é uma resposta válida
- Perguntas sobre objetos opcionais (dinheiro, celulares, armas)
- Complementos que podem não existir

### 11.2 Bug Corrigido: logs.html não exibia Seções 3-7

**Sintoma:** Ao clicar em um BO específico no dashboard de logs, as respostas das Seções 3-7 não apareciam.

**Causa Raiz:** O arquivo `docs/logs.html` foi criado quando só existiam Seções 1-2 e nunca foi atualizado:
- `questionLabels` só tinha labels para 1.x e 2.x
- Processamento de eventos só tratava `section1_completed` e `section2_completed`
- Renderização só verificava `hasSection1` e `hasSection2`

**Solução completa (5 pontos de modificação):**

| # | Local | Mudança |
|---|-------|---------|
| 1 | `questionLabels` | Adicionar labels 3.0-7.4 |
| 2 | Processamento eventos | Usar regex `/^section[1-7]_completed$/` |
| 3 | Verificação seções | Adicionar `hasSection3` a `hasSection7` |
| 4 | Renderização | Adicionar blocos para Seções 3-7 com cores |
| 5 | `renderGeneratedText()` | Usar `sectionConfig` para cores por seção |

**Código-chave para eventos:**
```javascript
// ANTES (ERRADO):
if (event.event_type === 'section1_completed' || event.event_type === 'section2_completed')

// DEPOIS (CORRETO):
if (event.event_type.match(/^section[1-7]_completed$/)) {
    const sectionMatch = event.event_type.match(/section(\d)_completed/);
    if (sectionMatch) {
        const section = parseInt(sectionMatch[1]);
        // ...
    }
}
```

### 11.3 Padrão de Validação para Cadeia de Custódia

A Seção 7 introduziu validação de **cadeia de custódia** - conjunto de informações que garantem a integridade da prova:

| Elemento | Obrigatório em | Validação |
|----------|----------------|-----------|
| QUEM encontrou | 7.2, 7.4 | `required_keywords` = graduação militar |
| ONDE encontrou | 7.2 | min_length >= 50 |
| COMO acondicionou | 7.4 | min_length >= 40 |
| PARA ONDE levou | 7.4 | `required_keywords_any` = destinos |

**Template para seções futuras com custódia:**
```python
"N.X": {
    "min_length": 40,
    "required_keywords": ["soldado", "sargento", "cabo", "tenente", "capitão"],  # QUEM
    "required_keywords_any": ["ceflan", "delegacia", "dp", "central"],  # PARA ONDE
    "error_message": "Informe QUEM (graduação + nome) e PARA ONDE (destino)."
}
```

### 11.4 Checklist Atualizado: logs.html para Novas Seções

> ⚠️ **NOVO:** Ao implementar uma nova seção, **TAMBÉM atualizar `docs/logs.html`:**

| # | Local | Ação |
|---|-------|------|
| 1 | `questionLabels` | Adicionar labels N.1 a N.Y |
| 2 | Processamento eventos | Atualizar regex para incluir seção N |
| 3 | `hasSection{N}` | Adicionar verificação de existência |
| 4 | Renderização HTML | Adicionar bloco com cor temática |
| 5 | `sectionConfig` | Adicionar entrada para seção N |

### 11.5 O que funcionou bem na Seção 7

1. **Reutilização de padrões** - `allow_none_response` baseado em `conditional_hospital` da Seção 6
2. **Testes unitários incluem "Nenhum objeto"** - Garantiu que nova funcionalidade funciona
3. **Checklist de 21 pontos do frontend** - Evitou bugs já conhecidos
4. **Cor âmbar (amber)** - Diferencia visualmente das outras seções
5. **Prompt LLM com fundamento jurídico** - Lei 11.343/06 citada corretamente

### 11.6 O que deu problema na Seção 7

| Problema | Causa Raiz | Tempo Perdido | Prevenção |
|----------|------------|---------------|-----------|
| logs.html não mostrava Seções 3-7 | Arquivo nunca atualizado | ~20 min | Adicionar logs.html ao checklist |
| Validação 7.3 rejeitava "Nenhum" | Faltava `allow_none_response` | ~15 min | Identificar casos de resposta negativa |

### 11.7 Recomendações para Seção 8

1. **Adicionar logs.html ao checklist** - Incluir 5 pontos de modificação (ver 11.4)
2. **Verificar se há perguntas com "Nenhum" válido** - Usar `allow_none_response`
3. **Seção 8 DEVE marcar BO como completo** - Adicionar `boCompleted = true` ao final
4. **Criar botão de conclusão final** - Não terá "Iniciar Seção 9"
5. **Atualizar versão para v0.12.2** - Manter padrão de incremento

### 11.8 Resumo de Commits da Seção 7

| Commit | Descrição | Arquivos Modificados |
|--------|-----------|---------------------|
| dd0f6da | docs: Add section implementation guide for future sections (4-8) | SECTION_IMPLEMENTATION_GUIDE.md |
| 4dfc369 | fix: logs.html - Corrigir exibição das Seções 3-7 | docs/logs.html + 39 outros |

### 11.9 Checklist Completo Atualizado (22 Pontos)

O checklist de 21 pontos do frontend agora inclui **1 novo ponto** para logs.html:

| # | Local | Ação |
|---|-------|------|
| 1-21 | `docs/index.html` | (ver seção 4.3 - checklist original) |
| **22** | `docs/logs.html` | Atualizar 5 locais (ver seção 11.4) |

---

## 12. Seção 8: Condução e Pós-Ocorrência (v0.12.2) - Lições Aprendidas

### 12.1 Diferenças Críticas da Seção 8

A Seção 8 é fundamentalmente diferente de todas as anteriores:

| Aspecto | Seções 1-7 | Seção 8 |
|--------|----------|--------|
| Pergunta condicional | Sim (maioria tem SIM/NÃO) | **NÃO** (todas 6 perguntas obrigatórias) |
| `boCompleted` | `pass` (não marca) | **MARCA como True** (única que faz isso) |
| Botão de transição | "Iniciar Seção N+1" | **"Copiar BO Completo" + "Iniciar Novo BO"** |
| Cor temática | Várias (blue, amber, etc.) | **Indigo** |
| allow_none_response | 1-2 perguntas | **4 perguntas** (8.2, 8.3, 8.4, 8.5) |
| Fundamento jurídico | Lei 11.343/06 específica | **Lei 11.343/06 + Lei 13.869/19 + CPP 282-284** |

### 12.2 Arquivos Criados para Seção 8

✅ Todos os 4 arquivos backend criados com sucesso:
1. `backend/state_machine_section8.py` - 186 linhas (sem skip logic)
2. `backend/validator_section8.py` - 232 linhas (com `allow_none_response` em 4 perguntas)
3. `tests/unit/test_section8.py` - 370+ linhas (35 testes + fixtures)
4. `tests/integration/test_section8_flow.py` - 305+ linhas (4 testes de integração com 50+ assertions)

✅ Fixture adicionada a `tests/conftest.py`:
- `section8_answers()` - 6 respostas válidas com exemplo realista completo

### 12.3 Padrões Reutilizáveis Identificados

1. **`allow_none_response` Pattern** - Agora usado em 4 perguntas:
   - `8.2`: "Sem agravantes", "Não havia agravantes"
   - `8.3`: "Não declarou", "Permaneceu em silêncio"
   - `8.4`: "Sem registros", "Sem antecedentes"
   - `8.5`: "Sem vínculo", "Não identificado"

2. **`required_keywords_any` Pattern** - Para validar destino em 8.6:
   - Aceita qualquer um de: CEFLAN, Delegacia, DIPC, Central, Hospital, UPA

3. **Graduação Militar Pattern** - Replicado em 8.1 e 8.6 (como 7.2 e 7.4)
   - Keywords: sargento, soldado, cabo, tenente, capitão (mais abreviações)

### 12.4 Testes Passando - Confirmação

```bash
# Integration Tests - 4 testes principais
[PASS] Teste 1: State Machine Seção 8 - Fluxo Completo (9 assertions)
[PASS] Teste 2: Validação de Todas as Perguntas (12 assertions)
[PASS] Teste 3: Variações de Respostas Negativas (16 assertions)
[PASS] Teste 4: Requisitos Críticos da Seção 8 (4 assertions)

Total: 41 assertions passando sem erros
```

### 12.5 O que Funcionou Bem na Seção 8

1. **Backend completo antes do frontend** - Evitou dependências circulares
2. **Tests como documentação** - Cada teste demonstra um use case real
3. **Reutilização de `allow_none_response`** - Padrão provou ser genérico
4. **Validação de destino com `required_keywords_any`** - Mais flexível que AND
5. **Fixture de respostas em conftest** - Dados compartilhados entre testes

### 12.6 Próximas Etapas - Frontend (22 Pontos)

A Seção 8 é a primeira onde o **backend está 100% pronto antes do frontend**:

| Fase | Status | Responsável |
|------|--------|------------|
| Backend Core | ✅ COMPLETO | Haiku |
| Backend Testes | ✅ COMPLETO | Haiku |
| Versão Backend | ✅ v0.12.2 | Haiku |
| **Frontend** | ⏳ PENDENTE | **Sonnet** (22 pontos) |
| **Validador Backend** | ✅ COMPLETO | (Haiku criou) |
| **Main.py Integration** | ⏳ PENDENTE | **Sonnet** |
| **LLM Service** | ⏳ PENDENTE | **Sonnet** |
| **E2E Tests** | ⏳ PENDENTE | **Sonnet** |

**Observação:** O separação clara entre Haiku (backend puro) e Sonnet (integração) funcionou bem.

### 12.7 Recomendações para Futuras Seções

1. **Usar Haiku para backend estrutural** - State machine + validator sempre com Haiku
2. **Usar Sonnet para integração** - Conectar backend com main.py/LLM com Sonnet
3. **Fixtures em conftest** - Evitar duplicação de dados de teste
4. **Tests como especificação** - Escrever testes ANTES de criar o validator
5. **Modular color schemes** - Usar Tailwind color names consistentemente

### 12.8 Resumo de Versão v0.12.2

- **Data:** 23/12/2025
- **Status:** ✅ Backend Completo (frontend pendente)
- **Seções:** 8/8 implementadas no backend
- **Linhas de código:** 1000+ (backend puro)
- **Testes:** 40+ testes passando
- **Documentação:** CHANGELOG, README, API, TESTING, ARCHITECTURE atualizado

---

## Referências

- [CLAUDE_CODE_WORKFLOW.md](CLAUDE_CODE_WORKFLOW.md) - Estratégia Haiku/Sonnet
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura técnica
- [TESTING.md](TESTING.md) - Guia de testes
- [API.md](API.md) - Referência de endpoints
- [SECTION8_RELEASE_NOTES.md](SECTION8_RELEASE_NOTES.md) - Release notes v0.12.2

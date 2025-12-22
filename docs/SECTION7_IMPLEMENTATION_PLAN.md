# Plano de Implementação - Seção 7: Apreensões e Cadeia de Custódia

**Versão:** v0.11.0
**Data:** 22/12/2025
**Custo Pré-Implementação:** USD 36.11 (ref: pós-Seção 6)

---

## Resumo Executivo

Implementar a Seção 7 (Apreensões e Cadeia de Custódia) seguindo o padrão estabelecido pelas Seções 3-6, com atenção especial aos **21 pontos de modificação no frontend**.

**Características da Seção 7:**
- 4 perguntas (7.1 a 7.4)
- Fundamento jurídico: Lei 11.343/06 (Lei de Drogas) - Arts. 33, 35, 40 + CPP Arts. 240§2 e 244
- Validação especial: 7.3 aceita "Nenhum objeto" como resposta válida
- Alerta obrigatório ao final: "📷 ATENÇÃO: Fotografar itens e anexar no BO"
- Cor temática: **Amarelo/Amber** (`amber-*`)
- **IMPORTANTE:** Seção 7 NÃO é a última - Seção 8 ainda virá depois

---

## 1. Perguntas da Seção 7

Extraídas de `materiais-claudio/_regras_gerais_-_gpt_trafico.txt` (linhas 77-83) e `_pacotao_2.txt` (Seção E):

| Step | Pergunta | Tipo |
|------|----------|------|
| 7.1 | Houve apreensão de drogas? | SIM/NÃO (condicional - pula seção se NÃO) |
| 7.2 | Descreva as substâncias apreendidas (tipo, quantidade, embalagem, local, quem encontrou) | Descritivo + graduação obrigatória |
| 7.3 | Quais objetos ligados ao tráfico foram apreendidos? | Descritivo OU "Nenhum objeto" |
| 7.4 | Como foi o acondicionamento e guarda? (lacração, responsável, destino) | Descritivo + graduação + destino |

**Total: 4 perguntas**

---

## 2. Checklist de Arquivos

### 2.1 Arquivos a CRIAR (4 arquivos)

| # | Arquivo | Executor | Prioridade |
|---|---------|----------|------------|
| 1 | `backend/state_machine_section7.py` | **Haiku** | Alta |
| 2 | `backend/validator_section7.py` | **Sonnet** | Alta |
| 3 | `tests/unit/test_section7.py` | **Haiku** | Média |
| 4 | `tests/integration/test_section7_flow.py` | **Haiku** | Média |

### 2.2 Arquivos a MODIFICAR (10 arquivos)

| # | Arquivo | Tipo de Edição | Executor |
|---|---------|----------------|----------|
| 5 | `backend/main.py` | Imports + endpoints + lógica chat | **Sonnet** |
| 6 | `backend/llm_service.py` | Método generate_section7_text + prompt | **Sonnet** |
| 7 | `docs/index.html` | JS: 21 pontos de modificação | **Sonnet** |
| 8 | `tests/conftest.py` | Fixture section7_answers | **Haiku** |
| 9 | `tests/e2e/automate_release.py` | run_section7_flow() + --start-section 7 | **Sonnet** |
| 10 | `tests/e2e/test_scenarios.json` | Cenários da seção 7 | **Haiku** |
| 11 | `docs/TESTING.md` | Casos de teste manuais | **Haiku** |
| 12 | `docs/API.md` | Documentar /start_section/7 | **Haiku** |
| 13 | `CHANGELOG.md` | Release notes v0.11.0 | **Haiku** |
| 14 | `README.md` | Atualizar versão e status (7/8 seções) | **Haiku** |

---

## 3. Ordem de Execução Detalhada

### Fase 1: Backend Core

**Tarefa 1.1: Criar `backend/state_machine_section7.py`** [Haiku]
- Copiar estrutura de `state_machine_section6.py`
- Definir `SECTION7_QUESTIONS` com 4 perguntas
- Definir `SECTION7_STEPS = ["7.1", "7.2", "7.3", "7.4", "complete"]`
- Classe `BOStateMachineSection7` com lógica de skip em 7.1
- `get_skip_reason()` retorna "Não se aplica (não houve apreensão de drogas)"

**Tarefa 1.2: Criar `backend/validator_section7.py`** [Sonnet]
- Definir `VALIDATION_RULES_SECTION7` (ver seção 4.2)
- **NOVA funcionalidade:** `allow_none_response` para 7.3 (aceita "Nenhum objeto")
- Método `_check_none_response()` para validação de resposta negativa
- Validação de graduação em 7.2 e 7.4
- Validação de destino (CEFLAN, delegacia) em 7.4

### Fase 2: Testes Unitários [Haiku]

**Tarefa 2.1: Criar `tests/unit/test_section7.py`**
- `TestSection7StateMachine`: init, questions, steps, skip, continue, full_flow
- `TestSection7Validator`:
  - 7.1 yes/no
  - 7.2 exige graduação
  - 7.3 aceita "Nenhum objeto"
  - 7.4 exige graduação + destino

**Tarefa 2.2: Atualizar `tests/conftest.py`**
- Adicionar fixture `section7_answers()` com 4 respostas válidas

### Fase 3: Integração Backend [Sonnet]

**Tarefa 3.1: Modificar `backend/main.py`**
- Imports: `from state_machine_section7 import BOStateMachineSection7`
- Imports: `from validator_section7 import ResponseValidatorSection7`
- Session data: adicionar `"section7_text": None`
- Endpoint `/start_section/7`: criar instância BOStateMachineSection7
- Endpoint `/chat`: validação para steps 7.x + geração de texto
- Endpoint `/update_answer`: validação para steps 7.x
- Endpoint `/sync_session`: suporte a steps 7.x
- **IMPORTANTE:** Seção 6 NÃO marca mais `boCompleted` - mover para Seção 8

**Tarefa 3.2: Modificar `backend/llm_service.py`**
- Método `generate_section7_text(section_data, provider)`
- Método `_build_prompt_section7(section_data)` com fundamento jurídico
- Métodos `_generate_section7_with_gemini()` e `_generate_section7_with_groq()`

### Fase 4: Frontend [Sonnet] - 21 PONTOS

**Tarefa 4.1: Modificar `docs/index.html`**

| # | O que modificar | Ação |
|---|-----------------|------|
| 1 | Constante de perguntas | Criar `SECTION7_QUESTIONS` |
| 2 | ALL_SECTIONS | Adicionar entrada para seção 7 (emoji: 📦, cor: amber) |
| 3 | `startSection7()` | Criar função (modelo: startSection6) |
| 4 | `updateSidebarForSection7()` | Criar função |
| 5-8 | `handleBotResponse()` | 4 locais (progresso, conclusão, transição, NÃO marcar boCompleted) |
| 9-15 | `restoreFromDraft()` | 7 locais |
| 16-17 | `saveDraft/restoreDraft` | 2 locais |
| 18 | `updateHeaderSection()` | Adicionar seção 7 |
| 19 | `copyAllSections()` | Adicionar seletor section7 |
| 20 | `startSection7()` | Remover AMBOS os IDs de container |
| 21 | Botão de transição | Criar botão para Seção 8 |

**IMPORTANTE:**
- Seção 7 NÃO marca `boCompleted = true` (Seção 8 ainda virá)
- Criar botão de transição para Seção 8
- Exibir alerta de foto ao completar: "📷 ATENÇÃO: Fotografar itens e anexar no BO"

### Fase 5: Testes E2E

**Tarefa 5.1: Criar `tests/integration/test_section7_flow.py`** [Haiku]

**Tarefa 5.2: Atualizar `tests/e2e/automate_release.py`** [Sonnet]
- Método `run_section7_flow(page, slow_mode)`
- Screenshots: 37-section7-start, 38-section7-error, 39-section7-final
- Suporte a `--start-section 7`

**Tarefa 5.3: Atualizar `tests/e2e/test_scenarios.json`** [Haiku]

### Fase 6: Documentação [Haiku]

**Tarefa 6.1-6.5:** Atualizar TESTING.md, API.md, CHANGELOG.md, README.md, ROADMAP.md

---

## 4. Conteúdo Específico da Seção 7

### 4.1 Perguntas Completas

```python
SECTION7_QUESTIONS = {
    "7.1": "Houve apreensão de drogas?",
    "7.2": "Descreva as substâncias apreendidas: tipo, quantidade exata, embalagem, local onde foi encontrado e quem encontrou (graduação + nome)",
    "7.3": "Quais objetos ligados ao tráfico foram apreendidos? (dinheiro, celulares, balança, armas, cadernos)",
    "7.4": "Como foi o acondicionamento e guarda? (como lacrou, quem ficou responsável e destino do material)"
}
```

### 4.2 Regras de Validação

```python
VALIDATION_RULES_SECTION7 = {
    "7.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO: houve apreensão de drogas?"
    },
    "7.2": {
        "min_length": 50,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Soldado Breno encontrou 14 pedras de crack dentro da lata azul no banco de concreto",
            "A Soldado Pires localizou 23 pinos de cocaína dentro de um buraco no muro da casa 12"
        ],
        "error_message": "Descreva: tipo, quantidade, embalagem, local e QUEM encontrou (graduação + nome). Mínimo 50 caracteres."
    },
    "7.3": {
        "min_length": 30,
        "allow_none_response": True,
        "none_patterns": ["nenhum", "não havia", "não houve", "não foram"],
        "examples": [
            "Foram apreendidos R$ 450,00 em notas diversas, 2 celulares e 1 balança de precisão",
            "Nenhum objeto ligado ao tráfico foi encontrado"
        ],
        "error_message": "Liste objetos apreendidos (dinheiro, celulares, etc) ou informe 'Nenhum objeto'. Mínimo 30 caracteres."
    },
    "7.4": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "required_keywords_any": ["ceflan", "delegacia", "dp", "dipc", "central", "entrega"],
        "examples": [
            "O Soldado Faria lacrou no invólucro 01 e ficou responsável até a entrega na CEFLAN 2",
            "O Cabo Almeida acondicionou em saco plástico, fotografou e transportou até a Delegacia Civil"
        ],
        "error_message": "Informe: como lacrou, QUEM ficou responsável (graduação + nome) e DESTINO (CEFLAN, delegacia). Mínimo 40 caracteres."
    }
}
```

### 4.3 Prompt LLM (Fundamento Jurídico)

```
FUNDAMENTO JURÍDICO - APREENSÕES E CADEIA DE CUSTÓDIA:

Baseado na LEI 11.343/06 (Lei de Drogas) e CPP Arts. 240§2 e 244.

LEI 11.343/06:
- Art. 33: Tráfico de drogas
- Art. 35: Associação para o tráfico (2+ pessoas)
- Art. 40: Agravantes (armas, menores, escolas)

PRINCÍPIOS DA CADEIA DE CUSTÓDIA:
1. Identificar QUEM encontrou o material (graduação + nome)
2. Descrever ONDE encontrou (local preciso)
3. Informar COMO acondicionou (invólucro, saco)
4. Registrar PARA ONDE levou (CEFLAN, delegacia)

ESTRUTURA NARRATIVA (2-3 PARÁGRAFOS):

PARÁGRAFO 1 - SUBSTÂNCIAS:
- Tipo de droga (crack, cocaína, maconha)
- Quantidade exata (pedras, pinos, gramas)
- Embalagem (invólucros, lata, sacola)
- Local preciso (caixa azul em cima da geladeira)
- QUEM encontrou (graduação + nome)

PARÁGRAFO 2 - OBJETOS:
- Dinheiro (valores fracionados)
- Celulares, balança de precisão
- Armas, cadernos de contabilidade
- Embalagens vazias

PARÁGRAFO 3 - ACONDICIONAMENTO:
- Como foi lacrado (invólucro 01, 02)
- Quem ficou responsável
- Destino (CEFLAN, delegacia)
- Fotografias realizadas

ERROS A EVITAR:
❌ "Apreensão feita conforme protocolo" (genérico)
❌ "Várias drogas foram apreendidas" (sem quantificar)
❌ "Material entregue" (sem dizer QUEM entregou)
❌ "Drogas localizadas" (sem dizer ONDE e por QUEM)

REGRA DE OURO: Quantidade exata + Local preciso + Nome do policial
```

---

## 5. Distribuição Haiku vs Sonnet

| Executor | Tarefas | % do Trabalho |
|----------|---------|---------------|
| **Haiku** | 1.1, 2.1, 2.2, 5.1, 5.3, 6.1-6.5 | ~55% |
| **Sonnet** | 1.2, 3.1, 3.2, 4.1, 5.2 | ~45% |

**Estimativa de Custo:** ~$20 (baseado no custo da Seção 6)

---

## 6. Validação Final

### Checklist Pré-Deploy

**Backend:**
- [ ] `state_machine_section7.py` criado
- [ ] `validator_section7.py` criado com `allow_none_response`
- [ ] `main.py` com imports e endpoints
- [ ] `llm_service.py` com generate_section7_text
- [ ] Testes unitários passando

**Frontend (21 pontos):**
- [ ] SECTION7_QUESTIONS definida
- [ ] ALL_SECTIONS atualizado (emoji: 📦, cor: amber)
- [ ] startSection7() criada
- [ ] updateSidebarForSection7() criada
- [ ] handleBotResponse() - 4 locais (SEM boCompleted)
- [ ] restoreFromDraft() - 7 locais
- [ ] Botão de transição para Seção 8
- [ ] Alerta de foto exibido ao completar

**Testes:**
- [ ] `tests/unit/test_section7.py` passando
- [ ] `tests/integration/test_section7_flow.py` passando
- [ ] E2E gerando screenshots

### Comandos de Teste

```bash
# Testes unitários
pytest tests/unit/test_section7.py -v

# Testes de integração
pytest tests/integration/test_section7_flow.py -v

# E2E (início rápido na seção 7)
python tests/e2e/automate_release.py --version v0.11.0 --start-section 7 --no-video

# E2E completo
python tests/e2e/automate_release.py --version v0.11.0
```

---

## 7. Arquivos Críticos (Referência)

| Arquivo | Propósito |
|---------|-----------|
| `backend/state_machine_section6.py` | Modelo para state_machine_section7 |
| `backend/validator_section6.py` | Modelo para validator_section7 |
| `backend/main.py` | Integração backend (6 locais) |
| `backend/llm_service.py` | Geração de texto |
| `docs/index.html` | Frontend completo (21 pontos) |
| `materiais-claudio/_pacotao_2.txt` | Fonte das perguntas (Seção E) |

---

## 8. Notas de Implementação

1. **Lógica de Skip:** Pergunta 7.1 = "NÃO" pula para "complete"
2. **Validação 7.2:** Requer graduação militar (quem encontrou)
3. **Validação 7.3:** NOVA funcionalidade - `allow_none_response` aceita "Nenhum objeto"
4. **Validação 7.4:** Requer graduação + destino obrigatório
5. **Prompt LLM:** Estrutura de 2-3 parágrafos
6. **Frontend:** Seção 6 NÃO marca mais `boCompleted` - mover para Seção 8
7. **Frontend:** Seção 7 NÃO marca `boCompleted = true` (Seção 8 ainda virá)
8. **Frontend:** Criar botão de transição para Seção 8
9. **Frontend:** Exibir alerta "📷 ATENÇÃO: Fotografar itens e anexar no BO"
10. **Versão:** Incrementar para v0.11.0
11. **Cor:** Amber/Yellow (seguindo esquema de cores)

---

## 9. Exemplos de Respostas Válidas

### 7.1 - Houve apreensão de drogas?
```
SIM
```

### 7.2 - Substâncias apreendidas
```
O Soldado Breno encontrou 14 pedras de substância análoga ao crack dentro de uma lata azul sobre o banco de concreto próximo ao portão da casa 12. A Soldado Pires localizou 23 pinos de cocaína em um buraco no muro.
```

### 7.3 - Objetos ligados ao tráfico
```
Foram apreendidos R$ 450,00 em notas de R$ 10 e R$ 20, típicas de comercialização, 2 celulares Samsung, 1 balança de precisão e uma caderneta com anotações de contabilidade.
```
OU
```
Nenhum objeto ligado ao tráfico foi encontrado além das substâncias entorpecentes.
```

### 7.4 - Acondicionamento e guarda
```
O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02, fotografou todos os itens no local e ficou responsável pelo material até a entrega na CEFLAN 2.
```

---

## 10. Funcionalidade Nova: Validação de Resposta Negativa

A Seção 7 introduz uma nova funcionalidade de validação: `allow_none_response`.

### Implementação em `validator_section7.py`:

```python
@staticmethod
def _check_none_response(answer: str, none_patterns: list) -> bool:
    """
    Verifica se a resposta indica ausência de objetos/itens.

    Returns:
        True se a resposta indica "nenhum/não havia", False caso contrário
    """
    answer_lower = answer.lower()

    for pattern in none_patterns:
        if pattern in answer_lower:
            return True

    return False
```

### Uso na validação de 7.3:

```python
if step == "7.3" and rules.get("allow_none_response"):
    # Se resposta indica "nenhum objeto", aceitar sem exigir min_length
    if self._check_none_response(answer, rules.get("none_patterns", [])):
        return True, ""

    # Caso contrário, validar min_length normalmente
    if len(answer) < rules.get("min_length", 0):
        return False, rules["error_message"]
```

---

## 11. Decisões Já Definidas

- ✅ **4 perguntas** conforme materiais (7.1-7.4)
- ✅ **Seção 7 NÃO é a última** - Seção 8 ainda virá
- ✅ **Cor amber** para a seção 7
- ✅ **Implementação de `allow_none_response`** para validação 7.3
- ✅ **Alerta de foto** obrigatório ao completar

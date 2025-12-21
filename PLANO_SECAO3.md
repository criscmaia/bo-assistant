# Plano de Implementação: Seção 3 - Campana (Vigilância Velada)

## Status da Implementação Atual (Seções 1 e 2)

### Confirmado como Implementado:
- [x] Perguntas das seções 1 (6 perguntas) e 2 (8 perguntas)
- [x] Regras de validação com mensagens de erro específicas
- [x] Possibilidade de editar respostas anteriores
- [x] Botões de feedback (thumbs up/down) funcionando
- [x] Testes automatizados (unit, integration, e2e com screenshots/videos)
- [x] Restauração de rascunho adaptada para múltiplas seções
- [x] Documentação (API, TESTING, ARCHITECTURE)

### Não há pendências identificadas para Seções 1 e 2.

---

## Especificação da Seção 3: Campana

**Fonte:** `materiais-claudio/_regras_gerais_-_gpt_trafico.txt` (linhas 42-52)

### Perguntas (8 total: 1 condicional + 7 detalhadas)

| ID | Pergunta | Tipo |
|----|----------|------|
| 3.1 | A equipe realizou campana? | Condicional (SIM/NÃO) - Se NÃO, pula seção |
| 3.2 | Local exato da campana; ponto de observação; distância aproximada | Texto detalhado |
| 3.3 | Quem tinha visão direta e o que cada policial via | Texto c/ graduação |
| 3.4 | O que motivou a campana | Texto detalhado |
| 3.5 | Tempo da campana (contínua ou alternada) | Texto |
| 3.6 | O que foi visto: trocas, entrega/recebimento de objetos, etc. | Texto detalhado |
| 3.7 | Houve abordagem de usuários? O que tinham e o que relataram | Texto ou "NÃO" |
| 3.8 | Houve fuga ao notar a equipe? Como ocorreu | Texto ou "NÃO" |

---

## Arquivos a Criar/Modificar

### Backend (Criar)
1. **`backend/state_machine_section3.py`** - State machine para Seção 3
2. **`backend/validator_section3.py`** - Validador para Seção 3

### Backend (Modificar)
3. **`backend/main.py`** - Integrar Section 3 (imports, endpoint, chat logic)
4. **`backend/llm_service.py`** - Adicionar `generate_section3_text()`

### Frontend (Modificar)
5. **`docs/index.html`** - Adicionar suporte à Seção 3 (sidebar, botão iniciar, chat)

### Testes (Criar)
6. **`tests/unit/test_section3.py`** - Testes unitários
7. **`tests/integration/test_section3_flow.py`** - Testes de integração

### Testes (Modificar)
8. **`tests/conftest.py`** - Adicionar `section3_answers` fixture
9. **`tests/e2e/automate_release.py`** - Adicionar screenshots da Seção 3
10. **`tests/e2e/test_scenarios.json`** - Adicionar cenários Seção 3

### Documentação (Modificar)
11. **`docs/TESTING.md`** - Adicionar casos de teste Seção 3
12. **`docs/API.md`** - Documentar endpoints Seção 3

---

## Análise de Viabilidade: Claude Haiku vs Sonnet

### Características do Código a Implementar:

| Aspecto | Complexidade | Adequado para Haiku? |
|---------|--------------|----------------------|
| State machine | Baixa (cópia de Section2) | Sim |
| Validator | Baixa (padrão estabelecido) | Sim |
| main.py edits | Média (múltiplos pontos) | Parcial |
| Frontend JS | Alta (lógica complexa) | Não |
| Testes | Baixa (fixtures + cópia) | Sim |
| LLM prompts | Média (requer domínio) | Parcial |

### Recomendação:

**Usar Haiku para:**
- `state_machine_section3.py` (cópia adaptada de section2)
- `validator_section3.py` (cópia adaptada de section2)
- `tests/unit/test_section3.py`
- `tests/conftest.py` (adicionar fixture)
- Documentação simples

**Usar Sonnet para:**
- `backend/main.py` (integrações em múltiplos pontos)
- `docs/index.html` (JavaScript complexo, múltiplas funções)
- `backend/llm_service.py` (prompts específicos de domínio)
- `tests/e2e/automate_release.py` (lógica de automação)

### Economia Estimada:
- ~60% do código pode ser feito com Haiku
- Custo Haiku: ~$0.25/1M tokens vs Sonnet: ~$3/1M tokens
- Economia potencial: 70-80% nos arquivos simples

---

## Plano de Execução Detalhado

### Fase 1: Backend Core (Haiku)

#### 1.1 Criar `backend/state_machine_section3.py`

```python
# Estrutura esperada (copiar de section2 e adaptar):

SECTION3_QUESTIONS = {
    "3.1": "A equipe realizou campana antes da abordagem?",
    "3.2": "Onde foi feita a campana? (local, ponto de observação, distância)",
    "3.3": "Qual policial tinha visão direta e o que cada um via?",
    "3.4": "O que motivou a campana?",
    "3.5": "Quanto tempo durou a campana? (contínua ou alternada)",
    "3.6": "O que foi observado durante a campana?",
    "3.7": "Houve abordagem de usuários? O que tinham/relataram?",
    "3.8": "Houve fuga ao notar a equipe? Como ocorreu?"
}

SECTION3_STEPS = ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "complete"]

class BOStateMachineSection3:
    # Mesma estrutura de BOStateMachineSection2
    # Lógica condicional em 3.1 (se "NÃO", pula seção)
```

#### 1.2 Criar `backend/validator_section3.py`

```python
VALIDATION_RULES_SECTION3 = {
    "3.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N"],
        "error_message": "Responda com SIM ou NÃO."
    },
    "3.2": {
        "min_length": 30,
        "error_message": "Descreva o local da campana, ponto de observação e distância aproximada."
    },
    "3.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "sgt", "sd", "cb", "ten"],
        "error_message": "Informe qual policial (graduação + nome) tinha visão direta e o que via."
    },
    "3.4": {
        "min_length": 20,
        "error_message": "Descreva o que motivou a campana (denúncia, inteligência, histórico, etc.)."
    },
    "3.5": {
        "min_length": 10,
        "error_message": "Informe a duração e se foi contínua ou alternada."
    },
    "3.6": {
        "min_length": 40,
        "error_message": "Descreva atos CONCRETOS observados (trocas, entregas, esconderijos). Evite generalizações."
    },
    "3.7": {
        "min_length": 3,  # Aceita "NÃO"
        "error_message": "Houve abordagem de usuários? Se sim, descreva. Se não, escreva NÃO."
    },
    "3.8": {
        "min_length": 3,  # Aceita "NÃO"
        "error_message": "Houve fuga? Se sim, descreva como. Se não, escreva NÃO."
    }
}
```

### Fase 2: Backend Integration (Sonnet)

#### 2.1 Modificar `backend/main.py`

Pontos de modificação:
1. **Imports** (linha ~15): Adicionar `from state_machine_section3 import BOStateMachineSection3`
2. **Imports** (linha ~18): Adicionar `from validator_section3 import ResponseValidatorSection3`
3. **Session structure** (linha ~53): Adicionar `"section3_text": str`
4. **ChatResponse model** (linha ~66): Já suporta múltiplas seções
5. **start_section endpoint** (linha ~389): Alterar de `[2]` para `[2, 3]`
6. **Adicionar lógica** para `section_number == 3`
7. **chat endpoint**: Adicionar validação e geração para section 3
8. **sync_session**: Adicionar suporte a steps 3.x

#### 2.2 Modificar `backend/llm_service.py`

Adicionar método:
```python
def generate_section3_text(self, answers: Dict[str, str], provider: str = "gemini") -> str:
    """Gera texto narrativo da Seção 3 - Campana"""
    prompt = f"""
    Gere um texto narrativo em 3ª pessoa sobre a campana policial...

    Respostas:
    - Local: {answers.get('3.2', '')}
    - Policial com visão: {answers.get('3.3', '')}
    ...
    """
```

### Fase 3: Frontend (Sonnet)

#### 3.1 Modificar `docs/index.html`

1. **Adicionar constante SECTION3_QUESTIONS** (após linha ~307):
```javascript
const SECTION3_QUESTIONS = {
    '3.1': 'Realizou campana?',
    '3.2': 'Local da campana',
    '3.3': 'Policial com visão direta',
    '3.4': 'Motivação',
    '3.5': 'Duração',
    '3.6': 'O que foi observado',
    '3.7': 'Abordagem de usuários',
    '3.8': 'Houve fuga?'
};
```

2. **Adicionar em ALL_SECTIONS**:
```javascript
3: { emoji: '👁️', name: 'Campana', questions: SECTION3_QUESTIONS }
```

3. **Botão "Iniciar Seção 3"**: Exibir após Seção 2 completa
4. **Função startSection3()**: Similar a startSection2()
5. **updateSidebarForSection3()**: Atualizar sidebar
6. **Lógica de geração**: Container para texto da Seção 3
7. **saveDraft/restoreDraft**: Incluir answers 3.x

### Fase 4: Testes (Haiku + Sonnet)

#### 4.1 Criar `tests/unit/test_section3.py` (Haiku)
- Testar state machine initialization
- Testar skip logic (3.1 = "NÃO")
- Testar validações

#### 4.2 Modificar `tests/conftest.py` (Haiku)
```python
@pytest.fixture
def section3_answers() -> Dict:
    return {
        "3.1": "SIM",
        "3.2": "Esquina da Rua das Flores com Avenida Brasil, atrás do muro da casa 145, a aproximadamente 30 metros do bar do João",
        "3.3": "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral do estabelecimento.",
        "3.4": "Denúncia anônima recebida via COPOM informando comercialização de drogas no local",
        "3.5": "15 minutos de vigilância contínua",
        "3.6": "Foi observado um homem de camiseta vermelha retirando pequenos invólucros de uma mochila preta e entregando a dois indivíduos que chegaram de motocicleta. Após receberem os invólucros, os indivíduos entregaram dinheiro ao homem.",
        "3.7": "Sim, foi abordado um usuário que estava saindo do local. Ele portava 2 porções de substância análoga à cocaína e relatou ter comprado do 'cara de vermelho' por R$ 50,00.",
        "3.8": "Sim, ao perceber a movimentação policial, o homem de vermelho correu para o beco ao lado do bar, tentando fugir em direção à Rua Sete."
    }
```

#### 4.3 Criar `tests/integration/test_section3_flow.py` (Sonnet)
- Fluxo completo Seção 1 + 2 + 3
- Teste de skip (campana = NÃO)

#### 4.4 Modificar `tests/e2e/automate_release.py` (Sonnet)
- Adicionar `run_section3_flow()`
- Novos screenshots: 17-20+

### Fase 5: Documentação (Haiku)

#### 5.1 Atualizar `docs/TESTING.md`
- Adicionar casos de teste manuais Seção 3
- Adicionar respostas validadas

#### 5.2 Atualizar `docs/API.md`
- Documentar `/start_section/3`
- Exemplos de request/response

---

## Ordem de Execução Sugerida

| # | Tarefa | Modelo | Dependências |
|---|--------|--------|--------------|
| 1 | state_machine_section3.py | Haiku | Nenhuma |
| 2 | validator_section3.py | Haiku | Nenhuma |
| 3 | test_section3.py (unit) | Haiku | 1, 2 |
| 4 | conftest.py (fixture) | Haiku | Nenhuma |
| 5 | main.py (integração) | Sonnet | 1, 2 |
| 6 | llm_service.py | Sonnet | Nenhuma |
| 7 | index.html | Sonnet | 5 |
| 8 | test_section3_flow.py | Sonnet | 5, 7 |
| 9 | automate_release.py | Sonnet | 7 |
| 10 | Documentação | Haiku | Todos |

---

## Checklist Final

- [ ] Backend: state_machine_section3.py
- [ ] Backend: validator_section3.py
- [ ] Backend: main.py integração
- [ ] Backend: llm_service.py prompt
- [ ] Frontend: index.html (sidebar, botão, chat, draft)
- [ ] Testes: unit tests
- [ ] Testes: integration tests
- [ ] Testes: conftest fixture
- [ ] Testes: e2e screenshots/video
- [ ] Docs: TESTING.md
- [ ] Docs: API.md
- [ ] Versão: Atualizar APP_VERSION para 0.7.0

---

# INSTRUÇÕES DETALHADAS PARA CLAUDE HAIKU

## Tarefa 1: Criar `backend/state_machine_section3.py`

**Modelo:** HAIKU
**Arquivo de referência:** `backend/state_machine_section2.py`
**Ação:** Copiar e adaptar

### Instruções passo a passo:

1. Crie o arquivo `backend/state_machine_section3.py`
2. Copie a estrutura EXATA de `backend/state_machine_section2.py`
3. Faça APENAS estas substituições:

| De | Para |
|----|------|
| `SECTION2_QUESTIONS` | `SECTION3_QUESTIONS` |
| `SECTION2_STEPS` | `SECTION3_STEPS` |
| `BOStateMachineSection2` | `BOStateMachineSection3` |
| `"2.1"` a `"2.8"` | `"3.1"` a `"3.8"` |
| `Seção 2: Abordagem a Veículo` | `Seção 3: Campana (Vigilância Velada)` |

4. Substitua o dicionário de perguntas por:

```python
SECTION3_QUESTIONS = {
    "3.1": "A equipe realizou campana antes da abordagem?",
    "3.2": "Onde foi feita a campana? (local, ponto de observação, distância aproximada)",
    "3.3": "Qual policial tinha visão direta e o que cada um via?",
    "3.4": "O que motivou a campana?",
    "3.5": "Quanto tempo durou a campana? (contínua ou alternada)",
    "3.6": "O que foi observado durante a campana? (descreva atos CONCRETOS)",
    "3.7": "Houve abordagem de usuários durante a campana?",
    "3.8": "Houve fuga ao notar a equipe? Como ocorreu?"
}

SECTION3_STEPS = ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "complete"]
```

5. Na função `get_skip_reason()`, altere a mensagem:
   - De: `"Não se aplica (não havia veículo envolvido na ocorrência)"`
   - Para: `"Não se aplica (não houve campana antes da abordagem)"`

6. Mantenha TODA a lógica de skip idêntica (quando 3.1 = "NÃO")

---

## Tarefa 2: Criar `backend/validator_section3.py`

**Modelo:** HAIKU
**Arquivo de referência:** `backend/validator_section2.py`
**Ação:** Copiar e adaptar

### Instruções passo a passo:

1. Crie o arquivo `backend/validator_section3.py`
2. Copie a estrutura EXATA de `backend/validator_section2.py`
3. Substitua o dicionário de regras por:

```python
VALIDATION_RULES_SECTION3 = {
    "3.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO. A equipe realizou campana antes da abordagem?"
    },
    "3.2": {
        "min_length": 30,
        "examples": [
            "Esquina da Rua das Flores com Av. Brasil, atrás do muro da casa 145, a 30 metros do bar",
            "Dentro da viatura estacionada no nº 233 da Rua Sete, a um quarteirão do ponto",
            "Beco da Rua Principal, atrás de uma caçamba de lixo, a 20 metros do alvo"
        ],
        "error_message": "Descreva o local exato da campana, ponto de observação e distância aproximada até o suspeito."
    },
    "3.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral.",
            "O Soldado Faria conseguia ver a entrada do beco de sua posição atrás do muro."
        ],
        "error_message": "Informe qual policial (graduação + nome) tinha visão direta e o que cada um conseguia ver."
    },
    "3.4": {
        "min_length": 20,
        "examples": [
            "Denúncia anônima específica recebida via COPOM",
            "Informações da inteligência policial sobre o ponto",
            "Histórico de ocorrências no local e usuários abordados antes indicando o ponto"
        ],
        "error_message": "Descreva o que motivou a campana (denúncia, inteligência, histórico, usuários, moradores)."
    },
    "3.5": {
        "min_length": 10,
        "examples": [
            "10 minutos de vigilância contínua",
            "20 minutos alternados entre observação e deslocamento",
            "Aproximadamente 15 minutos de campana contínua"
        ],
        "error_message": "Informe a duração da campana e se foi contínua ou alternada."
    },
    "3.6": {
        "min_length": 40,
        "examples": [
            "O homem tirou pequenos invólucros da mochila preta e entregou para dois rapazes que chegaram de moto",
            "A mulher recebia dinheiro e retirava algo do bolso esquerdo, entregando aos compradores",
            "O suspeito pegava porções de um pote azul escondido atrás do poste e entregava aos usuários"
        ],
        "error_message": "Descreva atos CONCRETOS observados (trocas, entregas, esconderijos). NÃO use generalizações como 'atitude suspeita'."
    },
    "3.7": {
        "min_length": 3,
        "examples": [
            "NÃO",
            "Sim, foram abordados 2 usuários que saíam do local. Portavam 3 porções de cocaína e relataram ter comprado do 'cara de vermelho' por R$ 50",
            "Sim, 1 usuário foi abordado pelo Cabo Silva. Tinha 1 porção de maconha e disse ter comprado no bar"
        ],
        "error_message": "Houve abordagem de usuários? Se sim, informe quantos, o que tinham, o que relataram. Se não, escreva NÃO."
    },
    "3.8": {
        "min_length": 3,
        "examples": [
            "NÃO",
            "Sim, ao perceber a movimentação policial, correu para o beco ao lado da casa 40",
            "Sim, tentou fugir pulando o muro dos fundos do bar, sendo alcançado pelo Soldado Faria"
        ],
        "error_message": "Houve fuga ao notar a equipe? Se sim, descreva como. Se não, escreva NÃO."
    }
}
```

4. Renomeie a classe:
   - De: `ResponseValidatorSection2`
   - Para: `ResponseValidatorSection3`

5. Atualize todas as referências internas de `VALIDATION_RULES_SECTION2` para `VALIDATION_RULES_SECTION3`

6. REMOVA a função `_validate_vehicle_plate()` - não é necessária para Seção 3

7. Mantenha as funções:
   - `validate()`
   - `_validate_yes_no()`
   - `_check_required_keywords()` (para graduação em 3.3)
   - `get_validation_examples()`
   - `get_error_message()`

---

## Tarefa 3: Atualizar `tests/conftest.py`

**Modelo:** HAIKU
**Ação:** Adicionar fixture

### Instruções:

Adicione APÓS a fixture `section2_answers` (linha ~45):

```python
@pytest.fixture
def section3_answers() -> Dict:
    """Respostas válidas para Seção 3 (todas as 8 perguntas)"""
    return {
        "3.1": "SIM",
        "3.2": "Esquina da Rua das Flores com Avenida Brasil, atrás do muro da casa 145, a aproximadamente 30 metros do bar do João",
        "3.3": "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral do estabelecimento pela janela da viatura.",
        "3.4": "Denúncia anônima recebida via COPOM informando comercialização de drogas no local há pelo menos 3 meses",
        "3.5": "15 minutos de vigilância contínua atrás do muro da casa 145",
        "3.6": "Foi observado um homem de camiseta vermelha retirando pequenos invólucros de uma mochila preta e entregando a dois indivíduos que chegaram de motocicleta. Após receberem os invólucros, os indivíduos entregaram dinheiro ao homem de vermelho.",
        "3.7": "Sim, foi abordado um usuário que estava saindo do local. Ele portava 2 porções de substância análoga à cocaína e relatou ter comprado do 'cara de vermelho' por R$ 50,00.",
        "3.8": "Sim, ao perceber a movimentação policial, o homem de vermelho correu para o beco ao lado do bar, tentando fugir em direção à Rua Sete."
    }
```

---

## Tarefa 4: Criar `tests/unit/test_section3.py`

**Modelo:** HAIKU
**Arquivo de referência:** `tests/unit/test_backend_changes.py`
**Ação:** Criar novo arquivo

### Instruções:

Crie o arquivo com este conteúdo:

```python
# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 3: Campana (Vigilância Velada)
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section3 import BOStateMachineSection3, SECTION3_QUESTIONS, SECTION3_STEPS
from validator_section3 import ResponseValidatorSection3


class TestSection3StateMachine:
    """Testes para BOStateMachineSection3"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection3()
        assert sm.current_step == "3.1"
        assert sm.answers == {}
        assert sm.section_skipped == False

    def test_questions_defined(self):
        """Verifica que todas as 8 perguntas estão definidas"""
        assert len(SECTION3_QUESTIONS) == 8
        assert "3.1" in SECTION3_QUESTIONS
        assert "3.8" in SECTION3_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION3_STEPS == ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "complete"]

    def test_skip_section_on_no(self):
        """Testa que responder NÃO em 3.1 pula a seção"""
        sm = BOStateMachineSection3()
        sm.store_answer("NÃO")
        assert sm.section_skipped == True
        assert sm.current_step == "complete"
        assert sm.is_section_complete() == True

    def test_continue_on_yes(self):
        """Testa que responder SIM em 3.1 continua normalmente"""
        sm = BOStateMachineSection3()
        sm.store_answer("SIM")
        sm.next_step()
        assert sm.section_skipped == False
        assert sm.current_step == "3.2"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachineSection3()

        # 3.1 - SIM
        sm.store_answer("SIM")
        sm.next_step()

        # 3.2 a 3.8
        for step in ["3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 8


class TestSection3Validator:
    """Testes para ResponseValidatorSection3"""

    def test_validate_3_1_yes(self):
        """Testa validação de SIM para 3.1"""
        is_valid, error = ResponseValidatorSection3.validate("3.1", "SIM")
        assert is_valid == True
        assert error == ""

    def test_validate_3_1_no(self):
        """Testa validação de NÃO para 3.1"""
        is_valid, error = ResponseValidatorSection3.validate("3.1", "NÃO")
        assert is_valid == True

    def test_validate_3_1_invalid(self):
        """Testa resposta inválida para 3.1"""
        is_valid, error = ResponseValidatorSection3.validate("3.1", "TALVEZ")
        assert is_valid == False

    def test_validate_3_3_requires_graduation(self):
        """Testa que 3.3 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection3.validate("3.3", "João viu a porta do bar claramente")
        assert is_valid == False

        # Com graduação - deve passar
        is_valid, error = ResponseValidatorSection3.validate("3.3", "O Sargento João viu a porta do bar claramente")
        assert is_valid == True

    def test_validate_3_6_min_length(self):
        """Testa comprimento mínimo para 3.6 (atos concretos)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection3.validate("3.6", "Viu tráfico")
        assert is_valid == False

        # Detalhado - deve passar
        is_valid, error = ResponseValidatorSection3.validate("3.6", "O homem tirou pequenos invólucros da mochila preta e entregou para dois rapazes de moto")
        assert is_valid == True

    def test_validate_3_7_accepts_no(self):
        """Testa que 3.7 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidatorSection3.validate("3.7", "NÃO")
        assert is_valid == True

    def test_validate_3_8_accepts_no(self):
        """Testa que 3.8 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidatorSection3.validate("3.8", "NÃO")
        assert is_valid == True


if __name__ == "__main__":
    print("Executando testes da Seção 3...")

    # State Machine
    t = TestSection3StateMachine()
    t.test_initialization()
    print("✓ test_initialization")
    t.test_questions_defined()
    print("✓ test_questions_defined")
    t.test_steps_defined()
    print("✓ test_steps_defined")
    t.test_skip_section_on_no()
    print("✓ test_skip_section_on_no")
    t.test_continue_on_yes()
    print("✓ test_continue_on_yes")
    t.test_full_flow()
    print("✓ test_full_flow")

    # Validator
    v = TestSection3Validator()
    v.test_validate_3_1_yes()
    print("✓ test_validate_3_1_yes")
    v.test_validate_3_1_no()
    print("✓ test_validate_3_1_no")
    v.test_validate_3_1_invalid()
    print("✓ test_validate_3_1_invalid")
    v.test_validate_3_3_requires_graduation()
    print("✓ test_validate_3_3_requires_graduation")
    v.test_validate_3_6_min_length()
    print("✓ test_validate_3_6_min_length")
    v.test_validate_3_7_accepts_no()
    print("✓ test_validate_3_7_accepts_no")
    v.test_validate_3_8_accepts_no()
    print("✓ test_validate_3_8_accepts_no")

    print("\n✅ Todos os testes passaram!")
```

---

# INSTRUÇÕES DETALHADAS PARA CLAUDE SONNET

## Tarefa 5: Modificar `backend/main.py`

**Modelo:** SONNET
**Ação:** Múltiplas edições

### Pontos de modificação:

1. **Imports (linha ~15-18):** Adicionar imports da Seção 3
2. **Session structure (linha ~53):** Adicionar `section3_text`
3. **start_section endpoint (linha ~389):** Expandir para suportar seção 3
4. **chat endpoint:** Adicionar lógica para section 3
5. **sync_session:** Suportar steps 3.x

### Detalhes em cada ponto - ver código existente e seguir padrão.

---

## Tarefa 6: Modificar `backend/llm_service.py`

**Modelo:** SONNET
**Ação:** Adicionar 3 métodos

### Métodos a adicionar (seguir padrão da Seção 2):

1. `generate_section3_text(section_data, provider)` - Método público principal
2. `_generate_section3_with_gemini(section_data)` - Implementação Gemini
3. `_generate_section3_with_groq(section_data)` - Implementação Groq

### Prompt sugerido para LLM:

```python
def _build_section3_prompt(self, section_data: Dict[str, str]) -> str:
    """Constrói prompt para geração de texto da Seção 3 - Campana"""

    prompt = """Gere um texto narrativo em 3ª pessoa sobre a campana policial realizada pela equipe.

REGRAS OBRIGATÓRIAS:
- Narração em 3ª pessoa, voz ativa, ordem direta
- Frases curtas e objetivas, estilo jornalístico
- Dois espaços entre as frases
- PROIBIDO: juridiquês, rebuscamento, gerúndio
- PROIBIDO: termos genéricos como "em atitude suspeita", "resistiu ativamente"
- Conectar as observações à fundada suspeita conforme decisões recentes do STF (2025)
- Descrever ATOS CONCRETOS observados, não impressões subjetivas

INFORMAÇÕES COLETADAS:

1. LOCAL DA CAMPANA:
{local}

2. POLICIAL COM VISÃO DIRETA:
{policial}

3. MOTIVAÇÃO:
{motivacao}

4. DURAÇÃO:
{duracao}

5. O QUE FOI OBSERVADO (atos concretos):
{observacoes}

6. ABORDAGEM DE USUÁRIOS:
{usuarios}

7. TENTATIVA DE FUGA:
{fuga}

Gere um texto fluido de 2-3 parágrafos narrando a campana e conectando as observações concretas à fundada suspeita que justificou a abordagem posterior.
""".format(
        local=section_data.get("3.2", "Não informado"),
        policial=section_data.get("3.3", "Não informado"),
        motivacao=section_data.get("3.4", "Não informado"),
        duracao=section_data.get("3.5", "Não informado"),
        observacoes=section_data.get("3.6", "Não informado"),
        usuarios=section_data.get("3.7", "Não informado"),
        fuga=section_data.get("3.8", "Não informado")
    )
    return prompt
```

### Localização no arquivo:
Adicionar após `_generate_section2_with_groq()` (aproximadamente linha 450+)

---

## Tarefa 7: Modificar `docs/index.html`

**Modelo:** SONNET
**Ação:** Múltiplas edições JavaScript

### Principais pontos:

1. Adicionar `SECTION3_QUESTIONS` constante
2. Atualizar `ALL_SECTIONS` com seção 3
3. Criar função `startSection3()`
4. Criar função `updateSidebarForSection3()`
5. Adicionar container de texto gerado para seção 3
6. Botão "Iniciar Seção 3" após seção 2 completa
7. Atualizar `saveDraft()` e `restoreFromDraft()` para steps 3.x

---

## Tarefa 8-10: Testes e Documentação

**Modelo:** SONNET para testes e2e, HAIKU para docs

Seguir padrões existentes.

# 🚨 ETAPA 1: Adicionar Pergunta 1.7 (Art. 40 - Agravantes de Proximidade)

## Contexto

A Lei 11.343/06 (Lei de Drogas), Art. 40, prevê **aumento de pena** quando o tráfico ocorre:
- Nas imediações de escolas
- Nas imediações de hospitais
- Nas imediações de estabelecimentos prisionais
- Em transportes públicos
- Em locais de concentração de menores

**Esta informação é CRÍTICA para a tipificação correta do crime.**

---

## 📋 O QUE PRECISA SER ALTERADO

### Arquivo 1: `docs/index.html`

**Localização:** Linha ~387-394 (constante `SECTION1_QUESTIONS`)

**ANTES:**
```javascript
const SECTION1_QUESTIONS = {
    '1.1': 'Dia, data e hora do acionamento.',
    '1.2': 'Composição da guarnição e prefixo.',
    '1.3': 'Natureza do empenho.',
    '1.4': 'O que constava na ordem de serviço, informações do COPOM, DDU.',
    '1.5': 'Local exato da ocorrência (logradouro, número, bairro).',
    '1.6': 'O local é ponto de tráfico? Quais evidências anteriores? Há facção?'
};
```

**DEPOIS:**
```javascript
const SECTION1_QUESTIONS = {
    '1.1': 'Dia, data e hora do acionamento.',
    '1.2': 'Composição da guarnição e prefixo.',
    '1.3': 'Natureza do empenho.',
    '1.4': 'O que constava na ordem de serviço, informações do COPOM, DDU.',
    '1.5': 'Local exato da ocorrência (logradouro, número, bairro).',
    '1.6': 'O local é ponto de tráfico? Quais evidências anteriores? Há facção?',
    '1.7': 'O local é próximo a escola, hospital ou transporte público? Qual estabelecimento e a que distância aproximada?'
};
```

**ATENÇÃO:** Verificar se há outras referências a "6 perguntas" ou "1.6" como última pergunta no arquivo e atualizar para "7 perguntas" e "1.7".

---

### Arquivo 2: `backend/state_machine.py`

**Localização:** Linha ~9-17 (dicionário `QUESTIONS`) e linha ~20 (lista `STEPS`)

**ANTES:**
```python
QUESTIONS = {
    "1.1": "Dia, data e hora do acionamento.",
    "1.2": "Composição da guarnição e prefixo.",
    "1.3": "Natureza do empenho.",
    "1.4": "O que constava na ordem de serviço, informações do COPOM, DDU.",
    "1.5": "Local exato da ocorrência (logradouro, número, bairro).",
    "1.6": "O local é ponto de tráfico? Quais evidências anteriores? Há facção?"
}

STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "complete"]
```

**DEPOIS:**
```python
QUESTIONS = {
    "1.1": "Dia, data e hora do acionamento.",
    "1.2": "Composição da guarnição e prefixo.",
    "1.3": "Natureza do empenho.",
    "1.4": "O que constava na ordem de serviço, informações do COPOM, DDU.",
    "1.5": "Local exato da ocorrência (logradouro, número, bairro).",
    "1.6": "O local é ponto de tráfico? Quais evidências anteriores? Há facção?",
    "1.7": "O local é próximo a escola, hospital ou transporte público? Qual estabelecimento e a que distância aproximada?"
}

STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "complete"]
```

---

### Arquivo 3: `backend/validator.py`

**Localização:** Dentro do dicionário `VALIDATION_RULES` (após a regra "1.6")

**ADICIONAR** nova regra de validação:

```python
"1.7": {
    "min_length": 3,
    "allow_negative": True,  # Aceita "NÃO" como resposta válida
    "examples": [
        "Sim, a 50 metros da Escola Estadual João XXIII",
        "Próximo ao Hospital Municipal, aproximadamente 100 metros",
        "A 200 metros do ponto de ônibus da linha 4501",
        "NÃO"
    ],
    "error_message": "Informe se há escola, hospital ou transporte público próximo. Se sim, qual e a distância aproximada. Se não, responda 'NÃO'."
}
```

**TAMBÉM** atualizar a lista de steps que aceitam "NÃO":

**ANTES (linha ~35 aproximadamente):**
```python
if answer.upper() == "NÃO":
    if step in ["1.6"]:  # Histórico pode ser NÃO
        return True, None
```

**DEPOIS:**
```python
if answer.upper() == "NÃO":
    if step in ["1.6", "1.7"]:  # Histórico e proximidade podem ser NÃO
        return True, None
```

---

### Arquivo 4: `backend/llm_service.py`

**Localização:** Função `_build_prompt()`, dicionário `questions_map` (linha ~50 aproximadamente)

**ANTES:**
```python
questions_map = {
    "1.1": "Dia, data e hora do acionamento",
    "1.2": "Composição da guarnição e prefixo",
    "1.3": "Natureza do empenho",
    "1.4": "Ordem de serviço / COPOM / DDU",
    "1.5": "Local exato da ocorrência",
    "1.6": "Histórico do local / facção"
}
```

**DEPOIS:**
```python
questions_map = {
    "1.1": "Dia, data e hora do acionamento",
    "1.2": "Composição da guarnição e prefixo",
    "1.3": "Natureza do empenho",
    "1.4": "Ordem de serviço / COPOM / DDU",
    "1.5": "Local exato da ocorrência",
    "1.6": "Histórico do local / facção",
    "1.7": "Proximidade de escola/hospital/transporte (Art. 40)"
}
```

**TAMBÉM** atualizar o prompt de geração de texto para incluir a nova informação sobre agravantes. Procurar pela seção "ESTRUTURA ESPERADA" ou "REGRAS DE REDAÇÃO" e adicionar:

```python
# Adicionar ao prompt:
"""
8. Agravantes Art. 40 (se aplicável): Se o local é próximo a escola, hospital ou transporte público,
   mencionar: "O local da ocorrência situa-se a aproximadamente [X] metros do/da [estabelecimento],
   configurando a circunstância agravante prevista no Art. 40, inciso [III/IV] da Lei 11.343/06."
"""
```

---

## 🧪 TESTES NECESSÁRIOS

### Teste 1: Validação aceita "NÃO"
```
Entrada: "NÃO"
Esperado: Válido, avança para próxima pergunta
```

### Teste 2: Validação aceita resposta com estabelecimento
```
Entrada: "Sim, a 80 metros da Escola Municipal Dom Pedro"
Esperado: Válido
```

### Teste 3: Validação rejeita resposta vaga
```
Entrada: "sim"
Esperado: Inválido - "Se sim, informe qual estabelecimento e a distância"
```

### Teste 4: Fluxo completo
```
1. Responder perguntas 1.1 a 1.6 normalmente
2. Sistema deve mostrar pergunta 1.7
3. Responder 1.7
4. Sistema deve gerar texto incluindo informação sobre Art. 40 (se aplicável)
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Atualizar `docs/index.html` - adicionar pergunta 1.7
- [ ] Atualizar `docs/index.html` - verificar referências a "6 perguntas"
- [ ] Atualizar `backend/state_machine.py` - QUESTIONS
- [ ] Atualizar `backend/state_machine.py` - STEPS
- [ ] Atualizar `backend/validator.py` - adicionar regra 1.7
- [ ] Atualizar `backend/validator.py` - lista de steps que aceitam "NÃO"
- [ ] Atualizar `backend/llm_service.py` - questions_map
- [ ] Atualizar `backend/llm_service.py` - prompt de geração
- [ ] Criar/atualizar testes unitários
- [ ] Testar fluxo completo localmente
- [ ] Commit e push
- [ ] Verificar CI/CD passou
- [ ] Testar em produção

---

## 📚 REFERÊNCIA LEGAL

**Lei 11.343/06, Art. 40 - Causas de aumento de pena:**

> As penas previstas nos arts. 33 a 37 desta Lei são aumentadas de um sexto a dois terços, se:
> 
> III – a infração tiver sido cometida nas dependências ou imediações de estabelecimentos prisionais, de ensino ou hospitalares, de sedes de entidades estudantis, sociais, culturais, recreativas, esportivas, ou beneficentes, de locais de trabalho coletivo, de recintos onde se realizem espetáculos ou diversões de qualquer natureza, de serviços de tratamento de dependentes de drogas ou de reinserção social, de unidades militares ou policiais ou em transportes públicos;
>
> IV – o crime tiver sido praticado com violência, grave ameaça, emprego de arma de fogo, ou qualquer processo de intimidação difusa ou coletiva;

---

## 🔄 COMMIT SUGERIDO

```
feat(section1): add question 1.7 for Art. 40 aggravating factors

- Add proximity to schools/hospitals/transport question
- Update state machine flow (6 → 7 questions)
- Add validation rules for 1.7
- Update LLM prompt to include Art. 40 reference
- Addresses legal requirement for drug trafficking cases

Ref: Lei 11.343/06, Art. 40, III
```

---

**Criado em:** 30/12/2024
**Prioridade:** 🚨 URGENTE
**Estimativa:** 1-2 horas

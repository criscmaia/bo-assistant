# 📝 ETAPA 3: Expandir Seção 2 - Abordagem a Veículo

## Contexto

A Seção 2 precisa ser expandida de **8 perguntas** para **11 perguntas**, com foco em:
- Separar abordagem de ocupantes da busca no veículo
- Detalhar quem realizou a busca e onde
- Especificar o que foi encontrado e com quem

---

## 📋 COMPARAÇÃO DETALHADA

| # | ATUAL | NOVO | Ação |
|---|-------|------|------|
| 2.1 | "Havia veículo?" | "Havia veículo na ocorrência?" | ✅ Ajuste menor |
| 2.2 | "Marca/modelo/cor/placa." | "Qual a marca, modelo, cor e placa?" | ✅ Ajuste menor |
| 2.3 | "Onde foi visto?" | "Onde e em que contexto o veículo foi visto?" | 🔄 Expandir |
| 2.4 | "Qual policial percebeu e o que viu?" | "Quem percebeu primeiro, de onde, e o que exatamente viu?" | ✅ ≈ |
| 2.5 | "Como foi dada a ordem de parada?" | "Como foi dada a ordem de parada?" | ✅ Igual |
| 2.6 | "Parou ou houve perseguição?" | "O veículo parou imediatamente ou houve perseguição?" | ✅ Ajuste menor |
| 2.7 | "Como foi a abordagem e busca?" | "Como foi realizada a abordagem dos ocupantes?" | 🔄 Separar |
| 2.8 | "Haviam irregularidades?..." | Movido para 2.11 | 🔄 Renumerar |
| **2.9** | ❌ NÃO EXISTE | "Quem realizou a busca no veículo e em quais partes?" | 🆕 NOVA |
| **2.10** | ❌ NÃO EXISTE | "O que foi localizado, com quem e em qual parte do veículo?" | 🆕 NOVA |
| **2.11** | ❌ | "O veículo apresentava irregularidades? Furto, roubo, clonagem?" | 🔄 Renumerado |

---

## 📋 NOVA ESTRUTURA DA SEÇÃO 2

```javascript
const SECTION2_QUESTIONS = {
    '2.1': 'Havia veículo envolvido na ocorrência?',
    '2.2': 'Qual a marca, modelo, cor e placa do veículo?',
    '2.3': 'Onde e em que contexto o veículo foi visto? (local + situação)',
    '2.4': 'Qual policial percebeu primeiro? De onde viu e o que exatamente observou? (graduação + nome)',
    '2.5': 'Como foi dada a ordem de parada? (sirene, megafone, sinal manual)',
    '2.6': 'O veículo parou imediatamente ou houve perseguição? Se houve, descreva o trajeto.',
    '2.7': 'Como foi realizada a abordagem dos ocupantes? (quem abordou, quantos ocupantes, posicionamento)',
    '2.8': 'Quem realizou a busca pessoal nos ocupantes? (graduação + nome)',
    '2.9': 'Quem realizou a busca no veículo e em quais partes? (graduação + nome + locais vistoriados)',
    '2.10': 'O que foi localizado, com quem estava e em qual parte do veículo?',
    '2.11': 'O veículo apresentava irregularidades? (furto, roubo, clonagem, adulteração)'
};
```

---

## 📋 O QUE PRECISA SER ALTERADO

### Arquivo 1: `docs/index.html`

**Localização:** Linha ~396-406 (constante `SECTION2_QUESTIONS`)

**SUBSTITUIR COMPLETAMENTE** o bloco:

```javascript
// Perguntas da Seção 2 (Abordagem a Veículo)
const SECTION2_QUESTIONS = {
    '2.1': 'Havia veículo envolvido na ocorrência?',
    '2.2': 'Qual a marca, modelo, cor e placa do veículo?',
    '2.3': 'Onde e em que contexto o veículo foi visto? (local + situação)',
    '2.4': 'Qual policial percebeu primeiro? De onde viu e o que exatamente observou? (graduação + nome)',
    '2.5': 'Como foi dada a ordem de parada? (sirene, megafone, sinal manual)',
    '2.6': 'O veículo parou imediatamente ou houve perseguição? Se houve, descreva o trajeto.',
    '2.7': 'Como foi realizada a abordagem dos ocupantes? (quem abordou, quantos ocupantes, posicionamento)',
    '2.8': 'Quem realizou a busca pessoal nos ocupantes? (graduação + nome)',
    '2.9': 'Quem realizou a busca no veículo e em quais partes? (graduação + nome + locais vistoriados)',
    '2.10': 'O que foi localizado, com quem estava e em qual parte do veículo?',
    '2.11': 'O veículo apresentava irregularidades? (furto, roubo, clonagem, adulteração)'
};
```

---

### Arquivo 2: `backend/validator_section2.py`

**SUBSTITUIR COMPLETAMENTE** o dicionário `VALIDATION_RULES_SECTION2`:

```python
# Regras de validação para cada pergunta da Seção 2
VALIDATION_RULES_SECTION2 = {
    "2.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO. Havia veículo envolvido na ocorrência?"
    },
    "2.2": {
        "min_length": 15,
        "custom_check": "vehicle_plate",
        "examples": [
            "VW Gol branco, placa ABC-1D23",
            "Fiat Palio preto, placa DXY9876",
            "Honda CG 160 vermelha, placa ABC1A23"
        ],
        "error_message": "Informe marca, modelo, cor e placa do veículo. Ex: 'VW Gol branco, placa ABC-1D23'"
    },
    "2.3": {
        "min_length": 30,
        "examples": [
            "Na Rua das Flores, altura do nº 123, Bairro Centro. O veículo estava estacionado em frente ao bar.",
            "Rodovia BR-381, km 450, sentido BH. O veículo transitava em alta velocidade.",
            "Esquina da Av. Brasil com Rua Rio. O veículo parou ao ver a viatura."
        ],
        "error_message": "Informe o local exato E o contexto (estacionado, em movimento, parado, etc.). Mínimo 30 caracteres."
    },
    "2.4": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva, de dentro da viatura estacionada a 30 metros, viu o condutor arremessar objeto pela janela",
            "O Cabo Almeida, posicionado na esquina, observou o veículo mudar bruscamente de direção ao notar a viatura"
        ],
        "error_message": "Informe: QUEM viu (graduação + nome), DE ONDE viu e O QUE exatamente observou. Mínimo 40 caracteres."
    },
    "2.5": {
        "min_length": 20,
        "examples": [
            "Foi acionada sirene e dado comando verbal 'Parado, Polícia Militar!' pelo megafone",
            "O Sargento fez sinal manual para encostar e acionou o giroflex",
            "Comando verbal direto pela janela da viatura: 'Encosta o veículo!'"
        ],
        "error_message": "Descreva como foi dada a ordem de parada (sirene, megafone, sinal manual, comando verbal)."
    },
    "2.6": {
        "min_length": 15,
        "examples": [
            "Parou imediatamente no acostamento",
            "Houve perseguição por aproximadamente 500 metros pela Rua Sete até a Praça Central, onde o veículo colidiu com o meio-fio",
            "Tentou fugir pela contramão, percorreu 200 metros e parou ao encontrar bloqueio"
        ],
        "error_message": "Informe se parou imediatamente ou houve perseguição. Se houve, descreva o trajeto."
    },
    "2.7": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva abordou o condutor pelo lado esquerdo. O Cabo Almeida abordou o passageiro pelo lado direito. Havia 2 ocupantes.",
            "O Soldado Faria ordenou que os 3 ocupantes descessem com as mãos na cabeça. O Cabo posicionou-se na contenção."
        ],
        "error_message": "Descreva: QUEM abordou (graduação + nome), quantos ocupantes e como foi o posicionamento. Mínimo 40 caracteres."
    },
    "2.8": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Cabo Almeida realizou busca pessoal no condutor. O Soldado Faria revistou o passageiro.",
            "A Soldado Pires realizou busca pessoal na ocupante feminina"
        ],
        "error_message": "Informe QUEM (graduação + nome) realizou a busca pessoal em cada ocupante. Mínimo 30 caracteres."
    },
    "2.9": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Soldado Faria vistoriou o porta-luvas, console central e sob os bancos. O Cabo Silva verificou o porta-malas.",
            "O Sargento Alves realizou busca completa: painel, bancos dianteiros e traseiros, porta-malas e compartimento do estepe"
        ],
        "error_message": "Informe QUEM (graduação + nome) fez a busca e QUAIS PARTES do veículo foram vistoriadas. Mínimo 40 caracteres."
    },
    "2.10": {
        "min_length": 30,
        "allow_none_response": True,
        "none_patterns": ["nada encontrado", "nada localizado", "sem material", "não foi encontrado", "negativo"],
        "examples": [
            "No porta-luvas, o Soldado Faria localizou 20 porções de cocaína. No bolso do condutor João Silva, foram encontradas R$ 350,00 em notas diversas.",
            "Sob o banco traseiro, encontradas 15 pedras de crack. Com o passageiro, 2 celulares.",
            "Nada de ilícito foi localizado no veículo ou com os ocupantes"
        ],
        "error_message": "Informe O QUE foi encontrado, COM QUEM ou EM QUAL PARTE do veículo. Se nada, informe 'Nada localizado'."
    },
    "2.11": {
        "min_length": 3,
        "allow_none_response": True,
        "none_patterns": ["não", "nao", "negativo", "nenhuma", "sem irregularidade", "regular"],
        "examples": [
            "NÃO",
            "Veículo com queixa de furto, consta no REDS 2024-001234",
            "Placa clonada - chassi divergente do registrado no documento",
            "Veículo com registro de roubo em Contagem/MG, REDS 2023-005678"
        ],
        "error_message": "Informe irregularidades (furto, roubo, clonagem) com REDS se houver. Se não, responda 'NÃO'."
    }
}
```

---

### Arquivo 3: Atualizar a classe `ResponseValidatorSection2`

Verificar se a classe precisa de novos métodos para as validações adicionadas, especialmente:

1. **`allow_none_response`** para pergunta 2.10 (pode não encontrar nada)
2. **`none_patterns`** para aceitar respostas negativas

Se a classe não tiver suporte a `allow_none_response`, adicionar:

```python
@staticmethod
def _check_none_response(answer: str, none_patterns: list) -> bool:
    """
    Verifica se a resposta indica ausência de material/irregularidade.
    
    Args:
        answer: Resposta do usuário
        none_patterns: Lista de padrões que indicam "nada encontrado"
    
    Returns:
        True se a resposta indica negativo, False caso contrário
    """
    answer_lower = answer.lower()
    
    for pattern in none_patterns:
        if pattern.lower() in answer_lower:
            return True
    
    return False
```

E atualizar o método `validate()` para usar essa verificação nas perguntas 2.10 e 2.11.

---

## 🧪 TESTES NECESSÁRIOS

### Teste 1: Fluxo completo com 11 perguntas
```
1. Responder 2.1 com "SIM"
2. Verificar que aparecem perguntas 2.2 a 2.11 em sequência
3. Verificar barra de progresso mostra 11 perguntas
```

### Teste 2: Validação de placa (2.2)
```
Entrada: "Gol branco ABC-1D23"
Esperado: Válido (extrai placa Mercosul)

Entrada: "Gol branco"
Esperado: Inválido - falta placa
```

### Teste 3: Validação de graduação (2.4, 2.7, 2.8, 2.9)
```
Entrada: "O policial viu o veículo parar"
Esperado: Inválido - falta graduação

Entrada: "O Sargento Silva viu o veículo parar bruscamente"
Esperado: Válido
```

### Teste 4: Resposta negativa aceita (2.10, 2.11)
```
Entrada pergunta 2.10: "Nada localizado"
Esperado: Válido

Entrada pergunta 2.11: "NÃO"
Esperado: Válido
```

### Teste 5: Contexto obrigatório (2.3)
```
Entrada: "Rua das Flores"
Esperado: Inválido - falta contexto

Entrada: "Rua das Flores, altura do nº 100. Veículo estacionado em frente ao bar."
Esperado: Válido
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Frontend
- [ ] Atualizar `docs/index.html` - SECTION2_QUESTIONS (8→11 perguntas)
- [ ] Verificar sidebar mostra 11 perguntas na Seção 2
- [ ] Verificar barra de progresso atualizada

### Backend
- [ ] Atualizar `backend/validator_section2.py` - VALIDATION_RULES (8→11)
- [ ] Adicionar método `_check_none_response` se não existir
- [ ] Atualizar método `validate()` para novas regras
- [ ] Verificar integração com main.py

### Testes
- [ ] Criar/atualizar `tests/unit/test_validator_section2.py`
- [ ] Testar todas as 11 perguntas
- [ ] Testar validação de placa Mercosul
- [ ] Testar exigência de graduação militar
- [ ] Testar respostas negativas aceitas

### Deploy
- [ ] Testar localmente
- [ ] Commit e push
- [ ] Verificar CI passou
- [ ] Testar em produção

---

## 🔄 COMMIT SUGERIDO

```
feat(section2): expand vehicle approach section from 8 to 11 questions

- Split old 2.7 (approach + search) into separate questions
- Add 2.8: personal search on occupants
- Add 2.9: vehicle search details (who + where)
- Add 2.10: what was found, with whom, where
- Renumber 2.8 (irregularities) to 2.11
- Add context requirement to 2.3
- Update validation rules for all 11 questions

Improves documentation of vehicle search procedures per domain expert requirements
```

---

## 📚 FUNDAMENTAÇÃO

A separação das perguntas sobre busca pessoal e busca veicular é importante porque:

1. **Legalidade**: CPP Art. 244 autoriza busca pessoal. Busca em veículo tem fundamentação diferente.

2. **Cadeia de custódia**: É essencial saber QUEM encontrou O QUÊ e ONDE para a cadeia de custódia.

3. **Individualização**: Cada ocupante pode ter responsabilidade diferente dependendo do que foi encontrado COM ele vs. NO veículo.

---

**Criado em:** 30/12/2024
**Prioridade:** 📝 MÉDIO
**Estimativa:** 2-3 horas
**Dependência:** Completar Etapas 1 e 2 primeiro

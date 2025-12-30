# ⚠️ ETAPA 2: Reformular Seção 8 - Condução e Pós-Ocorrência

## Contexto

A Seção 8 é a que mais mudou no novo prompt do Claudio. Passou de **6 perguntas** para **11 perguntas**, com foco em:
- Detalhamento do transporte do preso
- Função do preso no tráfico
- Indícios de organização criminosa
- Destruição/ocultação de provas
- Envolvimento de menores
- Garantias constitucionais

---

## 📋 COMPARAÇÃO DETALHADA

| # | ATUAL | NOVO | Ação |
|---|-------|------|------|
| 8.1 | "Quem deu voz de prisão e por qual crime?" | "Quem deu voz de prisão e por qual crime?" | ✅ Manter |
| 8.2 | "Havia agravantes? (art. 40...)" | "Onde e como o preso foi transportado?" | 🔄 Substituir |
| 8.3 | "O preso declarou algo?" | "O preso declarou algo?" | ✅ Manter |
| 8.4 | "O preso possui registros anteriores?" | "Qual era a função do preso no tráfico?" | 🆕 Nova |
| 8.5 | "O preso possui vínculo com facção?" | "O preso possui passagens anteriores? (REDS)" | 🔄 Renumerar |
| 8.6 | "Garantias + destino" | "Há sinais de dedicação ao crime?" | 🆕 Nova |
| 8.7 | ❌ | "Papel na facção? (ocasional ou contínua)" | 🆕 Nova |
| 8.8 | ❌ | "Tentativa de destruir/ocultar provas ou intimidar?" | 🆕 Nova |
| 8.9 | ❌ | "Havia menor envolvido? Idade e participação?" | 🆕 Nova |
| 8.10 | ❌ | "Quem informou as garantias constitucionais?" | 🆕 Nova |
| 8.11 | ❌ | "Destino dos presos e materiais apreendidos" | 🆕 Nova |

**NOTA:** Baseado em materiais-claudio/SEÇÃO_8___CONDUÇÃO_E_PÓS-OCORRÊNCIA.md

---

## 📋 NOVA ESTRUTURA DA SEÇÃO 8

```javascript
const SECTION8_QUESTIONS = {
    '8.1': 'Quem deu voz de prisão e por qual crime? (graduação + nome + artigo)',
    '8.2': 'Onde e como o preso foi transportado até a delegacia?',
    '8.3': 'O preso declarou algo? (transcrição literal ou "permaneceu em silêncio")',
    '8.4': 'Qual era a função do preso no tráfico? (vapor, gerente, olheiro, etc.)',
    '8.5': 'O preso possui passagens anteriores? (informar REDS se houver)',
    '8.6': 'Há sinais de dedicação ao crime? O que mostra isso?',
    '8.7': 'O preso tem papel relevante na facção? Atuação ocasional ou contínua?',
    '8.8': 'Houve tentativa de destruir ou ocultar provas, ou intimidar alguém?',
    '8.9': 'Havia menor de idade envolvido na ocorrência? Se sim, idade e participação?',
    '8.10': 'Quem informou as garantias constitucionais ao preso? (graduação + nome)',
    '8.11': 'Qual o destino dos presos e dos materiais apreendidos? (delegacia, CEFLAN, etc.)'
};
```

**IMPORTANTE:** São 11 perguntas (8.1 a 8.11), não 12. A pergunta sobre "vínculo com facção" foi incorporada em 8.7 (papel na facção).

---

## 📋 O QUE PRECISA SER ALTERADO

### Arquivo 1: `docs/index.html`

**Localização:** Linha ~451-458 (constante `SECTION8_QUESTIONS`)

**SUBSTITUIR COMPLETAMENTE** o bloco `SECTION8_QUESTIONS` pelo novo:

```javascript
const SECTION8_QUESTIONS = {
    '8.1': 'Quem deu voz de prisão e por qual crime? (graduação + nome + artigo)',
    '8.2': 'Onde e como o preso foi transportado até a delegacia?',
    '8.3': 'O preso declarou algo? (transcrição literal ou "permaneceu em silêncio")',
    '8.4': 'Qual era a função do preso no tráfico? (vapor, gerente, olheiro, etc.)',
    '8.5': 'O preso possui passagens anteriores? (informar REDS se houver)',
    '8.6': 'Há sinais de dedicação ao crime? O que mostra isso?',
    '8.7': 'O preso tem papel relevante na facção? Atuação ocasional ou contínua?',
    '8.8': 'Houve tentativa de destruir ou ocultar provas, ou intimidar alguém?',
    '8.9': 'Havia menor de idade envolvido na ocorrência? Se sim, idade e participação?',
    '8.10': 'Quem informou as garantias constitucionais ao preso? (graduação + nome)',
    '8.11': 'Qual o destino dos presos e dos materiais apreendidos? (delegacia, CEFLAN, etc.)'
};
```

---

### Arquivo 2: `backend/validator_section8.py`

**SUBSTITUIR COMPLETAMENTE** o dicionário `VALIDATION_RULES_SECTION8`:

```python
VALIDATION_RULES_SECTION8 = {
    "8.1": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva deu voz de prisão pelo crime de tráfico de drogas (art. 33 da Lei 11.343/06)",
            "O Cabo Almeida deu voz de prisão por tráfico (art. 33) e associação (art. 35)"
        ],
        "error_message": "Informe QUEM deu voz de prisão (graduação + nome) e POR QUAL CRIME (artigo). Mínimo 30 caracteres."
    },
    "8.2": {
        "min_length": 20,
        "required_keywords_any": ["viatura", "prefixo", "veículo", "conduzido", "transportado"],
        "examples": [
            "O preso foi conduzido na viatura prefixo 1234, no banco traseiro, algemado",
            "Transportado na viatura da guarnição até a Delegacia de Plantão"
        ],
        "error_message": "Informe como o preso foi transportado (viatura, prefixo, posição). Mínimo 20 caracteres."
    },
    "8.3": {
        "min_length": 10,
        "allow_none_response": True,
        "none_patterns": ["não declarou", "permaneceu em silêncio", "silêncio", "nada declarou", "recusou"],
        "examples": [
            "O preso declarou: 'Essa droga não é minha, estava só guardando'",
            "Permaneceu em silêncio, exercendo seu direito constitucional",
            "Não declarou nada"
        ],
        "error_message": "Transcreva literalmente o que o preso declarou ou informe 'Permaneceu em silêncio'."
    },
    "8.4": {
        "min_length": 10,
        "allow_none_response": True,
        "none_patterns": ["não identificada", "não apurada", "desconhecida", "não informada"],
        "examples": [
            "Vapor - responsável pela venda direta aos usuários",
            "Gerente do ponto de tráfico",
            "Olheiro - vigiava a chegada da polícia",
            "Função não identificada durante a ocorrência"
        ],
        "error_message": "Informe a função no tráfico (vapor, gerente, olheiro, etc.) ou 'Não identificada'."
    },
    "8.5": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["sem passagens", "nada consta", "sem registros", "não possui", "negativo"],
        "examples": [
            "Possui REDS 2024-001234 por tráfico e REDS 2023-005678 por associação",
            "Sem passagens anteriores no sistema REDS",
            "Nada consta"
        ],
        "error_message": "Informe os REDS anteriores ou 'Sem passagens anteriores'."
    },
    "8.6": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não há", "sem indícios", "não identificado", "negativo", "não foram identificados"],
        "examples": [
            "Sim, portava cordão de ouro, relógio de luxo e R$ 5.000 em espécie",
            "Tatuagem com símbolo da facção no antebraço direito",
            "Não há indícios aparentes"
        ],
        "error_message": "Descreva indícios de dedicação ao crime (ostentação, tatuagens) ou 'Não há indícios'."
    },
    "8.7": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não", "sem papel", "não identificado", "negativo", "não possui", "ocasional"],
        "examples": [
            "Sim, identificado como gerente regional da facção na zona norte",
            "É conhecido como 'disciplina' da boca de fumo, atuação contínua",
            "Atuação ocasional, sem papel de liderança identificado"
        ],
        "error_message": "Informe papel na facção (ocasional ou contínua) ou 'Não identificado'."
    },
    "8.8": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não houve", "não tentou", "negativo", "não"],
        "examples": [
            "Sim, tentou jogar sacola com drogas pela janela ao ver a viatura",
            "Tentou engolir porções de cocaína durante a abordagem",
            "Ameaçou testemunha: 'Se falar de mim, vou voltar aqui'",
            "Não houve tentativa de destruição ou intimidação"
        ],
        "error_message": "Descreva tentativa de destruir/ocultar provas ou intimidar, ou 'Não houve'."
    },
    "8.9": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não havia", "não", "negativo", "nenhum menor"],
        "examples": [
            "Sim, menor de 16 anos atuava como olheiro",
            "Havia criança de 12 anos no imóvel, encaminhada ao Conselho Tutelar",
            "Não havia menor envolvido"
        ],
        "error_message": "Informe se havia menor, idade e participação, ou 'Não havia menor'."
    },
    "8.10": {
        "min_length": 20,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva informou as garantias constitucionais ao preso",
            "O Cabo Almeida leu os direitos do preso, que declarou ter compreendido"
        ],
        "error_message": "Informe QUEM (graduação + nome) informou as garantias constitucionais."
    },
    "8.11": {
        "min_length": 30,
        "required_keywords_any": ["delegacia", "ceflan", "dp", "dipc", "central", "plantão"],
        "examples": [
            "Presos conduzidos à Delegacia de Plantão Central. Drogas encaminhadas à CEFLAN 2",
            "Autor apresentado na DIPC. Material apreendido lacrado e entregue na CEFLAN",
            "Conduzido à DP de Contagem. Drogas e dinheiro entregues na delegacia"
        ],
        "error_message": "Informe destino dos PRESOS (delegacia) e dos MATERIAIS (CEFLAN). Mínimo 30 caracteres."
    }
}
```

**TAMBÉM** atualizar a docstring da classe para refletir as novas perguntas.

---

### Arquivo 3: `backend/llm_service.py`

Atualizar o mapeamento de perguntas da Seção 8 no prompt de geração (se houver referência específica à Seção 8).

Procurar por referências às perguntas antigas (8.2 sobre agravantes, por exemplo) e remover/atualizar.

---

### Arquivo 4: Testes

Atualizar/criar testes para as novas perguntas:

**Arquivo:** `tests/unit/test_validator_section8.py` (criar se não existir)

```python
import pytest
from validator_section8 import ResponseValidatorSection8

class TestSection8Validation:
    
    def test_8_1_requires_graduation_and_crime(self):
        """8.1 deve exigir graduação + nome + crime"""
        # Válido
        valid, _ = ResponseValidatorSection8.validate(
            "8.1", 
            "O Sargento Silva deu voz de prisão por tráfico art. 33"
        )
        assert valid == True
        
        # Inválido - sem graduação
        valid, error = ResponseValidatorSection8.validate(
            "8.1", 
            "Foi dada voz de prisão por tráfico"
        )
        assert valid == False
    
    def test_8_3_accepts_silence(self):
        """8.3 deve aceitar 'permaneceu em silêncio'"""
        valid, _ = ResponseValidatorSection8.validate(
            "8.3", 
            "Permaneceu em silêncio"
        )
        assert valid == True
    
    def test_8_4_accepts_function_or_unknown(self):
        """8.4 deve aceitar função ou 'não identificada'"""
        # Função conhecida
        valid, _ = ResponseValidatorSection8.validate("8.4", "Vapor")
        assert valid == True
        
        # Função desconhecida
        valid, _ = ResponseValidatorSection8.validate("8.4", "Não identificada")
        assert valid == True
    
    def test_8_10_minor_involvement(self):
        """8.10 deve validar envolvimento de menor"""
        # Com menor
        valid, _ = ResponseValidatorSection8.validate(
            "8.10", 
            "Sim, menor de 15 anos atuava como olheiro"
        )
        assert valid == True
        
        # Sem menor
        valid, _ = ResponseValidatorSection8.validate(
            "8.10", 
            "Não havia menor"
        )
        assert valid == True
    
    def test_8_12_requires_destination(self):
        """8.12 deve exigir destino"""
        valid, _ = ResponseValidatorSection8.validate(
            "8.12", 
            "Presos conduzidos à Delegacia Central. Drogas para CEFLAN"
        )
        assert valid == True
        
        valid, error = ResponseValidatorSection8.validate(
            "8.12", 
            "Foram conduzidos"
        )
        assert valid == False
```

---

## 🧪 TESTES DE FLUXO

### Teste 1: Fluxo completo da Seção 8
```
1. Responder Seções 1-7 normalmente
2. Iniciar Seção 8
3. Verificar que aparecem 11 perguntas em sequência (8.1 a 8.11)
4. Verificar que cada pergunta aceita as respostas esperadas
5. Verificar que texto gerado inclui todas as informações
```

### Teste 2: Perguntas com resposta negativa
```
Perguntas 8.3 a 8.9 devem aceitar respostas como:
- "Não"
- "Não há"
- "Sem vínculo"
- "Permaneceu em silêncio"
- etc.
```

### Teste 3: Perguntas obrigatórias
```
Perguntas 8.1, 8.2, 8.10 e 8.11 NÃO devem aceitar resposta vazia ou muito curta.
Devem exigir graduação militar onde especificado (8.1 e 8.10).
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Frontend
- [ ] Atualizar `docs/index.html` - SECTION8_QUESTIONS
- [ ] Verificar sidebar/progresso mostra 11 perguntas na Seção 8
- [ ] Verificar navegação entre perguntas funciona

### Backend
- [ ] Atualizar `backend/validator_section8.py` - VALIDATION_RULES
- [ ] Atualizar classe ResponseValidatorSection8
- [ ] Verificar integração com main.py

### LLM
- [ ] Atualizar `backend/llm_service.py` se necessário
- [ ] Remover referências ao antigo 8.2 (agravantes)
- [ ] Adicionar instruções para novas perguntas no prompt

### Testes
- [ ] Criar/atualizar `tests/unit/test_validator_section8.py`
- [ ] Testar todas as 11 perguntas
- [ ] Testar respostas negativas aceitas
- [ ] Testar fluxo completo

### Deploy
- [ ] Testar localmente
- [ ] Commit e push
- [ ] Verificar CI passou
- [ ] Testar em produção

---

## 🔄 COMMIT SUGERIDO

```
feat(section8): refactor section 8 with 11 questions

BREAKING CHANGE: Section 8 now has 11 questions instead of 6

- Remove old 8.2 (aggravating factors - moved to 1.7)
- Add 8.2: transport details
- Add 8.4: suspect's role in trafficking
- Add 8.6: evidence of crime dedication
- Add 8.7: faction role (occasional vs continuous)
- Add 8.8: evidence destruction/intimidation attempts
- Add 8.9: minor involvement
- Add 8.10: constitutional rights notification
- Add 8.11: destination of suspects and materials
- Update validation rules for all 11 questions

Addresses new requirements from domain expert (SEÇÃO_8.md)
```

---

## ⚠️ NOTAS IMPORTANTES

1. **Breaking Change**: Esta alteração muda significativamente o fluxo da Seção 8. BOs em andamento podem ser afetados.

2. **Migração de dados**: Se houver BOs salvos com a estrutura antiga, considerar estratégia de migração.

3. **Ordem das perguntas**: A ordem foi otimizada para fluxo lógico durante a ocorrência.

4. **Perguntas sensíveis**: 8.10 (menores) requer cuidado especial no tratamento da informação.

---

**Criado em:** 30/12/2024
**Prioridade:** ⚠️ IMPORTANTE
**Estimativa:** 3-4 horas
**Dependência:** Completar Etapa 1 primeiro

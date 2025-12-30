# 🔧 ETAPA 4: Ajustes - Seções 3, 4, 5 e 6

## Contexto

Baseado na análise dos arquivos `materiais-claudio/SEÇÃO_*.md` (fonte prioritária), as mudanças são:
- **Seção 3:** MANTER 8 perguntas (apenas ajustes textuais)
- **Seção 4:** MANTER 5 perguntas (apenas adicionar exemplos)
- **Seção 5:** Remover pergunta condicional 5.1, renumerar (4→3)
- **Seção 6:** Adicionar pergunta sobre arma/ameaça (5→6)

---

## 📋 SEÇÃO 3 - CAMPANA (8 → 8 perguntas) ✅ SEM MUDANÇA DE QUANTIDADE

### Mudança Principal
Apenas **ajustes textuais** para adicionar mais exemplos e detalhes, conforme SEÇÃO_3.md.

### ATUAL vs NOVO

| # | ATUAL | NOVO | Ação |
|---|-------|------|------|
| 3.1 | "Realizou campana?" | "A equipe realizou campana (vigilância velada)?" | ✅ Ajuste texto |
| 3.2 | "Local da campana..." | "Local exato da campana, ponto de observação e distância até o alvo." | ✅ Ajuste texto |
| 3.3 | "Policial com visão direta..." | "Quem tinha visão direta e o que cada um conseguia ver? (graduação + nome)" | ✅ Ajuste texto |
| 3.4 | "Motivação da campana" | "O que motivou a campana? (denúncia, inteligência, histórico)" | ✅ Ajuste texto |
| 3.5 | "Duração (contínua ou alternada)" | "Qual foi a duração da campana? (tempo e se foi contínua ou alternada)" | ✅ Ajuste texto |
| 3.6 | "O que foi observado (atos concretos)" | "O que foi visto? (entregas, usuários, esconderijos)" | ✅ Adicionar exemplos |
| 3.7 | "Abordagem de usuários?" | "Houve abordagem de usuário? O que portava? O que disse?" | ✅ Adicionar detalhes |
| 3.8 | "Houve fuga?" | "Houve fuga? Como ocorreu?" | ✅ Adicionar detalhes |

**NOTA:** A pergunta 3.8 está presente nos modelos de SEÇÃO_3.md (ex: Modelo 3 - "Tentativa de fuga").

### Estrutura MANTIDA (apenas ajustes textuais):

```javascript
const SECTION3_QUESTIONS = {
    '3.1': 'A equipe realizou campana (vigilância velada)?',
    '3.2': 'Local exato da campana, ponto de observação e distância aproximada até o alvo.',
    '3.3': 'Quem tinha visão direta e o que cada um conseguia ver? (graduação + nome)',
    '3.4': 'O que motivou a campana? (denúncia, inteligência, histórico do local)',
    '3.5': 'Qual foi a duração da campana? (tempo aproximado e se foi contínua ou alternada)',
    '3.6': 'O que foi visto durante a campana? (entregas, usuários, esconderijos)',
    '3.7': 'Houve abordagem de usuário? O que portava? O que disse?',
    '3.8': 'Houve fuga? Como ocorreu?'
};
```

---

## 📋 SEÇÃO 4 - ENTRADA EM DOMICÍLIO (5 → 5 perguntas) ✅ SEM MUDANÇA DE QUANTIDADE

### Mudança Principal
Apenas **adicionar exemplos** na pergunta 4.4, conforme SEÇÃO_4.md.

### ATUAL vs NOVO

| # | ATUAL | NOVO | Ação |
|---|-------|------|------|
| 4.1 | "Houve entrada em domicílio?" | "Houve entrada em domicílio?" | ✅ Igual |
| 4.2 | "O que foi visto/ouvido ANTES..." | "O que foi visto/ouvido ANTES do ingresso?" | ✅ Igual |
| 4.3 | "Policial que presenciou..." | "Quem viu e o quê? (graduação + nome)" | ✅ Ajuste texto |
| 4.4 | "Como ocorreu o ingresso" | "Como ocorreu o ingresso? (autorização, perseguição, droga à vista)" | ✅ Adicionar exemplos |
| 4.5 | "Ação de cada policial" | "Quais policiais entraram? Quem fez o quê?" | ✅ MANTER |

**NOTA:** A pergunta 4.5 está no checklist operacional de SEÇÃO_4.md ("Quem entrou primeiro?", "Qual o primeiro objeto visualizado?").

### Estrutura MANTIDA (apenas ajustes textuais):

```javascript
const SECTION4_QUESTIONS = {
    '4.1': 'Houve entrada em domicílio?',
    '4.2': 'O que foi visto/ouvido ANTES do ingresso?',
    '4.3': 'Quem viu e o quê? (graduação + nome)',
    '4.4': 'Como ocorreu o ingresso? (autorização, perseguição, droga à vista)',
    '4.5': 'Quais policiais entraram? Quem fez o quê?'
};
```

---

## 📋 SEÇÃO 5 - FUNDADA SUSPEITA (4 → 3 perguntas)

### Mudança Principal
A pergunta **5.1 condicional** ("Houve abordagem por fundada suspeita?") foi **REMOVIDA** porque:
- A seção já é opcional (só aparece quando relevante)
- O Prompt_2025-12-29.md mostra apenas 3 perguntas nesta seção
- Elimina pergunta redundante

**IMPORTANTE:** A mudança é remover a 5.1, NÃO a 5.4. As perguntas são renumeradas.

### ATUAL vs NOVO

| # | ATUAL | NOVO | Ação |
|---|-------|------|------|
| 5.1 | "Houve abordagem por fundada suspeita...?" | ❌ **REMOVIDA** (seção já é opcional) | 🗑️ Remover |
| 5.2 | "O que a equipe viu ao chegar...?" | → 5.1 "O que a equipe viu ao chegar no local?" | 🔄 Renumerar |
| 5.3 | "Quem viu, de onde, o que...?" | → 5.2 "Quem viu, de onde, e o que exatamente?" | 🔄 Renumerar |
| 5.4 | "Características dos abordados..." | → 5.3 "Descrever aparência e ações dos abordados." | 🔄 Renumerar |

### Nova estrutura:

```javascript
const SECTION5_QUESTIONS = {
    '5.1': 'O que a equipe viu ao chegar no local?',
    '5.2': 'Quem viu, de onde, e o que exatamente?',
    '5.3': 'Descrever aparência e ações dos abordados.'
};
```

---

## 📋 SEÇÃO 6 - REAÇÃO, USO DA FORÇA E ALGEMAS (5 → 6 perguntas)

### Mudança Principal
**ADICIONAR** pergunta sobre arma/ameaça ANTES das perguntas sobre resistência, conforme Prompt_2025-12-29.md (linha 177).

### ATUAL vs NOVO

| # | ATUAL | NOVO | Ação |
|---|-------|------|------|
| - | ❌ NÃO EXISTE | → 6.1 "Houve ameaça ou uso de arma? Contra quem e como?" | 🆕 ADICIONAR |
| 6.1 | "Houve resistência?" | → 6.2 "Houve resistência? Se NÃO, ignorar." | 🔄 Renumerar |
| 6.2 | "Descreva a resistência..." | → 6.3 "Descrever resistência (ex.: empurrão, fuga, soco)" | 🔄 Renumerar |
| 6.3 | "Técnica aplicada..." | → 6.4 "Técnica usada e resultado." | 🔄 Renumerar |
| 6.4 | "Justificativa algemas..." | → 6.5 "Justificar uso de algema (risco de fuga, agressividade)" | 🔄 Renumerar |
| 6.5 | "Ferimentos..." | → 6.6 "Ferimentos? Detalhar quem, tipo, local de atendimento." | 🔄 Renumerar |

### Nova estrutura:

```javascript
const SECTION6_QUESTIONS = {
    '6.1': 'Houve ameaça ou uso de arma? Contra quem e como?',
    '6.2': 'Houve resistência durante a abordagem?',
    '6.3': 'Descreva a resistência com fatos concretos (ex.: empurrão, fuga, soco)',
    '6.4': 'Qual técnica foi aplicada e qual foi o resultado?',
    '6.5': 'Por que foi necessário algemar? (risco de fuga, agressividade)',
    '6.6': 'Houve ferimentos? Descreva: quem, tipo, local de atendimento.'
};
```

---

## 📋 O QUE PRECISA SER ALTERADO

### Arquivo 1: `docs/index.html`

**Seção 3** - apenas ajustes textuais (mantém 8 perguntas):
```javascript
const SECTION3_QUESTIONS = {
    '3.1': 'A equipe realizou campana (vigilância velada)?',
    '3.2': 'Local exato da campana, ponto de observação e distância aproximada até o alvo.',
    '3.3': 'Quem tinha visão direta e o que cada um conseguia ver? (graduação + nome)',
    '3.4': 'O que motivou a campana? (denúncia, inteligência, histórico do local)',
    '3.5': 'Qual foi a duração da campana? (tempo aproximado e se foi contínua ou alternada)',
    '3.6': 'O que foi visto durante a campana? (entregas, usuários, esconderijos)',
    '3.7': 'Houve abordagem de usuário? O que portava? O que disse?',
    '3.8': 'Houve fuga? Como ocorreu?'
};
```

**Seção 4** - apenas ajustes textuais (mantém 5 perguntas):
```javascript
const SECTION4_QUESTIONS = {
    '4.1': 'Houve entrada em domicílio?',
    '4.2': 'O que foi visto/ouvido ANTES do ingresso?',
    '4.3': 'Quem viu e o quê? (graduação + nome)',
    '4.4': 'Como ocorreu o ingresso? (autorização, perseguição, droga à vista)',
    '4.5': 'Quais policiais entraram? Quem fez o quê?'
};
```

**Seção 5** - remover 5.1 e renumerar (4→3 perguntas):
```javascript
const SECTION5_QUESTIONS = {
    '5.1': 'O que a equipe viu ao chegar no local?',
    '5.2': 'Quem viu, de onde, e o que exatamente?',
    '5.3': 'Descrever aparência e ações dos abordados.'
};
```

**Seção 6** - adicionar 6.1 sobre arma (5→6 perguntas):
```javascript
const SECTION6_QUESTIONS = {
    '6.1': 'Houve ameaça ou uso de arma? Contra quem e como?',
    '6.2': 'Houve resistência durante a abordagem?',
    '6.3': 'Descreva a resistência com fatos concretos (ex.: empurrão, fuga, soco)',
    '6.4': 'Qual técnica foi aplicada e qual foi o resultado?',
    '6.5': 'Por que foi necessário algemar? (risco de fuga, agressividade)',
    '6.6': 'Houve ferimentos? Descreva: quem, tipo, local de atendimento.'
};
```

---

### Arquivo 2: `backend/validator_section3.py`

**MANTER** estrutura atual, apenas atualizar textos das perguntas.

---

### Arquivo 3: `backend/validator_section4.py`

**MANTER** estrutura atual, apenas adicionar exemplos na regra 4.4.

---

### Arquivo 4: `backend/validator_section5.py`

**REMOVER** a regra de validação para "5.1" e **RENUMERAR** as demais:
- 5.2 → 5.1
- 5.3 → 5.2
- 5.4 → 5.3

---

### Arquivo 5: `backend/validator_section6.py`

**ADICIONAR** regra para nova pergunta 6.1 e **RENUMERAR** as demais:

```python
"6.1": {
    "min_length": 5,
    "allow_none_response": True,
    "none_patterns": ["não houve", "não", "negativo"],
    "examples": [
        "Sim, o autor sacou arma de fogo e apontou para o Sargento Silva",
        "Não houve ameaça ou uso de arma"
    ],
    "error_message": "Descreva se houve ameaça ou uso de arma, ou informe 'Não houve'."
}
```

---

## 🧪 TESTES NECESSÁRIOS

### Seção 3 (8 perguntas - SEM MUDANÇA)
```
1. Verificar que aparecem 8 perguntas (3.1 a 3.8)
2. Verificar que textos foram atualizados com mais exemplos
3. Testar fluxo completo da campana
```

### Seção 4 (5 perguntas - SEM MUDANÇA)
```
1. Verificar que aparecem 5 perguntas (4.1 a 4.5)
2. Verificar que 4.4 agora inclui exemplos (autorização, perseguição, droga à vista)
3. Testar validação do ingresso
```

### Seção 5 (3 perguntas - ANTES 4)
```
1. Verificar que aparecem apenas 3 perguntas (5.1 a 5.3)
2. Verificar que pergunta condicional foi REMOVIDA
3. Nova 5.1 = antiga 5.2, nova 5.2 = antiga 5.3, nova 5.3 = antiga 5.4
```

### Seção 6 (6 perguntas - ANTES 5)
```
1. Verificar que aparecem 6 perguntas (6.1 a 6.6)
2. Verificar que NOVA 6.1 sobre arma/ameaça aparece PRIMEIRO
3. Verificar renumeração: antiga 6.1 agora é 6.2, etc.
4. Testar resposta "Não houve" para 6.1 é aceita
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Seção 3 - Campana (8 perguntas - ajustes textuais)
- [ ] Atualizar `docs/index.html` - SECTION3_QUESTIONS (apenas textos)
- [ ] Atualizar `backend/validator_section3.py` - ajustar textos/exemplos
- [ ] Verificar sidebar mostra 8 perguntas

### Seção 4 - Domicílio (5 perguntas - adicionar exemplos)
- [ ] Atualizar `docs/index.html` - SECTION4_QUESTIONS (apenas textos)
- [ ] Atualizar `backend/validator_section4.py` - adicionar exemplos em 4.4
- [ ] Verificar sidebar mostra 5 perguntas

### Seção 5 - Fundada Suspeita (4→3 perguntas)
- [ ] Atualizar `docs/index.html` - SECTION5_QUESTIONS (remover 5.1, renumerar)
- [ ] Atualizar `backend/validator_section5.py` - remover regra 5.1, renumerar
- [ ] Verificar sidebar mostra 3 perguntas

### Seção 6 - Reação/Força (5→6 perguntas)
- [ ] Atualizar `docs/index.html` - SECTION6_QUESTIONS (adicionar 6.1, renumerar)
- [ ] Atualizar `backend/validator_section6.py` - adicionar regra 6.1, renumerar
- [ ] Verificar sidebar mostra 6 perguntas

### Testes
- [ ] Testar fluxo de cada seção
- [ ] Verificar totais de perguntas corretos
- [ ] Testar que nova 6.1 aceita "Não houve"

### Deploy
- [ ] Testar localmente
- [ ] Commit e push
- [ ] Verificar CI passou
- [ ] Testar em produção

---

## 🔄 COMMIT SUGERIDO

```
feat(sections): adjust sections 3, 4, 5, and 6

Section 3 - Campana:
- Update question texts with more examples
- Keep all 8 questions (3.1 to 3.8)

Section 4 - Domicílio:
- Add examples to 4.4 (autorização, perseguição, droga à vista)
- Keep all 5 questions (4.1 to 4.5)

Section 5 - Fundada Suspeita:
- Remove conditional 5.1 (section is already optional)
- Renumber 5.2→5.1, 5.3→5.2, 5.4→5.3
- 4 → 3 questions

Section 6 - Reação/Força:
- Add new 6.1 "Houve ameaça ou uso de arma?"
- Renumber all subsequent questions
- 5 → 6 questions

Net change: +1 question across these sections (22 → 22)
Improves legal documentation per domain expert feedback
```

---

## 📊 RESUMO DAS MUDANÇAS

| Seção | Antes | Depois | Diferença | Tipo de Mudança |
|-------|-------|--------|-----------|-----------------|
| 3 - Campana | 8 | 8 | = | Ajustes textuais |
| 4 - Domicílio | 5 | 5 | = | Adicionar exemplos |
| 5 - Fundada Suspeita | 4 | 3 | -1 | Remover 5.1 condicional |
| 6 - Reação/Força | 5 | 6 | +1 | Adicionar arma/ameaça |
| **Total** | **22** | **22** | **=** | |

---

## ⚠️ NOTAS IMPORTANTES

1. **Seção 3 e 4 não perdem perguntas**: Apenas ajustes textuais e exemplos adicionados.

2. **Seção 5 - Pergunta removida é a 5.1 (condicional)**: A seção já é opcional, então a pergunta "Houve abordagem por fundada suspeita?" é redundante.

3. **Seção 6 - Nova pergunta é CRÍTICA**: A pergunta sobre arma/ameaça é importante para tipificação do crime (Art. 40, IV - emprego de arma de fogo).

4. **Consistência**: Após TODAS as etapas, o total de perguntas será:
   - Seção 1: 7 (+1) - Art. 40 proximidade
   - Seção 2: 11 (+3) - Separar abordagem/busca
   - Seção 3: 8 (=) - Ajustes textuais
   - Seção 4: 5 (=) - Adicionar exemplos
   - Seção 5: 3 (-1) - Remover condicional
   - Seção 6: 6 (+1) - Arma/ameaça
   - Seção 7: 4 (=) - Sem alteração
   - Seção 8: 11 (+5) - Expansão completa
   - **TOTAL: 55 perguntas** (antes: 46)

5. **Validadores**:
   - Seção 5: Remover regra 5.1, renumerar 5.2→5.1, etc.
   - Seção 6: Adicionar nova regra 6.1, renumerar demais

---

**Criado em:** 30/12/2024
**Atualizado em:** 30/12/2024 (correções baseadas em SEÇÃO_*.md)
**Prioridade:** 🔧 MÉDIA
**Estimativa:** 2-3 horas
**Dependência:** Completar Etapas 1, 2 e 3 primeiro

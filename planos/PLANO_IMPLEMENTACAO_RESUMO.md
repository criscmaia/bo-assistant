# 📋 PLANO DE IMPLEMENTAÇÃO - Atualização do BO Inteligente

## Visão Geral

Este documento consolida as 4 etapas necessárias para atualizar o sistema BO Inteligente conforme os novos requisitos do especialista Claudio Moreira (prompt de 29/12/2024).

---

## 📊 RESUMO EXECUTIVO

| Etapa | Descrição | Prioridade | Tempo Est. | Impacto |
|-------|-----------|------------|------------|---------|
| 1 | Adicionar pergunta 1.7 (Art. 40) | 🚨 URGENTE | 1-2h | +1 pergunta |
| 2 | Reformular Seção 8 completa | ⚠️ IMPORTANTE | 3-4h | +5 perguntas |
| 3 | Expandir Seção 2 | 📝 MÉDIO | 2-3h | +3 perguntas |
| 4 | Ajustar Seções 3, 4, 5 e 6 | 🔧 MÉDIA | 2-3h | = (net) |
| **TOTAL** | | | **8-12h** | **+9 perguntas** |

---

## 📈 MUDANÇA NO TOTAL DE PERGUNTAS

| Seção | ATUAL | APÓS IMPLEMENTAÇÃO | Δ | Etapa |
|-------|-------|-------------------|---|-------|
| 1 - Contexto | 6 | 7 | +1 | Etapa 1 |
| 2 - Veículo | 8 | 11 | +3 | Etapa 3 |
| 3 - Campana | 8 | 8 | = | Etapa 4 (ajustes textuais) |
| 4 - Domicílio | 5 | 5 | = | Etapa 4 (adicionar exemplos) |
| 5 - Fundada Suspeita | 4 | 3 | -1 | Etapa 4 (remover 5.1) |
| 6 - Força | 5 | 6 | +1 | Etapa 4 (adicionar arma/ameaça) |
| 7 - Apreensões | 4 | 4 | = | Sem alteração |
| 8 - Condução | 6 | 11 | +5 | Etapa 2 |
| **TOTAL** | **46** | **55** | **+9** |

---

## 🎯 ETAPA 1: Pergunta 1.7 - Art. 40 (Agravantes)

**Arquivo de referência:** `ETAPA_1_PERGUNTA_1.7_ART40.md`

### Por que é urgente?
O Art. 40 da Lei 11.343/06 prevê **aumento de pena** quando o tráfico ocorre próximo a escolas, hospitais ou transportes públicos. Esta informação é **essencial** para a tipificação correta do crime.

### Arquivos a alterar:
1. `docs/index.html` - adicionar pergunta 1.7
2. `backend/state_machine.py` - QUESTIONS e STEPS
3. `backend/validator.py` - nova regra de validação
4. `backend/llm_service.py` - atualizar prompt

### Nova pergunta:
```
"O local é próximo a escola, hospital ou transporte público? 
Qual estabelecimento e a que distância aproximada?"
```

---

## 🎯 ETAPA 2: Reformular Seção 8 - Condução

**Arquivo de referência:** `ETAPA_2_REFORMULAR_SECAO_8.md`

### Por que é importante?
A Seção 8 é a que mais mudou. O novo formato detalha melhor:
- Transporte do preso
- Função no tráfico
- Vínculo com facções
- Envolvimento de menores
- Garantias constitucionais

### Arquivos a alterar:
1. `docs/index.html` - SECTION8_QUESTIONS (6→11)
2. `backend/validator_section8.py` - novas regras

### Nova estrutura (11 perguntas):
- 8.1: Voz de prisão (quem + crime)
- 8.2: Transporte do preso
- 8.3: Declaração do preso
- 8.4: Função no tráfico (vapor, gerente, etc.)
- 8.5: Antecedentes/REDS
- 8.6: Dedicação ao crime
- 8.7: Papel na facção
- 8.8: Destruição de provas/intimidação
- 8.9: Envolvimento de menores
- 8.10: Garantias constitucionais
- 8.11: Destino pessoas/materiais

---

## 🎯 ETAPA 3: Expandir Seção 2 - Veículo

**Arquivo de referência:** `ETAPA_3_EXPANDIR_SECAO_2.md`

### Por que expandir?
Separar a busca no veículo da abordagem dos ocupantes é importante para:
- Cadeia de custódia
- Individualização de responsabilidades
- Documentação legal adequada

### Arquivos a alterar:
1. `docs/index.html` - SECTION2_QUESTIONS (8→11)
2. `backend/validator_section2.py` - novas regras

### Principais adições:
- 2.8: Busca pessoal nos ocupantes (quem fez)
- 2.9: Busca no veículo (quem fez + onde)
- 2.10: O que foi encontrado + com quem + onde

---

## 🎯 ETAPA 4: Ajustar Seções 3, 4, 5 e 6

**Arquivo de referência:** `ETAPA_4_AJUSTES_SECOES_3_4_5.md`

### Por que ajustar?
Baseado na análise dos materiais `SEÇÃO_*.md`:

**Seção 3 (8→8):** Apenas ajustes textuais - MANTER todas as perguntas
**Seção 4 (5→5):** Apenas adicionar exemplos - MANTER todas as perguntas
**Seção 5 (4→3):** Remover pergunta condicional 5.1 (seção já é opcional)
**Seção 6 (5→6):** Adicionar pergunta sobre arma/ameaça (Art. 40, IV)

### Arquivos a alterar:
1. `docs/index.html` - Seções 3, 4, 5 e 6
2. `backend/validator_section3.py` - atualizar textos
3. `backend/validator_section4.py` - adicionar exemplos
4. `backend/validator_section5.py` - remover 5.1, renumerar
5. `backend/validator_section6.py` - adicionar 6.1, renumerar

### Nova pergunta 6.1:
```
"Houve ameaça ou uso de arma? Contra quem e como?"
```

---

## 🔄 ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

```
1. ETAPA 1 (1.7)       →  Commit  →  Test  →  Deploy
        ↓
2. ETAPA 2 (Seção 8)   →  Commit  →  Test  →  Deploy
        ↓
3. ETAPA 3 (Seção 2)   →  Commit  →  Test  →  Deploy
        ↓
4. ETAPA 4 (3,4,5,6)   →  Commit  →  Test  →  Deploy
```

Cada etapa deve ser implementada, testada e deployada separadamente para facilitar rollback se necessário.

---

## 📁 ARQUIVOS ENVOLVIDOS

### Frontend
- `docs/index.html` - Todas as 4 etapas

### Backend
- `backend/state_machine.py` - Etapa 1
- `backend/validator.py` - Etapa 1
- `backend/validator_section2.py` - Etapa 3
- `backend/validator_section3.py` - Etapa 4
- `backend/validator_section4.py` - Etapa 4
- `backend/validator_section5.py` - Etapa 4
- `backend/validator_section6.py` - Etapa 4 (nova pergunta 6.1)
- `backend/validator_section8.py` - Etapa 2
- `backend/llm_service.py` - Etapas 1 e 2

### Testes
- `tests/unit/test_validator.py` - Etapa 1
- `tests/unit/test_validator_section2.py` - Etapa 3
- `tests/unit/test_validator_section6.py` - Etapa 4
- `tests/unit/test_validator_section8.py` - Etapa 2
- Outros testes conforme necessário

---

## ⚠️ BREAKING CHANGES

1. **Seção 8**: Muda completamente de 6 para 11 perguntas. BOs em andamento na Seção 8 podem ser afetados.

2. **Seção 5**: Renumeração - 5.2→5.1, 5.3→5.2, 5.4→5.3. Drafts salvos podem ter numeração antiga.

3. **Seção 6**: Renumeração - todas as perguntas avançam 1 número após nova 6.1.

4. **Validação**: Novas regras podem rejeitar respostas que antes eram aceitas.

---

## 🧪 ESTRATÉGIA DE TESTES

### Por Etapa
1. Testes unitários para cada validador alterado
2. Teste de fluxo completo da seção modificada
3. Teste de integração com geração de texto

### Pré-Deploy
1. Testar localmente todas as 8 seções
2. Verificar CI passou
3. Testar em staging se disponível

### Pós-Deploy
1. Criar um BO completo em produção
2. Verificar logs de erros
3. Monitorar feedbacks negativos

---

## 📚 DOCUMENTOS DE REFERÊNCIA

- `ETAPA_1_PERGUNTA_1.7_ART40.md` - Detalhes da Etapa 1
- `ETAPA_2_REFORMULAR_SECAO_8.md` - Detalhes da Etapa 2
- `ETAPA_3_EXPANDIR_SECAO_2.md` - Detalhes da Etapa 3
- `ETAPA_4_AJUSTES_SECOES_3_4_5.md` - Detalhes da Etapa 4

---

## 📞 CONTATO PARA DÚVIDAS

- **Domínio/Requisitos**: Claudio Moreira (Sgt. PM)
- **Técnico**: Cristiano Maia (Tech Lead)

---

**Criado em:** 30/12/2024
**Atualizado em:** 30/12/2024 (correções baseadas em SEÇÃO_*.md)
**Versão do Plano:** 2.0
**Status:** Pronto para implementação

## 📝 HISTÓRICO DE ALTERAÇÕES

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | 30/12/2024 | Versão inicial |
| 2.0 | 30/12/2024 | Correções após análise de materiais SEÇÃO_*.md |

### Correções da v2.0:
- Seção 3: 8→7 corrigido para 8→8 (manter todas)
- Seção 4: 5→4 corrigido para 5→5 (manter todas)
- Seção 5: remover 5.4 corrigido para remover 5.1 (condicional)
- Seção 6: adicionada alteração 5→6 (nova pergunta arma/ameaça)
- Seção 8: 6→12 corrigido para 6→11
- Total: 46→53 corrigido para 46→55

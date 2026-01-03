# TESTE_COMPLETO_E2E.py - Teste Definitivo

**Data de criação:** 03/01/2026
**Versão:** v0.13.2
**Status:** ✅ Pronto para execução

---

## 📋 O Que É

O **TESTE_COMPLETO_E2E.py** é o teste automatizado mais completo do BO Inteligente, validando:

1. ✅ **DraftModal** (restauração de rascunho após 3 respostas)
2. ✅ **Tooltips** (100% visíveis em todas as 4 bolinhas)
3. ✅ **Navegação bidirecional** (1↔2↔3 com persistência)
4. ✅ **Texto Groq vs Placeholder** (valida em CADA seção)
5. ✅ **Bolinha BO Final** (transição locked→completed)
6. ✅ **Modal de Confirmação** (customizado, não native)
7. ✅ **Follow-ups condicionais** (1.5=NÃO, 1.9=SIM)
8. ✅ **Skip de seção** (S2 pulada com texto Groq)
9. ✅ **Tela Final** (estrutura completa com 2 seções)

---

## 🎯 Por Que Este Teste É Diferente

| Aspecto | Testes Anteriores | TESTE_COMPLETO_E2E.py |
|---------|-------------------|------------------------|
| **DraftModal** | Não testava restauração | ✅ Testa após 3 respostas + F5 |
| **Tooltips** | Não validava posição | ✅ 100% visíveis (bbox completo) |
| **Navegação** | Linear (1→2→3) | ✅ Bidirecional (1↔2↔3) |
| **Texto Groq** | Validava no final | ✅ Valida em CADA seção |
| **Follow-ups** | Não validava lógica | ✅ Valida condições (NÃO/SIM) |
| **Bolinha Final** | Apenas locked | ✅ Transição locked→completed |
| **Modal** | window.confirm | ✅ Modal customizado |

---

## 🚀 Como Executar

### Pré-requisitos

```bash
pip install playwright
playwright install chromium
```

### Iniciar Servidores

**Terminal 1 - Frontend:**
```bash
cd c:\AI\bo-assistant\docs
python -m http.server 3000 --bind 127.0.0.1
```

**Terminal 2 - Backend:**
```bash
cd c:\AI\bo-assistant
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Executar Teste

```bash
python tests/manual/TESTE_COMPLETO_E2E.py
```

**Tempo estimado:** 2-3 minutos (incluindo esperas do Groq)

---

## 📊 Fluxo do Teste (9 Fases)

### Fase 1: Rascunho (DraftModal)
```
1. Responder 3 perguntas (1.1, 1.2, 1.3)
2. F5 (reload)
3. Validar que DraftModal aparece
4. Preview mostra "Seção 1: 3/? perguntas"
5. Clicar "Continuar" → Respostas restauradas
```
**Valida:** DraftModal funciona corretamente

---

### Fase 2: Completar Seção 1 (Follow-ups)
```
6. Responder 1.4
7. Responder 1.5 = "NÃO"
   → Validar que follow-ups 1.5.1/1.5.2 NÃO aparecem ✅
8. Responder 1.6, 1.7, 1.8
9. Responder 1.9 = "SIM"
   → Validar que follow-ups 1.9.1/1.9.2 APARECEM ✅
10. Responder 1.9.1, 1.9.2
11. Aguardar texto gerado (até 60s)
12. CRÍTICO: Validar texto renderizado === texto Groq (não placeholder)
```
**Valida:** Follow-ups condicionais + texto Groq na S1

---

### Fase 3: Tooltips (100% Visíveis)
```
13. Hover na bolinha Seção 1 → Validar bbox dentro viewport
14. Hover na bolinha Seção 2 → Validar bbox dentro viewport
15. Hover na bolinha Seção 3 → Validar bbox dentro viewport
16. Hover na bolinha BO Final → Validar bbox dentro viewport
17. Para cada tooltip:
    - bbox['y'] >= 0 (não sai pelo topo)
    - bbox['x'] >= 0 (não sai pela esquerda)
    - bbox['bottom'] <= viewport.height
    - bbox['right'] <= viewport.width
    - Classe CSS: --top OU --bottom
```
**Valida:** Tooltips 100% visíveis (correção Tarefa 3)

---

### Fase 4: Pular Seção 2 (Skip)
```
18. Clicar "Próxima Seção"
19. Clicar botão "Não havia veículo" (skip S2)
20. Aguardar texto de skip (até 30s)
21. CRÍTICO: Validar texto skip === texto Groq (não placeholder)
22. Validar bolinha S2 amarela (skipped)
```
**Valida:** Skip funciona + texto Groq no skip

---

### Fase 5: Seção 3 Parcial
```
23. Clicar "Próxima Seção"
24. Responder 3.2, 3.3, 3.4, 3.5
25. NÃO completar (parar antes da última pergunta)
```
**Valida:** Seção pode ficar em in_progress

---

### Fase 6: Navegação com Persistência
```
26. Clicar bolinha "Seção 1"
27. Validar:
    - Título mostra "Seção 1"
    - Texto gerado ainda está renderizado
    - Estado no localStorage: 'completed'
28. Clicar bolinha "Seção 2"
29. Validar:
    - Título mostra "Seção 2"
    - Texto de skip renderizado
    - Estado no localStorage: 'skipped'
30. Clicar bolinha "Seção 3"
31. Validar:
    - Título mostra "Seção 3"
    - Respostas 3.2-3.5 preservadas no localStorage
    - Estado no localStorage: 'in_progress'
```
**Valida:** Navegação bidirecional preserva dados

---

### Fase 7: Completar Seção 3
```
32. Responder 3.6 = "SIM", 3.6.1
33. Aguardar texto gerado (até 60s)
34. CRÍTICO: Validar texto renderizado === texto Groq (não placeholder)
```
**Valida:** Texto Groq na S3

---

### Fase 8: Bolinha BO Final (Transição)
```
35. Após completar todas as seções, validar:
    - Bolinha mudou de LOCKED → COMPLETED
    - Cor: verde #10b981
    - Ícone: ✓ (checkmark, não mais 🔒)
    - Cursor: pointer (não mais not-allowed)
    - Linha de conexão: 100% preenchida (verde)
36. Clicar na bolinha BO Final
37. Validar que navegou para FinalScreen
```
**Valida:** Bolinha BO Final (Tarefa 1)

---

### Fase 9: Tela Final + Modal
```
38. Validar estrutura:
    - 2 caixas de seção (S1 e S3) - S2 foi pulada
    - Botão "Copiar Seção 1"
    - Botão "Copiar Seção 3"
    - Botão "Copiar BO Completo (2 Seções)"
    - Botão "Iniciar Novo BO"
39. Clicar "Iniciar Novo BO"
40. Validar modal customizado (não window.confirm)
41. Clicar "Cancelar" → Modal fecha, nada acontece
42. Clicar "Iniciar Novo BO" novamente
43. Clicar "Confirmar" → localStorage limpo, volta para Seção 1
```
**Valida:** Modal de Confirmação (Tarefa 2)

---

## 📸 Screenshots Automáticos

O teste captura 9 screenshots em `docs/screenshots/e2e/`:

1. **01-draft-modal.png** - DraftModal com preview de 3 respostas
2. **02-s1-completed.png** - Seção 1 completa com texto Groq
3. **03-tooltips.png** - Tooltips 100% visíveis
4. **04-s2-skipped.png** - Seção 2 pulada (bolinha amarela)
5. **05-s3-parcial.png** - Seção 3 parcial (in_progress)
6. **06-s3-completed.png** - Seção 3 completa
7. **07-bolinha-final-completed.png** - Bolinha BO Final verde com ✓
8. **08-final-screen.png** - Tela Final (2 seções)
9. **09-modal-confirmacao.png** - Modal de confirmação customizado

---

## ✅ Critério de Sucesso

**TESTE PASSA (0 erros) SE:**
- ✅ DraftModal aparece e restaura corretamente
- ✅ Todos os tooltips 100% visíveis (bbox válido)
- ✅ Texto Groq renderizado em TODAS as seções (S1, S2 skip, S3)
- ✅ Navegação preserva estado e respostas
- ✅ Follow-ups aparecem/não aparecem conforme lógica
- ✅ Bolinha BO Final muda para completed
- ✅ Modal customizado aparece e funciona

**TESTE FALHA SE:**
- ❌ Qualquer tooltip fora do viewport (y < 0)
- ❌ Texto placeholder detectado em qualquer seção
- ❌ Navegação perde dados (respostas desaparecem)
- ❌ Bolinha BO Final não muda para completed
- ❌ Modal não aparece ou não funciona

---

## 📊 Relatório Gerado

Após execução, o teste gera automaticamente:

**Arquivo:** `RELATORIO_TESTE_E2E.md`

**Conteúdo:**
- Data e hora de execução
- Tempo total (segundos)
- Número de erros encontrados
- Número de requests Groq (esperado: 3+)
- Número de erros no console JavaScript
- Lista de fases executadas (9)
- Lista de screenshots capturados (9)
- Log completo timestampado

---

## 🐛 Detecção de Bugs

O teste detecta automaticamente:

### 1. Placeholders Genéricos (Bug Crítico)
```python
placeholders_invalidos = [
    "[Texto será gerado",
    "quando integração estiver completa",
    "API não disponível"
]
```
Se detectado → ❌ ERRO: Groq não gerou texto

### 2. Tooltips Fora do Viewport
```python
if bbox['y'] < 0:  # Saiu pelo topo
if bbox['x'] < 0:  # Saiu pela esquerda
if bbox['bottom'] > viewport.height:  # Saiu por baixo
if bbox['right'] > viewport.width:  # Saiu pela direita
```

### 3. Perda de Dados na Navegação
```python
# Verifica localStorage após clicar em bolinha
estado_storage = localStorage.getItem('bo_state')
if estado !== esperado → ❌ ERRO
```

### 4. Erros no Console JavaScript
```python
page.on('console', lambda msg:
    console_errors.append(msg.text) if msg.type == 'error'
)
```

---

## 💡 Diferenças vs TESTE_FINAL_3_SECOES.py

| Funcionalidade | TESTE_FINAL_3_SECOES.py | TESTE_COMPLETO_E2E.py |
|----------------|--------------------------|------------------------|
| **DraftModal** | ❌ Não testa | ✅ Testa restauração |
| **Tooltips** | ❌ Não valida posição | ✅ 100% visíveis |
| **Navegação** | ❌ Linear (1→2→3) | ✅ Bidirecional (1↔2↔3) |
| **Texto Groq** | ⚠️ Só no final | ✅ Em cada seção |
| **Follow-ups** | ⚠️ Responde mas não valida | ✅ Valida lógica |
| **Persistência** | ❌ Não testa | ✅ Valida localStorage |
| **Console Errors** | ❌ Não captura | ✅ Captura e reporta |
| **Screenshots** | 4 capturas | 9 capturas |
| **Tempo** | ~90s | ~2-3min |

---

## 🎯 Quando Usar Este Teste

### ✅ USE ESTE TESTE QUANDO:
- Validar todas as 4 melhorias implementadas (v0.13.2)
- Testar fluxo completo end-to-end
- Validar correções de bugs (tooltip, DraftModal, Groq)
- Fazer smoke test após deploy
- Verificar regressões após mudanças

### ⚠️ USE OUTRO TESTE SE:
- **Teste rápido** (8s): Use `TESTE_MELHORIAS_RAPIDO.py`
- **Apenas DraftModal** (20s): Use `TESTE_DRAFT_MODAL.py`
- **Skip de seção específico**: Use `TESTE_FINAL_SKIP_SECAO2.py`

---

## 🔧 Troubleshooting

### Problema: "Connection Refused" ao executar
**Solução:** Verificar que ambos os servidores estão rodando:
```bash
# Terminal 1
cd c:\AI\bo-assistant\docs
python -m http.server 3000

# Terminal 2
cd c:\AI\bo-assistant
python -m uvicorn backend.main:app --port 8000
```

### Problema: Timeout aguardando texto Groq
**Possíveis causas:**
1. Backend não está rodando
2. API key do Groq inválida ou expirada
3. Rede lenta (aumentar timeout de 60s para 120s)

**Debug:**
```python
# Em TESTE_COMPLETO_E2E.py, adicionar:
print(f"Groq requests: {self.groq_requests}")
print(f"Console errors: {self.console_errors}")
```

### Problema: "Modal não apareceu"
**Causa comum:** Mudança nos seletores CSS
**Solução:** Verificar classes atuais:
```javascript
// No navegador, abrir DevTools e executar:
document.querySelector('.draft-modal-overlay')
document.querySelector('.confirmation-modal')
```

---

## 📝 Manutenção Futura

### Se adicionar nova seção (ex: Seção 4):
1. Adicionar dados em `S4_COMPLETO = {...}`
2. Adicionar fase: `await self.fase10_secao4(pg)`
3. Validar texto Groq na nova seção
4. Atualizar screenshots (adicionar `10-s4-completed.png`)

### Se mudar estrutura de perguntas:
1. Atualizar dicionários `S1_COMPLETO`, `S3_COMPLETO`
2. Ajustar validações de follow-ups se necessário

### Se mudar seletores CSS:
1. Buscar por `query_selector()` no código
2. Atualizar seletores antigos para novos
3. Testar localmente antes de commit

---

## 🎉 Conclusão

O **TESTE_COMPLETO_E2E.py** é o teste mais completo e robusto do BO Inteligente, validando:

- ✅ **DraftModal** (Tarefa 4)
- ✅ **Tooltip Inteligente** (Tarefa 3)
- ✅ **Modal de Confirmação** (Tarefa 2)
- ✅ **Bolinha BO Final** (Tarefa 1)
- ✅ **Texto Groq** (Bug crítico corrigido)
- ✅ **Navegação Bidirecional** (Funcionalidade core)
- ✅ **Follow-ups Condicionais** (Lógica de negócio)

**Resultado esperado:** ✅ 0 erros em 2-3 minutos

Se este teste passa, o sistema está **100% funcional** e pronto para produção! 🚀

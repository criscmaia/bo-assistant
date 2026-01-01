# 🛟 Recovery Guide - BO Inteligente

**Versão Estável Atual:** v0.12.14-button-restore-fix
**Versão Anterior:** v0.12.13-draft-fixes
**Branch:** feature/ux-redesign-v1
**Data:** 2026-01-01
**Último Commit:** bec8fe8

---

## 🎯 Estado Atual Protegido

Esta versão contém **TODAS** as funcionalidades UX implementadas e validadas + **TODOS os bugs críticos corrigidos**:

✅ Modal customizado de rascunho
✅ Mensagens de erro acima do input
✅ Números das perguntas (1.1), 1.2), etc)
✅ Texto específico nos botões por contexto
✅ Prefill de data/hora na pergunta 1.1
✅ Input clearing híbrido
✅ Auto-skip da pergunta x.1
✅ Validações rigorosas de keywords
✅ Seção 1 com 11 perguntas corretas do TESTING.md (13 com condicionais)
✅ Seção 2 com 13 perguntas corretas do TESTING.md
✅ **Perguntas condicionais (follow-ups) funcionando** 🆕
✅ **Restauração de rascunho com input e próxima pergunta** 🆕
✅ **Auto-save sem perder última resposta** 🆕
✅ **Botões (single_choice) com follow-ups restauram corretamente** 🆕

---

## 🚨 Como Restaurar Se Algo Der Errado

### Opção 1: Restaurar Via Tag (Recomendado)

```bash
# Descartar mudanças não commitadas
git reset --hard

# Voltar para a tag estável MAIS RECENTE (recomendado)
git checkout v0.12.14-button-restore-fix

# OU voltar para tags anteriores
git checkout v0.12.13-draft-fixes
git checkout v0.12.12-conditional-questions-fix
git checkout v0.12.11-sections-1-2-complete

# Se quiser criar uma branch a partir da tag
git checkout -b recovery-from-tag v0.12.14-button-restore-fix
```

### Opção 2: Restaurar Via Commit Hash

```bash
# Voltar para o último commit bom (MAIS RECENTE)
git reset --hard bec8fe8

# OU voltar para commits anteriores
git reset --hard 1adcae7  # Auto-save timing fix
git reset --hard d9732db  # Draft restoration fix
git reset --hard 47f8962  # Conditional questions fix
git reset --hard 295b133  # Section 1 fix
git reset --hard 352f498  # Section 2 fix

# Ou criar branch a partir dele
git checkout -b recovery-from-commit bec8fe8
```

### Opção 3: Recuperar Arquivos Específicos

```bash
# Recuperar um arquivo específico da tag MAIS RECENTE
git checkout v0.12.14-button-restore-fix -- docs/js/components/SectionContainer.js

# Recuperar múltiplos arquivos
git checkout v0.12.14-button-restore-fix -- docs/js/components/TextInput.js docs/js/components/SectionContainer.js docs/js/data/sections.js

# OU recuperar de tags anteriores
git checkout v0.12.13-draft-fixes -- docs/js/components/SectionContainer.js
git checkout v0.12.11-sections-1-2-complete -- docs/js/data/sections.js
```

### Opção 4: Recuperar Backups do Stash

```bash
# Listar stashes
git stash list

# Aplicar o stash de backup (sem remover)
git stash apply stash@{0}

# Ou aplicar e remover
git stash pop stash@{0}
```

---

## 📦 Commits Importantes

| Hash | Descrição | Importância |
|------|-----------|-------------|
| `bec8fe8` | Fix button restore com follow-ups | 🔴 CRÍTICO |
| `1adcae7` | Fix auto-save timing (sem perder dados) | 🔴 CRÍTICO |
| `d9732db` | Fix draft restore mostrar input | 🔴 CRÍTICO |
| `47f8962` | Fix perguntas condicionais (follow-ups) | 🔴 CRÍTICO |
| `295b133` | Restaura Seção 1 completa | 🔴 CRÍTICO |
| `352f498` | Restaura Seção 2 completa | 🔴 CRÍTICO |
| `b7250fa` | Validação rigorosa 1.2 | 🔴 CRÍTICO |
| `ca4d3cb` | Todas validações UX | 🔴 CRÍTICO |
| `df6cf99` | Modal customizado | 🟡 IMPORTANTE |
| `5f25e52` | Auto-skip x.1 | 🟡 IMPORTANTE |
| `ebc9a08` | Números das perguntas | 🟢 FEATURE |
| `419fce1` | Botões por contexto | 🟢 FEATURE |

---

## 🔍 Verificar Estado Atual

```bash
# Ver branch atual e último commit
git log --oneline -5

# Ver status das mudanças
git status

# Ver tags disponíveis
git tag -l

# Ver informações da tag (mais recente)
git show v0.12.11-sections-1-2-complete

# Ver informações da tag anterior
git show v0.12.10-ux-complete
```

---

## ⚠️ NUNCA Faça Isso

❌ **NUNCA** use `git checkout -- .` sem ter certeza
❌ **NUNCA** use `git reset --hard` sem backup
❌ **NUNCA** force push para main/master
❌ **NUNCA** delete as tags v0.12.14-button-restore-fix, v0.12.13-draft-fixes, v0.12.12-conditional-questions-fix

---

## ✅ Sempre Faça Isso Antes de Mudanças Grandes

```bash
# 1. Commit tudo primeiro
git add .
git commit -m "WIP: salvando trabalho antes de mudança"

# 2. Criar branch de backup
git branch backup-$(date +%Y%m%d-%H%M%S)

# 3. Verificar que está tudo commitado
git status

# 4. Agora pode fazer a mudança arriscada
```

---

## 📞 Em Caso de Emergência

Se você perdeu algo e não sabe como recuperar:

1. **NÃO ENTRE EM PÂNICO**
2. **NÃO FAÇA MAIS NADA** (não commite, não resete, não delete)
3. Use `git reflog` para ver TUDO que foi feito
4. Procure o commit certo no reflog
5. Restaure com `git checkout <hash>`

```bash
# Ver histórico completo de TUDO
git reflog

# Encontrar o commit que você quer
git reflog | grep "commit message"

# Voltar para ele
git checkout <hash-do-reflog>
```

---

## 🎯 Status dos Arquivos Críticos

| Arquivo | Status | Validado |
|---------|--------|----------|
| `docs/js/data/sections.js` | ✅ Seções 1 e 2 corretas (TESTING.md) | SIM |
| `docs/js/components/TextInput.js` | ✅ Todas validações | SIM |
| `docs/js/components/SectionContainer.js` | ✅ Auto-skip + prefill | SIM |
| `docs/js/components/DraftModal.js` | ✅ Modal customizado | SIM |
| `docs/js/BOApp.js` | ✅ Integração completa | SIM |
| `docs/css/inputs.css` | ✅ Error acima + animação | SIM |
| `docs/css/draft-modal.css` | ✅ Estilos do modal | SIM |
| `STATUS-FINAL-v0.12.11.md` | ✅ Documento de status completo | SIM |

---

## 📚 Links Úteis

- **Tag Atual no GitHub:** https://github.com/criscmaia/bo-assistant/releases/tag/v0.12.14-button-restore-fix
- **Tags Anteriores:**
  - v0.12.13-draft-fixes: https://github.com/criscmaia/bo-assistant/releases/tag/v0.12.13-draft-fixes
  - v0.12.12-conditional-questions-fix: https://github.com/criscmaia/bo-assistant/releases/tag/v0.12.12-conditional-questions-fix
  - v0.12.11-sections-1-2-complete: https://github.com/criscmaia/bo-assistant/releases/tag/v0.12.11-sections-1-2-complete
- **Branch:** https://github.com/criscmaia/bo-assistant/tree/feature/ux-redesign-v1
- **Último Commit:** https://github.com/criscmaia/bo-assistant/commit/bec8fe8
- **Status Final:** STATUS-FINAL-v0.12.14.md

---

**Criado em:** 2026-01-01
**Por:** Claude Code
**Versão do Guia:** 1.1 (atualizado)

# Claude Code: Guia Completo

**Versão**: 3.0
**Última Atualização**: 2 de janeiro de 2026

Este documento unifica todas as informações sobre uso do Claude Code no projeto BO Inteligente, incluindo comandos customizados, otimização de custos e workflow recomendado.

---

## 📋 Índice

1. [Modelos e Custos](#-modelos-e-custos)
2. [Configuração](#-configuração)
3. [Alternando Modelos](#-alternando-modelos)
4. [Estratégia de Uso](#-estratégia-de-uso)
5. [Workflow Recomendado](#-workflow-recomendado)
6. [Comandos Customizados](#-comandos-customizados)
7. [Referências](#-referências)

---

## 💰 Modelos e Custos

### Modelos Disponíveis

| Modelo | Nome Completo | Input/MTok | Output/MTok | Velocidade |
|--------|---------------|------------|-------------|------------|
| **Haiku 4.5** | `claude-haiku-4-5-20251001` | $1.00 | $5.00 | Mais rápido |
| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | $3.00 | $15.00 | Balanceado |
| **Opus 4.5** | `claude-opus-4-5-20251101` | $5.00 | $25.00 | Mais capaz |

> **Fonte**: https://claude.com/pricing#api

### Estimativa de Economia

**Distribuição Recomendada:**

| Modelo | % do Uso | Tipos de Tarefa |
|--------|----------|-----------------|
| Haiku 4.5 | 60% | Exploração, git, implementações simples |
| Sonnet 4.5 | 35% | Planejamento, review, implementações complexas |
| Opus 4.5 | 5% | Arquitetura, debugging crítico |

**Comparação de Custos (10M tokens/dia):**

| Estratégia | Custo Diário | Custo Mensal |
|------------|--------------|--------------|
| 100% Sonnet 4.5 | ~$78 | ~$2,340 |
| 100% Haiku 4.5 | ~$26 | ~$780 |
| Mix 60/35/5 | ~$42 | ~$1,260 |

**Economia com estratégia híbrida**: ~45% comparado a 100% Sonnet

---

## ⚙️ Configuração

### Estrutura de Arquivos

```
bo-assistant/
├── .claude/
│   ├── settings.json           ← Compartilhado com equipe (git)
│   ├── settings.local.json     ← Configurações pessoais (ignorado pelo git)
│   ├── COMMIT_GUIDELINES.md    ← Padrões de commit
│   └── commands/               ← Comandos customizados (ver seção abaixo)
│       ├── test-local.sh
│       ├── fix-issue.md
│       └── validate-docs.md
└── ...
```

### Arquivo de Configuração Recomendado

Crie o arquivo `.claude/settings.local.json` no seu projeto:

```json
{
  "model": "claude-haiku-4-5-20251001",
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(pip install:*)",
      "Bash(git checkout:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git pull:*)",
      "Bash(git branch:*)",
      "Bash(python -m uvicorn:*)",
      "Bash(curl:*)",
      "Bash(ls:*)",
      "Bash(cat:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

> **Importante**: Use sempre o **nome completo do modelo** (ex: `claude-haiku-4-5-20251001`), não aliases.

### Hierarquia de Configuração

As configurações são aplicadas nesta ordem de prioridade (maior para menor):

1. **Enterprise Managed Policies** - Políticas corporativas
2. **Argumentos de linha de comando** - `claude --model opus`
3. **Local Project Settings** - `.claude/settings.local.json`
4. **Shared Project Settings** - `.claude/settings.json`
5. **User Settings** - `~/.claude/settings.json`

### Por que .claude está no .gitignore?

A pasta `.claude/` contém:
- **settings.json**: Configurações locais do Claude Code (pode conter dados sensíveis)
- **commands/**: Scripts e comandos customizados locais
- **estado local**: Cache, histórico, etc.

Por isso é recomendado manter no `.gitignore` e fazer o setup manual em cada clone do repositório.

---

## 🔄 Alternando Modelos

### Importante: Extensão VS Code vs CLI

A extensão VS Code do Claude Code **não tem paridade completa com o CLI**. Muitos comandos slash como `/status`, `/model`, `/help` e `/rewind` **não funcionam na extensão** - apenas no terminal.

### Método 1: Via Terminal Integrado (Recomendado para comandos slash)

1. Abra o terminal integrado do VS Code: `Ctrl + `` (backtick)
2. Execute `claude`
3. Use os comandos normalmente:

```
/model haiku     → Muda para Haiku 4.5
/model sonnet    → Muda para Sonnet 4.5
/model opus      → Muda para Opus 4.5
/status          → Verifica modelo atual
```

### Método 2: Via Arquivo de Configuração (Funciona na Extensão)

A forma mais confiável na extensão VS Code é usar o arquivo `.claude/settings.local.json`:

```json
{
  "model": "claude-haiku-4-5-20251001"
}
```

Após salvar, reinicie a extensão ou abra uma nova conversa.

### Método 3: Linha de Comando

Ao iniciar uma nova sessão no terminal:

```bash
claude --model haiku
claude --model sonnet
claude --model opus
```

### Método 4: Variáveis de Ambiente

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
claude
```

**Linux/Mac:**
```bash
export ANTHROPIC_MODEL="claude-haiku-4-5-20251001"
claude
```

### Verificação da Configuração

**Na Extensão VS Code:**

Como `/status` não funciona na extensão, use uma destas alternativas:

- **Pergunte diretamente ao Claude**: "Qual modelo você está usando agora?"
- **Verifique o arquivo de configuração**: O modelo definido em `.claude/settings.local.json` será usado automaticamente

**No Terminal (CLI):**

```
/status
```

O output mostrará qual modelo está em uso.

---

## 🎯 Estratégia de Uso

### Haiku 4.5 — Tarefas Simples e Repetitivas

**Custo**: ~$2.60/MTok (média input+output)

**Usar para:**
- Comandos git (status, add, commit, push, pull)
- Leitura de arquivos
- Buscas com grep e glob
- Operações de arquivo (criar, mover, renomear)
- Validação de testes simples
- Implementações com requisitos completamente claros

**Justificativa**: Haiku 4.5 oferece desempenho próximo ao Sonnet para tarefas bem definidas, com custo 67% menor e velocidade 4-5x maior.

### Sonnet 4.5 — Tarefas de Complexidade Moderada

**Custo**: ~$7.80/MTok (média input+output)

**Usar para:**
- Code review e análise de código
- Refatoração de médio porte
- Planejamento de implementação
- Implementações com lógica de negócio
- Debugging de issues conhecidas
- Tarefas multi-etapas com contexto

**Justificativa**: Sonnet 4.5 é o modelo mais equilibrado, oferecendo excelente raciocínio e capacidade de código a um custo moderado. É o padrão recomendado para desenvolvimento geral.

### Opus 4.5 — Tarefas Críticas e Complexas

**Custo**: ~$12.00/MTok (média input+output)

**Usar para:**
- Design de arquitetura de sistemas
- Debugging de bugs obscuros ou críticos
- Decisões de trade-offs técnicos importantes
- Análise de segurança
- Refatorações massivas de codebase
- Problemas que Sonnet não conseguiu resolver

**Justificativa**: Opus 4.5 é o modelo mais inteligente, capaz de raciocínio profundo e análise de sistemas complexos. Reserve para situações onde a qualidade máxima justifica o custo adicional.

---

## 🚀 Workflow Recomendado

### Cenário 1: Implementar Nova Feature

```
1. EXPLORAÇÃO (Haiku)
   /model haiku
   "Leia os arquivos relacionados à feature X"
   Custo estimado: $0.02-0.05

2. PLANEJAMENTO (Sonnet)
   /model sonnet
   "Planeje a implementação baseado na arquitetura existente"
   Custo estimado: $0.10-0.30

3. IMPLEMENTAÇÃO (Haiku)
   /model haiku
   "Implemente seguindo o plano definido"
   Custo estimado: $0.05-0.15

4. REVIEW (Sonnet)
   /model sonnet
   "Revise o código para edge cases e melhorias"
   Custo estimado: $0.05-0.15

5. GIT (Haiku)
   /model haiku
   "Commit e push das mudanças"
   Custo estimado: $0.01

TOTAL: ~$0.25-0.65
```

### Cenário 2: Debugging Crítico

```
1. COLETA DE INFORMAÇÕES (Haiku)
   /model haiku
   "Mostre os logs e código relacionado ao bug"
   Custo estimado: $0.02-0.05

2. ANÁLISE (Sonnet)
   /model sonnet
   "Analise o problema e identifique a causa raiz"
   Custo estimado: $0.10-0.30

3. SE NECESSÁRIO - ANÁLISE PROFUNDA (Opus)
   /model opus
   "O problema persiste. Faça uma análise completa do sistema"
   Custo estimado: $0.20-0.50

4. CORREÇÃO (Haiku ou Sonnet)
   Dependendo da complexidade da solução identificada
```

---

## 🛠️ Comandos Customizados

Este projeto possui 3 comandos customizados configurados via Claude Code skills.

### `/test-local` - Mover Issue para Teste Local

Move uma issue do GitHub para a coluna "Teste Local" no Kanban automaticamente.

**Setup:**

1. Crie a pasta de comandos:
```bash
mkdir -p .claude/commands
```

2. Crie o arquivo `.claude/commands/test-local.sh`:
```bash
#!/bin/bash
# Move issue to "Teste Local" column in Kanban

if [ -z "$1" ]; then
    echo "❌ Erro: Número da issue é obrigatório"
    echo "Uso: /test-local <numero>"
    exit 1
fi

ISSUE_NUMBER=$1

echo "🔍 Procurando issue #$ISSUE_NUMBER..."

# Passo 1: Encontrar o Item ID
ITEM_ID=$(gh project item-list 1 --owner criscmaia --format json | \
    jq -r ".items[] | select(.content.number==$ISSUE_NUMBER) | .id" | \
    head -1)

if [ -z "$ITEM_ID" ]; then
    echo "❌ Issue #$ISSUE_NUMBER não encontrada no Kanban"
    exit 1
fi

echo "✅ Item ID encontrado: $ITEM_ID"

# Passo 2: Mover para "Teste Local"
echo "📋 Movendo para coluna 'Teste Local'..."

gh project item-edit \
    --project-id PVT_kwHOAIpvJs4BLOCq \
    --id "$ITEM_ID" \
    --field-id PVTSSF_lAHOAIpvJs4BLOCqzg62_Ms \
    --single-select-option-id f19d663f

if [ $? -eq 0 ]; then
    echo "✅ Issue #$ISSUE_NUMBER movida para 'Teste Local' com sucesso!"
else
    echo "❌ Erro ao mover issue"
    exit 1
fi
```

3. Torne o script executável:
```bash
chmod +x .claude/commands/test-local.sh
```

4. Configure o hook no `.claude/settings.json`:
```json
{
    "hooks": {
        "UserPromptSubmit": [
            {
                "matcher": "/test-local",
                "hooks": [
                    {
                        "type": "command",
                        "command": "bash .claude/commands/test-local.sh $ARGUMENTS",
                        "statusMessage": "🧪 Movendo issue para Teste Local..."
                    }
                ]
            }
        ]
    }
}
```

**Uso:**
```
/test-local 5
```

Isso move a issue #5 para a coluna "Teste Local" no Kanban.

### `/fix-issue` - Ler e Corrigir Bugs da Issue

Lê uma issue do GitHub Projects e corrige os bugs descritos nela.

**Uso:**
```
/fix-issue 7
```

Lê a issue #7 e implementa as correções necessárias.

### `/validate-docs` - Validar Consistência de Versão

Valida se todos os documentos do projeto estão com a versão correta e consistente.

**Uso:**
```
/validate-docs
```

Verifica todos os arquivos `.md` e reporta inconsistências de versão.

---

## 📚 Referências

### Documentação Oficial

- **Documentação Claude Code**: https://code.claude.com/docs/en/settings
- **Preços API**: https://claude.com/pricing#api
- **Configuração de Modelos**: https://docs.claude.com/en/docs/claude-code/model-config
- **Help Center**: https://support.claude.com/en/articles/11940350-claude-code-model-configuration

### Documentação Interna

- [COMMIT_GUIDELINES.md](../.claude/COMMIT_GUIDELINES.md) - Padrões de commit do projeto
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Guia de desenvolvimento
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitetura técnica

---

**Última atualização:** 2 de janeiro de 2026
**Versão do projeto:** v0.13.0

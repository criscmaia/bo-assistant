# Configuração do Claude Code

Guia de setup para comandos customizados e configurações do Claude Code.

## Comandos Customizados

### /test-local - Mover Issue para Teste Local

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
    "permissions": {
        "deny": [
            "Read(./.env)",
            "Read(./secrets/**)"
        ]
    },
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

---

## Por que .claude está no .gitignore?

A pasta `.claude/` contém:
- **settings.json**: Configurações locais do Claude Code (pode conter dados sensíveis)
- **commands/**: Scripts e comandos customizados locais
- **estado local**: Cache, histórico, etc.

Por isso é recomendado manter no `.gitignore` e fazer o setup manual em cada clone do repositório.

## Próximos Comandos

Se precisar de mais comandos customizados, crie arquivos em `.claude/commands/` e registre os hooks no `.claude/settings.json`.

Exemplos de hooks possíveis:
- `/fix-issue` - Ler issue do GitHub
- `/test-e2e` - Rodar testes E2E
- `/deploy` - Deploy manual para staging

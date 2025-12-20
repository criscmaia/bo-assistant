# 🛡️ Configuração do ggshield

## Status Atual

✅ **ggshield instalado:** v1.45.0 (via pipx)
✅ **Pre-commit hook:** Ativo e funcionando
✅ **GitHub Actions:** Configurado ([security-scan.yml](workflows/security-scan.yml))
✅ **Autenticação:** Configurada

---

## Instalação Atual (pipx)

O ggshield foi instalado via **pipx**, que é a forma recomendada:

```bash
py -m pip install --user pipx
py -m pipx ensurepath
py -m pipx install ggshield
ggshield auth login
```

**Localização:** `C:\Users\user\.local\bin\ggshield.exe`

### Pre-commit Hook Configurado

O hook está em `.git/hooks/pre-commit` e usa o caminho absoluto para o ggshield:

```bash
/c/Users/user/.local/bin/ggshield.exe secret scan pre-commit
```

**Funciona automaticamente!** Escaneia cada commit antes de permitir.

---

## Comandos Úteis

### Escanear manualmente

```bash
# Escanear staged changes (antes de commit)
ggshield secret scan pre-commit

# Escanear commits específicos
ggshield secret scan commit-range HEAD~5..HEAD

# Escanear repositório inteiro
ggshield secret scan repo .

# Escanear arquivo específico
ggshield secret scan path arquivo.txt
```

### Ignorar falsos positivos

Adicione ao `.gitguardian.yaml` na raiz do projeto:

```yaml
version: 2
paths-ignore:
  - "**/*.md"  # Ignorar markdown
  - "**/test_*.py"  # Ignorar arquivos de teste

matches-ignore:
  - name: "False positive example"
    match: "sua_chave_aqui"  # Placeholder
```

---

## Como Testar

```bash
# O hook roda automaticamente a cada commit
git commit -m "test: security check"
# Output esperado: "No secrets have been found"

# Para testar detecção (NÃO COMMITAR DE VERDADE):
echo "test_key=ghp_1234567890abcdefghijklmnopqrstuvwxyz12" > test.txt
git add test.txt
git commit -m "test"  # Deve detectar e bloquear (se for uma key válida)

# Limpar teste
git reset HEAD
rm test.txt
```

---

## Camadas de Proteção Ativas

✅ **3 Camadas de Segurança:**

1. **Local (Pre-commit):** ggshield escaneia antes de cada commit
2. **CI/CD (GitHub Actions):** Escaneia automaticamente em push/PR
3. **Cloud (GitGuardian):** Monitoramento contínuo 24/7

**Status:** 🟢 Proteção máxima ativa!

---

**Criado em:** 19/12/2025
**Atualizado em:** 19/12/2025

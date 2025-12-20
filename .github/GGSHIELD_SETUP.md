# 🛡️ Configuração do ggshield

## Status Atual

✅ **ggshield instalado:** v1.45.0 (standalone)
⚠️ **Pre-commit hook:** Modo manual (reminder apenas)
✅ **GitHub Actions:** Configurado ([security-scan.yml](workflows/security-scan.yml))

---

## Por que o Hook Não Está Ativo?

O ggshield foi instalado via **standalone installer** (não via pip), então o Git Bash não consegue encontrá-lo no PATH durante o pre-commit.

### Soluções:

#### **Opção 1: Reinstalar via pip (Recomendado)**

```bash
# Desinstalar versão standalone
# (via Painel de Controle → Programas)

# Instalar via pip
pip install ggshield

# Configurar autenticação
ggshield auth login

# Instalar hook
ggshield install -m local
```

**Vantagens:**
- ✅ Pre-commit hook automático
- ✅ Bloqueio de commits com secrets
- ✅ Melhor integração com Git

---

#### **Opção 2: Usar manualmente antes de cada push**

```bash
# Sempre rodar antes de push:
ggshield secret scan pre-commit

# Ou escanear commits específicos:
ggshield secret scan commit-range HEAD~5..HEAD
```

**Vantagens:**
- ✅ Mais controle
- ✅ Não precisa reinstalar

---

#### **Opção 3: Confiar apenas no GitHub Actions**

O workflow `.github/workflows/security-scan.yml` já está configurado para escanear automaticamente em cada push/PR.

**Vantagens:**
- ✅ Nenhuma configuração local necessária
- ✅ Funciona para toda a equipe

**Desvantagens:**
- ⚠️ Só detecta secrets DEPOIS do push

---

## Configuração Atual do Hook

O arquivo `.git/hooks/pre-commit` atual apenas exibe um lembrete:

```bash
🔍 Security reminder: Run 'ggshield secret scan pre-commit' before pushing
   (Optional - GitGuardian will scan on GitHub Actions)
```

Isso **não bloqueia** commits, apenas lembra de escanear manualmente.

---

## Como Testar

```bash
# Criar arquivo com secret fake
echo "API_KEY=ghp_1234567890abcdefghijklmnopqrstuvwxyz12" > test_secret.txt

# Tentar commitar
git add test_secret.txt
git commit -m "test: secret detection"

# Se o hook estiver ativo, deve bloquear
# Se não, deve apenas mostrar o lembrete

# Limpar teste
git reset HEAD~1
rm test_secret.txt
```

---

## Recomendação Final

Para **máxima segurança**, use **Opção 1** (reinstalar via pip) + **GitHub Actions** (já configurado).

Isso cria **duas camadas de proteção**:
1. **Local:** ggshield bloqueia commits com secrets
2. **Cloud:** GitHub Actions escaneia PRs automaticamente

---

**Criado em:** 19/12/2025
**Atualizado em:** 19/12/2025

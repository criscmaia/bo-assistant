# 🔒 Política de Segurança

## Reportar Vulnerabilidades

Se você descobrir uma vulnerabilidade de segurança neste projeto, **NÃO crie uma issue pública**. Em vez disso:

1. **Envie um email para:** criscmaia@gmail.com
2. **Ou use:** [GitHub Security Advisories](https://github.com/criscmaia/bo-assistant/security/advisories/new)

Responderemos dentro de 48 horas.

---

## 🛡️ Práticas de Segurança

### 1. Gerenciamento de Credenciais

#### ✅ FAZER:
- Usar variáveis de ambiente (`.env`) para todas as credenciais
- Adicionar `.env` ao `.gitignore`
- Usar `env.example` com placeholders
- Rotar credenciais regularmente (a cada 90 dias)

#### ❌ NÃO FAZER:
- Commitar arquivos `.env`
- Hardcode de API keys no código
- Compartilhar credenciais via chat/email
- Usar credenciais de produção em desenvolvimento

### 2. Proteção de Dados Sensíveis

**Arquivos protegidos no `.gitignore`:**
```gitignore
.env
.env.local
.env.*.local
*.db
*.log
.claude/
```

### 3. Ferramentas de Segurança

#### Instaladas:
- ✅ **GitHub Secret Scanning** - Monitoramento automático
- ✅ **Dependabot** - Atualizações de segurança
- ✅ **GitGuardian** - Scan de credenciais em commits

#### Recomendadas (local):
```bash
# GitGuardian Shield
pip install ggshield
ggshield install -m local

# Gitleaks
brew install gitleaks  # macOS
choco install gitleaks  # Windows
gitleaks detect --source . --verbose

# Detect Secrets
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

### 4. Workflow de Segurança

#### Antes de Commitar:
```bash
# 1. Verificar se há credenciais
git diff --cached

# 2. Escanear com ggshield (se instalado)
ggshield secret scan pre-commit

# 3. Verificar .gitignore
git status --ignored
```

#### Após Commit:
- ✅ GitHub Actions escaneia automaticamente
- ✅ GitGuardian envia alertas se detectar secrets

### 5. Resposta a Incidentes

Se uma credencial foi exposta:

1. **IMEDIATAMENTE:**
   - ✅ Revogar a credencial comprometida
   - ✅ Gerar nova credencial
   - ✅ Atualizar nos ambientes (local, Render)

2. **Limpeza do Histórico:**
   ```bash
   # Remover do Git history
   git-filter-repo --path backend/.env --invert-paths --force

   # Ou usar replace-text
   git-filter-repo --replace-text <(echo 'CREDENCIAL_ANTIGA==>***REMOVED***') --force

   # Force push
   git push origin --force --all
   ```

3. **Notificar:**
   - ✅ Equipe de desenvolvimento
   - ✅ Usuários afetados (se aplicável)
   - ✅ GitGuardian (marcar como resolvido)

---

## 🔐 Credenciais em Produção (Render)

### Configuração Segura:

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Selecione o serviço `bo-assistant-backend`
3. Vá em **Environment** → **Environment Variables**
4. Adicione:
   - `GEMINI_API_KEY` = `[sua_chave]`
   - `DATABASE_URL` = `[connection_string]`

### ⚠️ NUNCA:
- Commitar credenciais de produção
- Usar mesma API key em dev e prod
- Compartilhar acesso ao Render sem 2FA

---

## 📊 Auditoria de Segurança

### Última Auditoria: 19/12/2025

**Resultados:**
- ✅ Nenhuma credencial exposta no repositório
- ✅ `.gitignore` configurado corretamente
- ✅ GitHub Secret Scanning ativo
- ✅ Histórico do Git limpo (credenciais antigas removidas)
- ✅ Banco de dados local (`bo_logs.db`) não versionado

**Próxima Auditoria:** 19/03/2026 (90 dias)

---

## 📚 Recursos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [GitGuardian Blog](https://blog.gitguardian.com/)
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)

---

**Versão:** 1.0
**Última Atualização:** 19/12/2025
**Responsável:** Cristiano Maia

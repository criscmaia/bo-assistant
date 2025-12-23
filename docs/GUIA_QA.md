# Guia Rápido para QA - BO Inteligente

## Como Reportar um Bug

### Passo 1: Acesse o GitHub
1. Entre em: `https://github.com/criscmaia/bo-assistant`
2. Clique na aba **"Issues"**
3. Clique no botão verde **"New issue"**

### Passo 2: Escolha o Tipo
Você verá 3 opções:
- **Bug Report** → Algo não funciona
- **Sugestão de Melhoria** → Ideia para melhorar
- **Dúvida** → Não tem certeza se é bug ou comportamento esperado

### Passo 3: Preencha o Template
Preencha todos os campos do template. **Campos importantes:**

| Campo | O que colocar |
|-------|---------------|
| **Versão** | Olhe no rodapé do sistema (ex: v0.7.0) |
| **Seção** | Qual das 8 seções estava usando |
| **Passos para Reproduzir** | Seja específico! "Cliquei no botão X" |
| **Evidências** | SEMPRE anexe imagem ou vídeo |

### Passo 4: Adicione Evidências

**Para imagens:**
- Print screen → Cole direto (Ctrl+V) na caixa de texto

**Para vídeos/GIFs:**
- Use o [ShareX](https://getsharex.com/) (grátis) para gravar GIFs
- Ou grave com o celular e arraste o arquivo para a caixa

**Para gravar a tela (Windows):**
- `Win + G` → Abre Xbox Game Bar → Clique em gravar

### Passo 5: Escolha a Prioridade
Marque UMA das opções:
- **Crítico** → Sistema não funciona / dados perdidos
- **Alto** → Funcionalidade importante quebrada
- **Médio** → Funciona, mas com problemas
- **Baixo** → Visual / texto / menor importância

### Passo 6: Envie
Clique em **"Submit new issue"**

---

## Como Acompanhar o Status

### No GitHub Projects (Kanban)
1. Acesse a aba **"Projects"** no repositório
2. Clique em **"BO Inteligente - QA & Bugs"**
3. Veja em qual coluna está seu bug:

```
📥 Novo           → Acabou de ser criado
🔍 Analisando     → Cristiano está analisando
🛠️ Corrigindo     → IA está corrigindo
🧪 Teste Local    → Cristiano testando no localhost
🚀 Em Produção    → Subiu pra prod, aguardando teste
✅ Validar QA     → VOCÊ precisa testar em prod!
✔️ Fechado        → Tudo certo, issue encerrada
```

### Quando o Bug Chegar em "✅ Validar QA"
1. Você receberá uma notificação
2. Teste novamente **em produção** na versão indicada
3. Comente na issue:
   - ✅ "Validado na versão X.X.X" → Cristiano fecha a issue
   - ❌ "Ainda ocorre" → Descreva o que aconteceu, volta para correção

---

## Dicas Importantes

### Faça
- Sempre informe a versão
- Sempre anexe evidência (imagem/vídeo)
- Seja específico nos passos
- Um bug por issue (não misture vários problemas)

### Evite
- Issues vagas como "não funciona"
- Sem evidências
- Múltiplos bugs na mesma issue
- Esquecer de informar a seção

---

## Labels (Etiquetas)

Ao criar uma issue, adicione as labels apropriadas:

**Tipo:**
- `bug` - Algo não funciona
- `melhoria` - Sugestão de melhoria
- `dúvida` - Precisa de esclarecimento
- `documentação` - Relacionado a docs

**Prioridade:**
- `crítico` - Bloqueia uso em produção

**Seção:**
- `seção-1` até `seção-8` - Qual seção do BO

**Status especial:**
- `duplicado` - Já existe outra issue igual
- `não vai corrigir` - Decidido não trabalhar nisso

---

## Atalhos Úteis

| Ação | Como fazer |
|------|------------|
| Mencionar alguém | `@criscmaia` |
| Referenciar outra issue | `#123` (número da issue) |

---

## Precisa de Ajuda?

Se tiver dúvidas sobre como usar o GitHub, crie uma issue do tipo "Dúvida".

---

**Versão do Guia:** 1.0  
**Atualizado:** Dezembro 2025

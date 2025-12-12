# Changelog v0.4.1

## [0.4.1] - 2025-12-12

### ✨ Adicionado
- **Sistema de Rascunho Automático (localStorage)**
  - Salva automaticamente após cada resposta válida
  - Modal ao carregar página perguntando se deseja continuar rascunho
  - Preview do rascunho mostrando respostas salvas e data
  - Expira automaticamente após 7 dias
  - Limpa automaticamente ao completar o BO
  - Indicador visual "💾 Rascunho salvo!" na sidebar
  - Salva também ao fechar aba (beforeunload)

- **Melhorias de UX**
  - Footer atualizado com indicador de salvamento automático
  - Toast de confirmação ao restaurar rascunho
  - Sincronização automática com backend ao restaurar

### 🛠 Corrigido
- Versão atualizada para v0.4.1 no header e footer

### 🎯 Benefícios
- **Reduz frustração**: Usuário não perde respostas se fechar aba acidentalmente
- **Tolerância a falhas**: Se servidor Render "dormir", rascunho permanece local
- **Experiência contínua**: Pode parar e continuar depois sem perder progresso

---

## Implementação Técnica

### Estrutura do Rascunho (localStorage)
```javascript
{
  sessionId: "uuid",           // ID da sessão (referência)
  boId: "BO-YYYYMMDD-xxxxx",   // ID do BO
  currentStep: "1.3",          // Próximo step a responder
  answers: {                    // Respostas salvas
    "1.1": "22/03/2025, 19h03",
    "1.2": "Sgt João, prefixo 1234"
  },
  savedAt: "2025-12-12T10:30:00Z",  // Timestamp
  version: "0.4.1"             // Versão do sistema
}
```

### Chave no localStorage
```
bo_inteligente_draft
```

### Fluxo de Restauração
1. Ao carregar página, verifica `loadDraft()`
2. Se existe rascunho válido (< 7 dias), mostra modal
3. Usuário escolhe "Continuar" ou "Começar Novo"
4. Se continuar: cria nova sessão no backend, restaura respostas localmente
5. Sincroniza cada resposta com backend via `/chat`
6. Mostra próxima pergunta

### Arquivos Modificados
- `docs/index.html` - Frontend com lógica de localStorage

---

## Como Testar

1. Responda 2-3 perguntas
2. Feche a aba do navegador
3. Abra novamente - deve aparecer modal de rascunho
4. Clique "Continuar" - deve restaurar respostas
5. Complete o BO - rascunho deve ser limpo automaticamente

---

**Desenvolvido por:** Claude + Cristiano Maia  
**Data:** 12/12/2025

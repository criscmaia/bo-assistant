# 🧪 FASE 7: Testes e Correções

**Projeto:** BO Inteligente - Redesign UX  
**Fase:** 7 de 8  
**Modelo recomendado:** 🟡 Sonnet  
**Tempo estimado:** 2-3 horas  
**Dependências:** Fase 6 concluída (Responsividade ajustada)

---

## 📋 Contexto

### O que foi feito nas fases anteriores?
- **Fase 0-4:** Componentes e integração
- **Fase 5:** Tela final
- **Fase 6:** Responsividade

### O que será feito nesta fase?
Testes completos do sistema, identificação e correção de bugs, polimento final:
1. Testes de fluxo completo (happy path)
2. Testes de edge cases
3. Testes de erro e recuperação
4. Correção de bugs encontrados
5. Polimento de UX

---

## 🎯 Objetivo

Garantir que o sistema está **pronto para produção**:
- Zero erros de console
- Fluxo completo funciona
- Erros são tratados graciosamente
- UX é fluida e intuitiva

---

## 📁 Arquivo a Modificar

`docs/index.html` (correções de bugs)

---

## ✅ Tarefas

### Tarefa 7.1: Teste de Fluxo Completo (Happy Path)

**Objetivo:** Verificar se o fluxo principal funciona do início ao fim.

**Passos manuais:**

1. **Iniciar servidores:**
```bash
# Terminal 1 - Backend (opcional, funciona offline)
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd docs
python -m http.server 3000
```

2. **Abrir** `http://localhost:3000`

3. **Verificar inicialização:**
   - [ ] Loading "Conectando ao servidor..." aparece
   - [ ] ProgressBar renderiza com 8 nós
   - [ ] Seção 1 carrega automaticamente
   - [ ] Primeira pergunta aparece no chat

4. **Responder Seção 1 completa:**
   - Responder todas as perguntas
   - [ ] Cada resposta aparece como bolha do usuário
   - [ ] Próxima pergunta aparece automaticamente
   - [ ] Progresso na barra atualiza
   - [ ] Ao completar, texto é gerado
   - [ ] Área de transição aparece com preview da Seção 2

5. **Navegar para Seção 2:**
   - Clicar "Iniciar Seção 2"
   - [ ] Transição suave (fade)
   - [ ] Seção 1 marca como completa (✓ verde)
   - [ ] Seção 2 começa

6. **Pular uma seção (ex: Seção 3):**
   - Quando aparecer opção de pular
   - [ ] Clicar "Pular"
   - [ ] Seção marca como pulada (⏭️)
   - [ ] Vai para próxima seção

7. **Completar até Seção 8:**
   - Continue respondendo/pulando
   - [ ] Todas as seções processadas

8. **Verificar Tela Final:**
   - [ ] Header verde "🎉 BO Completo!"
   - [ ] Lista mostra todas 8 seções com status
   - [ ] Texto completo renderiza
   - [ ] Botão "Copiar" funciona
   - [ ] Estatísticas aparecem

9. **Testar Novo BO:**
   - Clicar "Iniciar Novo BO"
   - [ ] Confirmação aparece
   - [ ] Ao confirmar, sistema reseta
   - [ ] Volta para Seção 1

**Se algum item falhar, anotar para correção na Tarefa 7.5.**

---

### Tarefa 7.2: Teste de Edge Cases

**Objetivo:** Testar situações não convencionais.

**Casos a testar:**

1. **Resposta vazia:**
   - Tentar enviar sem digitar nada
   - [ ] Sistema deve bloquear ou mostrar erro

2. **Resposta muito longa:**
   - Digitar 1000+ caracteres
   - [ ] Sistema aceita sem quebrar layout

3. **Caracteres especiais:**
   - Digitar: `<script>alert('xss')</script>`
   - [ ] Texto aparece escapado, não executa

4. **Navegação rápida:**
   - Clicar rapidamente em várias seções na barra
   - [ ] Sistema não quebra, última navegação vence

5. **Voltar para seção completa:**
   - Completar Seção 1, ir para Seção 2
   - Clicar na Seção 1 na barra de progresso
   - [ ] Seção 1 abre em modo leitura
   - [ ] Não pode editar respostas

6. **Refresh durante preenchimento:**
   - Responder algumas perguntas
   - Pressionar F5
   - [ ] Modal de restauração aparece
   - [ ] Ao confirmar, estado é restaurado

7. **Fechar e reabrir aba:**
   - Responder algumas perguntas
   - Fechar aba completamente
   - Reabrir
   - [ ] Rascunho ainda disponível (se < 24h)

8. **Múltiplas abas:**
   - Abrir sistema em 2 abas
   - [ ] Cada aba tem sua sessão (ou aviso)

**Anotar problemas encontrados.**

---

### Tarefa 7.3: Teste de Erros e Recuperação

**Objetivo:** Verificar tratamento de erros.

**Casos a testar:**

1. **Backend offline:**
   - Parar o backend (Ctrl+C)
   - Recarregar frontend
   - [ ] Aviso "Servidor offline" aparece
   - [ ] Sistema funciona em modo rascunho

2. **Erro de rede no meio:**
   - Responder algumas perguntas
   - Desconectar rede (modo avião no DevTools)
   - Tentar responder mais
   - [ ] Erro é tratado graciosamente
   - [ ] Dados não são perdidos

3. **API retorna erro:**
   - Via console, forçar erro:
   ```javascript
   app.api.baseUrl = 'http://localhost:9999'; // URL inválida
   ```
   - Tentar responder
   - [ ] Erro aparece, sistema não quebra

4. **LocalStorage cheio:**
   - Encher localStorage:
   ```javascript
   for (let i = 0; i < 10000; i++) {
       localStorage.setItem('test_' + i, 'x'.repeat(1000));
   }
   ```
   - Tentar salvar rascunho
   - [ ] Erro tratado, não quebra

5. **JSON inválido no localStorage:**
   - Corromper rascunho:
   ```javascript
   localStorage.setItem('bo_draft', 'not valid json');
   ```
   - Recarregar página
   - [ ] Sistema ignora e começa novo

**Limpar testes:**
```javascript
// Limpar localStorage de teste
for (let i = 0; i < 10000; i++) {
    localStorage.removeItem('test_' + i);
}
localStorage.removeItem('bo_draft');
```

---

### Tarefa 7.4: Verificar Console por Erros

**Objetivo:** Zero erros no console.

**Passos:**

1. Abrir DevTools (F12) → Console
2. Limpar console (Ctrl+L)
3. Recarregar página
4. Passar por todo o fluxo
5. **Anotar TODOS os erros/warnings:**

```
[ ] Erro: ________________
[ ] Erro: ________________
[ ] Warning: ______________
```

**Erros comuns a procurar:**
- `undefined is not a function`
- `Cannot read property of null`
- `Failed to fetch`
- `SyntaxError`
- Warnings de React/deprecation (não aplicável aqui)

---

### Tarefa 7.5: Correção de Bugs Encontrados

**Objetivo:** Corrigir todos os bugs identificados nas tarefas anteriores.

**Template de correção:**

Para cada bug encontrado:

1. **Descrever o bug:**
   - O que acontece
   - Como reproduzir
   - O que deveria acontecer

2. **Localizar no código:**
   - Arquivo: `docs/index.html`
   - Classe/função afetada
   - Linha aproximada

3. **Implementar correção:**
   - Código antes
   - Código depois
   - Justificativa

4. **Testar correção:**
   - Reproduzir cenário original
   - Confirmar que está corrigido
   - Verificar que não quebrou outra coisa

**Exemplo de correção:**

```javascript
// BUG: Resposta vazia é aceita
// ANTES:
_handleSubmit(answer) {
    this._addMessage(answer, false);
    // ...
}

// DEPOIS:
_handleSubmit(answer) {
    // Validar resposta não vazia
    if (!answer || !answer.trim()) {
        console.warn('[SectionContainer] Resposta vazia ignorada');
        return;
    }
    
    this._addMessage(answer.trim(), false);
    // ...
}
```

---

### Tarefa 7.6: Polimento de UX

**Objetivo:** Pequenas melhorias de experiência.

**Verificar e ajustar:**

1. **Scroll automático:**
   - Ao adicionar mensagem no chat
   - [ ] Scroll vai para o final automaticamente
   
   Se não funciona, adicionar:
   ```javascript
   // No método _addMessage ou similar
   this.chatArea.scrollTop = this.chatArea.scrollHeight;
   ```

2. **Focus automático:**
   - Ao carregar pergunta de texto
   - [ ] Input já está focado
   
   Se não funciona, adicionar:
   ```javascript
   // Após renderizar input
   setTimeout(() => {
       const input = document.querySelector('.text-input__field');
       if (input) input.focus();
   }, 100);
   ```

3. **Feedback visual de loading:**
   - Ao enviar resposta
   - [ ] Botão mostra estado de loading
   
   Se não existe, adicionar classe:
   ```css
   .text-input__button--loading {
       opacity: 0.7;
       pointer-events: none;
   }
   .text-input__button--loading::after {
       content: '...';
       animation: dots 1s infinite;
   }
   ```

4. **Transições suaves:**
   - Entre seções
   - [ ] Fade in/out funciona (200ms)

5. **Tooltips da barra:**
   - Hover sobre nós da ProgressBar
   - [ ] Tooltip aparece com nome da seção

6. **Estados de botão:**
   - Botões desabilitados
   - [ ] Visual claro de disabled
   - [ ] Cursor: not-allowed

7. **Mensagens de erro amigáveis:**
   - Verificar se erros são claros para o usuário
   - [ ] Sem jargão técnico
   - [ ] Sugerem ação

---

### Tarefa 7.7: Validação Final de Acessibilidade Básica

**Objetivo:** Garantir acessibilidade mínima.

**Verificar:**

1. **Navegação por teclado:**
   - Tab através dos elementos
   - [ ] Ordem lógica
   - [ ] Focus visível

2. **Contraste de cores:**
   - Usar ferramenta de contraste
   - [ ] Texto sobre fundo: 4.5:1 mínimo
   - [ ] Botões: contraste adequado

3. **Labels em inputs:**
   - [ ] Inputs têm placeholder descritivo
   - [ ] Botões têm texto claro

4. **Tamanho de toque:**
   - [ ] Botões >= 44x44px em mobile

**Correções rápidas se necessário:**

```css
/* Focus visível */
button:focus,
input:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
}

/* Melhorar contraste */
.some-light-text {
    color: #374151; /* De #9ca3af para mais escuro */
}
```

---

### Tarefa 7.8: Adicionar Logs de Debug Condicionais

**Objetivo:** Facilitar debug em produção sem poluir console.

**Adicionar no início do script:**

```javascript
        // ============================================
        // CONFIGURAÇÃO DE DEBUG
        // ============================================
        
        const DEBUG = {
            enabled: window.location.hostname === 'localhost',
            log: function(component, message, data = null) {
                if (!this.enabled) return;
                
                const timestamp = new Date().toLocaleTimeString();
                const prefix = `[${timestamp}] [${component}]`;
                
                if (data) {
                    console.log(prefix, message, data);
                } else {
                    console.log(prefix, message);
                }
            },
            warn: function(component, message, data = null) {
                if (!this.enabled) return;
                console.warn(`[${component}]`, message, data || '');
            },
            error: function(component, message, data = null) {
                // Erros sempre logados
                console.error(`[${component}]`, message, data || '');
            }
        };
        
        // Expor para debug manual
        window.DEBUG = DEBUG;
```

**Substituir console.log por DEBUG.log:**

```javascript
// ANTES:
console.log('[BOApp] Inicializando...');

// DEPOIS:
DEBUG.log('BOApp', 'Inicializando...');
```

**Nota:** Esta é uma melhoria opcional. Se o tempo for limitado, pular.

---

### Tarefa 7.9: Documentar Bugs Conhecidos (se houver)

**Objetivo:** Documentar limitações conhecidas.

Se após todas as correções ainda houver bugs menores que não serão corrigidos nesta fase, documentar:

**Criar comentário no código:**

```javascript
        // ============================================
        // BUGS CONHECIDOS / LIMITAÇÕES
        // ============================================
        // 
        // 1. [MENOR] Em Safari iOS 14, animação X pode piscar
        //    - Workaround: Desabilitar animação em Safari
        //    - Prioridade: Baixa
        //
        // 2. [MENOR] LocalStorage pode falhar em modo privado
        //    - Sistema funciona, mas não salva rascunho
        //    - Prioridade: Baixa
        //
        // ============================================
```

---

### Tarefa 7.10: Commit da Fase 7

**Objetivo:** Salvar o progresso.

**Comandos:**
```bash
cd /caminho/para/bo-assistant
git add .
git status

git commit -m "fix: testes, correções de bugs e polimento (Fase 7)

Testes realizados:
- Fluxo completo (happy path) ✓
- Edge cases (respostas vazias, XSS, etc.) ✓
- Erros e recuperação (offline, rede) ✓
- Console limpo de erros ✓

Correções:
- [listar bugs corrigidos]

Polimento:
- Scroll automático no chat
- Focus automático em inputs
- Transições suaves
- Feedback visual de loading

Acessibilidade:
- Navegação por teclado
- Focus visível
- Contraste adequado"

git push
```

---

## ✅ Checklist Final da Fase 7

Antes de prosseguir para a Fase 8, confirme:

- [ ] Happy path funciona do início ao fim
- [ ] Edge cases tratados
- [ ] Erros não quebram o sistema
- [ ] Console sem erros
- [ ] Bugs encontrados corrigidos
- [ ] UX polida (scroll, focus, transições)
- [ ] Acessibilidade básica ok
- [ ] Commit feito e pushado

---

## 🐛 Bugs Comuns e Soluções

### Input não foca automaticamente
```javascript
// Adicionar após renderizar componente
requestAnimationFrame(() => {
    const input = document.querySelector('.text-input__field');
    if (input) input.focus();
});
```

### Scroll não vai para o final
```javascript
// Adicionar após adicionar mensagem
const chat = document.querySelector('.section-chat');
chat.scrollTo({
    top: chat.scrollHeight,
    behavior: 'smooth'
});
```

### Clique duplo envia duas vezes
```javascript
// Adicionar flag de proteção
if (this.isSubmitting) return;
this.isSubmitting = true;

// ... processar ...

this.isSubmitting = false;
```

### Transição não funciona
```javascript
// Verificar se elemento existe antes de animar
const el = document.querySelector('.section-container');
if (!el) return;

el.style.opacity = '0';
await new Promise(r => setTimeout(r, 200));
// ... trocar conteúdo ...
el.style.opacity = '1';
```

### LocalStorage falha silenciosamente
```javascript
try {
    localStorage.setItem('bo_draft', JSON.stringify(data));
} catch (e) {
    DEBUG.warn('BOApp', 'localStorage indisponível:', e.message);
    // Continuar sem salvar
}
```

---

## ⏭️ Próxima Fase

**Fase 8: Refatoração (Opcional)**
- Modelo: 🔴 Opus (ou Sonnet)
- Arquivo: `FASE_8_REFATORACAO.md`
- Objetivo: Separar CSS/JS em arquivos, modularizar código

---

## 📚 Referências

- [Web Accessibility Checklist](https://www.a11yproject.com/checklist/)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [Testing Best Practices](https://testing-library.com/docs/guiding-principles/)

---

*Documento gerado em 31/12/2025*  
*Para execução com Claude Sonnet*

# 📱 FASE 6: Responsividade

**Projeto:** BO Inteligente - Redesign UX  
**Fase:** 6 de 8  
**Modelo recomendado:** 🟢 Haiku  
**Tempo estimado:** 1-2 horas  
**Dependências:** Fase 5 concluída (Tela Final funcionando)

---

## 📋 Contexto

### O que foi feito nas fases anteriores?
- **Fase 0-4:** Componentes principais implementados
- **Fase 5:** Tela final com resumo e exportação

### O que será feito nesta fase?
Ajustes finais de **responsividade** para garantir experiência perfeita em:
- 📱 Mobile (< 480px) - iPhone SE, etc.
- 📱 Mobile grande (480px - 768px) - iPhone Plus, Android
- 📊 Tablet (768px - 1024px) - iPad
- 🖥️ Desktop (> 1024px)

### Problemas comuns a resolver
1. Barra de progresso muito apertada em mobile
2. Botões pequenos demais para toque
3. Texto transbordando em telas pequenas
4. Modais/overlays não ajustados
5. Header ocupando muito espaço vertical

---

## 🎯 Objetivo

Revisar e ajustar CSS de todos os componentes para garantir:
- Touch targets mínimos de 44x44px
- Texto legível (mínimo 14px)
- Espaçamentos adequados
- Scroll suave
- Nenhum overflow horizontal

---

## 📁 Arquivo a Modificar

`docs/index.html`

---

## ✅ Tarefas

### Tarefa 6.1: Ajustar Header para mobile

**Objetivo:** Header mais compacto em telas pequenas.

**Localização:** No CSS, encontre os estilos do header ou adicione no final da seção de estilos globais.

**Adicione/Modifique:**

```css
        /* ============================================ */
        /* RESPONSIVIDADE GLOBAL */
        /* ============================================ */
        
        /* Header responsivo */
        @media (max-width: 480px) {
            header {
                padding: 12px 16px;
            }
            
            header h1 {
                font-size: 18px;
            }
            
            header p {
                font-size: 12px;
            }
        }
        
        /* Container principal responsivo */
        @media (max-width: 768px) {
            main {
                padding: 12px;
            }
        }
        
        @media (max-width: 480px) {
            main {
                padding: 8px;
            }
        }
```

---

### Tarefa 6.2: Ajustar ProgressBar para mobile

**Objetivo:** Barra de progresso usável em telas pequenas.

**Localização:** Na seção de CSS da ProgressBar, encontre os media queries existentes e **substitua/complemente**.

**Encontre a seção:**
```css
        /* Responsividade */
        @media (max-width: 768px) {
            .progress-node {
```

**Substitua TODA a seção de media queries da ProgressBar por:**

```css
        /* -------------------------------------------- */
        /* PROGRESSBAR - RESPONSIVIDADE */
        /* -------------------------------------------- */
        
        @media (max-width: 1024px) {
            .progress-bar {
                gap: 4px;
            }
            
            .progress-node {
                width: 36px;
                height: 36px;
                font-size: 14px;
            }
            
            .progress-line-container {
                height: 3px;
            }
        }
        
        @media (max-width: 768px) {
            #progress-bar-container {
                padding: 12px;
                margin-bottom: 12px;
            }
            
            .progress-bar {
                gap: 2px;
            }
            
            .progress-node {
                width: 32px;
                height: 32px;
                font-size: 12px;
            }
            
            .progress-line-container {
                height: 2px;
                min-width: 16px;
            }
            
            .progress-tooltip {
                font-size: 11px;
                padding: 6px 10px;
            }
        }
        
        @media (max-width: 480px) {
            #progress-bar-container {
                padding: 10px;
                border-radius: 8px;
            }
            
            .progress-bar {
                gap: 1px;
            }
            
            .progress-node {
                width: 28px;
                height: 28px;
                font-size: 11px;
            }
            
            .progress-line-container {
                min-width: 10px;
                flex: 1;
            }
            
            /* Em telas muito pequenas, esconder números e mostrar só ícones */
            .progress-node__number {
                display: none;
            }
            
            .progress-node--completed::after,
            .progress-node--skipped::after {
                font-size: 12px;
            }
        }
        
        /* Modo paisagem em mobile */
        @media (max-height: 500px) and (orientation: landscape) {
            #progress-bar-container {
                padding: 8px;
                margin-bottom: 8px;
            }
            
            .progress-node {
                width: 28px;
                height: 28px;
            }
        }
```

---

### Tarefa 6.3: Ajustar SectionContainer para mobile

**Objetivo:** Container de seção otimizado para toque.

**Localização:** Na seção de CSS do SectionContainer, encontre os media queries existentes e **complemente**.

**Encontre:**
```css
        /* Responsividade */
        @media (max-width: 768px) {
            .section-container {
```

**Substitua/Complemente com:**

```css
        /* -------------------------------------------- */
        /* SECTION CONTAINER - RESPONSIVIDADE */
        /* -------------------------------------------- */
        
        @media (max-width: 768px) {
            .section-container {
                height: calc(100vh - 160px);
                min-height: 350px;
                border-radius: 12px;
            }
            
            .section-header {
                padding: 12px 16px;
            }
            
            .section-header__title {
                font-size: 15px;
                gap: 8px;
            }
            
            .section-header__emoji {
                font-size: 20px;
            }
            
            .section-header__badge {
                font-size: 11px;
                padding: 3px 8px;
            }
            
            .section-chat {
                padding: 12px;
                gap: 12px;
            }
            
            .chat-message--bot,
            .chat-message--user {
                max-width: 90%;
            }
            
            .chat-message__bubble--bot,
            .chat-message__bubble--user {
                padding: 12px 14px;
                border-radius: 12px 12px 12px 4px;
            }
            
            .chat-message__text {
                font-size: 14px;
            }
            
            .chat-message__hint {
                font-size: 12px;
            }
        }
        
        @media (max-width: 480px) {
            .section-container {
                height: calc(100vh - 140px);
                min-height: 300px;
                border-radius: 8px;
            }
            
            .section-header {
                padding: 10px 12px;
            }
            
            .section-header__title {
                font-size: 14px;
            }
            
            .section-header__emoji {
                font-size: 18px;
            }
            
            .section-chat {
                padding: 10px;
                gap: 10px;
            }
            
            .chat-message--bot,
            .chat-message--user {
                max-width: 95%;
            }
            
            .chat-message__bubble--bot,
            .chat-message__bubble--user {
                padding: 10px 12px;
            }
            
            .chat-message__text {
                font-size: 14px;
                line-height: 1.4;
            }
            
            /* Área de texto gerado */
            .section-generated {
                padding: 12px;
            }
            
            .section-generated__text {
                padding: 12px;
                font-size: 13px;
                max-height: 150px;
            }
            
            /* Transição */
            .section-transition {
                padding: 12px;
            }
            
            .section-transition__preview {
                padding: 12px;
            }
            
            .section-transition__preview-emoji {
                font-size: 24px;
            }
            
            .section-transition__preview-name {
                font-size: 14px;
            }
        }
        
        /* Teclado virtual aberto (viewport reduzido) */
        @media (max-height: 400px) {
            .section-container {
                height: calc(100vh - 100px);
                min-height: 200px;
            }
            
            .section-chat {
                max-height: 150px;
            }
        }
```

---

### Tarefa 6.4: Ajustar Componentes de Input para mobile

**Objetivo:** Inputs com touch targets adequados (mínimo 44px).

**Localização:** Na seção de CSS dos componentes de input.

**Encontre os media queries existentes e substitua/complemente:**

```css
        /* -------------------------------------------- */
        /* INPUTS - RESPONSIVIDADE */
        /* -------------------------------------------- */
        
        @media (max-width: 768px) {
            .input-component {
                padding: 12px;
            }
            
            /* Text Input */
            .text-input {
                flex-direction: column;
                gap: 10px;
            }
            
            .text-input__field {
                padding: 14px 16px;
                font-size: 16px; /* Evita zoom no iOS */
                border-radius: 10px;
            }
            
            .text-input__button {
                width: 100%;
                padding: 14px 20px;
                font-size: 16px;
                min-height: 48px; /* Touch target */
            }
            
            .text-input__error {
                font-size: 13px;
            }
            
            /* Single Choice */
            .single-choice {
                flex-direction: column;
                gap: 10px;
            }
            
            .single-choice__option {
                max-width: none;
                width: 100%;
                padding: 16px 20px;
                min-height: 52px; /* Touch target */
                font-size: 16px;
            }
            
            .single-choice__icon {
                font-size: 22px;
            }
            
            /* Multiple Choice */
            .multiple-choice__option {
                padding: 14px 16px;
                min-height: 52px; /* Touch target */
            }
            
            .multiple-choice__checkbox {
                width: 26px;
                height: 26px;
            }
            
            .multiple-choice__label {
                font-size: 15px;
            }
            
            .multiple-choice__confirm {
                padding: 14px 20px;
                font-size: 16px;
                min-height: 48px;
            }
        }
        
        @media (max-width: 480px) {
            .input-component {
                padding: 10px;
            }
            
            .text-input__field {
                padding: 12px 14px;
            }
            
            .single-choice__option {
                padding: 14px 16px;
            }
            
            .multiple-choice__option {
                padding: 12px 14px;
            }
            
            .multiple-choice__checkbox {
                width: 24px;
                height: 24px;
            }
            
            .multiple-choice__hint {
                font-size: 12px;
            }
        }
```

---

### Tarefa 6.5: Ajustar Tela Final para mobile

**Objetivo:** Tela final totalmente responsiva.

**Localização:** Na seção de CSS da tela final, encontre os media queries existentes e complemente.

**Adicione/Substitua:**

```css
        /* -------------------------------------------- */
        /* TELA FINAL - RESPONSIVIDADE COMPLETA */
        /* -------------------------------------------- */
        
        @media (max-width: 768px) {
            .final-screen__header {
                padding: 24px 16px;
            }
            
            .final-screen__icon {
                font-size: 48px;
            }
            
            .final-screen__title {
                font-size: 24px;
            }
            
            .final-screen__subtitle {
                font-size: 14px;
            }
            
            .final-screen__content {
                padding: 16px;
            }
            
            .final-screen__summary {
                padding: 16px;
            }
            
            .final-screen__section-item {
                padding: 12px;
            }
            
            .final-screen__section-name {
                font-size: 13px;
            }
            
            .final-screen__text-header {
                flex-direction: column;
                gap: 12px;
                align-items: flex-start;
            }
            
            .final-screen__copy-btn {
                width: 100%;
                justify-content: center;
            }
            
            .final-screen__text-content {
                max-height: 300px;
                font-size: 13px;
            }
            
            .final-screen__actions {
                flex-direction: column;
                gap: 12px;
            }
            
            .final-screen__action-btn {
                padding: 16px 20px;
                font-size: 15px;
                min-height: 52px;
            }
            
            .final-screen__stats {
                flex-direction: column;
                gap: 8px;
                align-items: center;
            }
        }
        
        @media (max-width: 480px) {
            .final-screen__header {
                padding: 20px 12px;
            }
            
            .final-screen__icon {
                font-size: 40px;
                margin-bottom: 12px;
            }
            
            .final-screen__title {
                font-size: 20px;
            }
            
            .final-screen__content {
                padding: 12px;
            }
            
            .final-screen__summary {
                padding: 12px;
                margin-bottom: 16px;
            }
            
            .final-screen__summary-title {
                font-size: 14px;
            }
            
            .final-screen__section-item {
                padding: 10px 12px;
                gap: 8px;
            }
            
            .final-screen__section-icon {
                font-size: 16px;
            }
            
            .final-screen__section-name {
                font-size: 12px;
            }
            
            .final-screen__section-status {
                font-size: 10px;
                padding: 3px 6px;
            }
            
            .final-screen__text-box {
                margin-bottom: 16px;
            }
            
            .final-screen__text-header {
                padding: 12px;
            }
            
            .final-screen__text-title {
                font-size: 14px;
            }
            
            .final-screen__text-content {
                padding: 12px;
                max-height: 250px;
            }
            
            .final-screen__text-section-title {
                font-size: 13px;
            }
            
            .final-screen__stat {
                font-size: 13px;
            }
        }
```

---

### Tarefa 6.6: Ajustar Loading e Toasts para mobile

**Objetivo:** Overlays adequados em todas as telas.

**Localização:** Na seção de CSS de loading/toasts.

**Adicione:**

```css
        /* -------------------------------------------- */
        /* LOADING E TOASTS - RESPONSIVIDADE */
        /* -------------------------------------------- */
        
        @media (max-width: 480px) {
            #app-loading-overlay .loading-content {
                padding: 20px 24px;
                margin: 0 16px;
                border-radius: 10px;
            }
            
            #app-loading-overlay .loading-message {
                font-size: 14px;
            }
            
            .app-toast {
                left: 16px;
                right: 16px;
                bottom: 16px;
                text-align: center;
            }
        }
```

---

### Tarefa 6.7: Adicionar utilitários CSS para safe areas (iOS)

**Objetivo:** Suporte a notch e home indicator do iPhone.

**Localização:** No início da seção de CSS, após os estilos globais.

**Adicione:**

```css
        /* ============================================ */
        /* SAFE AREAS (iOS) */
        /* ============================================ */
        
        /* Suporte a env() para dispositivos com notch */
        @supports (padding: env(safe-area-inset-top)) {
            header {
                padding-top: calc(12px + env(safe-area-inset-top));
            }
            
            main {
                padding-left: calc(12px + env(safe-area-inset-left));
                padding-right: calc(12px + env(safe-area-inset-right));
            }
            
            .input-component {
                padding-bottom: calc(12px + env(safe-area-inset-bottom));
            }
            
            .final-screen__actions {
                padding-bottom: env(safe-area-inset-bottom);
            }
        }
```

---

### Tarefa 6.8: Adicionar meta viewport otimizado

**Objetivo:** Garantir viewport correto para mobile.

**Localização:** No `<head>` do HTML.

**Encontre:**
```html
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**Substitua por:**
```html
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
```

**Nota:** O `user-scalable=no` previne zoom acidental ao digitar. O `viewport-fit=cover` permite usar safe areas.

---

### Tarefa 6.9: Testar em diferentes tamanhos

**Objetivo:** Verificar responsividade em todos os breakpoints.

**Passos:**

1. Iniciar servidor:
```bash
cd docs
python -m http.server 3000
```

2. Abrir Chrome DevTools (F12) → Toggle Device Toolbar (Ctrl+Shift+M)

3. **Testar em cada dispositivo:**

| Dispositivo | Largura | Verificar |
|-------------|---------|-----------|
| iPhone SE | 375px | Tudo cabe, touch targets ok |
| iPhone 12 | 390px | Layout adequado |
| iPhone 14 Pro Max | 430px | Espaçamentos bons |
| iPad Mini | 768px | Transição tablet |
| iPad Pro | 1024px | Layout desktop |

4. **Checklist visual:**
   - [ ] ProgressBar: nós visíveis, clicáveis
   - [ ] SectionContainer: chat legível, scroll funciona
   - [ ] TextInput: campo grande o suficiente
   - [ ] SingleChoice: botões empilhados, touch ok
   - [ ] MultipleChoice: checkboxes clicáveis
   - [ ] FinalScreen: tudo legível e clicável
   - [ ] Nenhum overflow horizontal (scroll lateral)

5. **Testar orientação paisagem:**
   - Rotacionar para landscape
   - [ ] Layout se adapta
   - [ ] Nada quebra

6. **Testar com teclado virtual:**
   - Tocar no input de texto
   - [ ] Teclado não cobre o input
   - [ ] Scroll funciona com teclado aberto

---

### Tarefa 6.10: Commit da Fase 6

**Objetivo:** Salvar o progresso.

**Comandos:**
```bash
cd /caminho/para/bo-assistant
git add .
git status

git commit -m "feat: ajustes de responsividade para mobile e tablet (Fase 6)

- Header compacto em mobile
- ProgressBar adaptativa (28px em mobile)
- Touch targets mínimos de 44px
- SectionContainer otimizado para viewport reduzido
- Inputs empilhados em mobile
- Tela final totalmente responsiva
- Suporte a safe areas (iOS notch)
- Meta viewport otimizado
- Testado em iPhone SE até iPad Pro"

git push
```

---

## ✅ Checklist Final da Fase 6

Antes de prosseguir para a Fase 7, confirme:

- [ ] Header responsivo
- [ ] ProgressBar responsiva (todos breakpoints)
- [ ] SectionContainer responsivo
- [ ] Componentes de Input responsivos
- [ ] Tela Final responsiva
- [ ] Loading/Toasts responsivos
- [ ] Safe areas (iOS) configuradas
- [ ] Meta viewport atualizado
- [ ] Testado em iPhone SE (375px)
- [ ] Testado em iPad (768px)
- [ ] Testado em landscape
- [ ] Sem overflow horizontal
- [ ] Commit feito e pushado

---

## 🐛 Troubleshooting

### Zoom indesejado ao focar input (iOS)
- Verificar se font-size do input é >= 16px
- Verificar meta viewport

### Elementos cortados em iPhone
- Verificar safe areas
- Verificar padding-bottom nos containers

### Scroll horizontal aparece
- Inspecionar elemento que está transbordando
- Adicionar `overflow-x: hidden` no body

### Botões muito pequenos
- Verificar min-height de 44-48px
- Aumentar padding

### Teclado cobre input
- Usar `scrollIntoView()` ao focar
- Verificar altura do container

---

## ⏭️ Próxima Fase

**Fase 7: Testes e Correções**
- Modelo: 🟡 Sonnet
- Arquivo: `FASE_7_TESTES.md`
- Objetivo: Testes end-to-end, correção de bugs, polimento

---

## 📚 Referências

- [Touch Target Size](https://web.dev/accessible-tap-targets/)
- [Safe Areas CSS](https://developer.apple.com/design/human-interface-guidelines/ios/visual-design/adaptivity-and-layout/)
- [Viewport Meta Tag](https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag)

---

*Documento gerado em 31/12/2025*  
*Para execução com Claude Haiku*

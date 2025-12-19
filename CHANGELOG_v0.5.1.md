# Changelog - v0.5.1

**Data de release:** 19/12/2025
**Autor:** Claude Sonnet 4.5 via Claude Code

---

## 🎯 Resumo das Mudanças

Implementação de melhorias críticas de UX para o fluxo multi-seção do BO Inteligente:

1. **✅ View Persistente de Textos Gerados** - Usuário não perde mais os textos ao navegar entre seções
2. **✅ Numeração Completa de Perguntas** - Badges mostram IDs completos (e.g., "1.1", "2.3") para fácil referência

---

## 🚀 Novas Funcionalidades

### 1. Container Persistente de Textos Gerados

**Problema resolvido:** Ao avançar da Seção 1 para Seção 2, o texto gerado da Seção 1 desaparecia.

**Solução implementada:**
- Container `generated-sections-container` com accordion HTML nativo (`<details>`)
- Cada seção tem seu próprio card colapsável
- Textos permanecem visíveis durante toda a sessão
- Botão "Copiar BO Completo" quando há 2+ seções

**Arquivos modificados:**
- `docs/index.html` (linhas 219-260)

**Funções JavaScript adicionadas:**
```javascript
addGeneratedSectionText(sectionNumber, text)  // Adiciona texto ao card da seção
copySection(sectionNumber)                     // Copia seção individual
copyAllSections()                              // Copia TODAS as seções formatadas
```

**Comportamento:**
- Desktop: Todas seções visíveis, Seção 1 aberta por padrão
- Mobile: Seções collapsed por padrão (economiza espaço vertical)
- Scroll automático para o container ao completar seção

---

### 2. Numeração Completa de Perguntas

**Problema resolvido:** Sidebar mostrava apenas "0", "1", "2" ao invés dos IDs completos.

**Solução implementada:**
- Badges agora exibem IDs completos: "1.1", "1.2", "2.0", "2.1", etc.
- Facilita comunicação (usuário pode dizer "erro na pergunta 2.3")
- IDs mantidos mesmo quando pergunta está em andamento
- Apenas checkmark (✓) substitui o ID quando respondida

**Arquivos modificados:**
- `docs/index.html` (linhas 660-672, 760-772, 691-703)

**CSS responsivo:**
```css
@media (max-width: 768px) {
  #questions-list [id^="icon-"] {
    font-size: 0.65rem;  /* Menor em mobile */
    width: 2rem;
  }
}
```

---

## 🔧 Mudanças Técnicas

### HTML

**ANTES:**
```html
<div id="result-container" class="hidden ...">
  <h3>✅ Seção 1 - Texto Gerado</h3>
  <div id="generated-text">...</div>
</div>
```

**DEPOIS:**
```html
<div id="generated-sections-container" class="hidden">
  <h3>📄 Textos Gerados do BO</h3>

  <!-- Seção 1 -->
  <details id="section1-card" open>
    <summary>📝 Seção 1 - Contexto da Ocorrência</summary>
    <pre id="section1-text">...</pre>
    <button onclick="copySection(1)">📋 Copiar Seção 1</button>
  </details>

  <!-- Seção 2 -->
  <details id="section2-card">
    <summary>🚗 Seção 2 - Abordagem a Veículo</summary>
    <pre id="section2-text">...</pre>
    <button onclick="copySection(2)">📋 Copiar Seção 2</button>
  </details>

  <!-- Botão global -->
  <button onclick="copyAllSections()">📑 Copiar BO Completo</button>
</div>
```

### JavaScript

**Lógica de conclusão de seção (ANTES):**
```javascript
generatedText.textContent = data.generated_text;
resultContainer.classList.remove('hidden');
```

**Lógica de conclusão de seção (DEPOIS):**
```javascript
addGeneratedSectionText(currentSection, data.generated_text);
generatedSectionsContainer.scrollIntoView({ behavior: 'smooth' });
```

**Badges da sidebar (ANTES):**
```javascript
icon.textContent = step.split('.')[1];  // "1"
```

**Badges da sidebar (DEPOIS):**
```javascript
icon.textContent = step;  // "1.1"
```

### CSS

**Adicionado responsividade mobile:**
```css
/* Container de textos gerados */
@media (max-width: 768px) {
  #generated-sections-container details {
    margin-bottom: 0.5rem;
  }

  #generated-sections-container details[open] summary {
    border-bottom: 1px solid #e5e7eb;
  }
}

/* Badges menores em mobile */
@media (max-width: 768px) {
  #questions-list [id^="icon-"] {
    font-size: 0.65rem;
    width: 2rem;
  }
}
```

---

## 📱 Responsividade

### Desktop (>768px)
- Container de textos sempre visível
- Seção 1 aberta por padrão (`open`)
- Badges com largura de 2rem (32px)

### Mobile (≤768px)
- Seções collapsed economizam espaço
- Badges com fonte 0.65rem (legível)
- Sidebar overlay com IDs completos

---

## 🧪 Testes Realizados

### ✅ Teste 1: Fluxo Completo Seção 1 → Seção 2
1. Responder 6 perguntas da Seção 1
2. Verificar texto gerado em card verde
3. Verificar botão "Copiar Seção 1" funciona
4. Clicar em "Iniciar Seção 2"
5. **Verificar card da Seção 1 permanece visível** ← FIX CRÍTICO
6. Verificar sidebar atualiza para 8 perguntas (2.0-2.7)
7. Verificar header atualiza para "Seção 2"
8. Responder 8 perguntas da Seção 2
9. Verificar texto da Seção 2 aparece em card azul
10. Verificar botão "Copiar BO Completo" aparece
11. Verificar copiar BO completo gera texto formatado

### ✅ Teste 2: Numeração em Mobile
1. Abrir sidebar em dispositivo mobile
2. Verificar badges mostram "1.1", "1.2", não "1", "2"
3. Verificar legibilidade com fonte menor

### ✅ Teste 3: Copiar BO Completo
1. Completar Seção 1 e Seção 2
2. Clicar em "Copiar BO Completo"
3. Verificar texto copiado contém:
   - Separadores visuais (━━━━━)
   - Cabeçalhos das seções
   - Textos completos
   - Footer com versão e data

---

## 🔍 Detalhes de Implementação

### Por que `<details>` nativo?
- ✅ Acessível por padrão (ARIA, navegação por teclado)
- ✅ Sem JavaScript necessário para expand/collapse
- ✅ Semântico (HTML5 padrão)
- ✅ Performance: rendering nativo do browser

### Por que `onclick` inline ao invés de addEventListener?
- ✅ Simplicidade: código mais legível
- ✅ Funções globais (window scope)
- ✅ Evita necessidade de query selectors
- ✅ Compatível com geração dinâmica de HTML

### Escalabilidade
- ✅ Suporta até 8 seções futuras (design flexível)
- ✅ `copyAllSections()` detecta automaticamente seções visíveis
- ✅ Cada nova seção: apenas adicionar `<details>` no HTML

---

## 📊 Impacto

### Performance
- ✅ Sem impacto: usa `<details>` nativo (zero JS para accordion)
- ✅ Lazy rendering: seções só aparecem quando completas
- ✅ Memória: textos armazenados apenas em DOM (não em estado JS)

### Experiência do Usuário
- ✅ Zero perda de dados ao navegar entre seções
- ✅ Referência fácil a perguntas específicas ("erro na 2.3")
- ✅ Cópia rápida de seções individuais ou BO completo
- ✅ Layout limpo e organizado

---

## 🐛 Bugs Corrigidos

### Bug #1: Textos Desaparecem ao Avançar de Seção
**ANTES:** Ao clicar em "Iniciar Seção 2", o card verde da Seção 1 desaparecia (`hidden = true`).

**DEPOIS:** Card permanece visível. Novo container persistente mantém TODOS os textos.

**Código modificado:**
```javascript
// REMOVIDO:
resultContainer.classList.add('hidden');

// ADICIONADO:
// Nenhuma ação - container persiste automaticamente
```

### Bug #2: Sidebar sem Numeração Clara
**ANTES:** Círculos mostravam apenas "0", "1", "2".

**DEPOIS:** Badges mostram "1.1", "1.2", "2.0", "2.1".

---

## 🔮 Trabalho Futuro (v0.5.2+)

### Sprint 3: Mini Resumo ao Iniciar Seção (Opcional)
- Mostrar card amarelo com 3-4 respostas-chave da seção anterior
- Exemplo: Ao iniciar Seção 2, mostrar data/hora, guarnição e local da Seção 1
- Requer modificação backend: `/start_section` retornar `previous_section_summary`

### Sprint 4: Polimento Visual
- Adicionar contador "Seção 2/8" no header
- Progresso dentro da seção: "[3/8]"
- Mobile: Abreviar para "S2 - Veículo"

---

## 📚 Referências

- **Plan Mode:** `C:\Users\user\.claude\plans\piped-tickling-hickey.md`
- **Screenshots de referência:** `design/` (3 arquivos)
- **Versão anterior:** v0.5.0 (Seção 2 implementada)
- **Material base:** Claudio Moreira (Sargento PM)

---

## 👥 Créditos

- **Implementação:** Claude Sonnet 4.5 via Claude Code
- **Design UX:** Baseado em feedback e análise de screenshots
- **Metodologia:** Plan mode → Aprovação → Implementação incremental

---

## 📄 Licença

Mesma licença do projeto principal (BO Inteligente).

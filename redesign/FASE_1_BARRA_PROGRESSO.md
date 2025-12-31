# 📊 FASE 1: Barra de Progresso

**Projeto:** BO Inteligente - Redesign UX  
**Fase:** 1 de 8  
**Modelo recomendado:** 🟢 Haiku  
**Tempo estimado:** 2-3 horas  
**Dependências:** Fase 0 concluída

---

## 📋 Contexto

### O que foi feito na Fase 0?
- Branch `feature/ux-redesign-v1` criada
- Arquivo `docs/js/data/sections.js` com 8 seções e ~53 perguntas
- Estrutura de pastas preparada

### O que será feito nesta fase?
Criar o componente **ProgressBar** - uma barra de progresso horizontal no estilo Duolingo que mostra:
- 8 bolinhas numeradas (uma por seção)
- Linhas conectando as bolinhas
- Preenchimento gradual conforme o usuário avança
- Estados visuais: pendente, em progresso, completo, pulado
- Tooltips com nome da seção ao passar o mouse
- Navegação por clique (apenas seções já visitadas)

### Wireframe de referência
```
┌─────────────────────────────────────────────────────────────────┐
│  ●━━━━━●━━━━━●━━━━━◐━━━━━○━━━━━○━━━━━○━━━━━○                    │
│  1     2     3     4     5     6     7     8                    │
│  ✓     ✓     ✓    47%                                           │
│                    ↑                                            │
│               Seção atual                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Estados das bolinhas
- `○` **Pendente** (cinza claro) - Seção não iniciada
- `◐` **Em progresso** (azul) - Seção atual, parcialmente preenchida
- `●` **Completa** (verde) - Todas as perguntas respondidas
- `●⏭️` **Pulada** (cinza + ícone) - Seção foi pulada pelo usuário

---

## 🎯 Objetivo

Adicionar ao `index.html`:
1. HTML da barra de progresso
2. CSS para estilização e animações
3. JavaScript com classe `ProgressBar`

**Importante:** Nesta fase, o componente será criado de forma **isolada**. A integração com o resto do sistema será feita na Fase 4.

---

## 📁 Arquivo a Modificar

`docs/index.html`

---

## ✅ Tarefas

### Tarefa 1.1: Adicionar HTML da barra de progresso

**Objetivo:** Criar a estrutura HTML do componente.

**Localização:** Dentro do `<main>`, ANTES do container de chat atual.

**Encontre este trecho no index.html:**
```html
<!-- Main Content com Sidebar -->
<main class="flex-1 max-w-7xl w-full mx-auto p-4 flex gap-4">
    <!-- Sidebar - Histórico de Perguntas -->
    <aside id="sidebar" ...>
```

**Adicione ANTES do `<aside id="sidebar">`:**
```html
            <!-- ============================================ -->
            <!-- BARRA DE PROGRESSO - NOVO DESIGN -->
            <!-- ============================================ -->
            <div id="progress-bar-container" class="w-full bg-white rounded-lg shadow-lg p-4 mb-4">
                <div id="progress-bar" class="progress-bar">
                    <!-- Bolinhas e linhas serão renderizadas pelo JavaScript -->
                </div>
                
                <!-- Tooltip (invisível por padrão) -->
                <div id="progress-tooltip" class="progress-tooltip hidden">
                    <span class="tooltip-emoji"></span>
                    <span class="tooltip-name"></span>
                    <span class="tooltip-status"></span>
                </div>
            </div>
            <!-- FIM BARRA DE PROGRESSO -->
```

**Verificação:** O HTML deve estar logo após a tag `<main>` e antes do `<aside>`.

---

### Tarefa 1.2: Adicionar CSS da barra de progresso

**Objetivo:** Estilizar o componente com cores, animações e responsividade.

**Localização:** Dentro da tag `<style>` existente no `<head>`.

**Encontre a tag `<style>` e adicione ao FINAL, antes de `</style>`:**

```css
        /* ============================================ */
        /* BARRA DE PROGRESSO - ESTILOS */
        /* ============================================ */
        
        .progress-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 20px;
            position: relative;
        }
        
        .progress-node-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 2;
        }
        
        .progress-node {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 3px solid transparent;
            position: relative;
        }
        
        /* Estados das bolinhas */
        .progress-node--pending {
            background-color: #e5e7eb;
            color: #9ca3af;
            cursor: not-allowed;
        }
        
        .progress-node--in-progress {
            background-color: #3b82f6;
            color: white;
            border-color: #1d4ed8;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
            animation: pulse-progress 2s infinite;
        }
        
        .progress-node--completed {
            background-color: #10b981;
            color: white;
            border-color: #059669;
        }
        
        .progress-node--completed:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }
        
        .progress-node--skipped {
            background-color: #9ca3af;
            color: white;
            border-color: #6b7280;
        }
        
        .progress-node--skipped::after {
            content: '⏭️';
            position: absolute;
            top: -8px;
            right: -8px;
            font-size: 12px;
        }
        
        /* Checkmark para seções completas */
        .progress-node--completed::before {
            content: '✓';
            font-size: 18px;
        }
        
        /* Esconder número quando completo */
        .progress-node--completed .node-number,
        .progress-node--skipped .node-number {
            display: none;
        }
        
        /* Linha de conexão entre bolinhas */
        .progress-line-container {
            flex: 1;
            height: 6px;
            background-color: #e5e7eb;
            margin: 0 -5px;
            position: relative;
            z-index: 1;
        }
        
        .progress-line-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            border-radius: 3px;
            transition: width 0.5s ease;
            width: 0%;
        }
        
        /* Animação de pulsação para seção atual */
        @keyframes pulse-progress {
            0%, 100% {
                box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
            }
            50% {
                box-shadow: 0 0 0 8px rgba(59, 130, 246, 0.1);
            }
        }
        
        /* Tooltip */
        .progress-tooltip {
            position: absolute;
            background-color: #1f2937;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 13px;
            white-space: nowrap;
            z-index: 100;
            pointer-events: none;
            transform: translateX(-50%);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .progress-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: #1f2937;
        }
        
        .progress-tooltip .tooltip-emoji {
            margin-right: 6px;
        }
        
        .progress-tooltip .tooltip-status {
            margin-left: 8px;
            font-size: 11px;
            opacity: 0.8;
        }
        
        /* Label abaixo da bolinha (número da seção) */
        .progress-node-label {
            margin-top: 6px;
            font-size: 11px;
            color: #6b7280;
            font-weight: 500;
        }
        
        .progress-node--in-progress + .progress-node-label,
        .progress-node-wrapper:has(.progress-node--in-progress) .progress-node-label {
            color: #3b82f6;
            font-weight: 700;
        }
        
        /* Responsividade Mobile */
        @media (max-width: 768px) {
            .progress-bar {
                padding: 8px 10px;
            }
            
            .progress-node {
                width: 32px;
                height: 32px;
                font-size: 12px;
            }
            
            .progress-line-container {
                height: 4px;
            }
            
            .progress-node-label {
                font-size: 10px;
            }
            
            .progress-tooltip {
                font-size: 11px;
                padding: 6px 10px;
            }
        }
        
        @media (max-width: 480px) {
            .progress-node {
                width: 28px;
                height: 28px;
                font-size: 11px;
            }
            
            .progress-node--completed::before {
                font-size: 14px;
            }
            
            .progress-node--skipped::after {
                font-size: 10px;
                top: -6px;
                right: -6px;
            }
        }
```

**Verificação:** O CSS deve estar dentro da tag `<style>` existente.

---

### Tarefa 1.3: Adicionar JavaScript da classe ProgressBar

**Objetivo:** Criar a lógica do componente.

**Localização:** Dentro da tag `<script>` existente, ANTES das variáveis de estado da aplicação.

**Encontre este trecho:**
```javascript
    <script>
        // Configuração da API
        const API_URL = window.location.hostname === 'localhost' 
```

**Adicione DEPOIS de `<script>` e ANTES de `// Configuração da API`:**

```javascript
        // ============================================
        // CLASSE PROGRESSBAR - BARRA DE PROGRESSO
        // ============================================
        
        class ProgressBar {
            /**
             * Componente de barra de progresso horizontal
             * Mostra 8 seções com estados: pending, in_progress, completed, skipped
             */
            constructor(containerId, options = {}) {
                this.container = document.getElementById(containerId);
                this.tooltipEl = document.getElementById('progress-tooltip');
                
                // Dados das seções (do sections.js ou passado por opções)
                this.sections = options.sections || (window.SECTIONS_DATA ? window.SECTIONS_DATA.map(s => ({
                    id: s.id,
                    name: s.name,
                    emoji: s.emoji,
                    totalQuestions: s.questions.length + (s.skipQuestion ? 1 : 0)
                })) : []);
                
                // Estado de cada seção
                this.sectionStates = {};
                this.sections.forEach(s => {
                    this.sectionStates[s.id] = {
                        status: 'pending', // pending, in_progress, completed, skipped
                        answeredCount: 0,
                        totalCount: s.totalQuestions
                    };
                });
                
                // Seção atual
                this.currentSectionId = options.currentSection || 1;
                
                // Callback para navegação
                this.onSectionClick = options.onSectionClick || ((sectionId) => {
                    console.log('[ProgressBar] Clicou na seção:', sectionId);
                });
                
                // Renderizar
                if (this.container) {
                    this.render();
                }
            }
            
            /**
             * Renderiza a barra de progresso completa
             */
            render() {
                if (!this.container) return;
                
                this.container.innerHTML = '';
                
                this.sections.forEach((section, index) => {
                    // Wrapper da bolinha
                    const nodeWrapper = document.createElement('div');
                    nodeWrapper.className = 'progress-node-wrapper';
                    
                    // Bolinha
                    const node = document.createElement('div');
                    node.className = 'progress-node';
                    node.dataset.sectionId = section.id;
                    
                    // Número dentro da bolinha
                    const nodeNumber = document.createElement('span');
                    nodeNumber.className = 'node-number';
                    nodeNumber.textContent = section.id;
                    node.appendChild(nodeNumber);
                    
                    // Aplicar estado visual
                    this._applyNodeState(node, section.id);
                    
                    // Eventos
                    node.addEventListener('click', () => this._handleNodeClick(section.id));
                    node.addEventListener('mouseenter', (e) => this._showTooltip(e, section));
                    node.addEventListener('mouseleave', () => this._hideTooltip());
                    
                    nodeWrapper.appendChild(node);
                    
                    // Label abaixo (número)
                    const label = document.createElement('div');
                    label.className = 'progress-node-label';
                    label.textContent = `Seção ${section.id}`;
                    nodeWrapper.appendChild(label);
                    
                    this.container.appendChild(nodeWrapper);
                    
                    // Linha de conexão (exceto após a última)
                    if (index < this.sections.length - 1) {
                        const lineContainer = document.createElement('div');
                        lineContainer.className = 'progress-line-container';
                        lineContainer.dataset.lineAfter = section.id;
                        
                        const lineFill = document.createElement('div');
                        lineFill.className = 'progress-line-fill';
                        lineFill.id = `line-fill-${section.id}`;
                        
                        lineContainer.appendChild(lineFill);
                        this.container.appendChild(lineContainer);
                    }
                });
                
                // Aplicar estados iniciais
                this._updateAllLines();
            }
            
            /**
             * Aplica o estado visual correto à bolinha
             */
            _applyNodeState(node, sectionId) {
                const state = this.sectionStates[sectionId];
                
                // Remover classes anteriores
                node.classList.remove(
                    'progress-node--pending',
                    'progress-node--in-progress',
                    'progress-node--completed',
                    'progress-node--skipped'
                );
                
                // Aplicar classe do estado atual
                node.classList.add(`progress-node--${state.status}`);
            }
            
            /**
             * Atualiza estado de uma seção
             */
            updateSection(sectionId, status, answeredCount = null) {
                if (!this.sectionStates[sectionId]) return;
                
                this.sectionStates[sectionId].status = status;
                if (answeredCount !== null) {
                    this.sectionStates[sectionId].answeredCount = answeredCount;
                }
                
                // Atualizar visual da bolinha
                const node = this.container.querySelector(`[data-section-id="${sectionId}"]`);
                if (node) {
                    this._applyNodeState(node, sectionId);
                }
                
                // Atualizar linhas
                this._updateAllLines();
            }
            
            /**
             * Define a seção atual (em progresso)
             */
            setCurrentSection(sectionId) {
                // Remover status in_progress da seção anterior
                if (this.currentSectionId && this.sectionStates[this.currentSectionId]) {
                    const oldState = this.sectionStates[this.currentSectionId];
                    if (oldState.status === 'in_progress') {
                        oldState.status = 'pending';
                        const oldNode = this.container.querySelector(`[data-section-id="${this.currentSectionId}"]`);
                        if (oldNode) this._applyNodeState(oldNode, this.currentSectionId);
                    }
                }
                
                // Definir nova seção atual
                this.currentSectionId = sectionId;
                this.updateSection(sectionId, 'in_progress');
            }
            
            /**
             * Atualiza o progresso dentro de uma seção
             */
            updateProgress(sectionId, answeredCount, totalCount = null) {
                if (!this.sectionStates[sectionId]) return;
                
                const state = this.sectionStates[sectionId];
                state.answeredCount = answeredCount;
                if (totalCount !== null) {
                    state.totalCount = totalCount;
                }
                
                // Atualizar linha correspondente
                this._updateLineFill(sectionId);
            }
            
            /**
             * Marca seção como completa
             */
            markCompleted(sectionId) {
                this.updateSection(sectionId, 'completed');
                this.sectionStates[sectionId].answeredCount = this.sectionStates[sectionId].totalCount;
                this._updateLineFill(sectionId);
            }
            
            /**
             * Marca seção como pulada
             */
            markSkipped(sectionId) {
                this.updateSection(sectionId, 'skipped');
                this._updateLineFill(sectionId);
            }
            
            /**
             * Atualiza preenchimento de uma linha
             */
            _updateLineFill(sectionId) {
                const lineFill = document.getElementById(`line-fill-${sectionId}`);
                if (!lineFill) return;
                
                const state = this.sectionStates[sectionId];
                let percentage = 0;
                
                if (state.status === 'completed' || state.status === 'skipped') {
                    percentage = 100;
                } else if (state.status === 'in_progress' && state.totalCount > 0) {
                    percentage = (state.answeredCount / state.totalCount) * 100;
                }
                
                lineFill.style.width = `${percentage}%`;
            }
            
            /**
             * Atualiza todas as linhas
             */
            _updateAllLines() {
                this.sections.forEach(section => {
                    this._updateLineFill(section.id);
                });
            }
            
            /**
             * Trata clique em uma bolinha
             */
            _handleNodeClick(sectionId) {
                const state = this.sectionStates[sectionId];
                
                // Só permite clicar em seções já visitadas (completed ou skipped)
                // ou na seção atual
                if (state.status === 'completed' || state.status === 'skipped' || sectionId === this.currentSectionId) {
                    this.onSectionClick(sectionId);
                }
            }
            
            /**
             * Mostra tooltip ao passar mouse
             */
            _showTooltip(event, section) {
                if (!this.tooltipEl) return;
                
                const state = this.sectionStates[section.id];
                
                // Emoji
                const emojiSpan = this.tooltipEl.querySelector('.tooltip-emoji');
                if (emojiSpan) emojiSpan.textContent = section.emoji;
                
                // Nome
                const nameSpan = this.tooltipEl.querySelector('.tooltip-name');
                if (nameSpan) nameSpan.textContent = section.name;
                
                // Status
                const statusSpan = this.tooltipEl.querySelector('.tooltip-status');
                if (statusSpan) {
                    switch (state.status) {
                        case 'completed':
                            statusSpan.textContent = '✓ Completa';
                            break;
                        case 'skipped':
                            statusSpan.textContent = '⏭️ Pulada';
                            break;
                        case 'in_progress':
                            statusSpan.textContent = `${state.answeredCount}/${state.totalCount}`;
                            break;
                        default:
                            statusSpan.textContent = 'Pendente';
                    }
                }
                
                // Posicionar tooltip
                const rect = event.target.getBoundingClientRect();
                const containerRect = this.container.parentElement.getBoundingClientRect();
                
                this.tooltipEl.style.left = `${rect.left - containerRect.left + rect.width / 2}px`;
                this.tooltipEl.style.top = `${rect.top - containerRect.top - 45}px`;
                
                this.tooltipEl.classList.remove('hidden');
            }
            
            /**
             * Esconde tooltip
             */
            _hideTooltip() {
                if (this.tooltipEl) {
                    this.tooltipEl.classList.add('hidden');
                }
            }
            
            /**
             * Reseta a barra de progresso
             */
            reset() {
                this.sections.forEach(s => {
                    this.sectionStates[s.id] = {
                        status: 'pending',
                        answeredCount: 0,
                        totalCount: s.totalQuestions
                    };
                });
                this.currentSectionId = 1;
                this.render();
            }
        }
        
        // ============================================
        // FIM CLASSE PROGRESSBAR
        // ============================================
        
```

**Verificação:** O código deve estar dentro da tag `<script>`, antes das variáveis globais.

---

### Tarefa 1.4: Adicionar carregamento do sections.js

**Objetivo:** Garantir que o arquivo de configuração das seções seja carregado.

**Localização:** No `<head>`, antes do Tailwind CSS.

**Encontre este trecho:**
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BO Inteligente - Tráfico de Drogas</title>
    <script src="https://cdn.tailwindcss.com"></script>
```

**Adicione ANTES de `<script src="https://cdn.tailwindcss.com">`:**
```html
    <!-- Dados das seções -->
    <script src="js/data/sections.js"></script>
```

**Resultado:**
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BO Inteligente - Tráfico de Drogas</title>
    <!-- Dados das seções -->
    <script src="js/data/sections.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
```

---

### Tarefa 1.5: Inicializar ProgressBar para teste

**Objetivo:** Adicionar código de teste para verificar se o componente funciona.

**Localização:** No final da tag `<script>`, dentro da função `window.addEventListener('load', ...)`.

**Encontre este trecho:**
```javascript
        // Inicializar
        window.addEventListener('load', () => {
            initializeSidebar();
            startSession();
        });
```

**Substitua por:**
```javascript
        // Inicializar
        window.addEventListener('load', () => {
            // ============================================
            // INICIALIZAR BARRA DE PROGRESSO (NOVO)
            // ============================================
            const progressBar = new ProgressBar('progress-bar', {
                onSectionClick: (sectionId) => {
                    console.log('[App] Navegando para seção:', sectionId);
                    // TODO: Implementar navegação real na Fase 4
                }
            });
            
            // Expor para debug no console
            window.progressBar = progressBar;
            
            // TESTE: Simular estados diferentes (remover depois)
            setTimeout(() => {
                progressBar.setCurrentSection(1);
            }, 500);
            
            setTimeout(() => {
                progressBar.updateProgress(1, 2, 7); // 2 de 7 respondidas
            }, 1000);
            
            setTimeout(() => {
                progressBar.markCompleted(1);
                progressBar.setCurrentSection(2);
            }, 2000);
            
            setTimeout(() => {
                progressBar.markSkipped(2);
                progressBar.setCurrentSection(3);
            }, 3000);
            
            setTimeout(() => {
                progressBar.updateProgress(3, 3, 5); // 3 de 5 respondidas
            }, 4000);
            
            console.log('[App] ProgressBar inicializada. Use window.progressBar para testar.');
            // ============================================
            
            initializeSidebar();
            startSession();
        });
```

**Nota:** O código de teste com `setTimeout` será removido na Fase 4 quando integrarmos com o sistema real.

---

### Tarefa 1.6: Testar no navegador

**Objetivo:** Verificar se o componente funciona corretamente.

**Passos:**

1. Iniciar servidor local:
```bash
cd docs
python -m http.server 3000
```

2. Abrir `http://localhost:3000` no navegador

3. **Verificar visualmente:**
   - [ ] Barra de progresso aparece acima do chat
   - [ ] 8 bolinhas numeradas estão visíveis
   - [ ] Linhas conectam as bolinhas
   - [ ] Animação de teste roda (seções mudam de estado automaticamente)

4. **Verificar no console (F12):**
```javascript
// Deve mostrar a instância do ProgressBar
console.log(window.progressBar);

// Testar métodos manualmente
progressBar.markCompleted(4);
progressBar.setCurrentSection(5);
progressBar.updateProgress(5, 2, 6);
progressBar.markSkipped(6);
```

5. **Verificar tooltips:**
   - Passar o mouse sobre cada bolinha
   - Deve mostrar emoji + nome da seção + status

6. **Verificar clique:**
   - Clicar em seção completa/pulada → console deve logar
   - Clicar em seção pendente → nada deve acontecer (cursor bloqueado)

7. **Verificar responsividade:**
   - Reduzir largura da janela para < 768px
   - Bolinhas devem ficar menores
   - Tudo deve continuar visível e funcional

---

### Tarefa 1.7: Commit da Fase 1

**Objetivo:** Salvar o progresso.

**Comandos:**
```bash
cd /caminho/para/bo-assistant
git add .
git status
# Deve mostrar: docs/index.html modificado

git commit -m "feat: implementar barra de progresso horizontal (Fase 1)

- Criar componente ProgressBar com 8 estados de seção
- Adicionar CSS com animações e responsividade
- Implementar tooltips com nome/emoji da seção
- Adicionar navegação por clique em seções visitadas
- Carregar sections.js com dados das seções
- Incluir código de teste (será removido na Fase 4)"

git push
```

---

## ✅ Checklist Final da Fase 1

Antes de prosseguir para a Fase 2, confirme:

- [ ] HTML da barra de progresso adicionado
- [ ] CSS com todos os estados e animações
- [ ] Classe ProgressBar implementada com todos os métodos
- [ ] Script sections.js sendo carregado
- [ ] Teste visual: 8 bolinhas aparecem
- [ ] Teste visual: animação de demonstração funciona
- [ ] Teste visual: tooltips aparecem ao hover
- [ ] Teste visual: responsivo em mobile
- [ ] Teste no console: métodos funcionam
- [ ] Commit feito e pushado

---

## 🐛 Troubleshooting

### Barra não aparece
- Verificar se o HTML foi adicionado no lugar correto (dentro de `<main>`)
- Verificar console por erros de JavaScript
- Verificar se `sections.js` está carregando (deve logar no console)

### Erro "ProgressBar is not defined"
- Verificar se a classe foi adicionada ANTES das variáveis globais
- Verificar se não há erro de sintaxe no JavaScript

### Tooltips não aparecem
- Verificar se o elemento `#progress-tooltip` existe no HTML
- Verificar se o CSS do tooltip está presente

### Animação não funciona
- Verificar se o código de teste com `setTimeout` foi adicionado
- Verificar console por erros

### Bolinhas muito grandes/pequenas no mobile
- Verificar se as media queries CSS foram adicionadas

---

## ⏭️ Próxima Fase

**Fase 2: Container de Seção**
- Modelo: 🟢 Haiku
- Arquivo: `FASE_2_CONTAINER_SECAO.md`
- Objetivo: Criar container que gerencia uma seção independente (chat + texto gerado)

---

## 📚 Referências

Arquivos na pasta `redesign/`:
- `PROPOSTA_REDESIGN_UX_BO_INTELIGENTE.md` - Seção "Barra de Progresso"
- `PLANO_IMPLEMENTACAO_REDESIGN_UX.md` - Fase 1 detalhada

---

*Documento gerado em 31/12/2025*  
*Para execução com Claude Haiku*

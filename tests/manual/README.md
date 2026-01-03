# Testes Manuais - BO Inteligente

Esta pasta contém testes automatizados end-to-end (e2e) usando Playwright para validação manual do fluxo completo da aplicação.

## 📋 Testes Disponíveis

### 1. TESTE_FINAL_3_SECOES.py ⭐ **ATUALIZADO**
**Descrição**: Teste completo do caminho feliz com todas as 3 seções ativas + validação das 4 melhorias implementadas.

**Cobertura**:
- Seção 1: 13 perguntas (incluindo follow-ups 1.5.1, 1.5.2, 1.9.1, 1.9.2)
- Seção 2: 12 perguntas (2.2 a 2.13, skip automático 2.1)
- Seção 3: 6 perguntas (3.2 a 3.6.1, skip automático 3.1)
- Validação de textos gerados pelo Groq
- Validação da tela final com 3 seções individuais
- **NOVO**: Validação da bolinha "BO Final" (Tarefa 1) - estados locked/completed
- **NOVO**: Validação do tooltip inteligente (Tarefa 3) - posicionamento correto
- **NOVO**: Validação do modal de confirmação customizado (Tarefa 2)

**Tempo médio**: ~90 segundos (incluindo novas validações)

### 2. TESTE_FINAL_SKIP_SECAO2.py
**Descrição**: Teste com skip da seção 2 (não havia veículo).

**Cobertura**:
- Seção 1: 13 perguntas
- Seção 2: PULADA (clica no botão "Não havia veículo")
- Seção 3: 6 perguntas
- Validação da tela final com apenas 2 seções (S1 e S3)
- Validação do filtro de seções puladas

**Tempo médio**: ~50 segundos

### 3. TESTE_DRAFT_MODAL.py 🆕
**Descrição**: Teste dedicado para validar correções do DraftModal (Tarefa 4).

**Cobertura**:
- ✅ Modal NÃO aparece com localStorage vazio
- ✅ Modal NÃO aparece com draft vazio (sem respostas)
- ✅ Modal APARECE com draft válido (com respostas salvas)
- ✅ Preview mostra seções e contadores de perguntas
- ✅ Preview lista todas as respostas salvas (formato: 1.1: texto...)
- ✅ Botão "Começar Novo" limpa draft do localStorage
- ✅ Botão "Continuar" restaura respostas nos inputs

**Tempo médio**: ~20 segundos

### 4. TESTE_COMPLETO_E2E.py ⭐ **NOVO - TESTE DEFINITIVO**
**Descrição**: Teste end-to-end completo que valida TODAS as 4 melhorias + fluxo completo com navegação bidirecional.

**Cobertura Completa**:

#### 🎯 Fluxo de 9 Fases:
1. **Fase 1 - Rascunho**: Responder 3 perguntas → F5 → Validar DraftModal aparece e restaura
2. **Fase 2 - Completar S1**: Follow-ups condicionais (1.5=NÃO, 1.9=SIM) + validar texto Groq
3. **Fase 3 - Tooltips**: Validar 100% visíveis em TODAS as 4 bolinhas (S1, S2, S3, BO Final)
4. **Fase 4 - Skip S2**: Pular seção 2 + validar texto Groq skip reason
5. **Fase 5 - S3 Parcial**: Responder 3.2-3.5 (parar antes da última)
6. **Fase 6 - Navegação**: Clicar bolinhas 1↔2↔3 e validar persistência de dados
7. **Fase 7 - Completar S3**: Responder restante + validar texto Groq
8. **Fase 8 - Bolinha Final**: Validar locked→completed + clicar e ir para FinalScreen
9. **Fase 9 - Tela Final**: Validar estrutura + Modal de Confirmação customizado

#### ✅ Validações Críticas:
- **DraftModal**: Aparece após 3 respostas, preview correto, restauração funciona
- **Tooltips**: 100% dentro do viewport (bbox completo), classes CSS corretas
- **Texto Groq**: Valida em CADA seção (S1, S2 skip, S3) - detecta placeholders
- **Navegação**: Persistência de estado e respostas entre seções
- **Follow-ups**: Valida lógica condicional (1.5=NÃO não aparece, 1.9=SIM aparece)
- **Bolinha BO Final**: Transição locked→completed, cursor, ícone, clique funciona
- **Modal Confirmação**: Customizado (não native), botões funcionam, limpa localStorage

#### 📸 9 Screenshots Automáticos:
1. `01-draft-modal.png` - DraftModal com 3 respostas
2. `02-s1-completed.png` - Seção 1 completa com texto Groq
3. `03-tooltips.png` - Tooltips 100% visíveis
4. `04-s2-skipped.png` - Seção 2 pulada (amarela)
5. `05-s3-parcial.png` - Seção 3 parcial (in_progress)
6. `06-s3-completed.png` - Seção 3 completa
7. `07-bolinha-final-completed.png` - Bolinha verde com ✓
8. `08-final-screen.png` - Tela final (2 seções)
9. `09-modal-confirmacao.png` - Modal customizado

**Tempo médio**: ~2-3 minutos (incluindo esperas do Groq)

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install playwright
playwright install chromium
```

### Iniciar o Backend
```bash
python backend/main.py
```

### Executar os Testes
```bash
# ⭐ TESTE DEFINITIVO - Completo E2E (RECOMENDADO)
python tests/manual/TESTE_COMPLETO_E2E.py

# Teste completo (3 seções) + validação das 4 melhorias
python tests/manual/TESTE_FINAL_3_SECOES.py

# Teste com skip seção 2
python tests/manual/TESTE_FINAL_SKIP_SECAO2.py

# Teste do DraftModal (Tarefa 4)
python tests/manual/TESTE_DRAFT_MODAL.py

# Teste rápido (apenas melhorias, sem fluxo)
python tests/manual/TESTE_MELHORIAS_RAPIDO.py
```

## 📊 Relatórios

Os relatórios são gerados automaticamente após cada execução:
- `RELATORIO_TESTE_E2E.md` - ⭐ Relatório do teste definitivo completo E2E 🆕
- `RELATORIO_TESTE_FINAL.md` - Relatório do teste completo (3 seções + 4 melhorias)
- `RELATORIO_TESTE_SKIP_SECAO2.md` - Relatório do teste com skip
- `RELATORIO_DRAFT_MODAL.md` - Relatório do teste do DraftModal
- `RELATORIO_MELHORIAS_RAPIDO.md` - Relatório do teste rápido

## 🎯 O Que é Validado

### Tela Final
- ✅ Número correto de caixas de seção (3 ou 2 dependendo do skip)
- ✅ Botões "Copiar Seção X" individuais
- ✅ Botão "Copiar BO Completo (Todas Seções)"
- ✅ Botão "Iniciar Novo BO"
- ✅ Conteúdo visível em todas as seções
- ✅ Filtro correto de seções puladas

### Fluxo
- ✅ Navegação entre seções
- ✅ Geração de texto pelo Groq
- ✅ Skip de seções
- ✅ Transição para tela final

### 🆕 4 Melhorias (v0.13.2)

#### Tarefa 1: Bolinha "BO Final" no ProgressBar
- ✅ Bolinha aparece imediatamente (sempre visível)
- ✅ Estado LOCKED (cinza com 🔒) quando seções incompletas
- ✅ Cursor `not-allowed` quando locked (não clicável)
- ✅ Estado COMPLETED (verde com ✓) quando todas seções completas
- ✅ Cursor `pointer` quando completed (clicável)
- ✅ Clique navega para tela final quando completed
- ✅ Linha de conexão (0% locked, 100% completed)

#### Tarefa 2: Modal de Confirmação Customizado
- ✅ Modal customizado aparece (não native `window.confirm()`)
- ✅ Estilo consistente com DraftModal (reutiliza CSS)
- ✅ Título correto: "Iniciar Novo BO"
- ✅ Ícone correto: 🔄
- ✅ Botão "Confirmar" com estilo danger (vermelho)
- ✅ Botão "Cancelar" fecha modal sem limpar
- ✅ ESC fecha modal
- ✅ Clique fora fecha modal

#### Tarefa 3: Tooltip Inteligente
- ✅ Tooltip não aparece fora da tela (top negativo)
- ✅ Posicionamento dinâmico (acima ou abaixo da bolinha)
- ✅ Seta aponta corretamente (`.progress-tooltip--top` ou `--bottom`)
- ✅ Tooltip da bolinha BO Final mostra texto correto

#### Tarefa 4: DraftModal Corrigido
- ✅ Modal NÃO aparece com localStorage vazio
- ✅ Modal NÃO aparece com draft vazio (sem respostas)
- ✅ Modal APARECE com draft válido (com respostas)
- ✅ Preview mostra seções com contadores (X/Y perguntas)
- ✅ Preview lista respostas no formato (1.1: texto...)
- ✅ Botão "Começar Novo" limpa localStorage
- ✅ Botão "Continuar" restaura respostas

## 📸 Screenshots

Os testes capturam screenshots automaticamente em `docs/screenshots/v0.13.2/`:
- `FINAL-s1.png` / `SKIP-s1.png` - Após completar seção 1
- `FINAL-s2.png` / `SKIP-s2-skipped.png` - Após completar/pular seção 2
- `FINAL-s3.png` - Após completar seção 3
- `DEBUG-before-final.png` - Antes de carregar tela final
- `FINAL-complete.png` - Tela final completa
- `DRAFT-MODAL-preview.png` - Preview do DraftModal com respostas 🆕

## 🐛 Detecção de Bugs

Os testes automaticamente detectam e reportam erros em:
- Estrutura do DOM (elementos faltando)
- Estilos CSS (classes incorretas, cursor errado)
- Comportamento de cliques (navegação, modais)
- Posicionamento de elementos (tooltip fora da tela)
- LocalStorage (draft não limpo, respostas não restauradas)
- Conteúdo de texto (títulos, mensagens, ícones)

Se um bug for encontrado durante os testes, será:
1. ✅ Reportado no log com ❌ e contador de erros incrementado
2. ✅ Incluído no relatório markdown com detalhes
3. ✅ Screenshot capturado (se aplicável)

## 📝 Estrutura do Log

Cada validação gera log detalhado com:
```
[HH:MM:SS] === TAREFA X: Nome da Melhoria ===
[HH:MM:SS] ✅ Validação passou
[HH:MM:SS] ❌ ERRO: Descrição do problema
[HH:MM:SS] ⚠️  AVISO: Comportamento inesperado mas não crítico
[HH:MM:SS] === Tarefa X validada ===
```

Exemplo de erro detectado:
```
[14:30:45] ❌ ERRO: Bolinha deveria estar LOCKED (cinza)
[14:30:45] ❌ ERRO: Cursor deveria ser 'not-allowed', mas é 'pointer'
```

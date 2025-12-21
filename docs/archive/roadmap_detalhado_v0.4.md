# 🗺️ Roadmap Detalhado - BO Assistant

## 🎯 Fase Atual: v0.2.1 em Produção ✅

**Status:** Seção 1 completa com edição de respostas implementada  
**Deploy:** ✅ Backend (Render) + Frontend (GitHub Pages) funcionando  
**Validação:** ✅ Gemini aprovado pelo Sgt. Claudio Moreira

---

## 📋 Sprint 1: Melhorias de UX (Estimativa: 5-7 horas) 🔥 ATUAL

### 🔥 1.1 - Editar Resposta Anterior ✅ CONCLUÍDO
**Status:** ✅ Implementado e em produção (v0.2.1)  
**Data conclusão:** 05/12/2024  
**Impacto no Usuário:** ⭐⭐⭐⭐⭐ (Crítico)

**Funcionalidades implementadas:**
- ✅ Endpoint PUT /chat/{session_id}/answer/{step}
- ✅ Validação de resposta editada antes de salvar
- ✅ Mantém contexto da sessão após edição
- ✅ Testado e funcionando em produção

---

### 📜 1.2 - Histórico Visual de Perguntas/Respostas ⏳ EM ANDAMENTO
**Problema:** Usuário perde noção do que já respondeu  
**Impacto no Usuário:** ⭐⭐⭐⭐ (Alto)  
**Tempo Estimado:** 1-1.5 horas

**Funcionalidades:**
- [ ] Sidebar ou accordion com todas as perguntas/respostas
- [ ] Indicador de progresso: "📝 Pergunta 3/6"
- [ ] Scroll automático para pergunta atual
- [ ] Cards colapsáveis para economizar espaço
- [ ] Status visual: ✅ Respondida | ⏳ Atual | ⬜ Pendente

**Mockup Visual:**
```
┌─────────────────────────┐
│ 📝 Progresso: 3/6      │
├─────────────────────────┤
│ ✅ 1. Data e hora      │
│ └─ "22/12/2024, 19h03" │
├─────────────────────────┤
│ ✅ 2. Acionamento      │
│ └─ "Via COPOM..."      │
├─────────────────────────┤
│ ⏳ 3. Deslocamento     │ ← ATUAL
│ └─ [Aguardando...]     │
├─────────────────────────┤
│ ⬜ 4. Endereço         │
├─────────────────────────┤
│ ⬜ 5. Contexto         │
├─────────────────────────┤
│ ⬜ 6. Observação       │
└─────────────────────────┘
```

**Implementação Técnica:**
```javascript
// Frontend: manter array de perguntas/respostas
const conversationState = {
  questions: [
    { id: 1, text: "Data e hora", answer: "22/12/2024, 19h03", status: "completed" },
    { id: 2, text: "Acionamento", answer: "Via COPOM", status: "completed" },
    { id: 3, text: "Deslocamento", answer: null, status: "current" },
    { id: 4, text: "Endereço", answer: null, status: "pending" },
    // ...
  ]
};
```

---

### 💾 1.3 - Salvar Rascunho no Navegador (MÉDIA PRIORIDADE)
**Problema:** Usuário é interrompido e perde tudo  
**Impacto no Usuário:** ⭐⭐⭐⭐ (Alto)  
**Tempo Estimado:** 1-1.5 horas

**Funcionalidades:**
- [ ] Auto-save a cada resposta no `localStorage`
- [ ] Botão manual "💾 Salvar Rascunho"
- [ ] Ao abrir página: "Você tem um rascunho salvo de [data]. Quer continuar?"
- [ ] Botão "🗑️ Descartar Rascunho"
- [ ] Expiração automática após 7 dias

**Implementação Técnica:**
```javascript
// Frontend: localStorage
const draft = {
  timestamp: "2024-12-05T19:03:00Z",
  session_id: "abc-123",
  answers: {
    1: "22/12/2024, 19h03",
    2: "Via COPOM denúncia anônima",
    // ...
  },
  current_question: 3
};

localStorage.setItem('bo_draft', JSON.stringify(draft));

// Ao carregar página
const savedDraft = localStorage.getItem('bo_draft');
if (savedDraft) {
  showDraftDialog(JSON.parse(savedDraft));
}
```

**Validação de Sucesso:**
- [ ] Fecha navegador, reabre, rascunho ainda está lá
- [ ] Salva, espera 8 dias, rascunho expira
- [ ] Descarta rascunho, localStorage limpo

---

### 🎨 1.4 - Melhorias Visuais (BAIXA PRIORIDADE)
**Problema:** Interface muito básica  
**Impacto no Usuário:** ⭐⭐⭐ (Médio)  
**Tempo Estimado:** 1-2 horas

**Funcionalidades:**
- [ ] Loading spinner profissional (tipo GitHub)
- [ ] Animações suaves (fade-in/fade-out)
- [ ] Toast notifications ao invés de mensagens no chat
- [ ] Tema inspirado na identidade visual da PMMG
  - Cores: Azul marinho (#003366), Amarelo (#FFD700)
  - Logo da PM (se possível)
- [ ] Favicon personalizado
- [ ] Responsive melhorado (mobile-first)

**Antes vs Depois:**
```
ANTES:
[Carregando...]  ← texto simples

DEPOIS:
  ⏳ Processando resposta...
  [====>    ] 45%  ← barra de progresso animada
```

**Bibliotecas Sugeridas:**
- **Toastify.js** - Notifications bonitas
- **Animate.css** - Animações prontas
- **Lottie** - Loading animations

---

## 🧪 Sprint 2: Comparação de LLMs (Estimativa: 8-12 horas) ⚡ ADIADO

**Decisão:** Gemini 2.5 Flash foi aprovado pelo Sgt. Claudio Moreira.  
**Status:** 🟡 Adiado até ser necessário  
**Quando fazer:** Apenas se houver problemas com qualidade do Gemini em seções futuras

### 🤖 2.1 - Integrar Claude (Anthropic) ⚡ BACKLOG
**Objetivo:** Comparar qualidade Gemini vs Claude  
**Tempo Estimado:** 3-4 horas

**Tasks:**
- [ ] Criar conta Anthropic
- [ ] Obter API key
- [ ] Implementar `claude_service.py` no backend
- [ ] Adaptar mesmo prompt usado no Gemini
- [ ] Adicionar seletor de LLM no frontend

**Código Backend:**
```python
# backend/llm_providers/claude_service.py
import anthropic

def generate_text_claude(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text
```

---

### 🧠 2.2 - Integrar GPT-4 (OpenAI) ⚡ BACKLOG
**Objetivo:** Adicionar terceiro ponto de comparação  
**Tempo Estimado:** 2-3 horas

**Custo Estimado por Geração:**
- **Gemini 2.5 Flash:** ~$0.0001 (muito barato) ✅ ATUAL
- **Claude Sonnet 4:** ~$0.003
- **GPT-4o:** ~$0.005

---

### 📊 2.3 - Dashboard de Comparação ⚡ BACKLOG
**Objetivo:** Visualizar diferenças lado a lado  
**Tempo Estimado:** 3-5 horas

**Mockup:**
```
┌──────────────────────┬──────────────────────┬──────────────────────┐
│ Gemini 2.5 Flash     │ Claude Sonnet 4      │ GPT-4o               │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ No dia domingo, 22...│ No dia domingo, 22...│ No dia domingo, 22...│
│ (texto gerado)       │ (texto gerado)       │ (texto gerado)       │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ [👍 Melhor] [👎 Pior]│ [👍 Melhor] [👎 Pior]│ [👍 Melhor] [👎 Pior]│
│ [📋 Copiar]          │ [📋 Copiar]          │ [📋 Copiar]          │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

---

## 📝 Sprint 3: Seções 2-8 do BO (Estimativa: 20-30 horas) 📅 PRÓXIMO

### 🚗 3.1 - Seção 2: Abordagem a Veículo
**Status:** 🔜 Próximo após Sprint 1  
**Tempo Estimado:** 4-5 horas

**Perguntas:**
1. Tipo de abordagem (tática de alto risco ou não-tática)
2. Comandos verbais dados aos ocupantes
3. Reação dos abordados (colaborativa, resistência passiva, ativa)
4. Ordem de saída do veículo (motorista primeiro, depois passageiros)

**Implementação:**
- Adicionar 4 novas perguntas ao `state_machine.py`
- Criar validações específicas no `validator.py`
- Adaptar prompt do Gemini para Seção 2
- Testar geração de texto

---

### 👀 3.2 - Seção 3: Campana
**Tempo Estimado:** 3-4 horas

**Perguntas:**
1. Tempo de observação (ex: 15 minutos)
2. Ponto de observação (ex: viatura estacionada a 50m)
3. Movimentação observada durante campana
4. Momento que decidiu intervir (gatilho da ação)

---

### 🏠 3.3 - Seção 4: Entrada em Domicílio
**Tempo Estimado:** 4-5 horas

**Perguntas:**
1. Fundamento legal (flagrante, mandado judicial, consentimento)
2. Quem autorizou/permitiu entrada (morador, mandado de qual juiz)
3. Forma de entrada (porta aberta, arrombamento, consentida)

---

### ⚖️ 3.4 - Seção 5: Fundada Suspeita
**Tempo Estimado:** 5-6 horas (mais complexa)

**Perguntas:**
1. Justificativa técnica (nervosismo, fuga, denúncia, flagrante)
2. Elementos concretos observados (bulto na cintura, sacola, etc.)
3. Jurisprudência aplicável (súmulas STF/STJ)

---

### 💪 3.5 - Seção 6: Reação e Uso da Força
**Tempo Estimado:** 4-5 horas

**Perguntas:**
1. Tipo de resistência (passiva, ativa, agressão)
2. Nível de força empregado (verbal, física, instrumentos)
3. Gradação da força (proporcionalidade)

---

### 📦 3.6 - Seção 7: Apreensões
**Tempo Estimado:** 5-6 horas (mais trabalhosa)

**Perguntas (repetir para cada item):**
1. Descrição do item (ex: "23 pedras de crack")
2. Local de apreensão (ex: "bolso direito da calça")
3. Quem estava com item (ex: "indivíduo 1, João da Silva")

---

### 🚓 3.7 - Seção 8: Condução
**Tempo Estimado:** 3-4 horas

**Perguntas:**
1. Para onde foram conduzidos (delegacia, hospital, etc.)
2. Quem foi conduzido (nomes, qualificações)
3. Veículos utilizados na condução

---

## 🔐 Sprint 4: Autenticação & Persistência (Estimativa: 15-20 horas) 🔮 FUTURO

### 👤 4.1 - Sistema de Login
**Funcionalidades:**
- [ ] Cadastro de usuário (email + senha)
- [ ] Login/Logout
- [ ] Sessões seguras (JWT tokens)
- [ ] Recuperação de senha

**Stack Sugerida:**
- **Firebase Auth** (mais rápido) OU
- **FastAPI + PostgreSQL** (mais controle)

---

### 💾 4.2 - Banco de Dados
**Objetivo:** Salvar BOs gerados, histórico do usuário  

**Tabelas:**
```sql
-- Usuários
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  pm_registration VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- BOs Salvos
CREATE TABLE saved_bos (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title VARCHAR(255),
  sections JSONB,
  llm_provider VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Avaliações de LLM
CREATE TABLE llm_ratings (
  id UUID PRIMARY KEY,
  bo_id UUID REFERENCES saved_bos(id),
  llm_provider VARCHAR(50),
  rating INT,
  comment TEXT,
  created_at TIMESTAMP
);
```

---

### 📊 4.3 - Dashboard do Usuário
**Funcionalidades:**
- [ ] Lista de BOs salvos
- [ ] Filtros (data, tipo, status)
- [ ] Busca por palavra-chave
- [ ] Estatísticas: BOs criados, LLM favorito, etc.

---

## 🚀 Sprint 5: Features Avançadas (Estimativa: 10-15 horas) 🔮 FUTURO

### 📄 5.1 - Exportação para Word/PDF
**Funcionalidades:**
- [ ] Botão "📥 Baixar DOCX"
- [ ] Botão "📥 Baixar PDF"
- [ ] Template formatado (cabeçalho PM, fonte oficial)
- [ ] Metadados (data de geração, versão do sistema)

**Bibliotecas:**
- **Python:** `python-docx`, `reportlab`
- **Frontend:** `jsPDF` (gerar no navegador)

---

### 🔄 5.2 - Editar BO Após Geração
**Funcionalidades:**
- [ ] Editor WYSIWYG (tipo Google Docs)
- [ ] Histórico de edições
- [ ] Salvar versões (v1, v2, v3...)

**Bibliotecas:**
- **Quill.js** ou **TinyMCE**

---

### 🎤 5.3 - Entrada de Voz (FUTURO)
**Funcionalidades:**
- [ ] Botão 🎤 para gravar resposta
- [ ] Transcrição automática (Whisper API ou Web Speech API)
- [ ] Edição do texto transcrito antes de enviar

---

## 📱 Sprint 6: App Mobile (FUTURO DISTANTE) 🔮

### 📲 6.1 - PWA (Progressive Web App)
**Vantagens:**
- Funciona em qualquer celular
- Não precisa App Store
- Um código só (web = mobile)

**Funcionalidades PWA:**
- [ ] Instalável (ícone na tela inicial)
- [ ] Funciona offline (básico)
- [ ] Notificações push
- [ ] Câmera para fotos da cena

---

### 🍎 6.2 - App Nativo (Muito Futuro)
**Opções:**
- **React Native** - JavaScript
- **Flutter** - Dart (Google)
- **Swift** (iOS) + Kotlin (Android) - Nativo puro

**Tempo Estimado:** 40-60 horas (projeto grande)

---

## 🎯 Priorização Atual (Ordem de Execução)

### ✅ Concluído
1. ✅ Seção 1 em produção (v0.1.6)
2. ✅ Edição de respostas (v0.2.1)
3. ✅ Fix imports Render
4. ✅ Deploy estável

### 🔥 Agora (Dezembro 2024)
5. **1.2 - Histórico Visual** ⏳ EM ANDAMENTO
6. **1.3 - Salvar Rascunho**
7. **1.4 - Melhorias Visuais**
8. **Validação com Cláudio** (features UX)

### 📅 Janeiro 2025
9. **3.1 - Seção 2: Abordagem a Veículo**
10. **3.2 - Seção 3: Campana**
11. **3.3 - Seção 4: Entrada em Domicílio**
12. **Validação com Cláudio** (Seções 2-4)

### 📅 Fevereiro 2025
13. **3.4 - Seção 5: Fundada Suspeita**
14. **3.5 - Seção 6: Uso da Força**
15. **3.6 - Seção 7: Apreensões**
16. **3.7 - Seção 8: Condução**
17. **Validação com Cláudio** (BO completo)

### 📅 Março+ 2025
18. **Sprint 2: Comparação LLMs** (se necessário)
19. **Sprint 4: Autenticação**
20. **Sprint 5: Features Avançadas**

---

## 📊 Estimativas Totais

| Sprint | Descrição | Horas | Prioridade | Status |
|--------|-----------|-------|------------|--------|
| Sprint 1 | Melhorias UX | 5-7h | 🔥 Alta | ⏳ Em andamento |
| Sprint 2 | Comparação LLMs | 8-12h | ⚡ Baixa | 🟡 Adiado |
| Sprint 3 | Seções 2-8 | 20-30h | ⭐ Alta | 🔜 Próximo |
| Sprint 4 | Auth & DB | 15-20h | ⚡ Baixa | 🔮 Futuro |
| Sprint 5 | Features Avançadas | 10-15h | ⚡ Baixa | 🔮 Futuro |
| Sprint 6 | Mobile | 40-60h | 💡 Muito futuro | 🔮 Futuro |
| **TOTAL** | | **98-144h** | | |

---

## 🎯 Critérios de Sucesso por Sprint

### Sprint 1 ✅
- [ ] Usuário vê claramente progresso (3/6)
- [ ] Interface mostra todas respostas dadas
- [ ] Rascunho é salvo automaticamente
- [ ] Visual mais profissional (cores PMMG)
- [ ] Cláudio aprova melhorias de UX

### Sprint 3 ✅
- [ ] Todas as 8 seções implementadas
- [ ] BO completo gerado (ponta a ponta)
- [ ] Cláudio valida qualidade de TODAS as seções
- [ ] Texto gerado está pronto para ser copiado direto para sistema oficial

### Sprint 2 ✅ (Se necessário)
- [ ] 3 LLMs funcionando (Gemini, Claude, GPT)
- [ ] Dashboard de comparação operacional
- [ ] Cláudio avalia qual LLM é melhor para cada caso
- [ ] Decisão: qual LLM usar como padrão?

---

## 🔄 Processo de Validação com Cláudio

A cada entrega:
1. **Demo ao vivo** (compartilhar tela)
2. **Cláudio testa** com casos reais
3. **Feedback estruturado:**
   - O que está bom?
   - O que precisa ajustar?
   - Casos extremos (edge cases)
4. **Iteração** baseada no feedback
5. **Aprovação final** antes de próximo sprint

---

## 📝 Changelog

### v0.2.1 (05/12/2024)
- ✅ Adiciona edição de respostas anteriores
- ✅ Fix imports compatíveis com local e Render
- ✅ Endpoint PUT /chat/{session_id}/answer/{step}
- ✅ Deploy estável em produção

### v0.1.6 (02/12/2024)
- ✅ Seção 1 completa (6 perguntas)
- ✅ Validação inteligente
- ✅ Enriquecimento de datas
- ✅ Geração com Gemini 2.5 Flash
- ✅ Deploy inicial no Render + GitHub Pages

---

**Versão:** 2.1  
**Última atualização:** 05/12/2024  
**Status:** 📋 Roadmap atualizado com v0.2.1 e Sprint 1 em andamento
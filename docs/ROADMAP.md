# Roadmap - BO Inteligente

## Versão Atual: v0.7.0
**Última atualização**: 21/12/2025

---

## 🔄 Status da Fase 2

**Fase 2 (Seções 3-8)** iniciada com **v0.7.0 - Seção 3: Campana** completamente implementada!

### ✅ Status da Fase 1 (Concluída)

A **Fase 1 (Validação e Polimento)** foi **100% concluída** na v0.6.4.

**Marcos alcançados:**
- ✅ Seção 1 (Contexto da Ocorrência) + Seção 2 (Abordagem a Veículo) implementadas e funcionais
- ✅ Sistema de rascunhos com sincronização em bloco (endpoint `/sync_session`)
- ✅ Validação inteligente de respostas + logs completos + sistema de feedback
- ✅ Interface responsiva (desktop/tablet/mobile)
- ✅ Integração Groq Llama 3.3 70B (14.4k req/dia)

**Histórico detalhado:** Ver [CHANGELOG.md](../CHANGELOG.md#-histórico-de-features-por-fase)

---

## 📋 Backlog - Melhorias Incrementais

### Melhorias UX (Prioridade Baixa)
- [ ] **Mini resumo ao iniciar seção**
  - Mostrar 3-4 respostas-chave da seção anterior
  - Card amarelo colapsável em mobile
- [ ] **Templates de locais frequentes**
  - Salvar locais favoritos
  - Auto-completar endereços
- [ ] **Histórico de BOs**
  - Listar BOs anteriores do usuário
  - Reutilizar dados de ocorrências similares
- [ ] **Sugestões inteligentes**
  - Sugerir facções baseado no local
  - Auto-preencher prefixos baseado em histórico

---

## 🚀 Fase 2 - Seções 3-8 (Próxima)

### Objetivo
Implementar as 6 seções restantes do BO completo baseadas no material do Sgt. Claudio Moreira.

### Seções Planejadas

#### 🔍 Seção 3: Campana e Vigilância
- Objetivos da campana
- Duração e equipe envolvida
- Observações e comportamentos suspeitos
- Decisão pela abordagem

#### 🏠 Seção 4: Entrada em Domicílio
- Autorização (mandado, consentimento, flagrante)
- Procedimentos de segurança adotados
- Localização dos ilícitos
- Resistência ou reação

#### 🎯 Seção 5: Fundada Suspeita
- Fatos concretos observados
- Jurisprudência aplicável (STF HC 261029)
- Conduta atípica detalhada
- Correlação com denúncias

#### ⚠️ Seção 6: Reação e Uso da Força
- Tipo de reação dos envolvidos
- Nível de força empregado
- Procedimentos de segurança
- Preservação da vida

#### 📦 Seção 7: Apreensões
- Descrição detalhada dos ilícitos
- Quantidade e tipo de drogas
- Outros objetos apreendidos (armas, dinheiro, celulares)
- Lacração e cadeia de custódia

#### 🚔 Seção 8: Condução e Ocorrências
- Identificação dos conduzidos
- Destino (delegacia, hospital)
- Comunicações realizadas (família, advogado)
- Registro formal da ocorrência

### Estimativa de Complexidade
**Média a Alta** - Cada seção requer:
- Novas validações específicas
- Prompts LLM adaptados
- Jurisprudência aplicável
- Testes com casos reais

---

## 🔐 Fase 3 - Autenticação e Qualidade

### Sistema de Autenticação
- [ ] Login/registro de usuários (PM)
- [ ] Perfis: Soldado, Cabo, Sargento, Tenente, Capitão
- [ ] Permissões diferenciadas por patente
- [ ] Histórico de BOs por usuário

### Exportação PDF
- [ ] Gerar PDF formatado do BO completo
- [ ] Incluir brasão da PM e assinaturas digitais
- [ ] Opção de download ou envio por email
- [ ] Conformidade com layout oficial

### Comparação de LLMs
- [ ] Implementar suporte a Claude (Anthropic)
- [ ] Implementar suporte a GPT-4 (OpenAI)
- [ ] Dashboard para comparar qualidade das respostas
- [ ] Fallback automático se Gemini falhar

**Nota**: TODOs já existem no código (`llm_service.py:179-183`)

---

## 📊 Fase 4 - Analytics e Relatórios

### Dashboard de Métricas Operacionais
**Objetivo**: Fornecer visibilidade sobre uso do sistema e eficiência operacional.

#### Métricas a implementar:
- [ ] **Tempo médio de conclusão de BO** (por seção, por usuário, por unidade)
- [ ] **Taxa de conclusão** (% de BOs iniciados vs finalizados)
- [ ] **Horários de pico** (gráfico de uso por hora/dia)
- [ ] **Tipos de ocorrência mais comuns** (natureza do empenho)
- [ ] **Distribuição geográfica** (mapa de calor dos locais)
- [ ] **Taxa de uso do rascunho** (% de usuários que retomam BOs)
- [ ] **Tempo médio por pergunta** (identificar perguntas que geram dúvidas)

#### Arquivos novos:
- `docs/analytics.html` - Dashboard visual (Chart.js ou D3.js)
- `backend/analytics.py` - Endpoints para agregação de dados
- `backend/database.py` - Queries otimizadas para relatórios

---

### Relatórios de Qualidade de Redação
**Objetivo**: Avaliar qualidade dos BOs gerados e identificar melhorias.

#### Funcionalidades:
- [ ] **Score de qualidade** (0-100) baseado em:
  - Completude das informações
  - Clareza e objetividade
  - Conformidade com normas da PM
  - Uso correto de termos técnicos
- [ ] **Sugestões de melhoria** (ex: "Resposta 1.5 poderia ser mais específica")
- [ ] **Comparação entre unidades** (ranking de qualidade por batalhão)
- [ ] **Evolução temporal** (gráfico de melhoria ao longo do tempo)

#### Implementação técnica:
- Usar LLM secundário (Gemini Pro ou GPT-4) para avaliar qualidade
- Criar tabela `bo_quality_scores` no banco de dados
- Endpoint `GET /api/quality/report?unit=X&period=Y`

---

### Exportação de Dados para BI
**Objetivo**: Permitir análises avançadas em ferramentas de BI externas.

#### Funcionalidades:
- [ ] **API de exportação** (`GET /api/export/data`)
  - Formato: JSON, CSV, Parquet
  - Filtros: data, unidade, tipo de BO
  - Paginação e rate limiting
- [ ] **Webhook para integração** (notificar sistemas externos)
- [ ] **Conectores prontos**:
  - Power BI (arquivo .pbix de exemplo)
  - Tableau (conexão via API REST)
  - Google Data Studio
- [ ] **Data Lake** (opcional, para grandes volumes)
  - Exportar logs para S3/Google Cloud Storage
  - Formato Parquet para queries eficientes

#### Segurança:
- Autenticação via API Key
- Anonimização de dados sensíveis (nomes de policiais, placas)
- Conformidade com LGPD

---

## 📱 Fase 5 - Expansão

### Múltiplos Tipos de BO
- [ ] BO de roubo
- [ ] BO de furto
- [ ] BO de violência doméstica
- [ ] BO de acidente de trânsito

### Integração com Sistemas PM
- [ ] API para consulta de placas (DETRAN)
- [ ] Integração com CAD (Computer-Aided Dispatch)
- [ ] Sincronização com sistema de registro da PM

### Aplicativo Mobile
- [ ] App Android nativo (Kotlin/Jetpack Compose)
- [ ] App iOS nativo (Swift/SwiftUI)
- [ ] Modo offline com sincronização posterior

---

## 🔧 Melhorias Técnicas (DevOps & Qualidade)

### Testes Automatizados
- [ ] Testes unitários (pytest) para `validator.py` e `state_machine.py`
- [ ] Testes de integração (FastAPI TestClient)
- [ ] Testes E2E (Playwright ou Cypress)
- [ ] Cobertura mínima de 80%

### CI/CD
- [ ] GitHub Actions para:
  - Rodar testes automaticamente em PRs
  - Deploy automático no Render (backend)
  - Deploy automático no GitHub Pages (frontend)
- [ ] Linting (ruff, black) e type checking (mypy)

### Monitoramento
- [ ] Sentry para tracking de erros
- [ ] Prometheus + Grafana para métricas de performance
- [ ] Alertas para APIs lentas ou com alta taxa de erro

### Performance
- [ ] Caching de respostas do LLM (Redis)
- [ ] CDN para assets estáticos (Cloudflare)
- [ ] Upgrade para plano pago do Render (evitar cold starts)

---

## 📅 Sugestão de Priorização (próximos 6 meses)

### Sprint 1-2 (Jan-Fev 2026): Fase 2 - Seções 3-4
1. Definir perguntas com Sgt. Claudio
2. Implementar Seção 3 (Campana)
3. Implementar Seção 4 (Entrada Domicílio)
4. Testar com casos reais

### Sprint 3-4 (Mar-Abr 2026): Analytics Básico
1. Implementar métricas operacionais básicas
2. Criar dashboard simples de uso do sistema
3. Adicionar exportação CSV de logs

### Sprint 5-6 (Mai-Jun 2026): Fase 3 - Qualidade
1. Implementar exportação PDF
2. Adicionar suporte a Claude/OpenAI como backup
3. Sistema de autenticação simples

### Backlog Futuro (Jul+ 2026):
- Relatórios avançados de qualidade
- Integração com BI externo
- Seções 5-8 do BO
- App mobile

---

## 🎯 Métricas de Sucesso

### KPIs Fase 2 (Seções 3-8):
- 50+ BOs com todas 8 seções gerados no primeiro mês
- Tempo médio de conclusão < 15 minutos
- Taxa de satisfação > 85% (feedback positivo)

### KPIs Analytics:
- 100% dos gestores acessando dashboard mensalmente
- Redução de 20% no tempo médio de BO após 3 meses
- Identificação de 3+ padrões acionáveis (ex: perguntas confusas)

---

## 📝 Arquitetura Técnica

### Backend (Python + FastAPI)
- **State Machines**: Uma classe por seção (`state_machine_section{N}.py`)
- **Validators**: Regras específicas por seção (`validator_section{N}.py`)
- **LLM Service**: Prompts customizados por seção
- **Sessions**: Dict com múltiplas seções (`sessions[session_id]["sections"][N]`)

### Frontend (Vanilla JS + Tailwind)
- **Modular**: Cada seção tem próprio objeto de perguntas
- **Persistente**: Container de textos gerados permanece visível
- **Escalável**: `ALL_SECTIONS` map facilita adição de novas seções
- **Responsivo**: Media queries em 768px (mobile/desktop)

### Database (PostgreSQL)
- **logs**: Eventos de sessões, respostas, erros
- **sessions_metadata**: Dados agregados por sessão
- **quality_scores**: (futuro) Avaliações de qualidade

---

## 📚 Referências

- **Material Base**: Claudio Moreira (Sargento PM)
- **Jurisprudência**: STF HC 261029 (fundada suspeita)
- **Design System**: Tailwind CSS v3
- **LLM**: Google Gemini 2.5 Flash + Groq Llama 3.3 70B

---

## 👥 Créditos

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claude Sonnet 4.5** - Implementação via Claude Code
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)

---

## 📄 Licença

Mesma licença do projeto principal (BO Inteligente).

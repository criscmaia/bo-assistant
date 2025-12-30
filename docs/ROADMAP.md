# Roadmap - BO Inteligente

## Versão Atual: v0.12.8 (8/8 Seções Completas + Seção 8 Expandida)
**Última atualização:** 30/12/2024

> **Funcionalidades já implementadas:** Ver [CHANGELOG.md](CHANGELOG.md)
> **Arquitetura técnica:** Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## ✅ Funcionalidades Implementadas Recentemente

### CI/CD - GitHub Actions (v0.12.4)
✅ **Implementado em 29/12/2025**

**O que foi feito:**
- ✅ Workflow `.github/workflows/test.yml` configurado
- ✅ Roda automaticamente em push/PR para `main`
- ✅ Executa testes unitários e de integração (Python 3.13, Ubuntu latest)
- ✅ Timeout de 10min, variáveis mockadas (GEMINI_API_KEY, GROQ_API_KEY)
- ✅ Badge de status adicionado ao README
- ✅ Validação de código antes de merge

**Estrutura de testes reorganizada:**
- ✅ Testes E2E (Playwright) movidos para `tests/e2e/`
- ✅ CI exclui E2E (precisa de browser)
- ✅ Comandos documentados para rodar localmente

**Impacto:**
- ✅ Previne bugs em produção
- ✅ Garante qualidade em PRs
- ✅ Confiança para refatorações

---

## Backlog de Funcionalidades

### 1. Comparação e Avaliação de LLMs

**O que é:** Sistema para comparar a qualidade dos textos gerados por diferentes modelos de linguagem (LLMs) e escolher o melhor para o caso de uso de BOs policiais.

**Por que é importante:**
- Atualmente usamos Groq Llama 3.3 70B (principal) e Gemini 2.5 Flash (fallback), mas não temos dados objetivos de qual gera textos melhores
- Diferentes LLMs têm diferentes pontos fortes (precisão, criatividade, aderência a instruções)
- Custo varia significativamente entre providers
- Antes de escalar para mais usuários, precisamos garantir qualidade consistente

**LLMs candidatos a avaliar:**

| Modelo | Provider | Custo (por 1M tokens) | Pontos fortes |
|--------|----------|----------------------|---------------|
| **Llama 3.3 70B** | Groq | ~$0.60 | Rápido, barato, bom para instruções |
| **Gemini 2.5 Flash** | Google | ~$0.35 | Muito barato, contexto grande |
| **Claude 3.5 Sonnet** | Anthropic | ~$3.00 | Excelente em escrita, segue instruções com precisão |
| **GPT-4o** | OpenAI | ~$2.50 | Versátil, bem estabelecido |
| **GPT-4o-mini** | OpenAI | ~$0.15 | Muito barato, qualidade razoável |
| **Mixtral 8x22B** | Mistral/Groq | ~$0.90 | Open source, bom custo-benefício |

**Métricas de avaliação:**

*Métricas automáticas (NLP):*
- **BLEU (Bilingual Evaluation Understudy):** Mede sobreposição de n-gramas entre texto gerado e referência. Útil se tivermos BOs "modelo" escritos por Claudio.
- **ROUGE (Recall-Oriented Understudy for Gisting Evaluation):** Similar ao BLEU, mas focado em recall. Bom para verificar se informações importantes foram incluídas.
- **BERTScore:** Usa embeddings para medir similaridade semântica, não apenas palavras exatas. Mais robusto que BLEU/ROUGE.
- **NLI (Natural Language Inference):** Verifica se o texto gerado é logicamente consistente com as informações fornecidas (detecta "alucinações").
- **Perplexidade:** Mede quão "natural" o texto parece. Menor = mais fluente.

*Métricas humanas (avaliação por especialista):*
- **Precisão jurídica:** Usa termos corretos do direito penal/processual?
- **Fidelidade:** Não inventa informações além do fornecido?
- **Clareza:** Texto objetivo, profissional, sem ambiguidades?
- **Formatação:** Estrutura adequada para BO oficial?
- **Preferência geral:** Em teste cego, qual texto Claudio prefere?

*Métricas operacionais:*
- **Latência:** Tempo de geração (importante para UX)
- **Custo:** Custo por BO gerado
- **Taxa de erro:** Frequência de falhas/timeouts
- **Disponibilidade:** Uptime do provider

**O que precisaria ser feito:**
- Criar conjunto de "casos de teste" com inputs padronizados
- Gerar outputs com cada LLM candidato
- Implementar cálculo de métricas automáticas (BLEU, BERTScore, etc.)
- Interface para Claudio fazer avaliação cega (A vs B, sem saber qual é qual)
- Dashboard para consolidar resultados e tomar decisão

**Dependências:** Nenhuma técnica, mas precisa de tempo do Claudio para avaliação humana.

---

### 3. Monitoramento e Alertas

**O que é:** Sistema para acompanhar a saúde da aplicação em tempo real e ser notificado quando algo der errado.

**Por que é importante:**
- Atualmente não sabemos se o sistema está falhando até um usuário reclamar
- LLMs podem ter rate limits, timeouts, ou ficar indisponíveis
- Render free tier tem limitações (cold start, memória)
- Quando escalar para mais usuários, problemas precisam ser detectados rapidamente

**O que monitorar:**

*Erros e exceções:*
- Erros 500 no backend
- Falhas de conexão com LLMs
- Timeouts de geração de texto
- Erros de validação inesperados

*Performance:*
- Tempo de resposta dos endpoints
- Tempo de geração de texto por LLM
- Uso de memória do servidor
- Cold starts do Render

*Uso:*
- Requisições por minuto/hora
- BOs iniciados vs completados
- Taxa de abandono por seção

**Ferramentas comuns de mercado:**
- **Sentry:** Tracking de erros com stack traces, muito popular
- **Prometheus + Grafana:** Métricas e dashboards, open source
- **Datadog:** Solução completa, mais cara
- **UptimeRobot:** Monitoramento simples de disponibilidade (grátis)

**O que precisaria ser feito:**
- Escolher ferramenta de monitoramento
- Instrumentar código para enviar métricas
- Configurar alertas (email/Slack) para erros críticos
- Dashboard para visualizar saúde do sistema

**Dependências:** Nenhuma - pode ser feito independentemente.

---

### 4. Autenticação e Histórico de Usuário

**O que é:** Sistema de login para identificar usuários e permitir que acessem seus BOs anteriores.

**Por que é importante:**
- Atualmente o sistema é anônimo - não sabemos quem está usando
- Usuário perde acesso ao BO se fechar o navegador (só tem rascunho local)
- Impossível continuar um BO em outro dispositivo
- Necessário para qualquer funcionalidade personalizada (histórico, favoritos, etc.)

**Considerações:**
- Policiais militares podem ter restrições sobre uso de serviços externos
- Precisa ser simples (não criar fricção no uso)
- Dados são sensíveis (ocorrências policiais)
- Pode ser integrado com sistemas existentes da PM no futuro

**Opções de implementação:**
- Login com email/senha (mais simples)
- Login com Google/Microsoft (conveniente, mas dados vão para terceiros)
- Integração com sistema da PM (ideal, mas complexo)
- Código de acesso por unidade (meio termo)

**O que precisaria ser feito:**
- Definir modelo de autenticação com Claudio
- Implementar backend de autenticação
- Tela de login/registro
- Associar sessões/BOs ao usuário
- Tela de "Meus BOs" com histórico

**Dependências:** Decisão sobre modelo de autenticação com Claudio.

---

### 5. Exportação e Compartilhamento

**O que é:** Funcionalidade para exportar o BO finalizado em diferentes formatos e compartilhar por diferentes canais.

**Por que é importante:**
- Atualmente o usuário precisa copiar/colar manualmente
- PDF é formato padrão para documentos oficiais
- WhatsApp é muito usado por policiais para comunicação rápida
- Facilita integração com sistemas existentes

**Formatos de exportação:**
- **PDF:** Formato universal, pode incluir formatação profissional
- **DOCX:** Editável, caso precise de ajustes
- **TXT:** Simples, leve, compatível com qualquer sistema

**Canais de compartilhamento:**
- **Download direto:** Usuário baixa o arquivo
- **Email:** Enviar para si mesmo ou para delegacia
- **WhatsApp:** Compartilhar via API do WhatsApp Business
- **Copiar link:** Link temporário para acessar o BO (requer autenticação)

**UX sugerida:** Ícone de compartilhamento (⬆️) ao lado de cada BO finalizado, abrindo menu com opções.

**O que precisaria ser feito:**
- Implementar geração de PDF no backend (biblioteca como WeasyPrint ou ReportLab)
- Definir template/layout do PDF
- Integrar com API de email (SendGrid, AWS SES, etc.)
- Avaliar integração com WhatsApp Business API
- Interface de compartilhamento no frontend

**Dependências:** Autenticação (para histórico de BOs) é desejável mas não obrigatória.

---

### 6. Analytics - Métricas de Uso

**O que é:** Dashboard para visualizar como o sistema está sendo usado.

**Por que é importante:**
- Entender padrões de uso (horários de pico, seções mais demoradas)
- Identificar problemas (alta taxa de abandono em alguma seção?)
- Medir sucesso do produto (quantos BOs completados?)
- Dados para decisões de produto

**Métricas operacionais:**
- Total de BOs iniciados vs completados
- Taxa de conclusão por seção
- Tempo médio de preenchimento (total e por seção)
- Horários de pico de uso
- Distribuição geográfica (se tivermos essa info)
- Taxa de uso do rascunho (quantos retomam BOs?)
- Tempo médio por pergunta (identificar perguntas confusas)

**Métricas de engajamento:**
- Usuários ativos por dia/semana/mês
- Frequência de uso por usuário
- Retenção (usuários que voltam)

**Visualizações sugeridas:**
- Gráfico de linha: BOs/dia ao longo do tempo
- Funil: Taxa de conclusão por seção
- Heatmap: Horários de maior uso
- Tabela: Ranking de perguntas por tempo médio

**O que precisaria ser feito:**
- Definir quais métricas são prioritárias
- Criar queries para agregar dados do banco existente
- Desenvolver dashboard visual (pode ser página HTML simples com Chart.js)
- Atualização automática (polling ou WebSocket)

**Dependências:** Dados já estão sendo coletados no banco (bo_sessions, bo_events). Não precisa de autenticação para métricas agregadas.

---

### 7. Analytics - Qualidade de Redação

**O que é:** Sistema para avaliar e pontuar a qualidade dos BOs gerados.

**Por que é importante:**
- Garantir que o sistema está gerando textos de qualidade consistente
- Identificar padrões de respostas ruins dos usuários
- Feedback para melhorar prompts dos LLMs
- Gamificação para usuários (score de qualidade)

**Abordagens possíveis:**

*Avaliação por LLM secundário:*
- Usar outro LLM para avaliar o texto gerado
- Prompt: "Avalie este BO de 0-100 nos critérios: clareza, precisão, completude..."
- Vantagem: Automático, escalável
- Desvantagem: LLM avaliando LLM pode ter vieses

*Avaliação humana (Claudio):*
- Claudio revisa amostra de BOs periodicamente
- Interface para dar nota e comentários
- Vantagem: Avaliação de especialista, ground truth
- Desvantagem: Não escala, depende de disponibilidade

*Regras heurísticas:*
- Verificar tamanho mínimo do texto
- Detectar informações faltantes
- Validar termos jurídicos corretos
- Vantagem: Rápido, determinístico
- Desvantagem: Limitado, não captura nuances

**Métricas de qualidade:**
- Score geral (0-100)
- Completude: Todas as informações necessárias estão presentes?
- Clareza: Texto objetivo, sem ambiguidades?
- Precisão jurídica: Termos corretos, formatação adequada?
- Fidelidade: Não inventou informações?

**Aplicações:**
- Dashboard de qualidade média por período
- Alertas se qualidade cair abaixo de threshold
- Comparação entre diferentes versões de prompts
- Feedback para usuários ("Seu BO ficou 85/100")

**O que precisaria ser feito:**
- Definir critérios de qualidade com Claudio
- Escolher abordagem (LLM, humano, heurística, ou combinação)
- Implementar sistema de scoring
- Interface para visualização e drill-down

**Dependências:** Definição de critérios com Claudio. Idealmente após estabilizar comparação de LLMs (#2).

---

### 8. Analytics - Exportação para BI

**O que é:** API e conectores para exportar dados para ferramentas de Business Intelligence externas.

**Por que é importante:**
- Gestores da PM podem querer análises customizadas
- Ferramentas como Power BI e Tableau são padrão em organizações
- Permite análises que não previmos no dashboard interno
- Integração com outros dados da PM

**Funcionalidades:**
- API REST para consulta de dados (`GET /api/export/data`)
- Filtros: período, unidade, tipo de BO
- Formatos: JSON, CSV, Parquet
- Paginação e rate limiting
- Autenticação via API Key

**Conectores prontos (opcional):**
- Power BI: arquivo .pbix de exemplo
- Tableau: configuração de conexão
- Google Data Studio: template de relatório

**Considerações de segurança:**
- Anonimização de dados sensíveis (nomes, placas, endereços)
- Conformidade com LGPD
- Audit log de quem exportou o quê
- Controle de acesso por perfil

**O que precisaria ser feito:**
- Definir quais dados podem ser exportados
- Implementar endpoints de exportação
- Documentar API para equipe de BI
- Criar exemplos de uso com ferramentas populares

**Dependências:** Autenticação (#4) para controle de acesso. Analytics básico (#6) para ter dados significativos.

---

### 9. Upgrade de Infraestrutura

**O que é:** Migrar do plano gratuito do Render para um plano pago, eliminando limitações.

**Por que é importante:**
- Render free tier tem "cold start" (servidor dorme após 15min de inatividade)
- Primeira requisição após inatividade demora 30-60 segundos
- Isso prejudica experiência do usuário
- Limite de recursos (512MB RAM, CPU compartilhada)

**Opções no Render:**

| Plano | Preço | Cold Start | RAM | CPU |
|-------|-------|------------|-----|-----|
| Free | $0 | Sim (15min) | 512MB | Compartilhada |
| Starter | $7/mês | Não | 512MB | Compartilhada |
| Standard | $25/mês | Não | 2GB | Dedicada |
| Pro | $85/mês | Não | 4GB | Dedicada |

**Recomendação:** Starter ($7/mês) resolve o problema principal (cold start) com custo mínimo.

**Gatilho para upgrade:** Quando houver usuários regulares além do time de desenvolvimento (ex: Claudio treinando outros policiais).

**O que precisaria ser feito:**
- Monitorar uso atual para justificar upgrade
- Alterar plano no dashboard do Render
- Testar se performance melhorou
- Monitorar custos mensais

**Dependências:** Nenhuma técnica. Decisão de negócio baseada em uso.

---

### 10. Múltiplos Tipos de BO

**O que é:** Expandir o sistema para suportar outros tipos de Boletim de Ocorrência além de tráfico de drogas.

**Por que é importante:**
- Tráfico de drogas é apenas um dos muitos tipos de ocorrência
- Reutilizar a infraestrutura para outros casos aumenta valor do produto
- Cada tipo de BO tem estrutura e perguntas específicas
- Potencial de escalar para toda a PM

**Tipos de BO candidatos:**
- Roubo
- Furto
- Violência doméstica
- Acidente de trânsito
- Lesão corporal
- Porte ilegal de arma
- Dano ao patrimônio

**Considerações:**
- Cada tipo precisa de novo conjunto de perguntas/seções
- Validações específicas por tipo
- Prompts de LLM customizados
- Material de referência do especialista (equivalente ao material do Claudio)

**Arquitetura sugerida:**
- Estrutura modular: cada tipo de BO é um "módulo"
- Componentes compartilhados: autenticação, exportação, analytics
- Seleção de tipo na tela inicial
- Fácil adicionar novos tipos no futuro

**O que precisaria ser feito:**
- Priorizar quais tipos de BO implementar primeiro
- Conseguir material de referência/especialista para cada tipo
- Criar perguntas e validações
- Adaptar prompts de LLM
- Interface para seleção de tipo

**Dependências:** Estabilização do BO de tráfico atual. Material de especialista para cada novo tipo.

---

### 11. Integração com Sistemas da PM

**O que é:** Conectar o BO Inteligente com sistemas existentes da Polícia Militar.

**Por que é importante:**
- Evita digitação duplicada (dados já existem em outros sistemas)
- Validação automática de informações (placa existe? pessoa tem antecedentes?)
- Fluxo mais integrado com processos existentes
- Maior adoção institucional

**Integrações possíveis:**

*Consulta de placas (DETRAN):*
- Validar se placa existe
- Obter dados do veículo (marca, modelo, cor)
- Verificar se é roubado/furtado

*CAD (Computer-Aided Dispatch):*
- Importar dados do acionamento (horário, natureza, local)
- Preencher automaticamente Seção 1

*Sistema de registro da PM:*
- Enviar BO finalizado direto para o sistema oficial
- Evitar cópia/cola manual

*Consulta de antecedentes:*
- Verificar se suspeito tem passagens anteriores
- Informação relevante para o BO

**Desafios:**
- Acesso às APIs (burocracia, autorizações)
- Segurança e compliance
- Cada estado pode ter sistemas diferentes
- Manutenção de integrações

**O que precisaria ser feito:**
- Mapear sistemas existentes na PM de MG
- Entender requisitos de acesso/autorização
- Avaliar viabilidade técnica de cada integração
- Implementar integrações priorizadas
- Documentar para replicar em outros estados

**Dependências:** Relacionamento institucional com a PM. Autorizações de acesso.

---

### 12. Aplicativo Mobile

**O que é:** Versão nativa do sistema para smartphones (Android e iOS).

**Por que é importante:**
- Policiais frequentemente estão em campo, longe de computadores
- App nativo tem melhor performance e UX que site mobile
- Funcionalidades offline (preencher BO sem internet, sincronizar depois)
- Notificações push
- Acesso à câmera para fotos de evidências

**Considerações:**
- Desenvolver para Android E iOS aumenta complexidade
- Alternativa: Progressive Web App (PWA) - funciona como app mas é web
- Manutenção de duas codebases (web + mobile)
- Publicação nas lojas (Google Play, App Store) tem requisitos

**Abordagens:**

*Apps nativos separados:*
- Android: Kotlin + Jetpack Compose
- iOS: Swift + SwiftUI
- Melhor performance e UX
- Maior custo de desenvolvimento e manutenção

*Framework cross-platform:*
- React Native ou Flutter
- Uma codebase, dois apps
- Performance quase nativa
- Comunidade grande, fácil encontrar desenvolvedores

*Progressive Web App (PWA):*
- Mesma codebase do site atual
- Funciona offline com Service Workers
- Instalável na home screen
- Sem necessidade de publicar em lojas
- Algumas limitações (notificações no iOS, acesso a hardware)

**O que precisaria ser feito:**
- Decidir abordagem (nativo, cross-platform, PWA)
- Se PWA: adicionar Service Worker e manifest ao site atual
- Se app: desenvolver app, publicar nas lojas
- Implementar sincronização offline
- Testar em dispositivos reais

**Dependências:** Autenticação (#4) para sincronizar dados entre dispositivos. Site atual deve estar estável.

---

## Itens a Validar com Claudio

Decisões que dependem de input do especialista:

| # | Item | Pergunta | Impacta |
|---|------|----------|---------|
| 1 | **Modelo de autenticação** | Login com email? Código por unidade? Integração com sistema PM? | #4 |
| 2 | **Templates de locais** | Policiais reutilizam endereços frequentes? Vale salvar favoritos? | Backlog futuro |
| 3 | **Reutilizar dados entre BOs** | Cada caso é único ou dá para reaproveitar algo? | Backlog futuro |
| 4 | **Formato de exportação** | PDF agrega valor ou copy/paste resolve? Qual layout ideal? | #5 |
| 5 | **Canais de compartilhamento** | WhatsApp é útil? Email? Qual preferência? | #5 |
| 6 | **Perfis por patente** | Gera valor saber patente? Permissões diferentes? | #4 |
| 7 | **Critérios de qualidade** | O que define um "bom" BO? Como pontuar? | #7 |
| 8 | **Avaliação de BOs** | Claudio revisaria BOs de outros usuários? Com que frequência? | #7 |
| 9 | **Próximos tipos de BO** | Qual tipo priorizar depois de tráfico? Roubo? Furto? | #10 |
| 10 | **Integrações prioritárias** | Qual sistema da PM seria mais útil integrar primeiro? | #11 |

---

## Métricas de Sucesso

### Fase Atual: Validação
- [ ] 50+ BOs completos gerados
- [ ] Feedback positivo de Claudio em 80%+ dos textos
- [ ] Tempo médio de preenchimento < 15 minutos
- [ ] Zero bugs críticos reportados

### Próxima Fase: Escala Inicial
- [ ] 10+ policiais usando ativamente
- [ ] 200+ BOs/mês
- [ ] Taxa de conclusão > 70% (iniciados vs finalizados)
- [ ] NPS > 8 (satisfação dos usuários)

### Fase de Crescimento
- [ ] 100+ usuários ativos mensais
- [ ] Suporte a 2+ tipos de BO
- [ ] Integração com pelo menos 1 sistema PM
- [ ] App mobile lançado (ou PWA)

---

## Documentação Relacionada

- [CHANGELOG.md](CHANGELOG.md) - Histórico de versões
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura técnica
- [DEVELOPMENT.md](DEVELOPMENT.md) - Guia de desenvolvimento
- [docs/TESTING.md](docs/TESTING.md) - Guia de testes

---

## Equipe

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)
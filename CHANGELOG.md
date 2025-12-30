# Changelog v0.12.9

## 📜 Histórico de Features por Fase

### 🔄 Fase 2 Completa - Seções 3-8 (v0.7.0+)

#### v0.12.9 (30 de Dezembro de 2024) - Revisão Seções 1 e 2 (Documento Claudio 2025-12-30)

### ⚠️ BREAKING CHANGES
- **Seção 1 expandida de 7 para 11 perguntas** (+ sub-perguntas condicionais)
- **Seção 2 expandida de 11 para 13 perguntas** (+ reordenação)
- Renumeração: 1.5→1.6, 1.6→1.7+1.8, 1.7→1.9 (Seção 1)
- Reordenação: contexto (2.2) agora vem ANTES de placa (2.3) na Seção 2

### ✅ Adicionado na Seção 1
- **Nova Pergunta 1.5** - "Houve deslocamento entre o ponto de acionamento e o local da ocorrência?" (SIM/NÃO)
  - **Sub-pergunta 1.5.1** (condicional): "Local de onde a guarnição partiu"
  - **Sub-pergunta 1.5.2** (condicional): "Houve alguma alteração durante o percurso?"
- **Pergunta 1.6** separada em duas:
  - **1.7**: "O local é conhecido como ponto de tráfico?"
  - **1.8**: "O local é dominado por facção criminosa?"
- **Pergunta 1.9** expandida com sub-perguntas:
  - **1.9.1** (condicional): "Nome do estabelecimento"
  - **1.9.2** (condicional): "Distância aproximada"

### ✅ Adicionado na Seção 2
- **Nova Pergunta 2.5** - "Descreva se houve reação do motorista ou ocupantes"
- **Nova Pergunta 2.8** - "Se houve perseguição, por qual motivo o veículo parou?"

### 🔄 Alterado na Seção 1
- **Pergunta 1.3** reescrita com exemplos (190, DDU, mandado, patrulhamento)
- **Lógica condicional** implementada: sub-perguntas só aparecem se resposta pai = SIM
- Observação do Claudio incluída no prompt: "não existe patrulhamento de rotina... É sempre atividade + objetivo"

### 🔄 Alterado na Seção 2
- **Reordenação estratégica**: contexto do veículo (2.2) agora vem ANTES de marca/placa (2.3)
- **Pergunta 2.6** separada em duas: parou/perseguição (2.7) e motivo parada (2.8)
- **Busca veicular (2.10)** agora vem ANTES de busca pessoal (2.11)
- Textos simplificados e mais claros em várias perguntas

### 📊 Totais
- Total de perguntas: **55 → 61** (+6 perguntas)
- Seção 1: 7 → 11 perguntas (+4)
- Seção 2: 11 → 13 perguntas (+2)

---

#### v0.12.8 (30 de Dezembro de 2024) - Ajustes nas Seções 3, 4, 5 e 6

### ⚠️ BREAKING CHANGES
- **Seção 5 reduzida de 4 para 3 perguntas** (removida pergunta condicional 5.1)
- **Seção 6 expandida de 5 para 6 perguntas** (adicionada nova pergunta 6.1 sobre arma/ameaça)
- Renumeração: 5.2→5.1, 5.3→5.2, 5.4→5.3 (Seção 5)
- Renumeração: todas as perguntas da Seção 6 avançam 1 número após nova 6.1

### ✅ Adicionado
- **Nova Pergunta 6.1 na Seção 6 - Reação/Força**
  - "Houve ameaça ou uso de arma? Contra quem e como?"
  - Importante para tipificação (Art. 40, IV - emprego de arma de fogo)
  - Aceita resposta negativa ("Não houve")

### 🔄 Alterado
- **Seção 3 - Campana (8 perguntas - mantidas)**
  - Textos melhorados com mais detalhes e exemplos
  - 3.6: Exemplos de observação (entregas, usuários, esconderijos)
  - 3.7: Adicionado "O que portava? O que disse?" em abordagem
  - 3.8: Adicionado "Como ocorreu?" em fuga

- **Seção 4 - Domicílio (5 perguntas - mantidas)**
  - Pergunta 4.4 agora inclui exemplos (autorização, perseguição, droga à vista)

- **Seção 5 - Fundada Suspeita (4→3 perguntas)**
  - Removida pergunta condicional 5.1 "Houve abordagem por fundada suspeita?"
  - Seção já é opcional, pergunta condicional redundante
  - Renumeração: 5.2→5.1, 5.3→5.2, 5.4→5.3

- **Seção 6 - Reação/Força (5→6 perguntas)**
  - Nova 6.1 sobre arma/ameaça inserida como PRIMEIRA pergunta
  - Antigas perguntas renumeradas: 6.1→6.2, 6.2→6.3, 6.3→6.4, 6.4→6.5, 6.5→6.6

### 🧪 Testes
- **Atualizado `tests/unit/test_section5.py`** - 7 testes (adaptado para 3 perguntas)
- **Atualizado `tests/unit/test_section6.py`** - 18 testes (adaptado para 6 perguntas)
- Todos os testes unitários passando

### 📚 Fundamentação Legal
- **Art. 40, IV da Lei 11.343/06:** Uso de arma de fogo é agravante
- Nova pergunta 6.1 documenta esse elemento essencial para tipificação e fixação de pena

### 📊 Resumo das Mudanças
- Seção 3: 8 perguntas (mantidas - textos melhorados)
- Seção 4: 5 perguntas (mantidas - exemplos adicionados)
- Seção 5: 4→3 perguntas (removida condicional redundante)
- Seção 6: 5→6 perguntas (adicionada arma/ameaça)
- **Total líquido:** 22→22 perguntas (sem mudança no total)

#### v0.12.7 (30 de Dezembro de 2024) - Expansão Seção 2

### ✅ Adicionado
- **3 Novas Perguntas na Seção 2 - Abordagem a Veículo**
  - 2.8: "Quem realizou a busca pessoal nos ocupantes? (graduação + nome)"
  - 2.9: "Quem realizou a busca no veículo e em quais partes? (graduação + nome + locais vistoriados)"
  - 2.10: "O que foi localizado, com quem estava e em qual parte do veículo?"
  - Separação crítica para documentação da **cadeia de custódia**

### 🔄 Alterado
- **Seção 2 - Pergunta 2.7 dividida + Renumeração**
  - Antiga 2.7 (abordagem + busca combinadas) separada em 2.7 (abordagem) + 2.8 (busca pessoal) + 2.9 (busca veicular) + 2.10 (encontrado)
  - Antiga 2.8 (irregularidades) renumerada para 2.11
  - Pergunta 2.3 agora exige contexto (local + situação, mínimo 30 caracteres)

### 🧪 Testes
- **Criado `tests/unit/test_validator_section2.py`**
  - 29 testes unitários para Seção 2
  - Validação de placa Mercosul (ABC-1D23, ABC1D23)
  - Validação de graduação militar obrigatória em 2.4, 2.7, 2.8, 2.9
  - Validação de respostas negativas em 2.10 e 2.11 ("Nada localizado", "NÃO")
  - Todos os 160 testes unitários passando (131 anteriores + 29 novos)

### 📝 Validador
- **Adicionado método `_check_none_response()` em `backend/validator_section2.py`**
  - Permite aceitar respostas negativas em perguntas 2.10 e 2.11
  - Padrões aceitos: "nada encontrado", "nada localizado", "não", "negativo"

### 📚 Fundamentação Legal
- **CPP Art. 244:** Autoriza busca pessoal (2.8)
- **Cadeia de Custódia:** Separação entre busca pessoal e busca veicular é essencial para:
  - Identificar quem encontrou cada item
  - Onde cada item foi encontrado (com pessoa ou no veículo)
  - Individualizar responsabilidades dos ocupantes

#### v0.12.6 (30 de Dezembro de 2024) - Reformulação Seção 8

### ⚠️ BREAKING CHANGE
- **Seção 8 expandida de 6 para 11 perguntas**
  - BOs em andamento na Seção 8 podem ser afetados
  - Alteração visa melhorar documentação policial conforme metodologia do especialista

### ✅ Adicionado
- **5 Novas Perguntas na Seção 8 - Condução e Pós-Ocorrência**
  - 8.2: "Onde e como o preso foi transportado até a delegacia?"
  - 8.4: "Qual era a função do preso no tráfico? (vapor, gerente, olheiro)"
  - 8.6: "Há sinais de dedicação ao crime? O que mostra isso?"
  - 8.7: "O preso tem papel relevante na facção? Atuação ocasional ou contínua?"
  - 8.8: "Houve tentativa de destruir ou ocultar provas, ou intimidar alguém?"
  - 8.9: "Havia menor de idade envolvido? Se sim, idade e participação?"
  - 8.10: "Quem informou as garantias constitucionais ao preso?"
  - 8.11: "Qual o destino dos presos e materiais apreendidos?"

### 🔄 Alterado
- **Seção 8 - Perguntas Renumeradas**
  - Antiga 8.2 (agravantes Art. 40) removida - informação movida para pergunta 1.7
  - Antiga 8.3 mantida como 8.3 (Declaração do preso)
  - Antiga 8.4 renumerada para 8.5 (Passagens anteriores/REDS)
  - Antiga 8.5 incorporada em 8.7 (Papel na facção)
  - Antiga 8.6 separada em 8.10 (Garantias) e 8.11 (Destino)

### 🧪 Testes
- **Atualizado `tests/unit/test_section8.py`**
  - 37 testes unitários para Seção 8
  - Validação de respostas negativas ("NÃO", "Sem indícios") em 7 perguntas (8.3-8.9)
  - Validação de graduação militar obrigatória em 8.1 e 8.10
  - Validação de palavras-chave específicas em 8.2 (transporte) e 8.11 (destino)
  - Todos os 131 testes unitários passando

### 📝 Prompt LLM
- **Reescrito `_build_prompt_section8()` em `backend/llm_service.py`**
  - Prompt reorganizado em 4 parágrafos narrativos
  - Integra todas as 11 novas informações na geração de texto
  - Instruções detalhadas para incluir: transporte, função no tráfico, dedicação ao crime, papel na facção, destruição de provas, menores, garantias constitucionais, destino

### 📚 Fundamentação Legal
- Seção 8 agora documenta melhor elementos essenciais para:
  - Tipificação do crime (função no tráfico)
  - Fixação de pena (dedicação habitual, papel na facção)
  - Envolvimento de menores (Art. 243, ECA)
  - Garantias constitucionais (Art. 5º, CF)
  - Cadeia de custódia (destino de presos e materiais)

#### v0.12.5 (30 de Dezembro de 2024) - Pergunta 1.7 (Art. 40)

### ✅ Adicionado
- **Pergunta 1.7 - Agravantes de Proximidade (Art. 40)**
  - Nova pergunta na Seção 1: "O local é próximo a escola, hospital ou transporte público? Qual estabelecimento e a que distância aproximada?"
  - Validação aceita "NÃO" como resposta válida
  - Validação exige especificação do estabelecimento e distância quando resposta é positiva
  - Prompt do LLM atualizado para incluir frase modelo do Art. 40, inciso III da Lei 11.343/06
  - Seção 1 passa de 6 para 7 perguntas

### 🧪 Testes
- **Criado `tests/unit/test_section1.py`**
  - 12 testes unitários para Seção 1 (BOStateMachine + ResponseValidator)
  - Testes para validação da pergunta 1.7 (aceita "NÃO", aceita resposta detalhada, rejeita resposta muito curta)
  - Todos os 121 testes unitários passando

### 📚 Documentação
- Atualizada versão para v0.12.5 em todos os arquivos principais
- CHANGELOG.md, README.md, DEVELOPMENT.md, API.md, TESTING.md, SETUP.md, ARCHITECTURE.md, ROADMAP.md

#### v0.12.4 (29 de Dezembro de 2024) - CI/CD e Reorganização de Testes

### ✅ Adicionado
- **CI/CD com GitHub Actions** (`.github/workflows/test.yml`)
  - Testes automatizados em push/PR para branch main
  - Roda testes unitários e de integração (Python 3.13, Ubuntu latest)
  - Timeout de 10 minutos, variáveis de ambiente mockadas (GEMINI_API_KEY, GROQ_API_KEY)
  - Badge de status no README.md
  - Validação de código antes de merge
- **Comandos de teste local** documentados em `comandos.txt`
  - `$env:PYTHONPATH = "backend"` + `pytest tests/unit tests/integration -v --tb=short`
  - Permite rodar localmente exatamente como o CI roda

### 🔧 Melhorado
- **Estrutura de testes reorganizada**
  - Testes E2E (Playwright) movidos para `tests/e2e/`
  - CI roda apenas unit + integration (E2E exclui browser, mais lento)
  - 3 arquivos reclassificados: `test_draft_persistence.py`, `test_draft_recovery.py`, `test_section1_isolated.py`
- **Documentação de infraestrutura**
  - DEVELOPMENT.md: Seção completa sobre CI/CD
  - TESTING.md: Atualizada com estrutura E2E e badges
  - ROADMAP.md: CI/CD marcado como implementado

#### v0.12.3 (Dez 2025) - Correções de UX e Logging
- [x] **Bug Fix:** Logging gravando apenas 2 primeiras respostas (Issue #6) - Agora grava todas as respostas
- [x] **UX:** Títulos de seção melhorados: "Seção N: Nome" ao invés de "Próxima Etapa: Nome"
- [x] **UX:** Ordem dos botões invertida: "Não" à esquerda, "Sim" à direita
- [x] **UX:** Contraste do botão cinza melhorado (bg-gray-400 → bg-gray-600)
- [x] **UX:** Sidebar atualizada para mostrar pergunta X.1 como respondida ("Sim") ao iniciar seção
- [x] **UX:** Scroll automático para topo ao clicar "Sim" + foco no input
- [x] **UX:** Scroll automático para final ao clicar "Não" ou completar seção
- [x] **Logging:** Auto-respostas (X.1 = "Sim") agora registradas no /logs com flag `auto_responded: true`
- [x] Documentação atualizada (CHANGELOG.md, README.md, docs/*.md)

#### v0.12.2 (Dez 2025) - Seção 8: Condução e Pós-Ocorrência (FINAL - BO COMPLETO)
- [x] **Seção 8: Condução e Pós-Ocorrência** - 6 perguntas (8.1 a 8.6) - ÚLTIMA SEÇÃO
- [x] **BO 100% COMPLETO** - Todas as 8 seções implementadas (8/8 seções)
- [x] State machine SEM lógica condicional (todas as 6 perguntas são obrigatórias)
- [x] **IMPORTANTE:** Seção 8 MARCA BO COMO COMPLETO - `boCompleted = true`
- [x] Validação de graduação militar obrigatória em 8.1 (Sargento, Soldado, Cabo, Tenente, Capitão)
- [x] Validação `allow_none_response` em 4 perguntas (8.2, 8.3, 8.4, 8.5) - aceita respostas negativas
- [x] Validação de destino obrigatório em 8.6 (CEFLAN, Delegacia, DIPC, Central, Hospital, UPA)
- [x] Geração de texto final consolidado via LLM (Gemini + Groq) com fundamento jurídico Lei 11.343/06 + Lei 13.869/19 + CPP Arts. 282-284
- [x] Testes unitários (30+ testes) passando - state machine + validator com `allow_none_response`
- [x] Testes de integração (20+ testes) - validação completa de todas as 6 perguntas
- [x] Test scenarios JSON com casos de teste da Seção 8 (6 passos com validação de erros)
- [x] Documentação completa - versão atualizada em README.md, CHANGELOG.md, API.md, TESTING.md
- [x] Backend completamente integrado - versão v0.12.2
- [x] **FRONTEND PENDENTE:** 22 pontos críticos para suporte completo de Seção 8

#### v0.11.0 (Dez 2025) - Seção 7: Apreensões e Cadeia de Custódia
- [x] **Seção 7: Apreensões e Cadeia de Custódia** - 4 perguntas (7.1 a 7.4)
- [x] State machine com lógica condicional (pula se não houve apreensão em 7.1)
- [x] **NOVA FUNCIONALIDADE:** Validação `allow_none_response` - Aceita "Nenhum objeto" sem exigir comprimento mínimo (questão 7.3)
- [x] Validação de graduação militar obrigatória em 7.2 e 7.4 (Soldado, Sargento, Cabo, Tenente, Capitão)
- [x] Validação de destino obrigatório em 7.4 (CEFLAN, Delegacia, Central, DP, etc.)
- [x] Validação de cadeia de custódia - Rastreamento completo (Quem → Onde → Como → Para Onde)
- [x] Geração de texto via LLM (Gemini + Groq) com fundamento jurídico Lei 11.343/06 + CPP Arts. 240§2 e 244
- [x] Estrutura narrativa em 2-3 parágrafos (Substâncias → Objetos → Acondicionamento)
- [x] **IMPORTANTE:** Seção 7 NÃO marca BO como completo - Seção 8 ainda virá (7/8 seções)
- [x] Testes unitários (16 testes) passando - state machine + validator com `allow_none_response`
- [x] Testes de integração (6 testes) - validação de graduação, destino, cadeia de custódia
- [x] Test scenarios JSON atualizado com casos de teste da Seção 7 (6 passos com validação de erros)
- [x] Documentação completa (TESTING.md com Testes 21-22, API.md com /start_section/7, CHANGELOG.md, README.md)
- [x] Backend completamente integrado - versão v0.11.0

#### v0.10.0 (Dez 2025) - Seção 6: Reação e Uso da Força
- [x] **Seção 6: Reação e Uso da Força** - 5 perguntas (6.1 a 6.5)
- [x] State machine com lógica condicional (pula se não houve resistência em 6.1)
- [x] **NOVA FUNCIONALIDADE:** Validação de frases proibidas em 6.2 (rejeita "resistiu ativamente", "uso moderado da força", etc.)
- [x] Validador de técnica e graduação militar obrigatória em 6.3
- [x] Validador de justificativa objetiva para algemas em 6.4 (palavras-chave obrigatórias)
- [x] **NOVA FUNCIONALIDADE:** Validação condicional de hospital em 6.5 (se mencionar ferimento, exige hospital/UPA + nº da ficha)
- [x] Geração de texto via LLM (Gemini + Groq) com fundamento jurídico Súmula Vinculante 11 (STF) + Decreto 8.858/2016
- [x] Estrutura narrativa obrigatória em 4 parágrafos (Resistência → Técnica → Algemas → Integridade Física)
- [x] Testes unitários (16 testes) passando - state machine + validator com frases proibidas
- [x] Testes de integração (6 testes) - validação de frases proibidas, graduação, hospital
- [x] Test scenarios JSON atualizado com casos de teste da Seção 6 (erro de validação + retry)
- [x] Documentação completa (TESTING.md com Testes 16-20, API.md com /start_section/6, CHANGELOG.md, README.md)
- [x] Frontend com 21-point checklist completo (color teal, startSection6, updateSidebarForSection6, etc.)
- [x] E2E automation com --start-section 6 para fast-start testing
- [x] Seção 6 marca BO como "COMPLETO" (6/8 seções implementadas)
- [x] Backend completamente integrado - versão v0.10.0

#### v0.9.0 (Dez 2025) - Seção 5: Fundada Suspeita
- [x] **Seção 5: Fundada Suspeita** - 4 perguntas (5.1 a 5.4)
- [x] State machine com lógica condicional (pula se não houve fundada suspeita)
- [x] Validador com graduação militar obrigatória em 5.3 (mesma regra de 3.3 e 4.3)
- [x] Validador de observação detalhada (5.2) - mínimo 40 caracteres com contexto
- [x] Validador de testemunha (5.3) - mínimo 30 caracteres + posição e observação concreta
- [x] Validador de características individualizadas (5.4) - mínimo 50 caracteres (roupa, porte, nome + vulgo)
- [x] Geração de texto via LLM (Gemini + Groq) com fundamento jurídico STF HC 261029
- [x] Testes unitários (12 testes) passando - state machine + validator
- [x] Test scenarios JSON atualizado com casos de teste da Seção 5
- [x] Documentação completa (TESTING.md, API.md, CHANGELOG.md, README.md)
- [x] Seção 5 marca BO como completo (Seção 5 é a última seção por agora - 5/8)
- [x] Backend completamente integrado - versão v0.9.0

#### v0.8.0 (Dez 2025) - Seção 4: Entrada em Domicílio
- [x] **Seção 4: Entrada em Domicílio** - 5 perguntas (4.1 a 4.5)
- [x] State machine com lógica condicional (pula se não houve entrada em domicílio)
- [x] Validador com graduação militar obrigatória em 4.3 (mesma regra de 3.3)
- [x] Validador de justa causa (4.2) - mínimo 40 caracteres com evidência sensorial ANTES da entrada
- [x] Validador de tipo de ingresso (4.4) - perseguição contínua, autorização ou flagrante visual
- [x] Validador de ações policiais (4.5) - mínimo 50 caracteres com descrição detalhada
- [x] Geração de texto via LLM (Gemini + Groq) com fundamento jurídico STF
- [x] Frontend completo com cor temática laranja (vs roxo da S3)
- [x] Testes unitários (13 testes) e de integração (7 testes) - 100% passando
- [x] E2E automation com --start-section 4 para fast-start testing
- [x] Documentação (TESTING.md, API.md, CHANGELOG.md, README.md)
- [x] Seção 4 marca BO como completo (mudado de Seção 3)

#### v0.7.1 (Dez 2025) - Fast-Start para E2E Tests
- [x] Flag `--start-section` para testes rápidos (economia de 70% de tempo)
- [x] Método `prepare_sections_via_api()` para restaurar seções anteriores
- [x] Método `inject_session_and_restore()` para injetar estado sem modal
- [x] Suporte a --start-section 4 para teste direto da Seção 4

#### v0.7.0 (Dez 2025) - Seção 3: Campana
- [x] **Seção 3: Campana (Vigilância Velada)** - 8 perguntas (3.1 a 3.8)
- [x] State machine com lógica condicional (pula se não houve campana)
- [x] Validador com graduação militar obrigatória (3.3)
- [x] Validador de atos concretos vs generalizações (3.6)
- [x] Perguntas opcionais aceitam "NÃO" (3.7 e 3.8)
- [x] Geração de texto via LLM (Gemini + Groq)
- [x] Frontend completo (sidebar, cards, draft)
- [x] Testes unitários e de integração
- [x] Documentação (API, TESTING, README)

### ✅ Fase 1 Concluída - Validação e Polimento (v0.4.1 - v0.6.4)

#### v0.6.0-v0.6.4 (Dez 2025)
- [x] **Groq API Integration** (v0.6.0) - Llama 3.3 70B com 14.400 req/dia
- [x] **Arquitetura Multi-Provider** - Gemini + Groq com fallback automático
- [x] **Sistema de Rascunhos** (v0.6.2) - Salvamento automático com localStorage (7 dias)
- [x] **Endpoint `/sync_session`** (v0.6.4) - Restauração atômica de rascunhos (10x mais rápido)
- [x] **Renumeração IDs Seção 2** (v0.6.4) - 2.0-2.7 → 2.1-2.8 para consistência
- [x] **Correção crítica persistência** (v0.6.4) - Rascunho não persiste após BO completo
- [x] **Migração automática** - Frontend detecta e converte rascunhos v0.6.3
- [x] **Correções edição e validação** (v0.6.1-v0.6.3) - Endpoint PUT, estrutura dict
- [x] **Suporte a múltiplas seções em rascunhos** - localStorage com Seção 1 + Seção 2

#### v0.5.1 (Dez 2025) - UX Multi-Seção
- [x] **UX Multi-Seção** - Melhorias críticas de experiência do usuário
- [x] Container persistente de textos gerados (todas seções visíveis)
- [x] Numeração completa de perguntas ([1.1], [2.3])
- [x] Sidebar com todas 8 seções (completadas, atual, futuras)
- [x] Botão "Copiar BO Completo" quando há 2+ seções
- [x] Layout responsivo (mobile/tablet/desktop)
- [x] Accordion nativo (`<details>`) para performance

#### v0.5.0 (Dez 2025) - Seção 2
- [x] **Seção 2: Abordagem a Veículo** - 8 perguntas (inicialmente 2.0-2.7)
- [x] Validação de placa Mercosul (ABC1D23, ABC-1D23)
- [x] Lógica condicional (pular seção se não houve veículo)
- [x] Geração de texto via LLM para Seção 2
- [x] Endpoint `/start_section/{section_number}`
- [x] Refatoração de sessions para suportar múltiplas seções (tupla → dict)

#### v0.4.1 (Dez 2025) - Validação e Logs
- [x] Salvamento automático de rascunho (localStorage, 7 dias)
- [x] Validação de data/hora futura
- [x] Sugestão de data/hora atual
- [x] Correção de encoding UTF-8
- [x] Dashboard de logs
- [x] Sistema de feedback (👍👎)

---

## [0.7.1] - 2025-12-21 ⚡ **FAST-START PARA E2E TESTS**

### ✨ Adicionado - Fast-Start Feature

- **Flag `--start-section`** em `automate_release.py`
  - Permite começar testes E2E a partir de uma seção específica (1, 2 ou 3)
  - Seções anteriores são preenchidas via API `/sync_session` (não abre navegador)
  - Economia de **70% no tempo de teste** (1.5 min vs 5 min)
  - Sintaxe: `python tests/e2e/automate_release.py --version v0.7.1 --start-section 3 --no-video`

- **Método `prepare_sections_via_api()`** em `automate_release.py`
  - Cria sessão via `/new_session` endpoint
  - Preenche seções via `/sync_session` com respostas pré-validadas
  - Usa httpx para requisições assíncronas (mais rápido)
  - Extrai IDs reais do `test_scenarios.json` (trata `_retry`, `edit_X_success`)

- **Método `inject_session_and_restore()`** em `automate_release.py`
  - Injeta estado da sessão via JavaScript (sem draft modal)
  - Cria botão "Iniciar Seção X" dinamicamente com CSS correto
  - Atualiza sidebar com seções completadas
  - Desabilita chat input para seções já preenchidas

- **Documentação atualizada**
  - [docs/TESTING.md](docs/TESTING.md) - Flag `--start-section` com exemplos e economia
  - [docs/SETUP.md](docs/SETUP.md) - Setup de Playwright e uso de fast-start
  - [README.md](README.md) - Novidades v0.7.1 e status atual

### 📝 Casos de Uso

```bash
# Completo (Seção 1 → 2 → 3) - ~5 min com vídeo
python tests/e2e/automate_release.py --version v0.7.1

# Apenas Seção 3 - ~1.5 min (70% mais rápido!)
python tests/e2e/automate_release.py --version v0.7.1 --start-section 3 --no-video

# Apenas Seção 2 - ~2 min (60% mais rápido)
python tests/e2e/automate_release.py --version v0.7.1 --start-section 2 --no-video
```

### 🔧 Detalhes Técnicos

- **Integração com `/sync_session`** - Endpoint criado em v0.6.4, agora usado em automação
- **JavaScript injection** - Abordagem limpa sem dependência de draft recovery modal
- **httpx async** - Requisições HTTP assíncronas (não bloqueia Playwright)
- **Respaldo total** - Se API falhar, script continua (trata exceções gracefully)

### 🐛 Problemas Resolvidos

- **Automação lenta** - Original preenchimento visual levava 5+ min
- **Vídeo capturava tudo** - Agora video só começa da seção escolhida
- **Múltiplos terminais** - Agora rápido o suficiente para testar em paralelo

### 📚 Documentação

**Adicionado:**
- Seção "Flag `--start-section`" em [docs/TESTING.md](docs/TESTING.md)
- Seção "Uso com Fast-Start" em [docs/SETUP.md](docs/SETUP.md)
- Exemplos de economia de tempo em ambos os docs

**Atualizado:**
- Versão em [docs/TESTING.md](docs/TESTING.md) → v0.7.1
- Versão em [docs/SETUP.md](docs/SETUP.md) → v0.7.1
- Status em [README.md](README.md) → v0.7.1

---

## [0.7.0] - 2025-12-21 🎯 **SEÇÃO 3: CAMPANA (VIGILÂNCIA VELADA)**

### ✨ Adicionado - Seção 3 Completa

- **Backend: State Machine (`state_machine_section3.py`)**
  - 8 perguntas (3.1 a 3.8) sobre campana/vigilância velada
  - Lógica condicional: se 3.1 = "NÃO", pula toda a seção
  - Métodos: `get_current_question()`, `store_answer()`, `next_step()`, etc.
  - Flag `section_skipped` para controle de seção pulada

- **Backend: Validador (`validator_section3.py`)**
  - Validação de graduação militar em 3.3 (Sargento, Cabo, Soldado, Tenente, Capitão)
  - Validação de atos concretos em 3.6 (mínimo 40 caracteres, rejeita generalizações)
  - Perguntas 3.7 e 3.8 aceitam "NÃO" como resposta válida
  - Comprimentos mínimos: 3.2 (30), 3.3 (30), 3.4 (20), 3.5 (10), 3.6 (40), 3.7/3.8 (3)

- **Backend: Integração (`main.py`)**
  - Endpoint `/start_section/3` para iniciar Seção 3
  - Chat endpoint com validação para Section 3
  - Endpoint `/sync_session` suporta steps 3.x
  - Endpoint `/update_answer` suporta edição de respostas da Seção 3
  - Geração de texto da Seção 3 integrada

- **Backend: LLM Service (`llm_service.py`)**
  - Método `generate_section3_text()` para gerar narrativa
  - Implementação para Gemini e Groq
  - Prompt enfatiza atos concretos e jurisprudência STF 2025

- **Frontend (`index.html`)**
  - Constante `SECTION3_QUESTIONS` com 8 perguntas
  - Card roxo para Seção 3 no container de textos
  - Função `startSection3()` para iniciar seção
  - Função `updateSidebarForSection3()` para atualizar sidebar
  - Botão "Iniciar Seção 3" após completar Seção 2
  - Sistema de rascunhos suporta Seção 3
  - "Copiar BO Completo" inclui Seção 3

### 🐛 Corrigido

- **Endpoint `/update_answer` não validava Seção 3**
  - Bug: Respostas 3.x caíam em "Step inválido"
  - Solução: Adicionado `elif step.startswith("3.")` na validação

### 🧪 Testes

- **Testes Unitários (`tests/unit/test_section3.py`)**
  - 6 testes para state machine
  - 8 testes para validador
  - Cobertura: inicialização, skip logic, fluxo completo, validações

- **Testes de Integração (`tests/integration/test_section3_flow.py`)**
  - Sincronização Seção 3 incompleta
  - Sincronização completa (3 seções)
  - Sincronização com Seção 3 pulada
  - Validação de graduação militar
  - Validação de atos concretos
  - Perguntas opcionais

### 📚 Documentação

- **TESTING.md**: Testes 9-12 para Seção 3
- **API.md**: Endpoints e exemplos para Seção 3
- **README.md**: Atualizado para v0.7.0

### 🔍 Impacto

- **12 arquivos criados/modificados**
- **~650 linhas** de código
- **22 respostas** no fluxo completo (6 + 8 + 8)

---

## [0.6.4] - 2025-12-20 🎯 **CORREÇÃO CRÍTICA: Sistema de Rascunhos**

### ✨ Novo - Endpoint de Sincronização em Bloco
- **CRÍTICO: Implementado `/sync_session` para restauração de rascunhos**
  - Problema anterior: `restoreFromDraft()` fazia 1 requisição HTTP por resposta (14 requests para BO completo)
  - Tempo anterior: 14-20 segundos (1-1.5s por request)
  - Risco: Estado inconsistente se requisição falhasse no meio
  - Solução: Endpoint que processa todas as respostas atomicamente em 1 requisição
  - Performance: **10-14x mais rápido** (1-2s vs 14-20s)
  - Garantia: Sincronização atômica (ou processa tudo, ou falha tudo)
  - Arquivos: `backend/main.py` linhas 422-508

### 🔧 Refatorado - Sistema de Rascunhos v0.6.4
- **Enhanced saveDraft() - Estrutura completa**
  - Agora salva: `chatHistory` + `generatedTexts` + `sectionStatuses`
  - Permite restauração exata da interface visual
  - Arquivos: `docs/index.html` linhas 380-439

- **Reescrito restoreFromDraft() - Sincronização em bloco**
  - Usa `/sync_session` em vez de loop serial de 14 requests
  - Migração automática de IDs v0.6.3 (2.0-2.7 → 2.1-2.8)
  - Fallback para rascunhos sem `chatHistory`
  - Estado sincronizado atomicamente com backend
  - Arquivos: `docs/index.html` linhas 475-679

### 🔄 Alterado - Renumeração de IDs da Seção 2
- **BREAKING CHANGE: IDs renumerados para consistência**
  - Antes: 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
  - Agora: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
  - Motivação: Padrão consistente com Seção 1 (que usa 1.1-1.6)
  - Compatibilidade: Migração automática para rascunhos v0.6.3
  - Arquivos:
    - Backend: `state_machine_section2.py` (linhas 14-24)
    - Backend: `validator_section2.py` (linhas 17-87)
    - Frontend: `index.html` (linhas 307-316)

### ✨ Novo - Lógica de Seção "Não Aplicável"
- **Seção 2 pulada quando não há veículo**
  - Pergunta 2.1: "Havia veículo?"
  - Se resposta = "NÃO" → Seção marcada como `NOT_APPLICABLE`
  - UI mostra texto explicativo em cinza/itálico
  - BO finalizado (até Seção 3 ser implementada)
  - Arquivos:
    - Backend: `state_machine_section2.py` (linhas 59-67, 91-95)
    - Backend: `main.py` (linhas 243-269)
    - Frontend: `index.html` (linhas 1550-1570)

### 🐛 Corrigido - Persistência de Rascunho Após Conclusão
- **CRÍTICO: Rascunho aparecia após completar todas as seções**
  - Bug #1: `answersState` resetado ao iniciar Seção 2 (linha 1541)
    - Causava perda de respostas da Seção 1
    - Solução: Removido reset, `answersState` agora mantém todas as respostas
  - Bug #2: `beforeunload` salvava rascunho mesmo após BO completo
    - Solução: Adicionada flag `boCompleted` [index.html:328](docs/index.html#L328)
    - Flag marcada como `true` quando Seção 2 finaliza [index.html:1575](docs/index.html#L1575)
    - `beforeunload` verifica `!boCompleted` antes de salvar [index.html:1653](docs/index.html#L1653)
  - Bug #3: Flag não resetada em nova sessão
    - Solução: `boCompleted = false` em `startSession()` [index.html:1351](docs/index.html#L1351)
  - Arquivos: `docs/index.html` (linhas 328, 1351, 1402, 1575, 1653)

### 🧪 Testes
- **8 testes backend (test_backend_changes.py)**: ✅ 100% passando
- **4 testes integração (test_integration_sync.py)**: ✅ 100% passando
  - Sincronização Seção 1 incompleta
  - Sincronização Seção 2 incompleta
  - Sincronização completa (14 respostas)
  - Seção 2 pulada (NÃO havia veículo)
- **Teste manual persistência**: ✅ 100% passando
  - Rascunho salvo até pergunta 2.7 → Recarrega → Modal aparece ✓
  - Completa 2.8 → Recarrega → Modal NÃO aparece ✓

### 🔍 Impacto
- **4 arquivos modificados** (3 backend, 1 frontend)
- **~500 linhas** alteradas/adicionadas
- **Compatibilidade retroativa** com v0.6.3 (migração automática)
- **Performance**: Restauração de rascunho 10x mais rápida
- **Consistência**: IDs alinhados, estado sincronizado atomicamente

---

## [0.6.3] - 2025-12-20

### 🐛 Corrigido - Restauração de Rascunhos com Múltiplas Seções
- **CRÍTICO: Respostas restauradas fora de ordem**
  - Problema: `Object.entries()` não garante ordem, causava respostas da Seção 2 aparecerem na Seção 1
  - Exemplo: Resposta de 2.1 aparecia em 1.1, resposta de 2.2 aparecia em 1.2
  - Solução: Implementado sort customizado que ordena por seção e step numericamente:
    ```javascript
    const sortedSteps = Object.keys(answersState).sort((a, b) => {
        const [sectionA, stepA] = a.split('.').map(Number);
        const [sectionB, stepB] = b.split('.').map(Number);
        if (sectionA !== sectionB) return sectionA - sectionB;
        return stepA - stepB;
    });
    ```
  - Arquivos: `docs/index.html` linhas 519-524

- **CRÍTICO: Backend não iniciava Seção 2 ao restaurar rascunho**
  - Problema: Ao restaurar rascunho da Seção 2, backend continuava na Seção 1
  - Solução: Adicionada chamada `POST /start_section/2` antes de sincronizar respostas da Seção 2
  - Arquivos: `docs/index.html` linhas 532-543

---

## [0.6.2] - 2025-12-20

### 🐛 Corrigido - Sistema de Rascunhos (LocalStorage)
- **CRÍTICO: Sistema de rascunhos quebrado com Seção 2**
  - Problema 1: `saveDraft()` não salvava `currentSection`, causando erro ao restaurar
  - Problema 2: `formatDraftPreview()` sempre mostrava "X/6" mesmo na Seção 2 (deveria mostrar "X/14")
  - Problema 3: `restoreFromDraft()` assumia apenas Seção 1, quebrava com perguntas 2.x
  - Solução:
    - `saveDraft()` agora salva `currentSection` e atualiza version para '0.6.2'
    - `formatDraftPreview()` detecta automaticamente Seção 2 via `step.startsWith('2.')`
    - `restoreFromDraft()` refatorado para suportar ambas seções:
      - Restaura `currentSection` com fallback para v0.5.x
      - Busca perguntas de `SECTION1_QUESTIONS` ou `SECTION2_QUESTIONS` conforme step
      - Calcula progresso dinamicamente (6 ou 8 perguntas)
      - Determina próxima pergunta baseada em `sectionNum` e `stepNum`
  - Arquivos: `docs/index.html` linhas 359, 436-461, 475-583

### 🧪 Testes
- Adicionado script `test_draft_recovery.py` com Playwright para validar restauração de rascunhos
- Cobertura: Seção 1 (3 perguntas) e Seção 2 (8 perguntas da S1 + 2 da S2)

---

## [0.6.1] - 2025-12-20

### 🐛 Corrigido - Backend
- **CRÍTICO: Arquivo .env não estava sendo carregado**
  - Problema: Backend rodando de `backend/` não carregava `.env` corretamente
  - Solução: `.env` movido para raiz do projeto (`C:\AI\bo-assistant\.env`)
  - Backend deve ser iniciado do diretório raiz: `python -m uvicorn backend.main:app`
  - GROQ_API_KEY agora é carregado corretamente na inicialização

- **Endpoint de edição quebrado após refatoração multi-seção**
  - Problema: `PUT /chat/{session_id}/answer/{step}` tentava desempacotar `sessions[session_id]` como tupla
  - Causa: Estrutura mudou de tupla `(bo_id, state_machine)` para dict `{"bo_id": ..., "sections": {...}}`
  - Solução: Acessa `session_data["bo_id"]` e determina state_machine baseado no prefixo do step (1.x ou 2.x)
  - Commits: `f5bc007`

### 🐛 Corrigido - Automação de Release
- **Script de automação falhando na edição**
  - Problema: Seletor de input não aguardava elemento ficar visível
  - Solução: Adicionado `wait_for_selector('input.px-2', state='visible')` antes de interagir
  - Commits: `ef0b723`

- **Vídeo não capturando início da Seção 2**
  - Problema: Scroll para topo acontecia ANTES do click, depois página voltava
  - Solução: Movido scroll para DEPOIS do click no botão "Iniciar Seção 2"
  - Commits: `bd1b569`

- **Screenshot mobile da sidebar com sobreposição visual**
  - Problema: `full_page=True` fazia scroll e conteúdo aparecia através da sidebar fixed
  - Solução: Mudado para `full_page=False` (captura apenas viewport 430x932px)
  - Commits: `9041dfc`

### 🔧 Técnico
- **Frontend**: Suporte para `127.0.0.1` além de `localhost` na detecção de ambiente local
- **Frontend**: Versão atualizada para v0.6.1 em 3 locais (header, footer, JS)
- **Backend**: Removidos prints de debug temporários usados no diagnóstico
- **Backend**: Validação correta por seção no endpoint de edição (ResponseValidator vs ResponseValidatorSection2)
- **Documentação**: CLAUDE.md atualizado com comandos corretos de startup e troubleshooting

### ⚠️ Breaking Changes
- Arquivo `.env` DEVE estar na raiz do projeto, não mais em `backend/.env`
- Comando de startup mudou de `cd backend && uvicorn main:app` para `python -m uvicorn backend.main:app` (do diretório raiz)

### 📚 Lições Aprendidas
1. **python-dotenv carrega .env do CWD (current working directory)**
   - Se backend roda de `backend/`, procura `.env` em `backend/.env`
   - Se backend roda da raiz, procura `.env` na raiz
   - Solução: Sempre rodar de um diretório fixo e documentar

2. **Estruturas de dados em APIs devem ser imutáveis ou bem documentadas**
   - Mudança de tupla para dict quebrou endpoint de edição
   - Testes automatizados pegaram o bug imediatamente

3. **Screenshots full_page com elementos fixed/absolute**
   - `full_page=True` faz scroll virtual da página toda
   - Elementos `position: fixed` (como sidebar mobile) podem ter problemas
   - Usar `full_page=False` para capturar overlays/modals

4. **Ordem de operações em automação importa**
   - Scroll antes de click pode ser revertido pelo próprio click
   - Sempre testar a ordem: ação → efeito → captura

### ✅ Validado
- ✅ Groq API funcionando corretamente em localhost
- ✅ Seção 1 e Seção 2 gerando textos com sucesso
- ✅ Edição de respostas funcionando (ambas seções)
- ✅ Automação de release completa (screenshots + vídeo)
- ✅ `.env` está no `.gitignore` (linha 12) - seguro para commit

---

## [0.6.0] - 2025-12-20

### ✨ Adicionado
- **Suporte ao Groq API (Llama 3.3 70B)**
  - Integração completa com Groq para Seção 1 e Seção 2
  - 14.400 requisições/dia (720x mais que Gemini 2.5 Flash)
  - Modelo llama-3.3-70b-versatile com temperature 0.3
  - Tratamento de erro específico para rate limits do Groq

- **Arquitetura Multi-Provider Consolidada**
  - Backend suporta múltiplos providers: Gemini, Groq
  - Preparado para Claude e OpenAI (TODOs documentados)
  - Método `validate_api_keys()` inclui Groq
  - Fácil troca de provider no frontend (1 linha)

### 🔧 Técnico
- **Backend**: `groq==1.0.0` adicionado ao requirements.txt
- **Backend**: Novos métodos `_generate_with_groq()` e `_generate_section2_with_groq()`
- **Backend**: Provider routing atualizado em ambas seções
- **Frontend**: `llm_provider` alterado de 'gemini' para 'groq' (linhas 520, 1149, 1408)

### 🎯 Benefícios
- **Testes intensivos**: 14.4k req/dia permite iterações rápidas na fase de desenvolvimento
- **Flexibilidade**: Arquitetura permite voltar para Gemini ou testar outros providers facilmente
- **Custo zero**: Groq free tier sem necessidade de cartão de crédito
- **Performance**: Groq é 2-3x mais rápido que Gemini em média

### 🐛 Corrigido
- Atualizado Groq de 0.11.0 para 1.0.0 (compatibilidade com httpx 0.28.1)
- Erro de quota do Gemini agora tem mensagem específica (429 vs 500)

---

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

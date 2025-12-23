# 🧪 Guia de Testes - BO Inteligente

**Versão:** v0.12.0
**Última atualização:** 23/12/2025

Este documento cobre estratégias de teste, casos de teste manuais, automação de screenshots e respostas de teste validadas.

---

## 📋 Índice

- [Estrutura de Testes](#-estrutura-de-testes)
- [Estratégias de Teste](#-estratégias-de-teste)
- [Casos de Teste Manuais](#-casos-de-teste-manuais)
- [Respostas de Teste Validadas](#-respostas-de-teste-validadas)
- [Automação de Screenshots](#-automação-de-screenshots)
- [Testes de Carga](#-testes-de-carga)

---

## 📁 Estrutura de Testes

**Versão:** v0.6.4+

Os testes foram reorganizados em uma estrutura hierárquica por camada:

```
tests/
├── README.md                # Guia rápido de como rodar testes
├── conftest.py              # Fixtures pytest compartilhadas
├── pytest.ini               # Configuração pytest
│
├── unit/                    # Testes unitários (sem I/O)
│   └── test_backend_changes.py
│
├── integration/             # Testes de integração (com backend)
│   ├── test_complete_flow.py
│   ├── test_sync_session.py
│   ├── test_draft_persistence.py
│   ├── test_draft_recovery.py
│   └── test_section1_isolated.py
│
├── e2e/                     # Testes E2E (Playwright)
│   ├── README.md
│   ├── automate_release.py
│   └── test_scenarios.json
│
└── fixtures/                # Dados de teste
    └── valid_payload.json
```

### Como Rodar

```bash
# Unit tests (rápido - ~5s, não precisa de backend)
pytest tests/unit

# Integration tests (médio - ~30s, precisa de backend rodando)
pytest tests/integration

# E2E screenshots - MODO COMPLETO (longo - ~10min, precisa backend + frontend)
python tests/e2e/automate_release.py --version v0.12.0

# E2E screenshots - MODO RÁPIDO (começar da Seção 8)
# Preenche Seções 1-7 via API, tira screenshots apenas da Seção 8
python tests/e2e/automate_release.py --version v0.12.0 --start-section 8 --no-video

# E2E screenshots - Começar da Seção 7
python tests/e2e/automate_release.py --version v0.12.0 --start-section 7 --no-video

# E2E screenshots - Começar da Seção 6
python tests/e2e/automate_release.py --version v0.12.0 --start-section 6 --no-video

# E2E screenshots - Começar da Seção 5
python tests/e2e/automate_release.py --version v0.12.0 --start-section 5 --no-video

# E2E screenshots - Com vídeo (precisa MAIS tempo)
python tests/e2e/automate_release.py --version v0.12.0

# Todos os testes pytest juntos
pytest
```

Veja [tests/README.md](../tests/README.md) para detalhes completos.

---

## 🎯 Estratégias de Teste

### Tipos de Teste

| Tipo | Objetivo | Ferramenta | Status |
|------|----------|------------|--------|
| **Manual** | Validar UX e casos de uso reais | Navegador | ✅ Ativo |
| **Automação E2E** | Screenshots de releases | Playwright | ✅ Ativo |
| **Unitário** | Validadores e state machines | pytest | ⏳ Planejado |
| **Integração** | Endpoints da API | FastAPI TestClient | ⏳ Planejado |
| **Carga** | Comportamento sob alta demanda | Locust | ⏳ Planejado |

---

### Cobertura de Testes

**Áreas Críticas:**
- ✅ Validação de respostas (Seções 1, 2, 3, 4, 5, 6 e 7)
- ✅ Geração de texto (Gemini e Groq)
- ✅ Sistema de rascunhos (localStorage)
- ✅ Fluxo multi-seção (Seção 1 → Seção 2 → ... → Seção 7)
- ✅ Edição de respostas anteriores
- ✅ Endpoint `/sync_session` (restauração de rascunhos)
- ✅ Validação de graduação militar (Seções 3, 4, 5 e 7)
- ✅ Validação de justa causa (Seção 4)
- ✅ Validação de frases proibidas (Seção 6)
- ✅ Validação condicional de hospital (Seção 6)
- ✅ Validação de resposta negativa `allow_none_response` (Seção 7, questão 7.3) - NOVO
- ✅ Validação de destino obrigatório (Seção 7, questão 7.4) - NOVO
- ✅ Validação de cadeia de custódia (Seção 7) - NOVO
- ⏳ Casos de erro (rate limit, timeout)
- ⏳ Navegação mobile (responsividade)

---

## 🖐️ Casos de Teste Manuais

### Teste 1: Fluxo Feliz - Seção 1 Completa

**Objetivo:** Validar fluxo completo da Seção 1 com respostas válidas.

**Passos:**
1. Acessar https://criscmaia.github.io/bo-assistant/
2. Responder pergunta 1.1 (ver [Respostas Validadas](#respostas-validadas-seção-1))
3. Clicar em "Enviar"
4. Repetir para perguntas 1.2 até 1.6
5. Aguardar geração de texto (~3-5 segundos)
6. Verificar texto gerado no card de Seção 1

**Resultado Esperado:**
- Todas as respostas aceitas
- Texto gerado em 3ª pessoa
- Botão "Iniciar Seção 2" visível
- Card de Seção 1 permanece na tela

---

### Teste 2: Validação de Data/Hora Futura

**Objetivo:** Verificar se sistema rejeita datas futuras.

**Passos:**
1. Iniciar nova sessão
2. Responder pergunta 1.1 com data futura (ex: "30/12/2025, às 15h30")
3. Clicar em "Enviar"

**Resultado Esperado:**
- Mensagem de erro: "Por favor, não insira uma data futura. A ocorrência deve ser no passado ou hoje."
- Pergunta 1.1 permanece ativa
- Resposta não é armazenada

---

### Teste 3: Edição de Resposta Anterior

**Objetivo:** Validar funcionalidade de edição.

**Passos:**
1. Responder perguntas 1.1, 1.2, 1.3
2. Clicar no botão "Editar" da resposta 1.2
3. Alterar texto e clicar em "Salvar"
4. Continuar respondendo 1.4, 1.5, 1.6

**Resultado Esperado:**
- Resposta 1.2 atualizada com sucesso
- Texto gerado final inclui resposta editada
- Sem erros de validação

---

### Teste 4: Fluxo Multi-Seção (Seção 1 + 2)

**Objetivo:** Validar transição entre seções.

**Passos:**
1. Completar Seção 1
2. Clicar em "Iniciar Seção 2"
3. Responder pergunta 2.1 com "SIM"
4. Completar perguntas 2.2 até 2.8
5. Aguardar geração de texto
6. Clicar em "Copiar BO Completo"

**Resultado Esperado:**
- Seção 2 inicia corretamente
- Card de Seção 1 permanece visível
- Seção 2 gera texto independente
- Botão "Copiar BO Completo" copia ambas as seções
- Formato: "=== Seção 1 ===\n\n{texto1}\n\n=== Seção 2 ===\n\n{texto2}"

---

### Teste 5: Pular Seção 2 (Sem Veículo)

**Objetivo:** Validar lógica condicional da Seção 2.

**Passos:**
1. Completar Seção 1
2. Clicar em "Iniciar Seção 2"
3. Responder pergunta 2.1 com "NÃO"

**Resultado Esperado:**
- Texto gerado imediatamente
- Mensagem: "Não se aplica (não havia veículo envolvido na ocorrência)"
- Seção 2 marcada como completa
- Sem perguntas adicionais

---

### Teste 6: Validação de Placa Mercosul

**Objetivo:** Validar formato de placa específico.

**Passos:**
1. Completar Seção 1
2. Iniciar Seção 2 e responder 2.1 com "SIM"
3. Responder 2.2 com placa inválida:
   - "ABC123" (formato antigo)
   - "ABC12D3" (ordem errada)
   - "1ABC2D3" (começa com número)

**Resultado Esperado:**
- Mensagem de erro: "Por favor, inclua a placa do veículo no formato Mercosul (ABC1D23 ou ABC-1D23)."
- Resposta não aceita

**Respostas Válidas:**
- "ABC1D23"
- "ABC-1D23"
- "XYZ9W87"

---

### Teste 7: Sistema de Rascunhos

**Objetivo:** Validar salvamento automático e restauração.

**Passos:**
1. Responder perguntas 1.1, 1.2, 1.3
2. Fechar o navegador
3. Reabrir a página
4. Verificar se modal "Rascunho encontrado" aparece
5. Clicar em "Restaurar"

**Resultado Esperado:**
- Modal com botões "Restaurar" e "Descartar"
- Restauração rápida (~1-2 segundos)
- Estado completo restaurado (respostas + progresso)
- Pergunta atual correta (1.4)

---

### Teste 8: Expiração de Rascunho

**Objetivo:** Verificar expiração de 7 dias.

**Passos:**
1. Criar rascunho
2. Abrir DevTools → Application → Local Storage
3. Editar timestamp para 8 dias atrás
4. Recarregar página

**Resultado Esperado:**
- Rascunho não é restaurado
- Modal não aparece
- Sessão nova inicia do zero

---

### Teste 9: Fluxo Completo (Seção 1 + 2 + 3 + 4)

**Objetivo:** Validar fluxo completo com todas as quatro seções.

**Passos:**
1. Completar Seção 1 (perguntas 1.1 a 1.6)
2. Clicar em "Iniciar Seção 2"
3. Responder pergunta 2.1 com "SIM"
4. Completar Seção 2 (perguntas 2.2 a 2.8)
5. Clicar em "Iniciar Seção 3"
6. Responder pergunta 3.1 com "SIM"
7. Completar Seção 3 (perguntas 3.2 a 3.8)
8. Clicar em "Iniciar Seção 4"
9. Responder pergunta 4.1 com "SIM"
10. Completar Seção 4 (perguntas 4.2 a 4.5)

**Resultado Esperado:**
- Todas as quatro seções aparecem no container de textos gerados
- Seções 1, 2, 3 completadas aparecem como cards com checkmark na sidebar
- Texto gerado em 3ª pessoa para cada seção
- Botão "Copiar BO Completo" copia todas as quatro seções
- BO marcado como completo

---

### Teste 10: Pular Seção 4 (Sem Entrada em Domicílio)

**Objetivo:** Validar lógica condicional da Seção 4.

**Passos:**
1. Completar Seções 1, 2 e 3
2. Clicar em "Iniciar Seção 4"
3. Responder pergunta 4.1 com "NÃO"

**Resultado Esperado:**
- Texto gerado imediatamente
- Mensagem: "Não se aplica (não houve entrada em domicílio)"
- Seção 4 marcada como completa
- Sem perguntas adicionais (4.2-4.5)
- BO marcado como completo

---

### Teste 11: Validação de Justa Causa (Seção 4, Pergunta 4.2)

**Objetivo:** Validar obrigatoriedade de descrição detalhada da justa causa.

**Passos:**
1. Completar Seções 1, 2 e 3
2. Iniciar Seção 4 e responder 4.1 com "SIM"
3. Ao chegar em 4.2, responder sem detalhes:
   - "Viu algo"
   - "Suspeito dentro"
   - "Tinha droga lá"

**Resultado Esperado:**
- Mensagem de erro: "Descreva o que foi visto/ouvido/sentido ANTES da entrada..."
- Resposta não aceita
- Pergunta permanece ativa

**Respostas Válidas:**
- "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria"
- "Ouvimos sons de descarga no banheiro, compatíveis com eliminação de drogas"
- "Sentimos forte odor de maconha vindo da janela aberta"

---

### Teste 12: Validação de Ações Policiais (Seção 4, Pergunta 4.5)

**Objetivo:** Validar descrição detalhada das ações de cada policial.

**Passos:**
1. Chegar na pergunta 4.5
2. Tentar responder com generalização:
   - "Entraram"
   - "Fizeram busca"
   - "Encontraram drogas"

**Resultado Esperado:**
- Mensagem de erro: "Descreva ação por ação: quem entrou primeiro, por onde, quem ficou na contenção..."
- Resposta rejeitada

**Respostas Válidas:**
- "O Sargento Silva entrou primeiro pela porta. O Cabo Almeida ficou na contenção. O Soldado Pires procurou dentro"
- "O policial A entrou pela frente, B ficou observando a porta dos fundos, C revistou o interior localizando os entorpecentes"

---

### Teste 13: Fluxo Completo - Seção 5 (Fundada Suspeita)

**Objetivo:** Validar fluxo completo da Seção 5 com respostas válidas.

**Passos:**
1. Completar Seções 1, 2, 3 e 4
2. Clicar em "Iniciar Seção 5"
3. Responder pergunta 5.1 com "SIM"
4. Completar perguntas 5.2 até 5.4 com respostas válidas
5. Aguardar geração de texto (~3-5 segundos)
6. Verificar texto gerado no card de Seção 5

**Resultado Esperado:**
- Todas as respostas aceitas
- Texto gerado em 3ª pessoa
- BO marcado como "COMPLETO"
- Card de Seção 5 permanece visível com texto narrativo
- Botão "Copiar BO Completo" copia todas as 5 seções

---

### Teste 14: Pular Seção 5 (Sem Fundada Suspeita)

**Objetivo:** Validar lógica condicional da Seção 5.

**Passos:**
1. Completar Seções 1, 2, 3 e 4
2. Clicar em "Iniciar Seção 5"
3. Responder pergunta 5.1 com "NÃO"

**Resultado Esperado:**
- Texto gerado imediatamente
- Mensagem: "Não se aplica (não houve abordagem por fundada suspeita)"
- Seção 5 marcada como completa
- BO marcado como "COMPLETO"
- Sem perguntas adicionais

---

### Teste 15: Validação de Graduação Militar (Seção 5, Pergunta 5.3)

**Objetivo:** Validar obrigatoriedade de graduação militar em pergunta 5.3.

**Passos:**
1. Completar Seções 1-4 e iniciar Seção 5
2. Responder 5.1 com "SIM" e 5.2 com resposta válida
3. Ao chegar em 5.3, responder sem graduação:
   - "João viu o suspeito retirando invólucros"
   - "O policial viu do carro"

**Resultado Esperado:**
- Mensagem de erro: "Informe a GRADUAÇÃO + nome do policial, de onde viu e o que exatamente viu. Exemplo: 'O Sargento João viu...'"
- Resposta não aceita
- Pergunta permanece ativa

**Respostas Válidas:**
- "O Sargento João, de dentro da viatura estacionada a 20 metros, visualizou o suspeito retirando invólucros do buraco"
- "O Cabo Almeida, posicionado na esquina oposta, viu o indivíduo entregar pacotes"
- "O Soldado Pires, de pé próximo ao poste, observou todo o procedimento"

---

### Teste 16: Fluxo Completo - Seção 6 (Reação e Uso da Força)

**Objetivo:** Validar fluxo completo da Seção 6 com respostas válidas.

**Passos:**
1. Completar Seções 1 a 5
2. Clicar em "Iniciar Seção 6"
3. Responder pergunta 6.1 com "SIM"
4. Completar perguntas 6.2 até 6.5 com respostas válidas
5. Aguardar geração de texto (~3-5 segundos)
6. Verificar texto gerado no card de Seção 6

**Resultado Esperado:**
- Todas as respostas aceitas
- Texto gerado em 3ª pessoa, narrando a resistência, técnica aplicada, algemas e integridade física
- BO marcado como "COMPLETO"
- Card de Seção 6 permanece visível com texto narrativo
- Botão "Copiar BO Completo" copia todas as 6 seções

---

### Teste 17: Validação de Frases Proibidas (Seção 6, Pergunta 6.2) - NOVO

**Objetivo:** Validar rejeição de frases genéricas e obrigação de descrição concreta.

**Passos:**
1. Completar Seções 1-5 e iniciar Seção 6
2. Responder 6.1 com "SIM"
3. Ao chegar em 6.2, tentar responder com frases genéricas:
   - "O autor resistiu ativamente"
   - "Foi necessário uso moderado da força"
   - "O autor estava exaltado"
   - "Houve resistência"

**Resultado Esperado:**
- Mensagem de erro: "NÃO use a expressão '[frase]'. Descreva o que o autor FEZ..."
- Resposta não aceita
- Pergunta permanece ativa
- Força descrição concreta (soco, empurrão, fuga, etc.)

**Respostas Válidas:**
- "O autor empurrou o Cabo Rezende com força no peito tentando fugir"
- "O suspeito desferiu um soco em direção ao rosto do Sargento Silva"
- "O indivíduo recusou-se a colocar as mãos na cabeça e tentou sacar objeto da cintura"

---

### Teste 18: Validação de Técnica e Graduação (Seção 6, Pergunta 6.3)

**Objetivo:** Validar obrigatoriedade de graduação militar + técnica aplicada em 6.3.

**Passos:**
1. Completar Seções 1-5 e iniciar Seção 6
2. Responder 6.1 com "SIM" e 6.2 com resposta válida
3. Ao chegar em 6.3, responder sem graduação:
   - "João aplicou chave de braço"
   - "Técnica de imobilização foi utilizada"

**Resultado Esperado:**
- Mensagem de erro: "Informe: GRADUAÇÃO + nome do policial, qual técnica usou..."
- Resposta não aceita
- Pergunta permanece ativa

**Respostas Válidas:**
- "O Cabo Marcelo aplicou chave de braço no suspeito, imobilizando-o no chão sem lesões"
- "O Sargento Silva desviou do soco e aplicou golpe defensivo no braço do agressor"
- "O Soldado Pires empurrou o autor contra o muro, contendo a agressão"

---

### Teste 19: Validação Condicional de Hospital (Seção 6, Pergunta 6.5)

**Objetivo:** Validar que se mencionar ferimentos, exige informações de hospital/UPA com número da ficha.

**Passos:**
1. Completar Seções 1-5 e iniciar Seção 6
2. Responder 6.1 com "SIM" e completar 6.2, 6.3, 6.4
3. Ao chegar em 6.5:

   **Teste 19a - Sem ferimentos (válido):**
   ```
   Não houve ferimentos. A guarnição verificou a integridade física...
   ```
   - Resultado: ACEITO

   **Teste 19b - Com ferimento mas SEM hospital (inválido):**
   ```
   O autor apresentou escoriação no joelho esquerdo
   ```
   - Resultado: REJEITADO (falta hospital/UPA)
   - Mensagem: "Se SIM: descreva a lesão, onde foi atendido (hospital/UPA) e o número da ficha"

   **Teste 19c - Com ferimento E hospital + ficha (válido):**
   ```
   O autor apresentou escoriação no joelho esquerdo. Foi atendido no Hospital João XXIII (ficha nº 2025-12345)
   ```
   - Resultado: ACEITO

**Resultado Esperado:**
- Seção 6.5 força informação de hospital quando há lesão
- Número de ficha obrigatório (ficha nº, nº, número, etc.)
- Respostas sem ferimentos são aceitas sem exigir hospital
- BO marcado como completo

---

### Teste 20: Pular Seção 6 (Sem Resistência)

**Objetivo:** Validar lógica condicional da Seção 6.

**Passos:**
1. Completar Seções 1 a 5
2. Clicar em "Iniciar Seção 6"
3. Responder pergunta 6.1 com "NÃO"

**Resultado Esperado:**
- Texto gerado imediatamente
- Mensagem: "Não se aplica (não houve resistência durante a abordagem)"
- Seção 6 marcada como completa
- BO marcado como "COMPLETO"
- Sem perguntas adicionais (6.2-6.5)

---

### Teste 21: Fluxo Completo - Seção 7 (Apreensões e Cadeia de Custódia)

**Objetivo:** Validar fluxo completo da Seção 7 com respostas válidas.

**Passos:**
1. Completar Seções 1 a 6
2. Clicar em "Iniciar Seção 7"
3. Responder pergunta 7.1 com "SIM"
4. Completar perguntas 7.2 até 7.4 com respostas válidas:
   - **7.2:** "O Soldado Breno encontrou 14 pedras de substância análoga ao crack dentro de uma lata azul sobre o banco de concreto próximo ao portão da casa 12"
   - **7.3:** "Foram apreendidos R$ 450,00 em notas de R$ 10 e R$ 20, 2 celulares Samsung e 1 balança de precisão"
   - **7.4:** "O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02, fotografou todos os itens no local e ficou responsável pelo material até a entrega na CEFLAN 2"
5. Aguardar geração de texto (~3-5 segundos)
6. Verificar texto gerado no card de Seção 7

**Resultado Esperado:**
- Todas as respostas aceitas
- Texto gerado em 3ª pessoa, narrando substâncias, objetos e cadeia de custódia
- Card de Seção 7 permanece visível com texto narrativo
- Botão "Copiar BO Completo" copia todas as 7 seções
- **IMPORTANTE:** BO NÃO é marcado como "COMPLETO" (Seção 8 ainda virá) - botão de transição para Seção 8 visível
- Alerta: "📷 ATENÇÃO: Fotografar itens e anexar no BO"

---

### Teste 22: Pular Seção 7 (Sem Apreensão de Drogas)

**Objetivo:** Validar lógica condicional da Seção 7.

**Passos:**
1. Completar Seções 1 a 6
2. Clicar em "Iniciar Seção 7"
3. Responder pergunta 7.1 com "NÃO"

**Resultado Esperado:**
- Texto gerado imediatamente
- Mensagem: "Não se aplica (não houve apreensão de drogas)"
- Seção 7 marcada como completa
- **IMPORTANTE:** BO NÃO é marcado como "COMPLETO" (aguardando Seção 8)
- Sem perguntas adicionais (7.2-7.4)
- Botão de transição para Seção 8 visível

---

### Teste 11: Validação de Graduação Militar (Seção 3)

**Objetivo:** Validar obrigatoriedade de graduação militar em pergunta 3.3.

**Passos:**
1. Completar Seção 1 e 2
2. Iniciar Seção 3 e responder 3.1 com "SIM"
3. Responder perguntas 3.2, 3.4, 3.5, 3.6 com respostas válidas
4. Ao chegar em 3.3, responder sem graduação:
   - "Silva tinha visão da porta"
   - "O policial viu a entrega"

**Resultado Esperado:**
- Mensagem de erro: "Informe qual policial (graduação + nome) tinha visão direta..."
- Resposta não aceita
- Pergunta permanece ativa

**Respostas Válidas:**
- "O Sargento Silva tinha visão desobstruída"
- "O Cabo Almeida observava pelo portão"
- "O Soldado Faria conseguia ver a entrada"

---

### Teste 12: Validação de Atos Concretos (Seção 3, Pergunta 3.6)

**Objetivo:** Validar descrição de atos específicos vs generalizações.

**Passos:**
1. Chegar na pergunta 3.6
2. Tentar responder com generalização:
   - "Atitude suspeita"
   - "Movimentação estranha"
   - "Comportamento duvidoso"

**Resultado Esperado:**
- Mensagem de erro: "Descreva atos CONCRETOS observados (trocas, entregas, esconderijos). NÃO use generalizações..."
- Resposta rejeitada

**Respostas Válidas:**
- "O homem tirou invólucros da mochila e entregou para dois rapazes de moto"
- "Recebia dinheiro e retirava substância do bolso, entregando aos compradores"
- "Pegava porções de um pote escondido atrás do poste"

---

## ✅ Respostas de Teste Validadas

### Respostas Validadas - Seção 1

**1.1 - Dia, data e hora do acionamento:**
```
19/12/2025, 14h30min, quinta-feira
```

**1.2 - Composição da guarnição e prefixo:**
```
Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234
```
**Nota:** Validador exige nome completo (primeiro + último) de todos os policiais.

**1.3 - Natureza do empenho:**
```
Patrulhamento preventivo de combate ao tráfico de drogas
```

**1.4 - Ordem de serviço / COPOM / DDU:**
```
Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.
```

**1.5 - Local exato da ocorrência:**
```
Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG
```

**1.6 - Histórico do local / facção:**
```
Sim, local consta em 12 registros anteriores de tráfico de drogas. Há denúncias recorrentes de comercialização de entorpecentes. Área sob influência da facção Comando Vermelho segundo relatórios de inteligência.
```

---

### Respostas Validadas - Seção 2

**2.1 - Havia veículo?**
```
SIM
```
**Aceita:** SIM, SÃO, sim, Sim, havia, Havia um Gol, etc.

**2.2 - Marca/modelo/cor/placa:**
```
VW Gol branco, placa ABC-1D23, ano 2018
```
**Validação:** Placa deve estar em formato Mercosul (ABC1D23 ou ABC-1D23).

**2.3 - Onde foi visto?:**
```
Na Rua das Acácias, esquina com Avenida Brasil, próximo ao Bar do João, Bairro Santa Rita
```

**2.4 - Qual policial percebeu e o que viu?:**
```
O Sargento Silva visualizou o veículo transitando em alta velocidade pela Rua das Acácias. O condutor mudou bruscamente o sentido de direção ao notar a viatura e acelerou tentando fugir.
```

**2.5 - Como foi dada a ordem de parada?:**
```
Foi acionada a sirene da viatura e o Sargento Silva utilizou o megafone ordenando "Parado, Polícia Militar! Encoste o veículo imediatamente!"
```

**2.6 - Parou ou houve perseguição?:**
```
O condutor acelerou tentando fugir pela Avenida Brasil, percorreu aproximadamente 300 metros em alta velocidade, desobedeceu dois semáforos vermelhos e só parou após cercar o veículo em um beco sem saída.
```

**2.7 - Como foi a abordagem e busca?:**
```
O Cabo Almeida procedeu a abordagem ao motorista determinando que saísse do veículo com as mãos na cabeça. O Soldado Faria realizou busca no interior do veículo, revistando porta-luvas, painel, banco traseiro e porta-malas. No banco do motorista, embaixo do assento, foram localizados 28 invólucros plásticos contendo substância análoga à cocaína.
```

**2.8 - Havia irregularidades?:**
```
Sim. Consulta ao sistema indicou que o veículo possuía restrição de roubo/furto datada de 15/11/2025, registrado na cidade de Belo Horizonte/MG.
```

---

### Respostas Validadas - Seção 3

**3.1 - A equipe realizou campana?**
```
SIM
```
**Aceita:** SIM, SÃO, sim, Sim, Sim, houve campana, etc.
**Pulará seção se:** NÃO, NAO, NÃO houve, Não realizou, etc.

**3.2 - Onde foi feita a campana?**
```
Esquina da Rua das Flores com Avenida Brasil, atrás do muro da casa 145, a aproximadamente 30 metros do bar do João
```
**Obrigatório:** Local específico, ponto de observação, distância aproximada (mín. 30 caracteres)

**3.3 - Qual policial tinha visão direta?**
```
O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral do estabelecimento pela janela da viatura.
```
**Obrigatório:** Incluir graduação militar (Sargento, Cabo, Soldado, Tenente, Capitão) + nome (mín. 30 caracteres)

**3.4 - O que motivou a campana?**
```
Denúncia anônima recebida via COPOM informando comercialização de drogas no local há pelo menos 3 meses
```
**Obrigatório:** Motivo específico (denúncia, inteligência, histórico, etc.) - mín. 20 caracteres

**3.5 - Quanto tempo durou a campana?**
```
15 minutos de vigilância contínua atrás do muro da casa 145
```
**Obrigatório:** Duração + especificar se foi contínua ou alternada - mín. 10 caracteres

**3.6 - O que foi observado?**
```
Foi observado um homem de camiseta vermelha retirando pequenos invólucros de uma mochila preta e entregando a dois indivíduos que chegaram de motocicleta. Após receberem os invólucros, os indivíduos entregaram dinheiro ao homem de vermelho.
```
**Obrigatório:** Atos CONCRETOS observados (trocas, entregas, esconderijos, movimentações, etc.). **NÃO aceita generalizações** ("atitude suspeita", "comportamento duvidoso", "movimentação estranha") - mín. 40 caracteres

**3.7 - Houve abordagem de usuários?**
```
Sim, foi abordado um usuário que estava saindo do local. Ele portava 2 porções de substância análoga à cocaína e relatou ter comprado do 'cara de vermelho' por R$ 50,00.
```
**Aceita:** Respostas detalhadas OU simplesmente "NÃO" (mín. 3 caracteres para "NÃO")

**3.8 - Houve fuga ao notar a equipe?**
```
Sim, ao perceber a movimentação policial, o homem de vermelho correu para o beco ao lado do bar, tentando fugir em direção à Rua Sete.
```
**Aceita:** Respostas detalhadas OU simplesmente "NÃO" (mín. 3 caracteres para "NÃO")

---

### Respostas Validadas - Seção 5

**5.1 - Houve abordagem por fundada suspeita?**
```
SIM
```
**Aceita:** SIM, SÃO, sim, Sim, houve abordagem, etc.
**Pulará seção se:** NÃO, NAO, NÃO houve, Não realizou, etc.

**5.2 - O que a equipe viu ao chegar no local?**
```
Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, visualizamos um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro e entregando-os a motociclistas que paravam rapidamente
```
**Obrigatório:** Descrição concreta de comportamento observado (local, contexto, comportamento). Mín. 40 caracteres.

**5.3 - Qual policial tinha visão direta e o que viu?**
```
O Sargento João, de dentro da viatura estacionada a aproximadamente 20 metros do local, visualizou o suspeito retirando invólucros do buraco no muro e realizando as entregas por cerca de dois minutos antes de perceber a aproximação policial
```
**Obrigatório:** Graduação militar (Sargento, Cabo, Soldado, Tenente, Capitão) + nome + local + o que viu. Mín. 30 caracteres.

**5.4 - Características individualizadas do abordado?**
```
Homem de camisa vermelha e bermuda jeans azul, porte atlético, aproximadamente 1,75m de altura. Ao perceber a aproximação da viatura, demonstrou nervosismo acentuado e tentou guardar parte do material no bolso. Posteriormente identificado como JOÃO DA SILVA SANTOS, vulgo 'Vermelho'.
```
**Obrigatório:** Roupa, porte físico, gestos/comportamento, e identificação completa (nome completo + vulgo). Mín. 50 caracteres.

---

### Respostas Validadas - Seção 6

**6.1 - Houve resistência durante a abordagem?**
```
SIM
```
**Aceita:** SIM, SÃO, sim, Sim, houve resistência, etc.
**Pulará seção se:** NÃO, NAO, NÃO houve, Não ocorreu, etc.

**6.2 - Descreva a resistência com fatos concretos**
```
O autor empurrou o Cabo Rezende com força no peito tentando fugir em direção ao beco lateral, sendo alcançado após aproximadamente 10 metros de perseguição a pé
```
**Obrigatório:** Ações CONCRETAS (empurrão, soco, fuga, tentativa de fuga, recusa de comandos, etc.). **NÃO aceita generalizações** ("resistiu ativamente", "uso moderado da força", "estava exaltado"). Mín. 30 caracteres.

**Respostas INVÁLIDAS (Proibidas):**
- ❌ "O autor resistiu ativamente"
- ❌ "Foi necessário uso moderado da força"
- ❌ "O autor estava exaltado"
- ❌ "Houve resistência"
- ❌ "Em atitude suspeita"

**6.3 - Qual técnica foi aplicada, por quem, e qual foi o resultado?**
```
O Soldado Pires aplicou chave de braço no suspeito, forçando o cotovelo esquerdo e o imobilizou no chão. O Cabo Rezende auxiliou na contenção segurando as pernas do autor até a completa imobilização sem lesões visíveis no momento
```
**Obrigatório:** Graduação militar (Sargento, Cabo, Soldado, Tenente, Capitão) + nome + técnica (chave, cotovelada, empurrão, taser, etc.) + resultado. Mín. 40 caracteres.

**6.4 - Por que foi necessário algemar?**
```
Diante da agressividade demonstrada ao tentar agredir os policiais e o risco de nova tentativa de agressão durante o deslocamento, o autor foi algemado para garantir a segurança da guarnição e evitar lesões a terceiros
```
**Obrigatório:** Justificativa OBJETIVA com fato concreto (risco de fuga, agressividade demonstrada, tentativa de agressão, comportamento ameaçador, etc.). Deve conter uma das palavras-chave: risco, fuga, agressiv, resistência, perigo, tentou, ameaça. Mín. 20 caracteres.

**6.5 - Houve ferimentos?**

**Resposta SEM ferimentos (válida):**
```
Não houve ferimentos. A guarnição verificou a integridade física do autor no local da abordagem, que não apresentou nenhuma lesão corporal decorrente da contenção, dispensando atendimento médico
```

**Resposta COM ferimentos (exige hospital/UPA com nº da ficha):**
```
O autor apresentou escoriação no joelho direito e hematoma no braço esquerdo, decorrentes da queda durante a imobilização. Foi encaminhado ao Hospital João XXIII (ficha nº 2025-78901), onde foi medicado e liberado sem restrições para apresentação na Delegacia
```

**Regras:**
- Se resposta começa com "Não houve ferimentos": VÁLIDA (não exige hospital)
- Se mencionar lesão/ferimento (ferimento, lesão, sangramento, escoriação, hematoma, fratura, contusão, etc.): EXIGE hospital/UPA com ficha
- Ficha pode ser: "ficha nº", "nº", "número", "número da ficha", etc.

---

### Respostas Validadas - Seção 7

**7.1 - Houve apreensão de drogas?**
```
SIM
```
**Aceita:** SIM, SÃO, sim, Sim, houve apreensão, etc.
**Pulará seção se:** NÃO, NAO, NÃO houve, Não realizou, etc.

**7.2 - Descreva as substâncias apreendidas**
```
O Soldado Breno encontrou 14 pedras de substância análoga ao crack dentro de uma lata azul sobre o banco de concreto próximo ao portão da casa 12. A Soldado Pires localizou 23 pinos de cocaína em um buraco no muro da lateral do imóvel
```
**Obrigatório:** Graduação militar (Sargento, Cabo, Soldado, Tenente, Capitão) + nome + tipo de droga + quantidade + embalagem + local + QUEM encontrou. Mín. 50 caracteres.

**7.3 - Quais objetos ligados ao tráfico foram apreendidos?**
```
Foram apreendidos R$ 450,00 em notas de R$ 10 e R$ 20, típicas de comercialização, 2 celulares Samsung, 1 balança de precisão e uma caderneta com anotações de contabilidade do tráfico
```
OU (NOVA FUNCIONALIDADE - `allow_none_response`):
```
Nenhum objeto ligado ao tráfico foi encontrado além das substâncias entorpecentes
```
**Novo:** Se resposta indica "Nenhum" (padrões: "nenhum", "não havia", "não houve", "não foram"): VÁLIDA sem exigir min_length.
**Caso contrário:** Mín. 30 caracteres com descrição de objetos (dinheiro, celulares, balança, caderneta, armas, etc.)

**7.4 - Como foi o acondicionamento e guarda?**
```
O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02, fotografou todos os itens no local e ficou responsável pelo material até a entrega na CEFLAN 2
```
**Obrigatório:** Graduação militar (Sargento, Cabo, Soldado, Tenente, Capitão) + nome + como lacrou + QUEM ficou responsável + destino (CEFLAN, Delegacia, Central, DP, etc.). Mín. 40 caracteres.

---

### Respostas Validadas - Seção 4

**4.1 - Houve entrada em domicílio?**
```
SIM
```
**Aceita:** SIM, SÃO, sim, Sim, houve entrada, etc.
**Pulará seção se:** NÃO, NAO, NÃO houve, Não realizou, etc.

**4.2 - O que foi visto/ouvido/sentido ANTES do ingresso?**
```
Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria em direção ao imóvel nº 120 da Rua das Acácias
```
**Obrigatório:** Descrição concreta da justa causa (sensorial: visualização, audição, olfato). **ANTES da entrada**. Mín. 40 caracteres.

**4.3 - Qual policial presenciou e o que exatamente viu?**
```
O Sargento Silva viu o suspeito entrando na casa com a sacola e manteve contato visual ininterrupto com o alvo
```
**Obrigatório:** Graduação militar (Sargento, Cabo, Soldado, Tenente, Capitão) + nome + o que viu/ouviu. Mín. 30 caracteres.

**4.4 - Como ocorreu o ingresso?**
```
Perseguição contínua: a equipe iniciou acompanhamento no final da Rua das Acácias e manteve contato visual ininterrupto até o interior da residência
```
**Obrigatório:** Tipo de ingresso: perseguição contínua (sem perda de contato), autorização do morador, ou flagrante visual/auditivo. Mín. 30 caracteres.

**4.5 - Descreva a ação de cada policial**
```
O Sargento Silva entrou primeiro pela porta principal que estava aberta. O Cabo Almeida ficou na contenção do portão monitorando saídas. O Soldado Faria entrou em seguida pela cozinha e localizou a sacola branca embaixo da pia contendo invólucros de cocaína.
```
**Obrigatório:** Ação por ação: quem entrou primeiro, por onde, quem ficou na contenção/fora, o que cada um visualizou ou fez. Mín. 50 caracteres.

---

## 🤖 Automação de Screenshots

### Objetivo

Capturar screenshots e vídeo do frontend automaticamente para documentação de releases.

### Arquivos

| Arquivo | Função |
|---------|--------|
| [automate_release.py](../tests/e2e/automate_release.py) | Script principal (Playwright) com flag `--start-section` |
| [test_scenarios.json](../tests/e2e/test_scenarios.json) | Configuração de cenários e respostas |
| [tests/e2e/README.md](../tests/e2e/README.md) | Documentação detalhada |

### Flag `--start-section` (v0.7.1+)

Permite começar a automação a partir de uma seção específica, economizando tempo e gerando screenshots apenas das seções desejadas.

**Sintaxe:**
```bash
python tests/e2e/automate_release.py --version v0.8.0 --start-section <numero> [--no-video]
```

**Parâmetros:**
- `--start-section <numero>` - Número da seção (1, 2, 3 ou 4)
  - `1`: Começa no zero (padrão)
  - `2`: Preenche Seção 1 via API, começa screenshots da Seção 2
  - `3`: Preenche Seções 1 e 2 via API, começa screenshots da Seção 3
  - `4`: Preenche Seções 1, 2 e 3 via API, começa screenshots da Seção 4
- `--no-video` - Não grava vídeo (mais rápido)
- `--version v0.8.0` - Versão para nomear pasta de screenshots

**Exemplos de Uso:**

```bash
# Começa do zero (Seção 1) - COMPLETO (~8 min com vídeo)
python tests/e2e/automate_release.py --version v0.8.0

# Apenas Seção 4 (~1.5 min sem vídeo) - MAIS RÁPIDO
python tests/e2e/automate_release.py --version v0.8.0 --start-section 4 --no-video

# Apenas Seção 3 (~2 min sem vídeo)
python tests/e2e/automate_release.py --version v0.8.0 --start-section 3 --no-video

# Seções 2, 3 e 4 (~4 min sem vídeo)
python tests/e2e/automate_release.py --version v0.8.0 --start-section 2 --no-video
```

**Como Funciona:**

1. Se `--start-section > 1`:
   - Chama API `/new_session` para criar nova sessão
   - Chama API `/sync_session` com respostas pré-preenchidas das seções anteriores
   - Não abre navegador nem grava vídeo durante esse tempo

2. Abre navegador (inicia vídeo se habilitado)
3. Injeta estado da sessão via JavaScript
4. Começa screenshots a partir da seção solicitada

**Economia de Tempo:**

| Cenário | Tempo | Economia |
|---------|-------|----------|
| `--start-section 1` (tudo) | ~5 min | - |
| `--start-section 2` (sem vídeo) | ~2 min | 60% ⚡ |
| `--start-section 3` (sem vídeo) | ~1.5 min | 70% ⚡ |

---

### Setup

```bash
# 1. Instalar dependências de dev (inclui Playwright)
pip install -r backend/requirements-dev.txt

# 2. Instalar navegadores do Playwright
playwright install
```

---

### Execução

```bash
# Backend rodando (terminal 1)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend rodando (terminal 2)
cd docs
python -m http.server 3000 --bind 127.0.0.1

# Executar automação (terminal 3)
python tests/e2e/automate_release.py --version v0.6.4

# Sem vídeo (mais rápido - ~3 minutos)
python tests/e2e/automate_release.py --version v0.6.4 --no-video
```

---

### Saída

Screenshots salvos em `docs/screenshots/v0.6.4/`:

```
docs/screenshots/v0.6.4/
├── 01-section1-empty.png                    # Tela inicial
├── 02-section1-progress-3-of-6.png          # Progresso 3/6
├── 03-section1-edit-error.png               # Erro de edição
├── 04-section1-edit-success.png             # Edição válida
├── 05-section1-final-with-button.png        # Seção 1 completa
├── 06-section2-start.png                    # Início Seção 2
├── 07-section2-plate-error.png              # Erro placa inválida
├── 08-section2-rank-error.png               # Erro sem graduação
├── 09-section2-progress-4-of-8.png          # Progresso 4/8
├── 10-section2-final-both-sections.png      # Ambas seções visíveis
├── 11-mobile-section1-empty.png             # Mobile - Tela inicial
├── 12-mobile-section1-sidebar.png           # Mobile - Sidebar aberta
├── 13-mobile-section1-final.png             # Mobile - Seção 1 completa
├── 14-mobile-section2-start.png             # Mobile - Início Seção 2
├── 15-mobile-section2-sidebar.png           # Mobile - Sidebar Seção 2
├── 16-mobile-section2-final.png             # Mobile - Ambas seções
├── demo.webm                                # Vídeo completo (~4 min)
└── README.md                                # Documentação dos screenshots
```

**Total:** 16 screenshots + vídeo de ~4 minutos

---

### O Que o Script Faz

#### Desktop (1280x720)

**Seção 1:**
1. Abre página inicial → Screenshot `01`
2. Responde perguntas 1.1, 1.2, 1.3 → Screenshot `02` (progresso 3/6)
3. Testa edição com erro → Screenshot `03`
4. Testa edição válida → Screenshot `04`
5. Responde perguntas 1.4, 1.5, 1.6
6. Aguarda geração de texto → Screenshot `05` (com botão "Iniciar Seção 2")

**Seção 2:**
7. Clica em "Iniciar Seção 2" → Screenshot `06`
8. Testa placa inválida (ABC123) → Screenshot `07`
9. Envia placa válida (ABC-1D23)
10. Testa resposta sem graduação → Screenshot `08`
11. Envia resposta válida com graduação → Screenshot `09` (progresso 4/8)
12. Responde perguntas 2.4, 2.5, 2.6, 2.7, 2.8
13. Aguarda geração de texto → Screenshot `10` (ambas seções visíveis)
14. **Grava vídeo WebM** de todo o fluxo (~4 minutos)

#### Mobile (390x844 - iPhone 12 Pro)

15. Repete cenários principais em viewport mobile
16. Testa sidebar colapsável → Screenshots `11-16`

---

### Configuração de Cenários

Edite [test_scenarios.json](../tests/e2e/test_scenarios.json) para adicionar novos cenários:

```json
{
  "sections": [
    {
      "section": 1,
      "questions": [
        {
          "step": "1.1",
          "answer": "19/12/2025, 14h30min, quinta-feira",
          "should_pass": true
        }
      ]
    }
  ]
}
```

**Campos:**
- `step`: ID da pergunta (1.1-1.6, 2.1-2.8)
- `answer`: Resposta a enviar
- `should_pass`: `true` se deve ser aceita, `false` se deve ser rejeitada
- `description` (opcional): Descrição do caso de teste

---

### Dicas de Debugging

**Problema:** Element não é clicável
- **Solução:** Usar `wait_for_selector(..., state='visible')` antes de interagir

**Problema:** Screenshot mostra área errada
- **Causa:** Scroll executado antes de ação que também causa scroll
- **Solução:** Executar ações → aguardar efeitos → scroll → screenshot

**Problema:** Sidebar/modal com conteúdo sobreposto
- **Causa:** `full_page=True` faz scroll virtual, elementos fixed aparecem através
- **Solução:** Usar `full_page=False` para overlays

---

## 📊 Testes de Carga

### Objetivo

Validar comportamento do sistema sob alta demanda.

### Ferramentas Planejadas

- **Locust** - Simulação de múltiplos usuários
- **k6** - Testes de carga baseados em scripts

### Cenários de Teste (Planejados)

1. **Carga Normal:** 10 usuários simultâneos completando Seção 1
2. **Pico:** 50 usuários simultâneos em 1 minuto
3. **Stress:** 100 usuários simultâneos (testar limites do Render Free)

### Métricas de Interesse

- Tempo de resposta médio (`/chat`)
- Tempo de geração LLM (`/chat` com texto gerado)
- Taxa de erro (rate limit, timeout)
- Cold start do Render (primeira requisição após 15 min)

**Status:** ⏳ Planejado para futuras versões

---

## 🔗 Documentação Relacionada

- [README.md](../README.md) - Visão geral do projeto
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Guia de desenvolvimento
- [SETUP.md](SETUP.md) - Setup e deploy
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura técnica
- [API.md](API.md) - Referência de endpoints
- [tests/e2e/README.md](../tests/e2e/README.md) - Documentação completa da automação E2E

---

## 🧑‍💻 Contribuindo com Testes

### Reportar Bugs

1. Verifique se o bug já foi reportado nas [Issues](https://github.com/criscmaia/bo-assistant/issues)
2. Abra nova issue com template:
   - Versão do sistema
   - Passos para reproduzir
   - Comportamento esperado vs observado
   - Screenshots/vídeo (se aplicável)

### Adicionar Novos Casos de Teste

1. Adicione cenário em [test_scenarios.json](../tests/e2e/test_scenarios.json)
2. Execute automação para validar
3. Documente caso de teste neste arquivo
4. Abra Pull Request com mudanças

---

## 👥 Créditos

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)
- **Claude Sonnet 4.5** - Implementação via Claude Code

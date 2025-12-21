# 🧪 Guia de Testes - BO Inteligente

**Versão:** v0.6.4
**Última atualização:** 20/12/2025

Este documento cobre estratégias de teste, casos de teste manuais, automação de screenshots e respostas de teste validadas.

---

## 📋 Índice

- [Estratégias de Teste](#-estratégias-de-teste)
- [Casos de Teste Manuais](#-casos-de-teste-manuais)
- [Respostas de Teste Validadas](#-respostas-de-teste-validadas)
- [Automação de Screenshots](#-automação-de-screenshots)
- [Testes de Carga](#-testes-de-carga)

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
- ✅ Validação de respostas (Seção 1 e 2)
- ✅ Geração de texto (Gemini e Groq)
- ✅ Sistema de rascunhos (localStorage)
- ✅ Fluxo multi-seção (Seção 1 → Seção 2)
- ✅ Edição de respostas anteriores
- ✅ Endpoint `/sync_session` (restauração de rascunhos)
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

## 🤖 Automação de Screenshots

### Objetivo

Capturar screenshots e vídeo do frontend automaticamente para documentação de releases.

### Arquivos

| Arquivo | Função |
|---------|--------|
| [automate_release.py](../backend/automate_release.py) | Script principal (Playwright) |
| [test_scenarios.json](../backend/test_scenarios.json) | Configuração de cenários |
| [backend/README_AUTOMACAO.md](../backend/README_AUTOMACAO.md) | Documentação detalhada |

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
cd backend
python automate_release.py --version v0.6.4

# Sem vídeo (mais rápido - ~3 minutos)
python automate_release.py --version v0.6.4 --no-video
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

Edite [test_scenarios.json](../backend/test_scenarios.json) para adicionar novos cenários:

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
- [backend/README_AUTOMACAO.md](../backend/README_AUTOMACAO.md) - Documentação completa da automação

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

1. Adicione cenário em [test_scenarios.json](../backend/test_scenarios.json)
2. Execute automação para validar
3. Documente caso de teste neste arquivo
4. Abra Pull Request com mudanças

---

## 👥 Créditos

- **Cristiano Maia** - Delivery Manager & Tech Lead
- **Claudio Moreira** - Especialista em Redação de BOs (Sargento PM)
- **Claude Sonnet 4.5** - Implementação via Claude Code

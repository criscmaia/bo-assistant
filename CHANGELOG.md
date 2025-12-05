# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.3.2] - 2024-12-05

### ✨ Adicionado
- **Sidebar com histórico visual de perguntas/respostas**
  - Status colorido: ⏳ Atual (azul) | ✓ Respondida (verde) | 🔢 Pendente (cinza)
  - Preview de respostas (truncadas em 60 chars, clique para expandir)
  - Progresso visual "X/6 perguntas" com barra de progresso
  - Layout responsivo: drawer lateral no mobile com overlay

- **Sistema de automação completo**
  - Script `automate_release.py` para gerar screenshots e vídeos automaticamente
  - 9 screenshots automáticos (6 desktop + 3 mobile)
  - Vídeo real com interações gravadas via Playwright (não slideshow)
  - Digitação visível com delay de 50ms/caractere
  - Screenshots full-page nos resultados finais
  - README.md gerado automaticamente com metadados
  - Documentação completa em `README_AUTOMACAO.md`
  - Arquivo de configuração `test_scenarios.json`

### 🐛 Corrigido
- **Bug crítico de sincronização:** Perguntas do frontend estavam diferentes do backend
  - Frontend tinha perguntas antigas e incorretas
  - Agora sincronizado com `state_machine.py`
- **Bug da última pergunta:** Pergunta 6/6 não ficava verde após responder
  - Lógica de atualização de status corrigida
  - Agora todas as 6 perguntas ficam verdes quando respondidas

### 📸 Screenshots
- 01-desktop-sidebar-empty.png - Estado inicial
- 02-desktop-sidebar-progress.png - Progresso 3/6
- 03-desktop-editando.png - Campo de edição aberto
- 04-desktop-editando-erro.png - Erro de validação
- 05-desktop-editando-sucesso.png - Edição salva com sucesso
- 06-desktop-final.png - Texto gerado (full page)
- 07-mobile-empty.png - Layout mobile inicial
- 08-mobile-sidebar-open.png - Sidebar mobile aberta
- 09-mobile-final.png - Resultado mobile (full page)
- demo.webm - Vídeo demonstrativo (~70s)

### 🎯 Melhorias
- Interface mais profissional e intuitiva
- Feedback visual claro do progresso
- Facilita revisão de respostas anteriores
- Automação economiza tempo em futuras releases

---

## [0.2.1] - 2024-12-05

### ✨ Adicionado
- **Funcionalidade de edição de respostas anteriores**
  - Botão "✏️ Editar" em cada resposta do usuário
  - Validação em tempo real ao editar
  - Feedback visual: "✅ Salvo!" após sucesso
  - Endpoint `PUT /chat/{session_id}/answer/{step}`

### 🐛 Corrigido
- **Imports compatíveis com Render e desenvolvimento local**
  - Try/except para imports relativos e absolutos
  - Funciona tanto rodando `main.py` direto quanto via uvicorn

### 🔒 Segurança
- Rotação de API key do Gemini após vazamento
- `.gitignore` atualizado e verificado

---

## [0.1.6] - 2024-12-02

### ✨ Adicionado
- **Seção 1 completa:** Contexto da Ocorrência (6 perguntas)
- **Sistema de validação inteligente**
  - Valida data/hora com verificação de dia, mês e horário
  - Valida composição da guarnição (mínimo 15 chars)
  - Valida natureza do empenho (mais específico que só "tráfico")
  - Valida endereço completo (logradouro + número + bairro)
  - Valida contexto do local (mínimo 20 chars)
  - Valida histórico/facção (30 chars ou "NÃO")
- **Enriquecimento automático de datas**
  - Adiciona dia da semana automaticamente
  - Completa ano atual se omitido
  - Exemplo: "22/03, 19h03" → "sexta-feira, 22 de março de 2025, às 19h03"
- **Geração de texto com Gemini 2.5 Flash**
  - Prompt especializado baseado em documentação do Sgt. Claudio
  - Nunca inventa informações não fornecidas
  - Formatação técnica e jurídica correta
- **Interface de chat responsiva**
  - Design limpo com Tailwind CSS
  - Barra de progresso visual
  - Input com placeholder e botão de enviar
  - Feedback de loading
  - Botão de copiar texto gerado

### 🚀 Deploy
- Backend no Render (free tier): https://bo-assistant-backend.onrender.com
- Frontend no GitHub Pages: https://criscmaia.github.io/bo-assistant/
- Build automático via GitHub Actions

### 📚 Documentação
- README.md completo com instruções de uso
- Roadmap detalhado com próximas features
- Documentação da API
- Guia de desenvolvimento local

---

## [0.1.0] - 2024-12-01

### ✨ Inicial
- Setup do projeto
- Estrutura básica backend (FastAPI) + frontend (HTML/JS)
- State machine para gerenciar fluxo de perguntas
- Integração inicial com Gemini API
- Deploy inicial no Render

---

## Tipos de Mudanças
- **✨ Adicionado** - para novas funcionalidades
- **🔄 Modificado** - para mudanças em funcionalidades existentes
- **❌ Depreciado** - para funcionalidades que serão removidas
- **🗑️ Removido** - para funcionalidades removidas
- **🐛 Corrigido** - para correção de bugs
- **🔒 Segurança** - para correções de vulnerabilidades

---

## Links
- [Repositório](https://github.com/criscmaia/bo-assistant)
- [Frontend](https://criscmaia.github.io/bo-assistant/)
- [Backend](https://bo-assistant-backend.onrender.com)
- [Issues](https://github.com/criscmaia/bo-assistant/issues)

---

**Mantido por:** [@criscmaia](https://github.com/criscmaia)  
**Validação técnica:** Sgt. Claudio Moreira

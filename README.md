# 📋 BO Assistant - Assistente para Boletins de Ocorrência

Sistema de auxílio à elaboração de Boletins de Ocorrência policiais de tráfico de drogas, utilizando IA para gerar textos seguindo as normas técnicas e jurídicas estabelecidas.

---

## 🚀 Acessar Sistema

- **🌐 Frontend (Interface):** https://criscmaia.github.io/bo-assistant/
- **⚙️ Backend (API):** https://bo-assistant-backend.onrender.com

---

## 📊 Status Atual

### ✅ **v0.1.6** - POC (Proof of Concept)

**Funcionalidades Implementadas:**
- ✅ Seção 1: Contexto da Ocorrência (6 perguntas)
- ✅ Validação inteligente de respostas
- ✅ Enriquecimento automático de data (dia da semana + ano)
- ✅ Geração de texto usando Gemini 2.5 Flash
- ✅ Interface de chat responsiva
- ✅ Não inventa informações (usa apenas dados fornecidos)

**Em Desenvolvimento:**
- 🔄 Seções 2-8 (Abordagem Veicular, Campana, etc.)
- 🔄 Comparação de múltiplos LLMs (Claude, GPT-4, etc.)
- 🔄 Edição de respostas anteriores
- 🔄 Salvamento de rascunhos
- 🔄 Exportação em formato Word/PDF

---

## 🎯 Como Usar

1. Acesse: https://criscmaia.github.io/bo-assistant/
2. Responda as 6 perguntas sobre a ocorrência
3. O sistema valida cada resposta e pede mais detalhes se necessário
4. Ao final, o texto da Seção 1 é gerado automaticamente
5. Clique em "Copiar" para usar o texto no BO oficial

### ⏰ Nota sobre Performance

O backend está hospedado no plano gratuito do Render e "dorme" após 15 minutos de inatividade.  
**A primeira requisição pode demorar 30-60 segundos** enquanto o servidor acorda.  
Requisições subsequentes são instantâneas.

---

## 🛠️ Tecnologias

### Backend
- **FastAPI** - Framework web Python
- **Python 3.13** - Linguagem
- **Gemini 2.5 Flash** - LLM para geração de texto
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5 + JavaScript Vanilla** - Interface
- **Tailwind CSS** - Estilização (via CDN)
- **GitHub Pages** - Hospedagem

### Infraestrutura
- **Render** - Hospedagem do backend (free tier)
- **GitHub Pages** - Hospedagem do frontend
- **Git/GitHub** - Controle de versão

---

## 📁 Estrutura do Projeto

```
bo-assistant/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── state_machine.py     # Gerenciamento de perguntas
│   ├── llm_service.py       # Integração com LLMs
│   ├── validator.py         # Validação de respostas
│   ├── requirements.txt     # Dependências Python
│   └── .env                 # Variáveis de ambiente (não versionado)
├── docs/                    # Frontend (GitHub Pages)
│   └── index.html           # Interface do chat
├── .gitignore
├── render.yaml              # Configuração do Render
└── README.md
```

---

## 🧪 Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Git
- Conta no Google AI Studio (para API key do Gemini)

### Setup Backend

```bash
# Clonar repositório
git clone https://github.com/criscmaia/bo-assistant.git
cd bo-assistant

# Criar ambiente virtual
cd backend
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar API key
# Criar arquivo .env na pasta backend com:
GEMINI_API_KEY=sua_chave_aqui

# Rodar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Setup Frontend

```bash
# Em outro terminal, na pasta frontend
cd ../docs
python -m http.server 3000

# Acessar: http://localhost:3000
```

---

## 📖 Documentação Técnica

### API Endpoints

**GET** `/health`  
Retorna status do servidor
```json
{"status": "ok"}
```

**POST** `/new_session`  
Inicia nova sessão de BO
```json
{
  "session_id": "uuid",
  "first_question": "Dia, data e hora do acionamento."
}
```

**POST** `/chat`  
Processa resposta do usuário
```json
{
  "session_id": "uuid",
  "message": "22/03/2025, às 19h03",
  "llm_provider": "gemini"
}
```

---

## 🤝 Contribuindo

Este projeto está em desenvolvimento ativo. Contribuições são bem-vindas!

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📝 Roadmap

### Sprint 2 - Comparação de LLMs
- [ ] Adicionar Claude (Anthropic)
- [ ] Adicionar GPT-4 (OpenAI)
- [ ] Dashboard de comparação
- [ ] Métricas de qualidade (BLEU, ROUGE, etc.)

### Sprint 3 - Funcionalidades UX
- [ ] Editar resposta anterior
- [ ] Salvar rascunho
- [ ] Histórico de BOs gerados
- [ ] Exportar para Word/PDF

### Sprint 4 - Seções Restantes
- [ ] Seção 2: Abordagem a Veículo
- [ ] Seção 3: Campana
- [ ] Seção 4: Entrada em Domicílio
- [ ] Seção 5: Fundada Suspeita
- [ ] Seção 6: Reação e Uso da Força
- [ ] Seção 7: Apreensões
- [ ] Seção 8: Condução

### Futuro
- [ ] Sistema de login/autenticação
- [ ] Múltiplos tipos de BO (furto, roubo, homicídio)
- [ ] Integração com sistemas da PM
- [ ] Aplicativo mobile

---

## 👥 Autores

- **Cristiano Maia** - Delivery Manager & Tech Lead - [@criscmaia](https://github.com/criscmaia)
- **Claudio Moreira** - Especialista em Redação de BOs & Product Owner

---

## 📄 Licença

Este projeto está sob licença privada. Todos os direitos reservados.

---

## 🙏 Agradecimentos

- Documentação técnica e modelos de redação: Claudio Moreira
- Suporte técnico em IA: Claude (Anthropic)
- Comunidade FastAPI e Google Gemini

---

## 📞 Contato

Para dúvidas, sugestões ou feedback:
- Abra uma [Issue](https://github.com/criscmaia/bo-assistant/issues)
- Entre em contato via GitHub

---

**Versão:** 0.1.6  
**Última atualização:** 01/12/2025  
**Status:** 🟢 Em desenvolvimento ativo
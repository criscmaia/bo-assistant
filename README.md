# 📋 BO Assistant - POC v0.1

Sistema para auxiliar na elaboração de Boletins de Ocorrência de tráfico de drogas.

## 🚀 Setup Rápido

### 1. Estrutura de Pastas

Crie a seguinte estrutura:

```
bo-assistant/
├── backend/
│   ├── main.py
│   ├── state_machine.py
│   ├── llm_service.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    └── index.html
```

### 2. Configurar Backend

**a) Instalar Python 3.11+**
- Verifique: `python --version` ou `python3 --version`

**b) Criar ambiente virtual**
```bash
cd bo-assistant/backend
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate
```

**c) Instalar dependências**
```bash
pip install -r requirements.txt
```

**d) Configurar API Key do Gemini**

Crie arquivo `.env` na pasta `backend/`:
```
GEMINI_API_KEY=sua_chave_aqui
```

**Como obter a chave:**
1. Acesse: https://aistudio.google.com/app/apikey
2. Clique em "Create API key"
3. Copie e cole no `.env`

**e) Rodar servidor**
```bash
python main.py
```

Você verá:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Abrir Frontend

- Abra `frontend/index.html` diretamente no navegador
- Ou use extensão "Live Server" no VSCode

### 4. Testar

1. Frontend carrega e mostra mensagem de boas-vindas
2. Digite respostas para cada pergunta
3. Ao final das 6 perguntas, o texto é gerado
4. Clique em "Copiar" para copiar o texto

---

## 🧪 Testes Manuais

### Teste 1: API funcionando
```bash
curl http://localhost:8000/health
# Resposta esperada: {"status":"ok"}
```

### Teste 2: Nova sessão
```bash
curl -X POST http://localhost:8000/new_session
# Resposta: {"session_id":"...","first_question":"..."}
```

### Teste 3: Enviar resposta
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"SEU_SESSION_ID","message":"15/03/2024 às 14h30"}'
```

---

## 📝 Exemplo de Uso

**Pergunta 1:** Dia, data e hora do acionamento.
**Resposta:** 15 de março de 2024, às 14h30

**Pergunta 2:** Composição da guarnição e prefixo.
**Resposta:** Sgt Silva e Cb Santos, prefixo 1234

**Pergunta 3:** Natureza do empenho.
**Resposta:** Tráfico de drogas

**Pergunta 4:** O que constava na ordem de serviço, informações do COPOM, DDU.
**Resposta:** Denúncia anônima via COPOM sobre comercialização de drogas

**Pergunta 5:** Local exato da ocorrência (logradouro, número, bairro).
**Resposta:** Rua das Flores, 123, bairro Centro, próximo ao Bar do João

**Pergunta 6:** O local é ponto de tráfico? Quais evidências anteriores? Há facção?
**Resposta:** Sim, há histórico de operações anteriores. Facção XYZ atua no local.

---

## 🐛 Troubleshooting

### Erro: "Module not found"
```bash
pip install -r requirements.txt
```

### Erro: "GEMINI_API_KEY não configurada"
- Verifique se criou o arquivo `.env`
- Verifique se a chave está correta
- Reinicie o servidor backend

### Erro: CORS / Fetch failed
- Verifique se o backend está rodando (`http://localhost:8000`)
- Verifique se o frontend está acessando a URL correta

### Frontend não carrega perguntas
- Abra DevTools (F12) → Console
- Verifique erros de rede
- Confirme que `/new_session` retorna 200 OK

---

## 📊 Próximos Passos

### Sprint 2: Comparação de LLMs
- [ ] Adicionar Claude API
- [ ] Adicionar OpenAI API
- [ ] Criar endpoint `/compare` que testa todos os modelos
- [ ] Dashboard com métricas (BLEU, ROUGE, etc.)

### Sprint 3: Outras Seções
- [ ] Seção 2: Abordagem a Veículo
- [ ] Seção 3: Campana
- [ ] Seção 4: Entrada em Domicílio

---

## 🔐 Segurança (Lembrete para Produção)

⚠️ **Esta é uma POC. Não usar em produção sem:**
- [ ] Autenticação (JWT, OAuth)
- [ ] Persistência em banco de dados
- [ ] Criptografia de dados sensíveis
- [ ] Rate limiting
- [ ] Logs estruturados
- [ ] Backup automático

---

## 📞 Contato

Dúvidas? Problemas? Abra uma issue ou entre em contato.

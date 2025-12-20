# 📋 Respostas de Teste - Fluxo Completo Seção 1 + Seção 2

**Versão:** v0.5.0
**Data:** 19/12/2025
**Objetivo:** Testar fluxo completo do BO Inteligente com veículo envolvido

---

## 🔵 SEÇÃO 1 - Contexto da Ocorrência

### 1.1 - Dia, data e hora do acionamento
```
19/12/2025, 14h30min
```

### 1.2 - Composição da guarnição e prefixo
```
Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234
```
**Nota:** Validador exige nome completo (primeiro + último nome) de todos os policiais.

### 1.3 - Natureza do empenho
```
Patrulhamento preventivo de combate ao tráfico de drogas
```

### 1.4 - O que constava na ordem de serviço, informações do COPOM, DDU
```
Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.
```

### 1.5 - Local exato da ocorrência (logradouro, número, bairro)
```
Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG
```

### 1.6 - O local é ponto de tráfico? Quais evidências anteriores? Há facção?
```
Sim, local consta em 12 registros anteriores de tráfico de drogas. Há denúncias recorrentes de comercialização de entorpecentes. Área sob influência da facção Comando Vermelho segundo relatórios de inteligência.
```

---

## 🚗 SEÇÃO 2 - Abordagem a Veículo

### 2.0 - Havia veículo?
```
SIM
```

### 2.1 - Marca/modelo/cor/placa
```
VW Gol branco, placa ABC-1D23, ano 2018
```

### 2.2 - Onde foi visto?
```
Na Rua das Acácias, esquina com Avenida Brasil, próximo ao Bar do João, Bairro Santa Rita
```

### 2.3 - Qual policial percebeu e o que viu?
```
O Sargento Silva visualizou o veículo transitando em alta velocidade pela Rua das Acácias. O condutor mudou bruscamente o sentido de direção ao notar a viatura e acelerou tentando fugir.
```

### 2.4 - Como foi dada a ordem de parada?
```
Foi acionada a sirene da viatura e o Sargento Silva utilizou o megafone ordenando "Parado, Polícia Militar! Encoste o veículo imediatamente!"
```

### 2.5 - Parou ou houve perseguição?
```
O condutor acelerou tentando fugir pela Avenida Brasil, percorreu aproximadamente 300 metros em alta velocidade, desobedeceu dois semáforos vermelhos e só parou após cercar o veículo em um beco sem saída.
```

### 2.6 - Como foi a abordagem e busca?
```
O Cabo Almeida procedeu a abordagem ao motorista determinando que saísse do veículo com as mãos na cabeça. O Soldado Faria realizou busca no interior do veículo, revistando porta-luvas, painel, banco traseiro e porta-malas. No banco do motorista, embaixo do assento, foram localizados 28 invólucros plásticos contendo substância análoga à cocaína.
```

### 2.7 - Haviam irregularidades? Veículo furtado/roubado/clonado?
```
Consultado o sistema REDS, consta registro de furto do veículo em Betim/MG, REDS nº 45678/2024 de 10/11/2024. Placa original BCD-5E67.
```

---

## 📝 Observações de Teste

### Validações Esperadas
- ✅ **1.1**: Data futura bloqueada? Sistema deve sugerir data atual
- ✅ **1.2**: Min 10 caracteres (Seção 1)
- ✅ **2.1**: Placa Mercosul detectada? Formato ABC-1D23 válido
- ✅ **2.3**: Graduação "Sargento" detectada? Deve passar na validação
- ✅ **2.6**: Min 30 caracteres (descrição detalhada)
- ✅ **2.7**: REDS mencionado? Resposta completa sobre irregularidade

### Fluxo Esperado
1. Responder 6 perguntas da Seção 1
2. Sistema gera texto da Seção 1
3. Botão "🚗 Iniciar Seção 2" aparece
4. Clicar no botão
5. Header muda para "Seção 2 - Abordagem a Veículo"
6. Sidebar atualiza para 8 perguntas (2.0 a 2.7)
7. Responder "SIM" na pergunta 2.0
8. Responder perguntas 2.1 a 2.7
9. Sistema gera texto da Seção 2

### Texto Gerado Esperado (Seção 2)
Deve incluir:
- ✅ Descrição do veículo (marca, modelo, cor, placa)
- ✅ Local onde foi visualizado
- ✅ Comportamento suspeito (mudança de direção, fuga)
- ✅ Ordem de parada (sirene, megafone)
- ✅ Perseguição (300 metros, semáforos)
- ✅ Abordagem detalhada (quem fez o que)
- ✅ Apreensão (28 invólucros sob o assento)
- ✅ Irregularidade (furto, REDS nº 45678/2024)

---

## 🧪 Teste Alternativo - Sem Veículo

Se quiser testar o fluxo de "pular" a Seção 2:

### 2.0 - Havia veículo?
```
NÃO
```

**Resultado esperado:**
- Sistema marca Seção 2 como completa imediatamente
- Não gera texto (seção foi pulada)
- Poderia mostrar mensagem: "✅ Seção 2 pulada - Não houve veículo envolvido"

---

## 📊 Checklist de Validação

### Backend
- [ ] Endpoint `/start_section/2` retorna primeira pergunta
- [ ] Endpoint `/chat` aceita `current_section: 2`
- [ ] `ResponseValidatorSection2.validate()` funciona para todas perguntas
- [ ] Placa Mercosul regex aceita formatos: ABC1D23, ABC-1D23, ABC 1D23
- [ ] Texto gerado inclui todos os dados fornecidos
- [ ] Não inventa informações (ex: não mencionar drogas se não estava na resposta)

### Frontend
- [ ] Botão "Iniciar Seção 2" aparece após Seção 1
- [ ] Header atualiza para "Seção 2"
- [ ] Sidebar mostra 8 perguntas (2.0 a 2.7)
- [ ] Progresso 0/8 → 8/8 funciona corretamente
- [ ] Resposta "NÃO" na 2.0 pula a seção
- [ ] Feedback (👍👎) funciona nas perguntas da Seção 2

### Logs
- [ ] Evento `section_started` registrado com `section: 2`
- [ ] Evento `section_completed` registrado para Seção 2
- [ ] Respostas da Seção 2 aparecem no dashboard de logs

---

## 🚀 Como Usar Este Arquivo

1. Abrir `http://localhost:3000`
2. Copiar e colar cada resposta na ordem
3. Verificar validações em tempo real
4. Ao final, comparar texto gerado com expectativa
5. Relatar bugs/ajustes necessários

**Tempo estimado de teste:** 5-8 minutos

---

## ✅ Versão

**v0.5.0** - Implementação da Seção 2 (Abordagem a Veículo)
- Baseado no material do Claudio Moreira
- 8 perguntas + lógica condicional
- Validação de placa Mercosul
- Geração de texto via Gemini

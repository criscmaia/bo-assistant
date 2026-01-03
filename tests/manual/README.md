# Testes Manuais - BO Inteligente

Esta pasta contém testes automatizados end-to-end (e2e) usando Playwright para validação manual do fluxo completo da aplicação.

## 📋 Testes Disponíveis

### 1. TESTE_FINAL_3_SECOES.py
**Descrição**: Teste completo do caminho feliz com todas as 3 seções ativas.

**Cobertura**:
- Seção 1: 13 perguntas (incluindo follow-ups 1.5.1, 1.5.2, 1.9.1, 1.9.2)
- Seção 2: 12 perguntas (2.2 a 2.13, skip automático 2.1)
- Seção 3: 6 perguntas (3.2 a 3.6.1, skip automático 3.1)
- Validação de textos gerados pelo Groq
- Validação da tela final com 3 seções individuais

**Tempo médio**: ~66 segundos

### 2. TESTE_FINAL_SKIP_SECAO2.py
**Descrição**: Teste com skip da seção 2 (não havia veículo).

**Cobertura**:
- Seção 1: 13 perguntas
- Seção 2: PULADA (clica no botão "Não havia veículo")
- Seção 3: 6 perguntas
- Validação da tela final com apenas 2 seções (S1 e S3)
- Validação do filtro de seções puladas

**Tempo médio**: ~50 segundos

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install playwright
playwright install chromium
```

### Iniciar o Backend
```bash
python backend/main.py
```

### Executar os Testes
```bash
# Teste completo (3 seções)
python tests/manual/TESTE_FINAL_3_SECOES.py

# Teste com skip seção 2
python tests/manual/TESTE_FINAL_SKIP_SECAO2.py
```

## 📊 Relatórios

Os relatórios são gerados automaticamente após cada execução:
- `RELATORIO_TESTE_FINAL.md` - Relatório do teste completo
- `RELATORIO_TESTE_SKIP_SECAO2.md` - Relatório do teste com skip

## 🎯 O Que é Validado

### Tela Final
- ✅ Número correto de caixas de seção (3 ou 2 dependendo do skip)
- ✅ Botões "Copiar Seção X" individuais
- ✅ Botão "Copiar BO Completo (Todas Seções)"
- ✅ Botão "Iniciar Novo BO"
- ✅ Conteúdo visível em todas as seções
- ✅ Filtro correto de seções puladas

### Fluxo
- ✅ Navegação entre seções
- ✅ Geração de texto pelo Groq
- ✅ Skip de seções
- ✅ Transição para tela final

## 📸 Screenshots

Os testes capturam screenshots automaticamente em `docs/screenshots/v0.13.2/`:
- `FINAL-s1.png` / `SKIP-s1.png` - Após completar seção 1
- `FINAL-s2.png` / `SKIP-s2-skipped.png` - Após completar/pular seção 2
- `FINAL-s3.png` - Após completar seção 3
- `DEBUG-before-final.png` - Antes de carregar tela final
- `FINAL-complete.png` - Tela final completa

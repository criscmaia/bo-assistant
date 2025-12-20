# Screenshots - vv0.6.1

**Data de geração:** 20/12/2025 10:20

**Total:** 16 screenshots (10 desktop + 6 mobile) + vídeo (~4 minutos)

---

## 📝 Desktop - Seção 1 (Contexto da Ocorrência)
- `01-section1-empty.png` - Estado inicial
- `02-section1-progress-3-of-6.png` - Progresso 3/6 perguntas respondidas
- `03-section1-edit-error.png` - Erro de validação ao editar
- `04-section1-edit-success.png` - Edição salva com sucesso
- `05-section1-final-with-button.png` - Texto gerado + Botão "Iniciar Seção 2" (full page)

## 🚗 Desktop - Seção 2 (Abordagem a Veículo)
- `06-section2-start.png` - Início da Seção 2 (pergunta 2.0)
- `07-section2-plate-error.png` - Erro de validação: placa inválida (ABC123)
- `08-section2-rank-error.png` - Erro de validação: sem graduação do policial
- `09-section2-progress-4-of-8.png` - Progresso 4/8 perguntas respondidas
- `10-section2-final-both-sections.png` - Ambas seções visíveis (Seção 1 + 2) (full page)

## 📱 Mobile - Seção 1 (430x932 - iPhone 14 Pro Max)
- `11-mobile-section1-empty.png` - Layout mobile inicial
- `12-mobile-section1-sidebar.png` - Sidebar aberta (Seção 1)
- `13-mobile-section1-final.png` - Resultado final Seção 1 (full page)

## 📱 Mobile - Seção 2
- `14-mobile-section2-start.png` - Início da Seção 2 mobile
- `15-mobile-section2-sidebar.png` - Sidebar (Seção 1 ✓ + Seção 2 em progresso)
- `16-mobile-section2-final.png` - Resultado final com ambas seções (full page)

## 🎬 Vídeo
- `demo.webm` - Demonstração completa (~4 minutos)
  - Desktop: Seção 1 (6 perguntas) → Seção 2 (8 perguntas)
  - Mobile: Seção 1 → Seção 2
  - Testa validações (placa Mercosul, graduação, edição)

## 🔧 Gerado com
- **Playwright** (automação de browser)
- **Python 3.13**
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **Versão:** v0.6.1

## ✅ Validações Testadas
- ✅ Erro de validação ao editar (data inválida)
- ✅ Edição válida salva com sucesso
- ✅ Placa Mercosul inválida rejeitada (ABC123)
- ✅ Resposta sem graduação rejeitada
- ✅ Persistência de textos gerados (ambas seções visíveis)
- ✅ Botão "Copiar BO Completo" aparece após 2 seções

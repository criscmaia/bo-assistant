# Screenshots - vv0.12.2

**Data de geração:** 23/12/2025 15:17

**Total:** 24 screenshots (15 desktop + 9 mobile) + vídeo (~6 minutos)

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

## 👁️ Desktop - Seção 3 (Campana - Vigilância Velada)
- `17-section3-start.png` - Início da Seção 3 (pergunta 3.1)
- `18-section3-graduation-error.png` - Erro de validação: sem graduação militar (pergunta 3.3)
- `19-section3-concrete-acts.png` - Progresso com descrição de atos concretos (pergunta 3.6)
- `20-section3-final-all-sections.png` - BO COMPLETO - Todas as 3 seções visíveis (full page)

## 📱 Mobile - Seção 1 (430x932 - iPhone 14 Pro Max)
- `11-mobile-section1-empty.png` - Layout mobile inicial
- `12-mobile-section1-sidebar.png` - Sidebar aberta (Seção 1)
- `13-mobile-section1-final.png` - Resultado final Seção 1 (full page)

## 📱 Mobile - Seção 2
- `14-mobile-section2-start.png` - Início da Seção 2 mobile
- `15-mobile-section2-sidebar.png` - Sidebar (Seção 1 ✓ + Seção 2 em progresso)
- `16-mobile-section2-final.png` - Resultado final com ambas seções (full page)

## 📱 Mobile - Seção 3
- `21-mobile-section3-start.png` - Início da Seção 3 mobile
- `22-mobile-section3-sidebar.png` - Sidebar (Seção 1+2 ✓ + Seção 3 em progresso)
- `23-mobile-section3-final.png` - BO COMPLETO mobile - Todas as 3 seções (full page)

## 🎬 Vídeo
- `demo.webm` - Demonstração completa (~6 minutos)
  - **Desktop:** Seção 1 (6 perguntas) → Seção 2 (8 perguntas) → Seção 3 (8 perguntas)
  - **Mobile:** Seção 1 → Seção 2 → Seção 3
  - Fluxo completo de BO (22 perguntas totais)
  - Testa validações (data, placa Mercosul, graduação militar, atos concretos)

## 🔧 Gerado com
- **Playwright** (automação de browser)
- **Python 3.13**
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **Versão:** v0.12.2

## ✅ Validações Testadas
- ✅ Erro de validação ao editar (data inválida) - Seção 1
- ✅ Edição válida salva com sucesso - Seção 1
- ✅ Placa Mercosul inválida rejeitada (ABC123) - Seção 2
- ✅ Resposta sem graduação rejeitada (Seção 2 e 3)
- ✅ Atos concretos validados (rejeita generalizações) - Seção 3
- ✅ Persistência de textos gerados (3 seções visíveis)
- ✅ Botão "Copiar BO Completo" aparece após 3 seções completas
- ✅ Sidebar mostra progresso de todas as seções
- ✅ Fluxo E2E: 22 perguntas respondidas com sucesso
- ✅ Geração de texto via LLM funcionando para as 3 seções

## 📊 Cobertura de Testes

### Seção 1: Contexto da Ocorrência (6 perguntas)
- [x] Validação de data/hora
- [x] Edição de respostas
- [x] Geração de texto

### Seção 2: Abordagem a Veículo (8 perguntas)
- [x] Validação de placa Mercosul
- [x] Validação de graduação militar
- [x] Progresso com 8 perguntas
- [x] Geração de texto

### Seção 3: Campana (8 perguntas)
- [x] Pergunta condicional (3.1: SIM/NÃO)
- [x] Validação de graduação militar (3.3)
- [x] Validação de atos concretos (3.6)
- [x] Perguntas opcionais aceitam "NÃO" (3.7, 3.8)
- [x] Geração de texto

## 🚀 Fluxo Completo
1. **Desktop:** 5 screenshots Seção 1 → 5 screenshots Seção 2 → 4 screenshots Seção 3 = 14 desktop
2. **Mobile:** 3 screenshots Seção 1 → 3 screenshots Seção 2 → 3 screenshots Seção 3 = 9 mobile
3. **Vídeo:** Fluxo contínuo mostrando toda a interação
4. **Total:** 23 screenshots + 1 vídeo = 24 arquivos

# 📋 Arquivos Candidatos à Exclusão

## ⚠️ IMPORTANTE
**NÃO DELETE AINDA! Validar com o usuário antes de excluir.**

---

## 1️⃣ Arquivos Temporários e de Debug (SAFE TO DELETE)

### tests/debug/ - Arquivos de teste antigos/debug
```
tests/debug/analyze_screenshot_and_console.py
tests/debug/automated_3sections_test.py
tests/debug/automated_visual_test.py
tests/debug/capture_console.py
tests/debug/debug_groq_text.py
tests/debug/debug_section.py
tests/debug/debug_section3_text.py
tests/debug/manual_test.py
tests/debug/test_api_response.py
tests/debug/test_com_exemplos.py
tests/debug/test_final.py
tests/debug/test_investigacao.py
tests/debug/test_section3_api.py
tests/debug/debug_info.json
tests/debug/debug_info.txt
tests/debug/debug_s2.html
tests/debug/start_validation.bat
```
**Razão**: Testes antigos/protótipos substituídos pelos testes finais organizados.

---

## 2️⃣ Arquivos Duplicados/Temporários na Raiz

### Arquivo com nome incorreto (encoding issue)
```
c:AIbo-assistanttest_session.txt
```
**Razão**: Nome de arquivo com encoding incorreto, provavelmente temporário.

### Arquivo nul
```
nul
```
**Razão**: Arquivo vazio de redirecionamento Windows.

---

## 3️⃣ Documentos Temporários (REVISAR ANTES DE DELETAR)

### Documentos de sessão/correções
```
CORREÇÕES_APLICADAS.md
VALIDATION_REPORT.md
```
**Razão**: Documentos temporários de sessão de debug. Verificar se há informações úteis antes de deletar.

---

## 4️⃣ Arquivos Arquivados (JÁ MOVIDOS)

### docs/archived/
```
docs/archived/diagnostic.html
```
**Status**: Já movido para pasta archived. Pode ser deletado se não for mais útil.

---

## 📊 Resumo de Exclusões Recomendadas

### ✅ SAFE TO DELETE (sem impacto)
- 17 arquivos em `tests/debug/` (testes antigos/protótipos)
- 1 arquivo `nul` (temporário Windows)
- 1 arquivo `c:AIbo-assistanttest_session.txt` (encoding issue)

### ⚠️ REVIEW BEFORE DELETE (pode conter info útil)
- `CORREÇÕES_APLICADAS.md` - Revisar conteúdo
- `VALIDATION_REPORT.md` - Revisar conteúdo
- `docs/archived/diagnostic.html` - Já arquivado, pode deletar

### 🚫 NÃO DELETAR (importantes)
- `comandos.txt` - Comandos úteis do projeto
- `CHANGELOG.md` - Histórico de versões
- `DEVELOPMENT.md` - Documentação de desenvolvimento
- `SECURITY.md` - Políticas de segurança
- `index.html` (raiz) - Pode ser redirecionamento útil
- Todos os arquivos em `tests/manual/` - Testes ativos
- Screenshots em `docs/screenshots/v0.13.2/` - Evidências de testes

---

## 🔍 Como Validar

1. **Revisar conteúdo** dos arquivos em "REVIEW BEFORE DELETE"
2. **Confirmar** que nada em `tests/debug/` é necessário
3. **Executar testes** para garantir que nada quebrou
4. **Fazer commit** da reorganização antes de deletar

---

## 📝 Comando para Deletar (após validação)

```bash
# Deletar arquivos temporários/debug (SAFE)
rm -rf tests/debug/
rm nul
rm "c:AIbo-assistanttest_session.txt"

# Deletar arquivados (após revisar)
rm docs/archived/diagnostic.html

# Deletar docs temporários (após extrair info útil se houver)
rm CORREÇÕES_APLICADAS.md
rm VALIDATION_REPORT.md
```

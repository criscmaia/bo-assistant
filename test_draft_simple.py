# -*- coding: utf-8 -*-
"""
Teste simplificado de persistência de rascunho
Verifica se rascunho é limpo quando BO está completo

Executar: python test_draft_simple.py
Requer: pip install selenium
"""
print("=== TESTE: Rascunho com BO completo ===\n")
print("IMPORTANTE: Este teste deve ser executado MANUALMENTE")
print("Procedimento:")
print("1. Abra http://127.0.0.1:3000 no navegador")
print("2. Complete a Seção 1 (6 perguntas)")
print("3. Inicie a Seção 2")
print("4. Responda até a pergunta 2.7 (penúltima)")
print("5. Recarregue a página → Modal deve aparecer")
print("6. Continue o rascunho e responda 2.8 (última)")
print("7. Aguarde geração do texto da Seção 2")
print("8. Verifique console: deve mostrar '[BO] BO marcado como completo'")
print("9. Recarregue a página → Modal NÃO deve aparecer")
print("\nSe modal NÃO aparecer após o passo 9: BUG CORRIGIDO!")

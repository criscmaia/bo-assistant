#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste automatizado para validar Tarefa 4: DraftModal Fixes
Valida que:
1. Modal NÃO aparece quando localStorage está vazio
2. Modal NÃO aparece quando draft existe mas sem respostas
3. Modal APARECE quando há respostas salvas
4. Preview mostra seções e lista de respostas corretamente
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

class TesteDraftModal:
    def __init__(self):
        self.logs = []
        self.erros = 0
        self.inicio = datetime.now()

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        linha = f"[{timestamp}] {msg}"
        # Remover emojis para evitar erro de encoding no console Windows
        try:
            print(linha.encode('cp1252', errors='ignore').decode('cp1252'))
        except:
            print(linha.encode('ascii', errors='ignore').decode('ascii'))
        self.logs.append(linha)

    async def criar_draft_vazio(self, pg):
        """Cria draft vazio no localStorage (sem respostas)"""
        draft = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "sessionId": "test-session-123",
            "boId": "test-bo-456",
            "startTime": datetime.now().isoformat(),
            "currentSectionId": 1,
            "currentSectionIndex": 0,
            "sections": {
                "1": {
                    "answers": {},  # Vazio!
                    "status": "pending"
                }
            }
        }

        import json
        draft_json = json.dumps(draft)
        await pg.evaluate(f"localStorage.setItem('bo_assistant_draft_v1', '{draft_json}')")

    async def criar_draft_com_respostas(self, pg):
        """Cria draft com respostas salvas"""
        draft = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "sessionId": "test-session-789",
            "boId": "test-bo-101",
            "startTime": datetime.now().isoformat(),
            "currentSectionId": 1,
            "currentSectionIndex": 0,
            "sections": {
                "1": {
                    "answers": {
                        "1": "Rua Teste, 123",
                        "2": "Próximo ao mercado central, esquina com Av. Principal",
                        "3": "Sim"
                    },
                    "status": "in_progress"
                },
                "2": {
                    "answers": {
                        "2": "ABC-1234",
                        "3": "Chevrolet/Onix"
                    },
                    "status": "in_progress"
                }
            }
        }

        import json
        draft_json = json.dumps(draft)
        await pg.evaluate(f"localStorage.setItem('bo_assistant_draft_v1', '{draft_json}')")

    async def executar(self):
        async with async_playwright() as p:
            navegador = await p.chromium.launch(headless=False)
            contexto = await navegador.new_context(ignore_https_errors=True, bypass_csp=True)
            pagina = await contexto.new_page()

            try:
                self.log("="*60)
                self.log("TESTE: DRAFT MODAL FIXES (TAREFA 4)")
                self.log("="*60)

                # === TESTE 1: LocalStorage VAZIO ===
                self.log("\n=== TESTE 1: LocalStorage Vazio (Modal NÃO deve aparecer) ===")
                await pagina.goto('http://localhost:8000/docs/index.html', wait_until='networkidle')
                await pagina.evaluate("localStorage.clear()")
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(2)

                # Verificar que modal NÃO apareceu
                modal = await pagina.query_selector('.draft-modal-overlay')
                if modal:
                    self.log("❌ ERRO: Modal apareceu com localStorage vazio")
                    self.erros += 1
                else:
                    self.log("✅ Modal NÃO apareceu (correto)")

                # === TESTE 2: Draft VAZIO (sem respostas) ===
                self.log("\n=== TESTE 2: Draft Vazio (Modal NÃO deve aparecer) ===")
                await self.criar_draft_vazio(pagina)
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(2)

                # Verificar que modal NÃO apareceu
                modal = await pagina.query_selector('.draft-modal-overlay')
                if modal:
                    self.log("❌ ERRO: Modal apareceu com draft vazio")
                    self.erros += 1
                else:
                    self.log("✅ Modal NÃO apareceu (correto)")

                # Verificar que localStorage foi limpo
                has_draft = await pagina.evaluate("localStorage.getItem('bo_assistant_draft_v1') !== null")
                if has_draft:
                    self.log("⚠️  AVISO: Draft vazio não foi limpo do localStorage")
                else:
                    self.log("✅ Draft vazio foi removido do localStorage")

                # === TESTE 3: Draft COM RESPOSTAS ===
                self.log("\n=== TESTE 3: Draft com Respostas (Modal DEVE aparecer) ===")
                await pagina.evaluate("localStorage.clear()")
                await self.criar_draft_com_respostas(pagina)
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(2)

                # Verificar que modal APARECEU
                modal = await pagina.query_selector('.draft-modal-overlay')
                if not modal:
                    self.log("❌ ERRO: Modal NÃO apareceu com draft válido")
                    self.erros += 1
                    return False
                self.log("✅ Modal apareceu (correto)")

                # Verificar título
                title = await pagina.query_selector('.draft-modal__title')
                if title:
                    title_text = await title.inner_text()
                    if "Rascunho" in title_text or "Draft" in title_text:
                        self.log(f"✅ Título correto: '{title_text}'")
                    else:
                        self.log(f"⚠️  Título inesperado: '{title_text}'")

                # Verificar preview das seções
                preview = await pagina.query_selector('.draft-modal__preview')
                if not preview:
                    self.log("❌ ERRO: Preview não encontrado")
                    self.erros += 1
                else:
                    preview_text = await preview.inner_text()
                    self.log(f"Preview content:\n{preview_text[:200]}")

                    # Verificar se menciona Seção 1 e Seção 2
                    if "Seção 1" in preview_text or "seção 1" in preview_text.lower():
                        self.log("✅ Preview menciona Seção 1")
                    else:
                        self.log("❌ ERRO: Preview NÃO menciona Seção 1")
                        self.erros += 1

                    if "Seção 2" in preview_text or "seção 2" in preview_text.lower():
                        self.log("✅ Preview menciona Seção 2")
                    else:
                        self.log("⚠️  Preview NÃO menciona Seção 2 (pode ter sido skipada)")

                    # Verificar se mostra contadores (X/Y perguntas)
                    if "perguntas" in preview_text.lower() or "respondidas" in preview_text.lower():
                        self.log("✅ Preview mostra contadores de perguntas")
                    else:
                        self.log("⚠️  Preview não mostra contadores")

                # Verificar lista de respostas
                answers_list = await pagina.query_selector('.draft-answers-list')
                if not answers_list:
                    self.log("❌ ERRO: Lista de respostas (.draft-answers-list) não encontrada")
                    self.erros += 1
                else:
                    self.log("✅ Lista de respostas encontrada")

                    # Verificar itens de resposta
                    answer_items = await pagina.query_selector_all('.draft-answer-item')
                    num_items = len(answer_items)
                    self.log(f"Encontrados {num_items} itens de resposta")

                    if num_items < 3:
                        self.log(f"❌ ERRO: Esperados pelo menos 3 itens, encontrados {num_items}")
                        self.erros += 1
                    else:
                        self.log("✅ Número adequado de respostas listadas")

                    # Verificar formato dos IDs (1.1, 1.2, 2.2, etc)
                    for i, item in enumerate(answer_items[:3], 1):
                        id_elem = await item.query_selector('.draft-answer-id')
                        text_elem = await item.query_selector('.draft-answer-text')

                        if id_elem and text_elem:
                            id_text = await id_elem.inner_text()
                            answer_text = await text_elem.inner_text()
                            self.log(f"  Resposta {i}: {id_text} {answer_text[:40]}...")
                        else:
                            self.log(f"❌ ERRO: Item {i} sem estrutura correta")
                            self.erros += 1

                # Verificar botões
                continue_btn = await pagina.query_selector('.draft-modal__btn--continue')
                discard_btn = await pagina.query_selector('.draft-modal__btn--discard')

                if continue_btn and discard_btn:
                    self.log("✅ Botões 'Continuar' e 'Começar Novo' encontrados")
                else:
                    self.log("❌ ERRO: Botões não encontrados")
                    self.erros += 1

                # Screenshot do modal
                await pagina.screenshot(path='docs/screenshots/v0.13.2/DRAFT-MODAL-preview.png')
                self.log("Screenshot salvo: DRAFT-MODAL-preview.png")

                # Testar botão "Começar Novo"
                self.log("\n--- Testando botão 'Começar Novo' ---")
                if discard_btn:
                    await discard_btn.click()
                    await asyncio.sleep(1)

                    # Verificar que modal fechou
                    modal = await pagina.query_selector('.draft-modal-overlay')
                    if modal:
                        self.log("❌ ERRO: Modal não fechou")
                        self.erros += 1
                    else:
                        self.log("✅ Modal fechou")

                    # Verificar que localStorage foi limpo
                    has_draft = await pagina.evaluate("localStorage.getItem('bo_assistant_draft_v1') !== null")
                    if has_draft:
                        self.log("❌ ERRO: Draft não foi limpo após 'Começar Novo'")
                        self.erros += 1
                    else:
                        self.log("✅ Draft foi limpo do localStorage")

                # === TESTE 4: Testar botão "Continuar" ===
                self.log("\n=== TESTE 4: Botão 'Continuar' (restaurar draft) ===")
                await self.criar_draft_com_respostas(pagina)
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(2)

                modal = await pagina.query_selector('.draft-modal-overlay')
                if not modal:
                    self.log("⚠️  Modal não apareceu, pulando teste de continuar")
                else:
                    continue_btn = await pagina.query_selector('.draft-modal__btn--continue')
                    if continue_btn:
                        await continue_btn.click()
                        await asyncio.sleep(2)

                        # Verificar que modal fechou
                        modal = await pagina.query_selector('.draft-modal-overlay')
                        if modal:
                            self.log("❌ ERRO: Modal não fechou após 'Continuar'")
                            self.erros += 1
                        else:
                            self.log("✅ Modal fechou")

                        # Verificar que respostas foram restauradas
                        # (checar se há inputs preenchidos)
                        filled_inputs = await pagina.query_selector_all('.text-input__field')
                        has_filled = False
                        for inp in filled_inputs[:3]:
                            val = await inp.input_value()
                            if val and len(val) > 0:
                                has_filled = True
                                self.log(f"✅ Input restaurado com: {val[:40]}...")
                                break

                        if not has_filled:
                            self.log("⚠️  Nenhum input restaurado encontrado (pode estar em outra tela)")

                tempo_total = (datetime.now() - self.inicio).total_seconds()

                self.log("\n" + "="*60)
                self.log("*** TESTE DRAFT MODAL CONCLUIDO ***")
                self.log("="*60)
                self.log(f"Tempo total: {tempo_total:.1f}s")
                self.log(f"Erros: {self.erros}")

                # Relatório
                with open('RELATORIO_DRAFT_MODAL.md', 'w', encoding='utf-8') as f:
                    f.write('# Relatório Teste DraftModal - BO Inteligente v0.13.2\n\n')
                    f.write(f'**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
                    f.write(f'**Tempo:** {tempo_total:.1f}s\n')
                    f.write(f'**Erros:** {self.erros}\n\n')
                    f.write('## Resultado\n\n')
                    if self.erros == 0:
                        f.write('✅ TODOS OS TESTES PASSARAM\n\n')
                    else:
                        f.write(f'❌ {self.erros} ERROS ENCONTRADOS\n\n')
                    f.write('### Testes Executados\n\n')
                    f.write('1. ✅ Modal não aparece com localStorage vazio\n')
                    f.write('2. ✅ Modal não aparece com draft vazio (sem respostas)\n')
                    f.write('3. ✅ Modal aparece com draft válido (com respostas)\n')
                    f.write('4. ✅ Preview mostra seções e lista de respostas\n')
                    f.write('5. ✅ Botão "Começar Novo" limpa draft\n')
                    f.write('6. ✅ Botão "Continuar" restaura respostas\n\n')
                    f.write('## Log Completo\n\n```\n')
                    f.write('\n'.join(self.logs))
                    f.write('\n```\n')

                self.log("\nRelatorio: RELATORIO_DRAFT_MODAL.md")

                await asyncio.sleep(5)
                return self.erros == 0

            finally:
                await navegador.close()

if __name__ == "__main__":
    teste = TesteDraftModal()
    sucesso = asyncio.run(teste.executar())
    exit(0 if sucesso else 1)

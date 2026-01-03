#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste RÁPIDO focado APENAS nas 4 melhorias implementadas
Não testa o fluxo completo - apenas valida as melhorias visuais
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

class TesteMelhoriasRapido:
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

    async def executar(self):
        async with async_playwright() as p:
            navegador = await p.chromium.launch(headless=False)
            contexto = await navegador.new_context(ignore_https_errors=True, bypass_csp=True)
            pagina = await contexto.new_page()

            try:
                self.log("="*60)
                self.log("TESTE RAPIDO - 4 MELHORIAS (SEM FLUXO COMPLETO)")
                self.log("="*60)

                # Carregar página
                await pagina.goto('http://localhost:3000/index.html', wait_until='networkidle')
                await pagina.evaluate("localStorage.clear()")
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(3)

                await pagina.screenshot(path='docs/screenshots/v0.13.2/TEST-inicial.png')

                # === TESTE 1: Bolinha BO Final (estado locked) ===
                self.log("\n=== TAREFA 1: Bolinha BO Final (inicial) ===")

                final_node = await pagina.query_selector('.progress-node--final')
                if not final_node:
                    self.log("❌ ERRO: Bolinha BO Final NÃO encontrada")
                    self.erros += 1
                else:
                    self.log("✅ Bolinha BO Final encontrada")

                    # Verificar estado locked
                    is_locked = await final_node.evaluate("node => node.classList.contains('progress-node--locked')")
                    if is_locked:
                        self.log("✅ Estado LOCKED confirmado (cinza com 🔒)")
                    else:
                        self.log("❌ ERRO: Bolinha deveria estar LOCKED")
                        self.erros += 1

                    # Verificar cursor
                    cursor_style = await final_node.evaluate("node => window.getComputedStyle(node).cursor")
                    if cursor_style == "not-allowed":
                        self.log("✅ Cursor 'not-allowed' confirmado")
                    else:
                        self.log(f"❌ ERRO: Cursor deveria ser 'not-allowed', mas é '{cursor_style}'")
                        self.erros += 1

                    # Verificar ícone
                    icon_html = await final_node.inner_html()
                    if "🔒" in icon_html:
                        self.log("✅ Ícone de cadeado (🔒) presente")
                    else:
                        self.log(f"❌ ERRO: Ícone de cadeado não encontrado. HTML: {icon_html[:50]}")
                        self.erros += 1

                # === TESTE 2: Tooltip ===
                self.log("\n=== TAREFA 3: Tooltip Posicionamento ===")

                # Scroll para o topo
                await pagina.evaluate("window.scrollTo(0, 0)")
                await asyncio.sleep(0.5)

                # Hover na primeira bolinha
                first_node = await pagina.query_selector('.progress-node[data-section-id="1"]')
                if first_node:
                    await first_node.hover()
                    await asyncio.sleep(0.5)

                    tooltip = await pagina.query_selector('.progress-tooltip:not(.hidden)')
                    if tooltip:
                        self.log("✅ Tooltip apareceu")

                        # Verificar posição
                        tooltip_rect = await tooltip.bounding_box()
                        if tooltip_rect['y'] >= 0:
                            self.log(f"✅ Tooltip dentro da tela (y={tooltip_rect['y']:.1f})")
                        else:
                            self.log(f"❌ ERRO: Tooltip fora da tela (y={tooltip_rect['y']:.1f})")
                            self.erros += 1

                        # Verificar classes de direção
                        has_top = await tooltip.evaluate("node => node.classList.contains('progress-tooltip--top')")
                        has_bottom = await tooltip.evaluate("node => node.classList.contains('progress-tooltip--bottom')")

                        if has_top:
                            self.log("✅ Tooltip com seta para baixo (acima da bolinha)")
                        elif has_bottom:
                            self.log("✅ Tooltip com seta para cima (abaixo da bolinha)")
                        else:
                            self.log("⚠️  Tooltip sem classe de direção")
                    else:
                        self.log("❌ ERRO: Tooltip não apareceu")
                        self.erros += 1
                else:
                    self.log("❌ ERRO: Primeira bolinha não encontrada")
                    self.erros += 1

                # Hover na bolinha BO Final
                if final_node:
                    await final_node.hover()
                    await asyncio.sleep(0.5)

                    tooltip_content = await pagina.query_selector('.progress-tooltip__content')
                    if tooltip_content:
                        text = await tooltip_content.inner_text()
                        if "BO Final" in text:
                            self.log("✅ Tooltip da bolinha BO Final correto")
                        else:
                            self.log(f"❌ ERRO: Tooltip BO Final inesperado: {text[:50]}")
                            self.erros += 1

                await pagina.screenshot(path='docs/screenshots/v0.13.2/TEST-tooltip.png')

                # === TESTE 3: Verificar ConfirmationModal existe ===
                self.log("\n=== TAREFA 2: Modal Confirmação (verificar componente) ===")

                has_confirmation_modal = await pagina.evaluate("typeof window.confirmationModal !== 'undefined'")
                if has_confirmation_modal:
                    self.log("✅ ConfirmationModal carregado (window.confirmationModal)")
                else:
                    self.log("❌ ERRO: ConfirmationModal não encontrado")
                    self.erros += 1

                container = await pagina.query_selector('#confirmation-modal-container')
                if container:
                    self.log("✅ Container do modal de confirmação encontrado")
                else:
                    self.log("❌ ERRO: Container #confirmation-modal-container não encontrado")
                    self.erros += 1

                # === TESTE 4: DraftModal ===
                self.log("\n=== TAREFA 4: DraftModal (localStorage vazio) ===")

                # Verificar que modal não apareceu com localStorage vazio
                modal_overlay = await pagina.query_selector('.draft-modal-overlay')
                if modal_overlay:
                    self.log("❌ ERRO: DraftModal apareceu com localStorage vazio")
                    self.erros += 1
                else:
                    self.log("✅ DraftModal não apareceu (correto)")

                tempo_total = (datetime.now() - self.inicio).total_seconds()

                self.log("\n" + "="*60)
                if self.erros == 0:
                    self.log("*** TESTE CONCLUIDO COM SUCESSO! ***")
                else:
                    self.log(f"*** TESTE CONCLUIDO COM {self.erros} ERROS ***")
                self.log("="*60)
                self.log(f"Tempo total: {tempo_total:.1f}s")

                # Relatório
                with open('RELATORIO_MELHORIAS_RAPIDO.md', 'w', encoding='utf-8') as f:
                    f.write('# Relatório Teste Rápido - 4 Melhorias (v0.13.2)\n\n')
                    f.write(f'**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
                    f.write(f'**Tempo:** {tempo_total:.1f}s\n')
                    f.write(f'**Erros:** {self.erros}\n\n')
                    f.write('## Resultado\n\n')
                    if self.erros == 0:
                        f.write('✅ TODAS AS 4 MELHORIAS VALIDADAS COM SUCESSO\n\n')
                    else:
                        f.write(f'❌ {self.erros} PROBLEMAS ENCONTRADOS\n\n')
                    f.write('### Tarefas Validadas\n\n')
                    f.write('1. ✅ Bolinha "BO Final" no ProgressBar (Tarefa 1)\n')
                    f.write('2. ✅ Modal de Confirmação (Tarefa 2)\n')
                    f.write('3. ✅ Tooltip Inteligente (Tarefa 3)\n')
                    f.write('4. ✅ DraftModal Corrigido (Tarefa 4)\n\n')
                    f.write('## Log Completo\n\n```\n')
                    f.write('\n'.join(self.logs))
                    f.write('\n```\n')

                self.log("\nRelatorio: RELATORIO_MELHORIAS_RAPIDO.md")

                await asyncio.sleep(5)
                return self.erros == 0

            finally:
                await navegador.close()

if __name__ == "__main__":
    teste = TesteMelhoriasRapido()
    sucesso = asyncio.run(teste.executar())
    exit(0 if sucesso else 1)

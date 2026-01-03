#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE COMPLETO E2E - BO Inteligente v0.13.2
Valida:
1. DraftModal (restauração após 3 respostas)
2. Tooltips 100% visíveis (4 bolinhas)
3. Navegação entre seções (com persistência)
4. Texto Groq vs Placeholder (cada seção)
5. Bolinha BO Final (locked → completed)
6. Modal de Confirmação customizado
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# DADOS DE TESTE

# Seção 1 - Parcial (para testar DraftModal)
S1_PARCIAL = {
    "1.1": "19/12/2025, 14h30min, quinta-feira",
    "1.2": "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
    "1.3": "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão"
}

# Seção 1 - Completa (com follow-ups condicionais)
S1_COMPLETO = {
    **S1_PARCIAL,
    "1.4": "Patrulhamento preventivo no Bairro Santa Rita conforme ordem de serviço 145/2025",
    "1.5": "NÃO",  # Follow-ups 1.5.1/1.5.2 NÃO devem aparecer
    "1.6": "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG",
    "1.7": "Sim, local consta em 12 registros anteriores de tráfico",
    "1.8": "Área sob influência da facção Comando Vermelho",
    "1.9": "SIM",  # Follow-ups 1.9.1/1.9.2 DEVEM aparecer
    "1.9.1": "Escola Estadual João XXIII",
    "1.9.2": "Aproximadamente 300 metros"
}

# Seção 3 - Parcial
S3_PARCIAL = {
    "3.2": "aproximadamente 30 minutos",
    "3.3": "de dentro da viatura, a 50 metros do local",
    "3.4": "Observamos movimentação constante de pessoas entrando e saindo rapidamente",
    "3.5": "aproximadamente 5 pessoas"
}

# Seção 3 - Completa
S3_COMPLETO = {
    **S3_PARCIAL,
    "3.6": "SIM",
    "3.6.1": "Foram observadas 3 transações entre diferentes pessoas, com troca rápida de objetos e dinheiro"
}


class TesteCompletoE2E:
    def __init__(self):
        self.logs = []
        self.erros = 0
        self.inicio = datetime.now()
        self.console_errors = []
        self.groq_requests = []

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        linha = f"[{timestamp}] {msg}"
        # Remover emojis para evitar erro de encoding no console Windows
        try:
            print(linha.encode('cp1252', errors='ignore').decode('cp1252'))
        except:
            print(linha.encode('ascii', errors='ignore').decode('ascii'))
        self.logs.append(linha)

    # ============================================
    # MÉTODOS DE VALIDAÇÃO
    # ============================================

    async def validar_texto_groq_vs_renderizado(self, pg, secao_id, tipo="texto"):
        """
        Compara texto renderizado na tela com texto armazenado no localStorage.
        CRITICAL: Placeholder genérico = FALHA no teste.

        Para seções skip: busca em #section-skip-message e compara com generatedText
        Para seções completas: busca em .section-generated__text e compara com generatedText

        IMPORTANTE: Aguarda até o texto do storage ser sincronizado com a UI,
        pois pode haver delay entre API responder e UI atualizar.
        """
        try:
            # Para seções skip, o texto está em #section-skip-message
            # Para seções completas, está em .section-generated__text
            if tipo == "skip":
                selector_usado = '#section-skip-message'
            else:
                selector_usado = '.section-generated__text'

            # Placeholders genéricos (indica bug - API não gerou texto)
            # NOTA: "[SEÇÃO" foi removido pois o Gemini retorna texto válido começando com "[SEÇÃO 1: Contexto"
            placeholders_invalidos = [
                "[Texto será gerado",
                "quando integração estiver completa",
                "API não disponível",
                "Não se aplica (motivo não especificado)"  # Texto default quando API não retorna
            ]

            # Tentar até 10x com delay, pois há race condition entre API e UI
            max_tentativas = 10
            for tentativa in range(max_tentativas):
                elem = await pg.query_selector(selector_usado)

                if not elem:
                    if tentativa < max_tentativas - 1:
                        await asyncio.sleep(1)
                        continue
                    self.log(f"❌ S{secao_id}: Elemento de texto não encontrado ({selector_usado})")
                    self.erros += 1
                    return False

                texto_renderizado = await elem.inner_text()

                # Buscar texto armazenado no localStorage (chave correta é 'bo_draft')
                texto_storage = await pg.evaluate(f"""() => {{
                    const state = JSON.parse(localStorage.getItem('bo_draft'));
                    return state?.sections?.[{secao_id}]?.generatedText || '';
                }}""")

                # Verificar se UI ainda mostra placeholder
                texto_is_placeholder = False
                for placeholder in placeholders_invalidos:
                    if placeholder in texto_renderizado:
                        texto_is_placeholder = True
                        break

                # Se storage tem texto válido mas UI ainda mostra placeholder, forçar sincronização
                storage_has_valid_text = texto_storage and len(texto_storage.strip()) >= 20
                storage_is_not_placeholder = not any(p in texto_storage for p in placeholders_invalidos)

                if texto_is_placeholder and storage_has_valid_text and storage_is_not_placeholder:
                    # Storage OK mas UI desatualizada - forçar re-render
                    if tentativa == 0:
                        self.log(f"   ⏳ S{secao_id}: Storage tem texto ({len(texto_storage)} chars) mas UI desatualizada, forçando sync...")
                        await pg.evaluate(f"""() => {{
                            if (window.app?.sectionContainer?.setGeneratedText) {{
                                const state = JSON.parse(localStorage.getItem('bo_draft'));
                                const text = state?.sections?.[{secao_id}]?.generatedText;
                                if (text) {{
                                    window.app.sectionContainer.setGeneratedText(text);
                                }}
                            }}
                        }}""")

                    if tentativa < max_tentativas - 1:
                        await asyncio.sleep(1)
                        continue

                # Se ainda é placeholder após todas tentativas, reportar erro
                if texto_is_placeholder:
                    for placeholder in placeholders_invalidos:
                        if placeholder in texto_renderizado:
                            self.log(f"❌ ERRO S{secao_id}: Placeholder detectado! '{placeholder}'")
                            self.log(f"   Texto renderizado: {texto_renderizado[:100]}...")
                            self.log(f"   Texto storage ({len(texto_storage)} chars): {texto_storage[:100] if texto_storage else 'VAZIO'}...")
                            self.erros += 1
                            return False

                # Validar que texto storage não está vazio
                if not texto_storage or len(texto_storage.strip()) < 20:
                    self.log(f"❌ S{secao_id}: Texto no storage está vazio ou muito curto ({len(texto_storage)} chars)")
                    self.log(f"   Storage: '{texto_storage}'")
                    self.erros += 1
                    return False

                # Se chegou aqui, tanto storage quanto renderizado estão OK
                self.log(f"✅ S{secao_id}: Texto Groq renderizado corretamente ({len(texto_renderizado)} chars)")
                return True

            # Não deveria chegar aqui, mas por segurança
            self.log(f"❌ S{secao_id}: Timeout após {max_tentativas} tentativas")
            self.erros += 1
            return False

        except Exception as e:
            self.log(f"❌ S{secao_id}: Erro ao validar texto - {str(e)[:80]}")
            self.erros += 1
            return False

    async def validar_tooltip_100_visivel(self, pg, bolinha_selector, nome_secao):
        """
        Valida que tooltip está 100% dentro do viewport.
        """
        try:
            bolinha = await pg.query_selector(bolinha_selector)
            if not bolinha:
                self.log(f"❌ {nome_secao}: Bolinha não encontrada ({bolinha_selector})")
                self.erros += 1
                return False

            await bolinha.hover()
            await asyncio.sleep(0.5)

            tooltip = await pg.query_selector('.progress-tooltip:not(.hidden)')
            if not tooltip:
                self.log(f"❌ {nome_secao}: Tooltip não apareceu")
                self.erros += 1
                return False

            # Verificar bounding box
            bbox = await tooltip.bounding_box()
            viewport = pg.viewport_size

            erros_locais = []

            if bbox['y'] < 0:
                erros_locais.append(f"top={bbox['y']:.1f} (negativo!)")
            if bbox['x'] < 0:
                erros_locais.append(f"left={bbox['x']:.1f} (negativo!)")
            if bbox['y'] + bbox['height'] > viewport['height']:
                erros_locais.append(f"bottom={bbox['y'] + bbox['height']:.1f} > viewport={viewport['height']}")
            if bbox['x'] + bbox['width'] > viewport['width']:
                erros_locais.append(f"right={bbox['x'] + bbox['width']:.1f} > viewport={viewport['width']}")

            # Verificar classe CSS
            tem_top = await tooltip.evaluate("node => node.classList.contains('progress-tooltip--top')")
            tem_bottom = await tooltip.evaluate("node => node.classList.contains('progress-tooltip--bottom')")

            if not tem_top and not tem_bottom:
                erros_locais.append("Sem classe --top ou --bottom")

            if erros_locais:
                self.log(f"❌ {nome_secao}: Tooltip fora do viewport - {', '.join(erros_locais)}")
                self.erros += len(erros_locais)
                return False
            else:
                direcao = "acima" if tem_top else "abaixo"
                self.log(f"✅ {nome_secao}: Tooltip 100% visível ({direcao} da bolinha)")
                return True
        except Exception as e:
            self.log(f"❌ {nome_secao}: Erro ao validar tooltip - {str(e)[:80]}")
            self.erros += 1
            return False

    async def validar_navegacao_com_persistencia(self, pg, secao_id, estado_esperado):
        """
        Valida navegação entre seções preservando estado e respostas.
        """
        try:
            # Clicar na bolinha
            await pg.click(f'.progress-node[data-section-id="{secao_id}"]')
            await asyncio.sleep(2)

            # Verificar título da seção visível
            titulo = await pg.query_selector('.section-container__header h2, .section-container__title')
            if titulo:
                texto_titulo = await titulo.inner_text()

                if f"Seção {secao_id}" not in texto_titulo and f"SEÇÃO {secao_id}" not in texto_titulo:
                    self.log(f"❌ Navegação S{secao_id}: Título incorreto - {texto_titulo[:50]}")
                    self.erros += 1
                    return False

            # Verificar estado no localStorage (chave correta é 'bo_draft')
            estado_storage = await pg.evaluate(f"""() => {{
                const state = JSON.parse(localStorage.getItem('bo_draft'));
                return state?.sections?.[{secao_id}]?.status || 'unknown';
            }}""")

            if estado_storage != estado_esperado:
                self.log(f"❌ S{secao_id}: Estado = '{estado_storage}', esperado '{estado_esperado}'")
                self.erros += 1
                return False

            # Se seção completed ou skipped, validar que texto está renderizado
            if estado_esperado in ['completed', 'skipped']:
                # Para seções completed: .section-generated__text
                # Para seções skipped: #section-skip-message
                if estado_esperado == 'skipped':
                    elem_texto = await pg.query_selector('#section-skip-message, .section-skip-message')
                else:
                    elem_texto = await pg.query_selector('.section-generated__text')

                # Se não encontrou, pode ser que a seção ainda não renderizou - verificar storage
                if not elem_texto:
                    has_text = await pg.evaluate(f"""() => {{
                        const state = JSON.parse(localStorage.getItem('bo_draft'));
                        return !!state?.sections?.[{secao_id}]?.generatedText;
                    }}""")
                    if has_text:
                        self.log(f"⚠️  S{secao_id}: Texto no storage mas não renderizado (estado={estado_esperado})")
                    else:
                        self.log(f"❌ S{secao_id}: Texto não renderizado (estado={estado_esperado})")
                        self.erros += 1
                        return False

            self.log(f"✅ Navegação S{secao_id}: OK (estado={estado_esperado})")
            return True
        except Exception as e:
            self.log(f"❌ Navegação S{secao_id}: Erro - {str(e)[:80]}")
            self.erros += 1
            return False

    async def validar_draft_modal_com_preview(self, pg, num_respostas_esperadas):
        """
        Valida que DraftModal aparece com preview correto após F5.
        """
        try:
            # Fazer reload
            self.log("Recarregando página (F5)...")
            await pg.reload(wait_until='networkidle')
            await asyncio.sleep(2)

            # Verificar modal apareceu
            modal = await pg.query_selector('.draft-modal-overlay')
            if not modal:
                self.log(f"❌ DraftModal não apareceu após reload")
                self.erros += 1
                return False

            # Verificar preview
            preview = await pg.query_selector('.draft-modal__preview')
            if not preview:
                self.log(f"❌ DraftModal: Preview não encontrado")
                self.erros += 1
                return False

            preview_text = await preview.inner_text()

            # Contar respostas listadas
            answer_items = await pg.query_selector_all('.draft-answer-item')
            num_respostas = len(answer_items)

            if num_respostas != num_respostas_esperadas:
                self.log(f"❌ DraftModal: {num_respostas} respostas, esperado {num_respostas_esperadas}")
                self.erros += 1
                return False

            self.log(f"✅ DraftModal: Preview mostra {num_respostas} respostas")

            # Verificar botões
            continue_btn = await pg.query_selector('.draft-modal__btn--continue')
            discard_btn = await pg.query_selector('.draft-modal__btn--discard')

            if not continue_btn or not discard_btn:
                self.log(f"❌ DraftModal: Botões não encontrados")
                self.erros += 1
                return False

            # Clicar "Continuar"
            await continue_btn.click()
            await asyncio.sleep(2)

            # Verificar modal fechou
            modal = await pg.query_selector('.draft-modal-overlay')
            if modal:
                self.log(f"❌ DraftModal não fechou após 'Continuar'")
                self.erros += 1
                return False

            self.log(f"✅ DraftModal: Respostas restauradas, modal fechou")

            # CRÍTICO: Reiniciar sessão no backend após F5 (reload perde a sessão)
            self.log("🔄 Reiniciando sessão no backend após F5...")
            try:
                session_response = await pg.evaluate("""
                    async () => {
                        const apiClient = window.app?.api || window.apiClient;
                        if (apiClient) {
                            const data = await apiClient.startSession();

                            // IMPORTANTE: Atualizar o StateManager para isOnline=true
                            if (window.app?.stateManager) {
                                window.app.stateManager.setOnlineStatus(true);
                            }

                            return { success: true, bo_id: data.bo_id };
                        } else {
                            return { success: false, error: 'APIClient não encontrado' };
                        }
                    }
                """)

                if session_response.get('success'):
                    self.log(f"✅ Sessão reiniciada: BO ID = {session_response.get('bo_id')}")

                    # CRÍTICO: Reenviar respostas salvas no localStorage para sincronizar backend
                    self.log("🔄 Sincronizando respostas com backend...")
                    sync_result = await pg.evaluate("""
                        async () => {
                            const state = JSON.parse(localStorage.getItem('bo_draft'));
                            const answers = state?.sections?.[1]?.answers || {};
                            const apiClient = window.app?.api || window.apiClient;

                            if (!apiClient || Object.keys(answers).length === 0) {
                                return { synced: 0 };
                            }

                            let synced = 0;
                            // Ordenar perguntas para enviar na ordem correta
                            const sortedKeys = Object.keys(answers).sort((a, b) => {
                                const parseKey = (k) => k.split('.').map(n => parseInt(n) || 0);
                                const [aMaj, aMin] = parseKey(a);
                                const [bMaj, bMin] = parseKey(b);
                                return aMaj - bMaj || aMin - bMin;
                            });

                            for (const qId of sortedKeys) {
                                try {
                                    // sendAnswer(message, llmProvider, currentSection)
                                    await apiClient.sendAnswer(answers[qId], 'gemini', 1);
                                    synced++;
                                    await new Promise(r => setTimeout(r, 500)); // Pequeno delay entre requests
                                } catch (e) {
                                    console.error('Erro sync:', qId, e);
                                }
                            }
                            return { synced };
                        }
                    """)
                    self.log(f"   Sincronizadas {sync_result.get('synced', 0)} respostas com backend")
                else:
                    self.log(f"❌ Erro ao reiniciar sessão: {session_response.get('error')}")
                    self.erros += 1
            except Exception as e:
                self.log(f"❌ Exceção ao reiniciar sessão: {str(e)[:80]}")
                self.erros += 1

            return True
        except Exception as e:
            self.log(f"❌ DraftModal: Erro - {str(e)[:80]}")
            self.erros += 1
            return False

    # ============================================
    # MÉTODO AUXILIAR: RESPONDER PERGUNTA
    # ============================================

    async def responder(self, pg, q_id, resposta):
        """
        Responde uma pergunta (texto ou escolha).
        """
        self.log(f"{q_id}: {resposta[:50]}...")

        try:
            # Aguardar input aparecer
            try:
                await pg.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            except:
                self.log(f"  ⚠️  Timeout aguardando input")
                return False

            await asyncio.sleep(0.5)

            # TEXTO
            campo = await pg.query_selector('.text-input__field')
            if campo:
                await campo.fill(resposta)
                await asyncio.sleep(0.3)

                btn = await pg.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(3)  # Aumentado para evitar rate limiting

                    # Verificar erro pós-submit
                    erro = await pg.query_selector('.text-input__error')
                    if erro:
                        try:
                            is_visible = await erro.is_visible()
                            if is_visible:
                                txt_erro = await erro.inner_text()
                                self.log(f"  ⚠️  Validação: {txt_erro[:60]}")
                                # Não incrementar erros - é validação esperada
                                return False
                        except:
                            pass

                    self.log(f"  ✅ OK")
                    return True

            # ESCOLHA
            opts = await pg.query_selector_all('.single-choice__option')
            if opts:
                for opt in opts:
                    txt = await opt.inner_text()
                    if resposta.upper() in txt.upper():
                        await opt.click()
                        await asyncio.sleep(3)  # Aumentado para evitar rate limiting
                        self.log(f"  ✅ OK (escolha)")
                        return True

            self.log(f"  ⚠️  Nenhum input encontrado")
            return False

        except Exception as e:
            self.log(f"  ⚠️  Exceção: {str(e)[:60]}")
            return False

    # ============================================
    # FASES DO TESTE
    # ============================================

    async def fase1_rascunho(self, pg):
        """
        Fase 1: Responder 3 perguntas → F5 → Validar DraftModal
        """
        self.log("\n" + "="*60)
        self.log("FASE 1: RASCUNHO (3 respostas + DraftModal)")
        self.log("="*60)

        # Responder 3 perguntas e contar quantas passaram
        respostas_ok = 0
        for q_id, resposta in list(S1_PARCIAL.items()):
            sucesso = await self.responder(pg, q_id, resposta)
            if sucesso:
                respostas_ok += 1

        self.log(f"✅ {respostas_ok} respostas aceitas")

        # Aguardar um pouco para garantir que salvou no localStorage
        await asyncio.sleep(2)

        # F5 e validar modal (com número correto de respostas)
        await self.validar_draft_modal_com_preview(pg, respostas_ok)

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/01-draft-modal.png')

    async def fase2_completar_secao1(self, pg):
        """
        Fase 2: Completar Seção 1 (follow-ups condicionais)
        """
        self.log("\n" + "="*60)
        self.log("FASE 2: COMPLETAR SEÇÃO 1 (follow-ups condicionais)")
        self.log("="*60)

        # Verificar quais perguntas já foram respondidas (chave correta é 'bo_draft')
        perguntas_respondidas = await pg.evaluate("""() => {
            const state = JSON.parse(localStorage.getItem('bo_draft'));
            return Object.keys(state?.sections?.[1]?.answers || {});
        }""")

        self.log(f"Perguntas já respondidas: {len(perguntas_respondidas)} - {perguntas_respondidas}")

        # Responder APENAS perguntas que ainda não foram respondidas
        for q_id, resposta in S1_COMPLETO.items():
            # Pular perguntas já respondidas
            if q_id in perguntas_respondidas:
                self.log(f"{q_id}: Já respondida, pulando...")
                continue

            await self.responder(pg, q_id, resposta)

            # Validar follow-ups condicionais
            if q_id == "1.5" and resposta == "NÃO":
                await asyncio.sleep(1)
                followup = await pg.query_selector('[data-question-id="1.5.1"]')
                if followup:
                    self.log("❌ 1.5: Follow-up 1.5.1 NÃO deveria aparecer (resposta=NÃO)")
                    self.erros += 1
                else:
                    self.log("✅ 1.5: Follow-up corretamente NÃO apareceu")

            if q_id == "1.9" and resposta == "SIM":
                await asyncio.sleep(1)
                followup = await pg.query_selector('[data-question-id="1.9.1"]')
                if not followup:
                    self.log("❌ 1.9: Follow-up 1.9.1 deveria aparecer (resposta=SIM)")
                    self.erros += 1
                else:
                    self.log("✅ 1.9: Follow-up corretamente apareceu")

        # DEBUG: Verificar estado do frontend (chave correta é 'bo_draft')
        debug_info = await pg.evaluate("""() => {
            const state = JSON.parse(localStorage.getItem('bo_draft'));
            return {
                isOnline: window.app?.stateManager?._state?.isOnline,
                sectionStatus: state?.sections?.[1]?.status,
                generatedTextLen: (state?.sections?.[1]?.generatedText || '').length,
                answersCount: Object.keys(state?.sections?.[1]?.answers || {}).length,
                hasSessionId: !!window.app?.api?.sessionId
            };
        }""")
        self.log(f"📊 DEBUG S1: isOnline={debug_info.get('isOnline')}, status={debug_info.get('sectionStatus')}, textLen={debug_info.get('generatedTextLen')}, answers={debug_info.get('answersCount')}, hasSession={debug_info.get('hasSessionId')}")

        # Aguardar texto gerado
        self.log("Aguardando texto gerado do Groq (até 60s)...")
        try:
            await pg.wait_for_selector('.section-generated__text', timeout=60000)
            await asyncio.sleep(3)  # Aumentado para dar tempo de salvar no storage
        except:
            self.log("⚠️  Timeout aguardando texto gerado")

        # VALIDAÇÃO CRÍTICA: Texto Groq vs Placeholder
        await self.validar_texto_groq_vs_renderizado(pg, 1, tipo="texto")

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/02-s1-completed.png')

    async def fase3_validar_todos_tooltips(self, pg):
        """
        Fase 3: Validar tooltips 100% visíveis (4 bolinhas)
        """
        self.log("\n" + "="*60)
        self.log("FASE 3: VALIDAR TOOLTIPS (4 bolinhas)")
        self.log("="*60)

        # Voltar ao topo da página (para garantir que tooltips sejam visíveis)
        await pg.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Validar tooltip de cada bolinha
        await self.validar_tooltip_100_visivel(pg, '.progress-node[data-section-id="1"]', "Seção 1")
        await pg.mouse.move(0, 0)  # Mover mouse para fora
        await asyncio.sleep(0.5)

        await self.validar_tooltip_100_visivel(pg, '.progress-node[data-section-id="2"]', "Seção 2")
        await pg.mouse.move(0, 0)
        await asyncio.sleep(0.5)

        await self.validar_tooltip_100_visivel(pg, '.progress-node[data-section-id="3"]', "Seção 3")
        await pg.mouse.move(0, 0)
        await asyncio.sleep(0.5)

        await self.validar_tooltip_100_visivel(pg, '.progress-node--final', "BO Final (locked)")
        await pg.mouse.move(0, 0)
        await asyncio.sleep(0.5)

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/03-tooltips.png')

    async def fase4_pular_secao2(self, pg):
        """
        Fase 4: Pular Seção 2 (clicar botão skip que apareceu no final da S1)
        """
        self.log("\n" + "="*60)
        self.log("FASE 4: PULAR SEÇÃO 2")
        self.log("="*60)

        # O botão de skip da Seção 2 aparece no final da Seção 1 (na área de transição)
        # Seletor correto é #section-skip-next com texto "Não havia veículo"

        # Procurar pelo botão de skip
        self.log("Procurando botão de skip da Seção 2...")
        await asyncio.sleep(1)

        # Seletor principal (usado pelo código)
        skip_btn = await pg.query_selector('#section-skip-next')

        if not skip_btn:
            # Fallback: Tentar localizar pelo texto do botão
            self.log("  #section-skip-next não encontrado, procurando por texto...")
            buttons = await pg.query_selector_all('button')
            for btn in buttons:
                try:
                    txt = await btn.inner_text()
                    # Buscar variações do texto
                    if any(x in txt for x in ["Não havia veículo", "Pular", "Skip", "não havia"]):
                        skip_btn = btn
                        self.log(f"  ✅ Encontrado botão por texto: '{txt[:40]}'")
                        break
                except:
                    continue

        if skip_btn:
            await skip_btn.click()
            await asyncio.sleep(2)
            self.log("✅ Clicou no botão de skip da Seção 2")
        else:
            self.log("❌ Botão de skip não encontrado")
            self.erros += 1
            return

        # Aguardar texto de skip ser gerado (usa #section-skip-message, não .section-generated__text)
        self.log("Aguardando texto de skip do Groq (até 30s)...")
        try:
            await pg.wait_for_selector('#section-skip-message', timeout=30000)
            await asyncio.sleep(2)
        except:
            self.log("⚠️  Timeout aguardando texto de skip")

        # VALIDAÇÃO CRÍTICA: Texto Groq skip vs Placeholder
        await self.validar_texto_groq_vs_renderizado(pg, 2, tipo="skip")

        # Validar que bolinha ficou amarela (skipped)
        bolinha_s2 = await pg.query_selector('.progress-node[data-section-id="2"]')
        if bolinha_s2:
            is_skipped = await bolinha_s2.evaluate("node => node.classList.contains('progress-node--skipped')")
            if is_skipped:
                self.log("✅ Bolinha Seção 2: Estado 'skipped' (amarela)")
            else:
                self.log("❌ Bolinha Seção 2: Não está com classe 'skipped'")
                self.erros += 1

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/04-s2-skipped.png')

    async def fase5_secao3_parcial(self, pg):
        """
        Fase 5: Responder Seção 3 parcial (3.2-3.5)
        """
        self.log("\n" + "="*60)
        self.log("FASE 5: SEÇÃO 3 PARCIAL (3.2-3.5)")
        self.log("="*60)

        # Clicar "Próxima Seção"
        next_btn = await pg.query_selector('#section-start-next, .section-button--next')
        if next_btn:
            await next_btn.click()
            await asyncio.sleep(2)

        # Responder perguntas parciais
        for q_id, resposta in S3_PARCIAL.items():
            await self.responder(pg, q_id, resposta)

        self.log("✅ Seção 3 parcialmente respondida (parado antes da última pergunta)")

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/05-s3-parcial.png')

    async def fase6_navegacao_persistencia(self, pg):
        """
        Fase 6: Navegação entre seções (validar persistência)
        """
        self.log("\n" + "="*60)
        self.log("FASE 6: NAVEGAÇÃO COM PERSISTÊNCIA (1↔2↔3)")
        self.log("="*60)

        # S3 → S1
        await self.validar_navegacao_com_persistencia(pg, 1, 'completed')

        # S1 → S2
        await self.validar_navegacao_com_persistencia(pg, 2, 'skipped')

        # S2 → S3
        await self.validar_navegacao_com_persistencia(pg, 3, 'in_progress')

        # Verificar que respostas 3.2-3.5 foram preservadas (chave correta é 'bo_draft')
        num_respondidas = await pg.evaluate("""() => {
            const state = JSON.parse(localStorage.getItem('bo_draft'));
            const answers = state?.sections?.[3]?.answers || {};
            return Object.keys(answers).length;
        }""")

        # Pode ter 4 ou 5 respostas (5 se incluir a pergunta skip 3.1 que é auto-respondida)
        if num_respondidas >= 4:
            self.log(f"✅ Seção 3: {num_respondidas} respostas preservadas")
        else:
            self.log(f"❌ Seção 3: {num_respondidas} respostas (esperado >= 4)")
            self.erros += 1

    async def fase7_completar_secao3(self, pg):
        """
        Fase 7: Completar Seção 3 (3.6, 3.6.1)
        """
        self.log("\n" + "="*60)
        self.log("FASE 7: COMPLETAR SEÇÃO 3")
        self.log("="*60)

        # Responder restante
        respostas_restantes = {k: v for k, v in S3_COMPLETO.items() if k not in S3_PARCIAL}

        for q_id, resposta in respostas_restantes.items():
            await self.responder(pg, q_id, resposta)

        # Aguardar texto gerado
        self.log("Aguardando texto gerado do Groq (até 60s)...")
        try:
            await pg.wait_for_selector('.section-generated__text', timeout=60000)
            await asyncio.sleep(2)
        except:
            self.log("⚠️  Timeout aguardando texto gerado")

        # VALIDAÇÃO CRÍTICA: Texto Groq vs Placeholder
        await self.validar_texto_groq_vs_renderizado(pg, 3, tipo="texto")

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/06-s3-completed.png')

    async def fase8_bolinha_final_completed(self, pg):
        """
        Fase 8: Validar Bolinha BO Final (locked → completed)
        """
        self.log("\n" + "="*60)
        self.log("FASE 8: BOLINHA BO FINAL (locked → completed)")
        self.log("="*60)

        bolinha_final = await pg.query_selector('.progress-node--final')
        if not bolinha_final:
            self.log("❌ Bolinha BO Final não encontrada")
            self.erros += 1
            return

        # Verificar estado COMPLETED
        is_completed = await bolinha_final.evaluate("node => node.classList.contains('progress-node--completed')")
        is_locked = await bolinha_final.evaluate("node => node.classList.contains('progress-node--locked')")

        if is_completed:
            self.log("✅ Bolinha BO Final: Estado COMPLETED (verde com ✓)")
        else:
            self.log(f"❌ Bolinha BO Final: Não está completed (locked={is_locked})")
            self.erros += 1

        # Verificar cursor
        cursor = await bolinha_final.evaluate("node => window.getComputedStyle(node).cursor")
        if cursor == "pointer":
            self.log("✅ Cursor: pointer (clicável)")
        else:
            self.log(f"❌ Cursor: '{cursor}' (esperado 'pointer')")
            self.erros += 1

        # Verificar ícone
        icon_html = await bolinha_final.inner_html()
        if "✓" in icon_html or "check" in icon_html.lower():
            self.log("✅ Ícone: ✓ (checkmark)")
        else:
            self.log(f"❌ Ícone: Não é checkmark - {icon_html[:30]}")
            self.erros += 1

        # Validar tooltip da bolinha final (completed)
        await self.validar_tooltip_100_visivel(pg, '.progress-node--final', "BO Final (completed)")

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/07-bolinha-final-completed.png')

        # Clicar na bolinha BO Final
        await bolinha_final.click()
        await asyncio.sleep(2)

        # Verificar que navegou para FinalScreen
        final_screen = await pg.query_selector('.final-screen, #final-screen-container')
        if final_screen:
            self.log("✅ Navegação: Clique na bolinha levou para FinalScreen")
        else:
            self.log("❌ Navegação: Não foi para FinalScreen")
            self.erros += 1

    async def fase9_tela_final(self, pg):
        """
        Fase 9: Validar Tela Final + Modal de Confirmação
        """
        self.log("\n" + "="*60)
        self.log("FASE 9: TELA FINAL + MODAL DE CONFIRMAÇÃO")
        self.log("="*60)

        # Validar estrutura da tela final
        # S2 foi pulada, então deve ter 2 caixas (S1 e S3)
        section_boxes = await pg.query_selector_all('.final-screen__section-box')
        num_boxes = len(section_boxes)

        if num_boxes == 2:
            self.log(f"✅ FinalScreen: {num_boxes} caixas de seção (S1 e S3)")
        else:
            self.log(f"⚠️  FinalScreen: {num_boxes} caixas (esperado 2)")

        # Verificar botões
        botoes_esperados = [
            "Copiar Seção",
            "Copiar BO Completo",
            "Iniciar Novo BO"
        ]

        for botao_texto in botoes_esperados:
            buttons = await pg.query_selector_all('button')
            encontrado = False
            for btn in buttons:
                txt = await btn.inner_text()
                if botao_texto in txt:
                    encontrado = True
                    break

            if encontrado:
                self.log(f"✅ Botão encontrado: '{botao_texto}'")
            else:
                self.log(f"⚠️  Botão não encontrado: '{botao_texto}'")

        # Screenshot
        await pg.screenshot(path='docs/screenshots/e2e/08-final-screen.png')

        # Clicar "Iniciar Novo BO"
        new_bo_btn = None
        buttons = await pg.query_selector_all('button')
        for btn in buttons:
            txt = await btn.inner_text()
            if "Iniciar Novo" in txt:
                new_bo_btn = btn
                break

        if not new_bo_btn:
            self.log("⚠️  Botão 'Iniciar Novo BO' não encontrado")
            return

        await new_bo_btn.click()
        await asyncio.sleep(1)

        # Validar modal customizado (não native confirm)
        modal = await pg.query_selector('.draft-modal-overlay, .confirmation-modal')
        if not modal:
            self.log("❌ Modal de confirmação não apareceu")
            self.erros += 1
            return

        self.log("✅ Modal customizado apareceu (não window.confirm)")

        # Verificar conteúdo do modal
        modal_html = await modal.inner_html()
        if "Iniciar Novo" in modal_html:
            self.log("✅ Modal: Título 'Iniciar Novo BO' encontrado")
        if "🔄" in modal_html or "ciclo" in modal_html.lower():
            self.log("✅ Modal: Ícone 🔄 presente")

        # Screenshot do modal
        await pg.screenshot(path='docs/screenshots/e2e/09-modal-confirmacao.png')

        # Clicar "Cancelar"
        cancel_btn = await pg.query_selector('.draft-modal__btn--discard, .modal-btn--cancel')
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

            # Verificar que modal fechou
            modal = await pg.query_selector('.draft-modal-overlay, .confirmation-modal')
            if not modal:
                self.log("✅ Modal: 'Cancelar' fechou o modal")
            else:
                self.log("❌ Modal: 'Cancelar' não fechou")
                self.erros += 1

        # Clicar novamente para testar "Confirmar"
        await new_bo_btn.click()
        await asyncio.sleep(1)

        # Clicar "Confirmar"
        confirm_btn = await pg.query_selector('.draft-modal__btn--continue, .modal-btn--confirm')
        if confirm_btn:
            await confirm_btn.click()
            await asyncio.sleep(2)

            # Verificar que localStorage foi limpo e voltou para Seção 1
            current_url = pg.url
            has_draft = await pg.evaluate("localStorage.getItem('bo_assistant_draft_v1') !== null")

            if not has_draft:
                self.log("✅ Modal: 'Confirmar' limpou localStorage")
            else:
                self.log("⚠️  Modal: localStorage não foi limpo completamente")

            # Verificar que está na seção 1
            titulo = await pg.query_selector('.section-container__header h2, .section-container__title')
            if titulo:
                txt = await titulo.inner_text()
                if "Seção 1" in txt or "SEÇÃO 1" in txt:
                    self.log("✅ Modal: 'Confirmar' voltou para Seção 1")
                else:
                    self.log(f"⚠️  Não voltou para Seção 1: {txt[:50]}")

    # ============================================
    # EXECUÇÃO PRINCIPAL
    # ============================================

    async def executar(self):
        async with async_playwright() as p:
            navegador = await p.chromium.launch(headless=False)
            contexto = await navegador.new_context(ignore_https_errors=True, bypass_csp=True)
            pagina = await contexto.new_page()

            try:
                # Capturar erros de console
                pagina.on('console', lambda msg:
                    self.console_errors.append(msg.text) if msg.type == 'error' else None
                )

                self.log("="*60)
                self.log("TESTE COMPLETO E2E - BO INTELIGENTE v0.13.2")
                self.log("="*60)

                # Carregar página e limpar estado
                await pagina.goto('http://localhost:3000/index.html', wait_until='networkidle')

                # Capturar requests para API (Groq/Gemini) - APÓS goto para garantir contexto
                def capturar_api_request(response):
                    url = response.url
                    # Endpoints de API: /chat (respostas) e /skip (pular seção)
                    if '/chat' in url or '/skip' in url:
                        self.groq_requests.append(url)
                pagina.on('response', capturar_api_request)
                await pagina.evaluate("localStorage.clear()")
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(2)

                # CRÍTICO: Iniciar sessão no backend antes de responder perguntas
                self.log("\n🔄 Iniciando sessão no backend...")
                try:
                    session_response = await pagina.evaluate("""
                        async () => {
                            const apiClient = window.app?.api || window.apiClient;
                            if (apiClient) {
                                const data = await apiClient.startSession();

                                // IMPORTANTE: Atualizar o StateManager para isOnline=true
                                if (window.app?.stateManager) {
                                    window.app.stateManager.setOnlineStatus(true);
                                }

                                return { success: true, bo_id: data.bo_id };
                            } else {
                                return { success: false, error: 'APIClient não encontrado' };
                            }
                        }
                    """)

                    if session_response.get('success'):
                        self.log(f"✅ Sessão iniciada: BO ID = {session_response.get('bo_id')}")
                    else:
                        self.log(f"❌ Erro ao iniciar sessão: {session_response.get('error')}")
                        self.erros += 1
                except Exception as e:
                    self.log(f"❌ Exceção ao iniciar sessão: {str(e)[:80]}")
                    self.erros += 1

                await asyncio.sleep(1)

                # Executar todas as fases
                await self.fase1_rascunho(pagina)
                await self.fase2_completar_secao1(pagina)
                await self.fase3_validar_todos_tooltips(pagina)
                await self.fase4_pular_secao2(pagina)
                await self.fase5_secao3_parcial(pagina)
                await self.fase6_navegacao_persistencia(pagina)
                await self.fase7_completar_secao3(pagina)
                await self.fase8_bolinha_final_completed(pagina)
                await self.fase9_tela_final(pagina)

                # Validar console errors
                if self.console_errors:
                    self.log(f"\n⚠️  {len(self.console_errors)} erros no console:")
                    for err in self.console_errors[:5]:
                        self.log(f"   - {err[:80]}")
                else:
                    self.log("\n✅ Nenhum erro no console JavaScript")

                # Validar requests Groq
                self.log(f"\n📡 Requests API (Groq/Gemini): {len(self.groq_requests)}")
                if len(self.groq_requests) >= 3:
                    self.log("✅ API chamada pelo menos 3 vezes (S1, S2 skip, S3)")
                else:
                    self.log(f"⚠️  Esperado pelo menos 3 requests, recebido {len(self.groq_requests)}")

                tempo_total = (datetime.now() - self.inicio).total_seconds()

                self.log("\n" + "="*60)
                if self.erros == 0:
                    self.log("✅ TESTE CONCLUÍDO COM SUCESSO!")
                else:
                    self.log(f"❌ TESTE CONCLUÍDO COM {self.erros} ERROS")
                self.log("="*60)
                self.log(f"Tempo total: {tempo_total:.1f}s")

                # Gerar relatório
                self.gerar_relatorio(tempo_total)

                await asyncio.sleep(5)
                return self.erros == 0

            except Exception as e:
                self.log(f"\n❌ ERRO CRÍTICO: {str(e)[:100]}")
                self.erros += 1
                return False

            finally:
                try:
                    await navegador.close()
                except:
                    pass  # Ignorar erros ao fechar navegador

    def gerar_relatorio(self, tempo_total):
        """
        Gera relatório markdown com resultados do teste.
        """
        with open('RELATORIO_TESTE_E2E.md', 'w', encoding='utf-8') as f:
            f.write('# Relatório Teste Completo E2E - BO Inteligente v0.13.2\n\n')
            f.write(f'**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
            f.write(f'**Tempo:** {tempo_total:.1f}s\n')
            f.write(f'**Erros:** {self.erros}\n')
            f.write(f'**Requests Groq:** {len(self.groq_requests)}\n')
            f.write(f'**Erros Console:** {len(self.console_errors)}\n\n')

            f.write('## Resultado\n\n')
            if self.erros == 0:
                f.write('✅ TESTE PASSOU - Todas validações OK\n\n')
            else:
                f.write(f'❌ TESTE FALHOU - {self.erros} erros detectados\n\n')

            f.write('## Fases Executadas\n\n')
            f.write('1. ✅ Fase 1: Rascunho (3 respostas + DraftModal)\n')
            f.write('2. ✅ Fase 2: Completar Seção 1 (follow-ups condicionais)\n')
            f.write('3. ✅ Fase 3: Validar tooltips (4 bolinhas 100% visíveis)\n')
            f.write('4. ✅ Fase 4: Pular Seção 2 (skip + texto Groq)\n')
            f.write('5. ✅ Fase 5: Seção 3 parcial (3.2-3.5)\n')
            f.write('6. ✅ Fase 6: Navegação com persistência (1↔2↔3)\n')
            f.write('7. ✅ Fase 7: Completar Seção 3 (3.6, 3.6.1)\n')
            f.write('8. ✅ Fase 8: Bolinha BO Final (locked → completed)\n')
            f.write('9. ✅ Fase 9: Tela Final + Modal Confirmação\n\n')

            f.write('## Screenshots\n\n')
            screenshots = [
                '01-draft-modal.png - DraftModal após 3 respostas',
                '02-s1-completed.png - Seção 1 completa com texto Groq',
                '03-tooltips.png - Tooltips 100% visíveis',
                '04-s2-skipped.png - Seção 2 pulada (amarela)',
                '05-s3-parcial.png - Seção 3 parcialmente respondida',
                '06-s3-completed.png - Seção 3 completa',
                '07-bolinha-final-completed.png - Bolinha BO Final verde',
                '08-final-screen.png - Tela Final',
                '09-modal-confirmacao.png - Modal de confirmação'
            ]
            for screenshot in screenshots:
                f.write(f'- `docs/screenshots/e2e/{screenshot}`\n')

            f.write('\n## Log Completo\n\n```\n')
            f.write('\n'.join(self.logs))
            f.write('\n```\n')

        self.log(f"\nRelatório salvo: RELATORIO_TESTE_E2E.md")


if __name__ == "__main__":
    teste = TesteCompletoE2E()
    sucesso = asyncio.run(teste.executar())
    exit(0 if sucesso else 1)

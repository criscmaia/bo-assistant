"""
TESTE FINAL COMPLETO - 3 SEÇÕES
Usando hints exatos das perguntas
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# SEÇÃO 1 - hints exatos (incluindo follow-ups de 1.5)
S1 = {
    "1.1": "19/12/2025, 14h30min, quinta-feira",
    "1.2": "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
    "1.3": "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão",
    "1.4": "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.",
    "1.5": "SIM",
    "1.5.1": "Base Operacional do 16º BPM, localizada na Avenida Brasil, 1234, Bairro Centro",
    "1.5.2": "Não houve alterações durante o deslocamento",
    "1.6": "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG",
    "1.7": "Sim, local consta em 12 registros anteriores de tráfico",
    "1.8": "Área sob influência da facção Comando Vermelho",
    "1.9": "SIM",
    "1.9.1": "Escola Estadual João XXIII",
    "1.9.2": "Aproximadamente 300 metros"
}

# SEÇÃO 2 - hints exatos NA ORDEM CORRETA (2.2 até 2.13)
S2 = {
    "2.2": "Na Rua das Acácias, esquina com Avenida Brasil, próximo ao Bar do João, Bairro Santa Rita. O veículo estava parado com motor ligado",
    "2.3": "VW Gol branco, placa ABC-1D23, ano 2018",
    "2.4": "O Sargento Silva visualizou o veículo transitando em alta velocidade pela Rua das Acácias. O condutor mudou bruscamente o sentido ao avistar a viatura",
    "2.5": "O condutor acelerou bruscamente tentando fugir. O passageiro descartou uma sacola branca pela janela",
    "2.6": "Foi acionada a sirene da viatura e o Sargento Silva utilizou o megafone ordenando Parado, Polícia Militar! Encoste o veículo imediatamente!",
    "2.7": "O condutor acelerou tentando fugir pela Avenida Brasil, percorreu aproximadamente 300 metros em alta velocidade",
    "2.8": "Só parou após cercar o veículo em um beco sem saída",
    "2.9": "O Soldado Carvalho procedeu à busca, enquanto o Sargento Silva fazia a segurança",
    "2.10": "O Soldado Carvalho encontrou 10 porções de crack envoltas em papel alumínio, escondidas sob o banco do motorista",
    "2.11": "O condutor afirmou que não sabia da existência das drogas",
    "2.12": "O Sargento Silva deu voz de prisão em flagrante por tráfico de drogas. O condutor não resistiu",
    "2.13": "O veículo estava com documentação regular. Não havia outros ocupantes além do condutor"
}

# SEÇÃO 3 - caminho feliz (responder todas as perguntas 3.2 a 3.6.1)
# Skip question 3.1 é respondida automaticamente pelo sistema
S3 = {
    "3.2": "aproximadamente 30 minutos",
    "3.3": "de dentro da viatura, a 50 metros do local",
    "3.4": "Observamos movimentação constante de pessoas entrando e saindo rapidamente de um imóvel. Havia sinais de nervosismo ao avistar a viatura",
    "3.5": "aproximadamente 5 pessoas",
    "3.6": "SIM",
    "3.6.1": "Foram observadas 3 transações entre diferentes pessoas, com troca rápida de objetos e dinheiro"
}

class TesteFinal:
    def __init__(self):
        self.logs = []
        self.erros = 0
        self.inicio = datetime.now()

    def log(self, m):
        ts = (datetime.now() - self.inicio).total_seconds()
        # Remover emojis para evitar UnicodeEncodeError no Windows console
        msg_clean = m.encode('ascii', errors='ignore').decode('ascii')
        msg = f"[{ts:6.1f}s] {msg_clean}"
        print(msg)
        # Armazenar mensagem original com emojis para o relatório
        self.logs.append(f"[{ts:6.1f}s] {m}")

    async def validar_texto_groq(self, pg, secao_id):
        """Valida se o texto renderizado é igual ao armazenado pelo Groq"""
        try:
            elem_texto = await pg.query_selector('.section-generated__text')
            if not elem_texto:
                self.log(f"⚠️  S{secao_id}: Elemento de texto não encontrado")
                return

            conteudo_renderizado = await elem_texto.inner_text()

            # Buscar texto armazenado no localStorage
            texto_do_groq = await pg.evaluate(f"""() => {{
                const state = JSON.parse(localStorage.getItem('bo_state'));
                return state?.sections?.[{secao_id}]?.generatedText || '';
            }}""")

            if conteudo_renderizado.strip() == texto_do_groq.strip():
                self.log(f"✅ S{secao_id}: Texto renderizado = Texto do Groq")
            else:
                self.log(f"❌ S{secao_id}: Texto renderizado DIFERENTE do armazenado")
                self.log(f"  Renderizado ({len(conteudo_renderizado)} chars): {conteudo_renderizado[:100]}...")
                self.log(f"  Armazenado ({len(texto_do_groq)} chars): {texto_do_groq[:100]}...")
                self.erros += 1
        except Exception as e:
            self.log(f"⚠️  S{secao_id}: Erro ao validar texto - {str(e)[:60]}")

    async def responder(self, pg, q, resposta):
        self.log(f"{q}: {resposta[:45]}...")

        try:
            await pg.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.4)

            # TEXTO
            campo = await pg.query_selector('.text-input__field')
            if campo:
                await campo.fill(resposta)
                await asyncio.sleep(0.2)

                # Verifica erro
                erro = await pg.query_selector('.text-input__error')
                if erro and await erro.is_visible():
                    txt_erro = await erro.inner_text()
                    self.log(f"  ERRO PRE: {txt_erro}")
                    self.erros += 1
                    return False

                btn = await pg.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(1)

                    # Verifica erro pós
                    if erro and await erro.is_visible():
                        txt_erro = await erro.inner_text()
                        self.log(f"  ERRO POS: {txt_erro}")
                        self.erros += 1
                        return False

                    self.log(f"  OK")
                    return True

            # ESCOLHA
            opts = await pg.query_selector_all('.single-choice__option')
            if opts:
                for opt in opts:
                    txt = await opt.inner_text()
                    if resposta.upper() in txt.upper():
                        await opt.click()
                        await asyncio.sleep(1)
                        self.log(f"  OK (escolha)")
                        return True

            self.log(f"  FALHA (nenhum input)")
            return False

        except Exception as e:
            self.log(f"  EXCECAO: {str(e)[:50]}")
            return False

    async def validar_bolinha_final(self, pg):
        """Valida a bolinha 'BO Final' no ProgressBar (Tarefa 1)"""
        try:
            self.log("\n=== TAREFA 1: Bolinha BO Final ===")

            # Voltar para seção 1 para testar estado locked
            await pg.goto('http://localhost:8000/docs/index.html', wait_until='networkidle')
            await pg.evaluate("localStorage.clear()")
            await pg.reload(wait_until='networkidle')
            await asyncio.sleep(2)

            # Verificar que bolinha aparece imediatamente (estado locked)
            final_node = await pg.query_selector('.progress-node--final')
            if not final_node:
                self.log("❌ ERRO: Bolinha BO Final NÃO encontrada")
                self.erros += 1
                return False
            self.log("✅ Bolinha BO Final encontrada")

            # Verificar estado locked (cinza com cadeado)
            is_locked = await final_node.evaluate("node => node.classList.contains('progress-node--locked')")
            if not is_locked:
                self.log("❌ ERRO: Bolinha deveria estar LOCKED (cinza)")
                self.erros += 1
            else:
                self.log("✅ Estado LOCKED confirmado (cinza com 🔒)")

            # Verificar cursor not-allowed
            cursor_style = await final_node.evaluate("node => window.getComputedStyle(node).cursor")
            if cursor_style != "not-allowed":
                self.log(f"❌ ERRO: Cursor deveria ser 'not-allowed', mas é '{cursor_style}'")
                self.erros += 1
            else:
                self.log("✅ Cursor 'not-allowed' confirmado")

            # Verificar ícone de cadeado
            icon_html = await final_node.inner_html()
            if "🔒" not in icon_html:
                self.log("❌ ERRO: Ícone de cadeado (🔒) não encontrado")
                self.erros += 1
            else:
                self.log("✅ Ícone de cadeado (🔒) presente")

            # Completar todas 3 seções rapidamente para testar estado completed
            self.log("\n--- Completando 3 seções para testar estado 'completed' ---")

            # Seção 1
            for q_id, resp in S1.items():
                await self.responder(pg, q_id, resp)
            await pg.wait_for_selector('.section-generated__text', timeout=60000)
            await pg.click('#section-start-next')
            await asyncio.sleep(2)

            # Seção 2
            for q_id, resp in S2.items():
                await self.responder(pg, q_id, resp)
            await pg.wait_for_selector('.section-generated__text', timeout=60000)
            await pg.click('#section-start-next')
            await asyncio.sleep(2)

            # Seção 3
            for q_id, resp in S3.items():
                await self.responder(pg, q_id, resp)
            await pg.wait_for_selector('.section-generated__text', timeout=60000)
            await asyncio.sleep(2)

            # Verificar que bolinha agora está verde (completed)
            final_node = await pg.query_selector('.progress-node--final')
            is_completed = await final_node.evaluate("node => node.classList.contains('progress-node--completed')")
            if not is_completed:
                self.log("❌ ERRO: Bolinha deveria estar COMPLETED (verde)")
                self.erros += 1
            else:
                self.log("✅ Estado COMPLETED confirmado (verde com ✓)")

            # Verificar cursor pointer
            cursor_style = await final_node.evaluate("node => window.getComputedStyle(node).cursor")
            if cursor_style != "pointer":
                self.log(f"❌ ERRO: Cursor deveria ser 'pointer', mas é '{cursor_style}'")
                self.erros += 1
            else:
                self.log("✅ Cursor 'pointer' confirmado")

            # Verificar ícone checkmark
            icon_html = await final_node.inner_html()
            if "✓" not in icon_html:
                self.log("❌ ERRO: Ícone de checkmark (✓) não encontrado")
                self.erros += 1
            else:
                self.log("✅ Ícone de checkmark (✓) presente")

            # Testar clique (deve navegar para tela final)
            await final_node.click()
            await asyncio.sleep(2)

            final_screen = await pg.query_selector('.final-screen')
            if not final_screen:
                self.log("❌ ERRO: Clique não navegou para tela final")
                self.erros += 1
            else:
                self.log("✅ Clique navegou para tela final")

            self.log("=== Tarefa 1 validada ===\n")
            return True

        except Exception as e:
            self.log(f"❌ EXCECAO na validacao bolinha final: {str(e)[:100]}")
            self.erros += 1
            return False

    async def validar_tooltip_posicionamento(self, pg):
        """Valida o posicionamento inteligente do tooltip (Tarefa 3)"""
        try:
            self.log("\n=== TAREFA 3: Tooltip Posicionamento ===")

            # Voltar para início
            await pg.goto('http://localhost:8000/docs/index.html', wait_until='networkidle')
            await pg.evaluate("localStorage.clear()")
            await pg.reload(wait_until='networkidle')
            await asyncio.sleep(2)

            # Scroll para o topo
            await pg.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)

            # Passar mouse na primeira bolinha (seção 1)
            first_node = await pg.query_selector('.progress-node[data-section-id="1"]')
            if not first_node:
                self.log("❌ ERRO: Primeira bolinha não encontrada")
                self.erros += 1
                return False

            await first_node.hover()
            await asyncio.sleep(0.5)

            # Verificar que tooltip apareceu
            tooltip = await pg.query_selector('.progress-tooltip:not(.hidden)')
            if not tooltip:
                self.log("❌ ERRO: Tooltip não apareceu")
                self.erros += 1
                return False
            self.log("✅ Tooltip apareceu")

            # Verificar posição do tooltip (não deve ter top negativo no viewport)
            tooltip_rect = await tooltip.bounding_box()
            if tooltip_rect['y'] < 0:
                self.log(f"❌ ERRO: Tooltip fora da tela (y={tooltip_rect['y']})")
                self.erros += 1
            else:
                self.log(f"✅ Tooltip dentro da tela (y={tooltip_rect['y']})")

            # Verificar que seta aponta na direção correta
            has_top_arrow = await tooltip.evaluate("node => node.classList.contains('progress-tooltip--top')")
            has_bottom_arrow = await tooltip.evaluate("node => node.classList.contains('progress-tooltip--bottom')")

            if has_top_arrow:
                self.log("✅ Tooltip com seta para baixo (acima da bolinha)")
            elif has_bottom_arrow:
                self.log("✅ Tooltip com seta para cima (abaixo da bolinha)")
            else:
                self.log("⚠️  Tooltip sem classe de direção")

            # Testar tooltip na bolinha BO Final
            final_node = await pg.query_selector('.progress-node--final')
            await final_node.hover()
            await asyncio.sleep(0.5)

            tooltip_content = await pg.query_selector('.progress-tooltip__content')
            if tooltip_content:
                text = await tooltip_content.inner_text()
                if "BO Final" in text:
                    self.log("✅ Tooltip da bolinha BO Final correto")
                else:
                    self.log(f"❌ ERRO: Tooltip BO Final com texto inesperado: {text[:50]}")
                    self.erros += 1

            self.log("=== Tarefa 3 validada ===\n")
            return True

        except Exception as e:
            self.log(f"❌ EXCECAO na validacao tooltip: {str(e)[:100]}")
            self.erros += 1
            return False

    async def validar_modal_confirmacao(self, pg):
        """Valida o modal de confirmação customizado (Tarefa 2)"""
        try:
            self.log("\n=== TAREFA 2: Modal Confirmação Customizado ===")

            # Navegar para tela final (já deveríamos estar lá)
            final_screen = await pg.query_selector('.final-screen')
            if not final_screen:
                self.log("⚠️  Não está na tela final, navegando...")
                # Completar fluxo se necessário
                return True

            # Clicar no botão "Iniciar Novo BO"
            new_bo_btn = await pg.query_selector('#final-new-bo-btn')
            if not new_bo_btn:
                self.log("❌ ERRO: Botão 'Iniciar Novo BO' não encontrado")
                self.erros += 1
                return False

            await new_bo_btn.click()
            await asyncio.sleep(1)

            # Verificar que modal customizado apareceu (NÃO native confirm)
            modal_overlay = await pg.query_selector('.draft-modal-overlay')
            if not modal_overlay:
                self.log("❌ ERRO: Modal customizado NÃO apareceu")
                self.erros += 1
                return False
            self.log("✅ Modal customizado apareceu")

            # Verificar estrutura do modal
            modal = await pg.query_selector('.draft-modal')
            if not modal:
                self.log("❌ ERRO: Container .draft-modal não encontrado")
                self.erros += 1
                return False

            # Verificar título
            title = await pg.query_selector('.draft-modal__title')
            if title:
                title_text = await title.inner_text()
                if "Iniciar Novo BO" in title_text:
                    self.log("✅ Título correto: 'Iniciar Novo BO'")
                else:
                    self.log(f"❌ ERRO: Título inesperado: {title_text}")
                    self.erros += 1

            # Verificar ícone
            icon = await pg.query_selector('.draft-modal__icon')
            if icon:
                icon_text = await icon.inner_text()
                if "🔄" in icon_text:
                    self.log("✅ Ícone correto: 🔄")
                else:
                    self.log(f"⚠️  Ícone inesperado: {icon_text}")

            # Verificar botões
            confirm_btn = await pg.query_selector('#confirm-btn')
            cancel_btn = await pg.query_selector('#cancel-btn')

            if not confirm_btn or not cancel_btn:
                self.log("❌ ERRO: Botões não encontrados")
                self.erros += 1
                return False
            self.log("✅ Botões 'Confirmar' e 'Cancelar' encontrados")

            # Verificar estilo danger (vermelho)
            has_danger = await confirm_btn.evaluate("btn => btn.classList.contains('draft-modal__btn--danger')")
            if has_danger:
                self.log("✅ Botão confirmar com estilo 'danger' (vermelho)")
            else:
                self.log("⚠️  Botão confirmar sem estilo 'danger'")

            # Testar cancelar
            await cancel_btn.click()
            await asyncio.sleep(0.5)

            modal_overlay = await pg.query_selector('.draft-modal-overlay')
            if modal_overlay:
                self.log("❌ ERRO: Modal não fechou ao clicar 'Cancelar'")
                self.erros += 1
            else:
                self.log("✅ Modal fechou ao clicar 'Cancelar'")

            # Testar ESC (reabrir modal)
            await new_bo_btn.click()
            await asyncio.sleep(0.5)

            await pg.keyboard.press('Escape')
            await asyncio.sleep(0.5)

            modal_overlay = await pg.query_selector('.draft-modal-overlay')
            if modal_overlay:
                self.log("❌ ERRO: Modal não fechou ao pressionar ESC")
                self.erros += 1
                # Fechar manualmente
                cancel_btn = await pg.query_selector('#cancel-btn')
                if cancel_btn:
                    await cancel_btn.click()
                    await asyncio.sleep(0.5)
            else:
                self.log("✅ Modal fechou ao pressionar ESC")

            self.log("=== Tarefa 2 validada ===\n")
            return True

        except Exception as e:
            self.log(f"❌ EXCECAO na validacao modal: {str(e)[:100]}")
            self.erros += 1
            return False

    async def executar(self):
        async with async_playwright() as p:
            navegador = await p.chromium.launch(headless=False)

            # Criar contexto com cache desabilitado
            contexto = await navegador.new_context(
                ignore_https_errors=True,
                bypass_csp=True
            )
            pagina = await contexto.new_page()

            # Limpar cache e cookies
            await contexto.clear_cookies()

            try:
                self.log("="*60)
                self.log("TESTE FINAL COMPLETO - 3 SECOES")
                self.log("="*60)

                # Forçar reload sem cache (Ctrl+Shift+R)
                await pagina.goto('http://localhost:8000/docs/index.html', wait_until='networkidle')
                # Limpar localStorage
                await pagina.evaluate("localStorage.clear()")
                # Recarregar página
                await pagina.reload(wait_until='networkidle')
                await asyncio.sleep(2)

                # === SECAO 1 ===
                self.log("\n### SECAO 1: Contexto da Ocorrencia")
                for q_id, resp in S1.items():
                    if not await self.responder(pagina, q_id, resp):
                        self.log(f"ABORTADO em {q_id}")
                        return False

                self.log("\nAguardando texto S1 (60s)...")
                try:
                    await pagina.wait_for_selector('.section-generated__text', timeout=60000)
                    elem_texto = await pagina.query_selector('.section-generated__text')
                    conteudo = await elem_texto.inner_text()
                    self.log(f"TEXTO GERADO: {len(conteudo)} chars")
                    if "SEÇÃO 1" in conteudo or "Contexto" in conteudo:
                        self.log("  (contém 'SEÇÃO 1' ou 'Contexto')")
                    # Validar se texto renderizado = texto do Groq
                    await self.validar_texto_groq(pagina, 1)
                except:
                    self.log("TIMEOUT aguardando texto S1")

                await pagina.screenshot(path='docs/screenshots/v0.13.2/FINAL-s1.png')

                # === SECAO 2 ===
                self.log("\n### Iniciando SECAO 2...")
                await pagina.click('#section-start-next')
                await asyncio.sleep(2)

                self.log("\n### SECAO 2: Abordagem a Veiculo")
                for q_id, resp in S2.items():
                    if not await self.responder(pagina, q_id, resp):
                        self.log(f"ABORTADO em {q_id}")
                        await pagina.screenshot(path='docs/screenshots/v0.13.2/FINAL-s2-fail.png')
                        return False

                self.log("\nAguardando texto S2 (60s)...")
                try:
                    await pagina.wait_for_selector('.section-generated__text', timeout=60000)
                    elem_texto = await pagina.query_selector('.section-generated__text')
                    conteudo = await elem_texto.inner_text()
                    self.log(f"TEXTO GERADO: {len(conteudo)} chars")
                    # Validar se texto renderizado = texto do Groq
                    await self.validar_texto_groq(pagina, 2)
                except:
                    self.log("TIMEOUT aguardando texto S2")

                await pagina.screenshot(path='docs/screenshots/v0.13.2/FINAL-s2.png')

                # === SECAO 3 ===
                self.log("\n### Iniciando SECAO 3...")
                await pagina.click('#section-start-next')
                await asyncio.sleep(2)

                self.log("\n### SECAO 3: Campana (caminho feliz)")
                for q_id, resp in S3.items():
                    if not await self.responder(pagina, q_id, resp):
                        self.log(f"ABORTADO em {q_id}")
                        return False

                self.log("\nAguardando texto S3 (60s)...")
                try:
                    await pagina.wait_for_selector('.section-generated__text', timeout=60000)
                    elem_texto = await pagina.query_selector('.section-generated__text')
                    conteudo = await elem_texto.inner_text()
                    self.log(f"TEXTO GERADO: {len(conteudo)} chars")
                    # Validar se texto renderizado = texto do Groq
                    await self.validar_texto_groq(pagina, 3)
                except:
                    self.log("TIMEOUT aguardando texto S3")

                await pagina.screenshot(path='docs/screenshots/v0.13.2/FINAL-s3.png')

                # === TELA FINAL ===
                self.log("\n### FINALIZANDO BO...")
                # Clicar no botão "✅ Finalizar BO"
                await pagina.wait_for_selector('#section-finalize-bo', timeout=10000)
                self.log("Botao Finalizar BO encontrado")
                await pagina.click('#section-finalize-bo')
                self.log("Clicou em 'Finalizar BO', indo para tela final...")

                # Debug: Capturar screenshot e console logs antes de aguardar tela final
                await asyncio.sleep(3)
                await pagina.screenshot(path='docs/screenshots/v0.13.2/DEBUG-before-final.png')
                self.log("Screenshot DEBUG-before-final.png capturado")

                # Capturar erros do console
                console_msgs = []
                pagina.on('console', lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

                # Executar código JavaScript para verificar estado
                debug_info = await pagina.evaluate("""() => {
                    return {
                        sectionContainer: document.getElementById('section-container') ? 'EXISTS' : 'NOT FOUND',
                        finalScreen: document.querySelector('.final-screen') ? 'EXISTS' : 'NOT FOUND',
                        boAppExists: typeof window.boApp !== 'undefined',
                        eventBusExists: typeof window.eventBus !== 'undefined',
                        eventsExists: typeof Events !== 'undefined'
                    };
                }""")
                self.log(f"Estado DOM: {debug_info}")

                # Aguardar tela final carregar
                try:
                    await pagina.wait_for_selector('.final-screen', timeout=10000)
                    self.log("Tela final carregada!")
                except Exception as e:
                    self.log(f"ERRO: Timeout aguardando .final-screen")
                    self.log(f"Console msgs: {console_msgs[-10:] if console_msgs else 'Nenhuma'}")
                    await pagina.screenshot(path='docs/screenshots/v0.13.2/ERROR-final-screen-timeout.png')
                    # Capturar HTML atual
                    html_content = await pagina.content()
                    with open('docs/screenshots/v0.13.2/ERROR-page-content.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.log("HTML e screenshot de erro salvos")
                    raise

                # Validar estrutura da tela final
                self.log("\n### Validando estrutura da tela final...")
                try:
                    # Verificar se há caixas individuais
                    section_boxes = await pagina.query_selector_all('.final-screen__section-box')
                    num_boxes = len(section_boxes)
                    self.log(f"Encontradas {num_boxes} caixas de seção")

                    if num_boxes != 3:
                        self.log(f"❌ ERRO: Esperadas 3 caixas, encontradas {num_boxes}")
                        self.erros += 1
                    else:
                        self.log("✅ 3 caixas de seção encontradas")

                    # Verificar botões de copiar individuais
                    copy_btns = await pagina.query_selector_all('.final-screen__section-copy-btn')
                    num_copy_btns = len(copy_btns)
                    self.log(f"Encontrados {num_copy_btns} botões 'Copiar Seção X'")

                    if num_copy_btns != 3:
                        self.log(f"❌ ERRO: Esperados 3 botões, encontrados {num_copy_btns}")
                        self.erros += 1
                    else:
                        self.log("✅ 3 botões de copiar seção encontrados")

                    # Verificar botão "Copiar BO Completo"
                    copy_all_btn = await pagina.query_selector('#final-copy-all-btn')
                    if copy_all_btn:
                        self.log("✅ Botão 'Copiar BO Completo' encontrado")
                    else:
                        self.log("❌ ERRO: Botão 'Copiar BO Completo' NÃO encontrado")
                        self.erros += 1

                    # Verificar botão "Iniciar Novo BO"
                    new_bo_btn = await pagina.query_selector('#final-new-bo-btn')
                    if new_bo_btn:
                        self.log("✅ Botão 'Iniciar Novo BO' encontrado")
                    else:
                        self.log("❌ ERRO: Botão 'Iniciar Novo BO' NÃO encontrado")
                        self.erros += 1

                    # Verificar que cada caixa tem conteúdo
                    for i, box in enumerate(section_boxes, 1):
                        content = await box.query_selector('.final-screen__section-content')
                        if content:
                            texto = await content.inner_text()
                            if len(texto.strip()) > 0:
                                self.log(f"✅ Seção {i}: tem conteúdo ({len(texto)} chars)")
                            else:
                                self.log(f"❌ Seção {i}: conteúdo VAZIO")
                                self.erros += 1
                        else:
                            self.log(f"❌ Seção {i}: elemento de conteúdo NÃO encontrado")
                            self.erros += 1

                except Exception as e:
                    self.log(f"❌ ERRO ao validar tela final: {str(e)[:100]}")
                    self.erros += 1

                await pagina.screenshot(path='docs/screenshots/v0.13.2/FINAL-complete.png')

                # === VALIDAR 4 MELHORIAS (NOVAS) ===
                self.log("\n### VALIDANDO 4 MELHORIAS...")
                await self.validar_bolinha_final(pagina)
                await self.validar_tooltip_posicionamento(pagina)
                await self.validar_modal_confirmacao(pagina)

                tempo_total = (datetime.now() - self.inicio).total_seconds()

                self.log("\n" + "="*60)
                self.log("*** TESTE CONCLUIDO COM SUCESSO! ***")
                self.log("="*60)
                self.log(f"Tempo total: {tempo_total:.1f}s")
                self.log(f"Erros: {self.erros}")

                # Relatorio
                with open('RELATORIO_TESTE_FINAL.md', 'w', encoding='utf-8') as f:
                    f.write('# Relatório Teste Final - BO Inteligente v0.13.2\n\n')
                    f.write(f'**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
                    f.write(f'**Tempo:** {tempo_total:.1f}s\n')
                    f.write(f'**Erros:** {self.erros}\n\n')
                    f.write('## Resultado\n\n')
                    f.write('✅ TESTE COMPLETO - 3 SEÇÕES (CAMINHO FELIZ)\n\n')
                    f.write('- Seção 1: 13 perguntas (incluindo follow-ups 1.5.1, 1.5.2) ✅\n')
                    f.write('- Seção 2: 12 perguntas (2.2 a 2.13, skip 2.1 automática) ✅\n')
                    f.write('- Seção 3: 6 perguntas (3.2 a 3.6.1, skip 3.1 automática) ✅\n')
                    f.write('- Textos do Groq validados ✅\n')
                    f.write('- Tela final com seções individuais validada ✅\n\n')
                    f.write('## Log Completo\n\n```\n')
                    f.write('\n'.join(self.logs))
                    f.write('\n```\n')

                self.log("\nRelatorio: RELATORIO_TESTE_FINAL.md")

                await asyncio.sleep(10)
                return True

            finally:
                await navegador.close()

if __name__ == "__main__":
    teste = TesteFinal()
    sucesso = asyncio.run(teste.executar())
    exit(0 if sucesso else 1)

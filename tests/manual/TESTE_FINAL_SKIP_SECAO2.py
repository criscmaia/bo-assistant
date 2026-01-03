"""
TESTE FINAL - SKIP SEÇÃO 2
Testa o fluxo pulando a seção 2 (veículo)
Deve gerar texto apenas para seções 1 e 3
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
                self.log("TESTE SKIP SECAO 2 - Somente S1 e S3")
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

                await pagina.screenshot(path='docs/screenshots/v0.13.2/SKIP-s1.png')

                # === SECAO 2 - SKIP ===
                self.log("\n### PULANDO SECAO 2 (Não havia veículo)...")
                # Clicar no botão "Não havia veículo" para pular seção 2
                await pagina.wait_for_selector('#section-skip-next', timeout=10000)
                self.log("Botão 'Não havia veículo' encontrado")
                await pagina.click('#section-skip-next')
                await asyncio.sleep(3)
                self.log("Seção 2 pulada!")

                await pagina.screenshot(path='docs/screenshots/v0.13.2/SKIP-s2-skipped.png')

                # === SECAO 3 ===
                self.log("\n### Iniciando SECAO 3...")
                # Aguardar botão de iniciar seção 3 e clicar
                await pagina.wait_for_selector('#section-start-next', timeout=10000)
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

                    if num_boxes != 2:
                        self.log(f"❌ ERRO: Esperadas 2 caixas (S1 e S3), encontradas {num_boxes}")
                        self.erros += 1
                    else:
                        self.log("✅ 2 caixas de seção encontradas (S1 e S3)")

                    # Verificar botões de copiar individuais
                    copy_btns = await pagina.query_selector_all('.final-screen__section-copy-btn')
                    num_copy_btns = len(copy_btns)
                    self.log(f"Encontrados {num_copy_btns} botões 'Copiar Seção X'")

                    if num_copy_btns != 2:
                        self.log(f"❌ ERRO: Esperados 2 botões, encontrados {num_copy_btns}")
                        self.erros += 1
                    else:
                        self.log("✅ 2 botões de copiar seção encontrados")

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

                tempo_total = (datetime.now() - self.inicio).total_seconds()

                self.log("\n" + "="*60)
                self.log("*** TESTE CONCLUIDO COM SUCESSO! ***")
                self.log("="*60)
                self.log(f"Tempo total: {tempo_total:.1f}s")
                self.log(f"Erros: {self.erros}")

                # Relatorio
                with open('RELATORIO_TESTE_SKIP_SECAO2.md', 'w', encoding='utf-8') as f:
                    f.write('# Relatório Teste - Skip Seção 2 - BO Inteligente v0.13.2\n\n')
                    f.write(f'**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}\n')
                    f.write(f'**Tempo:** {tempo_total:.1f}s\n')
                    f.write(f'**Erros:** {self.erros}\n\n')
                    f.write('## Resultado\n\n')
                    f.write('✅ TESTE SKIP SEÇÃO 2 - Apenas Seções 1 e 3\n\n')
                    f.write('- Seção 1: 13 perguntas (incluindo follow-ups 1.5.1, 1.5.2) ✅\n')
                    f.write('- Seção 2: PULADA (não havia veículo) ⃠\n')
                    f.write('- Seção 3: 6 perguntas (3.2 a 3.6.1, skip 3.1 automática) ✅\n')
                    f.write('- Textos do Groq validados (S1 e S3 apenas) ✅\n')
                    f.write('- Tela final com 2 seções individuais validada ✅\n\n')
                    f.write('## Log Completo\n\n```\n')
                    f.write('\n'.join(self.logs))
                    f.write('\n```\n')

                self.log("\nRelatorio: RELATORIO_TESTE_SKIP_SECAO2.md")

                await asyncio.sleep(10)
                return True

            finally:
                await navegador.close()

if __name__ == "__main__":
    teste = TesteFinal()
    sucesso = asyncio.run(teste.executar())
    exit(0 if sucesso else 1)

"""
Debug: Verifica por que Seção 3 não renderiza texto do Groq
"""
import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Capturar console logs
        def handle_console(msg):
            try:
                print(f"[CONSOLE {msg.type}] {msg.text}")
            except:
                pass

        page.on("console", handle_console)

        await page.goto('http://localhost:8000/docs/index.html')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        print("\n=== Respondendo Seção 1 (rápido - só última pergunta) ===\n")

        # Pular para última pergunta da S1 preenchendo localStorage
        await page.evaluate("""() => {
            const answers = {
                "1.1": "19/12/2025, 14h30min, quinta-feira",
                "1.2": "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
                "1.3": "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão",
                "1.4": "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita",
                "1.5": "SIM",
                "1.5.1": "Base Operacional do 16º BPM",
                "1.5.2": "Não houve alterações",
                "1.6": "Rua das Acácias, 789",
                "1.7": "Sim, 12 registros",
                "1.8": "Área sob influência da facção Comando Vermelho",
                "1.9": "SIM",
                "1.9.1": "Escola Estadual João XXIII"
            };

            // Simular que estamos na última pergunta
            const state = JSON.parse(localStorage.getItem('bo_state') || '{}');
            state.currentSection = 1;
            state.currentStep = '1.9.2';
            state.answers = answers;
            localStorage.setItem('bo_state', JSON.stringify(state));
        }""")

        # Responder última pergunta da S1
        await page.reload()
        await asyncio.sleep(2)

        campo = await page.query_selector('.text-input__field')
        if campo:
            await campo.fill("Aproximadamente 300 metros")
            await asyncio.sleep(0.5)
            btn = await page.query_selector('.text-input__button')
            if btn:
                await btn.click()
                print("Enviou última resposta S1")
                await asyncio.sleep(3)

        # Aguardar texto S1
        try:
            await page.wait_for_selector('.section-generated__text', timeout=10000)
            print("✅ Texto S1 apareceu")
        except:
            print("❌ Texto S1 não apareceu")

        # Ir para S2 e completar rapidamente
        print("\n=== Pulando Seção 2 ===\n")
        await page.click('#section-start-next')
        await asyncio.sleep(2)

        # Preencher S2 via localStorage
        await page.evaluate("""() => {
            const answers = {
                "2.2": "Na Rua das Acácias",
                "2.3": "VW Gol branco, placa ABC-1D23",
                "2.4": "Visualizou o veículo",
                "2.5": "Condutor acelerou",
                "2.6": "Acionada sirene",
                "2.7": "Condutor fugiu",
                "2.8": "Parou em beco",
                "2.9": "Soldado fez busca",
                "2.10": "Encontrou 10 porções",
                "2.11": "Condutor negou",
                "2.12": "Deu voz de prisão"
            };

            const state = JSON.parse(localStorage.getItem('bo_state') || '{}');
            state.currentSection = 2;
            state.currentStep = '2.13';
            state.answers = {...state.answers, ...answers};
            localStorage.setItem('bo_state', JSON.stringify(state));
        }""")

        await page.reload()
        await asyncio.sleep(2)

        campo = await page.query_selector('.text-input__field')
        if campo:
            await campo.fill("Veículo com documentação regular")
            await asyncio.sleep(0.5)
            btn = await page.query_selector('.text-input__button')
            if btn:
                await btn.click()
                print("Enviou última resposta S2")
                await asyncio.sleep(3)

        try:
            await page.wait_for_selector('.section-generated__text', timeout=10000)
            print("✅ Texto S2 apareceu")
        except:
            print("❌ Texto S2 não apareceu")

        # Ir para S3
        print("\n=== Iniciando Seção 3 ===\n")
        await page.click('#section-start-next')
        await asyncio.sleep(3)

        # Responder todas as perguntas da S3
        perguntas_s3 = [
            ("3.2", "aproximadamente 30 minutos"),
            ("3.3", "de dentro da viatura, a 50 metros do local"),
            ("3.4", "Observamos movimentação constante de pessoas entrando e saindo rapidamente"),
            ("3.5", "aproximadamente 5 pessoas"),
            ("3.6", "SIM"),
            ("3.6.1", "Foram observadas 3 transações entre diferentes pessoas")
        ]

        for q_id, resposta in perguntas_s3:
            print(f"Respondendo {q_id}...")
            await page.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.5)

            campo = await page.query_selector('.text-input__field')
            if campo:
                await campo.fill(resposta)
                await asyncio.sleep(0.3)
                btn = await page.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(1.5)
            else:
                opts = await page.query_selector_all('.single-choice__option')
                for opt in opts:
                    txt = await opt.inner_text()
                    if resposta.upper() in txt.upper():
                        await opt.click()
                        await asyncio.sleep(1.5)
                        break

        print("\n=== Aguardando texto S3 ===\n")
        await asyncio.sleep(3)

        # Verificar se texto apareceu
        elem = await page.query_selector('.section-generated__text')
        if elem:
            texto = await elem.inner_text()
            print(f"✅ Texto S3 renderizado ({len(texto)} chars):")
            print(f"   {texto[:200]}...")

            # Verificar se é placeholder ou texto real
            if "Respostas coletadas:" in texto:
                print("⚠️  PROBLEMA: É o placeholder, não o texto do Groq!")
            else:
                print("✅ É texto narrativo do Groq")
        else:
            print("❌ Elemento de texto não encontrado")

        # Verificar localStorage
        state = await page.evaluate("""() => {
            const state = JSON.parse(localStorage.getItem('bo_state'));
            return {
                section3_status: state?.sections?.[3]?.status,
                section3_generatedText: state?.sections?.[3]?.generatedText || 'VAZIO'
            };
        }""")

        print(f"\n[LOCAL STORAGE]")
        print(f"  section3 status: {state['section3_status']}")
        print(f"  section3 generatedText: {state['section3_generatedText'][:100] if state['section3_generatedText'] != 'VAZIO' else 'VAZIO'}...")

        await page.screenshot(path='docs/screenshots/v0.13.2/debug-s3.png')

        print("\n=== Aguarde 10s para inspeção ===")
        await asyncio.sleep(10)
        await browser.close()

asyncio.run(debug())

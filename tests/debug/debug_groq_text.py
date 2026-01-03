"""
Debug: Verifica se o Groq está gerando texto
"""
import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Capturar console logs (desabilitado - problema de encoding)
        # page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))

        # Capturar requisições de rede
        async def log_request(route, request):
            if "answer" in request.url:
                print(f"\n[REQUEST] {request.method} {request.url}")
                if request.post_data:
                    print(f"[POST DATA] {request.post_data[:200]}")
            await route.continue_()

        async def log_response(response):
            if "answer" in response.url:
                print(f"\n[RESPONSE] {response.status} {response.url}")
                try:
                    body = await response.json()
                    print(f"[RESPONSE BODY] {str(body)[:500]}")
                    if "generated_text" in body:
                        print(f"[GENERATED TEXT] {body['generated_text'][:200]}")
                except:
                    pass

        await page.route("**/*", log_request)
        page.on("response", log_response)

        await page.goto('http://localhost:8000/docs/index.html')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        print("\n=== Respondendo apenas última pergunta da Seção 1 ===\n")

        # Navegar até última pergunta da S1
        perguntas = [
            ("1.1", "19/12/2025, 14h30min, quinta-feira"),
            ("1.2", "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234"),
            ("1.3", "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão"),
            ("1.4", "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região."),
            ("1.5", "SIM"),
            ("1.5.1", "Base Operacional do 16º BPM, localizada na Avenida Brasil, 1234, Bairro Centro"),
            ("1.5.2", "Não houve alterações durante o deslocamento"),
            ("1.6", "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG"),
            ("1.7", "Sim, local consta em 12 registros anteriores de tráfico"),
            ("1.8", "Área sob influência da facção Comando Vermelho"),
            ("1.9", "SIM"),
            ("1.9.1", "Escola Estadual João XXIII"),
            ("1.9.2", "Aproximadamente 300 metros")
        ]

        for q_id, resposta in perguntas:
            await page.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.3)

            campo = await page.query_selector('.text-input__field')
            if campo:
                await campo.fill(resposta)
                await asyncio.sleep(0.2)
                btn = await page.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(1)
            else:
                opts = await page.query_selector_all('.single-choice__option')
                for opt in opts:
                    txt = await opt.inner_text()
                    if resposta.upper() in txt.upper():
                        await opt.click()
                        await asyncio.sleep(1)
                        break

        print("\n=== Aguardando texto gerado ===\n")
        await asyncio.sleep(5)

        # Verificar localStorage
        state = await page.evaluate("""() => {
            const state = JSON.parse(localStorage.getItem('bo_state'));
            return {
                section1_generatedText: state?.sections?.[1]?.generatedText || 'VAZIO',
                section1_status: state?.sections?.[1]?.status
            };
        }""")

        print(f"\n[LOCAL STORAGE] section1 status: {state['section1_status']}")
        print(f"[LOCAL STORAGE] section1 generatedText: {state['section1_generatedText'][:200]}")

        # Verificar texto renderizado
        elem = await page.query_selector('.section-generated__text')
        if elem:
            texto_renderizado = await elem.inner_text()
            print(f"\n[RENDERIZADO] {len(texto_renderizado)} chars: {texto_renderizado[:200]}")
        else:
            print("\n[RENDERIZADO] Elemento não encontrado")

        await page.screenshot(path='docs/screenshots/v0.13.2/debug-groq.png')

        print("\n=== Aguarde 10s para inspeção ===")
        await asyncio.sleep(10)
        await browser.close()

asyncio.run(debug())

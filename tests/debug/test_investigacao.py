import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

S1 = {
    "1.1": "19/12/2025, 14h30min, quinta-feira",
    "1.2": "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
    "1.3": "Via 190, DDU, Patrulhamento preventivo",
    "1.4": "Ordem de serviço determinava patrulhamento. COPOM informou denúncia de veículo transportando drogas.",
    "1.5": "NÃO",
    "1.6": "Rua das Acácias, 789, Bairro Santa Rita, Contagem/MG",
    "1.7": "Sim, 12 registros anteriores de tráfico",
    "1.8": "Área sob influência da facção Comando Vermelho",
    "1.9": "SIM",
    "1.9.1": "Escola Estadual João XXIII",
    "1.9.2": "Aproximadamente 300 metros"
}

S2 = {
    "2.2": "Chevrolet Onix, placa ABC-1234, cor prata, em alta velocidade pela via principal",
    "2.3": "Veículo em alta velocidade, motorista demonstrou nervosismo ao avistar viatura policial",
}

class T:
    def __init__(self):
        self.logs = []

    def log(self, m):
        ts = datetime.now().strftime("%H:%M:%S")
        msg = f"[{ts}] {m}"
        print(msg)
        self.logs.append(msg)

    async def check_error(self, pg):
        try:
            err = await pg.query_selector('.text-input__error')
            if err and await err.is_visible():
                txt = await err.inner_text()
                self.log(f"  >>> ERRO: {txt}")
                return txt
        except:
            pass
        return None

    async def get_question(self, pg):
        try:
            msgs = await pg.query_selector_all('.chat-message--bot')
            if msgs:
                last = msgs[-1]
                txt = await last.inner_text()
                return txt.split('\n')[0]
        except:
            pass
        return "???"

    async def ans(self, pg, q, a):
        self.log(f"\n{q}: {a[:50]}...")

        qtext = await self.get_question(pg)
        self.log(f"  Atual: {qtext[:50]}...")

        try:
            await pg.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.5)

            inp = await pg.query_selector('.text-input__field')
            if inp:
                self.log(f"  Tipo: TEXTO")
                await inp.fill(a)
                await asyncio.sleep(0.3)

                err = await self.check_error(pg)
                if err:
                    await pg.screenshot(path=f'docs/screenshots/v0.13.2/err-{q.replace(".", "-")}.png')
                    return False

                btn = await pg.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(1.5)

                    err = await self.check_error(pg)
                    if err:
                        await pg.screenshot(path=f'docs/screenshots/v0.13.2/err-{q.replace(".", "-")}.png')
                        return False

                    self.log(f"  OK")
                    return True

            opts = await pg.query_selector_all('.single-choice__option')
            if opts:
                self.log(f"  Tipo: ESCOLHA ({len(opts)} opts)")
                for opt in opts:
                    txt = await opt.inner_text()
                    if a.upper() in txt.upper():
                        await opt.click()
                        await asyncio.sleep(1.5)
                        self.log(f"  OK")
                        return True

            self.log(f"  FALHA")
            return False
        except Exception as e:
            self.log(f"  ERRO: {str(e)[:60]}")
            return False

    async def run(self):
        async with async_playwright() as p:
            br = await p.chromium.launch(headless=False)
            pg = await br.new_page()

            try:
                self.log("=== TESTE INVESTIGACAO ===")

                await pg.goto('http://localhost:8000/docs/index.html')
                await pg.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                # S1
                self.log("\n>>> SECAO 1")
                for q, a in S1.items():
                    if not await self.ans(pg, q, a):
                        self.log(f"ABORT S1 {q}")
                        return

                self.log("\nAguardando texto...")
                try:
                    await pg.wait_for_selector('.section-generated__text', timeout=60000)
                    self.log("OK Texto S1")
                except:
                    self.log("TIMEOUT S1")

                await pg.screenshot(path='docs/screenshots/v0.13.2/inv-s1.png')

                # S2
                self.log("\n>>> SECAO 2")
                await pg.click('#section-start-next')
                await asyncio.sleep(3)

                await pg.screenshot(path='docs/screenshots/v0.13.2/inv-s2-start.png')

                for q, a in S2.items():
                    if not await self.ans(pg, q, a):
                        self.log(f"\nABORT S2 {q}")
                        await pg.screenshot(path='docs/screenshots/v0.13.2/inv-s2-fail.png')

                        html = await pg.content()
                        with open('debug_s2.html', 'w', encoding='utf-8') as f:
                            f.write(html)
                        self.log("HTML: debug_s2.html")
                        return

                self.log("\nSUCESSO")

            finally:
                with open('inv_test.log', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.logs))

                await asyncio.sleep(5)
                await br.close()

asyncio.run(T().run())

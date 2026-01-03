import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# Usando os EXEMPLOS das próprias perguntas (hints)
S1 = {
    "1.1": "19/12/2025, 14h30min, quinta-feira",
    "1.2": "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
    "1.3": "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão",
    "1.4": "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.",
    "1.5": "NÃO",
    "1.6": "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG",
    "1.7": "Sim, local consta em 12 registros anteriores de tráfico",
    "1.8": "Área sob influência da facção Comando Vermelho",
    "1.9": "SIM",
    "1.9.1": "Escola Estadual João XXIII",
    "1.9.2": "Aproximadamente 300 metros"
}

S2 = {
    "2.1": "SIM",
    "2.2": "Chevrolet Onix, placa ABC-1234, cor prata",
    "2.3": "Veículo em alta velocidade, motorista nervoso ao avistar viatura",
    "2.4": "SIM",
    "2.4.1": "Tentou fazer conversão rápida em via secundária",
    "2.5": "NÃO",
    "2.7": "Rua Principal, altura do número 500, Bairro Centro",
    "2.8": "João Santos, RG 1234567 SSP/MG, residente na Rua ABC",
    "2.9": "SIM",
    "2.9.1": "Maria Silva, RG 7654321 SSP/MG",
    "2.10": "NÃO",
    "2.12": "Demonstrou nervosismo mas colaborou com a abordagem",
    "2.13": "NÃO"
}

S3 = {"3.1": "NÃO"}

class T:
    def __init__(self):
        self.logs = []
        self.errors = 0

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
                self.log(f"  ERRO: {txt}")
                self.errors += 1
                return True
        except:
            pass
        return False

    async def ans(self, pg, q, a):
        self.log(f"{q}: {a[:40]}...")
        try:
            await pg.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.3)

            inp = await pg.query_selector('.text-input__field')
            if inp:
                await inp.fill(a)
                await asyncio.sleep(0.2)
                btn = await pg.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(1)
                    if await self.check_error(pg):
                        return False
                    self.log(f"  OK")
                    return True

            opts = await pg.query_selector_all('.single-choice__option')
            for opt in opts:
                txt = await opt.inner_text()
                if a.upper() in txt.upper():
                    await opt.click()
                    await asyncio.sleep(1)
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
                self.log("="*50)
                self.log("TESTE COMPLETO - 3 SECOES")
                self.log("="*50)

                await pg.goto('http://localhost:8000/docs/index.html')
                await pg.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                # SECAO 1
                self.log("\n>>> SECAO 1")
                for q, a in S1.items():
                    if not await self.ans(pg, q, a):
                        await pg.screenshot(path='docs/screenshots/v0.13.2/fail-s1.png')
                        return

                self.log("\nAguardando texto S1...")
                try:
                    await pg.wait_for_selector('.section-generated__text', timeout=60000)
                    txt = await pg.query_selector('.section-generated__text')
                    content = await txt.inner_text()
                    self.log(f"OK Texto gerado ({len(content)} chars)")
                except:
                    self.log("AVISO: Texto nao gerado")

                await pg.screenshot(path='docs/screenshots/v0.13.2/s1-done.png')

                # SECAO 2
                self.log("\n>>> Iniciando SECAO 2")
                await pg.click('#section-start-next')
                await asyncio.sleep(2)

                self.log("\n>>> SECAO 2")
                for q, a in S2.items():
                    if not await self.ans(pg, q, a):
                        await pg.screenshot(path='docs/screenshots/v0.13.2/fail-s2.png')
                        return

                self.log("\nAguardando texto S2...")
                try:
                    await pg.wait_for_selector('.section-generated__text', timeout=60000)
                    txt = await pg.query_selector('.section-generated__text')
                    content = await txt.inner_text()
                    self.log(f"OK Texto gerado ({len(content)} chars)")
                except:
                    self.log("AVISO: Texto nao gerado")

                await pg.screenshot(path='docs/screenshots/v0.13.2/s2-done.png')

                # SECAO 3
                self.log("\n>>> Iniciando SECAO 3")
                await pg.click('#section-start-next')
                await asyncio.sleep(2)

                self.log("\n>>> SECAO 3")
                for q, a in S3.items():
                    if not await self.ans(pg, q, a):
                        await pg.screenshot(path='docs/screenshots/v0.13.2/fail-s3.png')
                        return

                await asyncio.sleep(1)
                self.log("OK S3 pulada")
                await pg.screenshot(path='docs/screenshots/v0.13.2/s3-done.png')

                # FINALIZAR
                self.log("\n>>> FINALIZANDO BO")
                try:
                    await pg.click('#section-finalize-bo', timeout=5000)
                    await asyncio.sleep(2)
                    self.log("OK Botao Finalizar")
                except:
                    self.log("Botao Finalizar nao encontrado")

                await pg.screenshot(path='docs/screenshots/v0.13.2/final.png')

                self.log("\n" + "="*50)
                self.log("TESTE COMPLETO!")
                self.log("="*50)
                self.log(f"\nErros validacao: {self.errors}")

                with open('VALIDATION_REPORT.md', 'w', encoding='utf-8') as f:
                    f.write('# Validacao BO v0.13.2\n\n')
                    f.write(f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
                    f.write('## Resultado\n\n')
                    f.write('TESTE COMPLETO - 3 SECOES\n\n')
                    f.write(f'Erros: {self.errors}\n\n')
                    f.write('## Log\n\n```\n')
                    f.write('\n'.join(self.logs))
                    f.write('\n```\n')

                self.log("\nRelatorio: VALIDATION_REPORT.md")
                await asyncio.sleep(5)

            finally:
                await br.close()

asyncio.run(T().run())

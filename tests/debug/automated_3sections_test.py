"""
Teste automatizado completo - Seções 1, 2 e 3
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

SECTION1_ANSWERS = {
    "1.1": "02/01/2026, 23h15, sexta-feira",
    "1.2": "Sargento João Silva, Cabo Pedro Almeida, viatura 2234",
    "1.3": "Via 190, patrulhamento preventivo",
    "1.4": "COPOM informou denúncia anônima de veículo",
    "1.5": "NÃO",
    "1.6": "Rua das Acácias, 789, Bairro Santa Rita",
    "1.7": "Sim, 12 registros anteriores",
    "1.8": "Comando Vermelho",
    "1.9": "SIM",
    "1.9.1": "Escola Estadual João XXIII",
    "1.9.2": "300 metros"
}

SECTION2_ANSWERS = {
    "2.1": "SIM",
    "2.2": "Onix placa ABC1234 prata",
    "2.3": "Alta velocidade nervosismo",
    "2.4": "SIM",
    "2.4.1": "Acelerou e tentou fugir",
    "2.5": "NÃO",
    "2.7": "Bairro Santa Rita",
    "2.8": "João Santos RG 1234567",
    "2.9": "SIM",
    "2.9.1": "Maria Silva RG 7654321",
    "2.10": "NÃO",
    "2.12": "Nervoso mas colaborou",
    "2.13": "NÃO"
}

SECTION3_ANSWERS = {
    "3.1": "NÃO",
}

class Tester:
    def __init__(self):
        self.logs = []
    
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")
        self.logs.append(f"[{ts}] {msg}")
    
    async def answer(self, page, qid, ans):
        self.log(f"Respondendo {qid}: {ans}")
        try:
            await page.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.5)
            
            # Texto
            inp = await page.query_selector('.text-input__field')
            if inp:
                await inp.fill(ans)
                await asyncio.sleep(0.3)
                btn = await page.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(1)
                    self.log(f"OK {qid}")
                    return True
            
            # Escolha
            opts = await page.query_selector_all('.single-choice__option')
            for opt in opts:
                txt = await opt.inner_text()
                if ans.upper() in txt.upper():
                    await opt.click()
                    await asyncio.sleep(1)
                    self.log(f"OK {qid}")
                    return True
            
            self.log(f"FALHA {qid}")
            return False
        except Exception as e:
            self.log(f"ERRO {qid}: {e}")
            return False
    
    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                self.log("Carregando pagina...")
                await page.goto('http://localhost:8000/docs/index.html')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # Seção 1
                self.log("=== SECAO 1 ===")
                for qid, ans in SECTION1_ANSWERS.items():
                    if not await self.answer(page, qid, ans):
                        return
                
                self.log("Aguardando texto gerado...")
                await page.wait_for_selector('.section-generated__text', timeout=60000)
                await asyncio.sleep(1)
                await page.screenshot(path='docs/screenshots/v0.13.2/test-s1-done.png')
                
                # Iniciar seção 2
                self.log("Iniciando Secao 2...")
                await page.click('#section-start-next')
                await asyncio.sleep(2)
                
                # Seção 2
                self.log("=== SECAO 2 ===")
                for qid, ans in SECTION2_ANSWERS.items():
                    if not await self.answer(page, qid, ans):
                        return
                
                self.log("Aguardando texto gerado...")
                await page.wait_for_selector('.section-generated__text', timeout=60000)
                await asyncio.sleep(1)
                await page.screenshot(path='docs/screenshots/v0.13.2/test-s2-done.png')
                
                # Iniciar seção 3
                self.log("Iniciando Secao 3...")
                await page.click('#section-start-next')
                await asyncio.sleep(2)
                
                # Seção 3
                self.log("=== SECAO 3 ===")
                for qid, ans in SECTION3_ANSWERS.items():
                    if not await self.answer(page, qid, ans):
                        return
                
                await asyncio.sleep(1)
                await page.screenshot(path='docs/screenshots/v0.13.2/test-s3-done.png')
                
                # Finalizar
                self.log("Finalizando BO...")
                try:
                    await page.click('#section-finalize-bo', timeout=5000)
                    await asyncio.sleep(2)
                except:
                    self.log("Botao Finalizar nao encontrado")
                
                await page.screenshot(path='docs/screenshots/v0.13.2/test-final.png')
                
                self.log("=== TESTE COMPLETO ===")
                
                # Salvar log
                with open('test_session.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.logs))
                
                await asyncio.sleep(5)
                
            finally:
                await browser.close()

if __name__ == "__main__":
    t = Tester()
    asyncio.run(t.run())

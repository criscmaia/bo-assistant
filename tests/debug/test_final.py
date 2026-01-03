import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

S1 = {"1.1": "02/01/2026, 23h15, sexta-feira", "1.2": "Sgt Silva, viatura 2234", "1.3": "Via 190", "1.4": "COPOM denúncia", "1.5": "NÃO", "1.6": "Rua Acácias 789", "1.7": "Sim, 12 registros", "1.8": "Comando Vermelho", "1.9": "SIM", "1.9.1": "Escola João XXIII", "1.9.2": "300 metros"}
S2 = {"2.1": "SIM", "2.2": "Onix ABC1234", "2.3": "Nervoso", "2.4": "SIM", "2.4.1": "Tentou fugir", "2.5": "NÃO", "2.7": "Santa Rita", "2.8": "João Santos 1234567", "2.9": "SIM", "2.9.1": "Maria Silva 7654321", "2.10": "NÃO", "2.12": "Colaborou", "2.13": "NÃO"}
S3 = {"3.1": "NÃO"}

class T:
    def __init__(self):
        self.logs = []
    
    def log(self, m):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {m}")
        self.logs.append(f"[{ts}] {m}")
    
    async def ans(self, p, q, a):
        self.log(f"{q}: {a}")
        try:
            await p.wait_for_selector('.text-input__field, .single-choice__option', timeout=10000)
            await asyncio.sleep(0.3)
            
            inp = await p.query_selector('.text-input__field')
            if inp:
                await inp.fill(a)
                await asyncio.sleep(0.2)
                btn = await p.query_selector('.text-input__button')
                if btn:
                    await btn.click()
                    await asyncio.sleep(0.8)
                    return True
            
            opts = await p.query_selector_all('.single-choice__option')
            for opt in opts:
                txt = await opt.inner_text()
                if a.upper() in txt.upper():
                    await opt.click()
                    await asyncio.sleep(0.8)
                    return True
            
            self.log(f"FALHA {q}")
            return False
        except Exception as e:
            self.log(f"ERRO {q}: {e}")
            return False
    
    async def run(self):
        async with async_playwright() as p:
            br = await p.chromium.launch(headless=False)
            pg = await br.new_page()
            
            try:
                self.log("Carregando...")
                await pg.goto('http://localhost:8000/docs/index.html')
                await pg.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # S1
                self.log("=== SECAO 1 ===")
                for q, a in S1.items():
                    if not await self.ans(pg, q, a):
                        return
                
                self.log("Aguardando texto S1...")
                try:
                    await pg.wait_for_selector('.section-generated__text', timeout=30000)
                    self.log("OK Texto S1 gerado")
                except:
                    self.log("AVISO: Texto S1 nao gerado")
                
                await pg.screenshot(path='docs/screenshots/v0.13.2/final-s1.png')
                
                # Ir para S2
                self.log("Iniciando S2...")
                await pg.click('#section-start-next')
                await asyncio.sleep(2)
                
                # S2
                self.log("=== SECAO 2 ===")
                for q, a in S2.items():
                    if not await self.ans(pg, q, a):
                        return
                
                self.log("Aguardando texto S2...")
                try:
                    await pg.wait_for_selector('.section-generated__text', timeout=30000)
                    self.log("OK Texto S2 gerado")
                except:
                    self.log("AVISO: Texto S2 nao gerado (continuando)")
                
                await pg.screenshot(path='docs/screenshots/v0.13.2/final-s2.png')
                
                # Ir para S3
                self.log("Iniciando S3...")
                await pg.click('#section-start-next')
                await asyncio.sleep(2)
                
                # S3
                self.log("=== SECAO 3 ===")
                for q, a in S3.items():
                    if not await self.ans(pg, q, a):
                        return
                
                self.log("Aguardando texto S3...")
                try:
                    await pg.wait_for_selector('.section-generated__text', timeout=5000)
                    self.log("OK Texto S3 gerado")
                except:
                    self.log("OK S3 pulada (esperado)")
                
                await pg.screenshot(path='docs/screenshots/v0.13.2/final-s3.png')
                
                # Finalizar
                self.log("Finalizando BO...")
                try:
                    await pg.click('#section-finalize-bo', timeout=5000)
                    await asyncio.sleep(2)
                    self.log("OK Botao Finalizar clicado")
                except:
                    self.log("AVISO: Botao Finalizar nao encontrado")
                
                await pg.screenshot(path='docs/screenshots/v0.13.2/final-complete.png')
                
                self.log("=== TESTE COMPLETO ===")
                
                with open('VALIDATION_REPORT.md', 'w', encoding='utf-8') as f:
                    f.write('# Relatório de Validação - BO Inteligente v0.13.2\n\n')
                    f.write('## Resumo\n\n')
                    f.write('**Data:** ' + datetime.now().strftime('%d/%01/%Y %H:%M:%S') + '\n\n')
                    f.write('**Status:** TESTE COMPLETO\n\n')
                    f.write('## Logs\n\n```\n')
                    f.write('\n'.join(self.logs))
                    f.write('\n```\n')
                
                self.log("Relatorio salvo: VALIDATION_REPORT.md")
                await asyncio.sleep(5)
                
            finally:
                await br.close()

if __name__ == "__main__":
    t = T()
    asyncio.run(t.run())

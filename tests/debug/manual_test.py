"""
Manual test - Opens browser and waits for user to test manually
"""
import asyncio
from playwright.async_api import async_playwright

async def manual_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        page.on('console', lambda msg: print(f"[{msg.type}] {msg.text}"))
        page.on('pageerror', lambda exc: print(f"[ERROR] {exc}"))

        await page.goto('http://localhost:8000/docs/index.html')
        await page.wait_for_load_state('networkidle')

        print("\n✅ Aplicação carregada!")
        print("📝 A página está aberta no navegador.")
        print("🧪 Teste manualmente:")
        print("   1. Verifique que a pergunta 1.1 aparece")
        print("   2. Digite uma resposta e clique em 'Enviar'")
        print("   3. Verifique que a próxima pergunta aparece")
        print("   4. Continue respondendo para testar o fluxo")
        print("\n⏸️  Pressione Ctrl+C para fechar quando terminar.\n")

        try:
            # Manter aberto
            await asyncio.sleep(3600)  # 1 hora
        except KeyboardInterrupt:
            print("\n✅ Teste manual encerrado.")

        await browser.close()

asyncio.run(manual_test())

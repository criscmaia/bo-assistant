import asyncio
from playwright.async_api import async_playwright
import json

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        logs = []
        errors = []

        page.on('console', lambda msg: logs.append({'type': msg.type, 'text': msg.text}))
        page.on('pageerror', lambda exc: errors.append(str(exc)))

        await page.goto('http://localhost:8000/docs/index.html')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)

        state = await page.evaluate('''() => ({
            header: document.querySelector('header') !== null,
            progressbar: document.querySelector('#progress-bar') !== null,
            section_container: document.querySelector('#section-container') !== null,
            chat: document.querySelector('.section-chat') !== null,
            input: document.querySelector('#user-input') !== null,
            SECTIONS_DATA: typeof window.SECTIONS_DATA !== 'undefined',
            ACTIVE_SECTIONS_COUNT: window.ACTIVE_SECTIONS_COUNT,
            app: typeof window.app !== 'undefined',
            progress_items: document.querySelectorAll('.progress-item').length,
            section_html: document.querySelector('#section-container')?.innerHTML?.substring(0, 1000),
        })''')

        result = {'state': state, 'console_logs': logs, 'errors': errors}

        with open('c:/AI/bo-assistant/debug_info.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        with open('c:/AI/bo-assistant/debug_info.txt', 'w', encoding='utf-8') as f:
            f.write("STATE:\n")
            for k, v in state.items():
                f.write(f"  {k}: {v}\n")
            f.write(f"\nCONSOLE LOGS ({len(logs)}):\n")
            for log in logs:
                f.write(f"  [{log['type']}] {log['text']}\n")
            f.write(f"\nERRORS ({len(errors)}):\n")
            for err in errors:
                f.write(f"  {err}\n")

        await asyncio.sleep(5)
        await browser.close()

asyncio.run(capture())

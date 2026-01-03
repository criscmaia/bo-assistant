import asyncio
from playwright.async_api import async_playwright
import json

async def debug_section():
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

        # Check detailed state
        detailed = await page.evaluate('''() => {
            const app = window.app;
            const sectionContainer = window.sectionContainer;

            return {
                app_exists: typeof app !== 'undefined',
                sectionContainer_exists: typeof sectionContainer !== 'undefined',
                sectionData_set: sectionContainer ? sectionContainer.sectionData !== null : false,
                state: sectionContainer ? sectionContainer.state : null,
                messages_count: sectionContainer ? sectionContainer.messages.length : 0,
                currentQuestionIndex: sectionContainer ? sectionContainer.currentQuestionIndex : null,
                isReadOnly: sectionContainer ? sectionContainer.isReadOnly : null,
                input_area_html: document.querySelector('#section-input-area')?.innerHTML || 'NOT FOUND',
                section_container_html_length: document.querySelector('#section-container')?.innerHTML?.length || 0,
            };
        }''')

        print('DETAILED STATE:')
        print(json.dumps(detailed, indent=2))

        print('\nCONSOLE LOGS (last 10):')
        for log in logs[-10:]:
            print(f"  [{log['type']}] {log['text']}")

        await browser.close()

asyncio.run(debug_section())

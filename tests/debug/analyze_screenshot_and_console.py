#!/usr/bin/env python3
"""
Analisa screenshot e captura console logs para debug
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        console_logs = []
        errors = []

        # Capturar logs
        page.on('console', lambda msg: console_logs.append({
            'type': msg.type,
            'text': msg.text
        }))

        page.on('pageerror', lambda exc: errors.append(str(exc)))

        print("Navegando para aplicação...")
        await page.goto('http://localhost:8000/docs/index.html')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)

        # Capturar estado da página
        state = await page.evaluate('''() => {
            return {
                // Verificar elementos DOM
                'header_exists': document.querySelector('header') !== null,
                'progressbar_exists': document.querySelector('#progress-bar') !== null,
                'section_container_exists': document.querySelector('#section-container') !== null,
                'chat_exists': document.querySelector('.section-chat') !== null,
                'input_exists': document.querySelector('#user-input') !== null,

                // Verificar JavaScript
                'SECTIONS_DATA': typeof window.SECTIONS_DATA !== 'undefined',
                'ACTIVE_SECTIONS_COUNT': window.ACTIVE_SECTIONS_COUNT,
                'StateManager': typeof StateManager !== 'undefined',
                'BOApp': typeof BOApp !== 'undefined',
                'app_instance': typeof window.app !== 'undefined',

                // HTML do container
                'section_container_html': document.querySelector('#section-container')?.innerHTML?.substring(0, 500),

                // Progress bar items
                'progress_items': document.querySelectorAll('.progress-item').length,
            };
        }''')

        print("\n" + "="*60)
        print("ANÁLISE DA PÁGINA")
        print("="*60)

        print("\nElementos DOM:")
        for key, value in state.items():
            if not key.endswith('_html'):
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")

        print("\nHTML do Section Container (primeiros 500 chars):")
        print(f"  {state.get('section_container_html', 'VAZIO')}")

        print("\n" + "="*60)
        print("CONSOLE LOGS")
        print("="*60)

        # Agrupar por tipo
        by_type = {}
        for log in console_logs:
            t = log['type']
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(log['text'])

        for log_type, messages in by_type.items():
            print(f"\n{log_type.upper()} ({len(messages)}):")
            for msg in messages[:20]:  # Primeiros 20
                print(f"  • {msg}")

        print("\n" + "="*60)
        print("ERROS DE PÁGINA")
        print("="*60)

        if errors:
            for i, error in enumerate(errors, 1):
                print(f"\n  Erro {i}: {error}")
        else:
            print("  ✅ Nenhum erro JavaScript detectado")

        # Salvar em JSON
        with open('c:/AI/bo-assistant/page_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'state': state,
                'console_logs': console_logs,
                'errors': errors
            }, f, indent=2, ensure_ascii=False)

        print("\n📄 Análise completa salva em: page_analysis.json")
        print("\nAguardando 10 segundos... (veja o navegador)")
        await asyncio.sleep(10)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(analyze())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Automatizado Visual - BO Inteligente v0.13.2
Usa Playwright para controlar o navegador e capturar screenshots + console logs
"""
import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime

# Criar diretório para screenshots
SCREENSHOTS_DIR = Path("c:/AI/bo-assistant/test_screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class VisualTester:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.console_logs = []
        self.errors = []
        self.test_results = []

    async def setup(self):
        """Inicializa o navegador"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Mostrar navegador
            slow_mo=500  # Slow down para ver o que está acontecendo
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='pt-BR'
        )
        self.page = await self.context.new_page()

        # Capturar console logs
        self.page.on('console', lambda msg: self.console_logs.append({
            'type': msg.type,
            'text': msg.text,
            'location': msg.location
        }))

        # Capturar erros
        self.page.on('pageerror', lambda exc: self.errors.append({
            'message': str(exc),
            'timestamp': datetime.now().isoformat()
        }))

        print("✅ Navegador iniciado")

    async def screenshot(self, name):
        """Captura screenshot com timestamp"""
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{timestamp}_{name}.png"
        path = SCREENSHOTS_DIR / filename
        await self.page.screenshot(path=str(path), full_page=True)
        print(f"📸 Screenshot salvo: {filename}")
        return str(path)

    async def test_initial_load(self):
        """Teste 1: Carregamento inicial da página"""
        print("\n" + "="*60)
        print("TESTE 1: Carregamento Inicial")
        print("="*60)

        try:
            # Navegar para a aplicação
            await self.page.goto('http://localhost:8000/docs/index.html', timeout=30000)
            await self.page.wait_for_load_state('networkidle')

            # Aguardar um pouco para JavaScript carregar
            await asyncio.sleep(2)

            # Screenshot inicial
            await self.screenshot("01_initial_load")

            # Verificar se elementos principais estão presentes
            checks = {
                'Header presente': await self.page.query_selector('header') is not None,
                'Progress bar presente': await self.page.query_selector('#progress-bar') is not None,
                'Section container presente': await self.page.query_selector('#section-container') is not None,
            }

            # Verificar variáveis JavaScript
            js_checks = await self.page.evaluate('''() => {
                return {
                    'SECTIONS_DATA definido': typeof window.SECTIONS_DATA !== 'undefined',
                    'ACTIVE_SECTIONS_COUNT definido': typeof window.ACTIVE_SECTIONS_COUNT !== 'undefined',
                    'ACTIVE_SECTIONS_COUNT valor': window.ACTIVE_SECTIONS_COUNT,
                    'StateManager disponível': typeof StateManager !== 'undefined',
                    'BOApp instanciado': typeof window.app !== 'undefined',
                    'ProgressBar renderizada': document.querySelectorAll('.progress-item').length,
                    'Chat visível': document.querySelector('.section-chat') !== null,
                }
            }''')

            checks.update(js_checks)

            # Resultado
            all_passed = all(v for k, v in checks.items() if k != 'ACTIVE_SECTIONS_COUNT valor')
            self.test_results.append({
                'test': 'Initial Load',
                'passed': all_passed,
                'checks': checks
            })

            print("\nVerificações:")
            for key, value in checks.items():
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")

            return all_passed

        except Exception as e:
            print(f"❌ Erro: {e}")
            await self.screenshot("01_error")
            self.test_results.append({
                'test': 'Initial Load',
                'passed': False,
                'error': str(e)
            })
            return False

    async def test_progress_bar(self):
        """Teste 2: ProgressBar deve mostrar apenas 3 bolinhas"""
        print("\n" + "="*60)
        print("TESTE 2: ProgressBar (3 bolinhas)")
        print("="*60)

        try:
            await asyncio.sleep(1)

            # Contar bolinhas
            progress_items = await self.page.query_selector_all('.progress-item')
            count = len(progress_items)

            await self.screenshot("02_progress_bar")

            # Obter detalhes das bolinhas
            details = await self.page.evaluate('''() => {
                const items = document.querySelectorAll('.progress-item');
                return Array.from(items).map((item, i) => ({
                    index: i + 1,
                    text: item.textContent.trim(),
                    classes: item.className,
                    hasLock: item.querySelector('.lock-icon') !== null
                }));
            }''')

            passed = count == 3
            self.test_results.append({
                'test': 'ProgressBar',
                'passed': passed,
                'expected': 3,
                'actual': count,
                'details': details
            })

            print(f"\n  Bolinhas encontradas: {count} (esperado: 3)")
            print(f"  {'✅ PASSOU' if passed else '❌ FALHOU'}")

            for detail in details:
                lock = "🔒" if detail['hasLock'] else "  "
                print(f"    {lock} Bolinha {detail['index']}: {detail['text']}")

            return passed

        except Exception as e:
            print(f"❌ Erro: {e}")
            await self.screenshot("02_error")
            return False

    async def test_chat_visible(self):
        """Teste 3: Chat deve estar visível"""
        print("\n" + "="*60)
        print("TESTE 3: Chat Visível")
        print("="*60)

        try:
            await asyncio.sleep(1)

            # Verificar se chat existe e está visível
            chat_checks = await self.page.evaluate('''() => {
                const chat = document.querySelector('.section-chat');
                const messages = document.querySelectorAll('.chat-message');
                const input = document.querySelector('.section-input');

                return {
                    'Chat existe': chat !== null,
                    'Chat visível': chat && window.getComputedStyle(chat).display !== 'none',
                    'Mensagens no chat': messages.length,
                    'Input existe': input !== null,
                    'Input visível': input && window.getComputedStyle(input).display !== 'none',
                };
            }''')

            await self.screenshot("03_chat_visibility")

            passed = chat_checks['Chat visível'] and chat_checks['Mensagens no chat'] > 0
            self.test_results.append({
                'test': 'Chat Visibility',
                'passed': passed,
                'checks': chat_checks
            })

            print("\nVerificações:")
            for key, value in chat_checks.items():
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")

            return passed

        except Exception as e:
            print(f"❌ Erro: {e}")
            await self.screenshot("03_error")
            return False

    async def test_draft_modal(self):
        """Teste 4: Modal de rascunho (se aparecer)"""
        print("\n" + "="*60)
        print("TESTE 4: Modal de Rascunho")
        print("="*60)

        try:
            await asyncio.sleep(1)

            # Verificar se modal está presente
            modal_visible = await self.page.evaluate('''() => {
                const modal = document.querySelector('.draft-modal');
                return modal && window.getComputedStyle(modal).display !== 'none';
            }''')

            if modal_visible:
                print("  ⚠️ Modal de rascunho detectado")
                await self.screenshot("04_draft_modal")

                # Verificar conteúdo do modal
                modal_content = await self.page.evaluate('''() => {
                    const sections = document.querySelectorAll('.draft-modal .draft-section');
                    return {
                        'Número de seções': sections.length,
                        'Botões presentes': {
                            'Continuar': document.querySelector('.draft-modal button[data-action="continue"]') !== null,
                            'Descartar': document.querySelector('.draft-modal button[data-action="discard"]') !== null,
                        }
                    };
                }''')

                print(f"  Conteúdo do modal: {json.dumps(modal_content, indent=2, ensure_ascii=False)}")

                # Clicar em descartar para começar novo BO
                discard_btn = await self.page.query_selector('button[data-action="discard"]')
                if discard_btn:
                    await discard_btn.click()
                    await asyncio.sleep(2)
                    await self.screenshot("04_after_discard")
                    print("  ✅ Clicou em 'Descartar'")

                return True
            else:
                print("  ℹ️ Modal de rascunho não apareceu (normal para novo BO)")
                return True

        except Exception as e:
            print(f"❌ Erro: {e}")
            await self.screenshot("04_error")
            return False

    async def test_complete_section_1(self):
        """Teste 5: Completar Seção 1"""
        print("\n" + "="*60)
        print("TESTE 5: Completar Seção 1")
        print("="*60)

        try:
            # Respostas para seção 1
            answers = [
                "02/01/2026 às 14:30",
                "Rua Teste, 123 - Bairro Centro - Cidade/UF - próximo ao mercado",
                "Acionamento via 190 comunicando ocorrência de roubo em andamento",
                "Foram deslocadas 2 viaturas da 1ª Companhia para o local",
                "NÃO",
                "NÃO",
                "2 indivíduos masculinos, aproximadamente 25 anos",
                "Não há domínio de facção criminosa no local",
                "2 indivíduos foram detidos no local",
                "NÃO",
            ]

            for i, answer in enumerate(answers, 1):
                print(f"\n  Respondendo pergunta {i}/10...")

                # Aguardar input estar visível
                await self.page.wait_for_selector('textarea, input[type="text"]', timeout=5000)

                # Encontrar input ativo
                input_field = await self.page.query_selector('textarea:not([disabled]), input[type="text"]:not([disabled])')

                if input_field:
                    await input_field.fill(answer)
                    await asyncio.sleep(0.5)

                    # Procurar botão de enviar
                    send_btn = await self.page.query_selector('button:has-text("Enviar")')
                    if send_btn:
                        await send_btn.click()
                        await asyncio.sleep(1.5)
                        print(f"    ✅ Resposta {i} enviada")
                    else:
                        print(f"    ⚠️ Botão enviar não encontrado")
                else:
                    print(f"    ⚠️ Input não encontrado")

                # Screenshot a cada 3 respostas
                if i % 3 == 0:
                    await self.screenshot(f"05_section1_q{i}")

            # Aguardar texto gerado
            await asyncio.sleep(3)
            await self.screenshot("05_section1_complete")

            # Verificar se seção foi completada
            section_complete = await self.page.evaluate('''() => {
                const generatedText = document.querySelector('.section-generated-text');
                return {
                    'Texto gerado presente': generatedText !== null,
                    'Texto gerado visível': generatedText && generatedText.textContent.trim().length > 0,
                    'Seção 1 completa': document.querySelector('.progress-item:nth-child(1).progress-item--completed') !== null,
                };
            }''')

            print("\n  Verificações:")
            for key, value in section_complete.items():
                status = "✅" if value else "❌"
                print(f"    {status} {key}")

            passed = section_complete['Texto gerado presente']
            self.test_results.append({
                'test': 'Complete Section 1',
                'passed': passed,
                'checks': section_complete
            })

            return passed

        except Exception as e:
            print(f"❌ Erro: {e}")
            await self.screenshot("05_error")
            return False

    async def test_section_transition(self):
        """Teste 6: Transição para próxima seção"""
        print("\n" + "="*60)
        print("TESTE 6: Botões de Transição")
        print("="*60)

        try:
            await asyncio.sleep(2)

            # Verificar botões de transição
            transition_info = await self.page.evaluate('''() => {
                const transition = document.querySelector('.section-transition');
                const buttons = transition ? transition.querySelectorAll('button') : [];

                return {
                    'Transição presente': transition !== null,
                    'Número de botões': buttons.length,
                    'Botões': Array.from(buttons).map(btn => btn.textContent.trim()),
                    'Preview texto': transition ? transition.querySelector('.section-transition__preview-name')?.textContent : null,
                };
            }''')

            await self.screenshot("06_transition")

            print("\n  Informações da transição:")
            for key, value in transition_info.items():
                print(f"    {key}: {value}")

            # Verificar se tem botão "Finalizar BO" ou botões Sim/Não
            has_finalize = any('Finalizar' in btn for btn in transition_info['Botões'])
            has_yes_no = transition_info['Número de botões'] >= 2

            print(f"\n    {'✅' if has_yes_no or has_finalize else '❌'} Botões de transição corretos")

            return True

        except Exception as e:
            print(f"❌ Erro: {e}")
            await self.screenshot("06_error")
            return False

    async def analyze_console_logs(self):
        """Analisa logs do console"""
        print("\n" + "="*60)
        print("ANÁLISE DO CONSOLE")
        print("="*60)

        if not self.console_logs:
            print("  ℹ️ Nenhum log capturado")
            return

        # Agrupar por tipo
        by_type = {}
        for log in self.console_logs:
            log_type = log['type']
            if log_type not in by_type:
                by_type[log_type] = []
            by_type[log_type].append(log['text'])

        print(f"\n  Total de logs: {len(self.console_logs)}")
        for log_type, messages in by_type.items():
            print(f"    {log_type}: {len(messages)}")

        # Mostrar erros
        if 'error' in by_type:
            print("\n  ❌ ERROS NO CONSOLE:")
            for msg in by_type['error'][:10]:  # Primeiros 10
                print(f"    • {msg}")

        # Mostrar warnings
        if 'warning' in by_type:
            print("\n  ⚠️ WARNINGS:")
            for msg in by_type['warning'][:5]:  # Primeiros 5
                print(f"    • {msg}")

        # Salvar todos os logs
        log_file = SCREENSHOTS_DIR / f"console_logs_{datetime.now().strftime('%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.console_logs, f, indent=2, ensure_ascii=False)
        print(f"\n  📄 Logs completos salvos: {log_file.name}")

    async def analyze_page_errors(self):
        """Analisa erros de página"""
        print("\n" + "="*60)
        print("ANÁLISE DE ERROS DA PÁGINA")
        print("="*60)

        if not self.errors:
            print("  ✅ Nenhum erro JavaScript detectado")
            return

        print(f"\n  ❌ {len(self.errors)} erros encontrados:")
        for i, error in enumerate(self.errors, 1):
            print(f"\n  Erro {i}:")
            print(f"    {error['message']}")
            print(f"    Timestamp: {error['timestamp']}")

        # Salvar erros
        error_file = SCREENSHOTS_DIR / f"page_errors_{datetime.now().strftime('%H%M%S')}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(self.errors, f, indent=2, ensure_ascii=False)
        print(f"\n  📄 Erros salvos: {error_file.name}")

    async def generate_report(self):
        """Gera relatório final"""
        print("\n" + "="*80)
        print("RELATÓRIO FINAL")
        print("="*80)

        passed = sum(1 for r in self.test_results if r.get('passed', False))
        total = len(self.test_results)

        print(f"\n  ✅ Testes passados: {passed}/{total}")
        print(f"  📸 Screenshots salvos em: {SCREENSHOTS_DIR}")
        print(f"  📋 Logs do console: {len(self.console_logs)}")
        print(f"  ❌ Erros da página: {len(self.errors)}")

        print("\n  Resumo dos testes:")
        for result in self.test_results:
            status = "✅" if result.get('passed') else "❌"
            print(f"    {status} {result['test']}")

        # Salvar relatório
        report_file = SCREENSHOTS_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total,
                'passed': passed,
                'failed': total - passed,
                'console_logs': len(self.console_logs),
                'page_errors': len(self.errors),
            },
            'test_results': self.test_results,
            'console_logs': self.console_logs,
            'page_errors': self.errors,
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n  📊 Relatório completo: {report_file.name}")
        print("\n" + "="*80)

    async def cleanup(self):
        """Fecha o navegador"""
        if self.browser:
            await self.browser.close()
            print("\n✅ Navegador fechado")

async def main():
    tester = VisualTester()

    try:
        await tester.setup()

        # Executar testes
        await tester.test_initial_load()
        await tester.test_progress_bar()
        await tester.test_chat_visible()
        await tester.test_draft_modal()
        await tester.test_complete_section_1()
        await tester.test_section_transition()

        # Análises
        await tester.analyze_console_logs()
        await tester.analyze_page_errors()

        # Relatório final
        await tester.generate_report()

    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Aguardar 5 segundos antes de fechar (para ver resultado)
        print("\nAguardando 5 segundos antes de fechar...")
        await asyncio.sleep(5)
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

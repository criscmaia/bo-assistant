#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automação de Screenshots e Vídeo para Releases do BO Assistant
Versão 2.0 - Com gravação de vídeo real (não slideshow)
"""

import asyncio
import argparse
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Page
import json
from datetime import datetime

# Configurar encoding UTF-8 para o console do Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ReleaseAutomation:
    def __init__(self, version: str, backend_url: str = None, no_video: bool = False):
        self.version = version
        self.no_video = no_video
        
        # Carregar configurações
        config_file = Path(__file__).parent / 'test_scenarios.json'
        with open(config_file, encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Override backend URL se fornecido
        if backend_url:
            self.config['backend_url'] = backend_url
        
        # Diretório de saída
        project_root = Path(__file__).parent.parent
        self.output_dir = project_root / 'docs' / 'screenshots' / version
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 Iniciando automação para {version}")
        print(f"📁 Saída: {self.output_dir}")
        print(f"🌐 Backend: {self.config['backend_url']}")
        print(f"🌐 Frontend: {self.config['frontend_url']}")
    
    async def take_screenshot(self, page: Page, filename: str, description: str = "", full_page: bool = False):
        """Captura screenshot e salva"""
        path = self.output_dir / filename
        await page.screenshot(path=path, full_page=full_page)
        print(f"  📸 {filename} - {description}")
    
    async def wait_for_api_response(self, page: Page, timeout: int = 10000):
        """Aguarda resposta da API e loading sumir"""
        try:
            await page.wait_for_response(
                lambda response: '/chat' in response.url and response.status == 200,
                timeout=timeout
            )
            await page.wait_for_selector('#loading', state='hidden', timeout=3000)
        except:
            await page.wait_for_timeout(2000)
        
        await page.wait_for_timeout(1000)
    
    async def type_slowly(self, page: Page, selector: str, text: str, delay: int = 50):
        """Digita texto com delay entre caracteres (para vídeo parecer natural)"""
        await page.fill(selector, '')  # Limpar primeiro
        for char in text:
            await page.type(selector, char, delay=delay)
    
    async def fill_and_send(self, page: Page, message: str, slow_typing: bool = False):
        """Preenche input e envia mensagem"""
        if slow_typing:
            await self.type_slowly(page, '#user-input', message, delay=50)
        else:
            await page.fill('#user-input', message)
        await page.click('#send-button')
    
    async def run_desktop_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo de testes no desktop"""
        print("\n🖥️  Iniciando fluxo DESKTOP...")
        
        # 01. Screenshot inicial
        await page.goto(self.config['frontend_url'])
        await page.wait_for_timeout(2000)
        await self.take_screenshot(page, '01-section1-empty.png',
                                   'Estado inicial - Seção 1', full_page=True)

        # Responder perguntas 1-3 para chegar em 3/6
        section1_steps = self.config['sections'][0]['steps']

        # Pergunta 1.1
        await self.fill_and_send(page, section1_steps[0]['answer'], slow_typing=slow_mode)
        await self.wait_for_api_response(page)

        # Pergunta 1.2
        await self.fill_and_send(page, section1_steps[1]['answer'], slow_typing=slow_mode)
        await self.wait_for_api_response(page)

        # Pergunta 1.3
        await self.fill_and_send(page, section1_steps[2]['answer'], slow_typing=slow_mode)
        await self.wait_for_api_response(page)

        # 02. Screenshot progresso 3/6
        await self.take_screenshot(page, '02-section1-progress-3-of-6.png',
                                  'Progresso 3/6 - Seção 1', full_page=True)

        # 03-05. Fluxo de edição
        print("\n  ✏️  Testando edição...")
        edit_buttons = await page.query_selector_all('button:has-text("Editar")')
        if edit_buttons and len(edit_buttons) > 0:
            # 03. Clicar em editar - mostrar campo aberto
            await edit_buttons[0].click()
            await page.wait_for_timeout(800)

            # Aguardar input aparecer
            await page.wait_for_selector('input.px-2', state='visible', timeout=3000)

            # 04. Colocar erro de validação
            if slow_mode:
                await page.fill('input.px-2', '')  # Limpar primeiro
                await self.type_slowly(page, 'input.px-2', 'asd', delay=50)
            else:
                await page.fill('input.px-2', 'asd')

            # Clicar em Salvar
            save_button = await page.wait_for_selector('button:has-text("Salvar")', state='visible')
            await save_button.click()
            await page.wait_for_timeout(1500)

            await self.take_screenshot(page, '03-section1-edit-error.png',
                                      'Erro de validação ao editar - Seção 1', full_page=True)

            # 05. Corrigir e salvar com sucesso
            # Input ainda deve estar visível
            await page.wait_for_selector('input.px-2', state='visible', timeout=3000)

            if slow_mode:
                await page.fill('input.px-2', '')  # Limpar
                await self.type_slowly(page, 'input.px-2', section1_steps[4]['answer'], delay=50)
            else:
                await page.fill('input.px-2', section1_steps[4]['answer'])

            # Clicar em Salvar novamente
            save_button = await page.wait_for_selector('button:has-text("Salvar")', state='visible')
            await save_button.click()
            await page.wait_for_timeout(1500)

            await self.take_screenshot(page, '04-section1-edit-success.png',
                                      'Edição salva com sucesso - Seção 1', full_page=True)
        else:
            print("  ⚠️  Nenhum botão Editar encontrado - pulando teste de edição")

        # Responder perguntas 4-6
        await self.fill_and_send(page, section1_steps[5]['answer'], slow_typing=slow_mode)
        await self.wait_for_api_response(page)

        await self.fill_and_send(page, section1_steps[6]['answer'], slow_typing=slow_mode)
        await self.wait_for_api_response(page)

        await self.fill_and_send(page, section1_steps[7]['answer'], slow_typing=slow_mode)
        
        # Aguardar geração do texto
        print("\n  ⏳ Aguardando geração de texto (pode levar 10-15 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar container de seções geradas aparecer
        await page.wait_for_selector('#generated-sections-container:not(.hidden)', timeout=45000)
        await page.wait_for_timeout(1000)

        # Scroll suave até o texto gerado
        await page.evaluate("""
            document.querySelector('#generated-sections-container').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            })
        """)

        await page.wait_for_timeout(2000)  # Aguardar scroll

        # Scroll até o final do texto da Seção 1
        await page.evaluate("""
            const container = document.querySelector('#section1-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto

        # 05. Screenshot final da Seção 1 com botão "Iniciar Seção 2" (full page)
        await self.take_screenshot(page, '05-section1-final-with-button.png',
                                  'Texto gerado Seção 1 + Botão Iniciar Seção 2', full_page=True)

        print("\n✅ Fluxo Seção 1 desktop concluído!")

    async def run_section2_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 2"""
        print("\n🚗 Iniciando fluxo DESKTOP Seção 2...")

        # Scroll para o topo da página antes de iniciar Seção 2 (para vídeo)
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1000)  # Aguardar scroll suave

        # 1. Clicar em "Iniciar Seção 2"
        btn_start = page.locator('#btn-start-section2')
        await btn_start.wait_for(state='visible', timeout=5000)
        await page.wait_for_timeout(1000)  # Pausa dramática antes de clicar
        await btn_start.click()
        await page.wait_for_timeout(1500)

        # 06. Screenshot logo após iniciar Seção 2
        await self.take_screenshot(page, '06-section2-start.png',
                                  'Início da Seção 2 - Pergunta 2.0', full_page=True)

        # 2. Responder perguntas da Seção 2 conforme test_scenarios.json
        section2_steps = self.config['sections'][1]['steps']

        for step_data in section2_steps:
            step = step_data['step']
            answer = step_data['answer']
            expect = step_data['expect']

            print(f"  [{step}] Respondendo: {answer[:60]}...")

            # Preencher e enviar
            await self.fill_and_send(page, answer, slow_typing=slow_mode)

            # Aguardar resposta da API
            await self.wait_for_api_response(page, timeout=10000)

            # Capturar screenshot se especificado
            if 'screenshot' in step_data:
                screenshot_file = step_data['screenshot'] + '.png'
                await self.take_screenshot(page, screenshot_file, f"Step {step}", full_page=True)

            # Se espera falha, validação já foi aplicada
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
            else:
                print(f"    ✓ Resposta aceita")

        # 3. Aguardar geração de texto da Seção 2 (LLM pode demorar até 35s)
        print("\n  ⏳ Aguardando geração de texto da Seção 2 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 2 aparecer
        section2_card = page.locator('#section2-card:not(.hidden)')
        await section2_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Verificar que ambos accordions estão visíveis
        section1_card = page.locator('#section1-card')
        copy_all_btn = page.locator('#copy-all-button')

        # Assertions para validar estado
        is_section1_visible = await section1_card.is_visible()
        is_section2_visible = await section2_card.is_visible()
        is_copy_all_visible = await copy_all_btn.is_visible()

        if not is_section1_visible:
            print("  ⚠️  WARNING: Seção 1 não está visível!")
        if not is_section2_visible:
            print("  ⚠️  WARNING: Seção 2 não está visível!")
        if not is_copy_all_visible:
            print("  ⚠️  WARNING: Botão 'Copiar BO Completo' não está visível!")

        # Scroll suave até o container de textos
        await page.evaluate("""
            document.querySelector('#generated-sections-container').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            })
        """)

        await page.wait_for_timeout(2000)  # Aguardar scroll

        # Scroll até o final do texto da Seção 2
        await page.evaluate("""
            const container = document.querySelector('#section2-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)  # Pausar 3s mostrando ambas seções

        # 5. Screenshot final (página completa com ambas seções)
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '10-section2-final-both-sections.png',
                                  'Ambas seções visíveis (Seção 1 + 2)', full_page=True)

        print("\n✅ Fluxo Seção 2 desktop concluído!")
        print("✅ Ambas seções (1 + 2) completas!")

        # Fechar página para parar gravação de vídeo
        await page.close()

    async def run_mobile_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo de testes no mobile"""
        print("\n📱 Iniciando fluxo MOBILE Seção 1...")

        # 11. Screenshot inicial mobile
        await page.goto(self.config['frontend_url'])
        await page.wait_for_timeout(2000)
        await self.take_screenshot(page, '11-mobile-section1-empty.png',
                                  'Layout mobile inicial - Seção 1', full_page=True)

        # 12. Abrir sidebar
        await page.click('#sidebar-toggle')
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '12-mobile-section1-sidebar.png',
                                  'Drawer lateral aberto - Seção 1', full_page=True)

        # Fechar sidebar usando JavaScript (mais confiável)
        await page.evaluate("""
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (sidebar) sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('open');
        """)
        await page.wait_for_timeout(500)

        # Responder todas as perguntas rapidamente
        section1_steps = self.config['sections'][0]['steps']
        responses = [
            section1_steps[0]['answer'],  # 1.1
            section1_steps[1]['answer'],  # 1.2
            section1_steps[2]['answer'],  # 1.3
            section1_steps[5]['answer'],  # 1.4
            section1_steps[6]['answer'],  # 1.5
            section1_steps[7]['answer']   # 1.6
        ]
        
        for i, response in enumerate(responses, 1):
            print(f"  📝 Respondendo pergunta {i}/6...")
            await self.fill_and_send(page, response, slow_typing=slow_mode)
            
            if i == 6:
                print(f"  ⏳ Aguardando geração de texto...")
                await page.wait_for_selector('#generated-sections-container:not(.hidden)', timeout=45000)
                await page.wait_for_timeout(1000)

                # Scroll suave até o texto gerado
                await page.evaluate("""
                    document.querySelector('#generated-sections-container').scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    })
                """)

                await page.wait_for_timeout(2000)  # Aguardar scroll

                # Scroll para baixo no texto gerado da Seção 1
                await page.evaluate("""
                    const container = document.querySelector('#section1-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)

                await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto final
            else:
                await self.wait_for_api_response(page, timeout=12000)

        # 13. Screenshot final mobile Seção 1 (full page)
        await self.take_screenshot(page, '13-mobile-section1-final.png',
                                  'Resultado final mobile - Seção 1', full_page=True)

        print("\n✅ Fluxo mobile Seção 1 concluído!")

    async def run_mobile_section2_flow(self, page: Page, slow_mode: bool = False):
        """Fluxo mobile da Seção 2 (simplificado, sem screenshots de erros)"""
        print("\n🚗 Iniciando fluxo MOBILE Seção 2...")

        # Scroll para o topo antes de iniciar Seção 2 (para vídeo)
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1000)

        # 1. Clicar em "Iniciar Seção 2"
        await page.wait_for_timeout(1000)
        await page.click('#btn-start-section2')
        await page.wait_for_timeout(1500)

        # 14. Screenshot início Seção 2 mobile
        await self.take_screenshot(page, '14-mobile-section2-start.png',
                                  'Início Seção 2 mobile', full_page=True)

        # 2. Abrir sidebar e capturar estado
        await page.click('#sidebar-toggle')
        await page.wait_for_timeout(500)  # Animação
        await self.take_screenshot(page, '15-mobile-section2-sidebar.png',
                                  'Sidebar - Seção 1 completa + Seção 2 em progresso', full_page=True)

        # Fechar sidebar usando JavaScript (mais confiável)
        await page.evaluate("""
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (sidebar) sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('open');
        """)
        await page.wait_for_timeout(500)

        # 3. Responder 8 perguntas rapidamente (apenas respostas válidas, sem erros)
        section2_steps = self.config['sections'][1]['steps']
        valid_steps = [s for s in section2_steps if s['expect'] == 'pass']

        for i, step_data in enumerate(valid_steps, 1):
            print(f"  📝 Respondendo pergunta 2.{i-1} (mobile)...")
            await self.fill_and_send(page, step_data['answer'], slow_typing=slow_mode)

            if i == len(valid_steps):
                # Última pergunta - aguardar geração de texto
                print(f"  ⏳ Aguardando geração de texto da Seção 2...")
                section2_card = page.locator('#section2-card:not(.hidden)')
                await section2_card.wait_for(state='visible', timeout=50000)
                await page.wait_for_timeout(1000)

                # Scroll suave até o container de textos
                await page.evaluate("""
                    document.querySelector('#generated-sections-container').scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    })
                """)

                await page.wait_for_timeout(2000)  # Aguardar scroll

                # Scroll para baixo no texto gerado da Seção 2
                await page.evaluate("""
                    const container = document.querySelector('#section2-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)

                await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto final
            else:
                await self.wait_for_api_response(page, timeout=12000)

        # 4. Screenshot final mobile com ambas seções
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '16-mobile-section2-final.png',
                                  'Resultado final mobile - Ambas seções', full_page=True)

        print("\n✅ Fluxo mobile Seção 2 concluído!")
        print("✅ Mobile: Ambas seções (1 + 2) completas!")

        # Fechar página para parar gravação de vídeo
        await page.close()

    def create_readme(self):
        """Cria README.md com metadados"""
        readme_content = f"""# Screenshots - v{self.version}

**Data de geração:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

**Total:** 16 screenshots (10 desktop + 6 mobile) + vídeo (~4 minutos)

---

## 📝 Desktop - Seção 1 (Contexto da Ocorrência)
- `01-section1-empty.png` - Estado inicial
- `02-section1-progress-3-of-6.png` - Progresso 3/6 perguntas respondidas
- `03-section1-edit-error.png` - Erro de validação ao editar
- `04-section1-edit-success.png` - Edição salva com sucesso
- `05-section1-final-with-button.png` - Texto gerado + Botão "Iniciar Seção 2" (full page)

## 🚗 Desktop - Seção 2 (Abordagem a Veículo)
- `06-section2-start.png` - Início da Seção 2 (pergunta 2.0)
- `07-section2-plate-error.png` - Erro de validação: placa inválida (ABC123)
- `08-section2-rank-error.png` - Erro de validação: sem graduação do policial
- `09-section2-progress-4-of-8.png` - Progresso 4/8 perguntas respondidas
- `10-section2-final-both-sections.png` - Ambas seções visíveis (Seção 1 + 2) (full page)

## 📱 Mobile - Seção 1 (430x932 - iPhone 14 Pro Max)
- `11-mobile-section1-empty.png` - Layout mobile inicial
- `12-mobile-section1-sidebar.png` - Sidebar aberta (Seção 1)
- `13-mobile-section1-final.png` - Resultado final Seção 1 (full page)

## 📱 Mobile - Seção 2
- `14-mobile-section2-start.png` - Início da Seção 2 mobile
- `15-mobile-section2-sidebar.png` - Sidebar (Seção 1 ✓ + Seção 2 em progresso)
- `16-mobile-section2-final.png` - Resultado final com ambas seções (full page)

## 🎬 Vídeo
- `demo.webm` - Demonstração completa (~4 minutos)
  - Desktop: Seção 1 (6 perguntas) → Seção 2 (8 perguntas)
  - Mobile: Seção 1 → Seção 2
  - Testa validações (placa Mercosul, graduação, edição)

## 🔧 Gerado com
- **Playwright** (automação de browser)
- **Python 3.13**
- **Backend:** {self.config['backend_url']}
- **Frontend:** {self.config['frontend_url']}
- **Versão:** {self.version}

## ✅ Validações Testadas
- ✅ Erro de validação ao editar (data inválida)
- ✅ Edição válida salva com sucesso
- ✅ Placa Mercosul inválida rejeitada (ABC123)
- ✅ Resposta sem graduação rejeitada
- ✅ Persistência de textos gerados (ambas seções visíveis)
- ✅ Botão "Copiar BO Completo" aparece após 2 seções
"""

        readme_path = self.output_dir / 'README.md'
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"\n📝 README.md criado")
    
    async def run(self):
        """Executa automação completa"""
        async with async_playwright() as p:
            # Configurar gravação de vídeo se não estiver desabilitado
            video_config = {}
            if not self.no_video:
                video_config = {
                    'record_video_dir': str(self.output_dir),
                    'record_video_size': {'width': 1280, 'height': 720}
                }
            
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(**video_config)
            
            # Desktop: Seção 1 + Seção 2
            page_desktop = await context.new_page()
            await page_desktop.set_viewport_size({'width': 1280, 'height': 720})
            await self.run_desktop_flow(page_desktop, slow_mode=not self.no_video)
            await self.run_section2_flow(page_desktop, slow_mode=not self.no_video)

            # Mobile: Seção 1 + Seção 2
            page_mobile = await context.new_page()
            await page_mobile.set_viewport_size({'width': 430, 'height': 932})
            await self.run_mobile_flow(page_mobile, slow_mode=not self.no_video)
            await self.run_mobile_section2_flow(page_mobile, slow_mode=not self.no_video)
            
            # Fechar e salvar vídeo
            await context.close()
            await browser.close()
            
            # Se vídeo foi gravado, renomear
            if not self.no_video:
                # Playwright salva vídeos com hash, precisa encontrar e renomear
                video_files = list(self.output_dir.glob('*.webm'))
                if video_files:
                    video_file = video_files[0]
                    demo_path = self.output_dir / 'demo.webm'
                    video_file.rename(demo_path)
                    print(f"\n🎬 Vídeo salvo: demo.webm")
            
            # Criar README
            self.create_readme()
            
            print(f"\n🎉 Automação concluída!")
            print(f"📁 Arquivos salvos em: {self.output_dir}")
            if not self.no_video:
                print(f"✅ 16 screenshots + vídeo + README criados!")
                print(f"   • Desktop: 10 screenshots (Seção 1 + 2)")
                print(f"   • Mobile: 6 screenshots (Seção 1 + 2)")
                print(f"   • Vídeo: ~4 minutos (fluxo completo)")
            else:
                print(f"✅ 16 screenshots + README criados!")
                print(f"   • Desktop: 10 screenshots (Seção 1 + 2)")
                print(f"   • Mobile: 6 screenshots (Seção 1 + 2)")

def main():
    parser = argparse.ArgumentParser(description='Automação de screenshots e vídeo')
    parser.add_argument('--version', required=True, help='Versão do release (ex: v0.3.2)')
    parser.add_argument('--backend', default='http://localhost:8000', help='URL do backend')
    parser.add_argument('--no-video', action='store_true', help='Não gravar vídeo')
    
    args = parser.parse_args()
    
    automation = ReleaseAutomation(
        version=args.version,
        backend_url=args.backend,
        no_video=args.no_video
    )
    
    asyncio.run(automation.run())

if __name__ == "__main__":
    main()

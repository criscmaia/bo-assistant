#!/usr/bin/env python3
"""
Automação de Screenshots e Vídeo para Releases do BO Assistant
Versão 2.0 - Com gravação de vídeo real (não slideshow)
"""

import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright, Page
import json
from datetime import datetime

class ReleaseAutomation:
    def __init__(self, version: str, backend_url: str = None, no_video: bool = False):
        self.version = version
        self.no_video = no_video
        
        # Carregar configurações
        config_file = Path(__file__).parent / 'test_scenarios.json'
        with open(config_file) as f:
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
        await self.take_screenshot(page, '01-desktop-sidebar-empty.png', 
                                   'Estado inicial')
        
        # Responder perguntas 1-3 para chegar em 3/6
        await self.fill_and_send(page, "21:11, dia 22/03", slow_typing=slow_mode)
        await self.wait_for_api_response(page)
        
        await self.fill_and_send(page, "prefixo 1234, Sargentos João Silva e Pedro Santos", slow_typing=slow_mode)
        await self.wait_for_api_response(page)
        
        await self.fill_and_send(page, "Tráfico de drogas", slow_typing=slow_mode)
        await self.wait_for_api_response(page)
        
        # 02. Screenshot progresso 3/6
        await self.take_screenshot(page, '02-desktop-sidebar-progress.png',
                                  'Progresso 3/6')
        
        # 03-05. Fluxo de edição
        print("\n  ✏️  Testando edição...")
        edit_buttons = await page.query_selector_all('button:has-text("Editar")')
        if edit_buttons:
            # 03. Clicar em editar - mostrar campo aberto
            await edit_buttons[0].click()
            await page.wait_for_timeout(500)
            
            await self.take_screenshot(page, '03-desktop-editando.png',
                                      'Editando campo')
            
            # 04. Colocar erro de validação
            edit_input = await page.query_selector('input.px-2')
            if slow_mode:
                await self.type_slowly(page, 'input.px-2', 'asd', delay=50)
            else:
                await edit_input.fill('asd')
            
            save_button = await page.query_selector('button:has-text("Salvar")')
            await save_button.click()
            await page.wait_for_timeout(1500)
            
            await self.take_screenshot(page, '04-desktop-editando-erro.png',
                                      'Erro de validação ao editar')
            
            # 05. Corrigir e salvar com sucesso
            if slow_mode:
                await page.fill('input.px-2', '')
                await self.type_slowly(page, 'input.px-2', '21:11, dia 23/03', delay=50)
            else:
                await edit_input.fill('21:11, dia 23/03')
            
            await save_button.click()
            await page.wait_for_timeout(1500)
            
            await self.take_screenshot(page, '05-desktop-editando-sucesso.png',
                                      'Edição salva com sucesso')
        
        # Responder perguntas 4-6
        await self.fill_and_send(page, "Denúncia anônima via COPOM reportando venda de drogas na esquina", slow_typing=slow_mode)
        await self.wait_for_api_response(page)
        
        await self.fill_and_send(page, "Rua das Acácias, sem número, apt 12, bairro Jardins", slow_typing=slow_mode)
        await self.wait_for_api_response(page)
        
        await self.fill_and_send(page, "Local com histórico de operações em 2024. Facção ABC atua na região", slow_typing=slow_mode)
        
        # Aguardar geração do texto
        print("\n  ⏳ Aguardando geração de texto (pode levar 10-15 segundos)...")
        
        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass
        
        # Aguardar caixa verde aparecer
        await page.wait_for_selector('#result-container.bg-green-50', timeout=25000)
        await page.wait_for_timeout(1000)
        
        # Scroll suave até o texto gerado
        await page.evaluate("""
            document.querySelector('#result-container').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            })
        """)
        
        await page.wait_for_timeout(2000)  # Aguardar scroll
        
        # Scroll até o final do texto
        await page.evaluate("""
            const container = document.querySelector('#generated-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)
        
        await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto
        
        # 06. Screenshot final (full page)
        await self.take_screenshot(page, '06-desktop-final.png',
                                  'Texto final gerado', full_page=True)
        
        print("\n✅ Fluxo desktop concluído!")
        
        # Fechar página para parar gravação de vídeo
        await page.close()
    
    async def run_mobile_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo de testes no mobile"""
        print("\n📱 Iniciando fluxo MOBILE...")
        
        # 07. Screenshot inicial mobile
        await page.goto(self.config['frontend_url'])
        await page.wait_for_timeout(2000)
        await self.take_screenshot(page, '07-mobile-empty.png',
                                  'Layout mobile inicial')
        
        # 08. Abrir sidebar
        await page.click('#sidebar-toggle')
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '08-mobile-sidebar-open.png',
                                  'Drawer lateral aberto')
        
        # Fechar sidebar usando botão
        await page.click('#sidebar-close')
        await page.wait_for_timeout(500)
        
        # Responder todas as perguntas rapidamente
        responses = [
            "21:11, dia 22/03",
            "prefixo 1234, Sargentos João Silva e Pedro Santos",
            "Tráfico de drogas",
            "Denúncia anônima via COPOM reportando venda de drogas na esquina",
            "Rua das Acácias, sem número, apt 12, bairro Jardins",
            "Local com histórico de operações em 2024. Facção ABC atua na região"
        ]
        
        for i, response in enumerate(responses, 1):
            print(f"  📝 Respondendo pergunta {i}/6...")
            await self.fill_and_send(page, response, slow_typing=slow_mode)
            
            if i == 6:
                print(f"  ⏳ Aguardando geração de texto...")
                await page.wait_for_selector('#result-container.bg-green-50', timeout=25000)
                await page.wait_for_timeout(1000)
                
                # Scroll suave até o texto gerado
                await page.evaluate("""
                    document.querySelector('#result-container').scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    })
                """)
                
                await page.wait_for_timeout(2000)  # Aguardar scroll
                
                # Scroll para baixo no texto gerado
                await page.evaluate("""
                    const container = document.querySelector('#generated-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)
                
                await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto final
            else:
                await self.wait_for_api_response(page, timeout=12000)
        
        # 09. Screenshot final mobile (full page)
        await self.take_screenshot(page, '09-mobile-final.png',
                                  'Resultado final mobile', full_page=True)
        
        print("\n✅ Fluxo mobile concluído!")
        
        # Fechar página para parar gravação de vídeo
        await page.close()
    
    def create_readme(self):
        """Cria README.md com metadados"""
        readme_content = f"""# Screenshots - v{self.version}

**Data de geração:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Desktop (1280x720)
- `01-desktop-sidebar-empty.png` - Estado inicial
- `02-desktop-sidebar-progress.png` - Progresso 3/6
- `03-desktop-editando.png` - Editando campo
- `04-desktop-editando-erro.png` - Erro de validação
- `05-desktop-editando-sucesso.png` - Edição salva
- `06-desktop-final.png` - Texto gerado (full page)

## Mobile (430x932 - iPhone 14 Pro Max)
- `07-mobile-empty.png` - Layout inicial
- `08-mobile-sidebar-open.png` - Sidebar aberta
- `09-mobile-final.png` - Resultado final (full page)

## Vídeo
- `demo.mp4` - Demonstração completa com interações reais

## Gerado com
- Playwright (automação)
- Python 3.13
- Backend: {self.config['backend_url']}
- Frontend: {self.config['frontend_url']}
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
            
            # Desktop
            page_desktop = await context.new_page()
            await page_desktop.set_viewport_size({'width': 1280, 'height': 720})
            await self.run_desktop_flow(page_desktop, slow_mode=not self.no_video)
            
            # Mobile
            page_mobile = await context.new_page()
            await page_mobile.set_viewport_size({'width': 430, 'height': 932})
            await self.run_mobile_flow(page_mobile, slow_mode=not self.no_video)
            
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
                print(f"✅ 9 screenshots + vídeo + README criados!")
            else:
                print(f"✅ 9 screenshots + README criados!")

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

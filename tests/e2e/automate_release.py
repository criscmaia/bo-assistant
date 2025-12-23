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
    def __init__(self, version: str, backend_url: str = None, no_video: bool = False, start_section: int = 1):
        self.version = version
        self.no_video = no_video
        self.start_section = start_section
        
        # Carregar configurações
        config_file = Path(__file__).parent / 'test_scenarios.json'
        with open(config_file, encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Override backend URL se fornecido
        if backend_url:
            self.config['backend_url'] = backend_url
        
        # Diretório de saída (raiz do projeto = 3 níveis acima)
        project_root = Path(__file__).parent.parent.parent
        self.output_dir = project_root / 'docs' / 'screenshots' / version

        # Criar diretório com tratamento de erro
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Diretório criado/verificado: {self.output_dir}")
            print(f"   Diretório existe: {self.output_dir.exists()}")
            print(f"   É diretório: {self.output_dir.is_dir()}")
        except Exception as e:
            print(f"❌ ERRO ao criar diretório: {e}")
            raise

        print(f"🚀 Iniciando automação para {version}")
        print(f"🌐 Backend: {self.config['backend_url']}")
        print(f"🌐 Frontend: {self.config['frontend_url']}")

        if self.start_section > 1:
            print(f"\n⚡ MODO RÁPIDO ATIVADO:")
            print(f"   • Começando pela Seção {self.start_section}")
            print(f"   • Seções anteriores serão preenchidas rapidamente (sem screenshots)")
            print(f"   • Chrome ficará aberto apenas durante Seção {self.start_section}")
        else:
            print(f"\n📸 MODO COMPLETO:")
            print(f"   • Screenshots de todas as 4 seções")
            print(f"   • Vídeo: {'SIM' if not self.no_video else 'NÃO'}")
    
    async def take_screenshot(self, page: Page, filename: str, description: str = "", full_page: bool = False):
        """Captura screenshot e salva"""
        path = self.output_dir / filename
        try:
            await page.screenshot(path=path, full_page=full_page)
            # Verificar se arquivo foi criado
            if path.exists():
                file_size = path.stat().st_size
                print(f"  📸 {filename} ({file_size} bytes) - {description}")
            else:
                print(f"  ⚠️  {filename} NÃO FOI SALVO! - {description}")
        except Exception as e:
            print(f"  ❌ ERRO ao salvar {filename}: {e}")
    
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
        # Aguardar input estar habilitado
        await page.wait_for_selector(f'{selector}:not([disabled])', timeout=30000)
        await page.fill(selector, '')  # Limpar primeiro
        for char in text:
            await page.type(selector, char, delay=delay)

    async def fill_and_send(self, page: Page, message: str, slow_typing: bool = False):
        """Preenche input e envia mensagem"""
        # Aguardar input estar habilitado antes de preencher
        await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
        if slow_typing:
            await self.type_slowly(page, '#user-input', message, delay=50)
        else:
            await page.fill('#user-input', message)
        await page.click('#send-button')

    async def prepare_sections_via_api(self, up_to_section: int):
        """
        Prepara seções anteriores via API (sem usar o browser).
        Usa /new_session + /sync_session para restaurar estado instantaneamente.
        Retorna o session_id criado.
        """
        import httpx

        backend_url = self.config['backend_url']

        print(f"  ⚡ Preparando Seções 1-{up_to_section} via API (instantâneo)...")

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Criar sessão via /new_session
            response = await client.post(f"{backend_url}/new_session")
            if response.status_code != 200:
                print(f"    ❌ ERRO ao criar sessão: {response.status_code} - {response.text}")
                return None
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"    ✓ Sessão criada: {session_id[:8]}...")

            # 2. Montar payload com todas as respostas até a seção desejada
            answers = {}

            for section_num in range(1, up_to_section + 1):
                section_config = self.config['sections'][section_num - 1]

                for step_data in section_config['steps']:
                    step = step_data['step']
                    expect = step_data.get('expect', 'pass')

                    # Ignorar steps que falham (são tentativas inválidas)
                    if expect == 'fail':
                        continue

                    # Extrair o ID real do step (ex: "2.1_retry" -> "2.1", "edit_1.1_success" -> "1.1")
                    if '_retry' in step:
                        real_step_id = step.replace('_retry', '')
                    elif step.startswith('edit_') and '_success' in step:
                        real_step_id = step.replace('edit_', '').replace('_success', '')
                    elif step.startswith('edit_'):
                        # Edições sem _success são falhas, ignorar
                        continue
                    else:
                        real_step_id = step

                    # Armazenar resposta (sobrescreve se já existir, ex: retry sobrescreve original)
                    answers[real_step_id] = step_data['answer']

            # Log das respostas finais
            for step_id in sorted(answers.keys()):
                print(f"    [{step_id}] {answers[step_id][:40]}...")

            # 3. Chamar /sync_session para restaurar estado
            payload = {
                "session_id": session_id,
                "answers": answers
            }

            response = await client.post(
                f"{backend_url}/sync_session",
                json=payload
            )

            if response.status_code == 200:
                print(f"    ✓ Seções 1-{up_to_section} sincronizadas via API!")
                return session_id
            else:
                print(f"    ❌ ERRO ao sincronizar: {response.status_code} - {response.text}")
                return None

    async def inject_session_and_restore(self, page: Page, session_id: str, up_to_section: int):
        """
        Injeta sessão diretamente no frontend via JavaScript.
        Abordagem: executa a mesma lógica que restoreFromDraft() faria, mas controlada por nós.
        """
        import json

        # Montar respostas no formato correto
        answers_js = {}

        for section_num in range(1, up_to_section + 1):
            section_config = self.config['sections'][section_num - 1]

            for step_data in section_config['steps']:
                step = step_data['step']
                expect = step_data.get('expect', 'pass')

                if expect == 'fail':
                    continue

                if '_retry' in step:
                    real_step_id = step.replace('_retry', '')
                elif step.startswith('edit_') and '_success' in step:
                    real_step_id = step.replace('edit_', '').replace('_success', '')
                elif step.startswith('edit_'):
                    continue
                else:
                    real_step_id = step

                answers_js[real_step_id] = step_data['answer']

        answers_json = json.dumps(answers_js)
        backend_url = self.config['backend_url']

        # Script JavaScript que simula a restauração completa
        restore_script = f"""
        (async function() {{
            const API_URL = '{backend_url}';
            const sessionId = '{session_id}';
            const answers = {answers_json};
            const upToSection = {up_to_section};

            console.log('[E2E] Iniciando restauração programática...');

            // 1. Chamar /sync_session para sincronizar backend
            console.log('[E2E] Chamando /sync_session...');
            const syncResponse = await fetch(API_URL + '/sync_session', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    session_id: sessionId,
                    answers: answers
                }})
            }});

            if (!syncResponse.ok) {{
                console.error('[E2E] Erro no sync_session:', syncResponse.status);
                return false;
            }}

            const syncData = await syncResponse.json();
            console.log('[E2E] sync_session OK:', syncData);

            // 2. Atualizar variáveis globais do frontend (acessando via window)
            // O frontend usa variáveis no escopo global do script
            if (typeof sessionId !== 'undefined') {{
                // Tentar atualizar a variável global sessionId
                try {{ eval('sessionId = "' + sessionId + '"'); }} catch(e) {{}}
            }}

            // 3. Atualizar UI - reconstruir histórico de chat
            const chatContainer = document.getElementById('chat-container');
            chatContainer.innerHTML = '';

            // Adicionar mensagem de boas-vindas
            const welcomeDiv = document.createElement('div');
            welcomeDiv.className = 'message-container flex justify-start mb-4';
            welcomeDiv.innerHTML = '<div class="bg-gray-100 rounded-lg p-4 max-w-3xl"><span class="text-gray-800">Sessão restaurada para teste E2E.</span></div>';
            chatContainer.appendChild(welcomeDiv);

            // 4. Mostrar container de textos gerados e cards
            const container = document.getElementById('generated-sections-container');
            if (container) {{
                container.classList.remove('hidden');
            }}

            for (let sec = 1; sec <= upToSection; sec++) {{
                const cardId = 'section' + sec + '-card';
                const card = document.getElementById(cardId);
                if (card) {{
                    card.classList.remove('hidden');
                    // Adicionar texto placeholder
                    const textEl = card.querySelector('#section' + sec + '-text');
                    if (textEl && !textEl.textContent.trim()) {{
                        textEl.textContent = '[Texto da Seção ' + sec + ' gerado - teste E2E]';
                    }}
                }}
            }}

            // 5. Criar botão para próxima seção baseado em upToSection
            if (upToSection === 2) {{
                // Criar botão "Iniciar Seção 3"
                if (!document.getElementById('btn-start-section3')) {{
                    console.log('[E2E] Criando botão Iniciar Seção 3...');

                    const section3ButtonDiv = document.createElement('div');
                    section3ButtonDiv.id = 'section3-button-container';
                    section3ButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-xl text-center';
                    section3ButtonDiv.innerHTML = `
                        <h3 class="text-xl font-bold text-purple-900 mb-2">👁️ Próxima Etapa: Campana</h3>
                        <p class="text-gray-700 mb-4">
                            A equipe realizou campana antes da abordagem? Continue para a próxima seção.
                        </p>
                        <button
                            id="btn-start-section3"
                            class="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors">
                            ▶️ Iniciar Seção 3
                        </button>
                    `;

                    // Inserir após o container de textos gerados
                    const genContainer = document.getElementById('generated-sections-container');
                    if (genContainer && genContainer.parentElement) {{
                        genContainer.parentElement.appendChild(section3ButtonDiv);
                    }}

                    // Event listener - usar a função global startSection3
                    const btn = document.getElementById('btn-start-section3');
                    if (btn && typeof startSection3 === 'function') {{
                        btn.addEventListener('click', startSection3);
                        console.log('[E2E] Event listener adicionado ao botão');
                    }}
                }}
            }} else if (upToSection === 3) {{
                // Criar botão "Iniciar Seção 4"
                if (!document.getElementById('btn-start-section4')) {{
                    console.log('[E2E] Criando botão Iniciar Seção 4...');

                    const section4ButtonDiv = document.createElement('div');
                    section4ButtonDiv.id = 'section4-button-container';
                    section4ButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-orange-50 to-orange-100 border-2 border-orange-200 rounded-xl text-center';
                    section4ButtonDiv.innerHTML = `
                        <h3 class="text-xl font-bold text-orange-900 mb-2">🏠 Próxima Etapa: Entrada em Domicílio</h3>
                        <p class="text-gray-700 mb-4">
                            Houve entrada em domicílio durante a ocorrência? Continue para a próxima seção.
                        </p>
                        <button
                            id="btn-start-section4"
                            class="px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition-colors">
                            ▶️ Iniciar Seção 4
                        </button>
                    `;

                    // Inserir após o container de textos gerados
                    const genContainer = document.getElementById('generated-sections-container');
                    if (genContainer && genContainer.parentElement) {{
                        genContainer.parentElement.appendChild(section4ButtonDiv);
                    }}

                    // Event listener - usar a função global startSection4
                    const btn = document.getElementById('btn-start-section4');
                    if (btn && typeof startSection4 === 'function') {{
                        btn.addEventListener('click', startSection4);
                        console.log('[E2E] Event listener adicionado ao botão Seção 4');
                    }}
                }}
            }} else if (upToSection === 4) {{
                // Criar botão "Iniciar Seção 5"
                if (!document.getElementById('btn-start-section5')) {{
                    console.log('[E2E] Criando botão Iniciar Seção 5...');

                    const section5ButtonDiv = document.createElement('div');
                    section5ButtonDiv.id = 'section5-button-container';
                    section5ButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-pink-50 to-pink-100 border-2 border-pink-200 rounded-xl text-center';
                    section5ButtonDiv.innerHTML = `
                        <h3 class="text-xl font-bold text-pink-900 mb-2">🎯 Próxima Etapa: Fundada Suspeita</h3>
                        <p class="text-gray-700 mb-4">
                            Houve abordagem por fundada suspeita (sem veículo, campana ou entrada em domicílio)? Continue para a próxima seção.
                        </p>
                        <button
                            id="btn-start-section5"
                            class="px-6 py-2 bg-pink-600 hover:bg-pink-700 text-white font-semibold rounded-lg transition-colors">
                            ▶️ Iniciar Seção 5
                        </button>
                    `;

                    // Inserir após o container de textos gerados
                    const genContainer = document.getElementById('generated-sections-container');
                    if (genContainer && genContainer.parentElement) {{
                        genContainer.parentElement.appendChild(section5ButtonDiv);
                    }}

                    // Event listener - usar a função global startSection5
                    const btn = document.getElementById('btn-start-section5');
                    if (btn && typeof startSection5 === 'function') {{
                        btn.addEventListener('click', startSection5);
                        console.log('[E2E] Event listener adicionado ao botão Seção 5');
                    }}
                }}
            }} else if (upToSection === 5) {{
                // Criar botão "Iniciar Seção 6"
                if (!document.getElementById('btn-start-section6')) {{
                    console.log('[E2E] Criando botão Iniciar Seção 6...');

                    const section6ButtonDiv = document.createElement('div');
                    section6ButtonDiv.id = 'section6-button-container';
                    section6ButtonDiv.className = 'mt-6 p-6 bg-gradient-to-r from-teal-50 to-cyan-100 border-2 border-teal-200 rounded-xl text-center';
                    section6ButtonDiv.innerHTML = `
                        <h3 class="text-xl font-bold text-teal-900 mb-2">⚔️ Próxima Etapa: Reação e Uso da Força</h3>
                        <p class="text-gray-700 mb-4">
                            Qual foi a reação do autor? Houve necessidade de uso da força? Continue para a próxima seção.
                        </p>
                        <button
                            id="btn-start-section6"
                            class="px-6 py-2 bg-teal-600 hover:bg-teal-700 text-white font-semibold rounded-lg transition-colors">
                            ▶️ Iniciar Seção 6
                        </button>
                    `;

                    // Inserir após o container de textos gerados
                    const genContainer = document.getElementById('generated-sections-container');
                    if (genContainer && genContainer.parentElement) {{
                        genContainer.parentElement.appendChild(section6ButtonDiv);
                    }}

                    // Event listener - usar a função global startSection6
                    const btn = document.getElementById('btn-start-section6');
                    if (btn && typeof startSection6 === 'function') {{
                        btn.addEventListener('click', startSection6);
                        console.log('[E2E] Event listener adicionado ao botão Seção 6');
                    }}
                }}
            }}

            // 6. Atualizar sidebar
            const sidebarItems = document.querySelectorAll('.sidebar-section');
            sidebarItems.forEach(item => {{
                const sectionNum = parseInt(item.dataset.section || '0');
                if (sectionNum > 0) {{
                    item.classList.remove('completed', 'active', 'pending');
                    if (sectionNum <= upToSection) {{
                        item.classList.add('completed');
                    }} else if (sectionNum === upToSection + 1) {{
                        item.classList.add('active');
                    }} else {{
                        item.classList.add('pending');
                    }}
                }}
            }});

            // 7. Desabilitar input de chat (seção completa)
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            if (userInput) userInput.disabled = true;
            if (sendButton) sendButton.disabled = true;

            console.log('[E2E] Restauração concluída!');
            return true;
        }})();
        """

        print(f"    ⏳ Executando restauração programática via JavaScript...")

        try:
            # Aguardar página carregar completamente (com timeout)
            await page.wait_for_load_state('domcontentloaded', timeout=10000)
            await page.wait_for_timeout(500)
        except:
            # Se timeout, continua mesmo assim
            pass

        # Limpar qualquer draft existente e fechar modal se aberto
        try:
            await page.evaluate("""
                localStorage.removeItem('bo_inteligente_draft');
                const modal = document.getElementById('draft-modal');
                if (modal) modal.classList.add('hidden');
            """)
        except:
            # Se falhar, continua
            pass

        # Executar o script de restauração com tratamento de erro
        try:
            result = await page.evaluate(restore_script)
        except Exception as e:
            print(f"    ⚠️  Erro na restauração: {str(e)}")
            # Continua mesmo com erro

        await page.wait_for_timeout(1500)  # Aguardar processamento

        # Verificar se cards aparecem
        for section_num in range(1, up_to_section + 1):
            card = page.locator(f'#section{section_num}-card')
            try:
                await card.wait_for(state='visible', timeout=10000)
                print(f"    ✓ Seção {section_num} restaurada visualmente")
            except:
                print(f"    ⚠️  Card da Seção {section_num} não apareceu")

        # Verificar botão da próxima seção
        if up_to_section < 3:
            next_section = up_to_section + 1
            btn = page.locator(f'#btn-start-section{next_section}')
            try:
                await btn.wait_for(state='visible', timeout=5000)
                print(f"    ✓ Botão 'Iniciar Seção {next_section}' visível")
            except:
                print(f"    ⚠️  Botão 'Iniciar Seção {next_section}' não apareceu")

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

        # 1. Clicar em "Iniciar Seção 2"
        btn_start = page.locator('#btn-start-section2')
        await btn_start.wait_for(state='visible', timeout=5000)
        await page.wait_for_timeout(1000)  # Pausa dramática antes de clicar
        await btn_start.click()
        await page.wait_for_timeout(500)

        # Scroll para o topo DEPOIS do click (para garantir que header da Seção 2 apareça no vídeo)
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)  # Aguardar scroll e animação

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

        # IMPORTANTE: Aguardar botão "Iniciar Seção 3" aparecer antes de prosseguir
        print("  🔍 Aguardando botão 'Iniciar Seção 3' aparecer...")
        btn_section3 = page.locator('#btn-start-section3')
        try:
            await btn_section3.wait_for(state='visible', timeout=5000)
            print("  ✓ Botão 'Iniciar Seção 3' visível!")
        except:
            print("  ⚠️  WARNING: Botão 'Iniciar Seção 3' não apareceu em 5s!")
            # Tentar dar scroll para baixo para ver se botão aparece
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(1000)

        # NÃO fechar página aqui - será reutilizada para Seção 3

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

        # 1. Clicar em "Iniciar Seção 2"
        await page.wait_for_timeout(1000)
        await page.click('#btn-start-section2')
        await page.wait_for_timeout(500)

        # Scroll para o topo DEPOIS do click
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # 14. Screenshot início Seção 2 mobile
        await self.take_screenshot(page, '14-mobile-section2-start.png',
                                  'Início Seção 2 mobile', full_page=True)

        # 2. Abrir sidebar e capturar estado (viewport apenas, não full page)
        await page.click('#sidebar-toggle')
        await page.wait_for_timeout(500)  # Animação
        await self.take_screenshot(page, '15-mobile-section2-sidebar.png',
                                  'Sidebar - Seção 1 completa + Seção 2 em progresso', full_page=False)

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

        # NÃO fechar página aqui - será reutilizada para Seção 3

    async def run_section3_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 3 - Desktop"""
        print("\n👁️  Iniciando fluxo DESKTOP Seção 3...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 3"
        print("  ⏳ Aguardando 2s após conclusão da Seção 2...")
        await page.wait_for_timeout(2000)

        # Verificar se botão existe
        btn_exists = await page.locator('#btn-start-section3').count()
        print(f"  🔍 Botão 'Iniciar Seção 3' encontrado: {btn_exists > 0}")

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section3');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 3"
        print("  🖱️  Aguardando botão ficar visível (timeout 10s)...")
        btn_start = page.locator('#btn-start-section3')
        await btn_start.wait_for(state='visible', timeout=10000)
        print("  ✓ Botão visível! Clicando...")
        await page.wait_for_timeout(1000)  # Pausa dramática antes de clicar
        await btn_start.click()
        print("  ✓ Botão clicado!")

        # Aguardar input ficar habilitado (primeira pergunta carregada)
        print("  ⏳ Aguardando primeira pergunta carregar (timeout 30s)...")
        try:
            await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
            print("  ✓ Primeira pergunta carregada!")
        except Exception as e:
            # Se timeout, capturar screenshot de debug
            print(f"  ❌ ERRO: Timeout aguardando input habilitado: {e}")
            input_state = await page.evaluate("document.getElementById('user-input')?.disabled")
            print(f"  🔍 Estado do input: disabled={input_state}")
            await self.take_screenshot(page, 'DEBUG-section3-timeout.png', 'Debug - Timeout Seção 3', full_page=True)
            raise
        await page.wait_for_timeout(500)

        # Scroll para o topo DEPOIS do click (para garantir que header da Seção 3 apareça no vídeo)
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)  # Aguardar scroll e animação

        # 17. Screenshot logo após iniciar Seção 3
        await self.take_screenshot(page, '17-section3-start.png',
                                  'Início da Seção 3 - Pergunta 3.1', full_page=True)

        # 2. Responder perguntas da Seção 3 conforme test_scenarios.json
        section3_steps = self.config['sections'][2]['steps']
        i = 0
        while i < len(section3_steps):
            step_data = section3_steps[i]
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

            # Se espera falha, não avança - próximo step é a retry
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
                # Próximo step (i+1) deve ser a retry (sem incremento de i aqui)
            else:
                print(f"    ✓ Resposta aceita")

            i += 1

        # 3. Aguardar geração de texto da Seção 3 (LLM pode demorar até 35s)
        print("\n  ⏳ Aguardando geração de texto da Seção 3 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 3 aparecer
        section3_card = page.locator('#section3-card:not(.hidden)')
        await section3_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Verificar que todos os 3 accordions estão visíveis
        section1_card = page.locator('#section1-card')
        section2_card = page.locator('#section2-card')
        copy_all_btn = page.locator('#copy-all-button')

        # Assertions para validar estado
        is_section1_visible = await section1_card.is_visible()
        is_section2_visible = await section2_card.is_visible()
        is_section3_visible = await section3_card.is_visible()
        is_copy_all_visible = await copy_all_btn.is_visible()

        if not is_section1_visible:
            print("  ⚠️  WARNING: Seção 1 não está visível!")
        if not is_section2_visible:
            print("  ⚠️  WARNING: Seção 2 não está visível!")
        if not is_section3_visible:
            print("  ⚠️  WARNING: Seção 3 não está visível!")
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

        # Scroll até o final do texto da Seção 3
        await page.evaluate("""
            const container = document.querySelector('#section3-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)  # Pausar 3s mostrando todas as 3 seções

        # 5. Screenshot final (página completa com todas as 3 seções)
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '20-section3-final-all-sections.png',
                                  'BO Completo - Todas as 3 seções visíveis', full_page=True)

        print("\n✅ Fluxo Seção 3 desktop concluído!")

    async def run_section4_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 4 - Desktop"""
        print("\n🏠 Iniciando fluxo DESKTOP Seção 4...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 4"
        print("  ⏳ Aguardando 2s após conclusão da Seção 3...")
        await page.wait_for_timeout(2000)

        # Verificar se botão existe
        btn_exists = await page.locator('#btn-start-section4').count()
        print(f"  🔍 Botão 'Iniciar Seção 4' encontrado: {btn_exists > 0}")

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section4');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 4"
        print("  🖱️  Aguardando botão ficar visível (timeout 10s)...")
        btn_start = page.locator('#btn-start-section4')
        await btn_start.wait_for(state='visible', timeout=10000)
        print("  ✓ Botão visível! Clicando...")
        await page.wait_for_timeout(1000)  # Pausa dramática antes de clicar
        await btn_start.click()
        print("  ✓ Botão clicado!")

        # Aguardar input ficar habilitado (primeira pergunta carregada)
        print("  ⏳ Aguardando primeira pergunta carregar (timeout 30s)...")
        try:
            await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
            print("  ✓ Primeira pergunta carregada!")
        except Exception as e:
            # Se timeout, capturar screenshot de debug e informação do estado
            print(f"  ❌ ERRO: Timeout aguardando input habilitado: {e}")
            input_state = await page.evaluate("document.getElementById('user-input')?.disabled")
            print(f"  🔍 Estado do input: disabled={input_state}")
            await self.take_screenshot(page, 'DEBUG-section4-timeout.png', 'Debug - Timeout Seção 4', full_page=True)
            raise
        await page.wait_for_timeout(500)

        # Scroll para o topo DEPOIS do click (para garantir que header da Seção 4 apareça no vídeo)
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)  # Aguardar scroll e animação

        # 21. Screenshot logo após iniciar Seção 4
        await self.take_screenshot(page, '21-section4-start.png',
                                  'Início da Seção 4 - Pergunta 4.1', full_page=True)

        # 2. Responder perguntas da Seção 4 conforme test_scenarios.json
        section4_steps = self.config['sections'][3]['steps']
        i = 0
        while i < len(section4_steps):
            step_data = section4_steps[i]
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

            # Se espera falha, não avança - próximo step é a retry
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
                # Próximo step (i+1) deve ser a retry (sem incremento de i aqui)
            else:
                print(f"    ✓ Resposta aceita")

            i += 1

        # 3. Aguardar geração de texto da Seção 4 (LLM pode demorar até 35s)
        print("\n  ⏳ Aguardando geração de texto da Seção 4 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 4 aparecer
        section4_card = page.locator('#section4-card:not(.hidden)')
        await section4_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Verificar que todos os 4 accordions estão visíveis
        section1_card = page.locator('#section1-card')
        section2_card = page.locator('#section2-card')
        section3_card = page.locator('#section3-card')
        copy_all_btn = page.locator('#copy-all-button')

        # Assertions para validar estado
        is_section1_visible = await section1_card.is_visible()
        is_section2_visible = await section2_card.is_visible()
        is_section3_visible = await section3_card.is_visible()
        is_section4_visible = await section4_card.is_visible()
        is_copy_all_visible = await copy_all_btn.is_visible()

        if not is_section1_visible:
            print("  ⚠️  WARNING: Seção 1 não está visível!")
        if not is_section2_visible:
            print("  ⚠️  WARNING: Seção 2 não está visível!")
        if not is_section3_visible:
            print("  ⚠️  WARNING: Seção 3 não está visível!")
        if not is_section4_visible:
            print("  ⚠️  WARNING: Seção 4 não está visível!")
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

        # Scroll até o final do texto da Seção 4
        await page.evaluate("""
            const container = document.querySelector('#section4-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)  # Pausar 3s mostrando todas as 4 seções

        # 5. Screenshot final (página completa com todas as 4 seções)
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '24-section4-final-all-sections.png',
                                  'BO Completo - Todas as 4 seções visíveis', full_page=True)

        print("\n✅ Fluxo Seção 4 desktop concluído!")
        print("✅ BO COMPLETO - 4 seções (1 + 2 + 3 + 4) completas!")

        # NÃO fechar página aqui - será reutilizada para Seção 5

    async def run_section5_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 5 - Desktop"""
        print("\n🎯 Iniciando fluxo DESKTOP Seção 5...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 5"
        print("  ⏳ Aguardando 2s após conclusão da Seção 4...")
        await page.wait_for_timeout(2000)

        # Verificar se botão existe
        btn_exists = await page.locator('#btn-start-section5').count()
        print(f"  🔍 Botão 'Iniciar Seção 5' encontrado: {btn_exists > 0}")

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section5');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 5"
        print("  🖱️  Aguardando botão ficar visível (timeout 10s)...")
        btn_start = page.locator('#btn-start-section5')
        await btn_start.wait_for(state='visible', timeout=10000)
        print("  ✓ Botão visível! Clicando...")
        await page.wait_for_timeout(1000)  # Pausa dramática antes de clicar
        await btn_start.click()
        print("  ✓ Botão clicado!")

        # Aguardar input ficar habilitado (primeira pergunta carregada)
        print("  ⏳ Aguardando primeira pergunta carregar (timeout 30s)...")
        try:
            await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
            print("  ✓ Primeira pergunta carregada!")
        except Exception as e:
            print(f"  ❌ ERRO: Timeout aguardando input habilitado: {e}")
            await self.take_screenshot(page, 'DEBUG-section5-timeout.png', 'Debug - Timeout Seção 5', full_page=True)
            raise
        await page.wait_for_timeout(500)

        # Scroll para o topo DEPOIS do click
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # 30. Screenshot logo após iniciar Seção 5
        await self.take_screenshot(page, '30-section5-start.png',
                                  'Início da Seção 5 - Pergunta 5.1', full_page=True)

        # 2. Responder perguntas da Seção 5
        section5_steps = self.config['sections'][4]['steps']
        i = 0
        while i < len(section5_steps):
            step_data = section5_steps[i]
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

            # Se espera falha, não avança
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
            else:
                print(f"    ✓ Resposta aceita")

            i += 1

        # 3. Aguardar geração de texto da Seção 5
        print("\n  ⏳ Aguardando geração de texto da Seção 5 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 5 aparecer
        section5_card = page.locator('#section5-card:not(.hidden)')
        await section5_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Scroll suave até o container de textos
        await page.evaluate("""
            document.querySelector('#generated-sections-container').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            })
        """)

        await page.wait_for_timeout(2000)  # Aguardar scroll

        # Scroll até o final do texto da Seção 5
        await page.evaluate("""
            const container = document.querySelector('#section5-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)  # Pausar 3s mostrando seções

        # 5. Screenshot final (página completa com seções 1-5)
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '32-section5-final-all-sections.png',
                                  'BO até Seção 5 - Seções 1-5 visíveis', full_page=True)

        print("\n✅ Fluxo Seção 5 desktop concluído!")
        print("✅ BO até Seção 5 - Seções 1-5 completas!")

        # NÃO fechar página aqui - será reutilizada para Seção 6

    async def run_section6_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 6 - Desktop (Reação e Uso da Força)"""
        print("\n⚔️ Iniciando fluxo DESKTOP Seção 6...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 6"
        print("  ⏳ Aguardando 2s após conclusão da Seção 5...")
        await page.wait_for_timeout(2000)

        # Verificar se botão existe
        btn_exists = await page.locator('#btn-start-section6').count()
        print(f"  🔍 Botão 'Iniciar Seção 6' encontrado: {btn_exists > 0}")

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section6');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 6"
        print("  🖱️  Aguardando botão ficar visível (timeout 10s)...")
        btn_start = page.locator('#btn-start-section6')
        await btn_start.wait_for(state='visible', timeout=10000)
        print("  ✓ Botão visível! Clicando...")
        await page.wait_for_timeout(1000)
        await btn_start.click()
        print("  ✓ Botão clicado!")

        # Aguardar input ficar habilitado
        print("  ⏳ Aguardando primeira pergunta carregar (timeout 30s)...")
        try:
            await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
            print("  ✓ Primeira pergunta carregada!")
        except Exception as e:
            print(f"  ❌ ERRO: Timeout aguardando input habilitado: {e}")
            await self.take_screenshot(page, 'DEBUG-section6-timeout.png', 'Debug - Timeout Seção 6', full_page=True)
            raise
        await page.wait_for_timeout(500)

        # Scroll para o topo
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # Screenshot logo após iniciar Seção 6
        await self.take_screenshot(page, '30-section6-start.png',
                                  'Início da Seção 6 - Pergunta 6.1', full_page=True)

        # 2. Responder perguntas da Seção 6
        section6_steps = self.config['sections'][5]['steps']
        i = 0
        while i < len(section6_steps):
            step_data = section6_steps[i]
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

            # Se espera falha
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
            else:
                print(f"    ✓ Resposta aceita")

            i += 1

        # 3. Aguardar geração de texto da Seção 6
        print("\n  ⏳ Aguardando geração de texto da Seção 6 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 6 aparecer
        section6_card = page.locator('#section6-card:not(.hidden)')
        await section6_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Scroll suave até o container de textos
        await page.evaluate("""
            document.querySelector('#generated-sections-container').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            })
        """)

        await page.wait_for_timeout(2000)

        # Scroll até o final do texto da Seção 6
        await page.evaluate("""
            const container = document.querySelector('#section6-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)

        # 5. Screenshot final (página completa com todas as 6 seções)
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '32-section6-final.png',
                                  'Seção 6 completa', full_page=True)

        print("\n✅ Fluxo Seção 6 desktop concluído!")

    async def run_section7_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 7 - Desktop (Apreensões e Cadeia de Custódia)"""
        print("\n📦 Iniciando fluxo DESKTOP Seção 7...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 7"
        print("  ⏳ Aguardando 2s após conclusão da Seção 6...")
        await page.wait_for_timeout(2000)

        # Verificar se botão existe
        btn_exists = await page.locator('#btn-start-section7').count()
        print(f"  🔍 Botão 'Iniciar Seção 7' encontrado: {btn_exists > 0}")

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section7');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 7"
        print("  🖱️  Aguardando botão ficar visível (timeout 10s)...")
        btn_start = page.locator('#btn-start-section7')
        await btn_start.wait_for(state='visible', timeout=10000)
        print("  ✓ Botão visível! Clicando...")
        await page.wait_for_timeout(1000)
        await btn_start.click()
        print("  ✓ Botão clicado!")

        # Aguardar input ficar habilitado
        print("  ⏳ Aguardando primeira pergunta carregar (timeout 30s)...")
        try:
            await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
            print("  ✓ Primeira pergunta carregada!")
        except Exception as e:
            print(f"  ❌ ERRO: Timeout aguardando input habilitado: {e}")
            await self.take_screenshot(page, 'DEBUG-section7-timeout.png', 'Debug - Timeout Seção 7', full_page=True)
            raise
        await page.wait_for_timeout(500)

        # Scroll para o topo
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # Screenshot logo após iniciar Seção 7
        await self.take_screenshot(page, '35-section7-start.png',
                                  'Início da Seção 7 - Pergunta 7.1', full_page=True)

        # 2. Responder perguntas da Seção 7
        section7_steps = self.config['sections'][6]['steps']
        i = 0
        while i < len(section7_steps):
            step_data = section7_steps[i]
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

            # Se espera falha
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
            else:
                print(f"    ✓ Resposta aceita")

            i += 1

        # 3. Aguardar geração de texto da Seção 7
        print("\n  ⏳ Aguardando geração de texto da Seção 7 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 7 aparecer
        section7_card = page.locator('#section7-card:not(.hidden)')
        await section7_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Scroll suave até o container de textos
        await page.evaluate("""
            document.querySelector('#generated-sections-container').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            })
        """)

        await page.wait_for_timeout(2000)

        # Scroll até o final do texto da Seção 7
        await page.evaluate("""
            const container = document.querySelector('#section7-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)

        # 5. Screenshot final da Seção 7
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '38-section7-complete.png',
                                  'Seção 7 completa', full_page=True)

        print("\n✅ Fluxo Seção 7 desktop concluído!")

    async def run_section8_flow(self, page: Page, slow_mode: bool = False):
        """Executa fluxo completo da Seção 8 - Desktop (Condução e Pós-Ocorrência) - ÚLTIMA SEÇÃO"""
        print("\n⚖️ Iniciando fluxo DESKTOP Seção 8 (ÚLTIMA SEÇÃO)...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 8"
        print("  ⏳ Aguardando 2s após conclusão da Seção 7...")
        await page.wait_for_timeout(2000)

        # Verificar se botão existe
        btn_exists = await page.locator('#btn-start-section8').count()
        print(f"  🔍 Botão 'Iniciar Seção 8' encontrado: {btn_exists > 0}")

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section8');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 8"
        print("  🖱️  Aguardando botão ficar visível (timeout 10s)...")
        btn_start = page.locator('#btn-start-section8')
        await btn_start.wait_for(state='visible', timeout=10000)
        print("  ✓ Botão visível! Clicando...")
        await page.wait_for_timeout(1000)
        await btn_start.click()
        print("  ✓ Botão clicado!")

        # Aguardar input ficar habilitado
        print("  ⏳ Aguardando primeira pergunta carregar (timeout 30s)...")
        try:
            await page.wait_for_selector('#user-input:not([disabled])', timeout=30000)
            print("  ✓ Primeira pergunta carregada!")
        except Exception as e:
            print(f"  ❌ ERRO: Timeout aguardando input habilitado: {e}")
            await self.take_screenshot(page, 'DEBUG-section8-timeout.png', 'Debug - Timeout Seção 8', full_page=True)
            raise
        await page.wait_for_timeout(500)

        # Scroll para o topo
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # Screenshot logo após iniciar Seção 8
        await self.take_screenshot(page, '39-section8-start.png',
                                  'Início da Seção 8 - Pergunta 8.1', full_page=True)

        # 2. Responder perguntas da Seção 8
        section8_steps = self.config['sections'][7]['steps']
        i = 0
        while i < len(section8_steps):
            step_data = section8_steps[i]
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

            # Se espera falha
            if expect == 'fail':
                print(f"    ⚠️  Validação de erro esperada funcionou")
            else:
                print(f"    ✓ Resposta aceita")

            i += 1

        # 3. Aguardar geração de texto da Seção 8
        print("\n  ⏳ Aguardando geração de texto da Seção 8 (pode levar 15-30 segundos)...")

        try:
            await page.wait_for_selector('text=Gerando texto', timeout=5000)
        except:
            pass

        # Aguardar card da Seção 8 aparecer
        section8_card = page.locator('#section8-card:not(.hidden)')
        await section8_card.wait_for(state='visible', timeout=50000)
        await page.wait_for_timeout(1000)

        # 4. Scroll suave até o container de textos
        await page.evaluate("""
            document.querySelector('#generated-sections-container').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            })
        """)

        await page.wait_for_timeout(2000)

        # Scroll até o final do texto da Seção 8
        await page.evaluate("""
            const container = document.querySelector('#section8-text');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        """)

        await page.wait_for_timeout(3000)

        # 5. Screenshot final (página completa com todas as 8 seções - BO COMPLETO)
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '42-section8-final-bo-complete.png',
                                  'BO 100% COMPLETO - Todas as 8 seções finalizadas', full_page=True)

        print("\n✅ Fluxo Seção 8 desktop concluído!")
        print("🎉 BO 100% COMPLETO - 8 seções (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8) finalizadas!")

        # Fechar página para parar gravação de vídeo
        await page.close()

    async def run_mobile_section3_flow(self, page: Page, slow_mode: bool = False):
        """Fluxo mobile da Seção 3 (simplificado, sem screenshots de erros)"""
        print("\n👁️  Iniciando fluxo MOBILE Seção 3...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 3"
        await page.wait_for_timeout(2000)  # Aguardar processamento da Seção 2

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section3');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 3"
        await page.click('#btn-start-section3')

        # Aguardar input ficar habilitado (primeira pergunta carregada)
        await page.wait_for_selector('#user-input:not([disabled])', timeout=15000)
        await page.wait_for_timeout(500)

        # Scroll para o topo DEPOIS do click
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # 21. Screenshot início Seção 3 mobile
        await self.take_screenshot(page, '21-mobile-section3-start.png',
                                  'Início Seção 3 mobile', full_page=True)

        # 2. Abrir sidebar e capturar estado
        await page.click('#sidebar-toggle')
        await page.wait_for_timeout(500)  # Animação
        await self.take_screenshot(page, '22-mobile-section3-sidebar.png',
                                  'Sidebar - Seções 1+2 ✓ + Seção 3 em progresso', full_page=False)

        # Fechar sidebar usando JavaScript (mais confiável)
        await page.evaluate("""
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (sidebar) sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('open');
        """)
        await page.wait_for_timeout(500)

        # 3. Responder 8 perguntas rapidamente (apenas respostas válidas, sem erros)
        section3_steps = self.config['sections'][2]['steps']
        valid_steps = [s for s in section3_steps if s['expect'] == 'pass']

        for i, step_data in enumerate(valid_steps, 1):
            print(f"  📝 Respondendo pergunta 3.{i-1} (mobile)...")
            await self.fill_and_send(page, step_data['answer'], slow_typing=slow_mode)

            if i == len(valid_steps):
                # Última pergunta - aguardar geração de texto
                print(f"  ⏳ Aguardando geração de texto da Seção 3...")
                section3_card = page.locator('#section3-card:not(.hidden)')
                await section3_card.wait_for(state='visible', timeout=50000)
                await page.wait_for_timeout(1000)

                # Scroll suave até o container de textos
                await page.evaluate("""
                    document.querySelector('#generated-sections-container').scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    })
                """)

                await page.wait_for_timeout(2000)  # Aguardar scroll

                # Scroll para baixo no texto gerado da Seção 3
                await page.evaluate("""
                    const container = document.querySelector('#section3-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)

                await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto final
            else:
                await self.wait_for_api_response(page, timeout=12000)

        # 4. Screenshot final mobile com todas as 3 seções
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '23-mobile-section3-final.png',
                                  'Resultado final mobile - Todas as 3 seções', full_page=True)

        print("\n✅ Fluxo mobile Seção 3 concluído!")

    async def run_mobile_section4_flow(self, page: Page, slow_mode: bool = False):
        """Fluxo mobile da Seção 4 (simplificado, sem screenshots de erros)"""
        print("\n🏠 Iniciando fluxo MOBILE Seção 4...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 4"
        await page.wait_for_timeout(2000)  # Aguardar processamento da Seção 3

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section4');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 4"
        btn_start = page.locator('#btn-start-section4')
        await btn_start.wait_for(state='visible', timeout=10000)
        await page.wait_for_timeout(1000)
        await btn_start.click()

        # Aguardar input ficar habilitado (primeira pergunta carregada)
        await page.wait_for_selector('#user-input:not([disabled])', timeout=15000)
        await page.wait_for_timeout(500)

        # Scroll para o topo
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # 2. Responder perguntas da Seção 4
        section4_steps = self.config['sections'][3]['steps']
        for idx, step_data in enumerate(section4_steps):
            step = step_data['step']
            answer = step_data['answer']
            expect = step_data['expect']

            # Pular screenshots de erro no mobile
            if expect == 'fail':
                continue

            print(f"  [{step}] Respondendo (mobile): {answer[:40]}...")

            # Preencher e enviar
            await self.fill_and_send(page, answer, slow_typing=slow_mode)

            # Última pergunta: aguardar geração de texto
            if idx == len([s for s in section4_steps if s['expect'] == 'success']) - 1:
                print("\n  ⏳ Aguardando geração de texto da Seção 4 (mobile)...")

                # Aguardar card da Seção 4 aparecer
                section4_card = page.locator('#section4-card:not(.hidden)')
                await section4_card.wait_for(state='visible', timeout=50000)
                await page.wait_for_timeout(1000)

                # Scroll até o final do texto da Seção 4
                await page.evaluate("""
                    const container = document.querySelector('#section4-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)

                await page.wait_for_timeout(3000)  # Pausar 3s mostrando texto final
            else:
                await self.wait_for_api_response(page, timeout=12000)

        # 3. Screenshot final mobile com todas as 4 seções
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '27-mobile-section4-final.png',
                                  'Resultado final mobile - Todas as 4 seções', full_page=True)

        print("\n✅ Fluxo mobile Seção 4 concluído!")
        print("✅ Mobile: BO COMPLETO - 4 seções (1 + 2 + 3 + 4) completas!")

        # NÃO fechar página aqui - será reutilizada para Seção 5

    async def run_mobile_section5_flow(self, page: Page, slow_mode: bool = False):
        """Fluxo mobile da Seção 5 (simplificado, sem screenshots de erros)"""
        print("\n🎯 Iniciando fluxo MOBILE Seção 5...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 5"
        await page.wait_for_timeout(2000)  # Aguardar processamento da Seção 4

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section5');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 5"
        await page.click('#btn-start-section5')

        # Aguardar input ficar habilitado
        await page.wait_for_selector('#user-input:not([disabled])', timeout=15000)
        await page.wait_for_timeout(500)

        # Scroll para o topo
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # Screenshot início Seção 5 mobile
        await self.take_screenshot(page, '33-mobile-section5-start.png',
                                  'Início Seção 5 mobile', full_page=True)

        # 2. Responder perguntas da Seção 5 (apenas respostas válidas no mobile)
        section5_steps = self.config['sections'][4]['steps']
        for idx, step_data in enumerate(section5_steps):
            step = step_data['step']
            answer = step_data['answer']
            expect = step_data['expect']

            # Pular screenshots de erro no mobile
            if expect == 'fail':
                continue

            print(f"  [{step}] Respondendo (mobile): {answer[:40]}...")

            # Preencher e enviar
            await self.fill_and_send(page, answer, slow_typing=slow_mode)

            # Última pergunta: aguardar geração de texto
            if idx == len([s for s in section5_steps if s['expect'] != 'fail']) - 1:
                print("\n  ⏳ Aguardando geração de texto da Seção 5 (mobile)...")

                # Aguardar card da Seção 5 aparecer
                section5_card = page.locator('#section5-card:not(.hidden)')
                await section5_card.wait_for(state='visible', timeout=50000)
                await page.wait_for_timeout(1000)

                # Scroll até o final do texto da Seção 5
                await page.evaluate("""
                    const container = document.querySelector('#section5-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)

                await page.wait_for_timeout(3000)
            else:
                await self.wait_for_api_response(page, timeout=12000)

        # 3. Screenshot final mobile com seções 1-5
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '34-mobile-section5-final.png',
                                  'Resultado final mobile - Seções 1-5', full_page=True)

        print("\n✅ Fluxo mobile Seção 5 concluído!")
        print("✅ Mobile: BO até Seção 5 - Seções 1-5 completas!")

        # NÃO fechar página aqui - será reutilizada para Seção 6

    async def run_mobile_section6_flow(self, page: Page, slow_mode: bool = False):
        """Fluxo mobile da Seção 6 (simplificado, sem screenshots de erros)"""
        print("\n⚔️ Iniciando fluxo MOBILE Seção 6...")

        # 1. Aguardar e rolar até o botão "Iniciar Seção 6"
        await page.wait_for_timeout(2000)  # Aguardar processamento da Seção 5

        # Scroll para garantir que o botão esteja visível
        await page.evaluate("""
            const btn = document.getElementById('btn-start-section6');
            if (btn) {
                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        """)
        await page.wait_for_timeout(1000)

        # Clicar em "Iniciar Seção 6"
        await page.click('#btn-start-section6')

        # Aguardar input ficar habilitado
        await page.wait_for_selector('#user-input:not([disabled])', timeout=15000)
        await page.wait_for_timeout(500)

        # Scroll para o topo
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # Screenshot início Seção 6 mobile
        await self.take_screenshot(page, '35-mobile-section6-start.png',
                                  'Início Seção 6 mobile', full_page=True)

        # 2. Responder perguntas da Seção 6
        section6_steps = self.config['sections'][5]['steps']
        for idx, step_data in enumerate(section6_steps):
            step = step_data['step']
            answer = step_data['answer']
            expect = step_data['expect']

            # Pular screenshots de erro no mobile
            if expect == 'fail':
                continue

            print(f"  [{step}] Respondendo (mobile): {answer[:40]}...")

            # Preencher e enviar
            await self.fill_and_send(page, answer, slow_typing=slow_mode)

            # Última pergunta: aguardar geração de texto
            if idx == len([s for s in section6_steps if s['expect'] != 'fail']) - 1:
                print("\n  ⏳ Aguardando geração de texto da Seção 6 (mobile)...")

                # Aguardar card da Seção 6 aparecer
                section6_card = page.locator('#section6-card:not(.hidden)')
                await section6_card.wait_for(state='visible', timeout=50000)
                await page.wait_for_timeout(1000)

                # Scroll até o final do texto da Seção 6
                await page.evaluate("""
                    const container = document.querySelector('#section6-text');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)

                await page.wait_for_timeout(3000)
            else:
                await self.wait_for_api_response(page, timeout=12000)

        # 3. Screenshot final mobile com todas as 6 seções
        await page.evaluate('window.scrollTo(0, 0)')  # Voltar ao topo
        await page.wait_for_timeout(500)
        await self.take_screenshot(page, '36-mobile-section6-final.png',
                                  'BO COMPLETO mobile - Todas as 6 seções', full_page=True)

        print("\n✅ Fluxo mobile Seção 6 concluído!")
        print("✅ Mobile: BO COMPLETO - 6 seções (1 + 2 + 3 + 4 + 5 + 6) completas!")

        # Fechar página para parar gravação de vídeo
        await page.close()

    def create_readme(self):
        """Cria README.md com metadados"""
        readme_content = f"""# Screenshots - v{self.version}

**Data de geração:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

**Total:** 24 screenshots (15 desktop + 9 mobile) + vídeo (~6 minutos)

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

## 👁️ Desktop - Seção 3 (Campana - Vigilância Velada)
- `17-section3-start.png` - Início da Seção 3 (pergunta 3.1)
- `18-section3-graduation-error.png` - Erro de validação: sem graduação militar (pergunta 3.3)
- `19-section3-concrete-acts.png` - Progresso com descrição de atos concretos (pergunta 3.6)
- `20-section3-final-all-sections.png` - BO COMPLETO - Todas as 3 seções visíveis (full page)

## 📱 Mobile - Seção 1 (430x932 - iPhone 14 Pro Max)
- `11-mobile-section1-empty.png` - Layout mobile inicial
- `12-mobile-section1-sidebar.png` - Sidebar aberta (Seção 1)
- `13-mobile-section1-final.png` - Resultado final Seção 1 (full page)

## 📱 Mobile - Seção 2
- `14-mobile-section2-start.png` - Início da Seção 2 mobile
- `15-mobile-section2-sidebar.png` - Sidebar (Seção 1 ✓ + Seção 2 em progresso)
- `16-mobile-section2-final.png` - Resultado final com ambas seções (full page)

## 📱 Mobile - Seção 3
- `21-mobile-section3-start.png` - Início da Seção 3 mobile
- `22-mobile-section3-sidebar.png` - Sidebar (Seção 1+2 ✓ + Seção 3 em progresso)
- `23-mobile-section3-final.png` - BO COMPLETO mobile - Todas as 3 seções (full page)

## 🎬 Vídeo
- `demo.webm` - Demonstração completa (~6 minutos)
  - **Desktop:** Seção 1 (6 perguntas) → Seção 2 (8 perguntas) → Seção 3 (8 perguntas)
  - **Mobile:** Seção 1 → Seção 2 → Seção 3
  - Fluxo completo de BO (22 perguntas totais)
  - Testa validações (data, placa Mercosul, graduação militar, atos concretos)

## 🔧 Gerado com
- **Playwright** (automação de browser)
- **Python 3.13**
- **Backend:** {self.config['backend_url']}
- **Frontend:** {self.config['frontend_url']}
- **Versão:** {self.version}

## ✅ Validações Testadas
- ✅ Erro de validação ao editar (data inválida) - Seção 1
- ✅ Edição válida salva com sucesso - Seção 1
- ✅ Placa Mercosul inválida rejeitada (ABC123) - Seção 2
- ✅ Resposta sem graduação rejeitada (Seção 2 e 3)
- ✅ Atos concretos validados (rejeita generalizações) - Seção 3
- ✅ Persistência de textos gerados (3 seções visíveis)
- ✅ Botão "Copiar BO Completo" aparece após 3 seções completas
- ✅ Sidebar mostra progresso de todas as seções
- ✅ Fluxo E2E: 22 perguntas respondidas com sucesso
- ✅ Geração de texto via LLM funcionando para as 3 seções

## 📊 Cobertura de Testes

### Seção 1: Contexto da Ocorrência (6 perguntas)
- [x] Validação de data/hora
- [x] Edição de respostas
- [x] Geração de texto

### Seção 2: Abordagem a Veículo (8 perguntas)
- [x] Validação de placa Mercosul
- [x] Validação de graduação militar
- [x] Progresso com 8 perguntas
- [x] Geração de texto

### Seção 3: Campana (8 perguntas)
- [x] Pergunta condicional (3.1: SIM/NÃO)
- [x] Validação de graduação militar (3.3)
- [x] Validação de atos concretos (3.6)
- [x] Perguntas opcionais aceitam "NÃO" (3.7, 3.8)
- [x] Geração de texto

## 🚀 Fluxo Completo
1. **Desktop:** 5 screenshots Seção 1 → 5 screenshots Seção 2 → 4 screenshots Seção 3 = 14 desktop
2. **Mobile:** 3 screenshots Seção 1 → 3 screenshots Seção 2 → 3 screenshots Seção 3 = 9 mobile
3. **Vídeo:** Fluxo contínuo mostrando toda a interação
4. **Total:** 23 screenshots + 1 vídeo = 24 arquivos
"""

        readme_path = self.output_dir / 'README.md'
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"\n📝 README.md criado")
    
    async def run(self):
        """Executa automação completa"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)

            # Se modo rápido, preparar seções anteriores via API ANTES de abrir o browser com vídeo
            session_id_desktop = None
            session_id_mobile = None

            if self.start_section > 1:
                print(f"\n⚡ MODO RÁPIDO: Preparando Seções 1-{self.start_section - 1} via API...")

                # Preparar sessões para desktop e mobile (cada um precisa de sua própria sessão)
                session_id_desktop = await self.prepare_sections_via_api(self.start_section - 1)
                session_id_mobile = await self.prepare_sections_via_api(self.start_section - 1)

                if not session_id_desktop or not session_id_mobile:
                    print("❌ ERRO: Falha ao preparar seções via API!")
                    return

            # Configurar gravação de vídeo se não estiver desabilitado
            video_config = {}
            if not self.no_video:
                video_config = {
                    'record_video_dir': str(self.output_dir),
                    'record_video_size': {'width': 1280, 'height': 720}
                }

            context = await browser.new_context(**video_config)

            # Desktop: Seção 1 + Seção 2 + Seção 3
            page_desktop = await context.new_page()
            await page_desktop.set_viewport_size({'width': 1280, 'height': 720})

            if self.start_section == 1:
                # Fluxo normal: todas as seções com screenshots
                await self.run_desktop_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section2_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section3_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section4_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section5_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section6_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 2:
                # Restaurar Seção 1 instantaneamente, depois fazer Seção 2-6 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seção 1 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 1)

                # Screenshot final da Seção 1 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '05-section1-final-with-button.png',
                                          'Final Seção 1 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 2-8 normalmente
                await self.run_section2_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section3_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section4_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section5_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section6_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 3:
                # Restaurar Seções 1 e 2 instantaneamente, depois fazer Seção 3-6 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seções 1 e 2 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 2)

                # Screenshot final da Seção 2 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '10-section2-final-both-sections.png',
                                          'Final Seção 2 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 3-8 normalmente
                await self.run_section3_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section4_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section5_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section6_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 4:
                # Restaurar Seções 1, 2 e 3 instantaneamente, depois fazer Seção 4-6 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seções 1, 2 e 3 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 3)

                # Screenshot final da Seção 3 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '17-section3-start.png',
                                          'Final Seção 3 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 4-8 normalmente
                await self.run_section4_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section5_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section6_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 5:
                # Restaurar Seções 1-4 instantaneamente, depois fazer Seção 5 e 6 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seções 1-4 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 4)

                # Screenshot final da Seção 4 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '24-section4-final-all-sections.png',
                                          'Final Seção 4 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 5-8 normalmente
                await self.run_section5_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section6_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 6:
                # Restaurar Seções 1-5 instantaneamente, depois fazer Seção 6 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seções 1-5 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 5)

                # Screenshot final da Seção 5 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '32-section5-final-all-sections.png',
                                          'Final Seção 5 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 6-8 normalmente
                await self.run_section6_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 7:
                # Restaurar Seções 1-6 instantaneamente, depois fazer Seção 7-8 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seções 1-6 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 6)

                # Screenshot final da Seção 6 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '32-section6-final.png',
                                          'Final Seção 6 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 7-8 normalmente
                await self.run_section7_flow(page_desktop, slow_mode=not self.no_video)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)
            elif self.start_section == 8:
                # Restaurar Seções 1-7 instantaneamente, depois fazer Seção 8 com screenshots
                print("\n⚡ MODO RÁPIDO DESKTOP: Restaurando Seções 1-7 instantaneamente...")
                await page_desktop.goto(self.config['frontend_url'])
                await page_desktop.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_desktop, session_id_desktop, 7)

                # Screenshot final da Seção 7 (para contexto)
                await page_desktop.evaluate('window.scrollTo(0, 0)')
                await page_desktop.wait_for_timeout(500)
                await self.take_screenshot(page_desktop, '38-section7-complete.png',
                                          'Final Seção 7 (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 8 normalmente (última seção)
                await self.run_section8_flow(page_desktop, slow_mode=not self.no_video)

            # Mobile: Seção 1 + Seção 2 + Seção 3 + Seção 4
            page_mobile = await context.new_page()
            await page_mobile.set_viewport_size({'width': 430, 'height': 932})

            if self.start_section == 1:
                # Fluxo normal: todas as seções com screenshots
                await self.run_mobile_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section2_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section3_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section4_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section5_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section6_flow(page_mobile, slow_mode=not self.no_video)
            elif self.start_section == 2:
                # Restaurar Seção 1 instantaneamente
                print("\n⚡ MODO RÁPIDO MOBILE: Restaurando Seção 1 instantaneamente...")
                await page_mobile.goto(self.config['frontend_url'])
                await page_mobile.wait_for_timeout(1000)
                await self.inject_session_and_restore(page_mobile, session_id_mobile, 1)

                # Screenshot final da Seção 1 mobile
                await page_mobile.evaluate('window.scrollTo(0, 0)')
                await page_mobile.wait_for_timeout(500)
                await self.take_screenshot(page_mobile, '13-mobile-section1-final.png',
                                          'Final Seção 1 mobile (restaurada instantaneamente)', full_page=True)

                # Agora fazer Seção 2-6 normalmente
                await self.run_mobile_section2_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section3_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section4_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section5_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section6_flow(page_mobile, slow_mode=not self.no_video)
            elif self.start_section == 3:
                # Restaurar Seções 1 e 2 instantaneamente
                print("\n⚡ MODO RÁPIDO MOBILE: Restaurando Seções 1 e 2 instantaneamente...")
                try:
                    await page_mobile.goto(self.config['frontend_url'])
                    await page_mobile.wait_for_timeout(1000)
                    await self.inject_session_and_restore(page_mobile, session_id_mobile, 2)
                except Exception as e:
                    print(f"    ⚠️  Erro ao restaurar mobile (tentando novamente): {str(e)[:100]}")
                    # Tentar reconectar
                    try:
                        await page_mobile.goto(self.config['frontend_url'])
                        await page_mobile.wait_for_timeout(2000)
                        await self.inject_session_and_restore(page_mobile, session_id_mobile, 2)
                    except Exception as e2:
                        print(f"    ⚠️  Erro persistente no mobile, pulando testes mobile")

                # Screenshot final da Seção 2 mobile
                await page_mobile.evaluate('window.scrollTo(0, 0)')
                await page_mobile.wait_for_timeout(500)
                await self.take_screenshot(page_mobile, '16-mobile-section2-final.png',
                                          'Final Seção 2 mobile (preenchida rapidamente)', full_page=True)

                # Agora fazer Seção 3-6 normalmente
                await self.run_mobile_section3_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section4_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section5_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section6_flow(page_mobile, slow_mode=not self.no_video)
            elif self.start_section == 4:
                # Restaurar Seções 1, 2 e 3 instantaneamente
                print("\n⚡ MODO RÁPIDO MOBILE: Restaurando Seções 1, 2 e 3 instantaneamente...")
                try:
                    await page_mobile.goto(self.config['frontend_url'])
                    await page_mobile.wait_for_timeout(1000)
                    await self.inject_session_and_restore(page_mobile, session_id_mobile, 3)
                except Exception as e:
                    print(f"    ⚠️  Erro ao restaurar mobile (tentando novamente): {str(e)[:100]}")
                    # Tentar reconectar
                    try:
                        await page_mobile.goto(self.config['frontend_url'])
                        await page_mobile.wait_for_timeout(2000)
                        await self.inject_session_and_restore(page_mobile, session_id_mobile, 3)
                    except Exception as e2:
                        print(f"    ⚠️  Erro persistente no mobile, pulando testes mobile")

                # Screenshot final da Seção 3 mobile
                await page_mobile.evaluate('window.scrollTo(0, 0)')
                await page_mobile.wait_for_timeout(500)
                await self.take_screenshot(page_mobile, '23-mobile-section3-final.png',
                                          'Final Seção 3 mobile (restaurada rapidamente)', full_page=True)

                # Agora fazer Seção 4-6 normalmente
                await self.run_mobile_section4_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section5_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section6_flow(page_mobile, slow_mode=not self.no_video)
            elif self.start_section == 5:
                # Restaurar Seções 1-4 instantaneamente
                print("\n⚡ MODO RÁPIDO MOBILE: Restaurando Seções 1-4 instantaneamente...")
                try:
                    await page_mobile.goto(self.config['frontend_url'])
                    await page_mobile.wait_for_timeout(1000)
                    await self.inject_session_and_restore(page_mobile, session_id_mobile, 4)
                except Exception as e:
                    print(f"    ⚠️  Erro ao restaurar mobile (tentando novamente): {str(e)[:100]}")
                    # Tentar reconectar
                    try:
                        await page_mobile.goto(self.config['frontend_url'])
                        await page_mobile.wait_for_timeout(2000)
                        await self.inject_session_and_restore(page_mobile, session_id_mobile, 4)
                    except Exception as e2:
                        print(f"    ⚠️  Erro persistente no mobile, pulando testes mobile")

                # Screenshot final da Seção 4 mobile
                await page_mobile.evaluate('window.scrollTo(0, 0)')
                await page_mobile.wait_for_timeout(500)
                await self.take_screenshot(page_mobile, '27-mobile-section4-final.png',
                                          'Final Seção 4 mobile (restaurada rapidamente)', full_page=True)

                # Agora fazer Seção 5 e 6 normalmente
                await self.run_mobile_section5_flow(page_mobile, slow_mode=not self.no_video)
                await self.run_mobile_section6_flow(page_mobile, slow_mode=not self.no_video)
            elif self.start_section == 6:
                # Restaurar Seções 1-5 instantaneamente
                print("\n⚡ MODO RÁPIDO MOBILE: Restaurando Seções 1-5 instantaneamente...")
                try:
                    await page_mobile.goto(self.config['frontend_url'])
                    await page_mobile.wait_for_timeout(1000)
                    await self.inject_session_and_restore(page_mobile, session_id_mobile, 5)
                except Exception as e:
                    print(f"    ⚠️  Erro ao restaurar mobile (tentando novamente): {str(e)[:100]}")
                    # Tentar reconectar
                    try:
                        await page_mobile.goto(self.config['frontend_url'])
                        await page_mobile.wait_for_timeout(2000)
                        await self.inject_session_and_restore(page_mobile, session_id_mobile, 5)
                    except Exception as e2:
                        print(f"    ⚠️  Erro persistente no mobile, pulando testes mobile")

                # Screenshot final da Seção 5 mobile
                await page_mobile.evaluate('window.scrollTo(0, 0)')
                await page_mobile.wait_for_timeout(500)
                await self.take_screenshot(page_mobile, '34-mobile-section5-final.png',
                                          'Final Seção 5 mobile (restaurada rapidamente)', full_page=True)

                # Agora fazer Seção 6 normalmente
                await self.run_mobile_section6_flow(page_mobile, slow_mode=not self.no_video)

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
                print(f"✅ 28 screenshots + vídeo + README criados!")
                print(f"   • Desktop: 17 screenshots (Seção 1 + 2 + 3 + 4)")
                print(f"   • Mobile: 11 screenshots (Seção 1 + 2 + 3 + 4)")
                print(f"   • Vídeo: ~8 minutos (fluxo completo BO)")
            else:
                print(f"✅ 28 screenshots + README criados!")
                print(f"   • Desktop: 17 screenshots (Seção 1 + 2 + 3 + 4)")
                print(f"   • Mobile: 11 screenshots (Seção 1 + 2 + 3 + 4)")

def main():
    parser = argparse.ArgumentParser(description='Automação de screenshots e vídeo')
    parser.add_argument('--version', required=True, help='Versão do release (ex: v0.3.2)')
    parser.add_argument('--backend', default='http://localhost:8000', help='URL do backend')
    parser.add_argument('--no-video', action='store_true', help='Não gravar vídeo')
    parser.add_argument('--start-section', type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8], default=1,
                        help='Seção inicial (1-8). Seções anteriores serão preenchidas rapidamente sem screenshots.')

    args = parser.parse_args()

    automation = ReleaseAutomation(
        version=args.version,
        backend_url=args.backend,
        no_video=args.no_video,
        start_section=args.start_section
    )

    asyncio.run(automation.run())

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Teste de persistência de rascunho - Bug Report do usuário
Cenário:
1. Responder Seção 1 completa (6 perguntas)
2. Iniciar Seção 2 e responder até 2.7 (penúltima pergunta)
3. Recarregar página → Deve aparecer rascunho
4. Continuar e responder 2.8 (última pergunta)
5. Texto da Seção 2 é gerado
6. Recarregar página → NÃO deve aparecer rascunho (BO completo)

Executar: python test_draft_persistence.py
"""
import asyncio
import json
from playwright.async_api import async_playwright

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_step(step_num, description):
    print(f"\n{Colors.CYAN}[PASSO {step_num}]{Colors.END} {description}")

def print_success(message):
    print(f"{Colors.GREEN}[OK]{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERRO]{Colors.END} {message}")

def print_info(message):
    print(f"{Colors.YELLOW}  > {Colors.END} {message}")

async def check_draft_in_localstorage(page):
    """Verifica se há rascunho no localStorage"""
    draft_str = await page.evaluate("localStorage.getItem('bo_draft')")
    if draft_str:
        draft = json.loads(draft_str)
        return True, draft
    return False, None

async def clear_localstorage(page):
    """Limpa o localStorage"""
    await page.evaluate("localStorage.clear()")

async def wait_for_bot_message(page, timeout=5000):
    """Espera aparecer uma mensagem do bot"""
    await page.wait_for_selector('.message-container.justify-start', timeout=timeout)

async def send_message(page, text, expect_generation=False):
    """Envia uma mensagem no chat"""
    # Digitar
    await page.fill('#user-input', text)
    # Clicar no botão de enviar
    await page.click('#send-button')

    # Se espera geração de texto (última pergunta), aguardar mais tempo
    timeout = 40000 if expect_generation else 10000

    # Aguardar processamento (esperar botão voltar a ficar ativo)
    await page.wait_for_selector('#send-button:not([disabled])', timeout=timeout)
    # Aguardar um pouco para garantir que a resposta foi renderizada
    await asyncio.sleep(0.5)

async def run_test():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}  TESTE DE PERSISTÊNCIA DE RASCUNHO (Bug Fix v0.6.4){Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # ==================================================================
            # PASSO 1: Iniciar nova sessão e completar Seção 1
            # ==================================================================
            print_step(1, "Iniciar nova sessão e completar Seção 1")

            await page.goto('http://127.0.0.1:3000')
            print_info("Página carregada")

            # Limpar localStorage antes de começar
            await clear_localstorage(page)
            print_info("localStorage limpo")

            # Aguardar mensagem de boas-vindas
            await wait_for_bot_message(page)
            print_info("Mensagem de boas-vindas recebida")

            # Responder as 6 perguntas da Seção 1
            section1_answers = [
                "Dia 20 de dezembro de 2024, às 14:00",
                "Cabo João Silva e Soldado Pedro Santos, prefixo 12345",
                "Patrulhamento preventivo na região do Bairro Centro",
                "Ordem de serviço nº 456/2024 emitida pela DDU",
                "Rua das Flores, altura do nº 123, Bairro Centro",
                "Sim, local conhecido por tráfico de drogas, facção CV atua na área"
            ]

            for i, answer in enumerate(section1_answers, start=1):
                is_last = (i == 6)
                print_info(f"Respondendo 1.{i}: {answer[:50]}...")
                await send_message(page, answer, expect_generation=is_last)

            # Aguardar texto da Seção 1 ser gerado
            await page.wait_for_selector('#section1-text', timeout=30000)
            print_success("Seção 1 completa, texto gerado")

            # Verificar que há rascunho salvo
            has_draft, draft = await check_draft_in_localstorage(page)
            if has_draft:
                print_success(f"Rascunho salvo no localStorage (6 respostas)")
            else:
                print_error("ERRO: Rascunho não foi salvo!")
                return False

            # ==================================================================
            # PASSO 2: Iniciar Seção 2 e responder até 2.7 (penúltima)
            # ==================================================================
            print_step(2, "Iniciar Seção 2 e responder até penúltima pergunta (2.7)")

            # Clicar no botão "Iniciar Seção 2"
            await page.click('#btn-start-section2')
            print_info("Botão 'Iniciar Seção 2' clicado")

            # Aguardar primeira pergunta da Seção 2
            await asyncio.sleep(1)

            # Responder as 7 primeiras perguntas da Seção 2 (parar antes da última)
            section2_answers = [
                "SIM",  # 2.1
                "VW Gol branco, placa ABC-1D23",  # 2.2
                "Rua das Flores, altura do nº 100",  # 2.3
                "O Sargento Lucas viu o veículo em alta velocidade",  # 2.4
                "Foi gritado 'Parado, Polícia Militar!' pelo megafone",  # 2.5
                "Parou imediatamente",  # 2.6
                "O Cabo Nogueira revistou o porta-luvas e encontrou entorpecente"  # 2.7
            ]

            for i, answer in enumerate(section2_answers, start=1):
                print_info(f"Respondendo 2.{i}: {answer[:50]}...")
                await send_message(page, answer)

            print_success("Respondeu até 2.7 (penúltima pergunta)")

            # Verificar que há rascunho salvo (Seção 1 + Seção 2 incompleta)
            has_draft, draft = await check_draft_in_localstorage(page)
            if has_draft:
                section1_count = len([k for k in draft['answers'].keys() if k.startswith('1.')])
                section2_count = len([k for k in draft['answers'].keys() if k.startswith('2.')])
                print_success(f"Rascunho salvo: Seção 1: {section1_count}/6, Seção 2: {section2_count}/8")

                if section1_count != 6 or section2_count != 7:
                    print_error(f"ERRO: Contagem incorreta! Esperado S1:6, S2:7")
                    return False
            else:
                print_error("ERRO: Rascunho não foi salvo!")
                return False

            # ==================================================================
            # PASSO 3: Recarregar página → Deve aparecer modal de rascunho
            # ==================================================================
            print_step(3, "Recarregar página e verificar modal de rascunho")

            await page.reload()
            print_info("Página recarregada")

            # Aguardar modal de rascunho aparecer
            try:
                await page.wait_for_selector('#draft-modal:not(.hidden)', timeout=3000)
                print_success("Modal de rascunho apareceu")
            except:
                print_error("ERRO: Modal de rascunho NÃO apareceu!")
                return False

            # Clicar em "Continuar"
            await page.click('#draft-continue')
            print_info("Clicou em 'Continuar'")

            # Aguardar restauração
            await asyncio.sleep(3)
            print_success("Rascunho restaurado")

            # ==================================================================
            # PASSO 4: Responder última pergunta (2.8) e gerar texto
            # ==================================================================
            print_step(4, "Responder última pergunta (2.8) e gerar texto da Seção 2")

            # Responder última pergunta (esperar geração de texto)
            await send_message(page, "NÃO", expect_generation=True)
            print_info("Respondeu 2.8: NÃO")

            # Aguardar texto da Seção 2 ser gerado
            await page.wait_for_selector('#section2-text', timeout=30000)
            print_success("Seção 2 completa, texto gerado")

            # Aguardar um pouco para garantir que clearDraft() foi executado
            await asyncio.sleep(1)

            # Verificar que rascunho foi REMOVIDO
            has_draft, _ = await check_draft_in_localstorage(page)
            if not has_draft:
                print_success("Rascunho foi REMOVIDO do localStorage")
            else:
                print_error("ERRO: Rascunho ainda existe no localStorage!")
                return False

            # ==================================================================
            # PASSO 5: Recarregar página → NÃO deve aparecer modal de rascunho
            # ==================================================================
            print_step(5, "Recarregar página e verificar que NÃO aparece modal")

            await page.reload()
            print_info("Página recarregada")

            # Aguardar um pouco
            await asyncio.sleep(2)

            # Verificar se modal de rascunho NÃO apareceu
            modal_visible = await page.is_visible('#draft-modal:not(.hidden)')
            if not modal_visible:
                print_success("Modal de rascunho NAO apareceu (correto)")
            else:
                print_error("ERRO: Modal de rascunho APARECEU (deveria estar oculto)!")
                return False

            # Verificar que nova sessão foi iniciada
            welcome_msg = await page.locator('text=Olá! Vou te ajudar').count()
            if welcome_msg > 0:
                print_success("Nova sessao iniciada automaticamente")
            else:
                print_error("ERRO: Nova sessão não foi iniciada!")
                return False

            print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
            print(f"{Colors.GREEN}  [OK] TODOS OS TESTES PASSARAM!{Colors.END}")
            print(f"{Colors.GREEN}{'='*70}{Colors.END}")

            return True

        except Exception as e:
            print_error(f"Erro durante teste: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Aguardar um pouco antes de fechar para ver o resultado
            await asyncio.sleep(2)
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(run_test())
    exit(0 if result else 1)

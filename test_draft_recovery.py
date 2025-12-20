# -*- coding: utf-8 -*-
"""
Teste de recuperação de rascunhos - Seção 1 e Seção 2
Verifica se o sistema de LocalStorage funciona corretamente
"""
from playwright.sync_api import sync_playwright
import time

def test_draft_section1():
    """Testa recuperação de rascunho na Seção 1 (após 3 perguntas)"""
    print("[TESTE 1] Recuperacao de rascunho na Secao 1")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Capturar logs do console
        page.on('console', lambda msg: print(f"  [BROWSER] {msg.text}"))

        # Abrir aplicação
        page.goto('http://127.0.0.1:3000')
        page.wait_for_selector('#user-input', state='visible', timeout=5000)

        # Responder 3 perguntas da Seção 1
        answers = [
            '19/12/2025, 14h30min',
            'Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234',
            'Patrulhamento preventivo de combate ao tráfico de drogas'
        ]

        for i, answer in enumerate(answers, 1):
            print(f"  Respondendo pergunta 1.{i}...")
            page.fill('#user-input', answer)
            page.click('#send-button')
            time.sleep(2)  # Aguardar processamento

        # Verificar localStorage
        draft = page.evaluate('() => JSON.parse(localStorage.getItem("bo_inteligente_draft"))')
        print(f"  Rascunho salvo: {len(draft['answers'])} respostas")
        print(f"  currentSection: {draft.get('currentSection', 'AUSENTE')}")
        print(f"  version: {draft['version']}")

        # Fechar e reabrir página
        print("  Fechando e reabrindo pagina...")
        page.close()
        page = context.new_page()
        page.goto('http://127.0.0.1:3000')

        # Aguardar modal de rascunho
        time.sleep(1)
        modal_visible = page.is_visible('#draft-modal')

        if modal_visible:
            print("  Modal de rascunho apareceu!")

            # Verificar conteúdo do preview
            preview_text = page.text_content('#draft-preview')
            print(f"  Preview: {preview_text[:100]}...")

            # Clicar em "Continuar"
            page.click('#draft-continue')
            time.sleep(3)

            # Verificar se histórico foi restaurado
            messages = page.query_selector_all('.message-container')
            print(f"  {len(messages)} mensagens restauradas")

            # Verificar se está na pergunta 1.4
            chat_text = page.text_content('#chat-container')
            if 'ordem de serviço' in chat_text.lower() or 'copom' in chat_text.lower():
                print("  [OK] TESTE PASSOU: Rascunho Secao 1 restaurado corretamente!")
            else:
                print("  [FALHA] TESTE FALHOU: Nao continuou da pergunta correta")
                print(f"     Conteudo do chat (ultimas 200 chars): {chat_text[-200:]}")
        else:
            print("  [FALHA] TESTE FALHOU: Modal nao apareceu")

        browser.close()


def test_draft_section2():
    """Testa recuperação de rascunho na Seção 2 (após 2 perguntas)"""
    print("\n[TESTE 2] Recuperacao de rascunho na Secao 2")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Abrir aplicação
        page.goto('http://127.0.0.1:3000')
        page.wait_for_selector('#user-input', state='visible', timeout=5000)

        # Responder todas as 6 perguntas da Seção 1 rapidamente
        section1_answers = [
            '19/12/2025, 14h30min',
            'Sargento João Silva, Cabo Pedro Almeida, viatura 2234',
            'Patrulhamento de combate ao tráfico',
            'Ordem de serviço nº 145/2025, COPOM informou denúncia',
            'Rua das Acácias, 789, Bairro Santa Rita',
            'Sim, 12 registros anteriores, área do Comando Vermelho'
        ]

        print("  Preenchendo Secao 1 completa...")
        for answer in section1_answers:
            page.fill('#user-input', answer)
            page.click('#send-button')
            time.sleep(1.5)

        # Aguardar geração do texto (Seção 1 completa)
        time.sleep(4)

        # Clicar em "Iniciar Seção 2"
        print("  Iniciando Secao 2...")
        page.click('button:has-text("Iniciar Secao 2")')
        time.sleep(2)

        # Responder 2 perguntas da Seção 2
        section2_answers = [
            'SIM',
            'VW Gol branco, placa ABC-1D23'
        ]

        for i, answer in enumerate(section2_answers, 1):
            print(f"  Respondendo pergunta 2.{i-1 if i==1 else i}...")
            page.fill('#user-input', answer)
            page.click('#send-button')
            time.sleep(2)

        # Verificar localStorage
        draft = page.evaluate('() => JSON.parse(localStorage.getItem("bo_inteligente_draft"))')
        print(f"  Rascunho salvo: {len(draft['answers'])} respostas totais")
        print(f"  currentSection: {draft.get('currentSection', 'AUSENTE')}")
        print(f"  Respostas Secao 1: {len([k for k in draft['answers'] if k.startswith('1.')])}")
        print(f"  Respostas Secao 2: {len([k for k in draft['answers'] if k.startswith('2.')])}")

        # Fechar e reabrir página
        print("  Fechando e reabrindo pagina...")
        page.close()
        page = context.new_page()
        page.goto('http://127.0.0.1:3000')

        # Aguardar modal
        time.sleep(1)
        modal_visible = page.is_visible('#draft-modal')

        if modal_visible:
            print("  Modal de rascunho apareceu!")

            # Verificar preview (deve mostrar X/14)
            preview_text = page.text_content('#draft-preview')
            print(f"  Preview: {preview_text[:150]}...")

            if '/14' in preview_text:
                print("  [OK] Preview detectou Secao 2 (X/14)")
            else:
                print("  [AVISO] Preview nao detectou Secao 2 corretamente")

            # Clicar em "Continuar"
            page.click('#draft-continue')
            time.sleep(4)

            # Verificar se histórico foi restaurado
            messages = page.query_selector_all('.message-container')
            print(f"  {len(messages)} mensagens restauradas")

            # Verificar se está na pergunta 2.2 (placa/onde foi visto)
            chat_text = page.text_content('#chat-container')
            if 'placa' in chat_text.lower() or 'onde foi visto' in chat_text.lower():
                print("  [OK] TESTE PASSOU: Rascunho Secao 2 restaurado corretamente!")
            else:
                print("  [FALHA] TESTE FALHOU: Nao continuou da pergunta correta")
                print(f"     Conteudo do chat (ultimas 200 chars): {chat_text[-200:]}")
        else:
            print("  [FALHA] TESTE FALHOU: Modal nao apareceu")

        browser.close()


if __name__ == '__main__':
    print("=" * 60)
    print("TESTES DE RECUPERACAO DE RASCUNHOS")
    print("=" * 60)

    try:
        test_draft_section1()
        test_draft_section2()
        print("\n" + "=" * 60)
        print("[OK] TODOS OS TESTES CONCLUIDOS!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERRO] ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()

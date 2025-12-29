# -*- coding: utf-8 -*-
"""
Teste apenas da Seção 1 - para validação rápida
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
            time.sleep(5)  # Aguardar sincronização backend

            # Verificar se histórico foi restaurado
            messages = page.query_selector_all('.message-container')
            print(f"  {len(messages)} mensagens restauradas")

            # Verificar se está na pergunta 1.4
            chat_text = page.text_content('#chat-container')
            if 'ordem de serviço' in chat_text.lower() or 'copom' in chat_text.lower():
                print("  [OK] TESTE PASSOU: Rascunho Secao 1 restaurado corretamente!")
                print("  [SUCESSO] Pergunta 1.4 esta visivel no chat")
            else:
                print("  [FALHA] TESTE FALHOU: Nao continuou da pergunta correta")
                print(f"     Conteudo do chat (ultimas 300 chars): {chat_text[-300:]}")
        else:
            print("  [FALHA] TESTE FALHOU: Modal nao apareceu")

        browser.close()

if __name__ == '__main__':
    try:
        test_draft_section1()
        print("\n[OK] TESTE CONCLUIDO!")
    except Exception as e:
        print(f"\n[ERRO] ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

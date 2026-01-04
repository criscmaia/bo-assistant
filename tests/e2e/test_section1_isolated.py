# -*- coding: utf-8 -*-
"""
Teste apenas da Seção 1 - para validação rápida

v0.13.2+: Atualizado para suportar botões SingleChoice (SIM/NÃO)
"""
from playwright.sync_api import sync_playwright
import time


def submit_answer(page, answer):
    """
    Submete uma resposta - detecta se é campo de texto ou botão SingleChoice
    v0.13.2+: Suporta perguntas SIM/NÃO com botões
    """
    text_input_visible = page.is_visible('.text-input__field')

    if text_input_visible:
        page.fill('.text-input__field', answer)
        page.click('.text-input__button')
    else:
        single_choice_visible = page.is_visible('.single-choice')
        if single_choice_visible:
            answer_upper = answer.upper().strip()
            if answer_upper in ['SIM', 'YES']:
                page.click('.single-choice__option--yes')
            elif answer_upper in ['NÃO', 'NAO', 'NO']:
                page.click('.single-choice__option--no')
            else:
                page.click(f'.single-choice__option:has-text("{answer}")')
        else:
            raise Exception(f"Nenhum input encontrado para resposta: {answer}")


def test_draft_section1():
    """Testa recuperação de rascunho na Seção 1 (após 3 perguntas)"""
    print("[TESTE 1] Recuperacao de rascunho na Secao 1")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Capturar logs do console (com fallback para encoding)
        def safe_print_console(msg):
            try:
                print(f"  [BROWSER] {msg.text}")
            except UnicodeEncodeError:
                print(f"  [BROWSER] {msg.text.encode('ascii', 'replace').decode()}")
        page.on('console', safe_print_console)

        # Abrir aplicação
        page.goto('http://127.0.0.1:3000')
        # v0.13.2+: Seletores atualizados para nova estrutura de componentes
        page.wait_for_selector('.text-input__field', state='visible', timeout=10000)

        # Responder 3 perguntas da Seção 1
        answers = [
            '19/12/2025, 14h30min',
            'Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234',
            'Patrulhamento preventivo de combate ao tráfico de drogas'
        ]

        for i, answer in enumerate(answers, 1):
            print(f"  Respondendo pergunta 1.{i}...")
            submit_answer(page, answer)
            time.sleep(2)  # Aguardar processamento

        # Verificar localStorage (v0.13.2+: nova estrutura com sections)
        draft = page.evaluate('() => JSON.parse(localStorage.getItem("bo_draft"))')
        section1_answers = draft['sections']['1']['answers']
        print(f"  Rascunho salvo: {len(section1_answers)} respostas")
        print(f"  currentSectionId: {draft.get('currentSectionId', 'AUSENTE')}")
        print(f"  version: {draft['version']}")

        # Fechar e reabrir página
        print("  Fechando e reabrindo pagina...")
        page.close()
        page = context.new_page()
        page.goto('http://127.0.0.1:3000')

        # Aguardar modal de rascunho (v0.13.2+: seletores atualizados)
        time.sleep(2)
        modal_visible = page.is_visible('.draft-modal-overlay')

        if modal_visible:
            print("  Modal de rascunho apareceu!")

            # Verificar conteúdo do preview (v0.13.2+)
            preview_text = page.text_content('.draft-modal__preview')
            print(f"  Preview: {preview_text[:100]}...")

            # Clicar em "Continuar" (v0.13.2+)
            page.click('#draft-continue-btn')
            time.sleep(5)  # Aguardar sincronização backend

            # Verificar se histórico foi restaurado
            messages = page.query_selector_all('.message-container')
            print(f"  {len(messages)} mensagens restauradas")

            # Verificar se está na pergunta 1.4
            section_text = page.text_content('#section-container')
            if 'ordem de serviço' in section_text.lower() or 'copom' in section_text.lower() or 'motivação' in section_text.lower():
                print("  [OK] TESTE PASSOU: Rascunho Secao 1 restaurado corretamente!")
                print("  [SUCESSO] Pergunta 1.4 esta visivel")
            else:
                print("  [FALHA] TESTE FALHOU: Nao continuou da pergunta correta")
                print(f"     Conteudo da secao (ultimas 300 chars): {section_text[-300:]}")
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

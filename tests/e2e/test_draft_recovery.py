# -*- coding: utf-8 -*-
"""
Teste de recuperação de rascunhos - Seção 1 e Seção 2
Verifica se o sistema de LocalStorage funciona corretamente

v0.13.2+: Atualizado para suportar botões SingleChoice (SIM/NÃO)
"""
from playwright.sync_api import sync_playwright
import time


def submit_answer(page, answer):
    """
    Submete uma resposta - detecta se é campo de texto ou botão SingleChoice
    v0.13.2+: Suporta perguntas SIM/NÃO com botões
    """
    # Verificar se há campo de texto visível
    text_input_visible = page.is_visible('.text-input__field')

    if text_input_visible:
        # Campo de texto normal
        page.fill('.text-input__field', answer)
        page.click('.text-input__button')
    else:
        # Verificar se há botões SingleChoice (SIM/NÃO)
        single_choice_visible = page.is_visible('.single-choice')
        if single_choice_visible:
            # Clicar no botão correspondente baseado na resposta
            answer_upper = answer.upper().strip()
            if answer_upper in ['SIM', 'YES']:
                page.click('.single-choice__option--yes')
            elif answer_upper in ['NÃO', 'NAO', 'NO']:
                page.click('.single-choice__option--no')
            else:
                # Tentar encontrar botão pelo texto
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
            time.sleep(3)

            # Verificar se histórico foi restaurado
            messages = page.query_selector_all('.message-container')
            print(f"  {len(messages)} mensagens restauradas")

            # Verificar se está na pergunta 1.4
            section_text = page.text_content('#section-container')
            if 'ordem de serviço' in section_text.lower() or 'copom' in section_text.lower() or 'motivação' in section_text.lower():
                print("  [OK] TESTE PASSOU: Rascunho Secao 1 restaurado corretamente!")
            else:
                print("  [FALHA] TESTE FALHOU: Nao continuou da pergunta correta")
                print(f"     Conteudo da secao (ultimas 300 chars): {section_text[-300:]}")
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

        # Capturar logs do console para debug (com fallback para encoding)
        def safe_print_console(msg):
            try:
                print(f"  [BROWSER] {msg.text}")
            except UnicodeEncodeError:
                print(f"  [BROWSER] {msg.text.encode('ascii', 'replace').decode()}")
        page.on('console', safe_print_console)

        # Abrir aplicação
        page.goto('http://127.0.0.1:3000')
        # v0.13.2+: Aguardar primeiro input (pode ser texto ou botões)
        page.wait_for_selector('.input-component', state='visible', timeout=10000)

        # Responder todas as perguntas da Seção 1
        # v0.13.2+: Seção 1 tem 9 perguntas (1.5 e 1.9 são SIM/NÃO)
        section1_answers = [
            '19/12/2025, 14h30min',                                    # 1.1 - data/hora
            'Sargento João Silva, Cabo Pedro Almeida, viatura 2234',   # 1.2 - guarnição
            'Patrulhamento de combate ao tráfico',                     # 1.3 - acionamento
            'Ordem de serviço nº 145/2025, COPOM informou denúncia',   # 1.4 - motivação
            'NÃO',                                                     # 1.5 - há câmeras? (botão)
            'Rua das Acácias, 789, Bairro Santa Rita',                 # 1.6 - endereço
            'Bairro Centro, próximo ao mercado municipal',             # 1.7 - bairro/referência
            'Denúncia anônima de briga em andamento',                  # 1.8 - denúncia
            'NÃO'                                                      # 1.9 - local é interesse público? (botão)
        ]

        print("  Preenchendo Secao 1 completa (9 perguntas)...")
        for i, answer in enumerate(section1_answers, 1):
            print(f"    Pergunta 1.{i}: {answer[:30]}...")
            submit_answer(page, answer)
            time.sleep(1.5)

        # Aguardar geração do texto (Seção 1 completa)
        time.sleep(4)

        # Clicar em "Iniciar Seção 2"
        print("  Aguardando botao 'Iniciar Secao 2'...")

        # Aguardar mais tempo para geração de texto
        time.sleep(5)

        # Verificar se botão existe
        try:
            # Tentar encontrar o botão de transição
            page.wait_for_selector('#section-start-next', state='visible', timeout=10000)
            print("  Botao #section-start-next encontrado!")
            page.click('#section-start-next')
        except Exception as e:
            print(f"  [DEBUG] Botao #section-start-next nao encontrado: {e}")
            # Verificar se há .section-transition
            has_transition = page.is_visible('.section-transition')
            print(f"  [DEBUG] .section-transition visivel? {has_transition}")
            # Verificar HTML do container
            container_html = page.evaluate('() => document.getElementById("section-container")?.innerHTML?.substring(0, 500)')
            print(f"  [DEBUG] HTML container: {container_html}")
            raise

        time.sleep(2)

        # Responder perguntas da Seção 2
        # IMPORTANTE: Ao clicar em "Sim, havia veículo", a pergunta 2.1 já é
        # respondida automaticamente via preAnswerSkipQuestion. O teste deve
        # começar a partir da pergunta 2.2.
        section2_test_answers = [
            'Na Rua das Flores, durante patrulhamento',  # 2.2 - onde veículo foi visto
            'VW Gol branco, placa ABC-1D23'              # 2.3 - descrição veículo
        ]

        for i, answer in enumerate(section2_test_answers, 2):  # Começa em 2.2
            print(f"  Respondendo pergunta 2.{i}: {answer[:30]}...")
            submit_answer(page, answer)
            time.sleep(2)

        # Verificar localStorage (v0.13.2+: nova estrutura com sections)
        draft = page.evaluate('() => JSON.parse(localStorage.getItem("bo_draft"))')
        section1_answers = draft['sections']['1']['answers']
        section2_answers = draft['sections'].get('2', {}).get('answers', {})
        print(f"  Rascunho salvo: {len(section1_answers) + len(section2_answers)} respostas totais")
        print(f"  currentSectionId: {draft.get('currentSectionId', 'AUSENTE')}")
        print(f"  Respostas Secao 1: {len(section1_answers)}")
        print(f"  Respostas Secao 2: {len(section2_answers)}")

        # Fechar e reabrir página
        print("  Fechando e reabrindo pagina...")
        page.close()
        page = context.new_page()
        page.goto('http://127.0.0.1:3000')

        # Aguardar modal (v0.13.2+: seletores atualizados)
        time.sleep(2)
        modal_visible = page.is_visible('.draft-modal-overlay')

        if modal_visible:
            print("  Modal de rascunho apareceu!")

            # Verificar preview (v0.13.2+: seletor atualizado)
            preview_text = page.text_content('.draft-modal__preview')
            print(f"  Preview: {preview_text[:150]}...")

            # Preview pode não mostrar toda a informação - verificação básica
            if preview_text and len(preview_text) > 50:
                print("  [OK] Preview tem conteudo do rascunho")
            else:
                print("  [AVISO] Preview vazio ou muito curto")

            # Clicar em "Continuar" (v0.13.2+: seletor atualizado)
            page.click('#draft-continue-btn')
            time.sleep(4)

            # Verificar se histórico foi restaurado
            messages = page.query_selector_all('.message-container')
            print(f"  {len(messages)} mensagens restauradas")

            # Verificar se está na pergunta 2.4 (quem viu o veículo)
            # Respondemos 2.2 (onde) e 2.3 (placa), então próxima é 2.4
            section_text = page.text_content('#section-container')
            if 'quem' in section_text.lower() or 'equipe' in section_text.lower() or 'viu' in section_text.lower():
                print("  [OK] TESTE PASSOU: Rascunho Secao 2 restaurado corretamente!")
            else:
                print("  [FALHA] TESTE FALHOU: Nao continuou da pergunta correta")
                print(f"     Esperava pergunta 2.4 (quem viu o veiculo)")
                print(f"     Conteudo da secao (ultimas 300 chars): {section_text[-300:]}")
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

# -*- coding: utf-8 -*-
import requests
import json

API_BASE = "http://localhost:8000"

# Respostas de teste
SECTION1_ANSWERS = [
    "19/12/2025, 14h30min",
    "Sargento Silva, Cabo Almeida e Soldado Faria, viatura 2234",
    "Patrulhamento preventivo de combate ao tráfico de drogas",
    "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.",
    "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG",
    "Sim, local consta em 12 registros anteriores de tráfico de drogas. Há denúncias recorrentes de comercialização de entorpecentes. Área sob influência da facção Comando Vermelho segundo relatórios de inteligência."
]

SECTION2_ANSWERS = [
    "SIM",
    "VW Gol branco, placa ABC-1D23, ano 2018",
    "Na Rua das Acácias, esquina com Avenida Brasil, próximo ao Bar do João, Bairro Santa Rita",
    "O Sargento Silva visualizou o veículo transitando em alta velocidade pela Rua das Acácias. O condutor mudou bruscamente o sentido de direção ao notar a viatura e acelerou tentando fugir.",
    "Foi acionada a sirene da viatura e o Sargento Silva utilizou o megafone ordenando 'Parado, Polícia Militar! Encoste o veículo imediatamente!'",
    "O condutor acelerou tentando fugir pela Avenida Brasil, percorreu aproximadamente 300 metros em alta velocidade, desobedeceu dois semáforos vermelhos e só parou após cercar o veículo em um beco sem saída.",
    "O Cabo Almeida procedeu a abordagem ao motorista determinando que saísse do veículo com as mãos na cabeça. O Soldado Faria realizou busca no interior do veículo, revistando porta-luvas, painel, banco traseiro e porta-malas. No banco do motorista, embaixo do assento, foram localizados 28 invólucros plásticos contendo substância análoga à cocaína.",
    "Consultado o sistema REDS, consta registro de furto do veículo em Betim/MG, REDS nº 45678/2024 de 10/11/2024. Placa original BCD-5E67."
]

def test_complete_flow():
    print("=" * 80)
    print("TESTE COMPLETO - BO INTELIGENTE v0.5.0")
    print("=" * 80)

    # 1. Nova sessão
    print("\n[1] Iniciando nova sessao...")
    r = requests.post(f"{API_BASE}/new_session")
    data = r.json()
    session_id = data["session_id"]
    bo_id = data["bo_id"]
    print(f"[OK] Session ID: {session_id}")
    print(f"[OK] BO ID: {bo_id}")

    # 2. Seção 1 - 6 perguntas
    print("\n" + "=" * 80)
    print("SECAO 1 - CONTEXTO DA OCORRENCIA")
    print("=" * 80)

    for i, answer in enumerate(SECTION1_ANSWERS, 1):
        print(f"\n1.{i} - Enviando resposta...")
        print(f"   Resposta: {answer[:60]}{'...' if len(answer) > 60 else ''}")

        r = requests.post(f"{API_BASE}/chat", json={
            "session_id": session_id,
            "message": answer,
            "current_section": 1,
            "llm_provider": "gemini"
        })

        result = r.json()

        if result.get("validation_error"):
            print(f"   [ERRO] {result['validation_error']}")
            return False
        elif result.get("is_section_complete"):
            print(f"   [OK] Secao 1 completa!")
            print(f"\nTEXTO GERADO (Secao 1):")
            print("-" * 80)
            print(result["generated_text"])
            print("-" * 80)
            break
        else:
            print(f"   [OK] Aceita! Proxima pergunta: {result.get('question', 'N/A')[:50]}...")

    # 3. Iniciar Seção 2
    print("\n" + "=" * 80)
    print("INICIANDO SECAO 2 - ABORDAGEM A VEICULO")
    print("=" * 80)

    r = requests.post(f"{API_BASE}/start_section/2", json={"session_id": session_id})
    data = r.json()
    print(f"[OK] Secao 2 iniciada!")
    print(f"   Primeira pergunta: {data['question']}")

    # 4. Seção 2 - 8 perguntas
    for i, answer in enumerate(SECTION2_ANSWERS):
        step = f"2.{i}"
        print(f"\n{step} - Enviando resposta...")
        print(f"   Resposta: {answer[:60]}{'...' if len(answer) > 60 else ''}")

        r = requests.post(f"{API_BASE}/chat", json={
            "session_id": session_id,
            "message": answer,
            "current_section": 2,
            "llm_provider": "gemini"
        })

        result = r.json()

        if result.get("validation_error"):
            print(f"   [ERRO] {result['validation_error']}")
            print(f"   [INFO] Sugestao: Ajustar validacao para aceitar esta resposta")
            return False
        elif result.get("is_section_complete"):
            print(f"   [OK] Secao 2 completa!")
            print(f"\nTEXTO GERADO (Secao 2):")
            print("-" * 80)
            print(result.get("generated_text", "TEXTO NAO GERADO"))
            print("-" * 80)
            break
        else:
            print(f"   [OK] Aceita! Proxima pergunta: {result.get('question', 'N/A')[:50]}...")

    print("\n" + "=" * 80)
    print("TESTE COMPLETO FINALIZADO COM SUCESSO!")
    print("=" * 80)
    print(f"\nResumo:")
    print(f"   [OK] Secao 1: 6 perguntas respondidas + texto gerado")
    print(f"   [OK] Secao 2: 8 perguntas respondidas + texto gerado")
    print(f"   [OK] BO ID: {bo_id}")
    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERRO CRITICO] {e}")
        import traceback
        traceback.print_exc()
        exit(1)

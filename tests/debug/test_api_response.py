"""
Teste simples: captura resposta da API ao completar seção
"""
import requests
import json

# Iniciar nova sessão
print("=== Iniciando nova sessão ===")
response = requests.post("http://localhost:8000/new_session")
session_data = response.json()
session_id = session_data["session_id"]
print(f"Session ID: {session_id}")

# Responder todas as perguntas da seção 1
perguntas = [
    "19/12/2025, 14h30min, quinta-feira",
    "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
    "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão",
    "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.",
    "SIM",  # 1.5
    "Base Operacional do 16º BPM, localizada na Avenida Brasil, 1234, Bairro Centro",  # 1.5.1
    "Não houve alterações durante o deslocamento",  # 1.5.2
    "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG",
    "Sim, local consta em 12 registros anteriores de tráfico",
    "Área sob influência da facção Comando Vermelho",
    "SIM",  # 1.9
    "Escola Estadual João XXIII",  # 1.9.1
    "Aproximadamente 300 metros"  # 1.9.2
]

print("\n=== Respondendo perguntas da Seção 1 ===")
for i, resposta in enumerate(perguntas, 1):
    payload = {
        "session_id": session_id,
        "message": resposta,
        "llm_provider": "groq"
    }

    response = requests.post("http://localhost:8000/chat", json=payload)
    data = response.json()

    print(f"{i}. {resposta[:50]}... -> {data.get('current_step', 'N/A')}")

    # Na última resposta, verificar se tem generated_text
    if i == len(perguntas):
        print("\n=== RESPOSTA FINAL (última pergunta) ===")
        print(f"Status Code: {response.status_code}")
        print(f"is_section_complete: {data.get('is_section_complete')}")
        print(f"generated_text presente: {'generated_text' in data}")

        if 'generated_text' in data:
            texto = data['generated_text']
            print(f"generated_text length: {len(texto) if texto else 0}")
            if texto:
                print(f"generated_text (primeiros 200 chars): {texto[:200]}")
            else:
                print("generated_text está VAZIO ou None!")
        else:
            print("generated_text NÃO está na resposta!")

        print(f"\nResposta completa:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

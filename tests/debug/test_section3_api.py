"""
Teste focado na Seção 3 - verificar se API retorna generated_text
"""
import requests
import json

print("=== Teste API - Secao 3 ===\n")

# Nova sessão
response = requests.post("http://localhost:8000/new_session")
session_data = response.json()
session_id = session_data["session_id"]
print(f"Session ID: {session_id}\n")

# Completar S1
print("Completando S1...")
s1_perguntas = [
    "19/12/2025, 14h30min, quinta-feira",
    "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
    "Via 190, DDU, Patrulhamento preventivo, Mandado de prisão",
    "Ordem de serviço nº 145/2025 determinava patrulhamento",
    "SIM",
    "Base Operacional do 16º BPM",
    "Não houve alterações",
    "Rua das Acácias, 789",
    "Sim, 12 registros",
    "Área sob influência da facção Comando Vermelho",
    "SIM",
    "Escola Estadual João XXIII",
    "Aproximadamente 300 metros"
]

for resp in s1_perguntas:
    r = requests.post("http://localhost:8000/chat", json={"session_id": session_id, "message": resp, "llm_provider": "groq"})

print("S1 completa\n")

# Iniciar S2
print("Iniciando S2...")
r = requests.post("http://localhost:8000/start_section/2", json={"session_id": session_id})
print(f"  status: {r.status_code}\n")

# Completar S2
print("Completando S2...")
s2_perguntas = [
    "Na Rua das Acácias, esquina com Avenida Brasil",
    "VW Gol branco, placa ABC-1D23, ano 2018",
    "O Sargento Silva visualizou o veículo",
    "O condutor acelerou bruscamente tentando fugir",
    "Foi acionada a sirene da viatura",
    "O condutor acelerou tentando fugir",
    "Só parou após cercar o veículo em um beco",
    "O Soldado Carvalho procedeu à busca",
    "O Soldado Carvalho encontrou 10 porções de crack",
    "O condutor afirmou que não sabia",
    "O Sargento Silva deu voz de prisão",
    "O veículo estava com documentação regular"
]

for resp in s2_perguntas:
    r = requests.post("http://localhost:8000/chat", json={"session_id": session_id, "message": resp, "llm_provider": "groq"})

print("S2 completa\n")

# Iniciar S3
print("Iniciando S3...")
r = requests.post("http://localhost:8000/start_section/3", json={"session_id": session_id})
print(f"  status: {r.status_code}")
resp_data = r.json()
print(f"  first_question: {resp_data.get('first_question', 'N/A')}")
print(f"  current_section: {resp_data.get('current_section', 'N/A')}\n")

# Completar S3
print("Completando S3...")
s3_perguntas = [
    "aproximadamente 30 minutos",
    "de dentro da viatura, a 50 metros do local",
    "Observamos movimentação constante de pessoas",
    "aproximadamente 5 pessoas",
    "SIM",
    "Foram observadas 3 transações entre diferentes pessoas"
]

for i, resp in enumerate(s3_perguntas, 1):
    payload = {"session_id": session_id, "message": resp, "llm_provider": "groq", "current_section": 3}
    r = requests.post("http://localhost:8000/chat", json=payload)
    data = r.json()

    print(f"  {i}. {resp[:40]}... -> {data.get('current_step', 'N/A')}")

    if i == len(s3_perguntas):
        print(f"\n=== RESPOSTA FINAL S3 ===")
        print(f"Status: {r.status_code}")
        print(f"is_section_complete: {data.get('is_section_complete')}")
        print(f"generated_text presente: {'generated_text' in data}")

        if 'generated_text' in data:
            texto = data['generated_text']
            if texto:
                print(f"generated_text length: {len(texto)}")
                print(f"Primeiros 200 chars: {texto[:200]}")
            else:
                print(f"generated_text VAZIO ou None!")
                print(f"Valor: {repr(texto)}")

        print(f"\n=== RESPOSTA COMPLETA ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))

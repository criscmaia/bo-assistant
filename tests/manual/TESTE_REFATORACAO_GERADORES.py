"""
Teste de integração para validar refatoração Template Method Pattern
Testa os geradores das seções 1-4 sem precisar do servidor web
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.llm_service import LLMService

def test_section1_generator():
    """Testa gerador da seção 1"""
    print("\n=== TESTE: Section1Generator ===")

    service = LLMService()

    # Dados mínimos para seção 1
    section_data = {
        "1.1": "22/03/2025 21:11",
        "1.2": "Sgt Silva e Cb Almeida, prefixo 1234",
        "1.3": "COPOM",
        "1.4": "Denúncia anônima de tráfico",
        "1.5": "NÃO",
        "1.6": "Rua das Flores, 123",
        "1.7": "NÃO",
        "1.8": "NÃO",
        "1.9": "NÃO",
    }

    try:
        # Testar com provider inexistente (deve dar erro)
        try:
            service.generate_section_text(1, section_data, "invalid")
            print("❌ FALHOU: Deveria rejeitar provider inválido")
            return False
        except ValueError as e:
            print(f"✓ ValueError esperado: {str(e)[:50]}...")

        # Testar seção inexistente
        try:
            service.generate_section_text(99, section_data, "groq")
            print("❌ FALHOU: Deveria rejeitar seção inexistente")
            return False
        except ValueError as e:
            print(f"✓ ValueError esperado: {str(e)[:50]}...")

        # Testar que prompt foi construído (não chama API de verdade)
        generator = service._generators[1]
        prompt = generator._build_prompt(section_data)

        if not prompt:
            print("❌ FALHOU: Prompt vazio")
            return False

        if "sexta-feira, 22 de março de 2025" not in prompt:
            print("❌ FALHOU: Data não foi enriquecida corretamente")
            return False

        print("✓ Prompt construído corretamente")
        print(f"✓ Tamanho do prompt: {len(prompt)} chars")

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_section2_skip_logic():
    """Testa skip logic da seção 2"""
    print("\n=== TESTE: Section2Generator Skip Logic ===")

    service = LLMService()

    # Seção 2 com skip (não havia veículo)
    section_data_skip = {"2.1": "NÃO"}

    try:
        result = service.generate_section_text(2, section_data_skip, "groq")

        if result != "":
            print(f"❌ FALHOU: Deveria retornar vazio, retornou: '{result[:50]}'")
            return False

        print("✓ Skip logic funcionando (retornou vazio)")

        # Seção 2 sem skip (havia veículo)
        section_data_no_skip = {
            "2.1": "SIM",
            "2.2": "Rua X",
            "2.3": "VW Gol branco ABC-1234",
        }

        generator = service._generators[2]
        prompt = generator._build_prompt(section_data_no_skip)

        if not prompt:
            print("❌ FALHOU: Deveria construir prompt quando 2.1=SIM")
            return False

        print("✓ Prompt construído quando não skip")

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_section3_skip_logic():
    """Testa skip logic da seção 3"""
    print("\n=== TESTE: Section3Generator Skip Logic ===")

    service = LLMService()

    # Seção 3 com skip (não houve campana)
    section_data_skip = {"3.1": "NÃO"}

    try:
        result = service.generate_section_text(3, section_data_skip, "groq")

        if result != "":
            print(f"❌ FALHOU: Deveria retornar vazio, retornou: '{result[:50]}'")
            return False

        print("✓ Skip logic funcionando (retornou vazio)")
        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_section4_skip_logic():
    """Testa skip logic da seção 4"""
    print("\n=== TESTE: Section4Generator Skip Logic ===")

    service = LLMService()

    # Seção 4 com skip (não houve entrada em domicílio)
    section_data_skip = {"4.1": "NÃO"}

    try:
        result = service.generate_section_text(4, section_data_skip, "groq")

        if result != "":
            print(f"❌ FALHOU: Deveria retornar vazio, retornou: '{result[:50]}'")
            return False

        print("✓ Skip logic funcionando (retornou vazio)")
        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_all_generators_initialized():
    """Testa que todos os 4 geradores foram inicializados"""
    print("\n=== TESTE: Inicialização de Geradores ===")

    service = LLMService()

    expected_sections = [1, 2, 3, 4]

    for section in expected_sections:
        if section not in service._generators:
            print(f"❌ FALHOU: Gerador da seção {section} não inicializado")
            return False

    print(f"✓ Todos os {len(expected_sections)} geradores inicializados")
    return True

def main():
    print("="*60)
    print("TESTES DE VALIDAÇÃO - REFATORAÇÃO TEMPLATE METHOD")
    print("="*60)

    tests = [
        ("Inicialização de Geradores", test_all_generators_initialized),
        ("Section1Generator", test_section1_generator),
        ("Section2 Skip Logic", test_section2_skip_logic),
        ("Section3 Skip Logic", test_section3_skip_logic),
        ("Section4 Skip Logic", test_section4_skip_logic),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ ERRO INESPERADO: {e}")
            results.append((name, False))

    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = "✓ OK" if p else "✗ FALHOU"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} testes passaram")

    if passed == total:
        print("\n✓ TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n✗ {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())

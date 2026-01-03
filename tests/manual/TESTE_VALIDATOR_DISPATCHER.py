"""
Teste simples para validar o validator_dispatcher.py
Testa se o dispatcher consegue retornar os validadores corretos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.validator_dispatcher import get_validator, validate_answer

def test_get_validator():
    """Testa get_validator() para todas as seções"""
    print("\n=== TESTE: get_validator() ===")

    try:
        # Testar seções 1-4 (as que estão ativas)
        for section in [1, 2, 3, 4]:
            validator = get_validator(section)
            if validator is None:
                print(f"FALHOU: Seção {section} retornou None")
                return False
            print(f"OK: Seção {section} - {validator.__name__}")

        # Testar seção inválida
        try:
            get_validator(99)
            print("FALHOU: Deveria lançar ValueError para seção 99")
            return False
        except ValueError as e:
            print(f"OK: ValueError esperado para seção 99 - {str(e)[:50]}...")

        return True

    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_validate_answer():
    """Testa validate_answer() helper function"""
    print("\n=== TESTE: validate_answer() ===")

    try:
        # Testar validação válida (seção 1, pergunta 1.1 com data válida)
        is_valid, error = validate_answer(1, "1.1", "22/03/2025 21:11")
        if not is_valid:
            print(f"FALHOU: Data válida foi rejeitada - {error}")
            return False
        print("OK: Data válida aceita")

        # Testar validação inválida (seção 1, pergunta 1.1 com data inválida)
        is_valid, error = validate_answer(1, "1.1", "data inválida")
        if is_valid:
            print("FALHOU: Data inválida foi aceita")
            return False
        print(f"OK: Data inválida rejeitada - {error[:50]}...")

        return True

    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    print("="*60)
    print("TESTES - VALIDATOR DISPATCHER")
    print("="*60)

    tests = [
        ("get_validator()", test_get_validator),
        ("validate_answer()", test_validate_answer),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"ERRO INESPERADO: {e}")
            results.append((name, False))

    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = "OK" if p else "FALHOU"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} testes passaram")

    if passed == total:
        print("\nTODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n{total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())

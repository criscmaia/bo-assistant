# Arquivo de Documentação Anterior

Este diretório contém cópias de versões anteriores da documentação do BO Inteligente, preservadas para referência histórica e auditoria.

## Estrutura

### `v0.12.9/`
Snapshot completo da documentação na versão **v0.12.9** (30 de dezembro de 2024):
- README.md
- DEVELOPMENT.md
- CHANGELOG.md
- API.md
- SETUP.md
- ARCHITECTURE.md
- TESTING.md
- ROADMAP.md

Esta era a versão antes da implementação completa do **Redesign UX** (v0.13.0+).

### `redesign-proposal/`
Propostas e planos do Redesign UX (12 arquivos), preservados como referência histórica:
- PROPOSTA_REDESIGN_UX_BO_INTELIGENTE.md
- PLANO_IMPLEMENTACAO_REDESIGN_UX.md
- FASE_0_PREPARACAO.md até FASE_8_REFATORACAO.md
- STATUS_IMPLEMENTACAO.md

Estes documentos representam o planejamento original do redesign que foi implementado na v0.13.0.

### `status-snapshots/`
Snapshots de status durante o desenvolvimento (3 arquivos):
- STATUS-FINAL-v0.12.11.md
- STATUS-FINAL-v0.12.14.md
- RECOVERY.md

Arquivos históricos de acompanhamento de desenvolvimento, preservados para auditoria.

## Propósito

- **Referência Histórica**: Entender como o sistema foi documentado em versões anteriores
- **Auditoria**: Rastrear mudanças na documentação ao longo do tempo
- **Recuperação**: Acessar informações específicas de versões antigas se necessário
- **Contexto**: Compreender a evolução do projeto

## Como Usar

Para comparar documentação entre versões:
```bash
diff docs/README.md docs/archive/v0.12.9/README.md
```

## Futuras Versões

Quando o projeto avançar para novas versões principais, novas pastas serão criadas:
- `v0.14.0/` (futuro)
- `v0.15.0/` (futuro)
- etc.

---

**Última atualização:** 2 de janeiro de 2026

**Reorganização da documentação (Passo 6):**
- Arquivada pasta `redesign/` → `redesign-proposal/`
- Arquivados arquivos de status → `status-snapshots/`
- Resultado: 59 → 32 arquivos .md (-46%)

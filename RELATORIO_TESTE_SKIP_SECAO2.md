# Relatório Teste - Skip Seção 2 - BO Inteligente v0.13.2

**Data:** 03/01/2026 09:53
**Tempo:** 50.3s
**Erros:** 2

## Resultado

✅ TESTE SKIP SEÇÃO 2 - Apenas Seções 1 e 3

- Seção 1: 13 perguntas (incluindo follow-ups 1.5.1, 1.5.2) ✅
- Seção 2: PULADA (não havia veículo) ⃠
- Seção 3: 6 perguntas (3.2 a 3.6.1, skip 3.1 automática) ✅
- Textos do Groq validados (S1 e S3 apenas) ✅
- Tela final com 2 seções individuais validada ✅

## Log Completo

```
[   1.1s] ============================================================
[   1.1s] TESTE SKIP SECAO 2 - Somente S1 e S3
[   1.1s] ============================================================
[   7.7s] 
### SECAO 1: Contexto da Ocorrencia
[   7.7s] 1.1: 19/12/2025, 14h30min, quinta-feira...
[   9.5s]   OK
[   9.5s] 1.2: Sargento João Silva, Cabo Pedro Almeida e Sol...
[  11.2s]   OK
[  11.2s] 1.3: Via 190, DDU, Patrulhamento preventivo, Manda...
[  12.9s]   OK
[  12.9s] 1.4: Ordem de serviço nº 145/2025 determinava patr...
[  14.7s]   OK
[  14.7s] 1.5: SIM...
[  16.2s]   OK (escolha)
[  16.2s] 1.5.1: Base Operacional do 16º BPM, localizada na Av...
[  17.9s]   OK
[  17.9s] 1.5.2: Não houve alterações durante o deslocamento...
[  19.6s]   OK
[  19.6s] 1.6: Rua das Acácias, altura do número 789, Bairro...
[  21.3s]   OK
[  21.3s] 1.7: Sim, local consta em 12 registros anteriores ...
[  23.1s]   OK
[  23.1s] 1.8: Área sob influência da facção Comando Vermelh...
[  24.8s]   OK
[  24.8s] 1.9: SIM...
[  26.3s]   OK (escolha)
[  26.3s] 1.9.1: Escola Estadual João XXIII...
[  28.0s]   OK
[  28.0s] 1.9.2: Aproximadamente 300 metros...
[  29.7s]   OK
[  29.7s] 
Aguardando texto S1 (60s)...
[  30.0s] TEXTO GERADO: 899 chars
[  30.0s]   (contém 'SEÇÃO 1' ou 'Contexto')
[  30.0s] ❌ S1: Texto renderizado DIFERENTE do armazenado
[  30.0s]   Renderizado (899 chars): [SEÇÃO 1: Contexto da Ocorrência]

Respostas coletadas:
• 1.1: 19/12/2025, 14h30min, quinta-feira
• ...
[  30.0s]   Armazenado (0 chars): ...
[  30.2s] 
### PULANDO SECAO 2 (Não havia veículo)...
[  30.2s] Botão 'Não havia veículo' encontrado
[  33.3s] Seção 2 pulada!
[  33.3s] 
### Iniciando SECAO 3...
[  35.4s] 
### SECAO 3: Campana (caminho feliz)
[  35.4s] 3.2: aproximadamente 30 minutos...
[  37.1s]   OK
[  37.1s] 3.3: de dentro da viatura, a 50 metros do local...
[  38.8s]   OK
[  38.8s] 3.4: Observamos movimentação constante de pessoas ...
[  40.5s]   OK
[  40.5s] 3.5: aproximadamente 5 pessoas...
[  42.2s]   OK
[  42.2s] 3.6: SIM...
[  43.7s]   OK (escolha)
[  43.7s] 3.6.1: Foram observadas 3 transações entre diferente...
[  45.4s]   OK
[  45.4s] 
Aguardando texto S3 (60s)...
[  46.8s] TEXTO GERADO: 1033 chars
[  46.8s] ❌ S3: Texto renderizado DIFERENTE do armazenado
[  46.8s]   Renderizado (1033 chars): Motivados pela observação de movimentação constante de pessoas entrando e saindo rapidamente de um i...
[  46.8s]   Armazenado (0 chars): ...
[  46.9s] 
### FINALIZANDO BO...
[  46.9s] Botao Finalizar BO encontrado
[  47.0s] Clicou em 'Finalizar BO', indo para tela final...
[  50.1s] Screenshot DEBUG-before-final.png capturado
[  50.2s] Estado DOM: {'sectionContainer': 'EXISTS', 'finalScreen': 'EXISTS', 'boAppExists': False, 'eventBusExists': True, 'eventsExists': True}
[  50.2s] Tela final carregada!
[  50.2s] 
### Validando estrutura da tela final...
[  50.2s] Encontradas 2 caixas de seção
[  50.2s] ✅ 2 caixas de seção encontradas (S1 e S3)
[  50.2s] Encontrados 2 botões 'Copiar Seção X'
[  50.2s] ✅ 2 botões de copiar seção encontrados
[  50.2s] ✅ Botão 'Copiar BO Completo' encontrado
[  50.2s] ✅ Botão 'Iniciar Novo BO' encontrado
[  50.2s] ✅ Seção 1: tem conteúdo (937 chars)
[  50.2s] ✅ Seção 2: tem conteúdo (1071 chars)
[  50.3s] 
============================================================
[  50.3s] *** TESTE CONCLUIDO COM SUCESSO! ***
[  50.3s] ============================================================
[  50.3s] Tempo total: 50.3s
[  50.3s] Erros: 2
```

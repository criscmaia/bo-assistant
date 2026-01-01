/**
 * BO Inteligente - Configuração das Seções
 *
 * Este arquivo define todas as seções e perguntas do BO de Tráfico de Drogas.
 * Usado pelos componentes do frontend para renderizar o fluxo de perguntas.
 *
 * Estrutura:
 * - id: Identificador único da seção (1-8)
 * - name: Nome da seção
 * - emoji: Emoji para exibição na barra de progresso
 * - skippable: Se a seção pode ser pulada
 * - skipCondition: Pergunta que determina se deve pular (opcional)
 * - questions: Array de perguntas da seção
 *
 * Tipos de input:
 * - text: Campo de texto livre
 * - single_choice: Seleção única (botões)
 * - multiple_choice: Seleção múltipla (checkboxes)
 */

// Versionamento do esquema de seções
const SECTIONS_VERSION = '1.0';
const SECTIONS_SCHEMA = {
    version: SECTIONS_VERSION,
    lastUpdated: '2025-12-31',
    totalSections: 8,
    totalQuestions: 53,
    description: 'Schema inicial - BO Tráfico de Drogas v1.0'
};

const SECTIONS_DATA = [
  // ========================================
  // SEÇÃO 1: CONTEXTO DA OCORRÊNCIA
  // ========================================
  {
    id: 1,
    name: "Contexto da Ocorrência",
    emoji: "🚔",
    skippable: false,
    questions: [
      {
        id: "1.1",
        text: "Dia, data e hora do acionamento.",
        hint: "Ex: 22/03/2025, às 19h03",
        inputType: "text",
        validation: {
          required: true,
          minLength: 10,
          pattern: "datetime"
        }
      },
      {
        id: "1.2",
        text: "Composição da guarnição e prefixo da viatura.",
        hint: "Ex: Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
        inputType: "text",
        validation: {
          required: true,
          minLength: 15,
          requiredKeywords: ["prefixo", "viatura"],
          errorMessage: "Informe graduação + nome completo de TODOS os policiais + prefixo/viatura. Ex: 'Sgt João Silva e Cb Pedro Santos, prefixo 1234'"
        }
      },
      {
        id: "1.3",
        text: "Natureza do empenho.",
        hint: "Ex: Tráfico de drogas, Flagrante de tráfico",
        inputType: "text",
        validation: {
          required: true,
          minLength: 10
        }
      },
      {
        id: "1.4",
        text: "O que constava na ordem de serviço, informações do COPOM, DDU.",
        hint: "Descreva o que foi informado no acionamento",
        inputType: "text",
        validation: {
          required: true,
          minLength: 20
        }
      },
      {
        id: "1.5",
        text: "Local exato da ocorrência (logradouro, número, bairro).",
        hint: "Ex: Rua das Acácias, nº 123, bairro Centro",
        inputType: "text",
        validation: {
          required: true,
          minLength: 20,
          requiredKeywords: ["rua", "numero", "bairro"],
          errorMessage: "Informe endereço completo com logradouro (rua/avenida), número e bairro. Ex: 'Rua das Flores, nº 123, Bairro Centro'"
        }
      },
      {
        id: "1.6",
        text: "O local é ponto de tráfico? Quais evidências anteriores? Há facção?",
        hint: "Se não houver histórico, escreva 'NÃO'",
        inputType: "text",
        validation: {
          required: true,
          minLength: 3
        }
      },
      {
        id: "1.7",
        text: "O local fica próximo a escola, hospital, ou transporte público?",
        hint: "Relevante para o Art. 40 da Lei de Drogas",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "1.7.1",
            text: "Qual estabelecimento e a que distância aproximada?",
            hint: "Ex: Escola Municipal João XXIII, a aproximadamente 50 metros",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      }
    ]
  },

  // ========================================
  // SEÇÃO 2: ABORDAGEM A VEÍCULO
  // ========================================
  {
    id: 2,
    name: "Abordagem a Veículo",
    emoji: "🚗",
    skippable: true,
    skipQuestion: {
      id: "2.0",
      text: "Havia veículo envolvido na ocorrência?",
      hint: "Se não havia veículo, esta seção será pulada",
      inputType: "single_choice",
      options: [
        { value: "sim", label: "SIM" },
        { value: "nao", label: "NÃO", skipsSection: true }
      ]
    },
    questions: [
      {
        id: "2.1",
        text: "Qual o tipo, marca, modelo e cor do veículo?",
        hint: "Ex: Motocicleta Honda CG 160, cor vermelha",
        inputType: "text",
        validation: {
          required: true,
          minLength: 10
        }
      },
      {
        id: "2.2",
        text: "Qual a placa do veículo?",
        hint: "Ex: ABC-1234 ou ABC1D23",
        inputType: "text",
        validation: {
          required: true,
          minLength: 7
        }
      },
      {
        id: "2.3",
        text: "Qual o número do Renavam?",
        hint: "Se não souber, escreva 'NÃO INFORMADO'",
        inputType: "text",
        validation: {
          required: true,
          minLength: 3
        }
      },
      {
        id: "2.4",
        text: "Qual o número do Chassi?",
        hint: "Se não souber, escreva 'NÃO INFORMADO'",
        inputType: "text",
        validation: {
          required: true,
          minLength: 3
        }
      },
      {
        id: "2.5",
        text: "O condutor apresentou CNH?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "2.5.1",
            text: "Qual o número da CNH e categoria?",
            hint: "Ex: CNH 12345678900, categoria AB",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      },
      {
        id: "2.6",
        text: "O veículo tinha irregularidades?",
        hint: "Documentação vencida, adulterações, etc.",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "2.6.1",
            text: "Quais irregularidades foram constatadas?",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      },
      {
        id: "2.7",
        text: "Onde as drogas foram encontradas no veículo?",
        hint: "Ex: sob o banco do motorista, no porta-malas, no console",
        inputType: "text",
        validation: {
          required: true,
          minLength: 10
        }
      }
    ]
  },

  // ========================================
  // SEÇÃO 3: CAMPANA
  // ========================================
  {
    id: 3,
    name: "Campana",
    emoji: "👁️",
    skippable: true,
    skipQuestion: {
      id: "3.0",
      text: "Houve campana/observação prévia antes da abordagem?",
      hint: "Monitoramento do local antes de agir",
      inputType: "single_choice",
      options: [
        { value: "sim", label: "SIM" },
        { value: "nao", label: "NÃO", skipsSection: true }
      ]
    },
    questions: [
      {
        id: "3.1",
        text: "Quanto tempo durou a campana?",
        hint: "Ex: aproximadamente 30 minutos",
        inputType: "text",
        validation: {
          required: true,
          minLength: 5
        }
      },
      {
        id: "3.2",
        text: "De onde a guarnição observava?",
        hint: "Ex: de dentro da viatura, a 50 metros do local",
        inputType: "text",
        validation: {
          required: true,
          minLength: 10
        }
      },
      {
        id: "3.3",
        text: "O que foi observado durante a campana?",
        hint: "Descreva movimentações, pessoas, transações suspeitas",
        inputType: "text",
        validation: {
          required: true,
          minLength: 30
        }
      },
      {
        id: "3.4",
        text: "Quantas pessoas foram vistas no local?",
        inputType: "text",
        validation: {
          required: true,
          minLength: 1
        }
      },
      {
        id: "3.5",
        text: "Foram observadas transações de compra e venda?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "3.5.1",
            text: "Descreva as transações observadas.",
            hint: "Quantas, entre quem, como ocorreram",
            inputType: "text",
            validation: {
              required: true,
              minLength: 20
            }
          }
        }
      }
    ]
  },

  // ========================================
  // SEÇÃO 4: ENTRADA EM DOMICÍLIO
  // ========================================
  {
    id: 4,
    name: "Entrada em Domicílio",
    emoji: "🏠",
    skippable: true,
    skipQuestion: {
      id: "4.0",
      text: "Houve entrada em domicílio?",
      inputType: "single_choice",
      options: [
        { value: "sim", label: "SIM" },
        { value: "nao", label: "NÃO", skipsSection: true }
      ]
    },
    questions: [
      {
        id: "4.1",
        text: "Qual foi a justificativa para a entrada?",
        inputType: "single_choice",
        options: [
          { value: "flagrante", label: "Flagrante delito" },
          { value: "consentimento", label: "Consentimento do morador" },
          { value: "mandado", label: "Mandado judicial" },
          { value: "perseguicao", label: "Perseguição" }
        ]
      },
      {
        id: "4.2",
        text: "Quem autorizou a entrada? (nome completo)",
        hint: "Se flagrante/perseguição, escreva 'N/A'",
        inputType: "text",
        validation: {
          required: true,
          minLength: 3
        }
      },
      {
        id: "4.3",
        text: "Qual a relação dessa pessoa com o imóvel?",
        hint: "Ex: proprietário, inquilino, morador",
        inputType: "text",
        validation: {
          required: true,
          minLength: 3
        }
      },
      {
        id: "4.4",
        text: "O consentimento foi dado de forma livre e voluntária?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "na", label: "N/A (flagrante/mandado)" }
        ]
      },
      {
        id: "4.5",
        text: "Descreva o interior do imóvel e onde as drogas foram encontradas.",
        hint: "Cômodo, móvel, local específico",
        inputType: "text",
        validation: {
          required: true,
          minLength: 20
        }
      }
    ]
  },

  // ========================================
  // SEÇÃO 5: FUNDADA SUSPEITA
  // ========================================
  {
    id: 5,
    name: "Fundada Suspeita",
    emoji: "🔍",
    skippable: false,
    questions: [
      {
        id: "5.1",
        text: "O que motivou a abordagem?",
        hint: "Descreva os elementos concretos que geraram a suspeita",
        inputType: "multiple_choice",
        options: [
          { value: "denuncia", label: "Denúncia anônima" },
          { value: "campana", label: "Observação durante campana" },
          { value: "atitude", label: "Atitude do suspeito" },
          { value: "local", label: "Local conhecido de tráfico" },
          { value: "fuga", label: "Tentativa de fuga" },
          { value: "outro", label: "Outro motivo" }
        ],
        validation: {
          minSelections: 1
        }
      },
      {
        id: "5.2",
        text: "Descreva detalhadamente os elementos que fundamentaram a suspeita.",
        hint: "Seja específico: comportamento, gestos, local, contexto",
        inputType: "text",
        validation: {
          required: true,
          minLength: 50
        }
      },
      {
        id: "5.3",
        text: "Como foi realizada a busca pessoal?",
        hint: "Quem revistou quem, como, onde",
        inputType: "text",
        validation: {
          required: true,
          minLength: 30
        }
      },
      {
        id: "5.4",
        text: "Os suspeitos foram algemados?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "5.4.1",
            text: "Qual a justificativa para o uso de algemas?",
            hint: "Resistência, perigo de fuga, etc.",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      }
    ]
  },

  // ========================================
  // SEÇÃO 6: REAÇÃO E USO DA FORÇA
  // ========================================
  {
    id: 6,
    name: "Reação e Uso da Força",
    emoji: "💪",
    skippable: true,
    skipQuestion: {
      id: "6.0",
      text: "Houve reação ou resistência dos suspeitos?",
      inputType: "single_choice",
      options: [
        { value: "sim", label: "SIM" },
        { value: "nao", label: "NÃO", skipsSection: true }
      ]
    },
    questions: [
      {
        id: "6.1",
        text: "Qual foi o tipo de reação?",
        inputType: "multiple_choice",
        options: [
          { value: "verbal", label: "Resistência verbal" },
          { value: "passiva", label: "Resistência passiva" },
          { value: "ativa", label: "Resistência ativa" },
          { value: "fuga", label: "Tentativa de fuga" },
          { value: "agressao", label: "Agressão física" },
          { value: "arma", label: "Uso de arma" }
        ],
        validation: {
          minSelections: 1
        }
      },
      {
        id: "6.2",
        text: "Descreva detalhadamente a reação.",
        hint: "O que o suspeito fez, disse, como reagiu",
        inputType: "text",
        validation: {
          required: true,
          minLength: 30
        }
      },
      {
        id: "6.3",
        text: "Qual foi a resposta da guarnição?",
        inputType: "multiple_choice",
        options: [
          { value: "verbal", label: "Comando verbal" },
          { value: "contencao", label: "Técnica de contenção" },
          { value: "algemas", label: "Uso de algemas" },
          { value: "forca", label: "Uso moderado de força" },
          { value: "arma", label: "Uso de arma" }
        ],
        validation: {
          minSelections: 1
        }
      },
      {
        id: "6.4",
        text: "Alguém ficou ferido?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "6.4.1",
            text: "Quem ficou ferido e quais foram as lesões?",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      },
      {
        id: "6.5",
        text: "Foi necessário atendimento médico?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "6.5.1",
            text: "Onde foi realizado o atendimento?",
            hint: "Nome do hospital/UPA",
            inputType: "text",
            validation: {
              required: true,
              minLength: 5
            }
          }
        }
      }
    ]
  },

  // ========================================
  // SEÇÃO 7: APREENSÕES
  // ========================================
  {
    id: 7,
    name: "Apreensões",
    emoji: "📦",
    skippable: false,
    questions: [
      {
        id: "7.1",
        text: "Quais tipos de drogas foram apreendidas?",
        inputType: "multiple_choice",
        options: [
          { value: "maconha", label: "Maconha" },
          { value: "cocaina", label: "Cocaína" },
          { value: "crack", label: "Crack" },
          { value: "lanca", label: "Lança-perfume" },
          { value: "ecstasy", label: "Ecstasy" },
          { value: "lsd", label: "LSD" },
          { value: "outra", label: "Outra substância" }
        ],
        validation: {
          minSelections: 1
        }
      },
      {
        id: "7.2",
        text: "Descreva a quantidade e forma de acondicionamento de cada droga.",
        hint: "Ex: 50 buchas de maconha, 30 pinos de cocaína, 20 pedras de crack",
        inputType: "text",
        validation: {
          required: true,
          minLength: 20
        }
      },
      {
        id: "7.3",
        text: "Onde exatamente as drogas foram encontradas?",
        hint: "Com quem, em que local, em qual recipiente",
        inputType: "text",
        validation: {
          required: true,
          minLength: 20
        }
      },
      {
        id: "7.4",
        text: "Foi apreendido dinheiro?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "7.4.1",
            text: "Qual o valor e em que notas/moedas?",
            hint: "Ex: R$ 350,00 em notas de R$ 10 e R$ 20",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      },
      {
        id: "7.5",
        text: "Foram apreendidos outros objetos?",
        hint: "Balança, celulares, armas, cadernos de anotação, etc.",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "7.5.1",
            text: "Descreva os objetos apreendidos.",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      },
      {
        id: "7.6",
        text: "Os materiais foram fotografados?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ]
      }
    ]
  },

  // ========================================
  // SEÇÃO 8: CONDUÇÃO
  // ========================================
  {
    id: 8,
    name: "Condução e Providências",
    emoji: "⛓️",
    skippable: false,
    questions: [
      {
        id: "8.1",
        text: "Quantos conduzidos no total?",
        inputType: "text",
        validation: {
          required: true,
          minLength: 1
        }
      },
      {
        id: "8.2",
        text: "Informe os dados de cada conduzido.",
        hint: "Nome completo, CPF, data de nascimento, filiação",
        inputType: "text",
        validation: {
          required: true,
          minLength: 30
        }
      },
      {
        id: "8.3",
        text: "Os conduzidos foram informados de seus direitos constitucionais?",
        hint: "Direito ao silêncio, à assistência de advogado e familiar",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ]
      },
      {
        id: "8.4",
        text: "Algum conduzido é menor de idade?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "8.4.1",
            text: "Quais procedimentos específicos foram adotados para o menor?",
            hint: "Apreensão em flagrante, comunicação ao Conselho Tutelar, etc.",
            inputType: "text",
            validation: {
              required: true,
              minLength: 20
            }
          }
        }
      },
      {
        id: "8.5",
        text: "Para qual unidade policial os conduzidos foram levados?",
        hint: "Ex: Delegacia de Plantão Centro, DPPC",
        inputType: "text",
        validation: {
          required: true,
          minLength: 5
        }
      },
      {
        id: "8.6",
        text: "Qual delegado recebeu a ocorrência?",
        hint: "Nome e matrícula, se disponível",
        inputType: "text",
        validation: {
          required: true,
          minLength: 5
        }
      },
      {
        id: "8.7",
        text: "Os conduzidos possuíam antecedentes criminais?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" },
          { value: "naoverificado", label: "NÃO VERIFICADO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "8.7.1",
            text: "Quais antecedentes foram identificados?",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      },
      {
        id: "8.8",
        text: "Algum conduzido pertence a organização criminosa conhecida?",
        inputType: "single_choice",
        options: [
          { value: "sim", label: "SIM" },
          { value: "nao", label: "NÃO" },
          { value: "naoverificado", label: "NÃO VERIFICADO" }
        ],
        followUp: {
          condition: "sim",
          question: {
            id: "8.8.1",
            text: "Qual organização e qual a função do conduzido?",
            inputType: "text",
            validation: {
              required: true,
              minLength: 10
            }
          }
        }
      }
    ]
  }
];

// Exportar para uso global (Vanilla JS)
window.SECTIONS_DATA = SECTIONS_DATA;

// Função auxiliar para contar total de perguntas
function countTotalQuestions() {
  let total = 0;
  SECTIONS_DATA.forEach(section => {
    if (section.skipQuestion) total++;
    section.questions.forEach(q => {
      total++;
      if (q.followUp) total++;
    });
  });
  return total;
}

// Função auxiliar para obter seção por ID
function getSectionById(sectionId) {
  return SECTIONS_DATA.find(s => s.id === sectionId);
}

// Função auxiliar para obter pergunta por ID
function getQuestionById(questionId) {
  for (const section of SECTIONS_DATA) {
    if (section.skipQuestion && section.skipQuestion.id === questionId) {
      return section.skipQuestion;
    }
    for (const question of section.questions) {
      if (question.id === questionId) return question;
      if (question.followUp && question.followUp.question.id === questionId) {
        return question.followUp.question;
      }
    }
  }
  return null;
}

// Exportar funções auxiliares
window.countTotalQuestions = countTotalQuestions;
window.getSectionById = getSectionById;
window.getQuestionById = getQuestionById;

console.log(`[sections.js] Carregado: ${SECTIONS_DATA.length} seções, ~${countTotalQuestions()} perguntas`);

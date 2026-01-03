/**
 * SectionContainer - Gerencia uma seção do BO
 * Inclui chat, input, texto gerado e transição
 * BO Inteligente v0.13.2
 *
 * NOTA v0.13.2: Estado agora é delegado para StateManager (Single Source of Truth).
 * Getters/setters para state, messages, answers, generatedText, skipReason delegam
 * para StateManager, eliminando duplicação de estado que causava bugs de regressão.
 *
 * Variáveis locais mantidas apenas para controle de UI:
 * - currentQuestionIndex (qual pergunta mostrar)
 * - isReadOnly (se está em modo leitura)
 * - followUpQueue (perguntas follow-up pendentes)
 */

class SectionContainer {
    /**
     * Componente que gerencia uma seção do BO
     * Inclui chat, input, texto gerado e transição
     */
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);

        // Referência ao StateManager (v0.13.1+)
        this.stateManager = typeof StateManager !== 'undefined' ? StateManager.getInstance() : null;

        // Dados da seção atual
        this.sectionData = options.sectionData || null;
        this.sectionId = options.sectionId || 1;

        // Estado UI local (NÃO duplicar estado do StateManager)
        // v0.13.2+: state, messages, answers, generatedText, skipReason são delegados ao StateManager
        this.currentQuestionIndex = 0; // Controle de UI - qual pergunta mostrar
        this.isReadOnly = false;
        this.followUpQueue = []; // Fila de perguntas follow-up (1.5.1, 1.5.2, etc)

        // Callbacks (DEPRECATED - usar EventBus)
        this.onAnswer = options.onAnswer || ((questionId, answer) => {});
        this.onComplete = options.onComplete || ((sectionId, answers) => {});
        this.onSkip = options.onSkip || ((sectionId) => {});
        this.onNavigateNext = options.onNavigateNext || ((nextSectionId) => {});
        this.onNavigateBack = options.onNavigateBack || (() => {});
        // v0.13.2 (Opção B): Callback para gerar texto via endpoint separado
        this.onGenerateText = options.onGenerateText || (async (sectionId) => null);

        // EventBus para comunicação desacoplada (v0.13.1+)
        this.eventBus = typeof window !== 'undefined' && window.eventBus ? window.eventBus : null;

        // =============================================================================
        // GETTERS - Delegam para StateManager (v0.13.2+ - Single Source of Truth)
        // =============================================================================

        // Helper para salvar resposta individual (porque getter retorna cópia)
        this._saveAnswer = (questionId, answer) => {
            if (this.stateManager) {
                this.stateManager.saveAnswer(this.sectionId, questionId, answer);
            }
        };

        Object.defineProperties(this, {
            'state': {
                get: () => this.stateManager?.getSectionStatus(this.sectionId) || 'pending',
                set: (value) => {
                    // Setter para compatibilidade - atualiza StateManager
                    if (value === 'completed') {
                        this.stateManager?.markSectionCompleted(this.sectionId);
                    } else if (value === 'skipped') {
                        this.stateManager?.markSectionSkipped(this.sectionId, this.skipReason);
                    } else if (this.stateManager) {
                        // Para pending/in_progress, setar diretamente
                        const section = this.stateManager._state.sections[this.sectionId];
                        if (section) section.status = value;
                    }
                }
            },
            'messages': {
                get: () => this.stateManager?.getSectionState(this.sectionId)?.messages || [],
                set: (value) => {
                    // Setter para compatibilidade - sincroniza com StateManager
                    if (this.stateManager && this.stateManager._state.sections[this.sectionId]) {
                        this.stateManager._state.sections[this.sectionId].messages = value;
                    }
                }
            },
            'answers': {
                get: () => this.stateManager?.getAnswers(this.sectionId) || {},
                set: (value) => {
                    // Setter para compatibilidade - sincroniza com StateManager
                    if (this.stateManager && this.stateManager._state.sections[this.sectionId]) {
                        this.stateManager._state.sections[this.sectionId].answers = { ...value };
                    }
                }
            },
            'generatedText': {
                get: () => {
                    const text = this.stateManager?.getGeneratedText(this.sectionId) || null;
                    console.log('[SectionContainer] getter generatedText - sectionId:', this.sectionId, 'text:', text ? text.substring(0, 50) + '...' : 'NULL');
                    return text;
                },
                set: (value) => {
                    console.log('[SectionContainer] setter generatedText - sectionId:', this.sectionId, 'value:', value ? value.substring(0, 50) + '...' : 'NULL');
                    this.stateManager?.setGeneratedText(this.sectionId, value);
                }
            },
            'skipReason': {
                get: () => this.stateManager?.getSectionState(this.sectionId)?.skipReason || null,
                set: (value) => {
                    if (this.stateManager && this.stateManager._state.sections[this.sectionId]) {
                        this.stateManager._state.sections[this.sectionId].skipReason = value;
                    }
                }
            }
        });

        // Elementos internos
        this.chatEl = null;
        this.inputEl = null;
        this.inputFieldEl = null;
        this.generatedEl = null;
        this.transitionEl = null;

        // Dispose Pattern - Rastreamento de listeners para cleanup (v0.13.1+)
        this._eventListeners = [];
        this._eventBusUnsubscribers = [];
    }

    /**
     * Carrega dados de uma seção
     *
     * options:
     *   - preAnswerSkipQuestion: Se fornecido, auto-responde o skipQuestion com este valor
     *     sem mostrar no chat (útil quando o usuário veio de um botão de transição tipo "Sim, havia veículo")
     */
    loadSection(sectionData, options = {}) {
        this.sectionData = sectionData;
        this.sectionId = sectionData.id;

        // v0.13.2+: Atualizar StateManager (Single Source of Truth)
        // Os getters/setters delegam automaticamente para StateManager
        if (options.state) {
            this.state = options.state; // Usa o setter que atualiza StateManager
        }
        if (options.messages && options.messages.length > 0) {
            this.messages = options.messages; // Usa o setter que atualiza StateManager
        }
        if (options.answers && Object.keys(options.answers).length > 0) {
            this.answers = options.answers; // Usa o setter que atualiza StateManager
        }
        if (options.generatedText) {
            this.generatedText = options.generatedText; // Usa o setter que atualiza StateManager
        }
        if (options.skipReason) {
            this.skipReason = options.skipReason; // Usa o setter que atualiza StateManager
        }

        // Controles de UI local
        this.currentQuestionIndex = options.currentQuestionIndex || 0;
        this.isReadOnly = options.isReadOnly || false;

        this.render();

        // Se não for read-only e estado é in_progress, garantir que mostra próxima pergunta
        if (!this.isReadOnly && this.state === 'in_progress') {
            if (this.messages.length === 0) {
                // Seção nova: mostrar primeira pergunta
                if (options.preAnswerSkipQuestion && this.sectionData.skipQuestion) {
                    const skipQ = this.sectionData.skipQuestion;

                    // Mostrar pergunta skipQuestion no chat
                    this._showQuestion(skipQ);

                    // Verificar se a resposta causa skip da seção
                    const answerLower = options.preAnswerSkipQuestion.toLowerCase();
                    const selectedOption = skipQ.options?.find(opt =>
                        opt.value.toLowerCase() === answerLower ||
                        opt.label.toLowerCase() === answerLower
                    );
                    const willSkipSection = selectedOption?.skipsSection === true;

                    // Auto-responder após delay
                    // CORREÇÃO v0.13.2: Não chamar _saveAnswer aqui, pois _onAnswer agora salva após validação
                    setTimeout(() => {
                        this._addUserMessage(options.preAnswerSkipQuestion);

                        // Se vai pular a seção, aguardar API e depois chamar _skipSection
                        if (willSkipSection) {
                            this.onAnswer(skipQ.id, options.preAnswerSkipQuestion).then((result) => {
                                // Se validação falhou, não pular (cenário raro para skip questions)
                                if (result?.validationError) {
                                    console.warn('[SectionContainer] Validação falhou em skip question:', result.validationError);
                                    this._removeLastUserMessage();
                                    return;
                                }
                                // CORREÇÃO: Usar skipReason retornado pela API
                                const skipReason = result?.skipReason || null;
                                setTimeout(() => {
                                    this._skipSection(skipReason);
                                }, 300);
                            }).catch((error) => {
                                console.error('Erro ao processar skip question:', error);
                            });
                        } else {
                            // Resposta normal, apenas enviar para API
                            this.onAnswer(skipQ.id, options.preAnswerSkipQuestion).then((result) => {
                                // Se validação falhou, não avançar
                                if (result?.validationError) {
                                    console.warn('[SectionContainer] Validação falhou:', result.validationError);
                                    this._removeLastUserMessage();
                                    return;
                                }
                                // Avançar para próxima pergunta
                                this.currentQuestionIndex = 1;
                                setTimeout(() => {
                                    this._showCurrentQuestion();
                                }, 500);
                            });
                        }
                    }, 300);
                } else {
                    this._showCurrentQuestion();
                }
            } else {
                // Restaurando rascunho ou voltando para seção em andamento
                this._restoreFollowUpState();

                // Obter próxima pergunta
                const nextQuestion = this._getCurrentQuestionForInput();
                if (nextQuestion) {
                    console.log('[SectionContainer] Renderizando input para pergunta:', nextQuestion.id, '- currentQuestionIndex:', this.currentQuestionIndex);

                    // Verificar se a pergunta já está no chat
                    const questionText = `${nextQuestion.id}) ${nextQuestion.text}`;
                    const questionAlreadyInChat = this.messages.some(msg =>
                        msg.type === 'bot' && msg.text === questionText
                    );

                    // Se não estiver no chat, adicionar
                    if (!questionAlreadyInChat) {
                        console.log('[SectionContainer] Pergunta não está no chat, adicionando:', nextQuestion.id);
                        this._addBotMessage(questionText, nextQuestion.hint);
                    }

                    // Renderizar input
                    this._renderInput(nextQuestion);
                } else {
                    console.log('[SectionContainer] Nenhuma pergunta pendente - seção completa');
                }
            }
        }
    }

    /**
     * Restaura estado de follow-ups ao carregar um rascunho
     * Se a pergunta atual já foi respondida e tem follow-ups pendentes, reconstrói a fila
     */
    _restoreFollowUpState() {
        if (!this.sectionData) return;

        const questions = this.sectionData.questions;

        // Calcular índice real da pergunta atual
        const realIndex = this.sectionData.skipQuestion ? this.currentQuestionIndex - 1 : this.currentQuestionIndex;

        if (realIndex < 0 || realIndex >= questions.length) return;

        const currentQuestion = questions[realIndex];

        // Verificar se esta pergunta já foi respondida
        const savedAnswer = this.answers[currentQuestion.id];
        if (!savedAnswer) return;

        // Verificar se tem follow-ups
        if (!currentQuestion.followUp || !currentQuestion.followUp.condition) return;

        // Verificar se a condição foi atendida
        const conditionMet = savedAnswer.toLowerCase().includes(currentQuestion.followUp.condition.toLowerCase());
        if (!conditionMet) return;

        // Verificar quais follow-ups ainda não foram respondidas
        if (currentQuestion.followUp.questions && currentQuestion.followUp.questions.length > 0) {
            const pendingFollowUps = currentQuestion.followUp.questions.filter(
                followUpQ => !this.answers[followUpQ.id]
            );

            if (pendingFollowUps.length > 0) {
                // Reconstruir fila com follow-ups pendentes
                this.followUpQueue = [...pendingFollowUps];
                console.log('[SectionContainer] Follow-up queue restaurada:', this.followUpQueue.map(q => q.id));
            }
        }
    }

    /**
     * Renderiza o container completo
     */
    render() {
        if (!this.container || !this.sectionData) return;

        const section = this.sectionData;

        // Adicionar data-section-id e data-state para estilização contextual
        this.container.setAttribute('data-section-id', section.id);
        this.container.setAttribute('data-state', this.state);

        // Determinar se o chat accordion deve estar aberto no início
        // Fica aberto se a seção está em progresso e há mensagens
        const shouldChatBeExpanded = this.state === 'in_progress' && this.messages.length > 0;

        this.container.innerHTML = `
            <!-- Header da Seção -->
            <div class="section-header">
                <div class="section-header__title">
                    <span class="section-header__emoji">${section.emoji}</span>
                    <span>Seção ${section.id}: ${section.name}</span>
                </div>
                <span class="section-header__badge section-header__badge--${this.state}">
                    ${this._getStatusLabel()}
                </span>
            </div>

            <!-- Chat (Accordion) - Oculto se seção foi pulada -->
            ${this.state !== 'skipped' ? `
            <button class="section-chat-toggle ${shouldChatBeExpanded ? '' : 'section-chat-toggle--collapsed'}" id="section-chat-toggle">
                Histórico do Chat (${this.messages.length} mensagens)
            </button>
            <div class="section-chat ${shouldChatBeExpanded ? 'section-chat--expanded' : ''}" id="section-chat">
                ${this._renderMessages()}
            </div>
            ` : `
            <!-- Mensagem customizada para seção pulada -->
            <pre id="section-skip-message" class="section-skip-message whitespace-pre-wrap text-sm text-gray-800 mb-3 italic text-gray-500" style="font-size: 0.95rem;">${this.skipReason || 'Não se aplica (motivo não especificado)'}</pre>
            `}


            <!-- Área de Input Dinâmica -->
            ${!this.isReadOnly && this.state === 'in_progress' ? `
            <div id="section-input-area">
                <!-- Input será renderizado pelo _renderInput() -->
            </div>
            ` : ''}

            <!-- Texto Gerado (se completed) -->
            ${this.state === 'completed' && this.generatedText ? `
            <div class="section-generated" id="section-generated">
                <div class="section-generated__header">
                    <span class="section-generated__title">
                        📄 Texto Gerado - Seção ${section.id}
                    </span>
                    <button class="section-generated__copy" id="section-copy-btn">
                        📋 Copiar
                    </button>
                </div>
                <div class="section-generated__text">${this.generatedText}</div>
            </div>
            ` : ''}

            <!-- Transição para próxima seção (se completed/skipped e não for última) -->
            ${(this.state === 'completed' || this.state === 'skipped') && this.sectionId < 8 ? this._renderTransition() : ''}

            <!-- Aviso de modo leitura -->
            ${this.isReadOnly ? `
            <div class="section-readonly-notice">
                <span class="section-readonly-notice__text">
                    📖 Modo leitura - Esta seção já foi finalizada
                </span>
                <button class="section-readonly-notice__btn" id="section-back-btn">
                    ↩️ Voltar para seção atual
                </button>
            </div>
            ` : ''}
        `;

        // Guardar referências
        this.chatEl = this.container.querySelector('#section-chat');
        this.inputEl = this.container.querySelector('#section-input');
        this.inputFieldEl = this.container.querySelector('#section-input-field');
        this.generatedEl = this.container.querySelector('#section-generated');
        this.transitionEl = this.container.querySelector('.section-transition');

        // Bind eventos
        this._bindEvents();

        // Scroll para final do chat (se há mensagens)
        if (this.messages.length > 0) {
            this._scrollChatToBottom();
        }
    }

    /**
     * Retorna label do status
     */
    _getStatusLabel() {
        switch (this.state) {
            case 'in_progress': {
                const answeredCount = Object.keys(this.answers).length;
                const totalQuestions = window.calculateSectionTotal
                    ? window.calculateSectionTotal(this.sectionId, this.answers)
                    : this.sectionData.questions.length + (this.sectionData.skipQuestion ? 1 : 0);
                return `${answeredCount}/${totalQuestions} perguntas`;
            }
            case 'completed': return '✓ Completa';
            case 'skipped': return '⃠\u00A0\u00A0\u00A0Não se aplica';
            default: return 'Pendente';
        }
    }

    /**
     * Renderiza mensagens do chat
     */
    _renderMessages() {
        if (this.messages.length === 0) {
            // Se seção foi pulada, mostrar motivo em vez de "Carregando..."
            if (this.state === 'skipped') {
                const skipMessage = this.skipReason || 'Não se aplica';
                return `<div class="section-skipped-message"><span>⃠</span> ${skipMessage}</div>`;
            }
            return '<div class="section-loading"><span class="section-loading__spinner"></span> Carregando...</div>';
        }

        return this.messages.map(msg => {
            if (msg.type === 'bot') {
                // Parse question ID from message text (e.g., "1.1) Question text" -> ID: "1.1", text: "Question text")
                const questionIdMatch = msg.text.match(/^([\d.]+)\)\s(.+)$/);
                let messageContent = msg.text;

                if (questionIdMatch) {
                    const questionId = questionIdMatch[1];
                    const questionText = questionIdMatch[2];
                    messageContent = `<span class="question-id">${questionId}</span> ${questionText}`;
                }

                return `
                    <div class="chat-message chat-message--bot">
                        <div class="chat-message__bubble chat-message__bubble--bot">
                            <div class="chat-message__text">${messageContent}</div>
                            ${msg.hint ? `<div class="chat-message__hint">${msg.hint}</div>` : ''}
                        </div>
                    </div>
                `;
            } else {
                return `
                    <div class="chat-message chat-message--user">
                        <div class="chat-message__bubble chat-message__bubble--user">
                            <div class="chat-message__text">${msg.text}</div>
                        </div>
                    </div>
                `;
            }
        }).join('');
    }

    /**
     * Renderiza área de transição
     */
    _renderTransition() {
        // Não mostrar botões de transição em modo read-only
        if (this.isReadOnly) return '';

        // Verificar se esta é a última seção ativa
        const maxSections = window.ACTIVE_SECTIONS_COUNT || 8;
        const isLastActiveSection = this.sectionId === maxSections;

        if (isLastActiveSection) {
            // Mostrar botão para finalizar o BO
            return `
                <div class="section-transition">
                    <div class="section-transition__preview">
                        <span class="section-transition__preview-emoji">✅</span>
                        <div class="section-transition__preview-info">
                            <div class="section-transition__preview-label">Próxima etapa</div>
                            <div class="section-transition__preview-name">Tela Final - Resumo do BO</div>
                        </div>
                    </div>
                    <div class="section-transition__buttons">
                        <button class="section-transition__btn section-transition__btn--start" id="section-finalize-bo">
                            ✅ Finalizar BO
                        </button>
                    </div>
                </div>
            `;
        }

        const nextSection = window.SECTIONS_DATA ? window.SECTIONS_DATA.find(s => s.id === this.sectionId + 1) : null;

        if (!nextSection) return '';

        const canSkip = nextSection.skippable !== false;

        // Textos específicos para cada seção (contexto-aware)
        const startTexts = {
            2: 'Sim, havia veículo',
            3: 'Sim, houve campana',
            4: 'Sim, houve entrada em domicílio',
            5: 'Sim, houve fundada suspeita',
            6: 'Sim, houve resistência',
            7: 'Sim, houve apreensão',
            8: 'Iniciar Seção 8 (FINAL)'
        };

        const skipTexts = {
            2: 'Não havia veículo',
            3: 'Não houve campana',
            4: 'Não houve entrada em domicílio',
            5: 'Não houve fundada suspeita',
            6: 'Não houve resistência',
            7: 'Não houve apreensão'
        };

        // Perguntas contextuais para cada transição
        const transitionQuestions = {
            2: 'Havia veículo envolvido na ocorrência?',
            3: 'Houve campana?',
            4: 'Houve entrada em domicílio?',
            5: 'Houve fundada suspeita?',
            6: 'Houve resistência?',
            7: 'Houve apreensão?',
            8: null
        };

        const nextSectionId = nextSection.id;
        const startButtonText = startTexts[nextSectionId] || `Iniciar Seção ${nextSectionId}`;
        const skipButtonText = skipTexts[nextSectionId] || 'Pular';

        // Icon para o botão de início
        const startButtonIcon = nextSectionId === 8 ? '▶️' : '✅';

        // Obter pergunta para esta transição
        const transitionQuestion = transitionQuestions[nextSectionId];

        return `
            <div class="section-transition">
                <div class="section-transition__preview">
                    <span class="section-transition__preview-emoji">${nextSection.emoji}</span>
                    <div class="section-transition__preview-info">
                        <div class="section-transition__preview-label">Próxima seção</div>
                        <div class="section-transition__preview-name">Seção ${nextSection.id}: ${nextSection.name}</div>
                    </div>
                </div>
                ${transitionQuestion ? `<div class="section-transition__question">${transitionQuestion}</div>` : ''}
                <div class="section-transition__buttons">
                    <button class="section-transition__btn section-transition__btn--start" id="section-start-next">
                        ${startButtonIcon} ${startButtonText}
                    </button>
                    ${canSkip ? `
                    <button class="section-transition__btn section-transition__btn--skip" id="section-skip-next">
                        <span style="display: inline-block; margin-right: 3px;">⃠</span>${skipButtonText}
                    </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Cria o componente de input correto baseado na pergunta
     */
    _createInputComponent(question) {
        const inputType = question.inputType || 'text';

        switch (inputType) {
            case 'single_choice':
                return new SingleChoice({
                    options: question.options || [
                        { value: 'sim', label: 'SIM' },
                        { value: 'nao', label: 'NÃO' }
                    ],
                    onSelect: (value, label, option) => {
                        this._handleInputSubmit(label, question, option);
                    }
                });

            case 'multiple_choice':
                return new MultipleChoice({
                    options: question.options || [],
                    minSelections: question.validation?.minSelections || 1,
                    maxSelections: question.validation?.maxSelections || null,
                    onConfirm: (values, labels) => {
                        this._handleInputSubmit(labels.join(', '), question);
                    }
                });

            case 'text':
            default:
                // Para pergunta 1.1, pré-preencher com data/hora atual
                let defaultValue = null;
                if (question.id === '1.1') {
                    defaultValue = this._generateCurrentDateTime();
                }

                return new TextInput({
                    placeholder: question.hint || 'Digite sua resposta...',
                    validation: question.validation || {},
                    defaultValue: defaultValue,
                    onSubmit: (value, onError) => {
                        this._handleInputSubmit(value, question, null, onError);
                    }
                });
        }
    }

    /**
     * Trata resposta do componente de input
     *
     * v0.13.2 (Opção B - 2 Requests): Fluxo simplificado backend-driven
     * 1. Envia resposta para /answer
     * 2. Se backend retorna willGenerateNow=true → mostra loading → chama /generate → completa
     * 3. Senão → continua com próxima pergunta
     */
    _handleInputSubmit(answer, question, option = null, onError = null) {
        // Verificar se deve pular seção (para skipQuestion)
        if (option?.skipsSection) {
            this._addUserMessage(answer);

            // Chamar onAnswer que vai enviar para API e retornar skip reason
            this.onAnswer(question.id, answer, { isSkipQuestion: true }).then((result) => {
                // Se validação falhou, não pular
                if (result?.validationError) {
                    this._removeLastUserMessage();
                    if (onError) onError(result.validationError);
                    return;
                }
                // CORREÇÃO: Usar skipReason retornado pela API
                const skipReason = result?.skipReason || null;
                setTimeout(() => {
                    this._skipSection(skipReason);
                }, 300);
            }).catch((error) => {
                console.error('Erro ao enviar skip question:', error);
                if (onError) onError('Erro ao processar resposta. Tente novamente.');
            });
            return;
        }

        // Adicionar mensagem do usuário (será removida se validação falhar)
        this._addUserMessage(answer);

        // Verificar se é uma pergunta follow-up (tem mais de um ponto no ID)
        const dotCount = (question.id.match(/\./g) || []).length;
        const isFollowUp = dotCount > 1;  // Ex: "1.5.1" tem 2 pontos, "1.5" tem 1 ponto

        // Verificar follow-up da pergunta atual (para processamento local após resposta)
        let hasFollowUp = false;
        if (question.followUp && question.followUp.condition) {
            const conditionMet = answer.toLowerCase().includes(question.followUp.condition.toLowerCase());
            hasFollowUp = conditionMet && (
                (question.followUp.questions && question.followUp.questions.length > 0) ||
                question.followUp.question
            );
        }

        // v0.13.2: Incrementar índice APÓS validação (não antes)
        const shouldIncrementIndex = (!isFollowUp || this.followUpQueue.length === 0) && !hasFollowUp;
        const previousIndex = this.currentQuestionIndex;

        // v0.13.2 (Opção B): Enviar resposta e aguardar decisão do backend
        this.onAnswer(question.id, answer).then(async (result) => {
            // Se validação falhou, reverter e mostrar erro
            if (result?.validationError) {
                console.log('[SectionContainer] Validação falhou');
                this._removeLastUserMessage();
                this._renderInput(question);
                if (this.currentInputComponent && typeof this.currentInputComponent.showError === 'function') {
                    this.currentInputComponent.showError(result.validationError);
                } else {
                    this._showError(result.validationError);
                }
                return;
            }

            // Se houve erro de API (rate limit, etc), mostrar no texto gerado
            if (result?.apiError) {
                console.log('[SectionContainer] Erro de API:', result.apiError);
                const errorText = `⚠️ Erro ao gerar texto:\n\n${result.apiError}\n\nAs respostas foram salvas. Tente novamente mais tarde.`;
                this.generatedText = errorText;
            }

            // Validação passou - incrementar índice se necessário
            if (shouldIncrementIndex) {
                this.currentQuestionIndex++;
                this._updateBadge();
            }

            // v0.13.2 (Opção B): Backend disse para gerar texto AGORA
            if (result?.willGenerateNow) {
                console.log('[SectionContainer] Backend sinalizou willGenerateNow - mostrando loading e chamando /generate');

                // Mostrar loading APENAS quando backend confirma que vai gerar
                this._showGeneratingTextOverlay();

                try {
                    // Chamar endpoint /generate via callback
                    await this.onGenerateText(this.sectionId);
                } catch (error) {
                    console.error('[SectionContainer] Erro ao gerar texto:', error);
                }

                // Esconder loading e completar seção
                this._hideGeneratingTextOverlay();
                this._completeSection();
                return;
            }

            // v0.13.2: Emitir evento ANSWER_SAVED
            if (this.eventBus && typeof Events !== 'undefined') {
                this.eventBus.emit(Events.ANSWER_SAVED, {
                    sectionId: this.sectionId,
                    questionId: question.id,
                    answer: answer
                });
            }

            // Ainda tem perguntas - continuar fluxo normal
            this._continueAfterAnswer(question, answer, isFollowUp, hasFollowUp);

        }).catch(error => {
            console.error('Erro ao salvar resposta:', error);
            this._removeLastUserMessage();
            this._renderInput(question);
            if (this.currentInputComponent && typeof this.currentInputComponent.showError === 'function') {
                this.currentInputComponent.showError('Erro ao processar resposta. Tente novamente.');
            } else {
                this._showError('Não foi possível salvar a resposta. Tente novamente.');
            }
        });
    }

    /**
     * Continua processamento após onAnswer (follow-ups ou próxima pergunta)
     */
    _continueAfterAnswer(question, answer, isFollowUp, hasFollowUp) {
        // Processar follow-ups
        if (isFollowUp && this.followUpQueue.length > 0) {
            // Ainda há follow-ups na fila
            setTimeout(() => {
                this._showNextFollowUp();
            }, 500);
            return;
        }

        if (question.followUp && question.followUp.condition) {
            const conditionMet = answer.toLowerCase().includes(question.followUp.condition.toLowerCase());

            if (conditionMet) {
                // Suportar múltiplas perguntas (questions array)
                if (question.followUp.questions && question.followUp.questions.length > 0) {
                    // Adicionar todas as perguntas follow-up à fila
                    this.followUpQueue = [...question.followUp.questions];
                    setTimeout(() => {
                        this._showNextFollowUp();
                    }, 500);
                    return;
                }
                // Suportar uma única pergunta (question singular) - backward compatibility
                else if (question.followUp.question) {
                    setTimeout(() => {
                        this._showQuestion(question.followUp.question);
                    }, 500);
                    return;
                }
            }
        }

        // Mostrar próxima pergunta
        setTimeout(() => {
            this._showCurrentQuestion();
        }, 500);
    }

    /**
     * Mostra próxima pergunta follow-up da fila
     */
    _showNextFollowUp() {
        if (this.followUpQueue.length > 0) {
            const nextQuestion = this.followUpQueue.shift();
            this._showQuestion(nextQuestion);
        } else {
            // Todas as follow-ups respondidas, avançar para próxima pergunta principal
            // Incrementar currentQuestionIndex (já que não foi incrementado antes)
            this.currentQuestionIndex++;
            this._updateBadge();
            setTimeout(() => {
                this._showCurrentQuestion();
            }, 500);
        }
    }

    /**
     * Mostra uma pergunta específica com o input correto
     */
    _showQuestion(question) {
        // Adicionar mensagem do bot com o número da pergunta
        const questionWithNumber = `${question.id}) ${question.text}`;
        this._addBotMessage(questionWithNumber, question.hint);

        // Renderizar input correto
        this._renderInput(question);
    }

    /**
     * Renderiza o input na área de input
     */
    _renderInput(question) {
        // Remover input anterior
        const inputArea = this.container.querySelector('#section-input-area');
        if (inputArea) {
            inputArea.innerHTML = '';

            // Criar novo componente
            this.currentInputComponent = this._createInputComponent(question);
            const inputEl = this.currentInputComponent.render();
            inputArea.appendChild(inputEl);

            // Focar se for TextInput
            if (this.currentInputComponent instanceof TextInput) {
                this.currentInputComponent.focus();
            }
        }
    }

    /**
     * Bind de eventos com Dispose Pattern
     * Rastreia todos os listeners para cleanup posteriormente
     */
    _bindEvents() {
        // Limpar listeners anteriores antes de adicionar novos
        this.dispose();

        // Helper para rastrear listeners
        const addListener = (element, event, handler) => {
            if (!element) return;
            element.addEventListener(event, handler);
            this._eventListeners.push({ element, event, handler });
        };

        // Toggle do chat (accordion)
        const chatToggle = this.container.querySelector('#section-chat-toggle');
        const chatToggleHandler = () => {
            this.chatEl.classList.toggle('section-chat--expanded');
            chatToggle.classList.toggle('section-chat-toggle--collapsed');
        };
        addListener(chatToggle, 'click', chatToggleHandler);

        // Copiar texto gerado
        const copyBtn = this.container.querySelector('#section-copy-btn');
        addListener(copyBtn, 'click', () => this._copyGeneratedText());

        // Iniciar próxima seção
        const startNextBtn = this.container.querySelector('#section-start-next');
        addListener(startNextBtn, 'click', () => {
            // v0.13.1+: Emitir evento via EventBus para navegação
            if (this.eventBus && typeof Events !== 'undefined') {
                this.eventBus.emit(Events.SECTION_CHANGE_REQUESTED, {
                    sectionId: this.sectionId + 1,
                    context: { preAnswerSkipQuestion: 'sim' }
                });
            }
            // Fallback: Manter callback para compatibilidade (DEPRECATED)
            this.onNavigateNext(this.sectionId + 1, { preAnswerSkipQuestion: 'sim' });
        });

        // Pular próxima seção
        const skipNextBtn = this.container.querySelector('#section-skip-next');
        addListener(skipNextBtn, 'click', () => {
            // v0.13.1+: Emitir evento via EventBus para navegação
            if (this.eventBus && typeof Events !== 'undefined') {
                this.eventBus.emit(Events.SECTION_CHANGE_REQUESTED, {
                    sectionId: this.sectionId + 1,
                    context: { preAnswerSkipQuestion: 'não' }
                });
            }
            // Fallback: Manter callback para compatibilidade (DEPRECATED)
            this.onNavigateNext(this.sectionId + 1, { preAnswerSkipQuestion: 'não' });
        });

        // Finalizar BO (v0.13.2+: quando há limite de seções ativas)
        const finalizeBOBtn = this.container.querySelector('#section-finalize-bo');
        addListener(finalizeBOBtn, 'click', () => {
            // Emitir evento para mostrar tela final via EventBus
            if (this.eventBus && typeof Events !== 'undefined') {
                this.eventBus.emit(Events.FINAL_SCREEN_REQUESTED, {
                    context: 'completed_all_active_sections'
                });
            } else {
                console.error('[SectionContainer] EventBus ou Events não disponível para emitir FINAL_SCREEN_REQUESTED');
            }
        });

        // Voltar para seção atual
        const backBtn = this.container.querySelector('#section-back-btn');
        addListener(backBtn, 'click', () => {
            // v0.13.1+: Emitir evento via EventBus para navegação
            if (this.eventBus && typeof Events !== 'undefined') {
                this.eventBus.emit(Events.SECTION_CHANGE_REQUESTED, {
                    sectionId: this.sectionId - 1
                });
            }
            // Fallback: Manter callback para compatibilidade (DEPRECATED)
            this.onNavigateBack();
        });

        console.log('[SectionContainer] Listeners bindados:', this._eventListeners.length);
    }

    /**
     * Dispose Pattern - Remove todos os event listeners (v0.13.1+)
     * Deve ser chamado ao trocar de seção para evitar memory leaks
     */
    dispose() {
        // Remover listeners DOM
        if (this._eventListeners && this._eventListeners.length > 0) {
            this._eventListeners.forEach(({ element, event, handler }) => {
                if (element) {
                    element.removeEventListener(event, handler);
                }
            });
            console.log('[SectionContainer] Disposed - listeners DOM removidos:', this._eventListeners.length);
            this._eventListeners = [];
        }

        // Remover listeners EventBus (v0.13.1+)
        if (this._eventBusUnsubscribers && this._eventBusUnsubscribers.length > 0) {
            this._eventBusUnsubscribers.forEach(unsubscribe => {
                if (typeof unsubscribe === 'function') {
                    unsubscribe();
                }
            });
            console.log('[SectionContainer] Disposed - listeners EventBus removidos:', this._eventBusUnsubscribers.length);
            this._eventBusUnsubscribers = [];
        }
    }

    /**
     * Mostra a pergunta atual
     */
    _showCurrentQuestion() {
        if (!this.sectionData) return;

        // Verificar se há follow-ups pendentes na fila (ex: após restaurar rascunho)
        if (this.followUpQueue.length > 0) {
            console.log('[SectionContainer] Mostrando follow-up da fila:', this.followUpQueue[0].id);
            this._showNextFollowUp();
            return;
        }

        const questions = this.sectionData.questions;

        // Verificar se tem skipQuestion primeiro
        if (this.sectionData.skipQuestion && this.currentQuestionIndex === 0 && !this.answers[this.sectionData.skipQuestion.id]) {
            const skipQ = this.sectionData.skipQuestion;
            this._showQuestion(skipQ);
            return;
        }

        // Calcular índice real (considerando skipQuestion)
        const realIndex = this.sectionData.skipQuestion ? this.currentQuestionIndex - 1 : this.currentQuestionIndex;

        if (realIndex >= 0 && realIndex < questions.length) {
            const question = questions[realIndex];
            // Verificar se esta pergunta já foi respondida (pode acontecer ao restaurar rascunho)
            if (this.answers[question.id]) {
                // Pergunta já respondida, avançar para próxima
                console.log('[SectionContainer] Pergunta já respondida:', question.id, '- avançando...');
                this.currentQuestionIndex++;
                this._updateBadge();
                this._showCurrentQuestion(); // Recursão para mostrar próxima
            } else {
                this._showQuestion(question);
            }
        } else if (realIndex >= questions.length) {
            // Todas as perguntas respondidas
            this._completeSection();
        }
    }

    /**
     * Retorna a pergunta atual para renderizar input (sem adicionar mensagem)
     * Usado ao restaurar rascunho ou voltar para seção em andamento
     */
    _getCurrentQuestionForInput() {
        if (!this.sectionData) return null;

        // Se há follow-ups pendentes, retornar próximo da fila
        if (this.followUpQueue.length > 0) {
            return this.followUpQueue[0];
        }

        const questions = this.sectionData.questions;

        // Verificar skipQuestion
        if (this.sectionData.skipQuestion && this.currentQuestionIndex === 0 && !this.answers[this.sectionData.skipQuestion.id]) {
            return this.sectionData.skipQuestion;
        }

        // Calcular índice real
        const realIndex = this.sectionData.skipQuestion ? this.currentQuestionIndex - 1 : this.currentQuestionIndex;

        if (realIndex >= 0 && realIndex < questions.length) {
            const question = questions[realIndex];
            // Se pergunta já respondida, avançar recursivamente
            if (this.answers[question.id]) {
                this.currentQuestionIndex++;
                this._updateBadge();
                return this._getCurrentQuestionForInput(); // Recursão
            }
            return question;
        }

        // Seção completa
        return null;
    }

    /**
     * Busca uma pergunta pelo ID em todas as estruturas da seção
     * v0.13.2: Helper para arquitetura backend-driven
     *
     * @param {string} questionId - ID da pergunta (ex: "3.6", "3.6.1")
     * @returns {Object|null} - Objeto da pergunta ou null se não encontrar
     */
    _findQuestionById(questionId) {
        if (!this.sectionData || !questionId) return null;

        // Buscar em skipQuestion
        if (this.sectionData.skipQuestion?.id === questionId) {
            return this.sectionData.skipQuestion;
        }

        // Buscar em questions principais
        for (const q of this.sectionData.questions) {
            if (q.id === questionId) return q;

            // Buscar em follow-ups (array de questions)
            if (q.followUp?.questions) {
                for (const fq of q.followUp.questions) {
                    if (fq.id === questionId) return fq;
                }
            }

            // Buscar em follow-up singular (question)
            if (q.followUp?.question?.id === questionId) {
                return q.followUp.question;
            }
        }

        return null;
    }

    /**
     * Adiciona mensagem do bot
     * Sincroniza com StateManager (v0.13.1+)
     */
    _addBotMessage(text, hint = null) {
        this.messages.push({ type: 'bot', text, hint });

        // Sincronizar com StateManager
        if (this.stateManager && this.sectionId) {
            this.stateManager.addMessage(this.sectionId, 'bot', text, hint);
        }

        this._updateChat();
    }

    /**
     * Adiciona mensagem do usuário
     * Sincroniza com StateManager (v0.13.1+)
     */
    _addUserMessage(text) {
        this.messages.push({ type: 'user', text });

        // Sincronizar com StateManager
        if (this.stateManager && this.sectionId) {
            this.stateManager.addMessage(this.sectionId, 'user', text);
        }

        this._updateChat();
    }

    /**
     * Remove última mensagem do usuário (para rollback em caso de validação falha)
     * CORREÇÃO v0.13.2: Necessário para reverter quando backend rejeita resposta
     */
    _removeLastUserMessage() {
        // Remover do array local de mensagens
        const messages = this.messages;
        for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].type === 'user') {
                messages.splice(i, 1);
                break;
            }
        }

        // Sincronizar com StateManager
        if (this.stateManager && this.sectionId) {
            const stateMessages = this.stateManager._state.sections[this.sectionId]?.messages;
            if (stateMessages) {
                for (let i = stateMessages.length - 1; i >= 0; i--) {
                    if (stateMessages[i].type === 'user') {
                        stateMessages.splice(i, 1);
                        break;
                    }
                }
            }
        }

        this._updateChat();
    }

    /**
     * Atualiza área de chat
     */
    _updateChat() {
        if (this.chatEl) {
            this.chatEl.innerHTML = this._renderMessages();
            // Scroll automático para o final quando há nova mensagem
            this._scrollChatToBottom();
        }
    }

    /**
     * Faz scroll automático para o final do chat
     */
    _scrollChatToBottom() {
        if (this.chatEl) {
            // Usar requestAnimationFrame para garantir que o DOM foi atualizado
            requestAnimationFrame(() => {
                this.chatEl.scrollTop = this.chatEl.scrollHeight;
            });
        }
    }

    /**
     * Mostra overlay "Gerando texto..." durante chamada API
     * v0.13.2+: Refatorado para usar UIOverlay
     */
    _showGeneratingTextOverlay() {
        UIOverlay.showGenerating('Seção finalizada com sucesso!<br>Gerando texto...');
    }

    /**
     * Esconde overlay "Gerando texto..."
     * v0.13.2+: Refatorado para usar UIOverlay
     */
    _hideGeneratingTextOverlay() {
        UIOverlay.hideGenerating();
    }

    /**
     * Atualiza badge de status
     */
    _updateBadge() {
        const badge = this.container.querySelector('.section-header__badge');
        if (badge) {
            badge.textContent = this._getStatusLabel();
        }
    }

    /**
     * Completa a seção
     */
    async _completeSection() {
        this.state = 'completed';

        // NÃO setar placeholder aqui - o texto já foi ou será setado por onComplete
        // Se por algum motivo não houver texto (offline), o placeholder será setado em _onSectionComplete do BOApp

        // v0.13.1+: Emitir evento via EventBus
        if (this.eventBus && typeof Events !== 'undefined') {
            this.eventBus.emit(Events.SECTION_COMPLETED, {
                sectionId: this.sectionId,
                answers: this.answers
            });
        }

        // Callback - AGUARDAR conclusão antes de renderizar
        await this.onComplete(this.sectionId, this.answers);

        // Esconder overlay após conclusão
        this._hideGeneratingTextOverlay();

        // Re-renderizar SOMENTE depois que onComplete terminar
        this.render();
    }

    /**
     * Pula a seção
     */
    _skipSection(skipReason = null) {
        console.log('[SectionContainer] _skipSection chamado - skipReason param:', skipReason, 'this.skipReason:', this.skipReason);
        this.state = 'skipped';
        this.skipReason = skipReason || this.skipReason || null;
        console.log('[SectionContainer] _skipSection - skipReason final:', this.skipReason);

        // v0.13.1+: Emitir evento via EventBus
        if (this.eventBus && typeof Events !== 'undefined') {
            this.eventBus.emit('section:skipped', {
                sectionId: this.sectionId,
                skipReason: this.skipReason
            });
        }

        this.onSkip(this.sectionId);
        this.render();
    }

    /**
     * Define a razão do skip (chamado pela API após skip question)
     */
    setSkipReason(skipReasonMessage) {
        console.log('[SectionContainer] setSkipReason chamado com:', skipReasonMessage);
        this.skipReason = skipReasonMessage || null;
        console.log('[SectionContainer] skipReason definido como:', this.skipReason);
    }

    /**
     * Copia texto gerado
     */
    _copyGeneratedText() {
        if (!this.generatedText) return;

        navigator.clipboard.writeText(this.generatedText).then(() => {
            const copyBtn = this.container.querySelector('#section-copy-btn');
            if (copyBtn) {
                copyBtn.textContent = '✅ Copiado!';
                setTimeout(() => {
                    copyBtn.textContent = '📋 Copiar';
                }, 2000);
            }
        });
    }

    /**
     * Mostra transição com fade
     */
    fadeOut() {
        return new Promise(resolve => {
            this.container.classList.remove('section-container--visible');
            this.container.classList.add('section-container--hidden');
            setTimeout(resolve, 200);
        });
    }

    /**
     * Mostra seção com fade
     */
    fadeIn() {
        return new Promise(resolve => {
            this.container.classList.remove('section-container--hidden');
            this.container.classList.add('section-container--visible');
            setTimeout(resolve, 200);
        });
    }

    /**
     * Define texto gerado (vem da API)
     */
    setGeneratedText(text) {
        this.generatedText = text;
        // Re-renderizar se seção já está completa (BUG FIX: texto não aparecia)
        if (this.state === 'completed') {
            this.render();
        }
    }

    /**
     * Retorna estado atual
     */
    getState() {
        return {
            sectionId: this.sectionId,
            state: this.state,
            answers: this.answers,
            messages: this.messages,
            currentQuestionIndex: this.currentQuestionIndex,
            generatedText: this.generatedText
        };
    }

    /**
     * Gera string com data e hora atual no formato: "31/12/2025, 14h30, terça-feira"
     * Usada como pré-preenchimento para pergunta 1.1
     */
    _generateCurrentDateTime() {
        const now = new Date();

        // Formatar dia/mês
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        const date = `${day}/${month}/${year}`;

        // Formatar hora
        const hour = String(now.getHours()).padStart(2, '0');
        const minute = String(now.getMinutes()).padStart(2, '0');
        const time = `${hour}h${minute}`;

        // Dia da semana em português
        const daysOfWeek = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];
        const dayOfWeek = daysOfWeek[now.getDay()];

        return `${date}, ${time}, ${dayOfWeek}`;
    }
}

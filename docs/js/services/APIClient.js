/**
 * APIClient - Cliente para comunicação com a API FastAPI
 * BO Inteligente v1.0
 */

class APIClient {
    /**
     * Cliente para comunicação com a API FastAPI
     */
    constructor(baseUrl = null) {
        this.baseUrl = baseUrl || this._detectBaseUrl();
        this.sessionId = null;
        this.boId = null;
    }

    /**
     * Detecta URL base baseado no ambiente
     */
    _detectBaseUrl() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        return 'https://bo-assistant-backend.onrender.com';
    }

    /**
     * Faz requisição genérica
     */
    async _request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            console.log(`[API] ${options.method || 'GET'} ${endpoint}`);

            const response = await fetch(url, finalOptions);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(
                    errorData.detail || `Erro ${response.status}`,
                    response.status,
                    errorData
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }

            // Erro de rede
            throw new APIError(
                'Não foi possível conectar ao servidor. Verifique sua conexão.',
                0,
                { originalError: error.message }
            );
        }
    }

    /**
     * Verifica se servidor está online
     */
    async healthCheck() {
        try {
            const data = await this._request('/health');
            return { online: true, ...data };
        } catch (error) {
            return { online: false, error: error.message };
        }
    }

    /**
     * Inicia nova sessão de BO
     */
    async startSession() {
        const data = await this._request('/new_session', {
            method: 'POST',
        });

        this.sessionId = data.session_id;
        this.boId = data.bo_id;

        console.log(`[API] Sessão iniciada: ${this.boId}`);

        return data;
    }

    /**
     * Envia resposta para o backend (validação + próxima pergunta)
     * NOTA: O backend atual só suporta Seção 1. Para outras seções,
     * usaremos modo offline temporariamente.
     */
    async sendAnswer(message, llmProvider = 'gemini') {
        if (!this.sessionId) {
            throw new APIError('Sessão não iniciada', 400);
        }

        const data = await this._request('/chat', {
            method: 'POST',
            body: JSON.stringify({
                session_id: this.sessionId,
                message: message,
                llm_provider: llmProvider,
            }),
        });

        return data;
    }

    /**
     * Edita uma resposta anterior
     */
    async editAnswer(step, message, llmProvider = 'gemini') {
        if (!this.sessionId) {
            throw new APIError('Sessão não iniciada', 400);
        }

        const data = await this._request(`/chat/${this.sessionId}/answer/${step}`, {
            method: 'PUT',
            body: JSON.stringify({
                message: message,
                llm_provider: llmProvider,
            }),
        });

        return data;
    }

    /**
     * Envia feedback
     */
    async sendFeedback(feedbackType, eventId = null, userMessage = null, context = null) {
        if (!this.boId) {
            console.warn('[API] BO ID não disponível para feedback');
            return null;
        }

        const data = await this._request('/feedback', {
            method: 'POST',
            body: JSON.stringify({
                bo_id: this.boId,
                event_id: eventId,
                feedback_type: feedbackType,
                user_message: userMessage,
                context: context,
                metadata: {
                    screen_resolution: `${screen.width}x${screen.height}`,
                    viewport: `${window.innerWidth}x${window.innerHeight}`,
                    user_agent: navigator.userAgent,
                },
            }),
        });

        return data;
    }

    /**
     * Obtém status da sessão
     */
    async getSessionStatus() {
        if (!this.sessionId) {
            return null;
        }

        const data = await this._request(`/session/${this.sessionId}/status`);
        return data;
    }

    /**
     * Retorna IDs atuais
     */
    getIds() {
        return {
            sessionId: this.sessionId,
            boId: this.boId,
        };
    }

    /**
     * Restaura sessão existente
     */
    restoreSession(sessionId, boId) {
        this.sessionId = sessionId;
        this.boId = boId;
    }
}

/**
 * Classe de erro customizada para API
 */
class APIError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

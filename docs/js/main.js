/**
 * main.js - Sistema DEBUG e Inicialização da Aplicação
 * BO Inteligente v1.0
 */

// ============================================
// SISTEMA DEBUG
// ============================================

const DEBUG = {
    enabled: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',

    log: function(component, message, data = null) {
        if (!this.enabled) return;
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[${timestamp}] [${component}]`;
        if (data) {
            console.log(prefix, message, data);
        } else {
            console.log(prefix, message);
        }
    },

    warn: function(component, message, data = null) {
        if (!this.enabled) return;
        console.warn(`[${component}]`, message, data || '');
    },

    error: function(component, message, error = null) {
        // Erros sempre logados
        console.error(`[${component}]`, message, error || '');
    }
};

// Expor para debug manual
window.DEBUG = DEBUG;

// ============================================
// INICIALIZAÇÃO DA APLICAÇÃO
// ============================================

// Instância global da aplicação
let app = null;

window.addEventListener('load', async () => {
    console.log('[Init] BO Inteligente v1.0 - Design Modularizado');
    console.log('[Init] Inicializando...');

    // Criar e inicializar aplicação
    app = new BOApp();
    await app.init();

    // Expor para debug
    window.app = app;
    window.progressBar = app.progressBar;
    window.sectionContainer = app.sectionContainer;
    window.api = app.api;

    console.log('[Init] Aplicação pronta!');
    console.log('[Init] Use window.app para debug.');
});

// ============================================
// FUNÇÕES GLOBAIS DE DEBUG
// ============================================

/**
 * Navega para uma seção (para debug)
 */
function goToSection(sectionId) {
    if (app) {
        app._navigateToSection(sectionId);
    }
}

/**
 * Limpa rascunho e reinicia
 */
function resetApp() {
    if (app) {
        app.clearDraft();
    }
    location.reload();
}

/**
 * Mostra estado atual
 */
function showState() {
    if (app) {
        console.log('Estado das seções:', app.sectionsState);
        console.log('Seção atual:', app.currentSectionIndex + 1);
        console.log('API:', app.api.getIds());
    }
}

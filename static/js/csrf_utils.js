/**
 * Utilidades CSRF para Django en Cloud Run
 * Proporciona funciones helper para obtener y enviar tokens CSRF correctamente
 */

/**
 * Obtiene el token CSRF desde las cookies
 * @returns {string|null} El token CSRF o null si no se encuentra
 */
function getCsrfTokenFromCookie() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Obtiene el token CSRF desde el DOM (input hidden en formularios)
 * @returns {string|null} El token CSRF o null si no se encuentra
 */
function getCsrfTokenFromDOM() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : null;
}

/**
 * Obtiene el token CSRF con fallback: primero intenta desde cookie, luego desde DOM
 * @returns {string|null} El token CSRF o null si no se encuentra
 */
function getCsrfToken() {
    return getCsrfTokenFromCookie() || getCsrfTokenFromDOM();
}

/**
 * Configura headers CSRF para fetch requests
 * @param {Object} headers - Headers existentes (opcional)
 * @returns {Object} Headers con CSRF token incluido
 */
function getCsrfHeaders(headers = {}) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
    return headers;
}

/**
 * Wrapper de fetch con CSRF token automático
 * @param {string} url - URL del endpoint
 * @param {Object} options - Opciones de fetch
 * @returns {Promise} Promise del fetch
 */
function fetchWithCsrf(url, options = {}) {
    options.headers = getCsrfHeaders(options.headers || {});
    options.credentials = options.credentials || 'same-origin';
    return fetch(url, options);
}

/**
 * Verifica si el token CSRF está disponible y válido
 * @returns {boolean} True si el token está disponible
 */
function isCsrfTokenAvailable() {
    const token = getCsrfToken();
    return token !== null && token !== '';
}

/**
 * Log de debug para verificar configuración CSRF
 */
function debugCsrf() {
    console.group('🔒 CSRF Debug Info');
    console.log('Cookie Token:', getCsrfTokenFromCookie());
    console.log('DOM Token:', getCsrfTokenFromDOM());
    console.log('Final Token:', getCsrfToken());
    console.log('Token Available:', isCsrfTokenAvailable());
    console.log('Cookies:', document.cookie);
    console.groupEnd();
}

// Exponer funciones globalmente
window.csrfUtils = {
    getCsrfToken,
    getCsrfTokenFromCookie,
    getCsrfTokenFromDOM,
    getCsrfHeaders,
    fetchWithCsrf,
    isCsrfTokenAvailable,
    debugCsrf
};

// Log de inicialización en desarrollo
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('✓ CSRF Utils loaded');
}

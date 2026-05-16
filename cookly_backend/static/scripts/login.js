import { getOrCreateFingerprint } from './fingerprint.js';
import { getStoredParams } from "./manageParamsMod.js";

export function handleAuthSuccess() {
    if (getStoredParams().ref_id) {
        window.location.href = '/pages/auth-to-client.html';
    }
    else {
        window.location.href = '/pages/profile.html';
    }
}

export function initLoginForm() {
    const loginButton = document.getElementById('loginButton');
    if (!loginButton) return;

    loginButton.addEventListener('click', handleLogin);

    async function handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const fingerprint = await getOrCreateFingerprint();

        showLoader(loginButton, true);

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Device-Fingerprint': fingerprint,
                },
                body: JSON.stringify({ email, password, fingerprint })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(
                    response.status === 403
                        ? 'Неправильный email или пароль'
                        : error.detail || 'Ошибка входа'
                );
            }
            handleAuthSuccess();
        } catch (error) {
            alert(error.message);
            showLoader(loginButton, false);
        }
    }

    function showLoader(button, isLoading) {
        if (isLoading) {
            button.dataset.originalText = button.textContent;
            button.textContent = '';
            button.disabled = true;

            const spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm';
            spinner.setAttribute('role', 'status');
            spinner.setAttribute('aria-hidden', 'true');

            const loadingText = document.createTextNode(' Загрузка...');

            button.appendChild(spinner);
            button.appendChild(loadingText);
        } else {
            button.textContent = button.dataset.originalText || 'Войти';
            button.disabled = false;
        }
    }
}

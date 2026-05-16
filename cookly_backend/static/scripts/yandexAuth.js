import { getOrCreateFingerprint } from './fingerprint.js';
import { fetchWithAuth } from './commonApi.js';

export async function sendYandexTokenToServer(token, authType) {
    const fingerprint = await getOrCreateFingerprint();
    const endpoint = authType === 'login' ? '/api/login/yandex' : '/api/register/yandex';

    await fetchWithAuth(endpoint, {
        method: 'POST',
        body: JSON.stringify({ yandex_token: token })
    });

    handleAuthSuccess();
}

function handleAuthSuccess() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('client_id') && params.get('redirect_url')) {
        window.location.href = '/pages/auth-to-client.html';
    } else {
        window.location.href = '/pages/profile.html';
    }
}

export function initYandexAuth({ clientId, redirectUri, authType = 'login' }) {
    const button = document.getElementById('yandexAuthBtn');
    if (!button) return;

    button.addEventListener('click', handleYandexAuth);

    async function handleYandexAuth() {
        alert("BOB")
        try {
            const data = await YaAuthSuggest.init(
                {
                    client_id: clientId,
                    response_type: 'token',
                    redirect_uri: redirectUri
                },
                window.location.origin
            ).then(({ handler }) => handler());

            if (!data?.access_token) {
                throw new Error('Не удалось получить токен');
            }

            await sendYandexTokenToServer(data.access_token, authType);
        } catch (error) {
            console.error('Yandex auth error:', error);
            handleYandexError(error);
        }
    }

    function handleYandexError(error) {
        const message = error.type === 'access_denied'
            ? 'Вы отменили авторизацию'
            : error.message || 'Ошибка авторизации через Яндекс';

        alert(message);
    }
}
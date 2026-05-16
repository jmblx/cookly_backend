import { getStoredParams } from './manageParamsMod.js';

export function setupReturnButton() {
    const params = getStoredParams();
    const returnButton = document.getElementById('return-button');
    if (!returnButton) return;

    const requiredParams = ['ref_id', 'redirect_url'];
    const hasAuthParams = requiredParams.every(param => params[param]);

    if (!hasAuthParams) {
        returnButton.classList.add('hidden');
        return;
    }

    returnButton.textContent = `<- Authorize on ${params.client_name || 'Client'}`;
    returnButton.addEventListener('click', () => {
        const redirectUrl = new URL('/pages/auth-to-client.html', window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            if (key !== 'client_name') {
                redirectUrl.searchParams.append(key, value);
            }
        });
        window.location.href = redirectUrl.toString();
    });
}

export function openAvatarUpload() {
    document.getElementById('avatar-upload')?.click();
}
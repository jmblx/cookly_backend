import { getOrCreateFingerprint } from './fingerprint.js';
// import { initYandexAuth } from './yandexAuth.js';
import { saveInitialQueryParams } from './manageParamsMod.js';
import {handleAuthSuccess} from "./login.js";
import { initRegisterConfirm } from './registerConfirm.js';

let confirmModal;

document.addEventListener('DOMContentLoaded', async () => {
    const fingerprint = await getOrCreateFingerprint();

    saveInitialQueryParams();

    // initYandexAuth({
    //     clientId: '83c64ffbf6db4ea282b7e4d0c5cfbb51',
    //     redirectUri: 'https://bidlo.taild3ccfe.ts.net/pages/yandex-login.html',
    //     authType: 'register'
    // });

    confirmModal = initRegisterConfirm(handleAuthSuccess);

    document.getElementById('registerButton')
        .addEventListener('click', handleRegister);
});

async function handleRegister() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const fingerprint = await getOrCreateFingerprint();

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Device-Fingerprint': fingerprint,
            },
            body: JSON.stringify({ email, password, fingerprint })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка регистрации');
        }

        confirmModal.openConfirmModal(email);

    } catch (error) {
        alert(error.message);
    }
}
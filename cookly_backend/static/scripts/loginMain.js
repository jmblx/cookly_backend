import { initYandexAuth } from './yandexAuth.js';
import {handleAuthSuccess, initLoginForm} from './login.js';
import { initPasswordReset } from './passwordReset.js';
import { saveInitialQueryParams } from './manageParamsMod.js';
import { fetchWithAuth } from './commonApi.js';

document.addEventListener('DOMContentLoaded', async () => {
    saveInitialQueryParams();
    initYandexAuth({
        clientId: '83c64ffbf6db4ea282b7e4d0c5cfbb51',
        redirectUri: 'https://bidlo.taild3ccfe.ts.net/pages/yandex-login.html',
        authType: 'login'
    });
    initLoginForm();
    initPasswordReset();
    await renderAccountSelector();
});

async function renderAccountSelector() {
    let resp;
    try {
        resp = await fetchWithAuth('/api/available-accounts');
        if (!resp.ok) throw new Error(resp.statusText);
    } catch {
        return;
    }

    const { accounts } = await resp.json();
    const keys = Object.keys(accounts || {});
    if (keys.length === 0) return;

    const section = document.getElementById('accountSection');
    const selector = document.getElementById('accountSelector');
    section.style.display = 'block';

    keys.forEach(id => {
        const info = accounts[id];
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-light w-100 mb-2 d-flex align-items-center';
        btn.innerHTML = `
            <img src="${info.avatar_url}" 
                 class="rounded-circle me-2" 
                 width="24" height="24" 
                 alt="avatar">
            <span>${info.email}</span>
        `;
        btn.addEventListener('click', async () => {
            try {
                const sw = await fetchWithAuth('/api/activate-account', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_active_user_id: id })
                });
                if (!sw.ok) throw new Error(sw.statusText);
                handleAuthSuccess()
            } catch (e) {
                console.error('Activate account error:', e);
                alert('Не удалось переключиться на аккаунт');
            }
        });
        selector.appendChild(btn);
    });
}

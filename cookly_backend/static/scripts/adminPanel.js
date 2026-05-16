// adminPanel.js

import {fetchWithAuth, loadUserAvatar, loadUserData, logoutClient, redirectToLogin} from './commonApi.js';

document.addEventListener('DOMContentLoaded', async () => {
    await renderUserPanel();
    await loadUserAvatar('user-panel-avatar');
});

async function renderUserPanel() {
    const me = await loadUserData();

    // Получаем аккаунты
    const availResp = await fetchWithAuth('/api/available-accounts');
    const { accounts, active_account_id } = await availResp.json();

    const panel = document.createElement('div');
    panel.className = 'admin-panel';

    // Левая часть (вкладки для админа)
    if (me.is_admin) {
        const path = window.location.pathname;
        const pageName = path.substring(path.lastIndexOf('/') + 1).split('.')[0];
        const tabs = [
            { name: 'resourceServers', label: 'Resource Servers', href: '/pages/resourceServers.html' },
            { name: 'clients',         label: 'Clients',          href: '/pages/clients.html'         },
        ];
        const left = document.createElement('div');
        tabs.forEach(tab => {
            const a = document.createElement('a');
            a.href = tab.href;
            a.textContent = tab.label;
            if (tab.name === pageName) a.classList.add('active-tab');
            left.appendChild(a);
        });
        panel.appendChild(left);
    } else {
        panel.appendChild(document.createElement('div'));
    }

    // Правая часть
    const right = document.createElement('div');
    right.style.display = 'flex';
    right.style.alignItems = 'center';
    right.style.gap = '10px';

    // Ссылка на профиль (всегда доступна)
    const profileLink = document.createElement('a');
    profileLink.href = '/pages/profile.html';
    const profileImg = document.createElement('img');
    profileImg.id = 'user-panel-avatar';
    profileImg.alt = 'User Avatar';
    profileImg.style.width = '32px';
    profileImg.style.height = '32px';
    profileImg.style.borderRadius = '50%';
    profileImg.src = '/icons/defaultAvatar.svg';
    profileLink.appendChild(profileImg);
    right.appendChild(profileLink);

    // Селектор аккаунтов
    const switcher = document.createElement('div');
    switcher.className = 'account-switcher';
    switcher.style.position = 'relative';

    const switchIcon = document.createElement('img');
    switchIcon.src = '/icons/switchUser.svg'; // иконка «сменить аккаунт»
    switchIcon.alt = 'Switch Account';
    switchIcon.classList.add('panel-icon');
    switchIcon.style.cursor = 'pointer';

    switcher.appendChild(switchIcon);

    const menu = document.createElement('div');
    menu.className = 'account-menu';
    Object.assign(menu.style, {
      position: 'absolute', top: '100%', right: '0',
      background: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
      borderRadius: '4px', overflow: 'hidden', display: 'none', zIndex: '1001'
    });

    Object.entries(accounts).forEach(([id, info]) => {
        const item = document.createElement('div');
        item.className = 'account-item d-flex align-items-center p-2';
        item.style.cursor = id === active_account_id ? 'default' : 'pointer';
        if (id === active_account_id) {
            item.style.background = '#e9ecef';
            item.style.opacity = '0.6';
        }
        item.innerHTML = `
            <img src="${info.avatar_url}" width="24" height="24" class="rounded-circle me-2">
            <span>${info.email}</span>
        `;
        if (id !== active_account_id) {
            item.addEventListener('click', () => switchAccount(id));
        }
        menu.appendChild(item);
    });

    // Кнопка «Добавить аккаунт»
    const addBtn = document.createElement('div');
    addBtn.className = 'account-item d-flex align-items-center p-2';
    addBtn.style.cursor = 'pointer';
    addBtn.style.borderTop = '1px solid #e0e0e0';
    addBtn.innerHTML = `
        <span style="font-size: 20px; margin-right: 8px;">＋</span>
        <span>Добавить аккаунт</span>
    `;
    addBtn.addEventListener('click', async () => {
        try {
            const resp = await fetchWithAuth('/api/deactivate-current-account', { method: 'POST' });
            if (!resp.ok) throw new Error(resp.statusText);
            redirectToLogin();
        } catch (e) {
            console.error(e);
            alert('Не удалось подготовить добавление аккаунта');
        }
    });
    menu.appendChild(addBtn);

    switcher.appendChild(menu);
    right.appendChild(switcher);

    // Кнопка logout
    const logoutBtn = document.createElement('button');
    logoutBtn.id = 'logout-button';
    logoutBtn.className = 'logout-button';
    logoutBtn.title = 'Logout';
    logoutBtn.onclick = () => logoutClient();
    const logoutImg = document.createElement('img');
    logoutImg.src = '/icons/logout.svg';
    logoutImg.alt = 'Logout';
    logoutImg.classList.add('panel-icon');
    logoutBtn.appendChild(logoutImg);
    right.appendChild(logoutBtn);

    panel.appendChild(right);
    document.body.prepend(panel);

    switchIcon.addEventListener('click', e => {
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', e => {
        if (!switcher.contains(e.target)) menu.style.display = 'none';
    });
}

async function switchAccount(newId) {
    try {
        const resp = await fetchWithAuth('/api/switch-account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_active_user_id: newId })
        });
        if (!resp.ok) throw new Error(resp.statusText);
        window.location.reload();
    } catch (e) {
        console.error('Switch account error:', e);
        alert('Не удалось сменить аккаунт');
    }
}

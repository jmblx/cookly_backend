// authToClient.js

import {fetchWithAuth, loadUserAvatar, loadUserData} from './commonApi.js';
import { getStoredParams } from './manageParamsMod.js';
import { logoutClient } from "./commonApi.js";

function getPresignedExpiry(url) {
    try {
        const params = new URL(url).searchParams;
        const dateStr = params.get('X-Amz-Date');       // e.g. "20250609T181711Z"
        const expires = parseInt(params.get('X-Amz-Expires') || '0', 10);
        if (!dateStr || !expires) return null;

        const year  = +dateStr.slice(0, 4);
        const month = +dateStr.slice(4, 6) - 1;
        const day   = +dateStr.slice(6, 8);
        const hour  = +dateStr.slice(9, 11);
        const min   = +dateStr.slice(11, 13);
        const sec   = +dateStr.slice(13, 15);

        const dt = new Date(Date.UTC(year, month, day, hour, min, sec));
        dt.setSeconds(dt.getSeconds() + expires - 10);
        return dt;
    } catch {
        return null;
    }
}

// Загружает и кэширует presigned avatar_url клиента
async function loadClientAvatar(clientId, imgElementId = 'client-avatar') {
    if (!clientId) return;
    const storageKey = `clientAvatar:${clientId}`;

    // Проверяем в localStorage
    let cached = null;
    try {
        const raw = localStorage.getItem(storageKey);
        if (raw) {
            cached = JSON.parse(raw);
            const expiresAt = new Date(cached.expires_at);
            if (expiresAt > new Date()) {
                document.getElementById(imgElementId).src = cached.avatar_url;
                return;
            }
        }
    } catch {
    }

    try {
        const response = await fetchWithAuth(`/api/client/${clientId}/avatar`);
        if (!response.ok) throw new Error('Ошибка загрузки аватарки клиента');
        const data = await response.json();
        const avatarUrl = data.avatar_url;
        const expiresAt = getPresignedExpiry(avatarUrl);
        if (expiresAt) {
            localStorage.setItem(storageKey, JSON.stringify({
                avatar_url: avatarUrl,
                expires_at: expiresAt.toISOString()
            }));
        }
        document.getElementById(imgElementId).src = avatarUrl;
    } catch (e) {
        console.error(e);
    }
}

// Получает данные о клиенте по ID клиента
async function getClientData(clientId) {
    try {
        const response = await fetchWithAuth(`/api/client/${clientId}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных клиента');
        return await response.json();
    } catch (error) {
        console.error('Error loading client data:', error);
        throw error;
    }
}

// Получает данные о референсе по ref_id
async function getRefData(refId) {
    try {
        // Сначала получаем информацию о референсе
        const response = await fetchWithAuth(`/api/client/refs/${refId}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных референса');
        return await response.json();
    } catch (error) {
        console.error('Error loading ref data:', error);
        throw error;
    }
}

// Находит client_id по ref_id (ищет среди всех клиентов)
async function findClientIdByRefId(refId) {
    try {
        // Пытаемся загрузить данные референса
        const refData = await getRefData(refId);

        if (!refData || !refData.client_name) {
            throw new Error('Не удалось получить данные референса');
        }

        // Теперь нужно найти ID клиента по имени
        // Для этого можно сделать поиск клиентов
        const searchResponse = await fetchWithAuth(`/api/client/search?search_input=${encodeURIComponent(refData.client_name)}`);
        if (!searchResponse.ok) throw new Error('Ошибка поиска клиента');

        const searchResults = await searchResponse.json();

        // Ищем клиента с соответствующим именем
        for (const [clientId, clientData] of Object.entries(searchResults)) {
            if (clientData.name === refData.client_name) {
                return parseInt(clientId);
            }
        }

        throw new Error(`Клиент "${refData.client_name}" не найден`);

    } catch (error) {
        console.error('Error finding client by ref:', error);
        throw error;
    }
}

// Альтернативный метод: получить все клиенты и найти нужный
async function findClientIdByRefIdAlternative(refId) {
    try {
        // Получаем данные референса
        const refData = await getRefData(refId);

        if (!refData || !refData.client_name) {
            throw new Error('Не удалось получить данные референса');
        }

        // Ищем клиента постранично
        let afterId = 0;
        const pageSize = 50;

        while (true) {
            const response = await fetchWithAuth(`/api/client/ids_data?after_id=${afterId}&page_size=${pageSize}`);
            if (!response.ok) throw new Error('Ошибка загрузки списка клиентов');

            const clientsData = await response.json();

            // Если нет результатов - завершаем
            if (!clientsData || Object.keys(clientsData).length === 0) {
                break;
            }

            // Ищем клиента с нужным именем
            for (const [clientId, clientData] of Object.entries(clientsData)) {
                if (clientData.name === refData.client_name) {
                    return parseInt(clientId);
                }

                // Обновляем afterId для следующей итерации
                afterId = Math.max(afterId, parseInt(clientId));
            }

            // Если получили меньше элементов, чем pageSize, значит это последняя страница
            if (Object.keys(clientsData).length < pageSize) {
                break;
            }
        }

        throw new Error(`Клиент "${refData.client_name}" не найден`);

    } catch (error) {
        console.error('Error finding client by ref (alternative):', error);
        throw error;
    }
}

export async function initAuthToClient() {
    try {
        const params = getStoredParams();
        const fingerprint = localStorage.getItem('deviceFingerprint') || '';

        // Проверяем наличие ref_id
        if (!params.ref_id) {
            throw new Error('Не указан ref_id');
        }

        // 1. Загружаем данные пользователя
        loadUserData("user-email");
        await loadUserAvatar('user-avatar');

        // 2. Получаем данные референса
        const refId = parseInt(params.ref_id, 10);
        const refData = await getRefData(refId);

        if (!refData) {
            throw new Error('Референс не найден');
        }

        // 3. Находим client_id по имени клиента из референса
        const clientId = await findClientIdByRefId(refId);

        if (!clientId) {
            throw new Error('Не удалось определить клиента');
        }

        // 4. Загружаем аватар клиента
        await loadClientAvatar(clientId, 'client-avatar');

        // 5. Формируем required_resources на основе данных референса
        const requiredResources = {
            user_data_needed: refData.user_scopes || [],
            rs_ids: Object.keys(refData.ref_resource_servers || {}).map(id => parseInt(id))
        };

        // 6. Авторизуем клиента
        const authData = await authorizeClient({
            ref_id: refId,
            redirect_url: params.redirect_url,
            code_verifier: params.code_verifier,
            code_challenge_method: params.code_challenge_method,
            client_id: clientId,
            required_resources: JSON.stringify(requiredResources)
        }, fingerprint);

        // 7. Настраиваем UI
        setupUI(authData, refData, requiredResources);

    } catch (error) {
        handleAuthError(error);
    }
}

async function authorizeClient(params, fingerprint) {
    try {
        // Подготавливаем тело запроса
        const requestBody = {
            redirect_url: params.redirect_url,
            code_verifier: params.code_verifier,
            code_challenge_method: params.code_challenge_method,
            fingerprint
        };

        // Добавляем ref_id если есть
        if (params.ref_id) {
            requestBody.ref_id = parseInt(params.ref_id, 10);
        }

        // Отправляем запрос
        const response = await fetchWithAuth('/api/auth-to-client', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        // Получаем текст ответа
        const responseText = await response.text();

        if (!response.ok) {
            // Пытаемся распарсить ошибку
            let errorData;
            try {
                errorData = JSON.parse(responseText);
            } catch (e) {
                errorData = { error: { title: responseText || 'Unknown error' } };
            }

            console.error('Authorization failed:', {
                status: response.status,
                statusText: response.statusText,
                responseText: responseText
            });

            throw new Error(errorData?.error?.title || `Authorization failed: ${response.status} ${response.statusText}`);
        }

        // Парсим успешный ответ
        try {
            return JSON.parse(responseText);
        } catch (e) {
            console.error('Failed to parse response as JSON:', responseText);
            throw new Error('Invalid response format from server');
        }

    } catch (error) {
        console.error('Error in authorizeClient:', error);
        throw error;
    }
}

function setupUI(authData, refData, requiredResources) {
    // Устанавливаем имя клиента
    document.getElementById('client-name').textContent = refData.client_name || 'Неизвестный клиент';

    const resourcesContainer = document.getElementById('requested-resources');
    resourcesContainer.innerHTML = ''; // Очищаем контейнер

    // Добавляем информацию о запрошенных данных пользователя
    if (requiredResources.user_data_needed && requiredResources.user_data_needed.length > 0) {
        const userDataStr = requiredResources.user_data_needed
            .map(scope => {
                switch(scope) {
                    case 'email': return 'Email';
                    case 'avatar_path': return 'Аватар';
                    default: return scope;
                }
            })
            .join(', ');

        addResourceItem(resourcesContainer,
            'Требуемые данные пользователя:',
            userDataStr);
    }

    // Добавляем информацию о ресурсных серверах
    if (refData.ref_resource_servers && Object.keys(refData.ref_resource_servers).length > 0) {
        const rsNames = Object.values(refData.ref_resource_servers).map(rs => rs.name);
        if (rsNames.length > 0) {
            addResourceItem(resourcesContainer,
                'Доступ к действиям на сервисах:',
                rsNames.join(', '));
        }
    }

    // // Добавляем информацию о самом референсе
    // if (refData.name) {
    //     addResourceItem(resourcesContainer,
    //         'Название референса:',
    //         refData.name);
    // }

    // Настраиваем кнопку авторизации
    document.getElementById('authorize-button').addEventListener('click', () => {
        if (document.getElementById('permission-checkbox').checked) {
            const redirectUrl = new URL(authData.redirect_url);
            redirectUrl.searchParams.append('auth_code', authData.auth_code);
            window.location.href = redirectUrl.toString();
        } else {
            alert('Пожалуйста, разрешите доступ к запрошенным ресурсам.');
        }
    });

    // Настраиваем ссылки на профиль
    document.getElementById('profile-link')?.addEventListener('click', goToProfilePage);
    document.querySelector('.gear-icon')?.addEventListener('click', e => {
        e.stopPropagation();
        goToProfilePage();
    });
}

function addResourceItem(container, title, content) {
    const li = document.createElement('li');
    li.className = 'list-group-item permission-item';
    li.innerHTML = `<strong>${title}</strong> ${content}`;
    container.appendChild(li);
}

function goToProfilePage() {
    const profileUrl = new URL('/pages/profile.html', window.location.origin);
    window.location.href = profileUrl.toString();
}

function handleAuthError(error) {
    console.error('Authorization error:', error);
    let message = 'Произошла ошибка авторизации';

    if (error.message.includes('is not a valid redirect URL')) {
        const invalidUrl = error.message.split('is not a valid redirect URL')[0].trim();
        message = `Недопустимый URL для перенаправления: ${invalidUrl}`;
    } else if (error.message.includes('Референс не найден')) {
        message = 'Референс не найден или у вас нет к нему доступа';
    } else if (error.message.includes('Не удалось определить клиента')) {
        message = 'Не удалось найти клиента, связанного с этим референсом';
    } else if (error.message !== 'Authorization failed') {
        message = error.message;
    }

    // Показываем сообщение об ошибке
    const errorContainer = document.getElementById('error-message');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', initAuthToClient);
document.getElementById("logout-button")?.addEventListener("click", logoutClient);
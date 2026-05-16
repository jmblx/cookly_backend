// clientRef.js

let clientId = null;
let refId = null;
let isEditMode = false;
let selectedResourceServers = new Map(); // Map<id, {id, name}>
let currentRefData = null;
let searchTimeout = null;
let searchDebounceDelay = 500; // Задержка в мс

document.addEventListener('DOMContentLoaded', async () => {
    // Получаем параметры из URL
    const params = new URLSearchParams(window.location.search);
    clientId = params.get('clientId');
    refId = params.get('refId');

    if (!clientId) {
        alert('Client ID не указан!');
        window.location.href = '/pages/clients.html';
        return;
    }

    // Инициализируем панель поиска
    initSearchPanel();

    // Загружаем информацию о клиенте
    await loadClientInfo();

    // Устанавливаем режим работы (создание или редактирование)
    isEditMode = !!refId;

    if (isEditMode) {
        // Режим редактирования - загружаем данные референса
        await loadRefData();
        document.getElementById('delete-ref-btn').style.display = 'block';
        document.getElementById('client-ref-title').textContent = 'Редактирование референса данных';
    } else {
        // Режим создания
        document.getElementById('client-ref-title').textContent = 'Создание нового референса данных';
    }

    // Настраиваем обработчики событий
    setupEventListeners();
});

// Функция инициализации панели поиска
function initSearchPanel() {
    const searchInput = document.getElementById('rs-search-input');
    const searchIcon = document.createElement('img');
    searchIcon.src = '/icons/lupa.png';
    searchIcon.alt = 'Поиск';
    searchIcon.className = 'search-panel-icon';

    // Создаем контейнер для иконки
    const iconContainer = document.createElement('div');
    iconContainer.className = 'search-icon-container';
    iconContainer.appendChild(searchIcon);

    // Добавляем иконку в input-group
    const inputGroup = document.querySelector('#rs-search-input').parentNode;
    inputGroup.appendChild(iconContainer);

    // Создаем контейнер для результатов
    const resultsContainer = document.createElement('div');
    resultsContainer.id = 'search-results-container';
    resultsContainer.className = 'search-results-container';

    // Добавляем результаты прямо после input-group
    inputGroup.parentNode.insertBefore(resultsContainer, inputGroup.nextSibling);

    // Обработчик ввода с дебаунсом
    searchInput.addEventListener('input', handleSearchInput);

    // Обработчик клика вне области поиска
    document.addEventListener('click', (e) => {
        const inputGroupContainer = inputGroup.parentNode;
        if (!inputGroupContainer.contains(e.target)) {
            hideSearchResults();
        }
    });
}

// Обработчик ввода с дебаунсом
function handleSearchInput(e) {
    const query = e.target.value.trim();

    // Очищаем предыдущий таймер
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    // Если строка пустая, скрываем результаты
    if (!query) {
        hideSearchResults();
        return;
    }

    // Устанавливаем новый таймер
    searchTimeout = setTimeout(() => {
        performSearch(query);
    }, searchDebounceDelay);
}

// Выполнение поиска
async function performSearch(query) {
    try {
        const response = await fetch(`/api/rs/search?search_input=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error(`Ошибка поиска: ${response.status}`);

        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Ошибка поиска ресурсных серверов:', error);
        showSearchError('Ошибка выполнения поиска');
    }
}

// Отображение результатов поиска
function displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results-container');
    resultsContainer.innerHTML = '';

    if (Object.keys(results).length === 0) {
        resultsContainer.innerHTML = '<div class="search-no-results">Ничего не найдено</div>';
        resultsContainer.classList.add('show');
        return;
    }

    Object.entries(results).forEach(([rsId, rsData]) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.setAttribute('data-rs-id', rsId);
        resultItem.setAttribute('data-rs-name', escapeHtml(rsData.name));
        resultItem.innerHTML = `
            <div class="search-result-content">
                <strong class="search-result-name">${escapeHtml(rsData.name)}</strong>
                <div class="search-result-id">ID: ${rsId}</div>
            </div>
            <button class="btn btn-sm btn-outline-primary search-add-btn">
                Добавить
            </button>
        `;
        resultsContainer.appendChild(resultItem);

        // Добавляем обработчик клика на весь элемент
        resultItem.addEventListener('click', (e) => {
            // Не реагируем на клик по самой кнопке "Добавить"
            if (!e.target.closest('.search-add-btn')) {
                addResourceServerFromElement(resultItem);
            }
        });

        // Добавляем обработчик клика на кнопку "Добавить"
        const addBtn = resultItem.querySelector('.search-add-btn');
        addBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Останавливаем всплытие, чтобы не сработал клик по всему элементу
            addResourceServerFromElement(resultItem);
        });
    });

    resultsContainer.classList.add('show');
}

// Функция для добавления Resource Server из элемента результата
function addResourceServerFromElement(element) {
    const rsId = element.getAttribute('data-rs-id');
    const rsName = element.getAttribute('data-rs-name');

    if (selectedResourceServers.has(parseInt(rsId))) {
        // Показываем визуальную обратную связь, что элемент уже выбран
        element.style.backgroundColor = '#ffebee';
        setTimeout(() => {
            element.style.backgroundColor = '';
        }, 300);
        return;
    }

    addResourceServer(parseInt(rsId), rsName);
    hideSearchResults();
    document.getElementById('rs-search-input').value = '';

    // Визуальная обратная связь о добавлении
    element.style.backgroundColor = '#e8f5e8';
    setTimeout(() => {
        element.style.backgroundColor = '';
    }, 300);
}

// Показать ошибку поиска
function showSearchError(message) {
    const resultsContainer = document.getElementById('search-results-container');
    resultsContainer.innerHTML = `<div class="search-error">${message}</div>`;
    resultsContainer.classList.add('show');
}

// Скрыть результаты поиска
function hideSearchResults() {
    const resultsContainer = document.getElementById('search-results-container');
    resultsContainer.classList.remove('show');
}

// Экранирование HTML для безопасности
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadClientInfo() {
    try {
        const response = await fetch(`/api/client/${clientId}`);
        if (!response.ok) throw new Error(`Ошибка загрузки клиента: ${response.status}`);

        const clientData = await response.json();
        document.getElementById('client-name-display').textContent = clientData.name;
    } catch (error) {
        console.error('Ошибка загрузки информации о клиенте:', error);
        alert('Не удалось загрузить информацию о клиенте');
    }
}

async function loadRefData() {
    try {
        const response = await fetch(`/api/client/refs/${refId}`);
        if (!response.ok) throw new Error(`Ошибка загрузки референса: ${response.status}`);

        currentRefData = await response.json();

        // Заполняем форму данными
        document.getElementById('ref-name-input').value = currentRefData.name;

        // Устанавливаем выбранные scopes
        if (currentRefData.user_scopes.includes('email')) {
            document.getElementById('scope-email').checked = true;
        }
        if (currentRefData.user_scopes.includes('avatar_path')) {
            document.getElementById('scope-avatar').checked = true;
        }

        // Добавляем выбранные Resource Servers
        Object.entries(currentRefData.ref_resource_servers).forEach(([rsId, rsData]) => {
            addResourceServer(parseInt(rsId), rsData.name);
        });
    } catch (error) {
        console.error('Ошибка загрузки данных референса:', error);
        alert('Не удалось загрузить данные референса');
    }
}

function setupEventListeners() {
    // Кнопка возврата к клиенту
    document.getElementById('back-to-client-btn').addEventListener('click', () => {
        window.location.href = `/pages/client.html?clientId=${clientId}`;
    });

    // Кнопка отмены
    document.getElementById('cancel-btn').addEventListener('click', () => {
        window.location.href = `/pages/client.html?clientId=${clientId}`;
    });

    // Сохранение референса
    document.getElementById('save-ref-btn').addEventListener('click', saveRef);

    // Удаление референса (только в режиме редактирования)
    if (isEditMode) {
        document.getElementById('delete-ref-btn').addEventListener('click', deleteRef);
    }
}

// Функция для добавления Resource Server
window.addResourceServer = function(rsId, rsName) {
    if (selectedResourceServers.has(rsId)) {
        // Показываем уведомление, что уже выбран
        showTemporaryNotification('Этот ресурсный сервер уже выбран', 'warning');
        return;
    }

    selectedResourceServers.set(rsId, { id: rsId, name: rsName });
    renderSelectedResourceServers();

    // Показываем уведомление об успешном добавлении
    showTemporaryNotification(`Добавлен: ${rsName}`, 'success');
};

// Функция для показа временных уведомлений
function showTemporaryNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'} 
                             alert-dismissible fade show position-fixed`;
    notification.style.top = '80px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function removeResourceServer(rsId) {
    const removedName = selectedResourceServers.get(rsId)?.name;
    selectedResourceServers.delete(rsId);
    renderSelectedResourceServers();

    if (removedName) {
        showTemporaryNotification(`Удален: ${removedName}`, 'info');
    }
}

function renderSelectedResourceServers() {
    const selectedList = document.getElementById('selected-rs-list');

    if (selectedResourceServers.size === 0) {
        selectedList.innerHTML = '<div class="empty-selection">Выберите ресурсные серверы из результатов поиска</div>';
        selectedList.classList.add('empty');
    } else {
        selectedList.innerHTML = '';
        selectedList.classList.remove('empty');

        selectedResourceServers.forEach((rs, rsId) => {
            const rsItem = document.createElement('div');
            rsItem.className = 'selected-rs-item';
            rsItem.innerHTML = `
                <span class="rs-name">${rs.name}</span>
                <button class="remove-rs" onclick="removeResourceServer(${rsId})" title="Удалить">×</button>
            `;
            selectedList.appendChild(rsItem);
        });
    }
}

async function saveRef() {
    // Собираем данные формы
    const refName = document.getElementById('ref-name-input').value.trim();

    // Проверка обязательных полей
    if (!refName) {
        alert('Введите название референса');
        document.getElementById('ref-name-input').focus();
        return;
    }

    if (selectedResourceServers.size === 0) {
        alert('Выберите хотя бы один ресурсный сервер');
        return;
    }

    // Собираем выбранные scopes
    const userScopes = [];
    if (document.getElementById('scope-email').checked) {
        userScopes.push('email');
    }
    if (document.getElementById('scope-avatar').checked) {
        userScopes.push('avatar_path');
    }

    // Подготавливаем данные для отправки
    const requestData = {
        name: refName,
        user_scopes: userScopes,
        rs_ids: Array.from(selectedResourceServers.keys()).map(id => parseInt(id))
    };

    try {
        let response;
        let successMessage;

        if (isEditMode) {
            // Режим редактирования - PUT запрос
            response = await fetch(`/api/client/${clientId}/refs/${refId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            successMessage = 'Референс успешно обновлен!';
        } else {
            // Режим создания - POST запрос
            response = await fetch(`/api/client/${clientId}/refs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            successMessage = 'Референс успешно создан!';
        }

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка сохранения: ${response.status} - ${errorText}`);
        }

        if (!isEditMode) {
            // При создании получаем ID нового референса
            const result = await response.json();
            refId = result.ref_id;
        }

        alert(successMessage);

        // Возвращаемся к странице клиента
        window.location.href = `/pages/client.html?clientId=${clientId}`;

    } catch (error) {
        console.error('Ошибка сохранения референса:', error);
        alert(`Ошибка сохранения референса: ${error.message}`);
    }
}

async function deleteRef() {
    if (!confirm('Вы уверены, что хотите удалить этот референс?')) {
        return;
    }

    try {
        const response = await fetch(`/api/client/${clientId}/refs/${refId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`Ошибка удаления: ${response.status}`);
        }

        alert('Референс успешно удален!');

        // Возвращаемся к странице клиента
        window.location.href = `/pages/client.html?clientId=${clientId}`;

    } catch (error) {
        console.error('Ошибка удаления референса:', error);
        alert('Не удалось удалить референс');
    }
}
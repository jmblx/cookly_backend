let isCreateMode = false;
let initialClientData = null;
let clientId = null; // Делаем clientId глобальной переменной

// Вспомогательная функция для парсинга и вычисления expiry из presigned URL
function getPresignedExpiry(url) {
    try {
        const params = new URL(url).searchParams;
        const dateStr = params.get('X-Amz-Date');       // e.g. "20250609T181711Z"
        const expires = parseInt(params.get('X-Amz-Expires') || '0', 10);
        if (!dateStr || !expires) return null;

        // Разбираем дату
        const year  = +dateStr.slice(0, 4);
        const month = +dateStr.slice(4, 6) - 1;
        const day   = +dateStr.slice(6, 8);
        const hour  = +dateStr.slice(9, 11);
        const min   = +dateStr.slice(11, 13);
        const sec   = +dateStr.slice(13, 15);

        const dt = new Date(Date.UTC(year, month, day, hour, min, sec));
        dt.setSeconds(dt.getSeconds() + expires - 10); // вычитаем 10 секунд
        return dt;
    } catch {
        return null;
    }
}

async function fetchClientData(clientId) {
    const storageKey = `clientAvatar:${clientId}`;
    let loadAvatar = true;
    let cached = null;

    // Проверяем localStorage
    try {
        const raw = localStorage.getItem(storageKey);
        if (raw) {
            cached = JSON.parse(raw);
            const exp = new Date(cached.expires_at);
            if (exp > new Date()) {
                loadAvatar = false;
            }
        }
    } catch {
        // если парсинг упал — будем обновлять
        loadAvatar = true;
    }

    const url = `/api/client/${clientId}?load_avatar=true`;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Ошибка загрузки клиента: ${response.status}`);
        const data = await response.json();

        // Если сервер прислал avatar_url и мы действительно загрузили новую
        if (loadAvatar && data.avatar_url) {
            const expiresAt = getPresignedExpiry(data.avatar_url);
            if (expiresAt) {
                localStorage.setItem(storageKey, JSON.stringify({
                    avatar_url: data.avatar_url,
                    expires_at: expiresAt.toISOString()
                }));
            }
            data._cachedAvatar = data.avatar_url;
        } else if (cached && cached.avatar_url) {
            // используем кешированную ссылку
            data._cachedAvatar = cached.avatar_url;
        }

        return data;
    } catch (error) {
        console.error(error);
        alert("Не удалось загрузить данные клиента.");
        return null;
    }
}

// ===== Функции для работы с референсами =====

async function loadClientRefs() {
    try {
        if (!clientId) return;

        const response = await fetch(`/api/client/${clientId}`);
        if (!response.ok) throw new Error(`Ошибка загрузки клиента: ${response.status}`);

        const clientData = await response.json();

        // Проверяем, есть ли референсы
        if (clientData.refs_ids_data) {
            renderClientRefs(clientData.refs_ids_data);
        } else {
            document.getElementById('client-refs-list').innerHTML =
                '<div class="text-center text-muted p-3">Нет созданных референсов</div>';
        }
    } catch (error) {
        console.error('Ошибка загрузки референсов:', error);
        document.getElementById('client-refs-list').innerHTML =
            '<div class="text-center text-danger p-3">Ошибка загрузки референсов</div>';
    }
}

function renderClientRefs(refsData) {
    const refsList = document.getElementById('client-refs-list');
    refsList.innerHTML = '';

    if (!refsData || Object.keys(refsData).length === 0) {
        refsList.innerHTML =
            '<div class="text-center text-muted p-3">Нет созданных референсов</div>';
        return;
    }

    Object.entries(refsData).forEach(([refId, refData]) => {
        const listItem = document.createElement('a');
        listItem.href = `/pages/clientRef.html?clientId=${clientId}&refId=${refId}`;
        listItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        listItem.innerHTML = `
            <div>
                <strong>${refData.name}</strong>
                <div class="text-muted small">ID: ${refId}</div>
            </div>
            <span class="badge bg-primary rounded-pill">Редактировать</span>
        `;
        refsList.appendChild(listItem);
    });
}

// Добавляем кнопку создания референса
function setupRefsButton() {
    const addRefBtn = document.getElementById('add-ref-btn');
    if (addRefBtn) {
        addRefBtn.addEventListener('click', () => {
            if (clientId) {
                window.location.href = `/pages/clientRef.html?clientId=${clientId}`;
            }
        });
    }
}

function renderClientInfo(clientData) {
    document.getElementById("client-name").textContent = `Клиент: ${clientData.name}`;
    document.getElementById("client-name-input").value = clientData.name;
    document.getElementById("client-base-url-input").value = clientData.base_url;
    document.getElementById("client-type-select").value = clientData.type;

    // Список URL
    const urlList = document.getElementById("allowed-urls-list");
    urlList.innerHTML = "";
    clientData.allowed_redirect_urls.forEach(url => addUrlField(url, false));

    // Аватарка
    if (clientData._cachedAvatar) {
        document.getElementById("client-avatar").src = clientData._cachedAvatar;
    }

    // Отображаем референсы, если они есть
    if (clientData.refs_ids_data) {
        renderClientRefs(clientData.refs_ids_data);
    } else {
        // Если в данных клиента нет референсов, загружаем их отдельно
        loadClientRefs();
    }

    disableClientEditing();
}

document.addEventListener("DOMContentLoaded", async function () {
    const params = new URLSearchParams(window.location.search);
    clientId = params.get("clientId"); // Теперь clientId глобальная

    if (!clientId) {
        isCreateMode = true;
        document.body.classList.add('create-mode');
        document.getElementById("client-name").textContent = "Создание нового клиента";
        enableClientEditing();
        addUrlField("", true);

        // Скрываем секцию референсов при создании нового клиента
        document.getElementById('client-refs-section').style.display = 'none';
        return;
    }

    const clientData = await fetchClientData(clientId);
    if (clientData) {
        initialClientData = clientData;
        renderClientInfo(clientData);
    }

    // Настраиваем кнопку для референсов
    setupRefsButton();

    // Логика загрузки нового аватара
    const editAvatarIcon = document.getElementById("edit-avatar-icon");
    const avatarInput = document.getElementById("avatar-file-input");
    editAvatarIcon.addEventListener("click", () => avatarInput.click());

    avatarInput.addEventListener("change", async () => {
        const file = avatarInput.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`/api/client/${clientId}/avatar`, {
                method: "POST",
                body: formData
            });
            if (!response.ok) throw new Error("Ошибка загрузки аватарки");

            const result = await response.json();
            const avatarUrl = result.avatar_path;
            const expiresAt = getPresignedExpiry(avatarUrl);
            if (expiresAt) {
                localStorage.setItem(`clientAvatar:${clientId}`, JSON.stringify({
                    avatar_url: avatarUrl,
                    expires_at: expiresAt.toISOString()
                }));
            }
            document.getElementById("client-avatar").src = avatarUrl;
        } catch (e) {
            console.error(e);
            alert("Не удалось обновить аватарку");
        }
    });
});


function enableClientEditing() {
    document.getElementById("client-name-input").disabled = false;
    document.getElementById("client-base-url-input").disabled = false;
    document.getElementById("client-type-select").disabled = false;
    document.querySelector(".add-url-btn").classList.remove("hidden");
    document.getElementById("save-client-btn").classList.remove("hidden");
    document.getElementById("edit-icon").classList.add("hidden");

    const urlInputs = document.querySelectorAll("#allowed-urls-list input");
    urlInputs.forEach(input => input.disabled = false);
}

function addUrlField(url = "", editable = true) {
    const urlList = document.getElementById("allowed-urls-list");
    const li = document.createElement("li");
    li.innerHTML = `
        <input type="text" class="form-control" value="${url}" ${editable ? '' : 'disabled'}>
        <button onclick="removeUrlField(this)">Удалить</button>
    `;
    urlList.appendChild(li);

    if (!url) {
        const input = li.querySelector('input');
        input.disabled = false;
        input.focus();
    }
}

function removeUrlField(button) {
    const li = button.parentElement;
    li.remove();
}

async function saveClient() {
    const newName = document.getElementById("client-name-input").value;
    const newBaseUrl = document.getElementById("client-base-url-input").value;
    const newClientType = document.getElementById("client-type-select").value;

    const urlInputs = document.querySelectorAll("#allowed-urls-list input");
    const newAllowedUrls = Array.from(urlInputs).map(input => input.value.trim()).filter(url => url);

    const requestData = {
        name: newName,
        base_url: newBaseUrl,
        allowed_redirect_urls: newAllowedUrls,
        type: parseInt(newClientType, 10)
    };

    try {
        let response;

        if (isCreateMode || !clientId) {
            response = await fetch("/api/client", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const newClient = await response.json();
                window.history.replaceState({}, "", `?clientId=${newClient.client_id}`);
                clientId = newClient.client_id;
                isCreateMode = false;
                document.body.classList.remove('create-mode');
            }
        } else {
            response = await fetch(`/api/client/${clientId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData)
            });
        }

        if (!response.ok) {
            throw new Error(`Ошибка сохранения: статус ${response.status}`);
        }

        alert(isCreateMode ? "Клиент успешно создан!" : "Данные клиента успешно обновлены!");

        if (isCreateMode) {
            const newClient = await response.json();
            initialClientData = newClient;
            renderClientInfo(newClient);
            disableClientEditing();
        } else {
            disableClientEditing();
            const clientData = await fetchClientData(clientId);
            if (clientData) {
                renderClientInfo(clientData);
            }
        }
    } catch (error) {
        console.error(error);
        alert(`Ошибка ${isCreateMode ? 'создания' : 'обновления'} данных клиента: ${error.message}`);
    }
}

function disableClientEditing() {
    document.getElementById("client-name-input").disabled = true;
    document.getElementById("client-base-url-input").disabled = true;
    document.getElementById("client-type-select").disabled = true;
    document.querySelector(".add-url-btn").classList.add("hidden");
    document.getElementById("save-client-btn").classList.add("hidden");
    document.getElementById("edit-icon").classList.remove("hidden");

    const urlInputs = document.querySelectorAll("#allowed-urls-list input");
    urlInputs.forEach(input => input.disabled = true);
}
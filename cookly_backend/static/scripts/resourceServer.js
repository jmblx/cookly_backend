let currentRsId = null;
let availableScopes = {};
let currentRsType = null;
let rolesDisabled = false;
let initialRSData = null;
let initialRolesData = [];
let isCreateMode = false;

document.addEventListener("DOMContentLoaded", async function () {
    const params = new URLSearchParams(window.location.search);
    currentRsId = params.get("rsId");

    if (!currentRsId) {
        isCreateMode = true;
        document.body.classList.add('create-mode');
        document.getElementById("rs-name").textContent = "Создание нового ресурсного сервера";
        document.getElementById("save-rs-btn").classList.remove("hidden");
        document.getElementById("rs-name-input").disabled = false;
        document.getElementById("rs-type-select").disabled = false;
        return;
    }

    const rsData = await fetchRSData(currentRsId);

    if (rsData) {
        currentRsType = rsData.type;
        initialRSData = {
            name: rsData.name,
            type: rsData.type
        };
        initialRolesData = [...(rsData.roles || [])];

        renderRSInfo(rsData);
        renderRoles(rsData.roles || []);
        initAvailableScopes(rsData.roles || []);

        if (currentRsType === "RS_CONTROLLED") {
            disableRolesSection();
        }

        document.getElementById("rs-name-input").disabled = false;
        document.getElementById("rs-type-select").disabled = false;
    }
});

function disableRolesSection() {
    document.getElementById("add-role-btn").disabled = true;
    document.getElementById("add-role-btn").classList.add("disabled-section");

    document.querySelectorAll(".role-name").forEach(input => {
        input.disabled = true;
    });
    document.querySelectorAll(".is-base-checkbox").forEach(checkbox => {
        checkbox.disabled = true;
    });
    document.querySelectorAll(".scope-checkbox").forEach(checkbox => {
        checkbox.disabled = true;
    });

    rolesDisabled = true;
}

function enableRolesSection() {
    document.getElementById("add-role-btn").disabled = false;
    document.getElementById("add-role-btn").classList.remove("disabled-section");

    document.querySelectorAll(".role-name").forEach(input => {
        input.disabled = false;
    });
    document.querySelectorAll(".is-base-checkbox").forEach(checkbox => {
        checkbox.disabled = false;
    });
    document.querySelectorAll(".scope-checkbox").forEach(checkbox => {
        checkbox.disabled = false;
    });

    rolesDisabled = false;
}

function initAvailableScopes(roles) {
    availableScopes = {};
    roles.forEach(role => {
        role.base_scopes.forEach(scope => {
            const [scopeKey] = scope.split(":");
            availableScopes[scopeKey] = true;
        });
    });
}

async function fetchRSData(rsId) {
    try {
        const response = await fetch(`/api/rs/${rsId}`);
        if (!response.ok) throw new Error("Ошибка загрузки данных");
        return await response.json();
    } catch (error) {
        console.error(error);
        alert("Не удалось загрузить данные ресурсного сервера.");
        return null;
    }
}

function renderRSInfo(rsData) {
    document.getElementById("rs-name").textContent = `Ресурсный сервер: ${rsData.name}`;
    document.getElementById("rs-name-input").value = rsData.name;
    document.getElementById("rs-type-select").value = rsData.type;
}

function renderRoles(roles) {
    const container = document.getElementById("roles-container");

    let emptyMessage = document.getElementById("empty-roles-message");
    if (!emptyMessage) {
        emptyMessage = document.createElement('div');
        emptyMessage.id = "empty-roles-message";
        emptyMessage.className = "empty-roles-message col-12";
        emptyMessage.innerHTML = "Нет созданных ролей. Нажмите 'Добавить роль', чтобы создать первую.";
        container.appendChild(emptyMessage);
    }

    container.innerHTML = '';
    container.appendChild(emptyMessage);

    if (!roles || roles.length === 0) {
        emptyMessage.classList.remove('hidden');
        return;
    }

    emptyMessage.classList.add('hidden');

    // Создаем Bootstrap row с отступами
    const row = document.createElement('div');
    row.className = 'row g-3'; // g-3 добавляет горизонтальные и вертикальные отступы между колонками
    container.appendChild(row);

    roles.forEach((role, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4'; // адаптивно: по 2 карточки на md и по 3 карточки на lg

        const roleCard = document.createElement("div");
        roleCard.classList.add("role-card", "h-100");
        roleCard.id = `role-${role.id}`;

        function createScopeCheckbox(scopeKey, scopeValue, bitPosition, label) {
            return `
                <div class="form-check">
                    <input class="form-check-input scope-checkbox" type="checkbox"
                           data-scope-key="${scopeKey}" data-bit-pos="${bitPosition}"
                           ${scopeValue[bitPosition] === "1" ? "checked" : ""}
                           onchange="checkRoleChanges(${role.id})"
                           ${rolesDisabled ? "disabled" : ""}>
                    <label class="form-check-label">${label}</label>
                </div>`;
        }

        let scopeManagement = '';
        if (!rolesDisabled) {
            scopeManagement = `
                <div class="scope-management mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="addScopeToRole(${role.id})">
                        Добавить scope
                    </button>
                    <div id="new-scopes-${role.id}" class="mt-2"></div>
                </div>
            `;
        }

        let scopeCheckboxes = "";
        const scopeLabels = ["Создание", "Чтение", "Обновление", "Удаление"];

        role.base_scopes.forEach(scope => {
            const [scopeKey, scopeValue] = scope.split(":");
            if (!scopeKey || !scopeValue) return;

            scopeCheckboxes += `
                <div class="scope-item mb-3">
                    <div class="d-flex align-items-center mb-1">
                        <strong>${scopeKey}</strong>
                        ${!rolesDisabled ? `<button class="btn btn-sm btn-outline-danger ms-2" onclick="removeScope('${role.id}', '${scopeKey}')">×</button>` : ''}
                    </div>
            `;

            scopeLabels.forEach((label, idx) => {
                scopeCheckboxes += createScopeCheckbox(scopeKey, scopeValue, idx, label);
            });

            scopeCheckboxes += `</div>`;
        });

        roleCard.innerHTML = `
            <div class="role-header mb-3">
                <div class="role-name-container">
                    <input type="text" value="${role.name}" class="form-control role-name"
                           oninput="checkRoleChanges(${role.id})"
                           ${rolesDisabled ? "disabled" : ""}>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <input class="form-check-input is-base-checkbox" type="checkbox"
                           ${role.is_base ? "checked" : ""} ${rolesDisabled ? "disabled" : ""}
                           onchange="checkRoleChanges(${role.id})">
                    <label class="form-check-label">Базовая роль</label>
                </div>
            </div>
            <div class="scopes-container">
                ${scopeCheckboxes}
            </div>
            ${scopeManagement}
            <div class="action-buttons">
                <button class="btn btn-success btn-sm mt-2 hidden save-btn"
                        id="save-role-${role.id}"
                        onclick="saveRole(${index}, ${role.id})">Сохранить</button>
                <button class="btn btn-danger btn-sm mt-2" onclick="deleteRole(${role.id})">Удалить</button>
            </div>
        `;
        col.appendChild(roleCard);
        row.appendChild(col);
    });
}

function addScopeToRole(roleId) {
    const container = document.getElementById(`new-scopes-${roleId}`);
    const scopeId = Date.now();

    const scopeField = document.createElement("div");
    scopeField.className = "scope-field mb-3";
    scopeField.innerHTML = `
        <div class="d-flex align-items-center gap-2 mb-2">
            <input type="text" class="form-control scope-key" placeholder="Ключ scope">
            <select class="form-select scope-permissions">
                <option value="0000">Нет доступа</option>
                <option value="1000">Только создание</option>
                <option value="0100">Только чтение</option>
                <option value="0010">Только обновление</option>
                <option value="0001">Только удаление</option>
                <option value="1111">Полный доступ</option>
                <option value="1100">Создание и чтение</option>
                <option value="0110">Чтение и обновление</option>
                <option value="0011">Обновление и удаление</option>
            </select>
            <button class="btn btn-danger btn-sm" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
        <button class="btn btn-primary btn-sm" onclick="confirmAddScope(${roleId}, this.parentElement)">Добавить</button>
    `;
    container.appendChild(scopeField);
}

function confirmAddScope(roleId, scopeField) {
    const keyInput = scopeField.querySelector(".scope-key");
    const permissionsSelect = scopeField.querySelector(".scope-permissions");

    const key = keyInput.value.trim();
    const permissions = permissionsSelect.value;

    if (!key) {
        alert("Пожалуйста, укажите ключ scope");
        return;
    }

    const roleCard = document.getElementById(`role-${roleId}`);
    const existingScopes = roleCard.querySelectorAll(".scope-item strong");
    for (let i = 0; i < existingScopes.length; i++) {
        if (existingScopes[i].textContent === key) {
            alert("Scope с таким ключом уже существует");
            return;
        }
    }

    const scopesContainer = roleCard.querySelector(".scopes-container");

    const scopeLabels = ["Создание", "Чтение", "Обновление", "Удаление"];
    let checkboxes = '';
    for (let i = 0; i < 4; i++) {
        checkboxes += `
            <div class="form-check">
                <input class="form-check-input scope-checkbox" type="checkbox"
                       data-scope-key="${key}" data-bit-pos="${i}"
                       ${permissions[i] === "1" ? "checked" : ""}
                       onchange="checkRoleChanges(${roleId})">
                <label class="form-check-label">${scopeLabels[i]}</label>
            </div>
        `;
    }

    const scopeItem = document.createElement("div");
    scopeItem.className = "scope-item mb-3";
    scopeItem.innerHTML = `
        <div class="d-flex align-items-center mb-1">
            <strong>${key}</strong>
            <button class="btn btn-sm btn-outline-danger ms-2" onclick="removeScope('${roleId}', '${key}')">×</button>
        </div>
        ${checkboxes}
    `;

    scopesContainer.appendChild(scopeItem);
    scopeField.remove();

    document.getElementById(`save-role-${roleId}`).classList.remove("hidden");
}

function checkRoleChanges(roleId) {
    const roleCard = document.getElementById(`role-${roleId}`);
    if (!roleCard) return;

    const roleIndex = initialRolesData.findIndex(r => r.id === roleId);
    if (roleIndex === -1) return;

    const initialRole = initialRolesData[roleIndex];
    const currentName = roleCard.querySelector(".role-name").value;
    const currentIsBase = roleCard.querySelector(".is-base-checkbox").checked;

    const currentScopes = {};
    const scopeItems = roleCard.querySelectorAll(".scope-item");
    scopeItems.forEach(item => {
        const scopeKey = item.querySelector("strong").textContent;
        const checkboxes = item.querySelectorAll(".scope-checkbox");
        let bits = ['0', '0', '0', '0'];

        checkboxes.forEach((checkbox, idx) => {
            bits[idx] = checkbox.checked ? '1' : '0';
        });

        currentScopes[scopeKey] = bits.join('');
    });

    const hasNameChanged = currentName !== initialRole.name;
    const hasBaseChanged = currentIsBase !== initialRole.is_base;

    const initialScopes = {};
    initialRole.base_scopes.forEach(scope => {
        const [key, value] = scope.split(":");
        initialScopes[key] = value;
    });

    const hasScopesChanged =
        Object.keys(currentScopes).length !== Object.keys(initialScopes).length ||
        Object.keys(currentScopes).some(key => currentScopes[key] !== initialScopes[key]);

    document.getElementById(`save-role-${roleId}`).classList.toggle("hidden", !(hasNameChanged || hasBaseChanged || hasScopesChanged));
}

function removeScope(roleId, scopeKey) {
    if (!confirm(`Удалить scope ${scopeKey}?`)) return;

    const roleCard = document.getElementById(`role-${roleId}`);
    const scopes = roleCard.querySelectorAll(".scope-item");

    scopes.forEach(scope => {
        if (scope.querySelector("strong").textContent === scopeKey) {
            scope.remove();
            checkRoleChanges(roleId);
        }
    });
}

function checkRSChanges() {
    if (isCreateMode) return;

    const currentName = document.getElementById("rs-name-input").value;
    const currentType = document.getElementById("rs-type-select").value;

    const hasChanges = currentName !== initialRSData.name || currentType !== initialRSData.type;
    document.getElementById("save-rs-btn").classList.toggle("hidden", !hasChanges);
}

async function saveRS() {
    const newName = document.getElementById("rs-name-input").value;
    const newType = document.getElementById("rs-type-select").value;

    if (newType === "RS_CONTROLLED" && currentRsType !== "RS_CONTROLLED") {
        const confirmChange = confirm("При смене типа на 'Управляется ресурсным сервером' все роли станут неактивными (но не будут удалены). Вы не сможете добавлять или редактировать роли. Продолжить?");
        if (!confirmChange) {
            document.getElementById("rs-type-select").value = currentRsType || "RBAC_BY_AS";
            checkRSChanges();
            return;
        }
        disableRolesSection();
    }
    else if (newType === "RBAC_BY_AS" && currentRsType === "RS_CONTROLLED" && rolesDisabled) {
        enableRolesSection();
    }

    try {
        let response;
        const params = new URLSearchParams(window.location.search);
        let rsId = params.get("rsId");

        if (isCreateMode || !rsId) {
            response = await fetch("/api/rs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: newName,
                    type: newType
                })
            });

            if (response.ok) {
                const newRS = await response.json();
                window.history.replaceState({}, "", `?rsId=${newRS.rs_id}`);
                rsId = newRS.rs_id;
                currentRsId = rsId;
                isCreateMode = false;
                document.body.classList.remove('create-mode');
            }
        } else {
            response = await fetch(`/api/rs/${rsId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    new_name: newName,
                    new_type: newType
                })
            });
        }

        if (!response.ok) throw new Error(`Ошибка сохранения: статус ${response.status}`);

        alert(isCreateMode ? "Ресурсный сервер успешно создан!" : "Данные ресурсного сервера успешно обновлены!");

        if (isCreateMode) {
            const newRS = await response.json();
            currentRsType = newType;
            initialRSData = { name: newName, type: newType };

            const rsData = await fetchRSData(newRS.rs_id);
            if (rsData) {
                initialRolesData = [...(rsData.roles || [])];
                renderRSInfo(rsData);
                renderRoles(rsData.roles || []);
                initAvailableScopes(rsData.roles || []);

                if (currentRsType === "RS_CONTROLLED") {
                    disableRolesSection();
                }
            }

            document.getElementById("rs-name").textContent = `Ресурсный сервер: ${newName}`;
        } else {
            initialRSData = { name: newName, type: newType };
            currentRsType = newType;

            const rsData = await fetchRSData(rsId);
            if (rsData) {
                initialRolesData = [...(rsData.roles || [])];
                renderRoles(rsData.roles || []);

                if (currentRsType === "RS_CONTROLLED") {
                    disableRolesSection();
                }
            }
        }

        document.getElementById("save-rs-btn").classList.add("hidden");
    } catch (error) {
        console.error(error);
        alert(`Ошибка ${isCreateMode ? 'создания' : 'обновления'} ресурсного сервера: ${error.message}`);

        if (!isCreateMode) {
            document.getElementById("rs-type-select").value = currentRsType;
            checkRSChanges();

            if (rolesDisabled && newType === "RBAC_BY_AS") {
                enableRolesSection();
            }
        }
    }
}

async function saveRole(index, roleId) {
    const roleCard = document.getElementById(`role-${roleId}`);
    if (!roleCard) return;

    const newName = roleCard.querySelector(".role-name").value;
    const isBase = roleCard.querySelector(".is-base-checkbox").checked;

    const newBaseScopes = {};

    const scopeItems = roleCard.querySelectorAll(".scope-item");
    scopeItems.forEach(item => {
        const scopeKey = item.querySelector("strong").textContent;
        const checkboxes = item.querySelectorAll(".scope-checkbox");
        let bits = ['0', '0', '0', '0'];

        checkboxes.forEach((checkbox, idx) => {
            bits[idx] = checkbox.checked ? '1' : '0';
        });

        newBaseScopes[scopeKey] = bits.join('');
    });

    const requestData = {
        new_name: newName,
        new_is_base: isBase,
        new_base_scopes: newBaseScopes
    };

    try {
        const response = await fetch(`/api/role/${roleId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) throw new Error("Ошибка сохранения роли");

        alert("Роль успешно обновлена!");

        const roleIndex = initialRolesData.findIndex(r => r.id === roleId);
        if (roleIndex !== -1) {
            initialRolesData[roleIndex] = {
                ...initialRolesData[roleIndex],
                name: newName,
                is_base: isBase,
                base_scopes: Object.entries(newBaseScopes).map(([key, value]) => `${key}:${value}`)
            };
        }

        document.getElementById(`save-role-${roleId}`).classList.add("hidden");

        renderRoles(initialRolesData);
    } catch (error) {
        console.error(error);
        alert("Ошибка обновления роли!");
    }
}

async function deleteRole(roleId) {
    if (!confirm("Вы уверены, что хотите удалить эту роль?")) return;

    try {
        const response = await fetch(`/api/role/${roleId}`, {
            method: "DELETE"
        });

        if (!response.ok) throw new Error("Ошибка удаления роли");

        alert("Роль успешно удалена!");

        const roleIndex = initialRolesData.findIndex(r => r.id === roleId);
        if (roleIndex !== -1) {
            initialRolesData.splice(roleIndex, 1);
        }

        renderRoles(initialRolesData);

        const rsData = await fetchRSData(currentRsId);
        if (rsData) {
            initialRolesData = [...(rsData.roles || [])];
            renderRoles(rsData.roles || []);
        }
    } catch (error) {
        console.error(error);
        alert("Ошибка удаления роли!");
    }
}

function showNewRoleSection() {
    document.getElementById("new-role-section").classList.remove("hidden");
    document.getElementById("add-role-btn").classList.add("hidden");
    addNewScopeField();
}

function cancelNewRole() {
    document.getElementById("new-role-section").classList.add("hidden");
    document.getElementById("add-role-btn").classList.remove("hidden");
    document.getElementById("new-role-name").value = "";
    document.getElementById("new-role-is-base").checked = false;
    document.getElementById("new-role-scopes").innerHTML = "";
}

function addNewScopeField() {
    const scopesContainer = document.getElementById("new-role-scopes");
    const scopeId = Date.now();

    const scopeField = document.createElement("div");
    scopeField.classList.add("scope-field", "mb-3");
    scopeField.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <input type="text" class="form-control scope-key" placeholder="Ключ scope (например, user_profile)">
            <select class="form-select scope-permissions">
                <option value="0000">Нет доступа</option>
                <option value="1000">Только создание</option>
                <option value="0100">Только чтение</option>
                <option value="0010">Только обновление</option>
                <option value="0001">Только удаление</option>
                <option value="1111">Полный доступ</option>
                <option value="1100">Создание и чтение</option>
                <option value="0110">Чтение и обновление</option>
                <option value="0011">Обновление и удаление</option>
            </select>
            <button class="btn btn-danger btn-sm" onclick="removeScopeField(this)">×</button>
        </div>
    `;
    scopesContainer.appendChild(scopeField);
}

function removeScopeField(button) {
    button.closest(".scope-field").remove();
}

async function confirmNewRole() {
    const name = document.getElementById("new-role-name").value.trim();
    const isBase = document.getElementById("new-role-is-base").checked;

    if (!name) {
        alert("Пожалуйста, укажите название роли");
        return;
    }

    const baseScopes = {};
    const scopeFields = document.querySelectorAll(".scope-field");

    scopeFields.forEach(field => {
        const keyInput = field.querySelector(".scope-key");
        const permissionsSelect = field.querySelector(".scope-permissions");

        const key = keyInput.value.trim();
        const permissions = permissionsSelect.value;

        if (key) {
            baseScopes[key] = permissions;
        }
    });

    if (Object.keys(baseScopes).length === 0) {
        alert("Пожалуйста, добавьте хотя бы один scope");
        return;
    }

    const requestData = {
        name: name,
        base_scopes: baseScopes,
        rs_id: parseInt(currentRsId),
        is_base: isBase
    };

    try {
        const response = await fetch("/api/role", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) throw new Error("Ошибка создания роли");

        const newRole = await response.json();
        alert("Роль успешно создана!");

        const rsData = await fetchRSData(currentRsId);
        if (rsData) {
            initialRolesData = [...(rsData.roles || [])];
            renderRoles(rsData.roles || []);
        }

        cancelNewRole();
    } catch (error) {
        console.error(error);
        alert("Ошибка создания роли: " + error.message);
    }
}
export async function setupPagination({
    containerId,
    fetchUrl,
    renderFn,
    pageSize = 15,
    itemLinkBase = '',
    queryParam = 'id'
}) {
    let afterIdStack = [];
    let currentAfterId = 0;
    let lastLoadedId = null;

    const container = document.getElementById(containerId);
    const paginationContainer = document.createElement("div");
    paginationContainer.className = "pagination-controls text-center mt-4";
    paginationContainer.innerHTML = `
        <button class="btn btn-secondary me-2" id="prev-page">Назад</button>
        <button class="btn btn-secondary" id="next-page">Вперёд</button>
    `;
    container.after(paginationContainer);

    const prevButton = paginationContainer.querySelector("#prev-page");
    const nextButton = paginationContainer.querySelector("#next-page");

    async function loadPage() {
        try {
            const response = await fetch(`${fetchUrl}?after_id=${currentAfterId}&page_size=${pageSize}`);
            if (!response.ok) throw new Error("Ошибка загрузки данных");
            const data = await response.json();

            renderFn(data, container, itemLinkBase, queryParam);

            const ids = Object.keys(data).map(Number);
            lastLoadedId = ids.length > 0 ? Math.max(...ids) : null;

            nextButton.disabled = !lastLoadedId;
            prevButton.disabled = afterIdStack.length === 0;
        } catch (e) {
            console.error(e);
            alert("Не удалось загрузить данные.");
        }
    }

    nextButton.onclick = async () => {
        if (lastLoadedId !== null) {
            afterIdStack.push(currentAfterId);
            currentAfterId = lastLoadedId;
            await loadPage();
        }
    };

    prevButton.onclick = async () => {
        if (afterIdStack.length > 0) {
            currentAfterId = afterIdStack.pop();
            await loadPage();
        }
    };

    await loadPage();
}

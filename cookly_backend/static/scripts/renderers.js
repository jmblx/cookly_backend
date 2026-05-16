export function renderCards(data, container, linkBase, param) {
    container.innerHTML = "";

    Object.entries(data).forEach(([id, { name }]) => {
        const card = document.createElement("div");
        card.classList.add("col-md-3", "card-item");
        card.textContent = name;
        card.onclick = () => window.location.href = `${linkBase}?${param}=${id}`;
        container.appendChild(card);
    });
}

export function initSearchPanel({ apiUrl, resultPageUrl, idNaming }) {
    const container = document.createElement('div');
    container.style.position = 'relative';
    container.style.marginTop = '60px';
    container.style.zIndex = 999;

    const inputWrapper = document.createElement('div');
    inputWrapper.style.position = 'relative';
    inputWrapper.style.maxWidth = '500px';
    inputWrapper.style.margin = '10px auto';

    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Поиск...';
    input.className = 'form-control';
    input.style.paddingRight = '40px';

    const icon = document.createElement('img');
    icon.src = '/icons/lupa.png';
    icon.alt = 'Поиск';
    icon.style.position = 'absolute';
    icon.style.top = '50%';
    icon.style.right = '10px';
    icon.style.transform = 'translateY(-50%)';
    icon.style.width = '20px';
    icon.style.height = '20px';
    icon.style.pointerEvents = 'none';
    icon.style.opacity = '0.6';

    inputWrapper.appendChild(input);
    inputWrapper.appendChild(icon);

    const resultsBox = document.createElement('div');
    resultsBox.style.position = 'absolute';
    resultsBox.style.top = '100%';
    resultsBox.style.left = '50%';
    resultsBox.style.transform = 'translateX(-50%)';
    resultsBox.style.backgroundColor = 'white';
    resultsBox.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
    resultsBox.style.borderRadius = '4px';
    resultsBox.style.maxHeight = '300px';
    resultsBox.style.overflowY = 'auto';
    resultsBox.style.width = '100%';
    resultsBox.style.maxWidth = '500px';
    resultsBox.style.zIndex = 1001;
    resultsBox.style.display = 'none';

    container.appendChild(inputWrapper);
    container.appendChild(resultsBox);
    document.body.insertBefore(container, document.body.firstChild.nextSibling); // сразу под админ-панелью

    let timeout = null;

    input.addEventListener('input', () => {
        if (timeout) clearTimeout(timeout);
        const query = input.value.trim();
        if (!query) {
            resultsBox.innerHTML = '';
            resultsBox.style.display = 'none';
            return;
        }
        timeout = setTimeout(() => {
            fetch(`${apiUrl}?search_input=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    resultsBox.innerHTML = '';
                    const keys = Object.keys(data);
                    if (keys.length === 0) {
                        resultsBox.style.display = 'none';
                        return;
                    }
                    keys.forEach(id => {
                        const item = document.createElement('div');
                        item.textContent = data[id].name;
                        item.style.padding = '10px';
                        item.style.cursor = 'pointer';
                        item.style.borderBottom = '1px solid #ccc';
                        item.addEventListener('click', () => {
                            window.location.href = `${resultPageUrl}?${idNaming}=${id}`;
                        });
                        resultsBox.appendChild(item);
                    });
                    resultsBox.style.display = 'block';
                })
                .catch(err => {
                    console.error('Ошибка поиска:', err);
                    resultsBox.style.display = 'none';
                });
        }, 1000);
    });

    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            resultsBox.style.display = 'none';
        }
    });
}

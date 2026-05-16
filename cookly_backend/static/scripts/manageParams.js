function saveInitialQueryParams() {
    const urlParams = new URLSearchParams(window.location.search);
    if (!sessionStorage.getItem('initialParams')) {
        const params = {};
        for (const [key, value] of urlParams.entries()) {
            params[key] = value;
        }
        sessionStorage.setItem('initialParams', JSON.stringify(params));
    }
}

function getStoredParams() {
    const data = sessionStorage.getItem('initialParams');
    return data ? JSON.parse(data) : {};
}

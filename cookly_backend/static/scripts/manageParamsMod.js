export function saveInitialQueryParams() {
    if ( getStoredParams().ref_id !== undefined ) {
        return
    }
        const urlParams = new URLSearchParams(window.location.search);
    const params = {};
    for (const [key, value] of urlParams.entries()) {
        params[key] = value;
    }
    sessionStorage.setItem('initialParams', JSON.stringify(params));
}

export function getStoredParams() {
    const data = sessionStorage.getItem('initialParams');
    return data ? JSON.parse(data) : {};
}

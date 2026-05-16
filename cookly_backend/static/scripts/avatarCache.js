import { fetchWithAuth } from './commonApi.js';

function getPresignedExpiry(url) {
    try {
        const params = new URL(url).searchParams;
        const dateStr = params.get('X-Amz-Date');
        const expires = parseInt(params.get('X-Amz-Expires') || '0', 10);
        if (!dateStr || !expires) return null;

        const [y, mo, d, , hh, mm, ss] = [
            dateStr.slice(0,4),
            dateStr.slice(4,6),
            dateStr.slice(6,8),
            dateStr[8],
            dateStr.slice(9,11),
            dateStr.slice(11,13),
            dateStr.slice(13,15),
        ];
        const dt = new Date(Date.UTC(+y, +mo-1, +d, +hh, +mm, +ss));
        dt.setSeconds(dt.getSeconds() + expires - 10);
        return dt;
    } catch {
        return null;
    }
}

/**
 * Загружает presigned URL аватарки клиента clientId и устанавливает его в <img id=imgId>.
 * Кэширует в localStorage под ключом `clientAvatar:${clientId}` с { avatar_url, expires_at }.
 * Если в хранилище есть живая ссылка — возвращает её без запросов.
 */
export async function loadClientAvatar(clientId, imgId) {
    const storageKey = `clientAvatar:${clientId}`;
    let needFetch = true;
    let cached = null;

    // проверяем кеш
    try {
        const raw = localStorage.getItem(storageKey);
        if (raw) {
            cached = JSON.parse(raw);
            const exp = new Date(cached.expires_at);
            if (exp > new Date()) {
                needFetch = false;
                document.getElementById(imgId).src = cached.avatar_url;
            }
        }
    } catch {
        needFetch = true;
    }

    if (!needFetch) return;

    // запрашиваем новую ссылку
    try {
        const url = `/api/client/${clientId}?load_avatar=true`;
        const res = await fetchWithAuth(url);
        if (!res.ok) throw new Error(res.statusText);
        const data = await res.json();
        const avatarUrl = data.avatar_url;
        const expiry = getPresignedExpiry(avatarUrl);
        if (avatarUrl && expiry) {
            localStorage.setItem(storageKey, JSON.stringify({
                avatar_url: avatarUrl,
                expires_at: expiry.toISOString()
            }));
            document.getElementById(imgId).src = avatarUrl;
        }
    } catch (e) {
        console.error('Error loading client avatar:', e);
    }
}

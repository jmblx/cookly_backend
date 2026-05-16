import { getStoredParams } from './manageParamsMod.js';

const fingerprint = localStorage.getItem('deviceFingerprint') || '';

export async function fetchWithAuth(url, options = {}) {
    const defaults = {
        credentials: 'include',
        headers: {
            'X-Device-Fingerprint': fingerprint,
        }
    };

    if (!(options.body instanceof FormData)) {
        defaults.headers['Content-Type'] = 'application/json';
    }

    const mergedOptions = {
        ...defaults,
        ...options,
        headers: {
            ...defaults.headers,
            ...options.headers,
        }
    };

    let response = await fetch(url, mergedOptions);

    if (response.status === 401) {
        const refreshResponse = await fetch("/api/auth-service/refresh", {
            credentials: 'include',
            headers: {
                'X-Device-Fingerprint': fingerprint,
            }
        });

        if (refreshResponse.ok) {
            response = await fetch(url, mergedOptions);
        } else {
            redirectToLogin();
            throw new Error('Unauthorized - refresh failed');
        }
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || error.detail || 'Request failed');
    }

    return response;
}


window._userDataPromise = null;
window._userData = null;

export async function loadUserData(emailElementId = 'user-email') {
  if (!window._userDataPromise) {
    window._userDataPromise = fetchWithAuth('/api/me')
      .then(res => res.json())
      .then(data => {
        // Сохраняем и сам объект
        window._userData = data;
        return data;
      })
      .catch(err => {
        window._userDataPromise = null;
        throw err;
      });
  }

  const userData = await window._userDataPromise;

  if (emailElementId) {
    const el = document.getElementById(emailElementId);
    if (el) el.textContent = userData.email;
  }

  return userData;
}

export async function uploadUserAvatar() {
  const fileInput = document.getElementById('avatar-upload');
  if (!fileInput?.files?.length) return false;

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  const res = await fetchWithAuth('/api/avatar', {
    method: 'POST',
    body: formData,
  });

  // Предполагаем, что сервер вернул JSON с полем avatar_update_timestamp
  const { avatar_update_timestamp } = await res.json();

  // Обновляем и в кэше userData
  if (window._userData) {
    window._userData.avatar_update_timestamp = avatar_update_timestamp;
  }
  // Если кто-то в будущем вызывает loadUserData() — он возьмёт из _userDataPromise,
  // но для аватара мы уже обновили объект.

  // И тут же перезагрузим картинку
  await loadUserAvatar();
  return true;
}

export async function loadUserAvatar(avatarElementId = 'user-avatar') {
  const avatarBase = '/user-avatars/jwt/';
  // Гарантируем, что данные загружены
  if (!window._userDataPromise) {
    await loadUserData();
  }
  // Ждём, пока промис отработает и наполнятся window._userData
  await window._userDataPromise;

  // Берём таймстамп из объекта
  const ts = window._userData?.avatar_update_timestamp;
  // Если вдруг нет — на всякий случай fallback на текущее время
  const url = ts ? `${avatarBase}?t=${ts}` : `${avatarBase}?t=${Math.floor(Date.now() / 1000)}`;

  try {
    const response = await fetchWithAuth(url);
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);

    const img = document.getElementById(avatarElementId);
    if (img) img.src = imageUrl;
    return imageUrl;
  } catch (err) {
    console.error('Error loading avatar:', err);
    const img = document.getElementById(avatarElementId);
    if (img) img.src = '/icons/defaultAvatar.svg';
    return '/icons/defaultAvatar.svg';
  }
}

export function redirectToLogin() {
    const params = getStoredParams();
    const loginUrl = new URL('/pages/login.html', window.location.origin);

    Object.entries(params).forEach(([key, value]) => {
        loginUrl.searchParams.append(key, value);
    });

    window.location.href = loginUrl.toString();
}

export async function logoutClient() {
    try {
        const response = await fetch("/api/auth-service/revoke", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (response.ok) {
            redirectToLogin();
        } else {
            const data = await response.json();
            alert(data.detail || "Logout failed");
        }
    } catch (error) {
        console.error("Logout error:", error);
        alert("Network error during logout");
    }
}


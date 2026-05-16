export async function generateFingerprint() {
    const navigatorData = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    };

    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(JSON.stringify(navigatorData));
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));

    return hashArray.map(byte => byte.toString(16).padStart(2, '0')).join('');
}

export async function getOrCreateFingerprint() {
    let fingerprint = localStorage.getItem('deviceFingerprint');
    if (!fingerprint) {
        fingerprint = await generateFingerprint();
        localStorage.setItem('deviceFingerprint', fingerprint);
    }
    return fingerprint;
}
import {getOrCreateFingerprint} from "./fingerprint.js";

export function initRegisterConfirm(handleSuccess) {
    const modalEl = document.getElementById('confirmEmailModal');
    const modal = new bootstrap.Modal(modalEl);

    let email = '';

    document.getElementById('confirmCodeBtn')
        .addEventListener('click', handleConfirm);

    document.getElementById('cancelConfirmBtn')
        .addEventListener('click', resetModal);

    document.querySelectorAll('.code-input').forEach((input, index) => {
        input.addEventListener('input', () => {
            if (input.value.length === 1 && index < 5) {
                input.nextElementSibling.focus();
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !input.value && index > 0) {
                input.previousElementSibling.focus();
            }
        });
    });

    function openConfirmModal(userEmail) {
        email = userEmail;
        modal.show();
    }

    async function handleConfirm() {
        try {
            const code = Array.from(document.querySelectorAll('.code-input'))
                .map(i => i.value)
                .join('');

            if (code.length !== 6) {
                throw new Error('Введите 6-значный код');
            }

            const fingerprint = await getOrCreateFingerprint();
            const resp = await fetch('/api/complete-register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Device-Fingerprint': fingerprint,
                },
                body: JSON.stringify({
                    email,
                    confirmation_token: code
                })
            });

            if (!resp.ok) {
                const err = await resp.json();
                if (resp.status === 403 || resp.status === 400 || resp.status === 401) {
                    throw new Error('Неверный код')
                }
                else {
                    throw new Error(err.detail || 'Ошибка подтверждения');
                }
            }

            modal.hide();
            resetModal();
            handleSuccess();

        } catch (e) {
            alert(e.message);
        }
    }

    function resetModal() {
        document.querySelectorAll('.code-input').forEach(i => i.value = '');
    }

    return { openConfirmModal };
}

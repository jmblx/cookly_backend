export function initPasswordReset() {
    const modal = new bootstrap.Modal(document.getElementById('forgotPasswordModal'));
    let currentStep = 1;
    let resetToken = null;
    let resetEmail = '';

    // Инициализация обработчиков
    document.getElementById('nextStepBtn').addEventListener('click', handleNextStep);
    document.getElementById('completeResetBtn').addEventListener('click', handleCompleteReset);
    document.getElementById('cancelResetBtn').addEventListener('click', resetModal);

    // Обработка ввода кода
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

    async function handleNextStep() {
        try {
            if (currentStep === 1) {
                resetEmail = document.getElementById('resetEmail').value;
                if (!resetEmail) throw new Error('Введите email');

                await fetch('/user/password/reset/request-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: resetEmail })
                });

                goToStep(2);
            }
            else if (currentStep === 2) {
                const code = Array.from(document.querySelectorAll('.code-input'))
                    .map(i => i.value).join('');

                if (code.length !== 6) throw new Error('Введите 6-значный код');

                const response = await fetch('/user/password/reset/verify-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: resetEmail, code })
                });

                const data = await response.json();
                resetToken = data.reset_token;
                goToStep(3);
            }
        } catch (error) {
            alert(error.message);
        }
    }

    async function handleCompleteReset() {
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (!newPassword || newPassword !== confirmPassword) {
            alert('Пароли не совпадают или не заполнены');
            return;
        }

        try {
            await fetch('/user/password/reset/confirm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reset_token: resetToken,
                    new_pwd: newPassword
                })
            });

            alert('Пароль успешно изменен');
            resetModal();
            modal.hide();
        } catch (error) {
            alert('Ошибка при изменении пароля');
        }
    }

    function goToStep(step) {
        currentStep = step;
        document.getElementById('resetProgress').style.width = `${step * 33}%`;
        document.querySelectorAll('.step').forEach((el, i) =>
            el.classList.toggle('active', i === step - 1));

        document.getElementById('nextStepBtn').style.display = step < 3 ? 'block' : 'none';
        document.getElementById('completeResetBtn').style.display = step === 3 ? 'block' : 'none';
    }

    function resetModal() {
        currentStep = 1;
        resetToken = null;
        document.getElementById('resetEmail').value = '';
        document.querySelectorAll('.code-input').forEach(i => i.value = '');
        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';
        goToStep(1);
    }
}
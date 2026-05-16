import {
    setupReturnButton,
    openAvatarUpload
} from './profileCommon.js';
import {loadUserData, loadUserAvatar, logoutClient, uploadUserAvatar} from "./commonApi.js";

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const userData = await loadUserData('user-email');

        await loadUserAvatar('user-avatar');

        setupReturnButton();

        document.getElementById('user-avatar')?.addEventListener('click', openAvatarUpload);
        document.querySelector('.edit-icon')?.addEventListener('click', openAvatarUpload);
        document.getElementById('avatar-upload')?.addEventListener('change', async () => {
            try {
                await uploadUserAvatar();
                alert('Avatar updated successfully!');
                await loadUserAvatar('user-avatar');
                await loadUserAvatar('user-panel-avatar');
            } catch {
                alert('Failed to upload avatar');
            }
        });
    } catch (error) {
        console.error('Admin profile initialization error:', error);
    }
});

document.getElementById("logout-button")?.addEventListener("click", logoutClient);
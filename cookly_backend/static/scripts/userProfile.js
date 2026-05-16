import {
    setupReturnButton,
    openAvatarUpload
} from './profileCommon.js';
import {loadUserData, loadUserAvatar, logoutClient, uploadUserAvatar} from "./commonApi.js";

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await Promise.all([
            loadUserData('user-email'),
            loadUserAvatar('user-avatar')
        ]);

        setupReturnButton();

        document.getElementById('user-avatar')?.addEventListener('click', openAvatarUpload);
        document.querySelector('.edit-icon')?.addEventListener('click', openAvatarUpload);
        document.getElementById('avatar-upload')?.addEventListener('change', async () => {
            try {
                await uploadUserAvatar();
                alert('Avatar updated successfully!');
                await loadUserAvatar('user-avatar');
            } catch {
                alert('Failed to upload avatar');
            }
        });
    } catch (error) {
        console.error('Profile initialization error:', error);
    }
});

document.getElementById("logout-button")?.addEventListener("click", logoutClient);
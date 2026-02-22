document.addEventListener('DOMContentLoaded', function () {
    var token = localStorage.getItem('bol_token');
    var userStr = localStorage.getItem('bol_user');
    var user = null;

    if (userStr) {
        try {
            user = JSON.parse(userStr);
        } catch (e) {
            user = null;
        }
    }

    var desktopLoginBtn = document.querySelector('.login-btn-desktop');
    var mobileLoginBtn = document.querySelector('.login-btn-mobile');
    var mobileAuthSection = document.querySelector('.mobile-auth-section');
    var blogNavLoginBtn = document.querySelector('.header .nav-links a[href="/login"]');

    if (token && user && user.name) {
        var firstName = user.name.split(' ')[0];

        if (desktopLoginBtn) {
            desktopLoginBtn.textContent = firstName;
            desktopLoginBtn.href = '#';
            desktopLoginBtn.classList.add('logged-in-user-btn');
            desktopLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                openLogoutModal(user.name);
            });
        }

        if (mobileLoginBtn && mobileAuthSection) {
            mobileAuthSection.innerHTML = '';
            var mobileUserBtn = document.createElement('a');
            mobileUserBtn.href = '#';
            mobileUserBtn.className = 'login-btn-mobile';
            mobileUserBtn.innerHTML = '<span class="login-btn-inner"><i class="ph ph-user" style="font-size:1.125rem"></i><span>' + firstName + '</span></span>';
            mobileUserBtn.addEventListener('click', function (e) {
                e.preventDefault();
                openLogoutModal(user.name);
            });
            mobileAuthSection.appendChild(mobileUserBtn);
        }

        if (blogNavLoginBtn) {
            blogNavLoginBtn.textContent = firstName;
            blogNavLoginBtn.href = '#';
            blogNavLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                openLogoutModal(user.name);
            });
        }
    }

    function createLogoutModal() {
        var existing = document.getElementById('logout-modal-overlay');
        if (existing) return existing;

        var overlay = document.createElement('div');
        overlay.id = 'logout-modal-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:none;justify-content:center;align-items:center;z-index:10000;padding:1rem;backdrop-filter:blur(4px);';

        var modal = document.createElement('div');
        modal.style.cssText = 'background:#fff;border-radius:16px;padding:2rem;max-width:380px;width:100%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.2);animation:logoutModalIn 0.25s ease;';

        var style = document.createElement('style');
        style.textContent = '@keyframes logoutModalIn{from{opacity:0;transform:scale(0.95) translateY(-10px)}to{opacity:1;transform:scale(1) translateY(0)}}';
        document.head.appendChild(style);

        var icon = document.createElement('div');
        icon.style.cssText = 'width:56px;height:56px;border-radius:50%;background:#f0f0ff;display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;';
        icon.innerHTML = '<i class="ph ph-sign-out" style="font-size:1.5rem;color:#3533CD"></i>';

        var heading = document.createElement('h3');
        heading.id = 'logout-modal-heading';
        heading.style.cssText = "font-family:'Plus Jakarta Sans',sans-serif;font-size:1.125rem;font-weight:700;color:#0D0D0D;margin-bottom:0.5rem;";
        heading.textContent = 'Log out?';

        var desc = document.createElement('p');
        desc.id = 'logout-modal-desc';
        desc.style.cssText = "font-family:'Plus Jakarta Sans',sans-serif;font-size:0.875rem;color:#777;margin-bottom:1.5rem;line-height:1.5;";
        desc.textContent = 'Are you sure you want to log out?';

        var btnWrap = document.createElement('div');
        btnWrap.style.cssText = 'display:flex;gap:0.75rem;justify-content:center;';

        var cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = "font-family:'Plus Jakarta Sans',sans-serif;padding:0.625rem 1.5rem;border-radius:10px;border:1.5px solid #e0ddd8;background:#fff;color:#0D0D0D;font-weight:600;font-size:0.875rem;cursor:pointer;transition:all 0.2s;";
        cancelBtn.addEventListener('mouseenter', function () { cancelBtn.style.borderColor = '#3533CD'; });
        cancelBtn.addEventListener('mouseleave', function () { cancelBtn.style.borderColor = '#e0ddd8'; });
        cancelBtn.addEventListener('click', function () { closeLogoutModal(); });

        var logoutBtn = document.createElement('button');
        logoutBtn.textContent = 'Log out';
        logoutBtn.style.cssText = "font-family:'Plus Jakarta Sans',sans-serif;padding:0.625rem 1.5rem;border-radius:10px;border:none;background:#0D0D0D;color:#fff;font-weight:600;font-size:0.875rem;cursor:pointer;transition:all 0.2s;";
        logoutBtn.addEventListener('mouseenter', function () { logoutBtn.style.background = '#333'; });
        logoutBtn.addEventListener('mouseleave', function () { logoutBtn.style.background = '#0D0D0D'; });
        logoutBtn.addEventListener('click', function () {
            localStorage.removeItem('bol_token');
            localStorage.removeItem('bol_user');
            window.location.reload();
        });

        btnWrap.appendChild(cancelBtn);
        btnWrap.appendChild(logoutBtn);
        modal.appendChild(icon);
        modal.appendChild(heading);
        modal.appendChild(desc);
        modal.appendChild(btnWrap);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) closeLogoutModal();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeLogoutModal();
        });

        return overlay;
    }

    function openLogoutModal(fullName) {
        var overlay = createLogoutModal();
        var heading = document.getElementById('logout-modal-heading');
        var desc = document.getElementById('logout-modal-desc');
        if (heading) heading.textContent = 'Hey, ' + fullName.split(' ')[0] + '!';
        if (desc) desc.textContent = 'Are you sure you want to log out of your account?';
        overlay.style.display = 'flex';
    }

    function closeLogoutModal() {
        var overlay = document.getElementById('logout-modal-overlay');
        if (overlay) overlay.style.display = 'none';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var token = localStorage.getItem('bol_token');
    if (token) {
        window.location.href = '/';
        return;
    }

    var tabs = document.querySelectorAll('.auth-tab');
    var forms = document.querySelectorAll('.auth-form');
    var switchLinks = document.querySelectorAll('.auth-switch-link');
    var passwordToggles = document.querySelectorAll('.password-toggle');

    function switchTab(tabName) {
        tabs.forEach(function (t) {
            t.classList.toggle('active', t.dataset.tab === tabName);
        });
        forms.forEach(function (f) {
            f.classList.toggle('active', f.id === tabName + '-form');
        });
        document.querySelectorAll('.auth-message').forEach(function (m) {
            m.className = 'auth-message';
            m.textContent = '';
        });
        document.querySelectorAll('.form-field').forEach(function (f) {
            f.classList.remove('error');
        });
    }

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            switchTab(tab.dataset.tab);
        });
    });

    switchLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            switchTab(link.dataset.switch);
        });
    });

    passwordToggles.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.dataset.target;
            var input = document.getElementById(targetId);
            if (!input) return;
            var icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'ph ph-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'ph ph-eye';
            }
        });
    });

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showMessage(elementId, text, type) {
        var el = document.getElementById(elementId);
        if (!el) return;
        el.className = 'auth-message ' + type;
        el.textContent = text;
    }

    function clearMessage(elementId) {
        var el = document.getElementById(elementId);
        if (!el) return;
        el.className = 'auth-message';
        el.textContent = '';
    }

    function setFieldError(inputEl, show) {
        var field = inputEl.closest('.form-field');
        if (!field) return;
        if (show) {
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    }

    var loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            clearMessage('login-message');

            var emailInput = document.getElementById('login-email');
            var passwordInput = document.getElementById('login-password');
            var email = emailInput.value.trim();
            var password = passwordInput.value;
            var valid = true;

            if (!email || !validateEmail(email)) {
                setFieldError(emailInput, true);
                valid = false;
            } else {
                setFieldError(emailInput, false);
            }

            if (!password) {
                setFieldError(passwordInput, true);
                valid = false;
            } else {
                setFieldError(passwordInput, false);
            }

            if (!valid) return;

            var btn = document.getElementById('login-submit-btn');
            btn.disabled = true;
            btn.classList.add('loading');

            try {
                var res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, password: password })
                });

                var data = await res.json();

                if (!res.ok) {
                    showMessage('login-message', data.detail || 'Login failed. Please try again.', 'error');
                    btn.disabled = false;
                    btn.classList.remove('loading');
                    return;
                }

                localStorage.setItem('bol_token', data.token);
                localStorage.setItem('bol_user', JSON.stringify(data.user));

                showMessage('login-message', 'Login successful! Redirecting...', 'success');
                setTimeout(function () {
                    window.location.href = '/';
                }, 800);
            } catch (err) {
                showMessage('login-message', 'Network error. Please try again.', 'error');
                btn.disabled = false;
                btn.classList.remove('loading');
            }
        });
    }

    var registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            clearMessage('register-message');

            var nameInput = document.getElementById('register-name');
            var emailInput = document.getElementById('register-email');
            var passwordInput = document.getElementById('register-password');
            var phoneInput = document.getElementById('register-phone');
            var companyInput = document.getElementById('register-company');

            var name = nameInput.value.trim();
            var email = emailInput.value.trim();
            var password = passwordInput.value;
            var phone = phoneInput.value.trim();
            var company = companyInput.value.trim();
            var valid = true;

            if (!name) {
                setFieldError(nameInput, true);
                valid = false;
            } else {
                setFieldError(nameInput, false);
            }

            if (!email || !validateEmail(email)) {
                setFieldError(emailInput, true);
                valid = false;
            } else {
                setFieldError(emailInput, false);
            }

            if (!password || password.length < 6) {
                setFieldError(passwordInput, true);
                valid = false;
            } else {
                setFieldError(passwordInput, false);
            }

            if (!valid) return;

            var btn = document.getElementById('register-submit-btn');
            btn.disabled = true;
            btn.classList.add('loading');

            try {
                var res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        email: email,
                        phone: phone || null,
                        company_name: company || null,
                        password: password
                    })
                });

                var data = await res.json();

                if (!res.ok) {
                    showMessage('register-message', data.detail || 'Registration failed. Please try again.', 'error');
                    btn.disabled = false;
                    btn.classList.remove('loading');
                    return;
                }

                localStorage.setItem('bol_token', data.token);
                localStorage.setItem('bol_user', JSON.stringify(data.user));

                showMessage('register-message', 'Account created! Redirecting...', 'success');
                setTimeout(function () {
                    window.location.href = '/';
                }, 800);
            } catch (err) {
                showMessage('register-message', 'Network error. Please try again.', 'error');
                btn.disabled = false;
                btn.classList.remove('loading');
            }
        });
    }

    var params = new URLSearchParams(window.location.search);
    if (params.get('tab') === 'register') {
        switchTab('register');
    }
});

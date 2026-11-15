document.addEventListener("DOMContentLoaded", function () {
    const existingToken = localStorage.getItem("bol_token");
    const urlParams = new URLSearchParams(window.location.search);
    if (existingToken && !urlParams.has("force")) {
        const nextUrl = urlParams.get("next") || "/";
        window.location.href = nextUrl;
        return;
    }

    const tabLoginBtn = document.getElementById("tabLoginBtn");
    const tabRegisterBtn = document.getElementById("tabRegisterBtn");
    const loginWrapper = document.getElementById("loginWrapper");
    const loginForm = document.getElementById("loginForm");
    const registerWrapper = document.getElementById("registerWrapper");
    const registerForm = document.getElementById("registerForm");
    const otpVerifyForm = document.getElementById("otpVerifyForm");
    const otpBackToDetailsBtn = document.getElementById("otpBackToDetailsBtn");
    const resendOtpBtn = document.getElementById("resendOtpBtn");
    const resendTimer = document.getElementById("resendTimer");
    const otpInputs = Array.from(document.querySelectorAll(".auth-otp-digit:not(.login-otp-digit)"));

    const loginMethodPasswordBtn = document.getElementById("loginMethodPasswordBtn");
    const loginMethodOtpBtn = document.getElementById("loginMethodOtpBtn");
    const loginOtpRequestForm = document.getElementById("loginOtpRequestForm");
    const loginOtpVerifyForm = document.getElementById("loginOtpVerifyForm");
    const loginOtpBackToPhoneBtn = document.getElementById("loginOtpBackToPhoneBtn");
    const loginResendOtpBtn = document.getElementById("loginResendOtpBtn");
    const loginResendTimer = document.getElementById("loginResendTimer");
    const loginOtpDigits = Array.from(document.querySelectorAll(".login-otp-digit"));

    let pendingRegistration = {
        name: "",
        email: "",
        phone: "",
        company_name: "",
        password: "",
    };

    let pendingLoginPhone = "";
    let resendCountdownInterval = null;
    let loginResendCountdownInterval = null;

    function setAlert(alertEl, message, type) {
        if (!alertEl) return;
        alertEl.className = "auth-alert " + type;
        alertEl.textContent = message;
        alertEl.style.display = "flex";
    }

    function clearAlert(alertEl) {
        if (!alertEl) return;
        alertEl.style.display = "none";
        alertEl.textContent = "";
        alertEl.className = "auth-alert";
    }

    function clearFieldErrors(container) {
        if (!container) return;
        container.querySelectorAll(".auth-field-group").forEach((group) => {
            group.classList.remove("has-error");
        });
    }

    function setFieldError(fieldId, isError) {
        const input = document.getElementById(fieldId);
        if (!input) return;
        const group = input.closest(".auth-field-group");
        if (!group) return;
        if (isError) {
            group.classList.add("has-error");
        } else {
            group.classList.remove("has-error");
        }
    }

    function switchAuthTab(tab) {
        clearAlert(document.getElementById("loginAlert"));
        clearAlert(document.getElementById("registerAlert"));
        clearAlert(document.getElementById("otpAlert"));
        clearFieldErrors(loginForm);
        clearFieldErrors(loginOtpRequestForm);
        clearFieldErrors(registerForm);

        if (tab === "register") {
            tabRegisterBtn.classList.add("active");
            tabLoginBtn.classList.remove("active");
            if (loginWrapper) loginWrapper.classList.remove("is-active");
            if (registerWrapper) registerWrapper.classList.add("is-active");
            if (registerForm) registerForm.style.display = "block";
            if (otpVerifyForm) otpVerifyForm.style.display = "none";
        } else {
            tabLoginBtn.classList.add("active");
            tabRegisterBtn.classList.remove("active");
            if (loginWrapper) loginWrapper.classList.add("is-active");
            if (registerWrapper) registerWrapper.classList.remove("is-active");
        }
    }

    function switchLoginMethod(method) {
        clearAlert(document.getElementById("loginAlert"));
        clearFieldErrors(loginForm);
        clearFieldErrors(loginOtpRequestForm);

        if (method === "otp") {
            if (loginMethodOtpBtn) loginMethodOtpBtn.classList.add("active");
            if (loginMethodPasswordBtn) loginMethodPasswordBtn.classList.remove("active");
            if (loginForm) loginForm.style.display = "none";
            if (loginOtpRequestForm) loginOtpRequestForm.style.display = "block";
            if (loginOtpVerifyForm) loginOtpVerifyForm.style.display = "none";
        } else {
            if (loginMethodPasswordBtn) loginMethodPasswordBtn.classList.add("active");
            if (loginMethodOtpBtn) loginMethodOtpBtn.classList.remove("active");
            if (loginForm) loginForm.style.display = "block";
            if (loginOtpRequestForm) loginOtpRequestForm.style.display = "none";
            if (loginOtpVerifyForm) loginOtpVerifyForm.style.display = "none";
        }
    }

    if (loginMethodPasswordBtn) {
        loginMethodPasswordBtn.addEventListener("click", () => switchLoginMethod("password"));
    }
    if (loginMethodOtpBtn) {
        loginMethodOtpBtn.addEventListener("click", () => switchLoginMethod("otp"));
    }

    if (tabLoginBtn) {
        tabLoginBtn.addEventListener("click", () => switchAuthTab("login"));
    }
    if (tabRegisterBtn) {
        tabRegisterBtn.addEventListener("click", () => switchAuthTab("register"));
    }

    document.querySelectorAll(".auth-switch-link").forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const target = this.dataset.switch;
            switchAuthTab(target);
        });
    });

    document.querySelectorAll(".auth-password-toggle").forEach((btn) => {
        btn.addEventListener("click", function () {
            const targetId = this.dataset.toggle;
            const input = document.getElementById(targetId);
            if (!input) return;
            const icon = this.querySelector("i");
            if (input.type === "password") {
                input.type = "text";
                if (icon) icon.className = "ph ph-eye-slash";
            } else {
                input.type = "password";
                if (icon) icon.className = "ph ph-eye";
            }
        });
    });

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function validatePhone(phone) {
        const digits = (phone || "").replace(/\D/g, "");
        return digits.length === 10;
    }

    function saveAuthSession(token, user) {
        localStorage.setItem("bol_token", token);
        localStorage.setItem("bol_user", JSON.stringify(user));
        document.cookie = `bol_token=${token}; path=/; max-age=259200; SameSite=Lax`;
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const alertEl = document.getElementById("loginAlert");
            clearAlert(alertEl);
            clearFieldErrors(loginForm);

            const identifierInput = document.getElementById("loginIdentifier");
            const passwordInput = document.getElementById("loginPassword");
            const submitBtn = document.getElementById("loginSubmitBtn");

            const identifier = identifierInput.value.trim();
            const password = passwordInput.value;

            let valid = true;
            if (!identifier) {
                setFieldError("loginIdentifier", true);
                valid = false;
            }
            if (!password) {
                setFieldError("loginPassword", true);
                valid = false;
            }

            if (!valid) return;

            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = "<span>Signing in...</span>";

            try {
                const response = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: identifier, password: password }),
                });

                const data = await response.json();

                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Invalid credentials. Please try again.", "error");
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                    return;
                }

                saveAuthSession(data.token, data.user);
                setAlert(alertEl, "Sign in successful! Redirecting...", "success");

                setTimeout(() => {
                    const nextUrl = urlParams.get("next") || "/";
                    window.location.href = nextUrl;
                }, 600);
            } catch (err) {
                setAlert(alertEl, "Network error. Please check your connection and try again.", "error");
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    function startLoginResendCooldown(seconds) {
        if (!loginResendOtpBtn || !loginResendTimer) return;
        if (loginResendCountdownInterval) clearInterval(loginResendCountdownInterval);

        let remaining = seconds || 30;
        loginResendOtpBtn.disabled = true;
        loginResendTimer.textContent = remaining + "s";

        loginResendCountdownInterval = setInterval(() => {
            remaining -= 1;
            if (remaining <= 0) {
                clearInterval(loginResendCountdownInterval);
                loginResendOtpBtn.disabled = false;
                loginResendTimer.textContent = "0s";
            } else {
                loginResendTimer.textContent = remaining + "s";
            }
        }, 1000);
    }

    if (loginOtpRequestForm) {
        loginOtpRequestForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const alertEl = document.getElementById("loginAlert");
            clearAlert(alertEl);
            clearFieldErrors(loginOtpRequestForm);

            const phoneInput = document.getElementById("loginOtpPhone");
            const sendBtn = document.getElementById("loginOtpSendBtn");
            const rawPhone = phoneInput.value.trim().replace(/\D/g, "");

            if (!rawPhone || rawPhone.length !== 10) {
                setFieldError("loginOtpPhone", true);
                return;
            }

            sendBtn.disabled = true;
            const originalText = sendBtn.innerHTML;
            sendBtn.innerHTML = "<span>Sending code...</span>";

            try {
                const response = await fetch("/api/auth/login/send-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ phone: rawPhone }),
                });

                const data = await response.json();
                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Unable to send login code. Please check your number.", "error");
                    sendBtn.disabled = false;
                    sendBtn.innerHTML = originalText;
                    return;
                }

                pendingLoginPhone = data.phone || ("+91" + rawPhone);
                const displayPhoneEl = document.getElementById("loginOtpDisplayPhone");
                if (displayPhoneEl) displayPhoneEl.textContent = pendingLoginPhone;

                const demoPill = document.getElementById("loginDemoOtpPill");
                const demoCode = document.getElementById("loginDemoOtpCode");
                if (data.demo_otp && demoPill && demoCode) {
                    demoCode.textContent = data.demo_otp;
                    demoPill.style.display = "inline-flex";
                } else if (demoPill) {
                    demoPill.style.display = "none";
                }

                loginOtpRequestForm.style.display = "none";
                loginOtpVerifyForm.style.display = "block";
                startLoginResendCooldown(data.cooldown || 30);
                loginOtpDigits.forEach((input) => (input.value = ""));
                if (loginOtpDigits[0]) loginOtpDigits[0].focus();
                setAlert(alertEl, "A 6-digit verification code has been sent to your mobile.", "success");
            } catch (err) {
                setAlert(alertEl, "Network error. Please try again.", "error");
            } finally {
                sendBtn.disabled = false;
                sendBtn.innerHTML = originalText;
            }
        });
    }

    if (loginResendOtpBtn) {
        loginResendOtpBtn.addEventListener("click", async function () {
            const alertEl = document.getElementById("loginAlert");
            clearAlert(alertEl);
            loginResendOtpBtn.disabled = true;

            try {
                const response = await fetch("/api/auth/login/resend-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ phone: pendingLoginPhone }),
                });

                const data = await response.json();
                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Unable to resend OTP.", "error");
                    loginResendOtpBtn.disabled = false;
                    return;
                }

                const demoPill = document.getElementById("loginDemoOtpPill");
                const demoCode = document.getElementById("loginDemoOtpCode");
                if (data.demo_otp && demoCode && demoPill) {
                    demoCode.textContent = data.demo_otp;
                    demoPill.style.display = "inline-flex";
                } else if (demoPill) {
                    demoPill.style.display = "none";
                }

                setAlert(alertEl, "A new login code has been generated.", "success");
                startLoginResendCooldown(data.cooldown || 30);
            } catch (err) {
                setAlert(alertEl, "Network error. Please try again.", "error");
                loginResendOtpBtn.disabled = false;
            }
        });
    }

    if (loginOtpBackToPhoneBtn) {
        loginOtpBackToPhoneBtn.addEventListener("click", function () {
            clearAlert(document.getElementById("loginAlert"));
            loginOtpVerifyForm.style.display = "none";
            loginOtpRequestForm.style.display = "block";
            const phoneInput = document.getElementById("loginOtpPhone");
            if (phoneInput) phoneInput.focus();
        });
    }

    loginOtpDigits.forEach((input, index) => {
        input.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
            if (this.value && index < loginOtpDigits.length - 1) {
                loginOtpDigits[index + 1].focus();
            }
        });

        input.addEventListener("keydown", function (e) {
            if (e.key === "Backspace" && !this.value && index > 0) {
                loginOtpDigits[index - 1].focus();
                loginOtpDigits[index - 1].value = "";
            }
        });

        input.addEventListener("paste", function (e) {
            e.preventDefault();
            const pasted = (e.clipboardData || window.clipboardData).getData("text");
            const cleanDigits = (pasted || "").replace(/\D/g, "").slice(0, 6);
            if (!cleanDigits) return;
            cleanDigits.split("").forEach((ch, idx) => {
                if (loginOtpDigits[idx]) loginOtpDigits[idx].value = ch;
            });
            const nextIdx = Math.min(cleanDigits.length, loginOtpDigits.length - 1);
            loginOtpDigits[nextIdx].focus();
        });
    });

    if (loginOtpVerifyForm) {
        loginOtpVerifyForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const alertEl = document.getElementById("loginAlert");
            const errorMsgEl = document.getElementById("loginOtpDigitsError");
            clearAlert(alertEl);
            if (errorMsgEl) errorMsgEl.style.display = "none";

            const otpValue = loginOtpDigits.map((i) => i.value).join("");
            if (otpValue.length !== 6) {
                if (errorMsgEl) errorMsgEl.style.display = "block";
                return;
            }

            const submitBtn = document.getElementById("loginOtpVerifySubmitBtn");
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = "<span>Signing in...</span>";

            try {
                const response = await fetch("/api/auth/login/verify-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        phone: pendingLoginPhone,
                        otp: otpValue,
                    }),
                });

                const data = await response.json();
                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Incorrect verification code. Please check and try again.", "error");
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                    return;
                }

                saveAuthSession(data.token, data.user);
                setAlert(alertEl, "Sign in successful! Redirecting...", "success");

                setTimeout(() => {
                    const nextUrl = urlParams.get("next") || "/";
                    window.location.href = nextUrl;
                }, 600);
            } catch (err) {
                setAlert(alertEl, "Network error. Please try again.", "error");
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    function startResendCooldown(seconds) {
        if (!resendOtpBtn || !resendTimer) return;
        if (resendCountdownInterval) clearInterval(resendCountdownInterval);

        let remaining = seconds || 30;
        resendOtpBtn.disabled = true;
        resendTimer.textContent = remaining + "s";

        resendCountdownInterval = setInterval(() => {
            remaining -= 1;
            if (remaining <= 0) {
                clearInterval(resendCountdownInterval);
                resendOtpBtn.disabled = false;
                resendTimer.textContent = "0s";
            } else {
                resendTimer.textContent = remaining + "s";
            }
        }, 1000);
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const alertEl = document.getElementById("registerAlert");
            clearAlert(alertEl);
            clearFieldErrors(registerForm);

            const nameInput = document.getElementById("regName");
            const emailInput = document.getElementById("regEmail");
            const phoneInput = document.getElementById("regPhone");
            const companyInput = document.getElementById("regCompany");
            const passwordInput = document.getElementById("regPassword");
            const continueBtn = document.getElementById("regContinueBtn");

            const name = nameInput.value.trim();
            const email = emailInput.value.trim();
            const phone = phoneInput.value.trim().replace(/\D/g, "");
            const company = companyInput.value.trim();
            const password = passwordInput.value;

            let valid = true;
            if (!name) {
                setFieldError("regName", true);
                valid = false;
            }
            if (!email || !validateEmail(email)) {
                setFieldError("regEmail", true);
                valid = false;
            }
            if (!phone || !validatePhone(phone)) {
                setFieldError("regPhone", true);
                valid = false;
            }
            if (!password || password.length < 6) {
                setFieldError("regPassword", true);
                valid = false;
            }

            if (!valid) return;

            continueBtn.disabled = true;
            const originalText = continueBtn.innerHTML;
            continueBtn.innerHTML = "<span>Sending verification code...</span>";

            try {
                const response = await fetch("/api/auth/register/send-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name: name,
                        email: email,
                        phone: phone,
                        company_name: company || null,
                        password: password,
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Registration failed. Please check your details.", "error");
                    continueBtn.disabled = false;
                    continueBtn.innerHTML = originalText;
                    return;
                }

                pendingRegistration = {
                    name: name,
                    email: email,
                    phone: data.phone || `+91${phone}`,
                    company_name: company || "",
                    password: password,
                };

                const displayPhoneEl = document.getElementById("otpDisplayPhone");
                if (displayPhoneEl) displayPhoneEl.textContent = pendingRegistration.phone;

                const demoOtpCodeEl = document.getElementById("demoOtpCode");
                const demoOtpPillEl = document.getElementById("demoOtpPill");
                if (data.demo_otp) {
                    if (demoOtpCodeEl) demoOtpCodeEl.textContent = data.demo_otp;
                    if (demoOtpPillEl) demoOtpPillEl.style.display = "inline-flex";
                } else if (demoOtpPillEl) {
                    demoOtpPillEl.style.display = "none";
                }

                registerForm.style.display = "none";
                otpVerifyForm.style.display = "block";
                clearAlert(document.getElementById("otpAlert"));

                startResendCooldown(data.cooldown || 30);

                otpInputs.forEach((i) => (i.value = ""));
                if (otpInputs.length > 0) otpInputs[0].focus();

                continueBtn.disabled = false;
                continueBtn.innerHTML = originalText;
            } catch (err) {
                setAlert(alertEl, "Network error. Please try again.", "error");
                continueBtn.disabled = false;
                continueBtn.innerHTML = originalText;
            }
        });
    }

    if (otpBackToDetailsBtn) {
        otpBackToDetailsBtn.addEventListener("click", function () {
            otpVerifyForm.style.display = "none";
            registerForm.style.display = "block";
            clearAlert(document.getElementById("registerAlert"));
        });
    }

    if (resendOtpBtn) {
        resendOtpBtn.addEventListener("click", async function () {
            const alertEl = document.getElementById("otpAlert");
            clearAlert(alertEl);

            try {
                resendOtpBtn.disabled = true;
                const response = await fetch("/api/auth/register/resend-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: pendingRegistration.email,
                        phone: pendingRegistration.phone,
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Unable to resend OTP. Please wait.", "error");
                    resendOtpBtn.disabled = false;
                    return;
                }

                const demoOtpPillEl = document.getElementById("demoOtpPill");
                if (data.demo_otp) {
                    const demoOtpCodeEl = document.getElementById("demoOtpCode");
                    if (demoOtpCodeEl) demoOtpCodeEl.textContent = data.demo_otp;
                    if (demoOtpPillEl) demoOtpPillEl.style.display = "inline-flex";
                } else if (demoOtpPillEl) {
                    demoOtpPillEl.style.display = "none";
                }

                setAlert(alertEl, "A new verification code has been generated.", "success");
                startResendCooldown(data.cooldown || 30);
            } catch (err) {
                setAlert(alertEl, "Network error. Please try again.", "error");
                resendOtpBtn.disabled = false;
            }
        });
    }

    otpInputs.forEach((input, index) => {
        input.addEventListener("input", function (e) {
            this.value = this.value.replace(/\D/g, "");
            if (this.value && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        input.addEventListener("keydown", function (e) {
            if (e.key === "Backspace" && !this.value && index > 0) {
                otpInputs[index - 1].focus();
                otpInputs[index - 1].value = "";
            }
        });

        input.addEventListener("paste", function (e) {
            e.preventDefault();
            const pasted = (e.clipboardData || window.clipboardData).getData("text");
            const cleanDigits = (pasted || "").replace(/\D/g, "").slice(0, 6);
            if (!cleanDigits) return;
            cleanDigits.split("").forEach((ch, idx) => {
                if (otpInputs[idx]) otpInputs[idx].value = ch;
            });
            const nextIdx = Math.min(cleanDigits.length, otpInputs.length - 1);
            otpInputs[nextIdx].focus();
        });
    });

    if (otpVerifyForm) {
        otpVerifyForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const alertEl = document.getElementById("otpAlert");
            const errorMsgEl = document.getElementById("otpDigitsError");
            clearAlert(alertEl);
            if (errorMsgEl) errorMsgEl.style.display = "none";

            const otpValue = otpInputs.map((i) => i.value).join("");
            if (otpValue.length !== 6) {
                if (errorMsgEl) errorMsgEl.style.display = "block";
                return;
            }

            const submitBtn = document.getElementById("otpSubmitBtn");
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = "<span>Verifying code...</span>";

            try {
                const response = await fetch("/api/auth/register/verify-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: pendingRegistration.email,
                        phone: pendingRegistration.phone,
                        otp: otpValue,
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    setAlert(alertEl, data.detail || "Incorrect verification code. Please check and try again.", "error");
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                    return;
                }

                saveAuthSession(data.token, data.user);
                setAlert(alertEl, "Account verified and created successfully! Redirecting...", "success");

                setTimeout(() => {
                    const nextUrl = urlParams.get("next") || "/";
                    window.location.href = nextUrl;
                }, 600);
            } catch (err) {
                setAlert(alertEl, "Network error. Please try again.", "error");
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    if (urlParams.get("tab") === "register" || window.location.hash === "#register") {
        switchAuthTab("register");
    }
});

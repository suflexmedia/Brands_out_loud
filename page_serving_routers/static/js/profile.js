document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("bol_token");
    if (!token) {
        window.location.href = "/login?next=/profile";
        return;
    }

    let currentUser = null;
    const tabButtons = Array.from(document.querySelectorAll(".profile-tab-btn"));
    const tabPanes = Array.from(document.querySelectorAll(".profile-tab-pane"));
    const phoneOtpDigits = Array.from(document.querySelectorAll(".profile-otp-digit"));

    function getInitials(name) {
        if (!name) return "U";
        const parts = name.trim().split(/\s+/);
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return parts[0].slice(0, 2).toUpperCase();
    }

    function switchProfileTab(tabId) {
        tabButtons.forEach((btn) => {
            const isMatch = btn.dataset.tab === tabId;
            btn.classList.toggle("active", isMatch);
            btn.setAttribute("aria-selected", isMatch ? "true" : "false");
        });

        tabPanes.forEach((pane) => {
            const targetId = "tab" + tabId.charAt(0).toUpperCase() + tabId.slice(1);
            pane.classList.toggle("active", pane.id === targetId);
        });

        window.location.hash = tabId;
    }

    tabButtons.forEach((btn) => {
        btn.addEventListener("click", () => switchProfileTab(btn.dataset.tab));
    });

    if (window.location.hash) {
        const hashTab = window.location.hash.replace("#", "");
        if (["purchases", "edit", "security"].includes(hashTab)) {
            switchProfileTab(hashTab);
        }
    }

    window.addEventListener("hashchange", () => {
        const hashTab = window.location.hash.replace("#", "");
        if (["purchases", "edit", "security"].includes(hashTab)) {
            switchProfileTab(hashTab);
        }
    });

    function setAlert(alertEl, message, type) {
        if (!alertEl) return;
        alertEl.className = "profile-alert " + type;
        alertEl.textContent = message;
        alertEl.style.display = "flex";
    }

    function clearAlert(alertEl) {
        if (!alertEl) return;
        alertEl.style.display = "none";
        alertEl.textContent = "";
        alertEl.className = "profile-alert";
    }

    function updateProfileUi(user) {
        currentUser = user;
        const initials = getInitials(user.name);
        const nameEl = document.getElementById("profileHeaderName");
        const avatarEl = document.getElementById("profileHeaderAvatar");
        const emailEl = document.getElementById("profileHeaderEmail");
        const phoneEl = document.getElementById("profileHeaderPhone");
        const currentPhoneDisplay = document.getElementById("currentPhoneDisplay");

        if (nameEl) nameEl.textContent = user.name || "Member";
        if (avatarEl) avatarEl.textContent = initials;
        if (emailEl) {
            emailEl.querySelector("span").textContent = user.email || "No email";
        }
        if (phoneEl) {
            phoneEl.querySelector("span").textContent = user.phone || "No mobile added";
        }
        if (currentPhoneDisplay) {
            currentPhoneDisplay.textContent = user.phone || "Not set";
        }

        const inputName = document.getElementById("editFullName");
        const inputCompany = document.getElementById("editCompanyName");
        const inputEmail = document.getElementById("editEmail");

        if (inputName) inputName.value = user.name || "";
        if (inputCompany) inputCompany.value = user.company_name || "";
        if (inputEmail) inputEmail.value = user.email || "";
    }

    async function loadUserProfile() {
        try {
            const rawUser = localStorage.getItem("bol_user");
            if (rawUser) {
                updateProfileUi(JSON.parse(rawUser));
            }

            const response = await fetch("/api/auth/me", {
                headers: { Authorization: "Bearer " + token },
            });
            if (response.status === 401) {
                localStorage.removeItem("bol_token");
                localStorage.removeItem("bol_user");
                window.location.href = "/login?next=/profile";
                return;
            }
            if (response.ok) {
                const data = await response.json();
                if (data.user) {
                    localStorage.setItem("bol_user", JSON.stringify(data.user));
                    updateProfileUi(data.user);
                }
            }
        } catch (e) {}
    }

    window.loadUserPurchases = async function () {
        const loadingEl = document.getElementById("purchasesLoading");
        const emptyEl = document.getElementById("purchasesEmpty");
        const listEl = document.getElementById("purchasesList");

        if (loadingEl) loadingEl.style.display = "flex";
        if (emptyEl) emptyEl.style.display = "none";
        if (listEl) listEl.style.display = "none";

        try {
            const res = await fetch("/api/auth/purchases", {
                headers: { Authorization: "Bearer " + token },
            });
            if (loadingEl) loadingEl.style.display = "none";

            if (!res.ok) {
                if (emptyEl) emptyEl.style.display = "block";
                return;
            }

            const data = await res.json();
            const purchases = data.purchases || [];

            if (purchases.length === 0) {
                if (emptyEl) emptyEl.style.display = "block";
                return;
            }

            listEl.innerHTML = purchases.map((p) => {
                const step1Class = p.progress_step >= 1 ? (p.progress_step > 1 ? "completed" : "active") : "";
                const step2Class = p.progress_step >= 2 ? (p.progress_step > 2 ? "completed" : "active") : "";
                const step3Class = p.progress_step >= 3 ? "completed" : "";

                return `
                <div class="purchase-item-card">
                    <div class="purchase-cover-wrap">
                        <img src="${p.cover_url}" alt="${p.item_title}" class="purchase-cover-img" onerror="this.src='/static/images/laserveda/book_cover.png'" />
                    </div>

                    <div class="purchase-details">
                        <div class="purchase-header-row">
                            <span class="order-badge-pill">${p.order_number}</span>
                            <span class="order-date-text">Ordered on ${p.date || "Recent"}</span>
                        </div>

                        <h3 class="purchase-title">${p.item_title}</h3>
                        <p class="purchase-subtitle">${p.item_subtitle}</p>
                        <div class="purchase-author">${p.item_author} · <span style="color:#93c5fd;">${p.item_edition}</span></div>

                        <div class="delivery-progress-wrap">
                            <div class="delivery-status-header">
                                <span class="delivery-status-pill">
                                    <i class="ph ph-package"></i>
                                    <span>${p.status_label}</span>
                                </span>
                                <span style="font-size:0.8vw;color:rgba(255,255,255,0.6);font-family:'Space Mono',monospace;">₹${p.amount} paid</span>
                            </div>

                            <div class="delivery-timeline">
                                <div class="timeline-step ${step1Class}">
                                    <div class="step-dot"></div>
                                    <span class="step-label">Order Confirmed</span>
                                </div>
                                <div class="timeline-step ${step2Class}">
                                    <div class="step-dot"></div>
                                    <span class="step-label">Dispatched</span>
                                </div>
                                <div class="timeline-step ${step3Class}">
                                    <div class="step-dot"></div>
                                    <span class="step-label">Delivered</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="purchase-actions">
                        <a href="${p.read_url}" class="btn-primary btn-read-ebook">
                            <i class="ph ph-book-open"></i>
                            <span>Read E-Book Online</span>
                        </a>
                        <span style="font-size:0.75vw;color:rgba(255,255,255,0.5);text-align:right;">Instant Digital Access Included</span>
                    </div>
                </div>
                `;
            }).join("");

            listEl.style.display = "flex";
        } catch (e) {
            if (loadingEl) loadingEl.style.display = "none";
            if (emptyEl) emptyEl.style.display = "block";
        }
    };

    const detailsForm = document.getElementById("profileDetailsForm");
    if (detailsForm) {
        detailsForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const alertEl = document.getElementById("profileDetailsAlert");
            clearAlert(alertEl);

            const nameInput = document.getElementById("editFullName");
            const companyInput = document.getElementById("editCompanyName");
            const saveBtn = document.getElementById("saveDetailsBtn");

            const newName = nameInput.value.trim();
            if (!newName) {
                setAlert(alertEl, "Please enter your full name.", "error");
                return;
            }

            saveBtn.disabled = true;
            saveBtn.innerHTML = "<span>Saving...</span>";

            try {
                const res = await fetch("/api/auth/profile", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: "Bearer " + token,
                    },
                    body: JSON.stringify({
                        name: newName,
                        company_name: companyInput.value.trim(),
                    }),
                });

                const data = await res.json();
                saveBtn.disabled = false;
                saveBtn.innerHTML = "<span>Save Changes</span>";

                if (!res.ok) {
                    setAlert(alertEl, data.detail || "Failed to update profile.", "error");
                    return;
                }

                if (currentUser) {
                    currentUser.name = newName;
                    currentUser.company_name = companyInput.value.trim();
                    localStorage.setItem("bol_user", JSON.stringify(currentUser));
                    updateProfileUi(currentUser);
                }

                setAlert(alertEl, "Personal details updated successfully!", "success");
            } catch (err) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = "<span>Save Changes</span>";
                setAlert(alertEl, "Network error. Please try again.", "error");
            }
        });
    }

    let targetNewPhone = "";

    window.togglePhoneChangeModule = function (show) {
        const module = document.getElementById("phoneChangeModule");
        const toggleWrap = document.getElementById("phoneChangeToggleWrap");
        const alertEl = document.getElementById("phoneAlert");
        clearAlert(alertEl);

        if (show) {
            if (module) module.style.display = "block";
            if (toggleWrap) toggleWrap.style.display = "none";
            document.getElementById("phoneStep1").style.display = "block";
            document.getElementById("phoneStep2").style.display = "none";
            const input = document.getElementById("newPhoneInput");
            if (input) {
                input.value = "";
                input.focus();
            }
        } else {
            if (module) module.style.display = "none";
            if (toggleWrap) toggleWrap.style.display = "block";
        }
    };

    window.requestPhoneChangeOtp = async function () {
        const input = document.getElementById("newPhoneInput");
        const alertEl = document.getElementById("phoneAlert");
        const sendBtn = document.getElementById("sendPhoneOtpBtn");
        clearAlert(alertEl);

        const cleanDigits = (input ? input.value : targetNewPhone).replace(/\D/g, "");
        if (cleanDigits.length < 10) {
            setAlert(alertEl, "Please enter a valid 10-digit mobile number.", "error");
            return;
        }

        targetNewPhone = cleanDigits.slice(-10);
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.innerHTML = "<span>Sending code...</span>";
        }

        try {
            const res = await fetch("/api/auth/profile/phone/send-otp", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + token,
                },
                body: JSON.stringify({ new_phone: targetNewPhone }),
            });

            const data = await res.json();
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = "<span>Send Verification OTP</span>";
            }

            if (!res.ok) {
                setAlert(alertEl, data.detail || "Unable to send verification code.", "error");
                return;
            }

            document.getElementById("phoneStep1").style.display = "none";
            document.getElementById("phoneStep2").style.display = "block";
            document.getElementById("otpTargetPhone").textContent = "+91 " + targetNewPhone;

            const demoPill = document.getElementById("phoneDemoOtpWrap");
            const demoCode = document.getElementById("phoneDemoOtpCode");
            if (data.demo_otp && demoPill && demoCode) {
                demoCode.textContent = data.demo_otp;
                demoPill.style.display = "inline-flex";
            }

            setAlert(alertEl, "A 6-digit verification code has been generated.", "success");
            phoneOtpDigits.forEach((d) => (d.value = ""));
            if (phoneOtpDigits[0]) phoneOtpDigits[0].focus();
        } catch (err) {
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = "<span>Send Verification OTP</span>";
            }
            setAlert(alertEl, "Network error. Please try again.", "error");
        }
    };

    phoneOtpDigits.forEach((input, index) => {
        input.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
            if (this.value && index < phoneOtpDigits.length - 1) {
                phoneOtpDigits[index + 1].focus();
            }
        });

        input.addEventListener("keydown", function (e) {
            if (e.key === "Backspace" && !this.value && index > 0) {
                phoneOtpDigits[index - 1].focus();
                phoneOtpDigits[index - 1].value = "";
            }
        });

        input.addEventListener("paste", function (e) {
            e.preventDefault();
            const pasted = (e.clipboardData || window.clipboardData).getData("text");
            const digits = (pasted || "").replace(/\D/g, "").slice(0, 6);
            if (!digits) return;
            digits.split("").forEach((ch, idx) => {
                if (phoneOtpDigits[idx]) phoneOtpDigits[idx].value = ch;
            });
            const nextIdx = Math.min(digits.length, phoneOtpDigits.length - 1);
            phoneOtpDigits[nextIdx].focus();
        });
    });

    window.confirmPhoneChangeOtp = async function () {
        const alertEl = document.getElementById("phoneAlert");
        const verifyBtn = document.getElementById("verifyPhoneOtpBtn");
        clearAlert(alertEl);

        const otpValue = phoneOtpDigits.map((i) => i.value).join("");
        if (otpValue.length !== 6) {
            setAlert(alertEl, "Please enter the complete 6-digit verification code.", "error");
            return;
        }

        verifyBtn.disabled = true;
        verifyBtn.innerHTML = "<span>Verifying...</span>";

        try {
            const res = await fetch("/api/auth/profile/phone/verify-otp", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + token,
                },
                body: JSON.stringify({
                    new_phone: targetNewPhone,
                    otp: otpValue,
                }),
            });

            const data = await res.json();
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = "<span>Verify & Update</span>";

            if (!res.ok) {
                setAlert(alertEl, data.detail || "Incorrect verification code. Please try again.", "error");
                return;
            }

            if (currentUser) {
                currentUser.phone = data.phone;
                localStorage.setItem("bol_user", JSON.stringify(currentUser));
                updateProfileUi(currentUser);
            }

            setAlert(alertEl, "Mobile number updated and verified successfully!", "success");
            setTimeout(() => {
                togglePhoneChangeModule(false);
            }, 1200);
        } catch (err) {
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = "<span>Verify & Update</span>";
            setAlert(alertEl, "Network error. Please try again.", "error");
        }
    };

    window.confirmDeleteMyAccount = async function () {
        if (!confirm("Are you sure you want to permanently delete your account?\nAll your encrypted profile information will be purged from our database.\nThis action cannot be undone.")) {
            return;
        }

        try {
            const res = await fetch("/api/auth/me", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + token,
                },
            });

            if (!res.ok) {
                const data = await res.json();
                alert(data.detail || "Failed to delete account. Please try again.");
                return;
            }

            localStorage.removeItem("bol_token");
            localStorage.removeItem("bol_user");
            alert("Your account has been permanently deleted.");
            window.location.href = "/";
        } catch (err) {
            alert("Network error while deleting account.");
        }
    };

    loadUserProfile();
    loadUserPurchases();
});

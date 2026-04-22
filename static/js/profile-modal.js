function getCsrfTokenFromCookie() {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="));
  return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : "";
}

function clearProfileErrors() {
  document.getElementById("profile-name-error").textContent = "";
  document.getElementById("profile-department-error").textContent = "";
}

function showProfileFeedback(message, isSuccess) {
  const feedback = document.getElementById("profile-feedback");
  feedback.textContent = message;
  feedback.classList.remove("hidden", "bg-rose-100", "text-rose-700", "bg-emerald-100", "text-emerald-700");
  if (isSuccess) {
    feedback.classList.add("bg-emerald-100", "text-emerald-700");
  } else {
    feedback.classList.add("bg-rose-100", "text-rose-700");
  }
}

function hideProfileFeedback() {
  const feedback = document.getElementById("profile-feedback");
  feedback.classList.add("hidden");
  feedback.textContent = "";
}

function applyProfileToDashboard(profile) {
  const nameEls = document.querySelectorAll("[data-profile-name]");
  const departmentEls = document.querySelectorAll("[data-profile-department]");
  const roleEls = document.querySelectorAll("[data-profile-role]");

  nameEls.forEach((el) => {
    el.textContent = profile.name || "Not set";
  });
  departmentEls.forEach((el) => {
    el.textContent = profile.department || "Not set";
  });
  roleEls.forEach((el) => {
    el.textContent = profile.role || "RN";
  });
}

async function loadProfileForm() {
  clearProfileErrors();
  hideProfileFeedback();

  const response = await fetch("/api/profile/", {
    method: "GET",
    headers: { "X-Requested-With": "XMLHttpRequest" },
    credentials: "same-origin",
  });

  if (!response.ok) {
    throw new Error("Unable to load profile.");
  }

  const profile = await response.json();
  const emailInput = document.getElementById("profile-email-input");
  if (emailInput) {
    emailInput.value = profile.email || "";
  }
  document.getElementById("profile-name-input").value = profile.name || "";
  document.getElementById("profile-department-input").value = profile.department || "";
}

function openProfileModal() {
  const modal = document.getElementById("profile-modal");
  const card = document.getElementById("profile-modal-card");
  const saveButton = document.getElementById("profile-save-button");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.style.display = "block";
  modal.classList.remove("is-visible");
  if (saveButton) {
    saveButton.disabled = false;
    saveButton.textContent = "Save / Update";
  }
  if (card) {
    card.style.position = "fixed";
    card.style.top = "50%";
    card.style.left = "50%";
    card.style.transform = "translate(-50%, -50%)";
  }
  window.requestAnimationFrame(() => {
    modal.classList.add("is-visible");
  });

  loadProfileForm().catch((error) => {
    showProfileFeedback(error.message, false);
  });
}

function closeProfileModal() {
  const modal = document.getElementById("profile-modal");
  if (!modal) return;
  modal.classList.remove("is-visible");
  window.setTimeout(() => {
    modal.style.display = "none";
    modal.classList.add("hidden");
  }, 220);
}

async function handleProfileSubmit(event) {
  event.preventDefault();
  clearProfileErrors();
  hideProfileFeedback();

  const form = document.getElementById("profile-form");
  const saveButton = document.getElementById("profile-save-button");
  const formData = new FormData(form);
  const name = (formData.get("name") || "").toString().trim();
  const department = (formData.get("department") || "").toString().trim();

  if (!name) {
    document.getElementById("profile-name-error").textContent = "Name is required.";
    return;
  }

  if (!department) {
    document.getElementById("profile-department-error").textContent = "Department is required.";
    return;
  }

  saveButton.disabled = true;
  saveButton.textContent = "Saving...";

  try {
    const response = await fetch("/api/profile/update/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCsrfTokenFromCookie(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
      credentials: "same-origin",
    });

    const payload = await response.json();

    if (!response.ok) {
      const errors = payload.errors || {};
      document.getElementById("profile-name-error").textContent = errors.name || "";
      document.getElementById("profile-department-error").textContent = errors.department || "";
      if (!errors.name && !errors.department) {
        showProfileFeedback("Unable to update profile.", false);
      }
      return;
    }

    applyProfileToDashboard(payload.profile);
    showProfileFeedback(payload.message || "Profile updated successfully.", true);
    window.setTimeout(closeProfileModal, 700);
  } catch (error) {
    showProfileFeedback("Unable to update profile.", false);
  } finally {
    saveButton.disabled = false;
    saveButton.textContent = "Save / Update";
  }
}

function initProfileModal() {
  const modal = document.getElementById("profile-modal");
  if (!modal) return;

  if (modal.dataset.initialized === "true") return;
  modal.dataset.initialized = "true";
  modal.style.display = "none";

  modal.addEventListener("click", (event) => {
    if (event.target === modal || event.target.closest("[data-profile-close]")) {
      closeProfileModal();
    }
  });

  const form = document.getElementById("profile-form");
  if (form) {
    form.addEventListener("submit", handleProfileSubmit);
  }
}

document.addEventListener("click", (event) => {
  const openButton = event.target.closest("[data-open-profile]");
  if (openButton) {
    event.preventDefault();
    openProfileModal();
  }
});

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initProfileModal);
} else {
  initProfileModal();
}

window.initProfileModal = initProfileModal;
window.openProfileModal = openProfileModal;
window.closeProfileModal = closeProfileModal;

function logout() {
  const shouldLogout = window.confirm("Are you sure you want to logout?");
  if (!shouldLogout) return;

  window.location.href = "/logout/";
}

function initAuthGuard() {
  // Auth guard is enforced on the backend via Django login_required.
}

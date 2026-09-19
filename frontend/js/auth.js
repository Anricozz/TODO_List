const authState = {
  mode: "login",
};

const authElements = {};

document.addEventListener("DOMContentLoaded", initAuth);

function initAuth() {
  cacheAuthElements();
  authElements.form.addEventListener("submit", handleAuthSubmit);
  authElements.tabs.forEach((tab) => {
    tab.addEventListener("click", () => switchMode(tab.dataset.mode));
  });
  refreshAuthIcons();
  restoreSession();
}

function cacheAuthElements() {
  authElements.form = document.querySelector("#auth-form");
  authElements.tabs = document.querySelectorAll("[data-mode]");
  authElements.title = document.querySelector("#auth-title");
  authElements.subtitle = document.querySelector("#auth-subtitle");
  authElements.username = document.querySelector("#auth-username");
  authElements.password = document.querySelector("#auth-password");
  authElements.error = document.querySelector("#auth-error");
  authElements.submit = document.querySelector("#auth-submit");
  authElements.submitLabel = document.querySelector("#auth-submit-label");
}

// 已有未失效的 token 时直接进待办页；失效则留在本页，不自动登入
async function restoreSession() {
  if (!window.TodoApi.hasStoredTokens()) {
    return;
  }

  try {
    await window.TodoApi.fetchCurrentUser();
  } catch {
    return;
  }

  window.TodoApi.redirectToApp();
}

function switchMode(mode) {
  authState.mode = mode;
  const isLogin = mode === "login";

  authElements.tabs.forEach((tab) => {
    const isActive = tab.dataset.mode === mode;
    tab.classList.toggle("is-active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
  });

  authElements.title.textContent = isLogin ? "登入你的清单" : "创建新账号";
  authElements.subtitle.textContent = isLogin
    ? "登入后只能看到属于你自己的待办。"
    : "只需用户名和密码，注册成功后会自动登入。";
  authElements.submitLabel.textContent = isLogin ? "登入" : "注册并登入";
  authElements.password.setAttribute(
    "autocomplete",
    isLogin ? "current-password" : "new-password",
  );
  authElements.error.textContent = "";
}

async function handleAuthSubmit(event) {
  event.preventDefault();
  authElements.error.textContent = "";

  const username = authElements.username.value.trim();
  const password = authElements.password.value;
  const isLogin = authState.mode === "login";

  if (username.length < 3) {
    authElements.error.textContent = "用户名至少需要 3 个字符。";
    authElements.username.focus();
    return;
  }

  if (password.length < 6) {
    authElements.error.textContent = "密码至少需要 6 个字符。";
    authElements.password.focus();
    return;
  }

  setAuthBusy(true);
  try {
    if (isLogin) {
      await window.TodoApi.login(username, password);
    } else {
      await window.TodoApi.register(username, password);
    }
  } catch (error) {
    authElements.error.textContent = formatAuthError(error);
    return;
  } finally {
    setAuthBusy(false);
  }

  window.TodoApi.redirectToApp();
}

function formatAuthError(error) {
  if (Array.isArray(error.detail)) {
    return error.detail
      .map((item) => item.msg?.replace(/^Value error, /, "") || "输入内容无效")
      .join("；");
  }
  return error.message || "请求失败，请稍后重试。";
}

function setAuthBusy(isBusy) {
  authElements.submit.disabled = isBusy;
  authElements.submit.setAttribute("aria-busy", String(isBusy));
}

function refreshAuthIcons() {
  if (window.lucide) {
    window.lucide.createIcons({
      attrs: {
        "stroke-width": 2,
      },
    });
  }
}

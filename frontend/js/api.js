class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

const config = window.APP_CONFIG;

// 这些接口的 401 是业务结果（密码错误、凭据失效），不触发自动刷新
const NO_REFRESH_PATHS = ["/auth/login", "/auth/register", "/auth/refresh"];

let refreshPromise = null;

function getAccessToken() {
  return window.localStorage.getItem(config.ACCESS_TOKEN_KEY);
}

function getRefreshToken() {
  return window.localStorage.getItem(config.REFRESH_TOKEN_KEY);
}

function saveTokens(data) {
  if (data?.access_token) {
    window.localStorage.setItem(config.ACCESS_TOKEN_KEY, data.access_token);
  }
  if (data?.refresh_token) {
    window.localStorage.setItem(config.REFRESH_TOKEN_KEY, data.refresh_token);
  }
}

function clearTokens() {
  window.localStorage.removeItem(config.ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(config.REFRESH_TOKEN_KEY);
}

function hasStoredTokens() {
  return Boolean(getAccessToken() || getRefreshToken());
}

function isLoginPage() {
  return window.location.pathname.endsWith("login.html");
}

function redirectToLogin() {
  window.location.replace(config.LOGIN_PAGE);
}

function redirectToApp() {
  window.location.replace(config.APP_PAGE);
}

function handleSessionExpired() {
  clearTokens();
  if (!isLoginPage()) {
    redirectToLogin();
  }
}

// 成功响应统一是 {code, message, data}，这里解包后只把 data 交给调用方
function unwrap(data) {
  if (data && typeof data === "object" && "code" in data && "data" in data) {
    return data.data;
  }
  return data;
}

async function send(path, options = {}) {
  const { auth = true, ...init } = options;
  const headers = new Headers(init.headers || {});

  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const accessToken = getAccessToken();
  if (auth && accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  let response;
  try {
    response = await fetch(`${config.API_BASE_URL}${path}`, {
      ...init,
      headers,
    });
  } catch {
    throw new ApiError("无法连接服务器，请确认后端已经启动。", 0, null);
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail ?? "请求失败，请稍后重试。";
    const message =
      typeof detail === "string" ? detail : "提交的信息格式不正确。";
    throw new ApiError(message, response.status, detail);
  }

  return unwrap(data);
}

// refresh token 换新的 access token；并发请求共用同一次刷新
async function refreshAccessToken() {
  if (refreshPromise) {
    return refreshPromise;
  }

  const refreshToken = getRefreshToken();
  refreshPromise = (async () => {
    if (!refreshToken) {
      throw new ApiError("登录状态无效或已过期，请重新登录", 401, null);
    }
    const data = await send("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
      auth: false,
    });
    window.localStorage.setItem(config.ACCESS_TOKEN_KEY, data.access_token);
    return data.access_token;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

async function request(path, options = {}) {
  try {
    return await send(path, options);
  } catch (error) {
    const skipRefresh = NO_REFRESH_PATHS.some((item) => path.startsWith(item));

    if (error.status !== 401 || skipRefresh || !getRefreshToken()) {
      if (error.status === 401 && !skipRefresh) {
        handleSessionExpired();
      }
      throw error;
    }

    try {
      await refreshAccessToken();
    } catch (refreshError) {
      // refresh token 也过期了：清空凭据，下次打开不会自动登入
      handleSessionExpired();
      throw refreshError;
    }

    return send(path, options);
  }
}

async function login(username, password) {
  const data = await send("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
    auth: false,
  });
  saveTokens(data);
  return data.user;
}

async function register(username, password) {
  const data = await send("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password }),
    auth: false,
  });
  saveTokens(data);
  return data.user;
}

function fetchCurrentUser() {
  return request("/auth/me");
}

function logout() {
  clearTokens();
  redirectToLogin();
}

window.TodoApi = Object.freeze({
  ApiError,
  clearTokens,
  fetchCurrentUser,
  getAccessToken,
  getRefreshToken,
  hasStoredTokens,
  login,
  logout,
  redirectToApp,
  redirectToLogin,
  register,
  request,
  saveTokens,
});

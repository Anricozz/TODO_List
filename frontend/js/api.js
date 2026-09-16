class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  let response;
  try {
    response = await fetch(`${window.APP_CONFIG.API_BASE_URL}${path}`, {
      ...options,
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

  return data;
}

window.TodoApi = Object.freeze({
  request,
  ApiError,
});

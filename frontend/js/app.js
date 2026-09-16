const state = {
  todos: [],
  filter: "all",
  search: "",
  pendingDeleteId: null,
};

const elements = {};

document.addEventListener("DOMContentLoaded", init);

function init() {
  cacheElements();
  bindEvents();
  updateTodayLabel();
  loadTodos();
  refreshIcons();
}

function cacheElements() {
  elements.todayLabel = document.querySelector("#today-label");
  elements.searchInput = document.querySelector("#search-input");
  elements.filterButtons = document.querySelectorAll("[data-filter]");
  elements.taskList = document.querySelector("#task-list");
  elements.emptyState = document.querySelector("#empty-state");
  elements.emptyTitle = document.querySelector("#empty-title");
  elements.emptyCopy = document.querySelector("#empty-copy");
  elements.emptyCreateButton = document.querySelector("#empty-create-button");
  elements.openCreateDialog = document.querySelector("#open-create-dialog");
  elements.taskTemplate = document.querySelector("#task-template");
  elements.todoDialog = document.querySelector("#todo-dialog");
  elements.todoForm = document.querySelector("#todo-form");
  elements.todoDialogTitle = document.querySelector("#todo-dialog-title");
  elements.todoId = document.querySelector("#todo-id");
  elements.todoTitle = document.querySelector("#todo-title");
  elements.todoDescription = document.querySelector("#todo-description");
  elements.todoPriority = document.querySelector("#todo-priority");
  elements.todoFormError = document.querySelector("#todo-form-error");
  elements.saveTodoButton = document.querySelector("#save-todo-button");
  elements.confirmDialog = document.querySelector("#confirm-dialog");
  elements.confirmDeleteButton = document.querySelector("#confirm-delete-button");
  elements.statTotal = document.querySelector("#stat-total");
  elements.statActive = document.querySelector("#stat-active");
  elements.statCompleted = document.querySelector("#stat-completed");
  elements.progressTrack = document.querySelector("#progress-track");
  elements.progressFill = document.querySelector("#progress-fill");
  elements.toastRegion = document.querySelector("#toast-region");
}

function bindEvents() {
  elements.openCreateDialog.addEventListener("click", openCreateTaskDialog);
  elements.emptyCreateButton.addEventListener("click", openCreateTaskDialog);
  elements.todoForm.addEventListener("submit", handleTodoSubmit);
  elements.confirmDeleteButton.addEventListener("click", confirmDelete);
  elements.searchInput.addEventListener("input", handleSearch);
  elements.taskList.addEventListener("click", handleTaskAction);

  elements.filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      elements.filterButtons.forEach((item) => {
        item.classList.toggle("is-active", item === button);
      });
      renderTodos();
    });
  });

  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelector(`#${button.dataset.closeDialog}`).close();
    });
  });

  [elements.todoDialog, elements.confirmDialog].forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        dialog.close();
      }
    });
  });
}

async function loadTodos() {
  try {
    state.todos = await window.TodoApi.request("/todos");
    renderTodos();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function renderTodos() {
  const filteredTodos = getFilteredTodos();
  elements.taskList.replaceChildren();

  filteredTodos.forEach((todo) => {
    const fragment = elements.taskTemplate.content.cloneNode(true);
    const item = fragment.querySelector(".task-item");
    const title = fragment.querySelector(".task-title");
    const description = fragment.querySelector(".task-description");
    const priority = fragment.querySelector(".priority-badge");
    const date = fragment.querySelector(".task-date");
    const check = fragment.querySelector(".task-check");
    const checkIcon = fragment.querySelector(".task-check [data-lucide]");

    item.dataset.id = todo.id;
    item.classList.toggle("is-completed", todo.completed);
    title.textContent = todo.title;
    description.textContent = todo.description || "";
    priority.textContent = priorityLabel(todo.priority);
    priority.dataset.priority = todo.priority;
    date.textContent = `创建于 ${formatShortDate(todo.created_at)}`;
    check.setAttribute(
      "aria-label",
      todo.completed ? "标记为待完成" : "标记为已完成",
    );
    if (todo.completed) {
      checkIcon.setAttribute("data-lucide", "circle-check-big");
    }

    elements.taskList.append(fragment);
  });

  updateEmptyState(filteredTodos.length);
  updateStats();
  refreshIcons();
}

function getFilteredTodos() {
  const keyword = state.search.trim().toLowerCase();
  return state.todos.filter((todo) => {
    const matchesFilter =
      state.filter === "all" ||
      (state.filter === "active" && !todo.completed) ||
      (state.filter === "completed" && todo.completed);
    const searchable = `${todo.title} ${todo.description || ""}`.toLowerCase();
    return matchesFilter && (!keyword || searchable.includes(keyword));
  });
}

function updateEmptyState(resultCount) {
  const hasTodos = state.todos.length > 0;
  const hasResults = resultCount > 0;
  elements.emptyState.hidden = hasResults;

  if (hasResults) {
    return;
  }

  if (!hasTodos) {
    elements.emptyTitle.textContent = "还没有任务";
    elements.emptyCopy.textContent = "创建第一件待办，让今天从清楚的一步开始。";
    elements.emptyCreateButton.hidden = false;
    return;
  }

  elements.emptyTitle.textContent = "没有符合条件的任务";
  elements.emptyCopy.textContent = "试试更换筛选条件或搜索其他关键词。";
  elements.emptyCreateButton.hidden = true;
}

function updateStats() {
  const total = state.todos.length;
  const completed = state.todos.filter((todo) => todo.completed).length;
  const active = total - completed;
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100);

  elements.statTotal.textContent = String(total);
  elements.statActive.textContent = String(active);
  elements.statCompleted.textContent = `${percentage}%`;
  elements.progressFill.style.width = `${percentage}%`;
  elements.progressTrack.setAttribute("aria-valuenow", String(percentage));
}

function handleSearch(event) {
  state.search = event.target.value;
  renderTodos();
}

function openCreateTaskDialog() {
  elements.todoForm.reset();
  elements.todoId.value = "";
  elements.todoPriority.value = "medium";
  elements.todoDialogTitle.textContent = "新建任务";
  elements.todoFormError.textContent = "";
  elements.todoDialog.showModal();
  elements.todoTitle.focus();
}

function openEditTaskDialog(todo) {
  elements.todoForm.reset();
  elements.todoId.value = String(todo.id);
  elements.todoTitle.value = todo.title;
  elements.todoDescription.value = todo.description || "";
  elements.todoPriority.value = todo.priority;
  elements.todoDialogTitle.textContent = "编辑任务";
  elements.todoFormError.textContent = "";
  elements.todoDialog.showModal();
  elements.todoTitle.focus();
}

async function handleTodoSubmit(event) {
  event.preventDefault();
  elements.todoFormError.textContent = "";

  const title = elements.todoTitle.value.trim();
  if (!title) {
    elements.todoFormError.textContent = "请输入任务名称。";
    elements.todoTitle.focus();
    return;
  }

  const todoId = elements.todoId.value;
  const payload = {
    title,
    description: elements.todoDescription.value.trim() || null,
    priority: elements.todoPriority.value,
  };

  setButtonBusy(elements.saveTodoButton, true);
  try {
    if (todoId) {
      const updated = await window.TodoApi.request(`/todos/${todoId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      replaceTodo(updated);
      showToast("任务已更新。");
    } else {
      const created = await window.TodoApi.request("/todos", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      state.todos.unshift(created);
      showToast("任务已创建。");
    }
    elements.todoDialog.close();
    renderTodos();
  } catch (error) {
    elements.todoFormError.textContent = formatApiError(error);
  } finally {
    setButtonBusy(elements.saveTodoButton, false);
  }
}

async function handleTaskAction(event) {
  const actionButton = event.target.closest("[data-action]");
  const taskItem = event.target.closest(".task-item");
  if (!actionButton || !taskItem) {
    return;
  }

  const todoId = Number(taskItem.dataset.id);
  const todo = state.todos.find((item) => item.id === todoId);
  if (!todo) {
    return;
  }

  if (actionButton.dataset.action === "edit") {
    openEditTaskDialog(todo);
    return;
  }

  if (actionButton.dataset.action === "delete") {
    state.pendingDeleteId = todo.id;
    elements.confirmDialog.showModal();
    return;
  }

  if (actionButton.dataset.action === "toggle") {
    actionButton.disabled = true;
    try {
      const updated = await window.TodoApi.request(`/todos/${todo.id}`, {
        method: "PATCH",
        body: JSON.stringify({ completed: !todo.completed }),
      });
      replaceTodo(updated);
      renderTodos();
    } catch (error) {
      showToast(error.message, "error");
      actionButton.disabled = false;
    }
  }
}

async function confirmDelete() {
  const todoId = state.pendingDeleteId;
  if (!todoId) {
    return;
  }

  setButtonBusy(elements.confirmDeleteButton, true);
  try {
    await window.TodoApi.request(`/todos/${todoId}`, { method: "DELETE" });
    state.todos = state.todos.filter((todo) => todo.id !== todoId);
    state.pendingDeleteId = null;
    elements.confirmDialog.close();
    renderTodos();
    showToast("任务已删除。");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(elements.confirmDeleteButton, false);
  }
}

function replaceTodo(updatedTodo) {
  state.todos = state.todos.map((todo) =>
    todo.id === updatedTodo.id ? updatedTodo : todo,
  );
}

function updateTodayLabel() {
  elements.todayLabel.textContent = new Intl.DateTimeFormat("zh-CN", {
    month: "long",
    day: "numeric",
    weekday: "long",
  }).format(new Date());
}

function formatShortDate(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

function priorityLabel(priority) {
  return {
    low: "低优先级",
    medium: "中优先级",
    high: "高优先级",
  }[priority] || "中优先级";
}

function formatApiError(error) {
  if (Array.isArray(error.detail)) {
    return error.detail
      .map((item) => item.msg?.replace(/^Value error, /, "") || "输入内容无效")
      .join("；");
  }
  return error.message || "请求失败，请稍后重试。";
}

function setButtonBusy(button, isBusy) {
  button.disabled = isBusy;
  button.setAttribute("aria-busy", String(isBusy));
}

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  const icon = document.createElement("i");
  const copy = document.createElement("span");

  toast.className = `toast${type === "error" ? " is-error" : ""}`;
  icon.setAttribute("data-lucide", type === "error" ? "circle-alert" : "circle-check");
  copy.textContent = message;
  toast.append(icon, copy);
  elements.toastRegion.append(toast);
  refreshIcons();

  window.setTimeout(() => toast.remove(), 3600);
}

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons({
      attrs: {
        "stroke-width": 2,
      },
    });
  }
}

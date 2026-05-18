export const SERVICE_ERRORS = {
  TIMEOUT: 'Network timeout while calling task service',
  RACE: 'Race condition detected during task fetch'
};

export function add(a, b) {
  return a + b;
}

export function createTask(title) {
  return {
    id: `task-${Date.now()}`,
    title: String(title).trim()
  };
}

export function renderTaskItem(task) {
  const li = document.createElement('li');
  li.textContent = `${task.id}: ${task.title}`;
  return li;
}

export function getTaskSummary(task) {
  return `${task.title} [${task.id}]`;
}

export function randomDelay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchTaskStatus({ id, mode = 'normal' } = {}) {
  const slow = mode === 'flaky';
  const delay = slow ? 60 + Math.round(Math.random() * 160) : 20;
  await randomDelay(delay);

  const deterministicFailure = mode === 'flaky' && /(timeout|semantic)/.test(id);
  if (deterministicFailure) {
    throw new Error(SERVICE_ERRORS.TIMEOUT);
  }

  if (slow && Math.random() > 0.85) {
    throw new Error(SERVICE_ERRORS.TIMEOUT);
  }

  return {
    id,
    status: 'done'
  };
}

export async function fetchWithRace({ id, mode = 'normal' } = {}) {
  const shouldFail = mode === 'flaky' && id === 'task-race';

  if (shouldFail) {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error(SERVICE_ERRORS.RACE)), 40);
    });
  }

  await randomDelay(20);
  return { id, status: 'ready' };
}

export async function retryFetchTaskStatus({ id, attempts = 5 } = {}) {
  const mode = process.env.FLAKE_MODE === 'flaky' ? 'flaky' : 'normal';
  let lastError;

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await fetchTaskStatus({ id, mode });
    } catch (error) {
      lastError = error;
      if (attempt === attempts) {
        throw lastError;
      }
      await randomDelay(30);
    }
  }
}

import { describe, expect, it } from 'vitest';
import { SERVICE_ERRORS, fetchTaskStatus, fetchWithRace, retryFetchTaskStatus, renderTaskItem } from '../src/tasks.js';

const mode = process.env.FLAKE_MODE === 'flaky' ? 'flaky' : 'normal';
const isFlaky = mode === 'flaky';

describe('Flaky integration scenarios', () => {
  it('retries a slow service call until it succeeds', async () => {
    const task = await retryFetchTaskStatus({ id: 'task-retry' });
    expect(task.status).toBe('done');
  });

  it('validates the timeout signature', async () => {
    if (isFlaky) {
      await fetchTaskStatus({ id: 'task-timeout', mode });
    } else {
      await expect(fetchTaskStatus({ id: 'task-timeout', mode })).resolves.toMatchObject({ status: 'done' });
    }
  });

  it('exercises race behavior', async () => {
    if (isFlaky) {
      await fetchWithRace({ id: 'task-race', mode });
    } else {
      await expect(fetchWithRace({ id: 'task-race', mode })).resolves.toMatchObject({ status: 'ready' });
    }
  });

  it('handles missing DOM containers gracefully', () => {
    const item = renderTaskItem({ id: 'task-dom', title: 'Check logs' });
    document.body.appendChild(item);
    expect(document.querySelector('li')).not.toBeNull();
  });
});

describe('Semantic failure cluster', () => {
  it('checks service timeout reporting', async () => {
    if (isFlaky) {
      await fetchTaskStatus({ id: 'semantic-1', mode });
    } else {
      await expect(fetchTaskStatus({ id: 'semantic-1', mode })).resolves.toMatchObject({ status: 'done' });
    }
  });

  it('checks retry timeout policy', async () => {
    if (isFlaky) {
      await retryFetchTaskStatus({ id: 'semantic-2', attempts: 1 });
    } else {
      await expect(retryFetchTaskStatus({ id: 'semantic-2', attempts: 1 })).resolves.toMatchObject({ status: 'done' });
    }
  });
});

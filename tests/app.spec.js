import { describe, expect, it } from 'vitest';
import { add, createTask, getTaskSummary, renderTaskItem } from '../src/tasks.js';

describe('Core task helpers', () => {
  it('calculates totals correctly', () => {
    expect(add(3, 4)).toBe(7);
    expect(add(-1, 1)).toBe(0);
  });

  it('creates trimmed task objects', () => {
    const task = createTask('  Review Pull Request  ');
    expect(task.title).toBe('Review Pull Request');
    expect(task.id).toMatch(/^task-\d+$/);
  });

  it('builds readable task summaries', () => {
    const task = { id: 'task-123', title: 'Ship release' };
    expect(getTaskSummary(task)).toBe('Ship release [task-123]');
  });

  it('renders task items into DOM nodes', () => {
    const container = document.createElement('ul');
    const task = { id: 'task-321', title: 'Fix bug' };
    const item = renderTaskItem(task);

    container.appendChild(item);
    expect(container.innerHTML).toContain('task-321: Fix bug');
    expect(item.tagName).toBe('LI');
  });
});

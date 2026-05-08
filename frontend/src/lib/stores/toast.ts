import { writable } from 'svelte/store';
import type { Toast } from '$lib/types';

export const toasts = writable<Toast[]>([]);

export function addToast(message: string, type: Toast['type'] = 'info') {
	const id = crypto.randomUUID();
	toasts.update((all) => [...all, { id, message, type }]);
	setTimeout(() => {
		toasts.update((all) => all.filter((t) => t.id !== id));
	}, 4000);
}

export function removeToast(id: string) {
	toasts.update((all) => all.filter((t) => t.id !== id));
}

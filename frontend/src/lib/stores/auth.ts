import { writable } from 'svelte/store';
import { account } from '$lib/appwrite';
import type { Models } from 'appwrite';

export const user = writable<Models.User<Models.Preferences> | null>(null);
export const isLoading = writable(true);

export async function initAuth() {
	try {
		const current = await account.get();
		user.set(current);
	} catch {
		user.set(null);
	} finally {
		isLoading.set(false);
	}
}

export async function login(email: string, password: string) {
	const session = await account.createEmailPasswordSession(email, password);
	const current = await account.get();
	user.set(current);
	return session;
}

export async function register(email: string, password: string, name: string) {
	await account.create('unique()', email, password, name);
	return login(email, password);
}

export async function logout() {
	await account.deleteSession('current');
	user.set(null);
}

import { writable, get } from 'svelte/store';
import { account, databases, DB_ID, COLLECTIONS, Query } from '$lib/appwrite';
import type { Models } from 'appwrite';

export type UserRole = 'admin' | 'manager' | 'cuoco';

export const user = writable<Models.User<Models.Preferences> | null>(null);
export const userRole = writable<UserRole | null>(null);
export const isLoading = writable(true);

export async function initAuth() {
	try {
		const current = await account.get();
		user.set(current);
		await loadUserRole(current.$id);
	} catch {
		user.set(null);
		userRole.set(null);
	} finally {
		isLoading.set(false);
	}
}

async function loadUserRole(userId: string) {
	try {
		const res = await databases.listDocuments(DB_ID, COLLECTIONS.UTENTI_APP, [
			Query.equal('user_id', userId),
			Query.limit(1)
		]);
		if (res.documents.length > 0) {
			const doc = res.documents[0] as any;
			userRole.set(doc.ruolo as UserRole);
		} else {
			// Default role if no record found — first user gets admin
			userRole.set('admin');
		}
	} catch {
		userRole.set('admin');
	}
}

export function hasRole(required: UserRole[]): boolean {
	const current = get(userRole);
	if (!current) return false;
	return required.includes(current);
}

export function canEdit(): boolean {
	return hasRole(['admin', 'manager']);
}

export function canDelete(): boolean {
	return hasRole(['admin']);
}

export async function login(email: string, password: string) {
	const session = await account.createEmailPasswordSession(email, password);
	const current = await account.get();
	user.set(current);
	await loadUserRole(current.$id);
	return session;
}

export async function register(email: string, password: string, name: string) {
	await account.create('unique()', email, password, name);
	return login(email, password);
}

export async function logout() {
	await account.deleteSession('current');
	user.set(null);
	userRole.set(null);
}

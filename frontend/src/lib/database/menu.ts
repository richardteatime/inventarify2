import { databases, DB_ID, COLLECTIONS, ID, Query, DEFAULT_PERMISSIONS } from '$lib/appwrite';
import type { MenuItem } from '$lib/types';

export async function listMenu(): Promise<MenuItem[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.MENU, [
		Query.orderAsc('piatto'),
		Query.limit(500)
	]);
	return res.documents as unknown as MenuItem[];
}

export async function listPiatti(): Promise<string[]> {
	const items = await listMenu();
	return [...new Set(items.map(i => i.piatto))];
}

export async function getRicetta(piatto: string): Promise<MenuItem[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.MENU, [
		Query.equal('piatto', piatto)
	]);
	return res.documents as unknown as MenuItem[];
}

export async function createMenuItem(data: Omit<MenuItem, '$id'>): Promise<MenuItem> {
	const res = await databases.createDocument(DB_ID, COLLECTIONS.MENU, ID.unique(), data, DEFAULT_PERMISSIONS);
	return res as unknown as MenuItem;
}

export async function deleteMenuItem(id: string): Promise<void> {
	await databases.deleteDocument(DB_ID, COLLECTIONS.MENU, id);
}

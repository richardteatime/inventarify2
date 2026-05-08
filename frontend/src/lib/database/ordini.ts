import { databases, DB_ID, COLLECTIONS, ID, Query, DEFAULT_PERMISSIONS } from '$lib/appwrite';
import type { Ordine, OrdineItem } from '$lib/types';

export async function listOrdini(): Promise<Ordine[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.ORDINI, [
		Query.orderDesc('data_ordine'),
		Query.limit(500)
	]);
	return res.documents as unknown as Ordine[];
}

export async function getOrdine(id: string): Promise<Ordine> {
	const res = await databases.getDocument(DB_ID, COLLECTIONS.ORDINI, id);
	return res as unknown as Ordine;
}

export async function createOrdine(data: Omit<Ordine, '$id'>): Promise<Ordine> {
	const res = await databases.createDocument(DB_ID, COLLECTIONS.ORDINI, ID.unique(), data, DEFAULT_PERMISSIONS);
	return res as unknown as Ordine;
}

export async function updateOrdine(id: string, data: Partial<Ordine>): Promise<Ordine> {
	const res = await databases.updateDocument(DB_ID, COLLECTIONS.ORDINI, id, data);
	return res as unknown as Ordine;
}

export async function listOrdineItems(ordineId: string): Promise<OrdineItem[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.ORDINI_ITEMS, [
		Query.equal('ordine_id', ordineId),
		Query.limit(500)
	]);
	return res.documents as unknown as OrdineItem[];
}

export async function createOrdineItem(data: Omit<OrdineItem, '$id'>): Promise<OrdineItem> {
	const res = await databases.createDocument(DB_ID, COLLECTIONS.ORDINI_ITEMS, ID.unique(), data, DEFAULT_PERMISSIONS);
	return res as unknown as OrdineItem;
}

export async function updateOrdineItem(id: string, data: Partial<OrdineItem>): Promise<OrdineItem> {
	const res = await databases.updateDocument(DB_ID, COLLECTIONS.ORDINI_ITEMS, id, data);
	return res as unknown as OrdineItem;
}

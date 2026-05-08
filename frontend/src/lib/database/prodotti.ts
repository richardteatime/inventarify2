import { databases, DB_ID, COLLECTIONS, ID, Query } from '$lib/appwrite';
import type { Prodotto } from '$lib/types';

export async function listProdotti(): Promise<Prodotto[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.PRODOTTI, [
		Query.orderAsc('prodotto')
	]);
	return res.documents as unknown as Prodotto[];
}

export async function createProdotto(data: Omit<Prodotto, '$id'>): Promise<Prodotto> {
	const res = await databases.createDocument(DB_ID, COLLECTIONS.PRODOTTI, ID.unique(), data);
	return res as unknown as Prodotto;
}

export async function updateProdotto(id: string, data: Partial<Prodotto>): Promise<Prodotto> {
	const res = await databases.updateDocument(DB_ID, COLLECTIONS.PRODOTTI, id, data);
	return res as unknown as Prodotto;
}

export async function deleteProdotto(id: string): Promise<void> {
	await databases.deleteDocument(DB_ID, COLLECTIONS.PRODOTTI, id);
}

export async function updateQuantita(id: string, delta: number): Promise<Prodotto> {
	const doc = await databases.getDocument(DB_ID, COLLECTIONS.PRODOTTI, id);
	const nuova = (doc as any).quantità_attuale + delta;
	return updateProdotto(id, { quantità_attuale: Math.max(0, nuova) });
}

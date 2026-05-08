import { databases, DB_ID, COLLECTIONS, ID, Query } from '$lib/appwrite';
import type { Vendita, MenuItem, Consumo } from '$lib/types';

export async function listVendite(limit = 100): Promise<Vendita[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.VENDITE, [
		Query.orderDesc('data'),
		Query.limit(limit)
	]);
	return res.documents as unknown as Vendita[];
}

export async function createVendita(data: Omit<Vendita, '$id'>): Promise<Vendita> {
	const res = await databases.createDocument(DB_ID, COLLECTIONS.VENDITE, ID.unique(), data);
	return res as unknown as Vendita;
}

export async function createVenditeBatch(items: Omit<Vendita, '$id'>[]): Promise<void> {
	// Appwrite non ha batch insert nativo, facciamo Promise.all
	await Promise.all(items.map(item => createVendita(item)));
}

export async function deleteAllVendite(): Promise<void> {
	const vendite = await listVendite(10000);
	await Promise.all(vendite.map(v => 
		databases.deleteDocument(DB_ID, COLLECTIONS.VENDITE, v.$id!)
	));
}

export async function calcolaConsumi(vendite: Vendita[], menu: MenuItem[]): Promise<Consumo[]> {
	const consumi: Record<string, { data: string; quantità: number }> = {};

	for (const v of vendite) {
		const ricetta = menu.filter(m => m.piatto === v.piatto);
		for (const r of ricetta) {
			const key = `${v.data}_${r.prodotto}`;
			if (!consumi[key]) {
				consumi[key] = { data: v.data, quantità: 0 };
			}
			consumi[key].quantità += v.quantità_venduta * r.quantità_prodotto;
		}
	}

	return Object.entries(consumi).map(([key, val]) => ({
		data: val.data,
		prodotto: key.split('_')[1],
		quantità_consumata: val.quantità,
		fonte: 'vendita'
	}));
}

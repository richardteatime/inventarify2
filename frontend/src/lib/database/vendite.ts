import { databases, DB_ID, COLLECTIONS, ID, Query, DEFAULT_PERMISSIONS } from '$lib/appwrite';
import type { Vendita, MenuItem, Consumo, Prodotto } from '$lib/types';

export async function listVendite(limit = 100): Promise<Vendita[]> {
	const res = await databases.listDocuments(DB_ID, COLLECTIONS.VENDITE, [
		Query.orderDesc('data'),
		Query.limit(limit)
	]);
	return res.documents as unknown as Vendita[];
}

export async function createVendita(data: Omit<Vendita, '$id'>): Promise<Vendita> {
	const res = await databases.createDocument(DB_ID, COLLECTIONS.VENDITE, ID.unique(), data, DEFAULT_PERMISSIONS);
	return res as unknown as Vendita;
}

export async function createVenditeBatch(items: Omit<Vendita, '$id'>[]): Promise<void> {
	await Promise.all(items.map(item => createVendita(item)));
}

export async function deleteAllVendite(): Promise<void> {
	const vendite = await listVendite(10000);
	await Promise.all(vendite.map(v => 
		databases.deleteDocument(DB_ID, COLLECTIONS.VENDITE, v.$id!)
	));
}

export async function calcolaConsumi(
	vendite: Vendita[],
	menu: MenuItem[],
	prodotti: Prodotto[]
): Promise<Consumo[]> {
	const prodottiByName = new Map(prodotti.map(p => [p.prodotto, p]));
	const consumi: Record<string, { data: string; prodotto_id: string; prodotto_nome: string; quantita: number }> = {};

	for (const v of vendite) {
		const ricetta = menu.filter(m => m.piatto === v.piatto);
		for (const r of ricetta) {
			// Preferisci prodotto_id se disponibile, altrimenti risolvi per nome
			let pid = r.prodotto_id;
			let nome = r.prodotto;
			if (!pid) {
				const p = prodottiByName.get(r.prodotto);
				if (p?.$id) {
					pid = p.$id;
				}
			}
			if (!pid) continue; // Salta se non riusciamo a risolvere l'ID

			const key = `${v.data}_${pid}`;
			if (!consumi[key]) {
				consumi[key] = { data: v.data, prodotto_id: pid, prodotto_nome: nome, quantita: 0 };
			}
			consumi[key].quantita += v.quantita_venduta * r.quantita_prodotto;
		}
	}

	return Object.values(consumi).map(c => ({
		data: c.data,
		prodotto: c.prodotto_nome,
		prodotto_id: c.prodotto_id,
		quantita_consumata: c.quantita,
		fonte: 'vendita'
	}));
}

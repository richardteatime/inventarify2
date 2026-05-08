import { Client, Account, Databases, Storage, ID, Query, Permission, Role } from 'appwrite';
import { PUBLIC_APPWRITE_ENDPOINT, PUBLIC_APPWRITE_PROJECT, PUBLIC_APPWRITE_DATABASE_ID } from '$env/static/public';

export const client = new Client()
	.setEndpoint(PUBLIC_APPWRITE_ENDPOINT)
	.setProject(PUBLIC_APPWRITE_PROJECT);

export const account = new Account(client);
export const databases = new Databases(client);
export const storage = new Storage(client);

export { ID, Query, Permission, Role };

// Collection IDs
export const DB_ID = PUBLIC_APPWRITE_DATABASE_ID;

export const COLLECTIONS = {
	PRODOTTI: 'prodotti',
	MENU: 'menu',
	VENDITE: 'vendite',
	ORDINI: 'ordini',
	ORDINI_ITEMS: 'ordini_items',
	CONSUMI: 'consumi',
	UTENTI_APP: 'utenti_app'
} as const;

// Bucket IDs
export const BUCKETS = {
	VENDITE_CSV: 'vendite-csv',
	ORDINI_CSV: 'ordini-csv'
} as const;

// Default permissions for shared data
export const DEFAULT_PERMISSIONS = [
	Permission.read(Role.users()),
	Permission.update(Role.users()),
	Permission.delete(Role.users())
];

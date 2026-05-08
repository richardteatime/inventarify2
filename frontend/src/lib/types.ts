export interface Prodotto {
	$id?: string;
	prodotto: string;
	quantità_attuale: number;
	unità: string;
	soglia_riordino: number;
	fornitore?: string;
	costo_unitario?: number;
	note?: string;
}

export interface MenuItem {
	$id?: string;
	piatto: string;
	prodotto: string;
	quantità_prodotto: number;
	porzione_default?: number;
}

export interface Vendita {
	$id?: string;
	data: string;
	piatto: string;
	quantità_venduta: number;
	turno?: 'pranzo' | 'cena';
}

export interface Ordine {
	$id?: string;
	data_ordine: string;
	fornitore?: string;
	stato: 'bozza' | 'inviato' | 'consegnato' | 'parziale';
	note?: string;
}

export interface OrdineItem {
	$id?: string;
	ordine_id: string;
	prodotto: string;
	quantità_ordinata: number;
	quantità_ricevuta: number;
	ricevuto: boolean;
}

export interface Consumo {
	$id?: string;
	data: string;
	prodotto: string;
	quantità_consumata: number;
	fonte: string;
}

export interface UserApp {
	$id?: string;
	user_id: string;
	ruolo: 'admin' | 'manager' | 'cuoco';
	ristorante_nome?: string;
	telefono?: string;
}

export interface Toast {
	id: string;
	message: string;
	type: 'success' | 'error' | 'info';
}

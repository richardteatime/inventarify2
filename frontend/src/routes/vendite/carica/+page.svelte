<script lang="ts">
	import { goto } from '$app/navigation';
	import { createVenditeBatch, calcolaConsumi } from '$lib/database/vendite';
	import { listMenu } from '$lib/database/menu';
	import { listProdotti, updateProdotto } from '$lib/database/prodotti';
	import { databases, DB_ID, COLLECTIONS, ID } from '$lib/appwrite';
	import { addToast } from '$lib/stores/toast';
	import type { Vendita, MenuItem, Prodotto } from '$lib/types';
	import Papa from 'papaparse';

	let file: File | null = null;
	let preview: Vendita[] = [];
	let loading = false;
	let step: 'upload' | 'preview' | 'done' = 'upload';

	function handleFile(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files && input.files[0]) {
			file = input.files[0];
			parseCSV();
		}
	}

	function parseCSV() {
		if (!file) return;
		Papa.parse(file, {
			header: true,
			skipEmptyLines: true,
			complete: (results) => {
				const headers = results.meta.fields || [];
				const required = ['data', 'piatto', 'quantita_venduta'];
				const missing = required.filter(r => !headers.includes(r));
				if (missing.length > 0) {
					addToast(`Colonne mancanti: ${missing.join(', ')}`, 'error');
					file = null;
					return;
				}

				preview = results.data
					.filter((row: any) => row.piatto && row.data)
					.map((row: any) => ({
						data: String(row.data).trim(),
						piatto: String(row.piatto).trim(),
						quantita_venduta: Math.max(0, parseFloat(String(row.quantita_venduta).trim()) || 0),
						turno: ['pranzo', 'cena'].includes(String(row.turno).trim().toLowerCase())
							? (String(row.turno).trim().toLowerCase() as 'pranzo' | 'cena')
							: undefined
					}));

				if (preview.length === 0) {
					addToast('Nessuna riga valida trovata nel CSV', 'error');
					file = null;
					return;
				}

				step = 'preview';
			},
			error: (err: any) => {
				addToast(`Errore parsing CSV: ${err.message}`, 'error');
				file = null;
			}
		});
	}

	async function handleConfirm() {
		loading = true;
		try {
			// 1. Create vendite
			await createVenditeBatch(preview.map(v => ({
				data: v.data,
				piatto: v.piatto,
				quantita_venduta: v.quantita_venduta,
				turno: v.turno
			})));

			// 2. Calculate consumi
			const menu = await listMenu();
			const prodotti = await listProdotti();
			const consumi = await calcolaConsumi(preview, menu, prodotti);

			// 3. Save consumi + update stock
			const prodottiMapById = new Map(prodotti.map(p => [p.$id!, p]));

			for (const c of consumi) {
				// Save consumo
				await databases.createDocument(DB_ID, COLLECTIONS.CONSUMI, ID.unique(), c);

				// Update stock by prodotto_id
				if (c.prodotto_id) {
					const prodotto = prodottiMapById.get(c.prodotto_id);
					if (prodotto) {
						const nuovaQty = Math.max(0, prodotto.quantita_attuale - c.quantita_consumata);
						await updateProdotto(prodotto.$id!, { quantita_attuale: nuovaQty });
					}
				}
			}

			addToast(`${preview.length} vendite caricate, ${consumi.length} consumi calcolati, stock aggiornato`, 'success');
			step = 'done';
		} catch (e: any) {
			addToast(e.message || 'Errore caricamento', 'error');
		} finally {
			loading = false;
		}
	}

	function handleReset() {
		file = null;
		preview = [];
		step = 'upload';
	}
</script>

<svelte:head>
	<title>Carica Vendite — Inventarify</title>
</svelte:head>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">Carica Vendite</h1>
	<p class="text-body-md text-shade-50">Importa un file CSV con le vendite giornaliere</p>
</div>

{#if step === 'upload'}
	<div class="card-pricing shadow-level-3 text-center py-xxl">
		<div class="w-16 h-16 mx-auto mb-lg rounded-full bg-canvas-cream flex items-center justify-center text-display-md font-display text-shade-40">
			CSV
		</div>
		<h3 class="font-display text-heading-lg text-ink mb-sm">Trascina o seleziona un file CSV</h3>
		<p class="text-body-md text-shade-50 mb-lg max-w-md mx-auto">
			Il file deve contenere le colonne: <code class="bg-canvas-cream px-xs py-xxs rounded-xs text-caption">data, piatto, quantita_venduta</code>
		</p>
		<label class="btn-primary-pill cursor-pointer inline-block">
			<input type="file" accept=".csv" class="hidden" on:change={handleFile} />
			Seleziona file CSV
		</label>
	</div>
{:else if step === 'preview'}
	<div class="card-pricing shadow-level-3 mb-lg">
		<div class="flex items-center justify-between mb-md">
			<h3 class="font-display text-heading-lg text-ink">Anteprima ({preview.length} righe)</h3>
			<button on:click={handleReset} class="text-caption text-shade-50 hover:text-ink">Annulla</button>
		</div>
		<div class="max-h-80 overflow-auto rounded-lg border border-hairline-light mb-lg">
			<table class="w-full">
				<thead class="bg-canvas-cream sticky top-0">
					<tr>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Data</th>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Piatto</th>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Q.ta</th>
					</tr>
				</thead>
				<tbody>
					{#each preview.slice(0, 20) as v}
						<tr class="border-b border-hairline-light last:border-0">
							<td class="px-md py-sm text-body-md">{v.data}</td>
							<td class="px-md py-sm text-body-md">{v.piatto}</td>
							<td class="px-md py-sm text-body-md">{v.quantita_venduta}</td>
						</tr>
					{/each}
				</tbody>
			</table>
			{#if preview.length > 20}
				<div class="text-center py-sm text-caption text-shade-50">
					...e altre {preview.length - 20} righe
				</div>
			{/if}
		</div>
		<button on:click={handleConfirm} disabled={loading} class="btn-primary-pill disabled:opacity-50 disabled:cursor-not-allowed">
			{loading ? 'Caricamento...' : `Conferma e carica ${preview.length} vendite`}
		</button>
	</div>
{:else if step === 'done'}
	<div class="card-pricing shadow-level-3 text-center py-xxl">
		<h3 class="font-display text-heading-lg text-ink mb-sm">Vendite caricate</h3>
		<p class="text-body-md text-shade-50 mb-lg">I consumi sono stati calcolati e il magazzino aggiornato automaticamente.</p>
		<div class="flex gap-sm justify-center">
			<button on:click={handleReset} class="btn-outline-on-light">Carica altro</button>
			<a href="/magazzino" class="btn-primary-pill text-no-underline">Vai al magazzino</a>
		</div>
	</div>
{/if}

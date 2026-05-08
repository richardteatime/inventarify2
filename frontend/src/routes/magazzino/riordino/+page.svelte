<script lang="ts">
	import { onMount } from 'svelte';
	import { listProdotti } from '$lib/database/prodotti';
	import { createOrdine, createOrdineItem } from '$lib/database/ordini';
	import { addToast } from '$lib/stores/toast';
	import { canEdit } from '$lib/stores/auth';
	import { subscribeToChanges } from '$lib/realtime';
	import { COLLECTIONS } from '$lib/appwrite';
	import { goto } from '$app/navigation';
	import type { Prodotto } from '$lib/types';

	let prodotti: Prodotto[] = [];
	let loading = true;
	let actionLoading = false;
	let fornitore = '';

	onMount(() => {
		loadData();
		const unsub = subscribeToChanges([COLLECTIONS.PRODOTTI], () => loadData());
		return unsub;
	});

	async function loadData() {
		try {
			const all = await listProdotti();
			prodotti = all.filter(p => p.quantita_attuale < p.soglia_riordino);
		} catch (e) {
			addToast('Errore caricamento', 'error');
		} finally {
			loading = false;
		}
	}

	function quantitaSuggerita(p: Prodotto): number {
		const diff = p.soglia_riordino - p.quantita_attuale;
		return Math.max(1, Math.ceil(diff));
	}

	async function generaOrdine() {
		if (prodotti.length === 0) return;
		actionLoading = true;
		try {
			const ordine = await createOrdine({
				data_ordine: new Date().toISOString(),
				fornitore: fornitore || undefined,
				stato: 'bozza',
				note: ''
			});

			for (const p of prodotti) {
				await createOrdineItem({
					ordine_id: ordine.$id!,
					prodotto: p.prodotto,
					prodotto_id: p.$id,
					quantita_ordinata: quantitaSuggerita(p),
					quantita_ricevuta: 0,
					ricevuto: false
				});
			}

			addToast(`Ordine #${ordine.$id?.slice(-6)} creato con ${prodotti.length} prodotti`, 'success');
			goto('/ordini');
		} catch (e: any) {
			addToast(e.message || 'Errore creazione ordine', 'error');
		} finally {
			actionLoading = false;
		}
	}

	function exportCSV() {
		const rows = prodotti.map(p => ({
			prodotto: p.prodotto,
			quantita: quantitaSuggerita(p)
		}));
		const csv = [
			'prodotto,quantita',
			...rows.map(r => `${r.prodotto},${r.quantita}`)
		].join('\n');
		const blob = new Blob([csv], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `prodotti_da_riordinare_${new Date().toISOString().slice(0,10)}.csv`;
		a.click();
		URL.revokeObjectURL(url);
		addToast('CSV scaricato', 'success');
	}
</script>

<svelte:head>
	<title>Riordino — Inventarify</title>
</svelte:head>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">Prodotti da Riordinare</h1>
	<p class="text-body-md text-shade-50">Prodotti sotto la soglia di riordino</p>
</div>

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else if prodotti.length === 0}
	<div class="card-pricing shadow-level-3 text-center py-xxl">
		<h2 class="font-display text-heading-lg text-ink mb-sm">Tutto a posto</h2>
		<p class="text-body-md text-shade-50">Nessun prodotto sotto la soglia di riordino</p>
		<a href="/magazzino" class="btn-primary-pill inline-block mt-lg">Torna al magazzino</a>
	</div>
{:else}
	<div class="card-pistachio-band mb-lg border border-hairline-light">
		<div class="flex items-center justify-between mb-md">
			<h2 class="font-display text-heading-lg text-ink">{prodotti.length} prodotti sotto soglia</h2>
			<span class="pill-tag-danger">Critico</span>
		</div>

		<div class="bg-canvas-light rounded-lg border border-hairline-light overflow-hidden mb-lg">
			<table class="w-full">
				<thead class="bg-canvas-cream border-b border-hairline-light">
					<tr>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Prodotto</th>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Attuale</th>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Soglia</th>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Unità</th>
						<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Quantità da ordinare</th>
					</tr>
				</thead>
				<tbody>
					{#each prodotti as p}
						<tr class="border-b border-hairline-light last:border-0">
							<td class="px-md py-sm text-body-md text-ink font-medium">{p.prodotto}</td>
							<td class="px-md py-sm text-body-md text-red-600 font-medium">{p.quantita_attuale}</td>
							<td class="px-md py-sm text-body-md text-shade-60">{p.soglia_riordino}</td>
							<td class="px-md py-sm text-body-md text-shade-60">{p.unita}</td>
							<td class="px-md py-sm text-body-md text-ink font-medium">{quantitaSuggerita(p)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="flex flex-col sm:flex-row gap-sm">
			<input
				bind:value={fornitore}
				placeholder="Fornitore (opzionale)"
				class="input-text max-w-xs"
			/>
			{#if canEdit()}
				<button on:click={generaOrdine} disabled={actionLoading} class="btn-primary-pill disabled:opacity-50">
					{actionLoading ? 'Generazione...' : 'Genera ordine in app'}
				</button>
			{/if}
			<button on:click={exportCSV} class="btn-outline-on-light">
				Scarica CSV
			</button>
		</div>
	</div>
{/if}

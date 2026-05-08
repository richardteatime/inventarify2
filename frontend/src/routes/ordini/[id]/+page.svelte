<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getOrdine, listOrdineItems, updateOrdine, updateOrdineItem } from '$lib/database/ordini';
	import { updateProdotto } from '$lib/database/prodotti';
	import { listProdotti } from '$lib/database/prodotti';
	import { addToast } from '$lib/stores/toast';
	import type { Ordine, OrdineItem, Prodotto } from '$lib/types';

	const id = $page.params.id;

	let ordine: Ordine | null = null;
	let items: OrdineItem[] = [];
	let prodotti: Prodotto[] = [];
	let loading = true;

	onMount(loadData);

	async function loadData() {
		try {
			[ordine, items] = await Promise.all([
				getOrdine(id),
				listOrdineItems(id)
			]);
			prodotti = await listProdotti();
		} catch (e) {
			addToast('Errore caricamento ordine', 'error');
		} finally {
			loading = false;
		}
	}

	async function toggleRicevuto(item: OrdineItem) {
		try {
			await updateOrdineItem(item.$id!, {
				ricevuto: !item.ricevuto,
				quantità_ricevuta: !item.ricevuto ? item.quantità_ordinata : 0
			});
			await loadData();
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	async function aggiornaMagazzino() {
		try {
			const ricevuti = items.filter(i => i.ricevuto);
			for (const item of ricevuti) {
				const prodotto = prodotti.find(p => p.prodotto === item.prodotto);
				if (prodotto?.$id) {
					await updateProdotto(prodotto.$id, {
						quantità_attuale: prodotto.quantità_attuale + (item.quantità_ricevuta || item.quantità_ordinata)
					});
				}
			}
			await updateOrdine(id, { stato: 'consegnato' });
			addToast('Magazzino aggiornato con successo!', 'success');
			await loadData();
		} catch (e: any) {
			addToast(e.message || 'Errore aggiornamento', 'error');
		}
	}

	async function cambiaStato(nuovo: Ordine['stato']) {
		try {
			await updateOrdine(id, { stato: nuovo });
			await loadData();
			addToast(`Stato aggiornato a: ${nuovo}`, 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	const statoLabels: Record<string, string> = {
		bozza: 'Bozza',
		inviato: 'Inviato',
		consegnato: 'Consegnato',
		parziale: 'Parziale'
	};
</script>

<svelte:head>
	<title>Ordine #{id.slice(-6)} — Inventarify</title>
</svelte:head>

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else if ordine}
	<div class="mb-xxl">
		<div class="flex items-center gap-sm mb-sm">
			<h1 class="font-display text-display-md text-ink">Ordine #{id.slice(-6)}</h1>
			<span class="pill-tag-shade">
				{statoLabels[ordine.stato]}
			</span>
		</div>
		<p class="text-body-md text-shade-50">
			{new Date(ordine.data_ordine).toLocaleDateString('it-IT')}
			{#if ordine.fornitore} · {ordine.fornitore}{/if}
		</p>
	</div>

	<!-- Azioni stato -->
	<div class="flex flex-wrap gap-sm mb-lg">
		{#if ordine.stato === 'bozza'}
			<button on:click={() => cambiaStato('inviato')} class="btn-primary-pill">📤 Segna come inviato</button>
		{:else if ordine.stato === 'inviato'}
			<button on:click={() => cambiaStato('parziale')} class="btn-aloe-pill">📦 Ricezione parziale</button>
		{/if}
		{#if ordine.stato !== 'consegnato' && ordine.stato !== 'bozza'}
			<button on:click={aggiornaMagazzino} class="btn-primary-pill">✓ Aggiorna magazzino</button>
		{/if}
		{#if ordine.stato === 'consegnato'}
			<span class="pill-tag-mint">Ordine completato</span>
		{/if}
	</div>

	<!-- Checklist -->
	<div class="card-pricing shadow-level-3">
		<h3 class="font-display text-heading-md text-ink mb-lg">🧾 Checklist Ricezione</h3>
		<div class="space-y-sm">
			{#each items as item}
				<div class="flex items-center gap-md p-md rounded-md border border-hairline-light transition-colors"
					class:bg-aloe-10={item.ricevuto}
					class:bg-canvas-light={!item.ricevuto}
				>
					<input
						type="checkbox"
						checked={item.ricevuto}
						on:change={() => toggleRicevuto(item)}
						class="w-5 h-5 accent-ink cursor-pointer"
					/>
					<div class="flex-1">
						<div class="text-body-md text-ink font-medium">{item.prodotto}</div>
						<div class="text-caption text-shade-50">
							Ordinato: {item.quantità_ordinata}
							{#if item.quantità_ricevuta > 0} · Ricevuto: {item.quantità_ricevuta}{/if}
						</div>
					</div>
					{#if item.ricevuto}
						<span class="pill-tag-mint">Ricevuto</span>
					{:else}
						<span class="pill-tag-shade">In attesa</span>
					{/if}
				</div>
			{/each}
		</div>
	</div>
{:else}
	<div class="card-pricing shadow-level-3 text-center py-xxl">
		<h2 class="font-display text-heading-lg text-ink mb-sm">Ordine non trovato</h2>
		<a href="/ordini" class="btn-primary-pill text-no-underline">Torna agli ordini</a>
	</div>
{/if}

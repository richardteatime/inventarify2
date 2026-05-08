<script lang="ts">
	import { onMount } from 'svelte';
	import { listOrdini, listOrdineItems } from '$lib/database/ordini';
	import { addToast } from '$lib/stores/toast';
	import type { Ordine, OrdineItem } from '$lib/types';

	let ordini: (Ordine & { items?: OrdineItem[] })[] = [];
	let loading = true;

	onMount(loadData);

	async function loadData() {
		try {
			const list = await listOrdini();
			ordini = await Promise.all(list.map(async o => {
				const items = await listOrdineItems(o.$id!);
				return { ...o, items };
			}));
		} catch (e) {
			addToast('Errore caricamento ordini', 'error');
		} finally {
			loading = false;
		}
	}

	const statoColors: Record<string, string> = {
		bozza: 'bg-shade-30 text-ink',
		inviato: 'bg-link-mint text-ink',
		consegnato: 'bg-aloe-10 text-ink',
		parziale: 'bg-pistachio-10 text-ink'
	};

	const statoLabels: Record<string, string> = {
		bozza: 'Bozza',
		inviato: 'Inviato',
		consegnato: 'Consegnato',
		parziale: 'Parziale'
	};
</script>

<svelte:head>
	<title>Ordini — Inventarify</title>
</svelte:head>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">📋 Ordini</h1>
	<p class="text-body-md text-shade-50">Gestisci ordini a fornitori e ricezione merce</p>
</div>

<div class="mb-lg">
	<a href="/magazzino/riordino" class="btn-primary-pill text-no-underline">+ Nuovo ordine da riordino</a>
</div>

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else}
	<div class="space-y-lg">
		{#each ordini as o}
			<div class="card-pricing shadow-level-3">
				<div class="flex flex-col sm:flex-row sm:items-center justify-between mb-md gap-sm">
					<div>
						<div class="flex items-center gap-sm mb-xs">
							<h3 class="font-display text-heading-lg text-ink">Ordine #{o.$id?.slice(-6)}</h3>
							<span class="pill-tag-shade {statoColors[o.stato]}">{statoLabels[o.stato]}</span>
						</div>
						<p class="text-caption text-shade-50">
							{new Date(o.data_ordine).toLocaleDateString('it-IT')}
							{#if o.fornitore} · Fornitore: {o.fornitore}{/if}
						</p>
					</div>
					{#if o.stato !== 'consegnato'}
						<a href="/ordini/{o.$id}" class="btn-aloe-pill text-no-underline text-center">
							{o.stato === 'bozza' ? 'Modifica / Invia' : 'Gestisci ricezione'}
						</a>
					{:else}
						<span class="pill-tag-mint">Completato</span>
					{/if}
				</div>

				{#if o.items && o.items.length > 0}
					<table class="w-full">
						<thead class="border-b border-hairline-light">
							<tr>
								<th class="text-left text-caption text-shade-50 py-sm font-medium">Prodotto</th>
								<th class="text-left text-caption text-shade-50 py-sm font-medium">Ordinato</th>
								<th class="text-left text-caption text-shade-50 py-sm font-medium">Ricevuto</th>
								<th class="text-left text-caption text-shade-50 py-sm font-medium">Stato</th>
							</tr>
						</thead>
						<tbody>
							{#each o.items as item}
								<tr class="border-b border-hairline-light last:border-0">
									<td class="py-sm text-body-md text-ink">{item.prodotto}</td>
									<td class="py-sm text-body-md text-shade-60">{item.quantita_ordinata}</td>
									<td class="py-sm text-body-md text-shade-60">{item.quantita_ricevuta}</td>
									<td class="py-sm">
										{#if item.ricevuto}
											<span class="pill-tag-mint">✓</span>
										{:else}
											<span class="pill-tag-shade">In attesa</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{/if}
			</div>
		{/each}

		{#if ordini.length === 0}
			<div class="card-pricing shadow-level-3 text-center py-xxl">
				<div class="text-display-md mb-sm">📭</div>
				<h3 class="font-display text-heading-lg text-ink mb-sm">Nessun ordine</h3>
				<p class="text-body-md text-shade-50 mb-lg">Crea il tuo primo ordine dalla pagina riordino</p>
				<a href="/magazzino/riordino" class="btn-primary-pill text-no-underline">Vai a riordino</a>
			</div>
		{/if}
	</div>
{/if}

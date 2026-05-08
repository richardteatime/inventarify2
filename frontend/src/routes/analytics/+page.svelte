<script lang="ts">
	import { onMount } from 'svelte';
	import { listVendite } from '$lib/database/vendite';
	import { listProdotti } from '$lib/database/prodotti';
	import { listMenu } from '$lib/database/menu';
	import { addToast } from '$lib/stores/toast';
	import type { Vendita, Prodotto, MenuItem } from '$lib/types';

	let vendite: Vendita[] = [];
	let prodotti: Prodotto[] = [];
	let menu: MenuItem[] = [];
	let loading = true;

	onMount(async () => {
		try {
			[vendite, prodotti, menu] = await Promise.all([
				listVendite(1000),
				listProdotti(),
				listMenu()
			]);
		} catch (e) {
			addToast('Errore caricamento dati', 'error');
		} finally {
			loading = false;
		}
	});

	// KPI
	$: totaleVendite = vendite.reduce((s, v) => s + v.quantita_venduta, 0);
	$: piattiUnici = new Set(vendite.map(v => v.piatto)).size;
	$: prodottiCritici = prodotti.filter(p => p.quantita_attuale < p.soglia_riordino).length;

	// Top piatti
	$: topPiatti = Object.entries(
		vendite.reduce<Record<string, number>>((acc, v) => {
			acc[v.piatto] = (acc[v.piatto] || 0) + v.quantita_venduta;
			return acc;
		}, {})
	)
		.sort((a, b) => b[1] - a[1])
		.slice(0, 10);

	// Consumo ingredienti
	$: consumi = vendite.flatMap(v => {
		const ricetta = menu.filter(m => m.piatto === v.piatto);
		return ricetta.map(r => ({
			prodotto: r.prodotto,
			quantità: v.quantita_venduta * r.quantita_prodotto
		}));
	});

	$: consumiAggregati = Object.entries(
		consumi.reduce<Record<string, number>>((acc, c) => {
			acc[c.prodotto] = (acc[c.prodotto] || 0) + c.quantità;
			return acc;
		}, {})
	)
		.sort((a, b) => b[1] - a[1])
		.slice(0, 10);

	// Vendite per giorno (ultimi 14 giorni)
	$: venditePerGiorno = Object.entries(
		vendite.reduce<Record<string, number>>((acc, v) => {
			acc[v.data] = (acc[v.data] || 0) + v.quantita_venduta;
			return acc;
		}, {})
	)
		.sort((a, b) => a[0].localeCompare(b[0]))
		.slice(-14);

	// Max per normalizzare barre
	$: maxConsumo = consumiAggregati.length > 0 ? consumiAggregati[0][1] : 1;
	$: maxPiatto = topPiatti.length > 0 ? topPiatti[0][1] : 1;
	$: maxGiorno = venditePerGiorno.length > 0 ? Math.max(...venditePerGiorno.map(x => x[1])) : 1;
</script>

<svelte:head>
	<title>Analytics — Inventarify</title>
</svelte:head>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm"> Analytics</h1>
	<p class="text-body-md text-shade-50">Report vendite, consumi e trend</p>
</div>

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else}
	<!-- KPI Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-xl mb-xxl">
		<div class="card-pricing shadow-level-3">
			<div class="pill-tag-mint w-fit mb-md">Vendite totali</div>
			<div class="font-display text-display-md text-ink">{totaleVendite}</div>
			<p class="text-caption text-shade-50 mt-xs">piatti venduti</p>
		</div>
		<div class="card-pricing shadow-level-3">
			<div class="pill-tag-shade w-fit mb-md">Piatti in carta</div>
			<div class="font-display text-display-md text-ink">{piattiUnici}</div>
			<p class="text-caption text-shade-50 mt-xs">diversi venduti</p>
		</div>
		<div class="card-pricing shadow-level-3">
			<div class="pill-tag-danger w-fit mb-md">Prodotti critici</div>
			<div class="font-display text-display-md text-ink">{prodottiCritici}</div>
			<p class="text-caption text-shade-50 mt-xs">sotto soglia</p>
		</div>
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-2 gap-xl">
		<!-- Top Piatti -->
		<div class="card-pricing shadow-level-3">
			<h3 class="font-display text-heading-lg text-ink mb-lg"> Piatti più venduti</h3>
			<div class="space-y-sm">
				{#each topPiatti as [piatto, qty]}
					<div class="flex items-center gap-sm">
						<span class="text-body-md text-ink w-48 truncate flex-shrink-0">{piatto}</span>
						<div class="flex-1 h-2 bg-canvas-cream rounded-pill overflow-hidden">
							<div class="h-full bg-ink rounded-pill transition-all" style="width: {(qty / maxPiatto) * 100}%"></div>
						</div>
						<span class="text-caption text-shade-50 w-10 text-right">{qty}</span>
					</div>
				{/each}
				{#if topPiatti.length === 0}
					<p class="text-shade-50 text-body-md text-center py-lg">Nessuna vendita</p>
				{/if}
			</div>
		</div>

		<!-- Consumo Ingredienti -->
		<div class="card-pricing shadow-level-3">
			<h3 class="font-display text-heading-lg text-ink mb-lg"> Ingredienti più consumati</h3>
			<div class="space-y-sm">
				{#each consumiAggregati as [prodotto, qty]}
					<div class="flex items-center gap-sm">
						<span class="text-body-md text-ink w-48 truncate flex-shrink-0">{prodotto}</span>
						<div class="flex-1 h-2 bg-canvas-cream rounded-pill overflow-hidden">
							<div class="h-full bg-aloe-10 rounded-pill transition-all" style="width: {(qty / maxConsumo) * 100}%"></div>
						</div>
						<span class="text-caption text-shade-50 w-14 text-right">{qty.toFixed(1)}</span>
					</div>
				{/each}
				{#if consumiAggregati.length === 0}
					<p class="text-shade-50 text-body-md text-center py-lg">Nessun dato</p>
				{/if}
			</div>
		</div>

		<!-- Vendite per giorno -->
		<div class="card-pricing shadow-level-3 lg:col-span-2">
			<h3 class="font-display text-heading-lg text-ink mb-lg"> Vendite giornaliere</h3>
			<div class="flex items-end gap-xs h-48">
				{#each venditePerGiorno as [giorno, qty]}
					<div class="flex-1 flex flex-col items-center gap-xs group">
						<div class="text-caption text-shade-50 opacity-0 group-hover:opacity-100 transition-opacity">{qty}</div>
						<div 
							class="w-full bg-ink rounded-t-xs transition-all hover:bg-shade-70"
							style="height: {(qty / maxGiorno) * 100}%"
						></div>
						<div class="text-micro text-shade-50 -rotate-45 origin-top-left translate-y-4">{giorno.slice(5)}</div>
					</div>
				{/each}
				{#if venditePerGiorno.length === 0}
					<p class="text-shade-50 text-body-md text-center w-full py-lg">Nessun dato</p>
				{/if}
			</div>
		</div>
	</div>
{/if}

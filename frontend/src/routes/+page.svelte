<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores/auth';
	import { databases, DB_ID, COLLECTIONS, Query } from '$lib/appwrite';
	import { listPiatti } from '$lib/database/menu';
	import { addToast } from '$lib/stores/toast';
	import { subscribeToChanges } from '$lib/realtime';
	import type { Prodotto, Vendita } from '$lib/types';

	let prodotti: Prodotto[] = [];
	let vendite: Vendita[] = [];
	let piatti: string[] = [];
	let loading = true;

	onMount(() => {
		if (!$user) return;
		loadData();
		const unsub = subscribeToChanges(
			[COLLECTIONS.PRODOTTI, COLLECTIONS.VENDITE],
			() => loadData()
		);
		return unsub;
	});

	async function loadData() {
		try {
			const [prodRes, vendRes, piattiRes] = await Promise.all([
				databases.listDocuments(DB_ID, COLLECTIONS.PRODOTTI, [Query.limit(500)]),
				databases.listDocuments(DB_ID, COLLECTIONS.VENDITE, [Query.limit(500)]),
				listPiatti()
			]);
			prodotti = prodRes.documents as unknown as Prodotto[];
			vendite = vendRes.documents as unknown as Vendita[];
			piatti = piattiRes;
		} catch (e) {
			addToast('Errore caricamento dashboard', 'error');
		} finally {
			loading = false;
		}
	}

	$: prodottiSottoSoglia = prodotti.filter(p => p.quantita_attuale < p.soglia_riordino);
	$: totaleVendite = vendite.reduce((sum, v) => sum + v.quantita_venduta, 0);
	$: piattiUnici = piatti.length;
</script>

<svelte:head>
	<title>Dashboard — Inventarify</title>
</svelte:head>

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento dashboard...</div>
{:else}
	<!-- Header -->
	<div class="mb-xxl">
		<h1 class="font-display text-display-md text-ink mb-sm">Dashboard</h1>
		<p class="text-body-md text-shade-50">Panoramica del tuo ristorante in tempo reale</p>
	</div>

	<!-- KPI Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-xl mb-xxl">
		<div class="card-pricing shadow-level-3">
			<div class="pill-tag-mint w-fit mb-md">Prodotti</div>
			<div class="font-display text-display-md text-ink">{prodotti.length}</div>
			<p class="text-caption text-shade-50 mt-xs">in magazzino</p>
		</div>

		<div class="card-pricing shadow-level-3">
			<div class="pill-tag-shade w-fit mb-md">Vendite</div>
			<div class="font-display text-display-md text-ink">{totaleVendite}</div>
			<p class="text-caption text-shade-50 mt-xs">piatti venduti totali</p>
		</div>

		<div class="card-pricing shadow-level-3">
			<div class="pill-tag-mint w-fit mb-md">Menu</div>
			<div class="font-display text-display-md text-ink">{piattiUnici}</div>
			<p class="text-caption text-shade-50 mt-xs">piatti in carta</p>
		</div>
	</div>

	<!-- Alert Section -->
	{#if prodottiSottoSoglia.length > 0}
		<div class="card-pistachio-band mb-xxl border border-hairline-light">
			<div class="flex items-center justify-between mb-md">
				<h2 class="font-display text-heading-lg text-ink">Prodotti sotto soglia</h2>
				<span class="pill-tag-danger">{prodottiSottoSoglia.length} critici</span>
			</div>
			<div class="space-y-sm">
				{#each prodottiSottoSoglia as p}
					<div class="flex items-center justify-between bg-canvas-light rounded-md px-md py-sm border border-hairline-light">
						<span class="text-body-md text-ink font-medium">{p.prodotto}</span>
						<span class="text-caption text-shade-50">
							{p.quantita_attuale} {p.unita} / soglia {p.soglia_riordino} {p.unita}
						</span>
					</div>
				{/each}
			</div>
			<a href="/magazzino/riordino" class="btn-primary-pill inline-block mt-lg">Genera ordine riordino</a>
		</div>
	{:else}
		<div class="card-pricing shadow-level-3 mb-xxl text-center py-xxl">
			<h2 class="font-display text-heading-lg text-ink mb-sm">Tutto a posto</h2>
			<p class="text-body-md text-shade-50">Nessun prodotto sotto la soglia di riordino</p>
		</div>
	{/if}

	<!-- Quick Actions -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-xl">
		<a href="/vendite/carica" class="card-pricing shadow-level-3 hover:shadow-level-4 transition-shadow duration-200 block no-underline">
			<div class="pill-tag-mint w-fit mb-md">Azione rapida</div>
			<h3 class="font-display text-heading-lg text-ink mb-sm">Carica vendite</h3>
			<p class="text-body-md text-shade-50">Importa il CSV delle vendite giornaliere per aggiornare i consumi automaticamente.</p>
		</a>

		<a href="/ordini" class="card-pricing shadow-level-3 hover:shadow-level-4 transition-shadow duration-200 block no-underline">
			<div class="pill-tag-shade w-fit mb-md">Gestione</div>
			<h3 class="font-display text-heading-lg text-ink mb-sm">Gestisci ordini</h3>
			<p class="text-body-md text-shade-50">Controlla lo stato degli ordini e aggiorna l'inventario alla ricezione della merce.</p>
		</a>
	</div>
{/if}

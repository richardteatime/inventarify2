<script lang="ts">
	import { onMount } from 'svelte';
	import { listProdotti, createProdotto, updateProdotto, deleteProdotto } from '$lib/database/prodotti';
	import { addToast } from '$lib/stores/toast';
	import type { Prodotto } from '$lib/types';

	let prodotti: Prodotto[] = [];
	let loading = true;
	let search = '';
	let editingId: string | null = null;

	// Form nuovo prodotto
	let showForm = false;
	let newProdotto: Omit<Prodotto, '$id'> = {
		prodotto: '',
		quantità_attuale: 0,
		unità: 'kg',
		soglia_riordino: 0,
		fornitore: '',
		costo_unitario: 0,
		note: ''
	};

	onMount(loadData);

	async function loadData() {
		try {
			prodotti = await listProdotti();
		} catch (e) {
			addToast('Errore caricamento magazzino', 'error');
		} finally {
			loading = false;
		}
	}

	async function handleCreate() {
		try {
			await createProdotto(newProdotto);
			addToast('Prodotto aggiunto', 'success');
			newProdotto = { prodotto: '', quantità_attuale: 0, unità: 'kg', soglia_riordino: 0, fornitore: '', costo_unitario: 0, note: '' };
			showForm = false;
			await loadData();
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	async function handleUpdate(id: string, data: Partial<Prodotto>) {
		try {
			await updateProdotto(id, data);
			editingId = null;
			await loadData();
			addToast('Prodotto aggiornato', 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	async function handleDelete(id: string) {
		if (!confirm('Eliminare questo prodotto?')) return;
		try {
			await deleteProdotto(id);
			await loadData();
			addToast('Prodotto eliminato', 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	$: filtered = prodotti.filter(p => 
		p.prodotto.toLowerCase().includes(search.toLowerCase())
	);
	$: sottoSoglia = filtered.filter(p => p.quantità_attuale < p.soglia_riordino);
</script>

<svelte:head>
	<title>Magazzino — Inventarify</title>
</svelte:head>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">📦 Magazzino</h1>
	<p class="text-body-md text-shade-50">Gestisci prodotti, scorte e soglie di riordino</p>
</div>

<!-- Actions bar -->
<div class="flex flex-col sm:flex-row gap-md mb-lg items-start sm:items-center justify-between">
	<input
		type="text"
		bind:value={search}
		placeholder="Cerca prodotto..."
		class="input-text max-w-xs"
	/>
	<div class="flex gap-sm">
		<a href="/magazzino/riordino" class="btn-aloe-pill text-no-underline">
			📥 Prodotti sotto soglia ({sottoSoglia.length})
		</a>
		<button on:click={() => showForm = !showForm} class="btn-primary-pill">
			{showForm ? 'Annulla' : '+ Nuovo prodotto'}
		</button>
	</div>
</div>

<!-- Form nuovo prodotto -->
{#if showForm}
	<div class="card-pricing shadow-level-3 mb-lg">
		<h3 class="font-display text-heading-md text-ink mb-lg">Nuovo prodotto</h3>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-md">
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Nome</label>
				<input bind:value={newProdotto.prodotto} class="input-text" placeholder="es. Pomodori" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Quantità</label>
				<input type="number" step="0.01" bind:value={newProdotto.quantità_attuale} class="input-text" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Unità</label>
				<select bind:value={newProdotto.unità} class="input-text">
					<option>kg</option>
					<option>litri</option>
					<option>botteglie</option>
					<option>pz</option>
					<option>confezioni</option>
				</select>
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Soglia riordino</label>
				<input type="number" step="0.01" bind:value={newProdotto.soglia_riordino} class="input-text" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Fornitore</label>
				<input bind:value={newProdotto.fornitore} class="input-text" placeholder="es. Rossi Srl" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Costo unitario (€)</label>
				<input type="number" step="0.01" bind:value={newProdotto.costo_unitario} class="input-text" />
			</div>
		</div>
		<button on:click={handleCreate} class="btn-primary-pill mt-lg">Salva prodotto</button>
	</div>
{/if}

<!-- Tabella -->
{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else}
	<div class="bg-canvas-light rounded-lg border border-hairline-light overflow-hidden">
		<table class="w-full">
			<thead class="bg-canvas-cream border-b border-hairline-light">
				<tr>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Prodotto</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Quantità</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Unità</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Soglia</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Stato</th>
					<th class="text-right text-caption text-shade-50 px-md py-sm font-medium">Azioni</th>
				</tr>
			</thead>
			<tbody>
				{#each filtered as p}
					<tr class="border-b border-hairline-light last:border-0 hover:bg-canvas-cream transition-colors">
						<td class="px-md py-sm">
							{#if editingId === p.$id}
								<input bind:value={p.prodotto} class="input-text text-body-md py-xs px-sm" />
							{:else}
								<span class="text-body-md text-ink font-medium">{p.prodotto}</span>
							{/if}
						</td>
						<td class="px-md py-sm">
							{#if editingId === p.$id}
								<input type="number" step="0.01" bind:value={p.quantità_attuale} class="input-text text-body-md py-xs px-sm w-24" />
							{:else}
								<span class="text-body-md text-ink">{p.quantità_attuale}</span>
							{/if}
						</td>
						<td class="px-md py-sm text-body-md text-shade-60">{p.unità}</td>
						<td class="px-md py-sm text-body-md text-shade-60">{p.soglia_riordino}</td>
						<td class="px-md py-sm">
							{#if p.quantità_attuale < p.soglia_riordino}
								<span class="pill-tag-danger">Sotto soglia</span>
							{:else}
								<span class="pill-tag-mint">OK</span>
							{/if}
						</td>
						<td class="px-md py-sm text-right">
							{#if editingId === p.$id}
								<button on:click={() => handleUpdate(p.$id!, { quantità_attuale: p.quantità_attuale, prodotto: p.prodotto })} class="text-caption text-aloe-10 hover:text-ink mr-sm">✓</button>
								<button on:click={() => editingId = null} class="text-caption text-shade-50 hover:text-ink">✕</button>
							{:else}
								<button on:click={() => editingId = p.$id!} class="text-caption text-shade-50 hover:text-ink mr-sm">✏️</button>
								<button on:click={() => handleDelete(p.$id!)} class="text-caption text-shade-50 hover:text-red-600">🗑️</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if filtered.length === 0}
			<div class="text-center py-xxl text-shade-50 text-body-md">
				Nessun prodotto trovato
			</div>
		{/if}
	</div>
{/if}

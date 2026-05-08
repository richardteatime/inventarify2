<script lang="ts">
	import { onMount } from 'svelte';
	import { listMenu, listPiatti, createMenuItem, deleteMenuItem, getRicetta } from '$lib/database/menu';
	import { addToast } from '$lib/stores/toast';
	import type { MenuItem } from '$lib/types';

	let menu: MenuItem[] = [];
	let piatti: string[] = [];
	let loading = true;
	let selectedPiatto = '';
	let showForm = false;

	let newItem: Omit<MenuItem, '$id'> = {
		piatto: '',
		prodotto: '',
		quantita_prodotto: 0,
		porzione_default: 1
	};

	onMount(loadData);

	async function loadData() {
		try {
			[menu, piatti] = await Promise.all([listMenu(), listPiatti()]);
		} catch (e) {
			addToast('Errore caricamento menu', 'error');
		} finally {
			loading = false;
		}
	}

	async function handleCreate() {
		try {
			await createMenuItem(newItem);
			addToast('Ingrediente aggiunto alla ricetta', 'success');
			newItem = { piatto: newItem.piatto, prodotto: '', quantita_prodotto: 0, porzione_default: 1 };
			await loadData();
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	async function handleDelete(id: string) {
		if (!confirm('Rimuovere questo ingrediente?')) return;
		try {
			await deleteMenuItem(id);
			await loadData();
			addToast('Ingrediente rimosso', 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		}
	}

	$: grouped = menu.reduce<Record<string, MenuItem[]>>((acc, item) => {
		if (!acc[item.piatto]) acc[item.piatto] = [];
		acc[item.piatto].push(item);
		return acc;
	}, {});

	$: piattiList = selectedPiatto ? [selectedPiatto] : Object.keys(grouped).sort();
</script>

<svelte:head>
	<title>Menu — Inventarify</title>
</svelte:head>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">🍽️ Menu / Ricette</h1>
	<p class="text-body-md text-shade-50">Associa piatti e ingredienti per il calcolo automatico consumi</p>
</div>

<div class="flex flex-col sm:flex-row gap-md mb-lg items-start sm:items-center justify-between">
	<select bind:value={selectedPiatto} class="input-text max-w-xs">
		<option value="">Tutti i piatti</option>
		{#each piatti as p}
			<option>{p}</option>
		{/each}
	</select>
	<button on:click={() => showForm = !showForm} class="btn-primary-pill">
		{showForm ? 'Annulla' : '+ Aggiungi ingrediente'}
	</button>
</div>

{#if showForm}
	<div class="card-pricing shadow-level-3 mb-lg">
		<h3 class="font-display text-heading-md text-ink mb-lg">Nuovo ingrediente</h3>
		<div class="grid grid-cols-1 sm:grid-cols-4 gap-md">
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Piatto</label>
				<input bind:value={newItem.piatto} list="piatti-list" class="input-text" placeholder="Nome piatto" />
				<datalist id="piatti-list">
					{#each piatti as p}
						<option>{p}</option>
					{/each}
				</datalist>
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Prodotto</label>
				<input bind:value={newItem.prodotto} class="input-text" placeholder="es. Pomodori" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Quantità / porzione</label>
				<input type="number" step="0.001" bind:value={newItem.quantita_prodotto} class="input-text" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Unità</label>
				<input bind:value={newItem.porzione_default} class="input-text" placeholder="1" />
			</div>
		</div>
		<button on:click={handleCreate} class="btn-primary-pill mt-lg">Salva ingrediente</button>
	</div>
{/if}

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else}
	<div class="space-y-lg">
		{#each piattiList as piatto}
			<div class="card-pricing shadow-level-3">
				<div class="flex items-center justify-between mb-md">
					<h3 class="font-display text-heading-lg text-ink">{piatto}</h3>
					<span class="pill-tag-shade">{grouped[piatto].length} ingredienti</span>
				</div>
				<table class="w-full">
					<thead class="border-b border-hairline-light">
						<tr>
							<th class="text-left text-caption text-shade-50 py-sm font-medium">Prodotto</th>
							<th class="text-left text-caption text-shade-50 py-sm font-medium">Quantità / porzione</th>
							<th class="text-right text-caption text-shade-50 py-sm font-medium"></th>
						</tr>
					</thead>
					<tbody>
						{#each grouped[piatto] as item}
							<tr class="border-b border-hairline-light last:border-0">
								<td class="py-sm text-body-md text-ink">{item.prodotto}</td>
								<td class="py-sm text-body-md text-shade-60">{item.quantita_prodotto}</td>
								<td class="py-sm text-right">
									<button on:click={() => handleDelete(item.$id!)} class="text-caption text-shade-50 hover:text-red-600">🗑️</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/each}
	</div>
{/if}

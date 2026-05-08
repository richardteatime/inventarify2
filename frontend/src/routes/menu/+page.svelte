<script lang="ts">
	import { onMount } from 'svelte';
	import { listMenu, listPiatti, createMenuItem, deleteMenuItem } from '$lib/database/menu';
	import { listProdotti } from '$lib/database/prodotti';
	import { addToast } from '$lib/stores/toast';
	import { canEdit } from '$lib/stores/auth';
	import { subscribeToChanges } from '$lib/realtime';
	import { COLLECTIONS } from '$lib/appwrite';
	import ConfirmModal from '$lib/components/ui/ConfirmModal.svelte';
	import type { MenuItem, Prodotto } from '$lib/types';

	let menu: MenuItem[] = [];
	let piatti: string[] = [];
	let prodotti: Prodotto[] = [];
	let loading = true;
	let actionLoading = false;
	let selectedPiatto = '';
	let showForm = false;
	let formErrors: Record<string, string> = {};

	let deleteModalOpen = false;
	let deleteTargetId: string | null = null;

	let newItem: Omit<MenuItem, '$id'> = {
		piatto: '',
		prodotto: '',
		prodotto_id: '',
		quantita_prodotto: 0,
		porzione_default: 1
	};

	onMount(() => {
		loadData();
		const unsub = subscribeToChanges([COLLECTIONS.MENU], () => loadData());
		return unsub;
	});

	async function loadData() {
		try {
			[menu, piatti, prodotti] = await Promise.all([
				listMenu(),
				listPiatti(),
				listProdotti()
			]);
		} catch (e) {
			addToast('Errore caricamento menu', 'error');
		} finally {
			loading = false;
		}
	}

	function validateItem(data: Partial<MenuItem>): boolean {
		formErrors = {};
		if (!data.piatto || data.piatto.trim().length < 2) {
			formErrors.piatto = 'Nome piatto obbligatorio (min 2 caratteri)';
		}
		if (!data.prodotto_id) {
			formErrors.prodotto_id = 'Seleziona un prodotto';
		}
		if (data.quantita_prodotto === undefined || data.quantita_prodotto <= 0) {
			formErrors.quantita_prodotto = 'Quantità deve essere maggiore di 0';
		}
		return Object.keys(formErrors).length === 0;
	}

	function onSelectProdotto(e: Event) {
		const select = e.target as HTMLSelectElement;
		const pid = select.value;
		const p = prodotti.find(x => x.$id === pid);
		newItem.prodotto_id = pid;
		newItem.prodotto = p ? p.prodotto : '';
	}

	async function handleCreate() {
		if (!validateItem(newItem)) return;
		actionLoading = true;
		try {
			await createMenuItem(newItem);
			addToast('Ingrediente aggiunto alla ricetta', 'success');
			newItem = { piatto: newItem.piatto, prodotto: '', prodotto_id: '', quantita_prodotto: 0, porzione_default: 1 };
			await loadData();
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		} finally {
			actionLoading = false;
		}
	}

	function requestDelete(id: string) {
		deleteTargetId = id;
		deleteModalOpen = true;
	}

	async function confirmDelete() {
		if (!deleteTargetId) return;
		actionLoading = true;
		try {
			await deleteMenuItem(deleteTargetId);
			await loadData();
			addToast('Ingrediente rimosso', 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		} finally {
			actionLoading = false;
			deleteTargetId = null;
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

<ConfirmModal
	open={deleteModalOpen}
	title="Rimuovi ingrediente"
	message="Rimuovere questo ingrediente dalla ricetta?"
	confirmText="Rimuovi"
	cancelText="Annulla"
	danger={true}
	on:confirm={confirmDelete}
	on:cancel={() => deleteModalOpen = false}
/>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">Menu / Ricette</h1>
	<p class="text-body-md text-shade-50">Associa piatti e ingredienti per il calcolo automatico consumi</p>
</div>

<div class="flex flex-col sm:flex-row gap-md mb-lg items-start sm:items-center justify-between">
	<select bind:value={selectedPiatto} class="input-text max-w-xs">
		<option value="">Tutti i piatti</option>
		{#each piatti as p}
			<option>{p}</option>
		{/each}
	</select>
	{#if canEdit()}
		<button on:click={() => showForm = !showForm} class="btn-primary-pill">
			{showForm ? 'Annulla' : '+ Aggiungi ingrediente'}
		</button>
	{/if}
</div>

{#if showForm && canEdit()}
	<div class="card-pricing shadow-level-3 mb-lg">
		<h3 class="font-display text-heading-md text-ink mb-lg">Nuovo ingrediente</h3>
		<div class="grid grid-cols-1 sm:grid-cols-4 gap-md">
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Piatto *</label>
				<input bind:value={newItem.piatto} list="piatti-list" class="input-text" placeholder="Nome piatto" />
				<datalist id="piatti-list">
					{#each piatti as p}
						<option>{p}</option>
					{/each}
				</datalist>
				{#if formErrors.piatto}<span class="text-caption text-red-600 mt-xs">{formErrors.piatto}</span>{/if}
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Prodotto *</label>
				<select on:change={onSelectProdotto} class="input-text" value={newItem.prodotto_id}>
					<option value="">Seleziona prodotto</option>
					{#each prodotti as p}
						<option value={p.$id}>{p.prodotto} ({p.unita})</option>
					{/each}
				</select>
				{#if formErrors.prodotto_id}<span class="text-caption text-red-600 mt-xs">{formErrors.prodotto_id}</span>{/if}
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Quantità / porzione *</label>
				<input type="number" step="0.001" min="0.001" bind:value={newItem.quantita_prodotto} class="input-text" />
				{#if formErrors.quantita_prodotto}<span class="text-caption text-red-600 mt-xs">{formErrors.quantita_prodotto}</span>{/if}
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Unità</label>
				<input bind:value={newItem.porzione_default} class="input-text" placeholder="1" />
			</div>
		</div>
		<button on:click={handleCreate} disabled={actionLoading} class="btn-primary-pill mt-lg disabled:opacity-50">
			{actionLoading ? 'Salvataggio...' : 'Salva ingrediente'}
		</button>
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
							{#if canEdit()}
								<th class="text-right text-caption text-shade-50 py-sm font-medium"></th>
							{/if}
						</tr>
					</thead>
					<tbody>
						{#each grouped[piatto] as item}
							<tr class="border-b border-hairline-light last:border-0">
								<td class="py-sm text-body-md text-ink">{item.prodotto}</td>
								<td class="py-sm text-body-md text-shade-60">{item.quantita_prodotto}</td>
								{#if canEdit()}
									<td class="py-sm text-right">
										<button on:click={() => requestDelete(item.$id!)} class="text-caption text-red-500 hover:text-red-700 font-medium">Elimina</button>
									</td>
								{/if}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/each}
	</div>
{/if}

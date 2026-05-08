<script lang="ts">
	import { onMount } from 'svelte';
	import { listProdotti, createProdotto, updateProdotto, deleteProdotto } from '$lib/database/prodotti';
	import { addToast } from '$lib/stores/toast';
	import { canEdit, canDelete } from '$lib/stores/auth';
	import { subscribeToChanges } from '$lib/realtime';
	import { COLLECTIONS } from '$lib/appwrite';
	import ConfirmModal from '$lib/components/ui/ConfirmModal.svelte';
	import type { Prodotto } from '$lib/types';

	let prodotti: Prodotto[] = [];
	let loading = true;
	let actionLoading = false;
	let search = '';
	let editingId: string | null = null;
	let editBuffer: Partial<Prodotto> = {};

	// Delete modal
	let deleteModalOpen = false;
	let deleteTargetId: string | null = null;

	// Form nuovo prodotto
	let showForm = false;
	let formErrors: Record<string, string> = {};
	let newProdotto: Omit<Prodotto, '$id'> = {
		prodotto: '',
		quantita_attuale: 0,
		unita: 'kg',
		soglia_riordino: 0,
		fornitore: '',
		costo_unitario: 0,
		note: ''
	};

	onMount(() => {
		loadData();
		const unsub = subscribeToChanges([COLLECTIONS.PRODOTTI], () => {
			if (!editingId) loadData();
		});
		return unsub;
	});

	async function loadData() {
		try {
			prodotti = await listProdotti();
		} catch (e) {
			addToast('Errore caricamento magazzino', 'error');
		} finally {
			loading = false;
		}
	}

	function validateProdotto(data: Partial<Prodotto>): boolean {
		formErrors = {};
		if (!data.prodotto || data.prodotto.trim().length < 2) {
			formErrors.prodotto = 'Nome prodotto obbligatorio (min 2 caratteri)';
		}
		if (data.quantita_attuale !== undefined && data.quantita_attuale < 0) {
			formErrors.quantita_attuale = 'Quantità non può essere negativa';
		}
		if (data.soglia_riordino !== undefined && data.soglia_riordino < 0) {
			formErrors.soglia_riordino = 'Soglia non può essere negativa';
		}
		return Object.keys(formErrors).length === 0;
	}

	async function handleCreate() {
		if (!validateProdotto(newProdotto)) return;
		actionLoading = true;
		try {
			await createProdotto(newProdotto);
			addToast('Prodotto aggiunto', 'success');
			newProdotto = { prodotto: '', quantita_attuale: 0, unita: 'kg', soglia_riordino: 0, fornitore: '', costo_unitario: 0, note: '' };
			showForm = false;
			await loadData();
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		} finally {
			actionLoading = false;
		}
	}

	function startEdit(p: Prodotto) {
		editingId = p.$id!;
		editBuffer = {
			prodotto: p.prodotto,
			quantita_attuale: p.quantita_attuale,
		};
	}

	function cancelEdit() {
		editingId = null;
		editBuffer = {};
	}

	async function handleSaveEdit(id: string) {
		if (!validateProdotto(editBuffer)) return;
		actionLoading = true;
		try {
			await updateProdotto(id, editBuffer);
			editingId = null;
			editBuffer = {};
			await loadData();
			addToast('Prodotto aggiornato', 'success');
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
			await deleteProdotto(deleteTargetId);
			await loadData();
			addToast('Prodotto eliminato', 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		} finally {
			actionLoading = false;
			deleteTargetId = null;
		}
	}

	$: filtered = prodotti.filter(p =>
		p.prodotto.toLowerCase().includes(search.toLowerCase())
	);
	$: sottoSoglia = filtered.filter(p => p.quantita_attuale < p.soglia_riordino);
</script>

<svelte:head>
	<title>Magazzino — Inventarify</title>
</svelte:head>

<ConfirmModal
	open={deleteModalOpen}
	title="Elimina prodotto"
	message="Eliminare questo prodotto? L'azione non può essere annullata."
	confirmText="Elimina"
	cancelText="Annulla"
	danger={true}
	on:confirm={confirmDelete}
	on:cancel={() => deleteModalOpen = false}
/>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">Magazzino</h1>
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
			Prodotti sotto soglia ({sottoSoglia.length})
		</a>
		{#if $canEdit}
			<button on:click={() => showForm = !showForm} class="btn-primary-pill">
				{showForm ? 'Annulla' : '+ Nuovo prodotto'}
			</button>
		{/if}
	</div>
</div>

<!-- Form nuovo prodotto -->
{#if showForm && $canEdit}
	<div class="card-pricing shadow-level-3 mb-lg">
		<h3 class="font-display text-heading-md text-ink mb-lg">Nuovo prodotto</h3>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-md">
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Nome *</label>
				<input bind:value={newProdotto.prodotto} class="input-text" placeholder="es. Pomodori" />
				{#if formErrors.prodotto}<span class="text-caption text-red-600 mt-xs">{formErrors.prodotto}</span>{/if}
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Quantità *</label>
				<input type="number" step="0.01" min="0" bind:value={newProdotto.quantita_attuale} class="input-text" />
				{#if formErrors.quantita_attuale}<span class="text-caption text-red-600 mt-xs">{formErrors.quantita_attuale}</span>{/if}
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Unità</label>
				<select bind:value={newProdotto.unita} class="input-text">
					<option>kg</option>
					<option>litri</option>
					<option>botteglie</option>
					<option>pz</option>
					<option>confezioni</option>
				</select>
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Soglia riordino *</label>
				<input type="number" step="0.01" min="0" bind:value={newProdotto.soglia_riordino} class="input-text" />
				{#if formErrors.soglia_riordino}<span class="text-caption text-red-600 mt-xs">{formErrors.soglia_riordino}</span>{/if}
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Fornitore</label>
				<input bind:value={newProdotto.fornitore} class="input-text" placeholder="es. Rossi Srl" />
			</div>
			<div>
				<label class="text-caption text-shade-50 block mb-xs">Costo unitario (€)</label>
				<input type="number" step="0.01" min="0" bind:value={newProdotto.costo_unitario} class="input-text" />
			</div>
		</div>
		<button on:click={handleCreate} disabled={actionLoading} class="btn-primary-pill mt-lg disabled:opacity-50">
			{actionLoading ? 'Salvataggio...' : 'Salva prodotto'}
		</button>
	</div>
{/if}

<!-- Tabella -->
{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else}
	<div class="bg-canvas-light rounded-lg border border-hairline-light overflow-x-auto">
		<table class="w-full min-w-[600px]">
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
								<input bind:value={editBuffer.prodotto} class="input-text text-body-md py-xs px-sm" />
							{:else}
								<span class="text-body-md text-ink font-medium">{p.prodotto}</span>
							{/if}
						</td>
						<td class="px-md py-sm">
							{#if editingId === p.$id}
								<input type="number" step="0.01" min="0" bind:value={editBuffer.quantita_attuale} class="input-text text-body-md py-xs px-sm w-24" />
							{:else}
								<span class="text-body-md text-ink">{p.quantita_attuale}</span>
							{/if}
						</td>
						<td class="px-md py-sm text-body-md text-shade-60">{p.unita}</td>
						<td class="px-md py-sm text-body-md text-shade-60">{p.soglia_riordino}</td>
						<td class="px-md py-sm">
							{#if p.quantita_attuale < p.soglia_riordino}
								<span class="pill-tag-danger">Sotto soglia</span>
							{:else}
								<span class="pill-tag-mint">OK</span>
							{/if}
						</td>
						<td class="px-md py-sm text-right">
							{#if editingId === p.$id}
								<button on:click={() => handleSaveEdit(p.$id!)} disabled={actionLoading} class="text-caption text-aloe-10 hover:text-ink mr-sm font-medium">Salva</button>
								<button on:click={cancelEdit} class="text-caption text-shade-50 hover:text-ink font-medium">Annulla</button>
							{:else}
								{#if $canEdit}
									<button on:click={() => startEdit(p)} class="text-caption text-shade-50 hover:text-ink mr-sm font-medium">Modifica</button>
								{/if}
								{#if $canDelete}
									<button on:click={() => requestDelete(p.$id!)} class="text-caption text-red-500 hover:text-red-700 font-medium">Elimina</button>
								{/if}
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

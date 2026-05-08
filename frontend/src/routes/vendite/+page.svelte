<script lang="ts">
	import { onMount } from 'svelte';
	import { listVendite, deleteAllVendite } from '$lib/database/vendite';
	import { addToast } from '$lib/stores/toast';
	import ConfirmModal from '$lib/components/ui/ConfirmModal.svelte';
	import type { Vendita } from '$lib/types';

	let vendite: Vendita[] = [];
	let loading = true;
	let actionLoading = false;
	let resetModalOpen = false;

	onMount(loadData);

	async function loadData() {
		try {
			vendite = await listVendite(200);
		} catch (e) {
			addToast('Errore caricamento vendite', 'error');
		} finally {
			loading = false;
		}
	}

	async function handleReset() {
		actionLoading = true;
		try {
			await deleteAllVendite();
			await loadData();
			addToast('Vendite eliminate', 'success');
		} catch (e: any) {
			addToast(e.message || 'Errore', 'error');
		} finally {
			actionLoading = false;
			resetModalOpen = false;
		}
	}
</script>

<svelte:head>
	<title>Vendite — Inventarify</title>
</svelte:head>

<ConfirmModal
	open={resetModalOpen}
	title="Elimina tutte le vendite"
	message="Eliminare TUTTE le vendite? Questo non può essere annullato. Il magazzino NON verrà ripristinato automaticamente."
	confirmText="Elimina tutto"
	cancelText="Annulla"
	danger={true}
	on:confirm={handleReset}
	on:cancel={() => resetModalOpen = false}
/>

<div class="mb-xxl">
	<h1 class="font-display text-display-md text-ink mb-sm">Storico Vendite</h1>
	<p class="text-body-md text-shade-50">Visualizza e gestisci le vendite caricate</p>
</div>

<div class="flex flex-col sm:flex-row gap-sm mb-lg justify-between items-start sm:items-center">
	<a href="/vendite/carica" class="btn-primary-pill text-no-underline">Carica nuove vendite</a>
	<button on:click={() => resetModalOpen = true} disabled={actionLoading} class="btn-outline-on-light disabled:opacity-50">
		Reset tutte le vendite
	</button>
</div>

{#if loading}
	<div class="text-shade-50 text-body-md">Caricamento...</div>
{:else}
	<div class="bg-canvas-light rounded-lg border border-hairline-light overflow-x-auto">
		<table class="w-full min-w-[500px]">
			<thead class="bg-canvas-cream border-b border-hairline-light">
				<tr>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Data</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Piatto</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Quantità</th>
					<th class="text-left text-caption text-shade-50 px-md py-sm font-medium">Turno</th>
				</tr>
			</thead>
			<tbody>
				{#each vendite as v}
					<tr class="border-b border-hairline-light last:border-0 hover:bg-canvas-cream transition-colors">
						<td class="px-md py-sm text-body-md text-shade-60">{v.data}</td>
						<td class="px-md py-sm text-body-md text-ink font-medium">{v.piatto}</td>
						<td class="px-md py-sm text-body-md text-ink">{v.quantita_venduta}</td>
						<td class="px-md py-sm">
							{#if v.turno}
								<span class="pill-tag-shade">{v.turno}</span>
							{:else}
								<span class="text-caption text-shade-40">—</span>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if vendite.length === 0}
			<div class="text-center py-xxl text-shade-50 text-body-md">
				Nessuna vendita registrata
			</div>
		{/if}
	</div>
{/if}

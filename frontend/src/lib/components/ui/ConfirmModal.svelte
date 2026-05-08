<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let open = false;
	export let title = 'Conferma';
	export let message = 'Sei sicuro?';
	export let confirmText = 'Conferma';
	export let cancelText = 'Annulla';
	export let danger = false;

	const dispatch = createEventDispatcher();

	function confirm() {
		open = false;
		dispatch('confirm');
	}

	function cancel() {
		open = false;
		dispatch('cancel');
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') cancel();
	}
</script>

<svelte:window on:keydown={handleKeydown}/>

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center px-lg">
		<!-- Backdrop -->
		<div class="absolute inset-0 bg-canvas-night/50" on:click={cancel}></div>

		<!-- Modal -->
		<div class="relative bg-canvas-light rounded-lg shadow-level-4 w-full max-w-md p-xxl">
			<h3 class="font-display text-heading-xl text-ink mb-sm">{title}</h3>
			<p class="text-body-md text-shade-60 mb-lg">{message}</p>

			<div class="flex gap-sm justify-end">
				<button on:click={cancel} class="btn-outline-on-light">
					{cancelText}
				</button>
				<button on:click={confirm} class={danger ? 'btn-primary-pill bg-red-600 hover:bg-red-700' : 'btn-primary-pill'}>
					{confirmText}
				</button>
			</div>
		</div>
	</div>
{/if}

<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Toast } from '$lib/types';

	export let toast: Toast;

	const dispatch = createEventDispatcher();

	const colors = {
		success: 'bg-aloe-10 text-ink border-hairline-light',
		error: 'bg-red-50 text-red-700 border-red-200',
		info: 'bg-canvas-light text-ink border-hairline-light'
	};

	const icons = {
		success: '✅',
		error: '❌',
		info: 'ℹ️'
	};
</script>

<div class="flex items-center gap-sm px-md py-sm rounded-lg border shadow-level-3 min-w-[280px] {colors[toast.type]}">
	<span class="text-body-md">{icons[toast.type]}</span>
	<span class="text-body-md flex-1">{toast.message}</span>
	<button
		on:click={() => dispatch('dismiss')}
		class="text-shade-50 hover:text-ink transition-colors text-caption"
	>
		✕
	</button>
</div>

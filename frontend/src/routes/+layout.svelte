<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { user, isLoading, initAuth, logout } from '$lib/stores/auth';
	import { toasts, removeToast } from '$lib/stores/toast';
	import Toast from '$lib/components/ui/Toast.svelte';

	onMount(() => {
		initAuth();
	});

	$: if (!$isLoading && !$user && $page.url.pathname !== '/login') {
		goto('/login');
	}

	const navItems = [
		{ label: ' Dashboard', href: '/' },
		{ label: ' Magazzino', href: '/magazzino' },
		{ label: ' Menu', href: '/menu' },
		{ label: ' Vendite', href: '/vendite' },
		{ label: ' Ordini', href: '/ordini' },
		{ label: ' Analytics', href: '/analytics' },
	];

	function isActive(href: string) {
		return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
	}

	async function handleLogout() {
		await logout();
		goto('/login');
	}
</script>

{#if $isLoading}
	<div class="min-h-screen flex items-center justify-center bg-canvas-cream">
		<div class="text-shade-50 text-body-md">Caricamento...</div>
	</div>
{:else if $user}
	<div class="min-h-screen flex">
		<!-- Sidebar -->
		<aside class="w-64 bg-canvas-light border-r border-hairline-light flex flex-col sticky top-0 h-screen">
			<div class="px-xl py-lg border-b border-hairline-light">
				<h1 class="font-display text-heading-lg text-ink tracking-wide">Inventarify</h1>
				<p class="text-caption text-shade-50 mt-xs">Gestione magazzino</p>
			</div>

			<nav class="flex-1 px-lg py-lg space-y-xs">
				{#each navItems as item}
					<a
						href={item.href}
						class="block px-md py-sm rounded-md text-body-md transition-colors duration-150"
						class:bg-aloe-10={isActive(item.href)}
						class:text-ink={isActive(item.href)}
						class:text-shade-60={!isActive(item.href)}
						class:hover:bg-canvas-cream={!isActive(item.href)}
					>
						{item.label}
					</a>
				{/each}
			</nav>

			<div class="px-xl py-lg border-t border-hairline-light">
				<div class="text-caption text-shade-50 truncate">{$user.email}</div>
				<button
					on:click={handleLogout}
					class="mt-sm text-micro text-shade-40 hover:text-ink transition-colors"
				>
					Logout
				</button>
			</div>
		</aside>

		<!-- Main content -->
		<main class="flex-1 min-h-screen">
			<div class="max-w-6xl mx-auto px-xl py-lg">
				<slot />
			</div>
		</main>
	</div>

	<!-- Toasts -->
	<div class="fixed bottom-lg right-lg z-50 space-y-sm flex flex-col items-end">
		{#each $toasts as toast (toast.id)}
			<Toast {toast} on:dismiss={() => removeToast(toast.id)} />
		{/each}
	</div>
{:else}
	<slot />
{/if}

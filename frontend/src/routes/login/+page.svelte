<script lang="ts">
	import { goto } from '$app/navigation';
	import { login, register } from '$lib/stores/auth';
	import { addToast } from '$lib/stores/toast';

	let email = '';
	let password = '';
	let name = '';
	let isRegister = false;
	let loading = false;

	async function handleSubmit() {
		loading = true;
		try {
			if (isRegister) {
				await register(email, password, name);
				addToast('Account creato con successo!', 'success');
			} else {
				await login(email, password);
				addToast('Benvenuto!', 'success');
			}
			goto('/');
		} catch (err: any) {
			addToast(err.message || 'Errore durante l\'accesso', 'error');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{isRegister ? 'Registrati' : 'Accedi'} — Inventarify</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-canvas-cream px-lg">
	<div class="w-full max-w-[420px]">
		<!-- Logo -->
		<div class="text-center mb-xxl">
			<h1 class="font-display text-display-lg text-ink tracking-wide">Inventarify</h1>
			<p class="text-caption text-shade-50 mt-xs uppercase tracking-wider">Gestione magazzino ristorante</p>
		</div>

		<!-- Card -->
		<div class="card-pricing shadow-level-4">
			<h2 class="font-display text-heading-xl text-ink mb-lg">
				{isRegister ? 'Crea account' : 'Accedi'}
			</h2>

			<form on:submit|preventDefault={handleSubmit} class="space-y-lg">
				{#if isRegister}
					<div>
						<label class="block text-caption text-shade-50 mb-xs">Nome</label>
						<input
							type="text"
							bind:value={name}
							required
							class="input-text"
							placeholder="Il tuo nome"
						/>
					</div>
				{/if}

				<div>
					<label class="block text-caption text-shade-50 mb-xs">Email</label>
					<input
						type="email"
						bind:value={email}
						required
						class="input-text"
						placeholder="tu@email.com"
					/>
				</div>

				<div>
					<label class="block text-caption text-shade-50 mb-xs">Password</label>
					<input
						type="password"
						bind:value={password}
						required
						minlength="8"
						class="input-text"
						placeholder="••••••••"
					/>
				</div>

				<button
					type="submit"
					disabled={loading}
					class="btn-primary-pill w-full disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{loading ? 'Caricamento...' : isRegister ? 'Crea account' : 'Accedi'}
				</button>
			</form>

			<div class="mt-lg pt-lg border-t border-hairline-light text-center">
				<button
					on:click={() => isRegister = !isRegister}
					class="text-caption text-shade-50 hover:text-ink transition-colors"
				>
					{isRegister ? 'Hai già un account? Accedi' : 'Non hai un account? Registrati'}
				</button>
			</div>
		</div>
	</div>
</div>

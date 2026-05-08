import { client, DB_ID } from '$lib/appwrite';

export type RealtimeEvent = 'create' | 'update' | 'delete';

/**
 * Subscribe to real-time changes on one or more collections.
 * Returns an unsubscribe function.
 */
export function subscribeToChanges(
	collectionIds: string[],
	onChange: (collectionId: string, event: RealtimeEvent, payload: any) => void
): () => void {
	const channels = collectionIds.map(
		(id) => `databases.${DB_ID}.collections.${id}.documents`
	);

	const unsubscribe = client.subscribe(channels, (response) => {
		const event = response.events.find(
			(e: string) =>
				e.includes('.create') || e.includes('.update') || e.includes('.delete')
		);
		if (!event) return;

		const type: RealtimeEvent = event.includes('.create')
			? 'create'
			: event.includes('.update')
				? 'update'
				: 'delete';

		const collectionId = collectionIds.find((id) =>
			event.includes(`.collections.${id}.`)
		);
		if (collectionId) {
			onChange(collectionId, type, response.payload);
		}
	});

	return unsubscribe;
}

import { watch } from "vue";
import { currentTrack, feed } from "../controllers/localFeedStore.js";
import { drippingState } from "../controllers/drippingState.js";
import {
	sendBoost,
	makeStreamMeta,
	makeStreamValueMeta,
} from "../controllers/lightningPayments.js";


export default function useSatDripping() {
	// Drips every five seconds. Users define sat drip amounts in sats/minute.
	const dripInterval = 5000;
	const userSetInterval = 60000;

	let timerId = null;

	function sendBatchedPayment() {
		if (drippingState.currentFractionalSatsOwed < 1.0){
			return;
		}

		// Note that makeStreamValueMeta is designed to statistically distribute small
		// numbers of sats.
		const valueMeta = makeStreamValueMeta(
			Math.floor(drippingState.currentFractionalSatsOwed),
			drippingState.currentValueRecipients,
		);

		sendBoost(drippingState.currentStreamMeta, valueMeta);

		// Should be reset anyways, but just in case:
		drippingState.currentFractionalSatsOwed = 0.0;
	}

	function onDrippingInterval() {
		const dripAmount = (dripInterval / userSetInterval) * drippingState.dripRate;
		drippingState.currentFractionalSatsOwed += dripAmount;
	}

	function updateDrippingTrack() {
		drippingState.currentStreamMeta = makeStreamMeta(
			feed[0].title,
			feed[0].guid,
			currentTrack.value.title,
			currentTrack.value.guid,
		);

		drippingState.currentValueRecipients = currentTrack.value.value;
		drippingState.currentFractionalSatsOwed = 0.0;
	}

	function startDripTimer() {
		timerId = setInterval(onDrippingInterval, dripInterval);
	}

	function stopDripTimer() {
		clearInterval(timerId);
		timerId = null;
	}


	watch(currentTrack, () => {
		if (drippingState.enabled) {
			const canDrip = currentTrack.value.value.length > 0;
			drippingState.active = canDrip;
		}
	});


	watch(
		() => drippingState.active,
		(active) => {
			if (active) {
				updateDrippingTrack();
				startDripTimer();
			}
			else {
				stopDripTimer();
				sendBatchedPayment();
			}
		}
	);
}

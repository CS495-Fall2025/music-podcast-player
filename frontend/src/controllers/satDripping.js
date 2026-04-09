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
	let satsSpentInt = 0;
	let satsSpentFractional = 0.0;

	function startDripTimer() {
		timerId = setInterval(() => {
			const dripAmount = (dripInterval / userSetInterval) * drippingState.dripRate;
			satsSpentFractional += dripAmount;

			const spendAmount = Math.floor(satsSpentFractional) - satsSpentInt;
			satsSpentInt += spendAmount;

			if (spendAmount > 0) {
				const streamMeta = makeStreamMeta(
					feed[0].title,
					feed[0].guid,
					currentTrack.value.title,
					currentTrack.value.guid,
				);
				// Note that makeStreamValueMeta is designed to statistically distribute small
				// numbers of sats.
				const valueMeta = makeStreamValueMeta(
					spendAmount,
					currentTrack.value.value,
				);

				console.log(`Spend ${spendAmount}`);
				console.log(valueMeta);
				console.log(currentTrack.value.value);
				sendBoost(streamMeta, valueMeta);
			}

			console.log(`Frac: ${satsSpentFractional} - Int: ${satsSpentInt}`);
		}, dripInterval);
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
				startDripTimer();
			}
			else {
				stopDripTimer();
			}
		}
	);
}

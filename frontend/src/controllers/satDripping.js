import { watch } from "vue";
import { currentTrack } from "../controllers/localFeedStore.js";
import { drippingState } from "../controllers/drippingState.js";


export default function useSatDripping() {
	// Drips every five seconds. Users define sat drip amounts in sats/minute.
	const dripInterval = 5000;
	const userSetInterval = 60000;

	let timerId = null;
	let satsSpentInt = 0;
	let satsSpentFractional = 0.0;

	function startDripTimer() {
		timerId = setInterval(() => {
			console.log("Drip!");
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

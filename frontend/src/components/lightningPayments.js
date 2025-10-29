import { ref } from "vue";

import {
	init,
	onConnected,
	onDisconnected,
} from '@getalby/bitcoin-connect';


const wallet = ref(null);

onConnected((provider) => {
	wallet.value = provider;
});

onDisconnected(() => {
	wallet.value = null;
});


export function initializeLightning() {
	init({
		appName: "RSS Music Player",
		filters: ["nwc"],
		showBalance: false,
		persistConnection: true,
		providerConfig: {
			nwc: {
				authorizationUrlOptions: {
					requestMethods: [
						"get_balance",
						"pay_keysend",
					]
				}
			}
		}
	});
}


// Based on fields from https://github.com/lightning/blips/blob/master/blip-0010.md
// Designed specifically for boost payments, use makeStreamMeta for stream payments in
// the future.
export function makeBoostagramMeta(
	podcastName,
	podcastGuid,
	trackName,
	trackGuid,
	playbackSeconds,
	message,
	senderName,
) {
	return {
		podcast: podcastName,
		uid: podcastGuid,
		episode: trackName,
		episode_guid: trackGuid,
		ts: playbackSeconds,
		action: "boost",
		app_name: __NAME__,
		app_version: __VERSION__,
		message: message,
		sender_name: senderName,
	}
}


// Ensure value type is keysend and recipient type is node before passing recipients 
// into this function.
// Recipients format: [{name: str, address: str, split: str(number)}]
export function makePaymentMeta(
	
) {

}


export function sendBoost() {
	
}

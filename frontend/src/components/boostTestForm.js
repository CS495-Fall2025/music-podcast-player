	import {
		init,
		launchModal,
		requestProvider,
	} from '@getalby/bitcoin-connect';


export async function onTestBoostSubmitted(event) {
  event.preventDefault();
  let data = new FormData(event.target);

	console.log(data)

	const provider = await requestProvider();
	
	const records = {
		"podcast": "Jazz No Es Polca",
		"feedID": 7427670,
		"url": "https://wavlake.com/feed/music/960ee35a-10a5-4769-858f-7e32afc1a298",
		"guid": "fc1fc86b-ab84-5db8-a532-05c9f1ec4f36",
		"episode_guid": "36d61e40-7a95-4275-9cc1-839f26efd774",
		"time": 90,
		"action": "boost",
		"app_name": "RSSMusicPlayer",
		"name": "Juanjo Corbalán via Wavlake",
	};

	const boost = {
		destination: data.get("recipientAddress"),
		amount: String(data.get("sats")),
		customRecords: {
			"7629169": formatPodcastJSON(records)
		}
	}

	console.log(boost);

	provider.keysend(boost);
}


export async function onConnectWalletClicked() {
	// Initialize Bitcoin Connect
	init({
		appName: 'RSS Music Player', // your app name
	});

	await launchModal();
}


function formatPodcastJSON(obj) {
	let json = JSON.stringify(obj);

	json = json.replace(/:(?=(?:[^"]*"[^"]*")*[^"]*$)/g, ': ');
	json = json.replace(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/g, ', ');

	return json;
}


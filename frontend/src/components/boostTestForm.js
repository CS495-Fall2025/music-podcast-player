import {
	connectWallet,
	makeBoostMeta,
	makeValueMeta,
	sendBoost,
} from './lightningPayments.js';


export async function onTestBoostSubmitted(event) {
	event.preventDefault();
	let data = new FormData(event.target);

	console.log(data);

	const boostMeta = makeBoostMeta(
		"Jazz No Es Polca",
		"fc1fc86b-ab84-5db8-a532-05c9f1ec4f36",
		"El Polquero",
		"f3de2def-77d0-4f4b-ad38-e2bee1adac31",
		data.get("message"),
		"Sender name"
	);

	const valueMeta = makeValueMeta(
		parseInt(data.get("sats")),
		[
			{
				name: "Artist 1",
				address: data.get("recipientAddress"),
				split: 33,
			},
			{
				name: "Artist 2",
				address: data.get("recipientAddress"),
				split: 33,
			},
			{
				name: "Artist 3",
				address: data.get("recipientAddress"),
				split: 33,
			}
		]
	);

	console.log(boostMeta);
	console.log(valueMeta);

	sendBoost(boostMeta, valueMeta);
}


export async function onConnectWalletClicked() {
	await connectWallet();
}

import { describe, it, expect } from "vitest";
import { makeStreamMeta, makeStreamValueMeta } from "../src/controllers/lightningPayments.js";

describe("makeStreamMeta", () => {
  it("uses provided information", () => {
		const meta = makeStreamMeta(
			"Podcast Name",
			"podcastguid",
			"Track Name",
			"trackguid",
		);
    expect(meta.podcast).toBe("Podcast Name");
    expect(meta.guid).toBe("podcastguid");
    expect(meta.episode).toBe("Track Name");
    expect(meta.episode_guid).toBe("trackguid");
  });
  
	it("uses stream action", () => {
		const meta = makeStreamMeta(
			"Podcast Name",
			"podcastguid",
			"Track Name",
			"trackguid",
		);
    expect(meta.action).toBe("stream");
  });
});

describe("makeStreamValueMeta", () => {
  it("uses recipient information", () => {
		const meta = makeStreamValueMeta(
			50,
			[
				{
					address: "recipient-1-addr",
					customKey: "300",
					customRecord: {300: "recipient-1-custom-value"},
					customValue: "recipient-1-custom-value",
					recipient: "recipient-1",
					split: "100",
					type: "value",
					valueType: "node",
				},
			],
		);
    expect(meta[0].address).toBe("recipient-1-addr");
    expect(meta[0].customRecord).toStrictEqual({300: "recipient-1-custom-value"});
    expect(meta[0].meta.name).toBe("recipient-1");
  });
  
	it("divides sats randomly by split", () => {
		const meta = makeStreamValueMeta(
			5000,
			[
				{
					address: "recipient-1-addr",
					customKey: "300",
					customRecord: {300: "recipient-1-custom-value"},
					customValue: "recipient-1-custom-value",
					recipient: "recipient-1",
					split: "90",
					type: "value",
					valueType: "node",
				},
				{
					address: "recipient-2-addr",
					customKey: "300",
					customRecord: {300: "recipient-2-custom-value"},
					customValue: "recipient-2-custom-value",
					recipient: "recipient-2",
					split: "10",
					type: "value",
					valueType: "node",
				},
			],
		);

		// This test CAN FAIL, but it's very unlikely that it will. This is necessary
		// because the function under test uses weighted randomness.
    expect(meta[0].meta.value_msat).toBeGreaterThan(0);
    expect(meta[1].meta.value_msat).toBeGreaterThan(0);
    expect(meta[0].meta.value_msat).toBeGreaterThan(meta[1].meta.value_msat * 5);

		expect(meta[0].meta.value_msat + meta[1].meta.value_msat).toBe(5000000);
  });
});


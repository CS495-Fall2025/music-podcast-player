import { describe, it, expect } from "vitest";
import userTrack from "../src/controllers/userTrack.js";
import { currentTrack } from "../src/controllers/localFeedStore.js";

describe("userTrack", () => {
  // Test component name is set correctly
  it("has correct component name", () => {
    expect(userTrack.name).toBe("userTrack");
  });

  // Test track prop is required and correct type
  it("requires track prop", () => {
    expect(userTrack.props.track.required).toBe(true);
    expect(userTrack.props.track.type).toBe(Object);
  });

  // Test selectTrack method updates the current track
  it("selectTrack method updates currentTrack", () => {
    const mockTrack = { audio: "test.mp3" };
    const component = {
      track: mockTrack,
    };

    userTrack.methods.selectTrack.call(component);
    expect(currentTrack.value).toStrictEqual(mockTrack);

    currentTrack.value = "";
  });
});

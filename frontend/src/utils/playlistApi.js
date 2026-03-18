export async function fetchUserPlaylists() {
  const response = await fetch("/mock-playlists.json", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load playlist data.");
  }

  return response.json();
}

export async function fetchPlaylistDetail(playlistId) {
  const response = await fetch(`/mock-playlist-${playlistId}.json`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load playlist tracks.");
  }

  return response.json();
}

import loadConfig from "../config";

export async function fetchUserPlaylists() {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/me`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Unable to load playlist data.");
  }

  return response.json();
}

export async function fetchPlaylistDetail(playlistId) {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/${playlistId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Unable to load playlist tracks.");
  }

  return response.json();
}

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

export async function deletePlaylist(playlistId) {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/${playlistId}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Unable to delete playlist.");
  }

  return response.json();
}

export async function removeTrackFromPlaylist(playlistId, trackUrl) {
  const config = await loadConfig();
  const response = await fetch(
    `${config.backendUrl}/playlists/${playlistId}/tracks/remove`,
    {
      method: "DELETE",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_url: trackUrl }),
    },
  );

  if (!response.ok) {
    throw new Error("Unable to remove track.");
  }

  return response.json();
}

export async function reorderTrackInPlaylist(
  playlistId,
  trackUrl,
  newPosition,
) {
  const config = await loadConfig();
  const response = await fetch(
    `${config.backendUrl}/playlists/${playlistId}/tracks/reorder`,
    {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_url: trackUrl, new_position: newPosition }),
    },
  );

  if (!response.ok) {
    throw new Error("Unable to reorder track.");
  }

  return response.json();
}

export async function fetchPublicUserPlaylists(username) {
  const config = await loadConfig();
  const response = await fetch(
    `${config.backendUrl}/playlists/user/${username}`,
  );

  if (!response.ok) {
    throw new Error("User not found.");
  }

  return response.json();
}

export async function fetchPublicPlaylistDetail(playlistId) {
  const config = await loadConfig();
  const response = await fetch(
    `${config.backendUrl}/playlists/public/${playlistId}`,
  );

  if (!response.ok) {
    throw new Error("Unable to load playlist tracks.");
  }

  return response.json();
}

export async function createPlaylist(title, description = "") {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/create`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description }),
  });

  if (!response.ok) {
    throw new Error("Unable to create playlist.");
  }

  return response.json();
}

export async function updatePlaylist(playlistId, title, description = "") {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/playlists/${playlistId}`, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description }),
  });

  if (!response.ok) {
    throw new Error("Unable to update playlist.");
  }

  return response.json();
}

export async function addTrackToPlaylist(playlistId, trackUrl, feedUrl = null) {
  const config = await loadConfig();
  const response = await fetch(
    `${config.backendUrl}/playlists/${playlistId}/tracks/add`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_url: trackUrl, feed_url: feedUrl }),
    },
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.message ||
        data.error ||
        `Request failed with status ${response.status}`,
    );
  }

  return data;
}

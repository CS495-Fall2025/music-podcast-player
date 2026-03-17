import loadConfig from "../config";
import { playlist, playlistTracks } from "./playlistStore.js";

async function requestPlaylist(playlistId) {
    const config = await loadConfig();

    return fetch(
        `${config.backendUrl}/playlists/${playlistId}`
    ).then((response) => {
        if (!response.ok) {
            console.log(`Request returned status ${response.status}`);
            throw new Error(`Request returned status ${response.status}`);
        }

        return response.json();
    }).then(response => parseResponse(response)
    ).catch((message) => handleError(message));
}

function parseResponse(response) {
    console.log(response);
    playlist.splice(0, playlist.length, ...response["playlist"]);
    playlistTracks.splice(0, playlistTracks.length, ...response["tracks"]);
}

function handleError(message) {
    console.log("Error encountered while reading response from backend.");
    console.log(message);
}

export { requestPlaylist };
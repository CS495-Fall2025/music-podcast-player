import loadConfig from "../config";

export async function getPageContent(page) {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/pages/${page}`, {
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error(`Failed to load page content: ${response.status}`);
  }
  const data = await response.json();
  return data.html;
}

export async function putPageContent(page, html) {
  const config = await loadConfig();
  const response = await fetch(`${config.backendUrl}/pages/${page}`, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ html }),
  });
  if (!response.ok) {
    throw new Error(`Failed to save page content: ${response.status}`);
  }
  const data = await response.json();
  return data.html;
}

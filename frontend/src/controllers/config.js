export default async function loadConfig() {
	// Not cached so we always have an up-to-date config.
  const result = await fetch("/config.json", { cache: "no-store" });
  if (!result.ok) {
		throw Error("Unable to load config.")
  }

  const config = await result.json();

  return config;
}

import { computed, ref } from "vue";

export default function useSatUsd() {
  const sats = ref(0);
  const satPrice = ref(null);
  const loadingPrice = ref(false);

  const fetchPrice = async () => {
    loadingPrice.value = true;
    try {
      const res = await fetch(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
      );
      const data = await res.json();
      satPrice.value = data.bitcoin.usd / 100000000;
    } catch (e) {
      console.error("Error fetching BTC price:", e);
    } finally {
      loadingPrice.value = false;
    }
  };

  const priceMessage = computed(() => {
    if (loadingPrice.value) return "Loading price...";
    if (!satPrice.value) return "Price unavailable";
    return `${sats.value} sat ≈ ${(sats.value * satPrice.value).toFixed(2)} USD`;
  });

  return {
    sats,
    fetchPrice,
    priceMessage,
  };
}

function generateRandomString(length = 128) {
  if (length < 43 || length > 128) {
    throw new Error("Code verifier length must be between 43 and 128");
  }

  const charset =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  let result = "";

  for (let i = 0; i < length; i++) {
    result += charset.charAt(Math.floor(Math.random() * charset.length));
  }

  return result;
}

async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const digest = await crypto.subtle.digest("SHA-256", data);

  // Convert to base64url
  const base64 = btoa(String.fromCharCode.apply(null, new Uint8Array(digest)));
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

export async function generatePKCE() {
  const verifier = generateRandomString(128);
  const challenge = await generateCodeChallenge(verifier);

  return {
    verifier,
    challenge,
  };
}

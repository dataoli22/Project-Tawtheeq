const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${options.method || "GET"} ${path} failed: ${res.status} ${body}`);
  }
  return res.json();
}

export const api = {
  listPersonas: () => request("/personas"),
  getScore: (personaId) => request(`/score/${personaId}`),
  getProviders: (personaId) => request(`/providers/${personaId}`),
  getInvoices: (personaId) => request(`/invoices/${personaId}`),
  createInvoice: (payload) =>
    request("/invoices", { method: "POST", body: JSON.stringify(payload) }),
  fundInvoice: (tokenId) => request(`/invoices/${tokenId}/fund`, { method: "POST" }),
  repay: (tokenId) =>
    request("/fund/repay", { method: "POST", body: JSON.stringify({ token_id: tokenId }) }),
  chat: (personaId, message) =>
    request("/chat", { method: "POST", body: JSON.stringify({ persona_id: personaId, message }) }),
  getPlaygroundDefaults: () => request("/playground/defaults"),
  scorePlayground: (signals) =>
    request("/playground/score", { method: "POST", body: JSON.stringify({ signals }) }),
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Offer {
  id: number;
  portal: string;
  title: string;
  company: string;
  url: string;
  summary: string | null;
  technologies: string | null;
  modality: string | null;
  salary: string | null;
  score: number | null;
  reason: string | null;
  status: string;
  scraped_at: string;
}

export async function getOffers(status = "PENDIENTE"): Promise<Offer[]> {
  try {
    const res = await fetch(`${API}/api/offers?status=${status}`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function applyOffer(id: number): Promise<void> {
  await fetch(`${API}/api/offers/${id}/apply`, { method: "PATCH" });
}

export async function saveOffer(id: number): Promise<void> {
  await fetch(`${API}/api/offers/${id}/save`, { method: "PATCH" });
}

export async function discardOffer(id: number): Promise<void> {
  await fetch(`${API}/api/offers/${id}/discard`, { method: "PATCH" });
}

export async function blockCompany(name: string): Promise<void> {
  await fetch(`${API}/api/companies/block`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export async function triggerScraping(): Promise<void> {
  await fetch(`${API}/api/scraper/trigger`, { method: "POST" });
}

// --- Respuestas automáticas ---

export interface Answer {
  id: number;
  descripcion: string;
  keywords: string[];
  respuesta: string;
  portal: string | null;
  activo: boolean;
  creado_at: string;
}

export async function getAnswers(): Promise<Answer[]> {
  try {
    const res = await fetch(`${API}/api/answers`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function createAnswer(data: Omit<Answer, "id" | "activo" | "creado_at">): Promise<Answer | null> {
  try {
    const res = await fetch(`${API}/api/answers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function updateAnswer(id: number, data: Partial<Omit<Answer, "id" | "creado_at">>): Promise<Answer | null> {
  try {
    const res = await fetch(`${API}/api/answers/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function deleteAnswer(id: number): Promise<void> {
  await fetch(`${API}/api/answers/${id}`, { method: "DELETE" });
}

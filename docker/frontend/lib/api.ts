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

// --- Stats ---

export interface Stats {
  sent_this_week: number;
  total_sent: number;
  total_pending: number;
  total_discarded: number;
  by_portal: { portal: string; count: number }[];
}

export async function getStats(): Promise<Stats | null> {
  try {
    const res = await fetch(`${API}/api/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

// --- Portals ---

export interface Portal {
  name: string;
  url: string;
  auto_apply: boolean;
  market: string;
  session_active: boolean;
  applications_count: number;
}

export async function getPortals(): Promise<Portal[]> {
  try {
    const res = await fetch(`${API}/api/portals`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function validatePortal(url: string): Promise<any> {
  try {
    const res = await fetch(`${API}/api/portals/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

// --- CV ---

export async function getCvEs(): Promise<any> {
  try {
    const res = await fetch(`${API}/api/cv/es`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function saveCvEs(data: any): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/cv/es`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.ok;
  } catch { return false; }
}

export async function getCvEn(): Promise<any> {
  try {
    const res = await fetch(`${API}/api/cv/en`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function saveCvEn(data: any): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/cv/en`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.ok;
  } catch { return false; }
}

export async function uploadCvPdf(lang: "es" | "en", file: File): Promise<boolean> {
  try {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API}/api/cv/${lang}/upload`, { method: "POST", body: form });
    return res.ok;
  } catch { return false; }
}

export async function getCvPdfUrl(lang: "es" | "en"): Promise<string> {
  return `${API}/api/cv/${lang}/pdf`;
}

export async function cvPdfExists(lang: "es" | "en"): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/cv/${lang}/pdf/exists`, { cache: "no-store" });
    if (!res.ok) return false;
    const data = await res.json();
    return data.exists === true;
  } catch { return false; }
}

export async function getProfile(): Promise<any> {
  try {
    const res = await fetch(`${API}/api/cv/profile`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function saveProfile(data: any): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/cv/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.ok;
  } catch { return false; }
}

// --- Settings ---

export async function getSettings(): Promise<any> {
  try {
    const res = await fetch(`${API}/api/settings`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function saveSettings(data: any): Promise<boolean> {
  try {
    const res = await fetch(`${API}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.ok;
  } catch { return false; }
}

export async function testWhatsapp(): Promise<{ status: string; message: string } | null> {
  try {
    const res = await fetch(`${API}/api/settings/test-whatsapp`, { method: "POST" });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

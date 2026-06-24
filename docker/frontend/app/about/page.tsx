"use client";

import { useEffect, useState, useRef } from "react";
import { getProfile, saveProfile, uploadCvPdf, cvPdfExists } from "@/lib/api";

const LANG_LEVELS = ["Nativo", "C2", "C1", "B2", "B1", "A2", "A1"];
const LANG_LEVEL_DESCRIPTIONS: Record<string, string> = {
  Nativo: "Hablante nativo",
  C2: "Maestría (comprensión y expresión perfectas)",
  C1: "Dominio operativo eficaz",
  B2: "Usuario independiente avanzado",
  B1: "Usuario independiente básico",
  A2: "Plataforma básica",
  A1: "Iniciación",
  Native: "Native speaker",
};

const DEFAULT_PROFILE = {
  stack: [] as { tech: string; level: string; years: string; willing: string }[],
  avoid_technologies: [] as string[],
  work_modality: { preference: "", acceptable: "", rejected: "", timezone: "Chile (UTC-3 / UTC-4)" },
  geo_availability: "",
  salary: { usd_min: "", usd_preferred: "", eur_min: "", eur_preferred: "", clp_min: "", clp_preferred: "" },
  languages: [] as { language: string; level: string; contexts: string }[],
  contract_type: "",
  min_project_duration: "",
  selection_process: "",
  communication_tools: "",
  methodology: "",
};

export default function AboutPage() {
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [pdfEsExists, setPdfEsExists] = useState(false);
  const [pdfEnExists, setPdfEnExists] = useState(false);

  useEffect(() => {
    Promise.all([getProfile(), cvPdfExists("es"), cvPdfExists("en")]).then(([pr, hasEs, hasEn]) => {
      if (pr) setProfile({ ...DEFAULT_PROFILE, ...pr });
      setPdfEsExists(hasEs);
      setPdfEnExists(hasEn);
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    setSaving(true);
    await saveProfile(profile);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-white mb-2">Configura tu perfil</h1>
      <div className="bg-blue-950 border border-blue-800 rounded-xl p-4 mb-6">
        <p className="text-blue-300 text-sm font-medium mb-1">¿Por qué es importante completar estos datos?</p>
        <p className="text-blue-400 text-xs leading-relaxed">
          Wunen usa tu CV y perfil para que el evaluador de IA seleccione las mejores ofertas para ti,
          y para generar cartas de presentación personalizadas al postular automáticamente.
          Entre más completo esté tu perfil, mejores serán los resultados.
        </p>
      </div>

      {loading ? (
        <div className="text-gray-500 text-center py-20">Cargando datos...</div>
      ) : (
        <>
          {/* CV en PDF (Español e Inglés) */}
          <div className="grid sm:grid-cols-2 gap-4">
            <CvPdfUpload lang="es" hasFile={pdfEsExists} onUploaded={() => setPdfEsExists(true)} />
            <CvPdfUpload lang="en" hasFile={pdfEnExists} onUploaded={() => setPdfEnExists(true)} />
          </div>

          {/* Formulario de perfil */}
          <div className="mt-8">
            <ProfileForm profile={profile} setProfile={setProfile} />
          </div>

          <div className="mt-8 flex items-center gap-4">
            <button onClick={handleSave} disabled={saving}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors text-sm">
              {saving ? "Guardando..." : "Guardar perfil"}
            </button>
            {saved && <span className="text-green-400 text-sm">✓ Guardado</span>}
          </div>
        </>
      )}
    </div>
  );
}

// ── Profile Form ─────────────────────────────────────────────────────────────

function ProfileForm({ profile, setProfile }: { profile: typeof DEFAULT_PROFILE; setProfile: (v: typeof DEFAULT_PROFILE) => void }) {
  const TECH_LEVELS = ["Avanzado", "Intermedio", "Básico"];

  function addStack() {
    setProfile({ ...profile, stack: [...profile.stack, { tech: "", level: "Intermedio", years: "", willing: "Sí" }] });
  }
  function removeStack(i: number) {
    setProfile({ ...profile, stack: profile.stack.filter((_, j) => j !== i) });
  }
  function setStack(i: number, field: string, val: string) {
    const stack = profile.stack.map((s, j) => j === i ? { ...s, [field]: val } : s);
    setProfile({ ...profile, stack });
  }

  function addAvoid() {
    setProfile({ ...profile, avoid_technologies: [...profile.avoid_technologies, ""] });
  }
  function setAvoid(i: number, val: string) {
    const avoid = profile.avoid_technologies.map((v, j) => j === i ? val : v);
    setProfile({ ...profile, avoid_technologies: avoid });
  }
  function removeAvoid(i: number) {
    setProfile({ ...profile, avoid_technologies: profile.avoid_technologies.filter((_, j) => j !== i) });
  }

  function addLang() {
    setProfile({ ...profile, languages: [...profile.languages, { language: "", level: "B2", contexts: "" }] });
  }
  function setLang(i: number, field: string, val: string) {
    const languages = profile.languages.map((l, j) => j === i ? { ...l, [field]: val } : l);
    setProfile({ ...profile, languages });
  }
  function removeLang(i: number) {
    setProfile({ ...profile, languages: profile.languages.filter((_, j) => j !== i) });
  }

  function setModality(field: string, val: string) {
    setProfile({ ...profile, work_modality: { ...profile.work_modality, [field]: val } });
  }
  function setSalary(field: string, val: string) {
    setProfile({ ...profile, salary: { ...profile.salary, [field]: val } });
  }

  return (
    <div className="space-y-8">
      {/* Stack tecnológico */}
      <section>
        <SectionTitle>Stack tecnológico</SectionTitle>
        <div className="space-y-3">
          {profile.stack.map((s, i) => (
            <div key={i} className="grid grid-cols-12 gap-2 items-center">
              <div className="col-span-4">
                <Input value={s.tech} onChange={(v) => setStack(i, "tech", v)} placeholder="PHP, Python, Java..." />
              </div>
              <div className="col-span-3">
                <select value={s.level} onChange={(e) => setStack(i, "level", e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
                  {TECH_LEVELS.map((l) => <option key={l}>{l}</option>)}
                </select>
              </div>
              <div className="col-span-2">
                <Input value={s.years} onChange={(v) => setStack(i, "years", v)} placeholder="Años" />
              </div>
              <div className="col-span-2">
                <select value={s.willing} onChange={(e) => setStack(i, "willing", e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
                  <option>Sí</option>
                  <option>No</option>
                </select>
              </div>
              <div className="col-span-1 text-center">
                <button onClick={() => removeStack(i)} className="text-gray-600 hover:text-red-400 text-lg">×</button>
              </div>
            </div>
          ))}
          <div className="grid grid-cols-12 gap-2 text-xs text-gray-600 px-1">
            <div className="col-span-4">Tecnología</div>
            <div className="col-span-3">Nivel</div>
            <div className="col-span-2">Años</div>
            <div className="col-span-2">¿Dispuesto?</div>
          </div>
          <button onClick={addStack} className="text-blue-400 hover:text-blue-300 text-sm font-medium">+ Agregar tecnología</button>
        </div>

        <div className="mt-5">
          <p className="text-sm text-gray-400 mb-2">Tecnologías que prefiero evitar:</p>
          <div className="space-y-2">
            {profile.avoid_technologies.map((t, i) => (
              <div key={i} className="flex gap-2">
                <Input value={t} onChange={(v) => setAvoid(i, v)} placeholder=".Net, Windows..." />
                <button onClick={() => removeAvoid(i)} className="text-gray-600 hover:text-red-400 text-lg">×</button>
              </div>
            ))}
            <button onClick={addAvoid} className="text-blue-400 hover:text-blue-300 text-sm font-medium">+ Agregar</button>
          </div>
        </div>
      </section>

      {/* Modalidad de trabajo */}
      <section>
        <SectionTitle>Modalidad de trabajo</SectionTitle>
        <div className="space-y-4">
          <Field label="Preferencia">
            <Input value={profile.work_modality.preference} onChange={(v) => setModality("preference", v)} placeholder="Remoto" />
          </Field>
          <Field label="Aceptable">
            <Input value={profile.work_modality.acceptable} onChange={(v) => setModality("acceptable", v)} placeholder="Híbrido" />
          </Field>
          <Field label="No acepto">
            <Input value={profile.work_modality.rejected} onChange={(v) => setModality("rejected", v)} placeholder="Presencial" />
          </Field>
          <Field label="Zona horaria">
            <Input value={profile.work_modality.timezone} onChange={(v) => setModality("timezone", v)} placeholder="Chile (UTC-3 / UTC-4)" />
          </Field>
          <Field label="Disponibilidad geográfica">
            <Input value={profile.geo_availability} onChange={(v) => setProfile({ ...profile, geo_availability: v })} placeholder="Todos en rango +/-2 horas" />
          </Field>
        </div>
      </section>

      {/* Expectativa salarial */}
      <section>
        <SectionTitle>Expectativa salarial</SectionTitle>
        <div className="grid grid-cols-2 gap-4">
          <Field label="USD mínimo (freelance/hora)">
            <Input value={profile.salary.usd_min} onChange={(v) => setSalary("usd_min", v)} placeholder="9" type="number" />
          </Field>
          <Field label="USD preferido (freelance/hora)">
            <Input value={profile.salary.usd_preferred} onChange={(v) => setSalary("usd_preferred", v)} placeholder="12" type="number" />
          </Field>
          <Field label="EUR mínimo (freelance/hora)">
            <Input value={profile.salary.eur_min} onChange={(v) => setSalary("eur_min", v)} placeholder="9" type="number" />
          </Field>
          <Field label="EUR preferido (freelance/hora)">
            <Input value={profile.salary.eur_preferred} onChange={(v) => setSalary("eur_preferred", v)} placeholder="12" type="number" />
          </Field>
          <Field label="CLP mínimo (dependencia/mes)">
            <Input value={profile.salary.clp_min} onChange={(v) => setSalary("clp_min", v)} placeholder="1200000" type="number" />
          </Field>
          <Field label="CLP preferido (dependencia/mes)">
            <Input value={profile.salary.clp_preferred} onChange={(v) => setSalary("clp_preferred", v)} placeholder="1500000" type="number" />
          </Field>
        </div>
      </section>

      {/* Idiomas */}
      <section>
        <SectionTitle>Idiomas para el trabajo</SectionTitle>
        <div className="space-y-3">
          {profile.languages.map((l, i) => (
            <div key={i} className="flex gap-3 items-start">
              <div className="w-32">
                <Input value={l.language} onChange={(v) => setLang(i, "language", v)} placeholder="Español" />
              </div>
              <div className="w-36">
                <select value={l.level} onChange={(e) => setLang(i, "level", e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
                  {LANG_LEVELS.map((lv) => <option key={lv}>{lv}</option>)}
                </select>
              </div>
              <div className="flex-1">
                <Input value={l.contexts} onChange={(v) => setLang(i, "contexts", v)} placeholder="Todo, lectura, reuniones..." />
              </div>
              <button onClick={() => removeLang(i)} className="text-gray-600 hover:text-red-400 text-lg mt-1.5">×</button>
            </div>
          ))}
          <button onClick={addLang} className="text-blue-400 hover:text-blue-300 text-sm font-medium">+ Agregar idioma</button>
        </div>
      </section>

      {/* Otros criterios */}
      <section>
        <SectionTitle>Otros criterios</SectionTitle>
        <div className="space-y-4">
          <Field label="Tipo de contrato">
            <Input value={profile.contract_type} onChange={(v) => setProfile({ ...profile, contract_type: v })} placeholder="Freelance, dependencia, cualquiera..." />
          </Field>
          <Field label="Duración mínima de proyecto">
            <Input value={profile.min_project_duration} onChange={(v) => setProfile({ ...profile, min_project_duration: v })} placeholder="Indiferente, mínimo 3 meses..." />
          </Field>
          <Field label="Proceso de selección">
            <Input value={profile.selection_process} onChange={(v) => setProfile({ ...profile, selection_process: v })} placeholder="Acepto pruebas técnicas de hasta 2 horas..." />
          </Field>
          <Field label="Herramientas de comunicación">
            <Input value={profile.communication_tools} onChange={(v) => setProfile({ ...profile, communication_tools: v })} placeholder="Slack, Teams, Discord, email..." />
          </Field>
          <Field label="Metodología">
            <Input value={profile.methodology} onChange={(v) => setProfile({ ...profile, methodology: v })} placeholder="Ágil/Scrum, sin preferencia..." />
          </Field>
        </div>
      </section>
    </div>
  );
}

// ── CV PDF Upload ─────────────────────────────────────────────────────────────

function CvPdfUpload({ lang, hasFile, onUploaded }: { lang: "es" | "en"; hasFile: boolean; onUploaded: (lang: "es" | "en") => void }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const label = lang === "es" ? "CV en PDF (Español)" : "CV in PDF (English)";
  const downloadName = lang === "es" ? "cv_es.pdf" : "cv_en.pdf";

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Solo se aceptan archivos PDF");
      return;
    }
    setUploading(true);
    setError(null);
    const ok = await uploadCvPdf(lang, file);
    setUploading(false);
    if (ok) {
      setSuccess(true);
      onUploaded(lang);
      setTimeout(() => setSuccess(false), 3000);
    } else {
      setError("Error al subir el archivo. Intenta de nuevo.");
    }
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-1">{label}</h3>
      <p className="text-xs text-gray-500 mb-4">
        Sube el archivo PDF de tu CV. Se usará en postulaciones que requieran adjuntar el CV.
      </p>
      <div className="flex items-center gap-3 flex-wrap">
        <label className="cursor-pointer bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
          {uploading ? "Subiendo..." : hasFile ? "Reemplazar PDF" : "Subir PDF"}
          <input ref={inputRef} type="file" accept=".pdf,application/pdf" className="hidden" onChange={handleFile} disabled={uploading} />
        </label>
        {hasFile && (
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cv/${lang}/pdf`}
            target="_blank"
            rel="noreferrer"
            download={downloadName}
            className="text-cyan-400 hover:text-cyan-300 text-sm transition-colors"
          >
            Descargar PDF actual
          </a>
        )}
        {success && <span className="text-green-400 text-sm">✓ PDF subido correctamente</span>}
        {error && <span className="text-red-400 text-sm">{error}</span>}
      </div>
      {hasFile && (
        <p className="text-xs text-gray-600 mt-2">Ya tienes un PDF cargado. Sube uno nuevo para reemplazarlo.</p>
      )}
    </div>
  );
}

// ── Shared UI ─────────────────────────────────────────────────────────────────

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="text-base font-semibold text-white mb-4 pb-2 border-b border-gray-800">{children}</h2>;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1.5">{label}</label>
      {children}
    </div>
  );
}

function Input({ value, onChange, placeholder, type = "text", disabled = false }: {
  value: string; onChange: (v: string) => void; placeholder?: string; type?: string; disabled?: boolean;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600 disabled:opacity-40"
    />
  );
}

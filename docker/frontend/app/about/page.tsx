"use client";

import { useEffect, useState, useCallback } from "react";
import { getCvEs, saveCvEs, getCvEn, saveCvEn, getProfile, saveProfile } from "@/lib/api";

type Tab = "cv-es" | "cv-en" | "profile";

const SKILL_LEVELS_ES = ["Avanzado", "Intermedio", "Básico"];
const SKILL_LEVELS_EN = ["Advanced", "Intermediate", "Basic"];
const LANG_LEVELS = ["Nativo", "C2", "C1", "B2", "B1", "A2", "A1"];
const LANG_LEVELS_EN = ["Native", "C2", "C1", "B2", "B1", "A2", "A1"];
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

const DEFAULT_CV = {
  name: "", title: "", presentation: "",
  contact: { phone: "", email: "", linkedin: "", github: "" },
  professional_summary: "",
  skills: [] as { name: string; level: string }[],
  experience: [] as { role: string; company: string; start: string; end: string; current: boolean; bullets: string[] }[],
  education: [] as { degree: string; institution: string; year: string }[],
  languages: [] as { language: string; level: string }[],
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
  const [tab, setTab] = useState<Tab>("cv-es");
  const [cvEs, setCvEs] = useState(DEFAULT_CV);
  const [cvEn, setCvEn] = useState(DEFAULT_CV);
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    Promise.all([getCvEs(), getCvEn(), getProfile()]).then(([es, en, pr]) => {
      if (es) setCvEs({ ...DEFAULT_CV, ...es });
      if (en) setCvEn({ ...DEFAULT_CV, ...en });
      if (pr) setProfile({ ...DEFAULT_PROFILE, ...pr });
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    setSaving(true);
    if (tab === "cv-es") await saveCvEs(cvEs);
    else if (tab === "cv-en") await saveCvEn(cvEn);
    else await saveProfile(profile);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "cv-es", label: "CV (Español)" },
    { key: "cv-en", label: "CV (English)" },
    { key: "profile", label: "Perfil" },
  ];

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

      {/* Tabs */}
      <div className="flex gap-1 mb-8 bg-gray-900 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === t.key ? "bg-gray-700 text-white" : "text-gray-400 hover:text-gray-200"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-gray-500 text-center py-20">Cargando datos...</div>
      ) : (
        <>
          {tab === "cv-es" && <CvForm cv={cvEs} setCv={setCvEs} lang="es" />}
          {tab === "cv-en" && <CvForm cv={cvEn} setCv={setCvEn} lang="en" />}
          {tab === "profile" && <ProfileForm profile={profile} setProfile={setProfile} />}

          <div className="mt-8 flex items-center gap-4">
            <button onClick={handleSave} disabled={saving}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors text-sm">
              {saving ? "Guardando..." : "Guardar datos"}
            </button>
            {saved && <span className="text-green-400 text-sm">✓ Guardado</span>}
          </div>
        </>
      )}
    </div>
  );
}

// ── CV Form ─────────────────────────────────────────────────────────────────

function CvForm({ cv, setCv, lang }: { cv: typeof DEFAULT_CV; setCv: (v: typeof DEFAULT_CV) => void; lang: "es" | "en" }) {
  const isEs = lang === "es";
  const levels = isEs ? SKILL_LEVELS_ES : SKILL_LEVELS_EN;
  const langLevels = isEs ? LANG_LEVELS : LANG_LEVELS_EN;

  function setContact(field: string, val: string) {
    setCv({ ...cv, contact: { ...cv.contact, [field]: val } });
  }

  function addSkill() {
    setCv({ ...cv, skills: [...cv.skills, { name: "", level: levels[0] }] });
  }
  function removeSkill(i: number) {
    setCv({ ...cv, skills: cv.skills.filter((_, j) => j !== i) });
  }
  function setSkill(i: number, field: string, val: string) {
    const skills = cv.skills.map((s, j) => j === i ? { ...s, [field]: val } : s);
    setCv({ ...cv, skills });
  }

  function addExp() {
    setCv({ ...cv, experience: [...cv.experience, { role: "", company: "", start: "", end: "", current: false, bullets: [""] }] });
  }
  function removeExp(i: number) {
    setCv({ ...cv, experience: cv.experience.filter((_, j) => j !== i) });
  }
  function setExp(i: number, field: string, val: any) {
    const experience = cv.experience.map((e, j) => j === i ? { ...e, [field]: val } : e);
    setCv({ ...cv, experience });
  }
  function addBullet(i: number) {
    const experience = cv.experience.map((e, j) => j === i ? { ...e, bullets: [...e.bullets, ""] } : e);
    setCv({ ...cv, experience });
  }
  function setBullet(expIdx: number, bIdx: number, val: string) {
    const experience = cv.experience.map((e, j) => j === expIdx ? { ...e, bullets: e.bullets.map((b, k) => k === bIdx ? val : b) } : e);
    setCv({ ...cv, experience });
  }
  function removeBullet(expIdx: number, bIdx: number) {
    const experience = cv.experience.map((e, j) => j === expIdx ? { ...e, bullets: e.bullets.filter((_, k) => k !== bIdx) } : e);
    setCv({ ...cv, experience });
  }

  function addEdu() {
    setCv({ ...cv, education: [...cv.education, { degree: "", institution: "", year: "" }] });
  }
  function removeEdu(i: number) {
    setCv({ ...cv, education: cv.education.filter((_, j) => j !== i) });
  }
  function setEdu(i: number, field: string, val: string) {
    const education = cv.education.map((e, j) => j === i ? { ...e, [field]: val } : e);
    setCv({ ...cv, education });
  }

  function addLang() {
    setCv({ ...cv, languages: [...cv.languages, { language: "", level: langLevels[0] }] });
  }
  function removeLang(i: number) {
    setCv({ ...cv, languages: cv.languages.filter((_, j) => j !== i) });
  }
  function setLang(i: number, field: string, val: string) {
    const languages = cv.languages.map((l, j) => j === i ? { ...l, [field]: val } : l);
    setCv({ ...cv, languages });
  }

  return (
    <div className="space-y-8">
      {/* Datos básicos */}
      <section>
        <SectionTitle>{isEs ? "Datos básicos" : "Basic info"}</SectionTitle>
        <div className="space-y-4">
          <Field label={isEs ? "Nombre" : "Name"}>
            <Input value={cv.name} onChange={(v) => setCv({ ...cv, name: v })} placeholder={isEs ? "Rodrigo Moya Apablaza" : "John Doe"} />
          </Field>
          <Field label={isEs ? "Presentación corta / Cargo" : "Short title / Role"}>
            <Input value={cv.title} onChange={(v) => setCv({ ...cv, title: v })} placeholder={isEs ? "Ingeniero de Software" : "Software Engineer"} />
          </Field>
        </div>
      </section>

      {/* Contacto */}
      <section>
        <SectionTitle>{isEs ? "Información de contacto" : "Contact information"}</SectionTitle>
        <div className="space-y-4">
          <Field label={isEs ? "Teléfono" : "Phone"}>
            <Input value={cv.contact.phone} onChange={(v) => setContact("phone", v)} placeholder="+56 9 12345678" type="tel" />
          </Field>
          <Field label="Email">
            <Input value={cv.contact.email} onChange={(v) => setContact("email", v)} placeholder="correo@ejemplo.com" type="email" />
          </Field>
          <Field label={`LinkedIn ${isEs ? "(Opcional)" : "(Optional)"}`}>
            <Input value={cv.contact.linkedin} onChange={(v) => setContact("linkedin", v)} placeholder="linkedin.com/in/usuario" />
          </Field>
          <Field label={`GitHub ${isEs ? "(Opcional)" : "(Optional)"}`}>
            <Input value={cv.contact.github} onChange={(v) => setContact("github", v)} placeholder="github.com/usuario" />
          </Field>
        </div>
      </section>

      {/* Resumen profesional */}
      <section>
        <SectionTitle>{isEs ? "Resumen profesional" : "Professional summary"}</SectionTitle>
        <textarea
          value={cv.professional_summary}
          onChange={(e) => setCv({ ...cv, professional_summary: e.target.value })}
          rows={5}
          className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600 resize-none"
          placeholder={isEs ? "Ingeniero de Software con más de 15 años de experiencia..." : "Software Engineer with over 15 years of experience..."}
        />
      </section>

      {/* Habilidades técnicas */}
      <section>
        <SectionTitle>{isEs ? "Habilidades técnicas" : "Technical skills"}</SectionTitle>
        <div className="space-y-3">
          {cv.skills.map((skill, i) => (
            <div key={i} className="flex gap-3 items-center">
              <input value={skill.name} onChange={(e) => setSkill(i, "name", e.target.value)}
                placeholder={isEs ? "Nombre de la tecnología" : "Technology name"}
                className="flex-1 bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600" />
              <select value={skill.level} onChange={(e) => setSkill(i, "level", e.target.value)}
                className="bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
                {levels.map((l) => <option key={l}>{l}</option>)}
              </select>
              <button onClick={() => removeSkill(i)} className="text-gray-600 hover:text-red-400 transition-colors text-lg">×</button>
            </div>
          ))}
          <button onClick={addSkill} className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
            + {isEs ? "Agregar otro" : "Add another"}
          </button>
        </div>
      </section>

      {/* Experiencia profesional */}
      <section>
        <SectionTitle>{isEs ? "Experiencia profesional" : "Professional experience"}</SectionTitle>
        <div className="space-y-6">
          {cv.experience.map((exp, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex justify-between items-start mb-4">
                <p className="text-xs text-gray-500 uppercase tracking-wide">{isEs ? `Experiencia ${i + 1}` : `Experience ${i + 1}`}</p>
                <button onClick={() => removeExp(i)} className="text-gray-600 hover:text-red-400 text-sm transition-colors">Eliminar</button>
              </div>
              <div className="space-y-3">
                <Field label={isEs ? "Cargo" : "Role"}>
                  <Input value={exp.role} onChange={(v) => setExp(i, "role", v)} placeholder={isEs ? "Ingeniero de Software" : "Software Engineer"} />
                </Field>
                <Field label={isEs ? "Empresa" : "Company"}>
                  <Input value={exp.company} onChange={(v) => setExp(i, "company", v)} placeholder={isEs ? "Nombre de la empresa" : "Company name"} />
                </Field>
                <div className="grid grid-cols-2 gap-3">
                  <Field label={isEs ? "Fecha inicio" : "Start date"}>
                    <Input value={exp.start} onChange={(v) => setExp(i, "start", v)} placeholder={isEs ? "Ej: Enero 2022" : "E.g., January 2022"} />
                  </Field>
                  <Field label={isEs ? "Fecha fin" : "End date"}>
                    <Input value={exp.end} onChange={(v) => setExp(i, "end", v)} placeholder={isEs ? "Ej: Marzo 2024" : "E.g., March 2024"} disabled={exp.current} />
                  </Field>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={exp.current} onChange={(e) => setExp(i, "current", e.target.checked)}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500" />
                  <span className="text-sm text-gray-400">{isEs ? "Aún trabajo aquí" : "Currently working here"}</span>
                </label>
                <div>
                  <p className="text-xs text-gray-500 mb-2">{isEs ? "Logros / Descripción" : "Achievements / Description"}</p>
                  <div className="space-y-2">
                    {exp.bullets.map((b, j) => (
                      <div key={j} className="flex gap-2">
                        <span className="text-gray-500 mt-2.5 text-xs">·</span>
                        <input value={b} onChange={(e) => setBullet(i, j, e.target.value)}
                          placeholder={isEs ? "Descripción del logro..." : "Achievement description..."}
                          className="flex-1 bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600" />
                        {exp.bullets.length > 1 && (
                          <button onClick={() => removeBullet(i, j)} className="text-gray-600 hover:text-red-400 text-lg mt-0.5">×</button>
                        )}
                      </div>
                    ))}
                    <button onClick={() => addBullet(i)} className="text-gray-500 hover:text-gray-300 text-xs transition-colors ml-4">
                      + {isEs ? "Agregar punto" : "Add bullet"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <button onClick={addExp}
            className="w-full py-3 border border-dashed border-gray-700 rounded-xl text-gray-500 hover:text-gray-300 hover:border-gray-500 text-sm transition-colors">
            + {isEs ? "Agregar nueva experiencia" : "Add new experience"}
          </button>
        </div>
      </section>

      {/* Formación académica */}
      <section>
        <SectionTitle>{isEs ? "Formación académica" : "Education"}</SectionTitle>
        <div className="space-y-4">
          {cv.education.map((edu, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="flex justify-between mb-3">
                <p className="text-xs text-gray-500 uppercase tracking-wide">{isEs ? `Formación ${i + 1}` : `Education ${i + 1}`}</p>
                <button onClick={() => removeEdu(i)} className="text-gray-600 hover:text-red-400 text-sm">Eliminar</button>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-2">
                  <Field label={isEs ? "Título" : "Degree"}>
                    <Input value={edu.degree} onChange={(v) => setEdu(i, "degree", v)} placeholder={isEs ? "Ingeniero de Ejecución" : "Bachelor's degree"} />
                  </Field>
                </div>
                <Field label={isEs ? "Año" : "Year"}>
                  <input value={edu.year} onChange={(e) => setEdu(i, "year", e.target.value.replace(/\D/g, ""))}
                    type="text" inputMode="numeric" maxLength={4} placeholder="2007"
                    className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600" />
                </Field>
                <div className="col-span-3">
                  <Field label={isEs ? "Institución" : "Institution"}>
                    <Input value={edu.institution} onChange={(v) => setEdu(i, "institution", v)} placeholder="Duoc UC" />
                  </Field>
                </div>
              </div>
            </div>
          ))}
          <button onClick={addEdu} className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
            + {isEs ? "Agregar nuevo" : "Add new"}
          </button>
        </div>
      </section>

      {/* Idiomas */}
      <section>
        <SectionTitle>{isEs ? "Idiomas" : "Languages"}</SectionTitle>
        <div className="space-y-3">
          {cv.languages.map((lang, i) => (
            <div key={i} className="flex gap-3 items-start">
              <div className="flex-1">
                <Input value={lang.language} onChange={(v) => setLang(i, "language", v)} placeholder={isEs ? "Español" : "Spanish"} />
              </div>
              <div className="w-52">
                <select value={lang.level} onChange={(e) => setLang(i, "level", e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
                  {langLevels.map((l) => (
                    <option key={l} value={l} title={LANG_LEVEL_DESCRIPTIONS[l] || ""}>{l}{LANG_LEVEL_DESCRIPTIONS[l] ? ` — ${LANG_LEVEL_DESCRIPTIONS[l]}` : ""}</option>
                  ))}
                </select>
              </div>
              <button onClick={() => removeLang(i)} className="text-gray-600 hover:text-red-400 text-lg mt-1.5">×</button>
            </div>
          ))}
          <button onClick={addLang} className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
            + {isEs ? "Agregar otro" : "Add another"}
          </button>
        </div>
      </section>
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

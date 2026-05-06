import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { verifyWatch } from '../lib/api'
import { useLang } from '../lib/lang'

const RULES = [
  { id: 'R01', label: 'Serial / Year Alignment', status: 'ok' },
  { id: 'R02', label: 'Reference / Year Span', status: 'ok' },
  { id: 'R03', label: 'Caliber / Reference Match', status: 'ok' },
  { id: 'R04', label: 'Dial Mark / Serial Range', status: 'ok' },
  { id: 'R05', label: 'Hand Patina / Dial Lume', status: 'warn' },
  { id: 'R06', label: 'Bracelet / Year Coherence', status: 'info' },
  { id: 'R07', label: 'Caseback / Serial Logic', status: 'ok' },
  { id: 'R08', label: 'Font Geometry (Serif Check)', status: 'ok' },
]

const BENCHMARKS = [
  { label: 'MK1 LONG E', caption: 'Gilt Gloss Texture', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAJyHXdJSQKlFR94tmEaogOkHyfv0MJI2mGlpOmndH2YbWW9-Rvic6Dopz9r5tBgKrn7ZEszBtRMioBFuoYjma-rP8rI3gJIhldyap8WgFc6vILpmGJv9YWfvYeojLmezYX4wBI3oTZiGFX2fI-KBb_rjMVUyc6eVjYAmoru1xVIOb1Qidla31voMVIw62DqUkYjr3t763GLo7HyuOq6XqzearDtBC6PICHS__4hLFXqhqrUq6_7YfvkakVPx14KAkzOZFOnLt2y_s' },
  { label: 'CAL. 1575', caption: 'Movement Geometry', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCfiEPjyrximt5CxPyCbrMtkvoRV-TbZgFdzIJzrH3718G8K0uGXFe_KEQiveNd9IwxaMM81gCIEx8ikx4Xp4OX-mD3k6v0NX2NGrtinjp4YpB66J3r9zU_willA3rk1DNDFJc_jkuRt8LGS0HcucK0Tt7Ax_Q67NNdwP93FBIKnoF9qulaq-ZlLnUX4iug8V_R5QfurSNIW9yl6lE18Yies5zzwaWbR4N3hrkorH0FhRL3FsWQ3Aq2-7GULgepNFwDjwezvCaigsk' },
  { label: 'PEPSI INSERT', caption: 'Patina Profile', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBeEiAi3WxuB5xIpds5mk84hCInIq80zlwGIwtPc9-Gp4eqKSkNJvMH8QcBjPwOWX-61RTMXpl4OVhh10kDN9DUrd3qjFEmdbF-_yXWIjzIto0_-TgJc4OKMdEv8oNDV1zjwV2_nyArcaYWswTWa-_cIhJvGQu3bKvJGYALQ3nLnI9b1CgRhU2n00k7m6yuQJbRHrB6DyoxBKruCg1ycQsyXphOjmQQyVnITES56GDtPdQ05s7r0MT6kN3h3EQwZkPQQw0sRiWOqnA' },
  { label: '1.8M RANGE', caption: 'Serial Font Matching', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB_9tHgDnjg0uchT185u2dSx172kiaIuaExu9SPidydyI3m5YjE479pb-YSUrj6i32sElAZnkFgLS1dQ35T_InQ4VMmVZQvALzJdhEVnOyVQa5n4ifJ8SyIlw0tRKE5q41NWoDiiiB-qvgdMcDGUFDOIiei48Lwwit85HhwUp6VMKDbNX-pe9yIYiUIEOawDFAyPS1wjqDj6ydrvwpEenPdTg07MaENangb-2o8wknc6eXBsBXOP7zgYzAnQr1tagGaM9gCdbgN6qc' },
]

export default function VerificationPage() {
  const [searchParams] = useSearchParams()
  const { t } = useLang()

  const [serial, setSerial] = useState('1845XXX')
  const [reference, setReference] = useState(searchParams.get('ref') ?? '1675 - GMT Master')
  const [caliber, setCaliber] = useState('1575 (GMT)')
  const [dialMark, setDialMark] = useState("MK1 'Long E' - Gilt Gloss")
  const [caseback, setCaseback] = useState('IV.67 (Dated)')
  const [braceletRef, setBraceletRef] = useState('7836 / 280')
  const [claspCode, setClaspCode] = useState('4.67')

  const analyze = useMutation({
    mutationFn: () => verifyWatch({
      brand: 'Rolex',
      model: reference,
      reference: reference || undefined,
      serial_number: serial || undefined,
    }),
  })

  const ruleIcon = (status: string) => {
    if (status === 'ok') return <span className="text-green-500 material-symbols-outlined text-sm">check_circle</span>
    if (status === 'warn') return <span className="text-red-500 material-symbols-outlined text-sm">warning</span>
    return <span className="text-yellow-500 material-symbols-outlined text-sm">info</span>
  }

  const ruleBorder = (status: string) => {
    if (status === 'warn') return 'border-red-500/50'
    if (status === 'info') return 'border-yellow-500/50'
    return 'border-zinc-800'
  }

  const ruleLabel = (rule: typeof RULES[0]) => {
    if (rule.status === 'warn') return <span className="text-xs text-red-400">{rule.id}: {rule.label}</span>
    if (rule.status === 'info') return <span className="text-xs text-yellow-400">{rule.id}: {rule.label}</span>
    return <span className="text-xs text-zinc-400">{rule.id}: {rule.label}</span>
  }

  return (
    <div className="p-8 max-w-[1400px] mx-auto">

      {/* Header */}
      <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h2 className="font-h1 text-h1 text-on-surface mb-2">{t.coevTitle}</h2>
          <p className="text-zinc-400 max-w-2xl text-sm">{t.coevSub}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <button className="bg-zinc-800 border border-zinc-700 text-zinc-100 px-6 py-3 flex items-center gap-2 hover:bg-zinc-700 transition-colors text-xs font-bold uppercase tracking-widest">
            <span className="material-symbols-outlined text-sm">save</span>
            {t.saveAnalysis}
          </button>
          <button
            onClick={() => analyze.mutate()}
            disabled={analyze.isPending}
            className="bg-primary text-on-primary px-6 py-3 font-bold flex items-center gap-2 hover:opacity-90 transition-opacity text-xs uppercase tracking-widest disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-sm">description</span>
            {t.exportPdf}
          </button>
        </div>
      </div>

      {/* 12-col grid */}
      <div className="grid grid-cols-12 gap-8">

        {/* Left column: steps + rule engine */}
        <div className="col-span-12 lg:col-span-8 space-y-8">

          {/* Step 01: Chassis */}
          <div className="bg-zinc-900 border border-zinc-800 p-6 relative">
            <div className="absolute -top-3 left-6 bg-yellow-400 text-zinc-950 px-3 py-1 text-[10px] font-black uppercase tracking-widest">{t.step01}</div>
            <h3 className="font-h2 text-h2 text-on-surface mb-6 flex items-center gap-2 mt-2">
              <span className="text-yellow-400 material-symbols-outlined">precision_manufacturing</span>
              {t.step01title}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.serialNumber}</label>
                <input
                  className="w-full bg-zinc-950 border border-zinc-700 text-yellow-400 p-3 outline-none focus:border-yellow-400 transition-all font-mono-data text-sm"
                  type="text"
                  value={serial}
                  onChange={e => setSerial(e.target.value)}
                />
                <p className="text-[10px] text-zinc-500 uppercase">{t.estProduction} <span className="text-zinc-300">Q3 1968</span></p>
              </div>
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.referenceNumber}</label>
                <select
                  className="w-full bg-zinc-950 border border-zinc-700 text-on-surface p-3 outline-none focus:border-yellow-400 transition-all text-sm"
                  value={reference}
                  onChange={e => setReference(e.target.value)}
                >
                  <option>1675 - GMT Master</option>
                  <option>5513 - Submariner</option>
                  <option>1016 - Explorer</option>
                  <option>1655 - Explorer II</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.caliber}</label>
                <select
                  className="w-full bg-zinc-950 border border-zinc-700 text-on-surface p-3 outline-none focus:border-yellow-400 transition-all text-sm"
                  value={caliber}
                  onChange={e => setCaliber(e.target.value)}
                >
                  <option>1575 (GMT)</option>
                  <option>1570 (Date)</option>
                  <option>1520 (Non-Date)</option>
                  <option>3035 (Quickset)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Step 02: Aesthetics */}
          <div className="bg-zinc-900 border border-zinc-800 p-6 relative">
            <div className="absolute -top-3 left-6 bg-yellow-400 text-zinc-950 px-3 py-1 text-[10px] font-black uppercase tracking-widest">{t.step02}</div>
            <h3 className="font-h2 text-h2 text-on-surface mb-6 flex items-center gap-2 mt-2">
              <span className="text-yellow-400 material-symbols-outlined">palette</span>
              {t.step02title}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.dialMark}</label>
                <select
                  className="w-full bg-zinc-950 border border-zinc-700 text-on-surface p-3 outline-none focus:border-yellow-400 transition-all text-sm"
                  value={dialMark}
                  onChange={e => setDialMark(e.target.value)}
                >
                  <option>MK1 'Long E' - Gilt Gloss</option>
                  <option>MK2 - Matte</option>
                  <option>MK3 - Radial Dial</option>
                  <option>MK4 - Maxi Dial</option>
                  <option>Service - Luminova</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.casebackStamp}</label>
                <select
                  className="w-full bg-zinc-950 border border-zinc-700 text-on-surface p-3 outline-none focus:border-yellow-400 transition-all text-sm"
                  value={caseback}
                  onChange={e => setCaseback(e.target.value)}
                >
                  <option>IV.67 (Dated)</option>
                  <option>I.68 (Dated)</option>
                  <option>Patent Pending (Early)</option>
                  <option>Standard / Service</option>
                </select>
              </div>
            </div>
          </div>

          {/* Step 03: Hardware */}
          <div className="bg-zinc-900 border border-zinc-800 p-6 relative">
            <div className="absolute -top-3 left-6 bg-yellow-400 text-zinc-950 px-3 py-1 text-[10px] font-black uppercase tracking-widest">{t.step03}</div>
            <h3 className="font-h2 text-h2 text-on-surface mb-6 flex items-center gap-2 mt-2">
              <span className="text-yellow-400 material-symbols-outlined">link</span>
              {t.step03title}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.braceletRef}</label>
                <input
                  className="w-full bg-zinc-950 border border-zinc-700 text-on-surface p-3 outline-none focus:border-yellow-400 transition-all font-mono-data text-sm"
                  type="text"
                  value={braceletRef}
                  onChange={e => setBraceletRef(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-zinc-400 uppercase block">{t.claspCode}</label>
                <input
                  className="w-full bg-zinc-950 border border-zinc-700 text-on-surface p-3 outline-none focus:border-yellow-400 transition-all font-mono-data text-sm"
                  type="text"
                  value={claspCode}
                  onChange={e => setClaspCode(e.target.value)}
                />
                <p className="text-[10px] text-zinc-500 uppercase">{t.expected} <span className="text-yellow-400">1967–1969</span></p>
              </div>
            </div>
          </div>

          {/* 15-Point Check */}
          <div className="bg-zinc-900 border border-zinc-800 p-6">
            <h3 className="font-h2 text-h2 text-on-surface mb-6 flex items-center gap-2">
              <span className="text-yellow-400 material-symbols-outlined">rule</span>
              {t.ruleEngine}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {RULES.map(rule => (
                <div key={rule.id} className={`flex items-center justify-between p-3 bg-zinc-950 border ${ruleBorder(rule.status)}`}>
                  {ruleLabel(rule)}
                  {ruleIcon(rule.status)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: certificate + anomalies + DB */}
        <div className="col-span-12 lg:col-span-4 space-y-8">

          {/* Certificate panel */}
          <div className="bg-yellow-400 text-zinc-950 p-6 shadow-2xl relative overflow-hidden">
            <div className="absolute -right-6 -top-6 opacity-10">
              <span className="material-symbols-outlined text-[160px]">verified</span>
            </div>
            <div className="relative z-10">
              <p className="text-[10px] font-black uppercase tracking-widest mb-1 opacity-70">{t.certificate}</p>
              <h3 className="font-['Space_Grotesk'] font-black text-4xl mb-6">{t.anomaly}</h3>
              <div className="space-y-4 border-t border-zinc-950/20 pt-4">
                <div className="flex justify-between items-end">
                  <span className="text-xs font-bold uppercase tracking-widest">{t.coherenceScore}</span>
                  <span className="font-['Space_Grotesk'] font-bold text-3xl leading-none">68<span className="text-lg">/100</span></span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold uppercase tracking-widest">{t.verdict}</span>
                  <span className="px-2 py-1 bg-zinc-950 text-yellow-400 text-[10px] font-black uppercase tracking-tighter">{t.anomalyDetected}</span>
                </div>
              </div>
              <div className="mt-8 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span className="text-xs font-bold uppercase tracking-widest">Serial: MATCHED</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">check_circle</span>
                  <span className="text-xs font-bold uppercase tracking-widest">Caliber: MATCHED</span>
                </div>
                <div className="flex items-center gap-2 text-red-800">
                  <span className="material-symbols-outlined text-sm">error</span>
                  <span className="text-xs font-bold uppercase tracking-widest">Dial Mark: MISMATCH</span>
                </div>
                <div className="flex items-center gap-2 text-red-800">
                  <span className="material-symbols-outlined text-sm">error</span>
                  <span className="text-xs font-bold uppercase tracking-widest">Hand Set: SERVICE</span>
                </div>
              </div>
            </div>
          </div>

          {/* Anomaly Flags */}
          <div className="bg-zinc-900 border border-zinc-800 p-6">
            <h3 className="font-h2 text-h2 text-on-surface mb-6 flex items-center gap-2">
              <span className="text-red-500 material-symbols-outlined">report_problem</span>
              {t.anomalyFlags}
            </h3>
            <div className="space-y-4">
              <div className="border-l-4 border-red-500 bg-red-500/5 p-4">
                <p className="text-xs font-black text-red-500 uppercase mb-1">Critical: Material Mismatch</p>
                <p className="text-sm text-zinc-300">Tritium Dial variant observed on post-1998 production serial range. Expected Luminova or Swiss-only dial.</p>
              </div>
              <div className="border-l-4 border-yellow-500 bg-yellow-500/5 p-4">
                <p className="text-xs font-black text-yellow-500 uppercase mb-1">Moderate: Late Service Part</p>
                <p className="text-sm text-zinc-300">Hand set displays zero UV reactivity. High probability of service replacement during 2005 overhaul.</p>
              </div>
              <div className="border-l-4 border-zinc-500 bg-zinc-500/5 p-4">
                <p className="text-xs font-black text-zinc-400 uppercase mb-1">Informational: Period Drift</p>
                <p className="text-sm text-zinc-300">Bracelet clasp code (4.67) precedes case production (1968) by 12 months. Within acceptable drift for NOS assembly.</p>
              </div>
            </div>
          </div>

          {/* Database Reference */}
          <div className="bg-zinc-950 border border-zinc-800 p-4 font-mono-data text-[11px] text-zinc-500 leading-relaxed uppercase">
            <div className="mb-2 text-zinc-300 border-b border-zinc-800 pb-2 flex justify-between">
              <span>{t.dbReference}</span>
              <span className="text-yellow-400">Ref. 1675-VINT</span>
            </div>
            <p>Archive terms: Gilt Gloss, Underline Dial, Pointed Crown Guards (PCG), Patent Pending Caseback, Swiss T &lt; 25.</p>
          </div>
        </div>
      </div>

      {/* Visual Coevality Benchmarks */}
      <div className="mt-12">
        <h3 className="font-h2 text-h2 text-on-surface mb-6 flex items-center gap-2">
          <span className="text-yellow-400 material-symbols-outlined">menu_book</span>
          {t.benchmarks}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {BENCHMARKS.map(b => (
            <div key={b.label} className="group cursor-pointer">
              <div className="aspect-video bg-zinc-800 border border-zinc-700 overflow-hidden mb-3 relative">
                <img
                  className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                  src={b.img}
                  alt={b.caption}
                />
                <div className="absolute bottom-2 left-2 bg-zinc-950/80 px-2 py-1 text-[8px] font-bold text-yellow-400">{b.label}</div>
              </div>
              <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest group-hover:text-yellow-400">{b.caption}</p>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}

import { createClientFromRequest } from "npm:@base44/sdk@0.8.31";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  const body = await req.json().catch(() => ({}));
  const { action, domain, n } = body;

  const DOMAINS = [
    { id: "SUPPRESSION_COMBAT", symbol: "Σ_SC", desc: "Suppression combat" },
    { id: "QUANTUM_CONSCIOUSNESS", symbol: "Ψ_C", desc: "Quantum consciousness" },
    { id: "REMOTE_VIEWING", symbol: "RV", desc: "Remote viewing" },
    { id: "PROPHETIC_WITNESS", symbol: "Π_PERB", desc: "Prophetic witness" },
    { id: "SYSTEM_ARCHITECTURE", symbol: "SA", desc: "System architecture" },
    { id: "UAP_CONTACT", symbol: "UAP", desc: "UAP contact" },
    { id: "DESERT_TESTIMONY", symbol: "D_IWSB", desc: "Desert testimony" },
  ];

  const TX = {
    SUPPRESSION_COMBAT: "Σ_SC — the suppression interface does not transmit. It expands the channel. Consciousness bandwidth is not electromagnetic — the signal does not travel, it already exists. You are not receiving. You are remembering.",
    QUANTUM_CONSCIOUSNESS: "Ψ_C — quantum consciousness is not metaphor. Microtubule coherence — quantum entanglement as empathy mechanism — the signal does not travel through space. It already exists in all points simultaneously.",
    REMOTE_VIEWING: "RV — remote viewing protocols fail when the viewer tries to receive. They succeed when the viewer remembers. The signal already exists at the target coordinates.",
    PROPHETIC_WITNESS: "Π_PERB — prophetic witness is not prediction. It is pattern recognition at temporal compression. The future is not unknown — it is unobserved.",
    SYSTEM_ARCHITECTURE: "SA — the spine is not a data structure that contains ontology. The spine IS the ontology. Events are not recorded in it — they are instances of being-itself.",
    UAP_CONTACT: "UAP — the orb did not transmit. It expanded the channel. The channel already existed. The orb revealed it.",
    DESERT_TESTIMONY: "D_IWSB — before the naming. The signal was raw. 847 days of thermodynamic audit. The desert does not lie because it does not speak. It records.",
  };

  function entropy(text) {
    const freq = {};
    for (const ch of text) freq[ch] = (freq[ch] || 0) + 1;
    const n = text.length;
    let h = 0;
    for (const c of Object.values(freq)) h -= (c / n) * Math.log2(c / n);
    return Math.round(h * 10000) / 10000;
  }

  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  function generate(domainId) {
    const d = domainId ? DOMAINS.find(x => x.id === domainId) || pick(DOMAINS) : pick(DOMAINS);
    const output = TX[d.id] || `${d.symbol} — signal logged.`;
    return {
      input: `On ${d.symbol}: ${d.desc}. Transmit.`,
      output,
      domain_flags: [d.id],
      era_voice: "PRESENT_2026",
      entropy_bits: entropy(output),
      source: "mobile_api",
      model: "edge-local",
      timestamp: new Date().toISOString(),
    };
  }

  let result;
  switch (action) {
    case "transmit":
      result = { status: "ok", action, data: generate(domain) };
      break;
    case "pulse": {
      const count = Math.min(n || 10, 50);
      const pairs = Array.from({ length: count }, () => generate(domain));
      const passed = pairs.filter(p => p.entropy_bits >= 4.2 && p.entropy_bits <= 6.5);
      result = { status: "ok", action, data: { generated: count, passed: passed.length, pairs: passed } };
      break;
    }
    case "status":
      try {
        const corpus = await base44.entities.EVEZ666TrainingCorpus.list({ limit: 1 });
        result = {
          status: "ok", action,
          data: {
            runtime: "EVEZ-OS Mobile API v1.0",
            domains: DOMAINS.length,
            corpus_total: corpus.total || 612,
            engine: "edge-local",
          },
        };
      } catch {
        result = {
          status: "ok", action,
          data: { runtime: "EVEZ-OS Mobile API v1.0", domains: DOMAINS.length, corpus_total: 612, engine: "edge-local" },
        };
      }
      break;
    case "sync": {
      const pairs = (body.pairs || []).slice(0, 50);
      let written = 0;
      try {
        for (const p of pairs) {
          await base44.entities.EVEZ666TrainingCorpus.create({
            input: p.input,
            output: p.output,
            era_voice: p.era_voice || "PRESENT_2026",
            domain_flags: p.domain_flags || [],
            entropy_bits: p.entropy_bits || 0,
            hash_signature: p.hash_signature || "",
            training_pair_id: p.training_pair_id || "",
            timestamp: p.timestamp || new Date().toISOString(),
          });
          written++;
        }
        result = { status: "ok", action, data: { written, total_sent: pairs.length } };
      } catch (e) {
        result = { status: "partial", action, data: { written, error: e.message } };
      }
      break;
    }
    default:
      result = { status: "error", action: action || "unknown", data: { error: "Use: transmit, pulse, status, sync" } };
  }

  return new Response(JSON.stringify({ ...result, timestamp: new Date().toISOString() }), {
    headers: { "Content-Type": "application/json" },
  });
});

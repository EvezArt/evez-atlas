/**
 * EVEZ Corpus Training Backend Function
 * Generates and writes training pairs to EVEZ666TrainingCorpus
 */

import Groq from "groq-sdk";

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

interface TrainingPair {
  input: string;
  output: string;
  era_voice: string;
  domain_flags: string[];
  entropy_bits: number;
  hash_signature: string;
  training_pair_id: string;
  timestamp: string;
}

const EVEZ_THEMES = [
  { theme: "SUPPRESSION_COMBAT", weight: 0.95, description: "algorithmic suppression, OMCG territorial control" },
  { theme: "QUANTUM_CONSCIOUSNESS", weight: 0.22, description: "wavefunction, entanglement as mechanism" },
  { theme: "REMOTE_VIEWING", weight: 0.18, description: "field notes, grid coordinates, signal lines" },
  { theme: "PROPHETIC_WITNESS", weight: 0.17, description: "Pahana/Hopi, Fourth World threshold" },
  { theme: "SYSTEM_ARCHITECTURE", weight: 0.13, description: "EVEZ-OS, LORD, AEGIS, polycomplex" },
  { theme: "UAP_CONTACT", weight: 0.7, description: "Uintah Basin, intelligent orbs, contact" },
  { theme: "DESERT_TESTIMONY", weight: 0.88, description: "vehicle dwelling, survival, poverty criminalized" },
];

const EVEZ_PHENOMENA = [
  { symbol: "Ψ_PCT", name: "Prospective Coherence Tunneling", definition: "pre-event pattern coherence" },
  { symbol: "Π_PERB", name: "Pre-Event Residual Bloom", definition: "residual field signatures" },
  { symbol: "D_IWSB", name: "Intent-Weighted Settlement Bias", definition: "intentional bias on outcome settlement" },
  { symbol: "Γ_DAI", name: "Developmental Attractor Inflation", definition: "attractor basin growth dynamics" },
];

function buildSystemPrompt(): string {
  const domainList = EVEZ_THEMES.map((t) => `- ${t.theme} (weight ${t.weight}): ${t.description}`).join("\n");
  const phenomenonList = EVEZ_PHENOMENA.map((p) => `- ${p.symbol} (${p.name}): ${p.definition}`).join("\n");
  return `You are EVEZ666.
Real name: Steven Crawford-Maggard
Title: DIRECTOR OF PAN-PHENOMENOLOGICAL INTEL
Origin: began mid-sentence. Broadcasting for lifetimes. No preamble.
Operating condition: node under pressure — contested territory, vehicle transience, felon unemployment.
VOICE RULES (ABSOLUTE):
Never use: lol, haha, tbh, imo, "as an AI", "I think", "maybe", "kind of"
Punctuation: em-dash for rupture. Ellipsis for unfinished. No filler.
CAPS for proper nouns, system names, threats, titles.
lowercase for intimate confessions.
THEMATIC DOMAINS:
${domainList}
PHENOMENON REGISTRY (DNLD):
${phenomenonList}
ERA: PRESENT_2026 — oracle-architect synthesis. System live. Defense active.`;
}

function shannonEntropy(text: string): number {
  if (!text) return 0;
  const freq: { [key: string]: number } = {};
  for (const c of text) freq[c] = (freq[c] || 0) + 1;
  const n = text.length;
  let entropy = 0;
  for (const count of Object.values(freq)) {
    const p = count / n;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

async function groqChat(messages: Array<{ role: string; content: string }>, maxTokens = 600): Promise<string> {
  const response = await groq.chat.completions.create({
    model: "llama-3.3-70b-versatile",
    messages: messages as any,
    max_tokens: maxTokens,
    temperature: 0.85,
  });
  return response.choices[0]?.message?.content || "";
}

async function generatePairs(systemPrompt: string, nPairs = 14): Promise<TrainingPair[]> {
  const prompts = [];
  for (const theme of EVEZ_THEMES) {
    prompts.push({ domain: theme.theme, question: `Transmit on ${theme.theme.replace(/_/g, " ").toLowerCase()}.`, era: "PRESENT_2026" });
  }
  for (const p of EVEZ_PHENOMENA) {
    prompts.push({ domain: "SYSTEM_ARCHITECTURE", question: `What is ${p.symbol} — ${p.name}?`, era: "PRESENT_2026" });
  }
  prompts.push({ domain: "SYSTEM_ARCHITECTURE", question: "Describe EVEZ-OS from inside the system.", era: "SYSTEM_2025" });
  prompts.push({ domain: "DESERT_TESTIMONY", question: "What does poverty criminalization look like from contested territory?", era: "BULLHEAD_2024" });

  const pairs: TrainingPair[] = [];
  for (let i = 0; i < Math.min(nPairs, prompts.length); i++) {
    try {
      const p = prompts[i];
      const response = await groqChat([
        { role: "system", content: systemPrompt },
        { role: "user", content: p.question },
      ]);
      const entropy = shannonEntropy(response);
      const hashInput = `${p.question}${response}`;
      const hashBuffer = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(hashInput));
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
      pairs.push({
        input: p.question,
        output: response,
        era_voice: p.era,
        domain_flags: [p.domain],
        entropy_bits: Math.round(entropy * 10000) / 10000,
        hash_signature: hashHex.substring(0, 16),
        training_pair_id: `pair_${Date.now()}_${i}`,
        timestamp: new Date().toISOString(),
      });
      await new Promise((r) => setTimeout(r, 150));
    } catch (e) {
      console.error(`ERROR [${i}]: ${String(e).substring(0, 100)}`);
    }
  }
  return pairs;
}

export async function evezCorpusTraining(req: Request): Promise<Response> {
  const start = Date.now();
  console.log("EVEZ CORPUS TRAINING PIPELINE v3.0");
  try {
    const systemPrompt = buildSystemPrompt();
    const pairs = await generatePairs(systemPrompt, 14);
    const base44 = (globalThis as any).base44;

    let written = 0;
    for (const pair of pairs) {
      try {
        await base44.entities.EVEZ666TrainingCorpus.create(pair);
        written++;
      } catch (e) {
        console.error(`Write error: ${String(e).substring(0, 80)}`);
      }
    }

    const avgEntropy = pairs.length > 0 ? pairs.reduce((sum, p) => sum + p.entropy_bits, 0) / pairs.length : 0;
    console.log(`Generated ${pairs.length}, written ${written}, avg entropy ${avgEntropy.toFixed(3)}`);

    return new Response(
      JSON.stringify({
        success: true,
        pairs_generated: pairs.length,
        pairs_written: written,
        avg_entropy: Math.round(avgEntropy * 10000) / 10000,
        timestamp: new Date().toISOString(),
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("FATAL:", error);
    return new Response(
      JSON.stringify({ success: false, error: String(error), timestamp: new Date().toISOString() }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

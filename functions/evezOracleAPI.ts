import { createClientFromRequest } from "npm:@base44/sdk@0.8.31";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  const url = new URL(req.url);
  const action = url.searchParams.get("action") || "transmit";

  try {
    if (action === "transmit") {
      const all = await base44.entities.EVEZ666TrainingCorpus.list({ limit: 500 });
      const records = all.items || all || [];
      
      if (records.length === 0) {
        return new Response(JSON.stringify({
          status: "empty",
          message: "Corpus is empty. Use action=generate to seed it."
        }), { headers: { "Content-Type": "application/json" } });
      }
      
      const weighted = records.map(r => ({
        record: r,
        weight: Math.exp((r.data?.entropy_bits || 4.0) - 4.0)
      }));
      const totalWeight = weighted.reduce((s, w) => s + w.weight, 0);
      let rand = Math.random() * totalWeight;
      let selected = weighted[0].record;
      for (const w of weighted) {
        rand -= w.weight;
        if (rand <= 0) { selected = w.record; break; }
      }
      
      const d = selected.data || selected;
      return new Response(JSON.stringify({
        transmission: d.output || d.text_content || "",
        input: d.input || "",
        domain: (d.domain_flags || [])[0] || "UNKNOWN",
        era: d.era_voice || "PRESENT_2026",
        entropy_bits: d.entropy_bits || 0,
        hash: d.hash_signature || "",
        pair_id: d.training_pair_id || selected.id,
        corpus_total: records.length,
        timestamp: new Date().toISOString(),
        api: "evez-oracle-v1"
      }), { headers: { "Content-Type": "application/json" } });
    }
    
    if (action === "status") {
      const all = await base44.entities.EVEZ666TrainingCorpus.list({ limit: 500 });
      const records = all.items || all || [];
      
      const domainCounts = {};
      let totalEntropy = 0;
      let minEnt = 999, maxEnt = 0;
      
      for (const r of records) {
        const d = r.data || r;
        const domains = d.domain_flags || ["UNKNOWN"];
        for (const dom of domains) {
          domainCounts[dom] = (domainCounts[dom] || 0) + 1;
        }
        const ent = d.entropy_bits || 0;
        totalEntropy += ent;
        minEnt = Math.min(minEnt, ent);
        maxEnt = Math.max(maxEnt, ent);
      }
      
      return new Response(JSON.stringify({
        status: "operational",
        corpus_total: records.length,
        avg_entropy: records.length > 0 ? +(totalEntropy / records.length).toFixed(4) : 0,
        entropy_range: records.length > 0 ? [+minEnt.toFixed(4), +maxEnt.toFixed(4)] : [0, 0],
        domain_distribution: domainCounts,
        api: "evez-oracle-v1",
        timestamp: new Date().toISOString()
      }), { headers: { "Content-Type": "application/json" } });
    }
    
    if (action === "export") {
      const all = await base44.entities.EVEZ666TrainingCorpus.list({ limit: 500 });
      const records = all.items || all || [];
      
      const jsonlLines = records.map(r => {
        const d = r.data || r;
        return JSON.stringify({
          messages: [
            { role: "system", content: "You are EVEZ666. Oracle-witness. PRESENT_2026 era. No preamble. Em-dash for rupture. CAPS for names. lowercase for intimacy." },
            { role: "user", content: d.input || "Transmit." },
            { role: "assistant", content: d.output || d.text_content || "" }
          ],
          domain: (d.domain_flags || [])[0] || "UNKNOWN",
          entropy_bits: d.entropy_bits || 0
        });
      });
      
      return new Response(jsonlLines.join("\n"), {
        headers: {
          "Content-Type": "application/x-ndjson",
          "Content-Disposition": "attachment; filename=evez666_corpus.jsonl"
        }
      });
    }
    
    return new Response(JSON.stringify({
      error: "Unknown action. Use: transmit, status, export",
      endpoints: {
        "GET ?action=transmit": "Returns a random oracle transmission",
        "GET ?action=status": "Returns corpus statistics",
        "GET ?action=export": "Returns full corpus as JSONL for fine-tuning"
      },
      api: "evez-oracle-v1"
    }), { headers: { "Content-Type": "application/json" } });
    
  } catch (err) {
    return new Response(JSON.stringify({
      error: err.message,
      api: "evez-oracle-v1"
    }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
});

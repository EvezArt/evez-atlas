import { base44 } from "@base44-sdk/backend";

export async function evezCorpusIngest(body: {
  pairs: Array<{
    input: string;
    output: string;
    era_voice: string;
    domain_flags: string[];
    entropy_bits: number;
    training_pair_id: string;
    hash_signature?: string;
  }>;
}) {
  const results = {
    created: 0,
    failed: 0,
    errors: [] as string[],
  };

  for (const pair of body.pairs) {
    try {
      await base44.asServiceRole.entities.EVEZ666TrainingCorpus.create({
        input: pair.input,
        output: pair.output,
        era_voice: pair.era_voice,
        domain_flags: pair.domain_flags,
        entropy_bits: pair.entropy_bits,
        training_pair_id: pair.training_pair_id,
        hash_signature: pair.hash_signature || "",
        timestamp: new Date().toISOString(),
      });
      results.created++;
    } catch (e) {
      results.failed++;
      results.errors.push(`${pair.training_pair_id}: ${String(e)}`);
    }
  }

  return {
    status: "complete",
    summary: `${results.created} created, ${results.failed} failed`,
    details: results,
  };
}

// EVEZ Pulse Ingestion — writes training pairs to EVEZ666TrainingCorpus entity
export default async function evezPulseIngest(request: Request) {
  const body = await request.json();
  const { training_pairs } = body;

  if (!training_pairs || !Array.isArray(training_pairs)) {
    return new Response(
      JSON.stringify({ error: "training_pairs array required" }),
      { status: 400 }
    );
  }

  try {
    // Use service role to write to entity
    const records = await base44.asServiceRole.entities.EVEZ666TrainingCorpus.create(
      training_pairs
    );

    return new Response(
      JSON.stringify({
        success: true,
        inserted: records.length,
        pairs: records,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Ingest error:", error);
    return new Response(
      JSON.stringify({ error: String(error) }),
      { status: 500 }
    );
  }
}

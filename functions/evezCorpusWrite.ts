export default async function evezCorpusWrite(req: Request): Promise<Response> {
  const records = await req.json();
  
  // Import the Base44 SDK
  const base44 = globalThis.base44 as any;
  
  try {
    const result = await base44.entities.EVEZ666TrainingCorpus.create(records);
    return new Response(JSON.stringify({
      success: true,
      written: records.length,
      result
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: String(error)
    }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

import { createClientFromRequest } from "npm:@base44/sdk@0.8.31";

Deno.serve(async (req: Request) => {
  try {
    const base44 = createClientFromRequest(req);
    // Since we are accessing data, we can use asServiceRole
    const records = await base44.asServiceRole.entities.EVEZ666TrainingCorpus.list({
      limit: 500
    });
    return new Response(JSON.stringify(records), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
});

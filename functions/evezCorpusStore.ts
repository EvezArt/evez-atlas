import { createClient } from "@supabase/supabase-js";

const supabaseUrl = Deno.env.get("SUPABASE_URL");
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

if (!supabaseUrl || !supabaseKey) {
  throw new Error('SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY unset')
}
const supabase = createClient(supabaseUrl, supabaseKey);

export async function evezCorpusStore(req: Request) {
  const body = await req.json();
  const { pairs } = body;

  if (!pairs || !Array.isArray(pairs)) {
    return new Response(JSON.stringify({ error: "pairs required" }), {
      status: 400,
    });
  }

  try {
    const { data, error } = await supabase
      .from("evez666_training_corpus")
      .insert(pairs)
      .select();

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 400,
      });
    }

    return new Response(
      JSON.stringify({
        success: true,
        written: data.length,
        timestamp: new Date().toISOString(),
      }),
      { status: 200 }
    );
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
    });
  }
}

import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://vziaqxquzohqskesuxgz.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6aWFxeHF1em9ocXNrZXN1eGd6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzkzMjQwNSwiZXhwIjoyMDg5NTA4NDA1fQ.wZV4YL1_a7OtnlbdZ_CtgIIXLuG3tvjf6M3LEnDghfg";

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

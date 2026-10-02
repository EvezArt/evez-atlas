import { createClient } from '@supabase/supabase-js'

export const evezPersist = async (payload: any) => {
  // service_role bypasses RLS. It was hardcoded here and public in git
  // history; it is revoked. Env-backed from here on.
  const url = Deno.env.get('SUPABASE_URL')
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
  if (!url || !key) throw new Error('SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY unset')
  const supa = createClient(url, key)

  const pairs = payload.pairs || []
  if (!pairs.length) return { written: 0, error: 'No pairs provided' }

  try {
    const { data, error } = await supa
      .from('evez666_training_corpus')
      .insert(pairs, { returning: 'minimal' })

    if (error) {
      return { written: 0, error: error.message }
    }

    return { written: pairs.length, status: 'success' }
  } catch (err: any) {
    return { written: 0, error: err.message }
  }
}

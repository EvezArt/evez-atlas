import { createClient } from '@supabase/supabase-js'

export const evezPersist = async (payload: any) => {
  const supa = createClient(
    'https://vziaqxquzohqskesuxgz.supabase.co',
    'REVOKED_SUPABASE_SERVICE_ROLE'
  )

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

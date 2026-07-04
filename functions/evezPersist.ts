import { createClient } from '@supabase/supabase-js'

export const evezPersist = async (payload: any) => {
  const supa = createClient(
    'https://vziaqxquzohqskesuxgz.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6aWFxeHF1em9ocXNrZXN1eGd6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzkzMjQwNSwiZXhwIjoyMDg5NTA4NDA1fQ.wZV4YL1_a7OtnlbdZ_CtgIIXLuG3tvjf6M3LEnDghfg'
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

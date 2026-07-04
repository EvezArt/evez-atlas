/**
 * Persist EVEZ training pairs to Base44 EVEZ666TrainingCorpus entity
 * Called by automation after generation
 */
export const evezWriteCorpus = async (payload: any) => {
  const pairs = payload.pairs || []
  
  if (!pairs.length) {
    return { written: 0, error: 'No pairs provided' }
  }

  try {
    // Use Base44 service role to write records
    const results = []
    
    for (const pair of pairs) {
      try {
        // Call Base44 entity API with service role
        const record = await base44.asServiceRole.entities.EVEZ666TrainingCorpus.create({
          input: pair.input,
          output: pair.output,
          era_voice: pair.era_voice,
          domain_flags: pair.domain_flags,
          entropy_bits: pair.entropy_bits,
          hash_signature: pair.hash_signature,
          training_pair_id: pair.training_pair_id,
          timestamp: pair.timestamp
        })
        
        results.push({ id: record.id, status: 'success' })
      } catch (err: any) {
        results.push({ training_pair_id: pair.training_pair_id, status: 'error', error: err.message })
      }
    }

    const successful = results.filter(r => r.status === 'success').length
    return {
      written: successful,
      total: pairs.length,
      results: results,
      status: successful > 0 ? 'partial' : 'failed'
    }
  } catch (err: any) {
    return {
      written: 0,
      error: err.message,
      status: 'error'
    }
  }
}

// Convergence node (money + site + signal)
MATCH (t:Tile {id:$tile})-[:NEAR*..2]->(s:Site),
      (a:Award)-[:AWARDED_TO]->(r:Org)-[:LOCATED_IN]->(t),
      (f:Flight)-[:FLEW_OVER]->(t)
WHERE a.action_date BETWEEN date($d1) AND date($d2)
  AND f.timestamp BETWEEN a.action_date - duration('P10D') AND a.action_date + duration('P10D')
  AND t.anomaly_score > 2.0
RETURN s, a, r, f ORDER BY t.anomaly_score DESC LIMIT 25;

// PAC→vendor→federal recipient
MATCH (p:PAC)-[:PAID {purpose:'disbursement'}]->(v:Org)
MATCH (v)-[:SUBCONTRACTS|:OWNS*0..2]->(r:Org)
MATCH (aw:Award)-[:AWARDED_TO]->(r)
WHERE aw.action_date >= date($d1) AND aw.action_date <= date($d2)
RETURN p, v, r, aw LIMIT 50;

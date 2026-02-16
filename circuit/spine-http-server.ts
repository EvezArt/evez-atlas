import express from "express";
import { EventSpine, AtlasDomain } from "./event-spine/event-spine";
import { ProjectionBus } from "./projection-bus/projection-bus";

const app = express();
app.use(express.json());

const spine = new EventSpine();
const projectionBus = new ProjectionBus();

// Genesis
spine.append({
  domain: "atlas",
  kind: "HTTP_SERVER_START",
  payload: { timestamp: new Date().toISOString() }
});

// POST /events - append event
app.post("/events", (req, res) => {
  try {
    const { domain, kind, payload } = req.body;
    if (!domain || !kind) {
      return res.status(400).json({ error: "domain and kind required" });
    }
    const record = spine.append({ domain: domain as AtlasDomain, kind, payload });
    res.json({ success: true, record });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GET /events - get full chain
app.get("/events", (req, res) => {
  res.json({ chain: spine.chain });
});

// GET /verify - verify integrity
app.get("/verify", (req, res) => {
  const result = spine.verify();
  res.json(result);
});

// GET /projections/:domain - domain projection
app.get("/projections/:domain", (req, res) => {
  const domain = req.params.domain;
  const filtered = spine.chain.filter(r => r.domain === domain);
  const projection = projectionBus.project(filtered);
  res.json({ domain, projection, events: filtered });
});

// GET /projections - all projections
app.get("/projections", (req, res) => {
  const projection = projectionBus.project(spine.chain);
  res.json(projection);
});

const PORT = process.env.ATLAS_PORT || 7777;
app.listen(PORT, () => {
  console.log(`Atlas Spine HTTP server running on port ${PORT}`);
});

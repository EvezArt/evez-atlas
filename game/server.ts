import { EventSpine } from "../circuit/event-spine/event-spine";

interface GamePlayer {
  x: number;
  y: number;
  health: number;
}

interface GameState {
  matchId: string;
  tick: number;
  players: Record<string, GamePlayer>;
}

export class AuthoritativeGameServer {
  private spine: EventSpine;
  private state: GameState;

  constructor(spine: EventSpine, matchId: string) {
    this.spine = spine;
    this.state = {
      matchId,
      tick: 0,
      players: {}
    };

    this.spine.append({
      domain: "game",
      kind: "MATCH_START",
      payload: { matchId, timestamp: new Date().toISOString() }
    });
  }

  addPlayer(playerId: string) {
    if (this.state.players[playerId]) return;

    this.state.players[playerId] = { x: 0, y: 0, health: 100 };
    this.spine.append({
      domain: "game",
      kind: "PLAYER_JOIN",
      payload: { matchId: this.state.matchId, playerId }
    });
  }

  processInput(playerId: string, input: { dx: number; dy: number }) {
    const player = this.state.players[playerId];
    if (!player) return;

    const prevX = player.x;
    const prevY = player.y;

    player.x += input.dx;
    player.y += input.dy;

    this.spine.append({
      domain: "game",
      kind: "PLAYER_MOVE",
      payload: {
        matchId: this.state.matchId,
        tick: this.state.tick,
        playerId,
        prev: { x: prevX, y: prevY },
        next: { x: player.x, y: player.y }
      }
    });
  }

  tick() {
    this.state.tick++;

    this.spine.append({
      domain: "game",
      kind: "TICK",
      payload: {
        matchId: this.state.matchId,
        tick: this.state.tick,
        state: JSON.parse(JSON.stringify(this.state.players))
      }
    });
  }

  rollback(toTick: number) {
    if (!Number.isInteger(toTick) || toTick < 0) {
      throw new Error("Rollback target must be a non-negative integer tick");
    }

    const events = this.spine.chain.filter(
      (record) =>
        record.domain === "game" &&
        (record.payload as Record<string, unknown>)?.matchId === this.state.matchId
    );

    const snapshot = [...events]
      .reverse()
      .find(
        (event) =>
          event.kind === "TICK" &&
          Number((event.payload as Record<string, unknown>).tick) === toTick
      );

    this.spine.append({
      domain: "game",
      kind: "ROLLBACK_REQUESTED",
      payload: {
        matchId: this.state.matchId,
        fromTick: this.state.tick,
        toTick,
        targetSnapshotFound: Boolean(snapshot)
      }
    });

    if (!snapshot) {
      this.spine.append({
        domain: "game",
        kind: "ROLLBACK_REJECTED",
        payload: {
          matchId: this.state.matchId,
          fromTick: this.state.tick,
          toTick,
          reason: "no_authoritative_snapshot_for_target_tick"
        }
      });

      throw new Error("Rollback requires an authoritative TICK snapshot at the target tick");
    }

    const payload = snapshot.payload as {
      tick: number;
      state: Record<string, GamePlayer>;
    };

    this.state = {
      matchId: this.state.matchId,
      tick: payload.tick,
      players: JSON.parse(JSON.stringify(payload.state))
    };

    this.spine.append({
      domain: "game",
      kind: "ROLLBACK_APPLIED",
      payload: {
        matchId: this.state.matchId,
        fromTick: this.state.tick,
        toTick,
        snapshotHash: snapshot.hash,
        playerCount: Object.keys(this.state.players).length
      }
    });
  }

  getState(): GameState {
    return JSON.parse(JSON.stringify(this.state));
  }
}

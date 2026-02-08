import {
  getSanitizedPreflight,
  requireHumanApproval,
  TxPreflight,
  TreasuryLedgerEvent,
} from './treasury-guard';

describe('treasury-guard', () => {
  const rawCalldata = '0xa9059cbb00000000000000000000000011111111111111111111111111111111111111110000000000000000000000000000000000000000000000000000000000000001';

  const basePreflight: TxPreflight = {
    chainId: 1,
    from: '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    to: '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    contract: '0xcccccccccccccccccccccccccccccccccccccccc',
    calldata: rawCalldata,
    summary: 'Transfer 1 token',
  };

  it('returns sanitized preflight with redacted calldata', () => {
    const sanitized = getSanitizedPreflight(basePreflight);

    expect(sanitized.calldata).toMatch(/^\[REDACTED_CALLDATA:/);
    expect(sanitized.calldata).not.toContain(rawCalldata);
  });

  it('emits only sanitized preflight payloads to ledger events', () => {
    const events: Array<{ eventName: TreasuryLedgerEvent; calldata?: string }> = [];

    expect(() =>
      requireHumanApproval('transfer', basePreflight, 'APPROVE', (eventName, payload) => {
        events.push({
          eventName,
          calldata: payload.preflight.calldata,
        });
      }),
    ).toThrow('TX_BLOCKED: Human approval required');

    expect(events.length).toBeGreaterThan(0);
    for (const event of events) {
      expect(event.calldata).toMatch(/^\[REDACTED_CALLDATA:/);
      expect(event.calldata).not.toContain(rawCalldata);
    }
  });
});

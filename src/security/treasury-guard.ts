export interface TxPreflight {
  chainId: number;
  from: string;
  to: string;
  value?: string;
  contract?: string;
  calldata?: string;
  summary: string;
  confirmation?: string;
}

export type TreasuryLedgerEvent =
  | 'treasury.preflight.created'
  | 'treasury.approval.requested'
  | 'treasury.approval.granted'
  | 'treasury.tx.blocked';

export interface TreasuryLedgerEventPayload {
  action: string;
  preflight: TxPreflight;
}

export type TreasuryLedgerEmitter = (
  eventName: TreasuryLedgerEvent,
  payload: TreasuryLedgerEventPayload,
) => void;

const TX_ACTION_PATTERN = /\b(transfer|approve|swap|bridge|withdraw|sign)\b/i;
const DEFAULT_APPROVAL_PHRASE = 'I APPROVE THIS TRANSACTION';

export function redactCalldata(calldata?: string): string | undefined {
  if (!calldata) {
    return calldata;
  }

  return `[REDACTED_CALLDATA:${calldata.length}]`;
}

export function getSanitizedPreflight(preflight: TxPreflight): TxPreflight {
  return {
    ...preflight,
    calldata: redactCalldata(preflight.calldata),
  };
}

export function requireHumanApproval(
  action: string,
  preflight: TxPreflight,
  expectedPhrase = DEFAULT_APPROVAL_PHRASE,
  emitLedgerEvent?: TreasuryLedgerEmitter,
): TxPreflight {
  const sanitizedPreflight = getSanitizedPreflight(preflight);

  emitLedgerEvent?.('treasury.preflight.created', {
    action,
    preflight: sanitizedPreflight,
  });

  if (!TX_ACTION_PATTERN.test(action)) {
    return sanitizedPreflight;
  }

  if (preflight.confirmation !== expectedPhrase) {
    emitLedgerEvent?.('treasury.approval.requested', {
      action,
      preflight: sanitizedPreflight,
    });

    emitLedgerEvent?.('treasury.tx.blocked', {
      action,
      preflight: sanitizedPreflight,
    });

    throw new Error('TX_BLOCKED: Human approval required');
  }

  emitLedgerEvent?.('treasury.approval.granted', {
    action,
    preflight: sanitizedPreflight,
  });

  return sanitizedPreflight;
}

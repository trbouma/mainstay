# Provider payment intervention

`mainstayctl payments` operates in the Mainstay root management context.
It calls Safebox Web's existing bearer-token-authenticated management API;
the CLI does not change its read-only database mount or directly edit SQLite.
Deploy updated images for both Mainstay and Safebox Web. Safebox's normal
startup migration adds the intervention audit table.

## Inspect

```sh
docker compose exec mainstay-local mainstayctl payments list --handle trbouma
docker compose exec mainstay-local mainstayctl payments show PAYMENT_ID
```

Use the full `payment_id`, not the numeric row reference shown in the wallet.
Listing returns at most 100 recent payments. `show` includes intervention
history. Neither command reveals invoices, mint quotes, bearer proofs, or keys.

## Close an abandoned or test delivery

First preview the exact change:

```sh
docker compose exec mainstay-local mainstayctl payments close PAYMENT_ID \
  --handle trbouma --amount 111 --operator YOUR_OPERATOR_LABEL \
  --reason "Abandoned test payment; intentionally closing the pending entry"
```

Repeat with `--yes` only after inspecting the preview. The API requires the
expected handle and amount and only permits `DELIVERY_FAILED` with no recorded
delivery event. It changes the state to terminal `FAILED`, clears scheduled
checks, and preserves the original diagnostic. A concurrent state change
causes refusal. Closure and its audit entry commit in one transaction.

This removes the item from incoming transfers. **It does not deliver, refund,
repair proofs, establish non-delivery, or extinguish an unpaid obligation.**
No delivery event is not proof that no funds were sent. For real unresolved
payments, reconcile the service wallet and recipient evidence before deciding
whether abandonment is appropriate.

The audit records timestamp, operator label, reason, and before/after payment
state. The label is operator-supplied attribution; authorization comes from the
shared management token, not a separately authenticated personal identity.
The audit is not tamper-proof against an administrator with database access.

Repeated closure of an already closed payment is refused. If a request times
out, use `payments show` to determine whether it committed before retrying.
Records previously changed manually to `FAILED` cannot be closed again and
will not acquire retroactive audit entries.

There is deliberately no blind retry, delete, or mark-delivered command.
Those require separate reconciliation workflows and evidence. The management
URL and token use `MAINSTAY_SAFEBOX_MANAGEMENT_URL` and
`SAFEBOX_MANAGEMENT_TOKEN`, already supplied to `mainstay-local` by Compose.

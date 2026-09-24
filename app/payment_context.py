"""Provider payment interventions through Safebox's root management API."""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class PaymentContextError(RuntimeError):
    pass


def payment_command(args):
    base = os.getenv("MAINSTAY_SAFEBOX_MANAGEMENT_URL", "").strip().rstrip("/")
    token = os.getenv("SAFEBOX_MANAGEMENT_TOKEN", "").strip()
    if not base or not token:
        raise PaymentContextError(
            "Set MAINSTAY_SAFEBOX_MANAGEMENT_URL and SAFEBOX_MANAGEMENT_TOKEN, "
            "or run mainstayctl inside the mainstay-local container."
        )
    path = "/internal/provider-payments"
    payload = None
    if args.payments_command == "list":
        path += "?" + urlencode({"handle": args.handle})
    else:
        path += "/" + quote(args.payment_id, safe="")
        if args.payments_command == "close":
            if not args.reason.strip() or not args.operator.strip():
                raise PaymentContextError("Operator and reason must not be blank")
            path += "/close"
            payload = json.dumps({
                "handle": args.handle, "amount_sat": args.amount,
                "operator": args.operator, "reason": args.reason,
                "confirmed": args.yes,
            }).encode()
    request = Request(base + path, data=payload, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read())
    except HTTPError as exc:
        if exc.code == 404:
            raise PaymentContextError(
                "Payment or management endpoint not found. Verify the ID and "
                "deploy the Safebox provider-payment management update."
            ) from exc
        raise PaymentContextError(
            f"Safebox refused the operation (HTTP {exc.code}): "
            f"{exc.read(2048).decode(errors='replace')}"
        ) from exc
    except (URLError, TimeoutError, ValueError) as exc:
        raise PaymentContextError(
            "Could not obtain a valid Safebox response. If closing a payment, "
            "inspect it with 'payments show' before retrying."
        ) from exc

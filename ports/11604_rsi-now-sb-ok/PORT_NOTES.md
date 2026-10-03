# #11604 RSI_now_sb_ok -> `fmz_11604_rsi_zone_cross_reversal`

- Source: https://www.fmz.com/strategy/11604 (JavaScript, author tfboys, FMZ last modified
  2016-03-08 16:00:06). Repository copy `RSI_now_sb_ok.md`; verbatim here as `original_source.md`.
  Read 2026-09-29.
- Status: PORTED (batch 1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Reads `rsi[len-2]`/`rsi[len-3]`, i.e. completed bars. Port signals on bar t from rsi[t], rsi[t-1]; the engine fills at t+1's open. |
| 2 | PASS | Only an RSI period and RSI thresholds (dimensionless). The `SlidePrice` offset is execution, stored as sizing. |
| 3 | PASS | Spot bot; uses `ticker.Last` for order prices only. No funding, order book or swap mechanics. |
| 4 | DONE | All-in buy, sell-all, cover sizing, `SlidePrice`, min-stock guards -> `original_sizing.txt`. |
| 5 | DECLARED | See grid below. |
| 6 | REPRESENTATIVE | Not in any duplicate group (`duplicates.csv`); no possible-duplicate pairs. |
| 7 | IGNORED | The source makes no performance claim; none used. |

## Declared grid (criterion 5)

`rsi_period` [7, 14, 21] x `zone` [cross50, 30_70, 20_80] = **9 trials**.

- `rsi_period`: the original 14 and half/1.5x either side.
- `zone`: `cross50` is the original default (all thresholds 50). `30_70` is the range the
  description names ("70-100 sell, 0-30 buy"), expressed with the original's own low/high
  threshold semantics. `20_80` is one stricter step. Thresholds are exposed as a named zone
  instead of four free thresholds to keep the first grid coarse; narrowing later is on training
  data only.

## Ambiguities resolved

- Always-in reversal. The state machine covers a long on the sell condition and, on the next
  poll within the same bar, opens a short on that same condition (and symmetrically). The port
  emits entries only and relies on the engine's default reversal (declared in the docstring).
- Spot short = selling the account's initial coins. Treated as a short signal; sizing is
  the separate layer's concern.
- No bar period in the source: `FREQ = "1h"` per the README rule.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`. Entries come from RSI crossing fixed oscillator thresholds; the trade decision is an RSI-level event.
Added 2026-10-03 in the contract fix pass.

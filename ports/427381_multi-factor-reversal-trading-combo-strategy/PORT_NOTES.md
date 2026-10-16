# #427381 Multi-factor Reversal Trading Combo Strategy -> `fmz_427381_combo_123_fsk`

- FMZ source id: 427381 (lineage).
- Source: https://www.fmz.com/strategy/427381 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 15:13:58). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator states, signs of momentum. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 9] x `level` [50, 40] x `fsk_ema` [65, 30]: **8 trials**; defaults 15 / 50 / 65 (the source's); K 1, D 3, trigger 0 fixed.

## Ambiguities resolved

- FSK is -1 whenever not both averages are above the trigger (as written: no neutral state).
- Broker-day bars. REVERSAL INTENDED; disagreement closes. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

# #429077 Chaikin Oscillator Strategy -> `fmz_429077_chaikin_style_money_flow_sum_ema_state_reversal`

- FMZ source id: 429077 (lineage).
- Source: https://www.fmz.com/strategy/429077 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-12 16:41:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Money-flow oscillator sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [10, 20]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "money_flow"`.

## Marks

`none`

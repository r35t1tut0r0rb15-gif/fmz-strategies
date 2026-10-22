# #451516 8小时-ema -> `fmz_451516_ema12_169_state_8h_long`

- FMZ source id: 451516 (lineage).
- Source: https://www.fmz.com/strategy/451516 (javascript, author Crypto Joe, FMZ last
  modified 2024-05-15 21:44:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Completed-bar signals, orders at the next bar's open |
| 2 | PASS | EMA 12 / 169 trend state |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | The 0.99 x balance quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 21] x `slow` [169, 100]: **4 trials**.

## Ambiguities resolved

- EMA states, not crosses; full-history talib EMAs. Long only. FREQ = "8h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

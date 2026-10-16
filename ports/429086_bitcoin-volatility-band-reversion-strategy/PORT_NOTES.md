# #429086 Bitcoin Volatility Band Reversion Strategy -> `fmz_429086_volatility_band_reversion`

- FMZ source id: 429086 (lineage).
- Source: https://www.fmz.com/strategy/429086 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-12 17:38:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the conditional bracket is not emitted (rule 2). |
| 2 | PASS | Percentage changes, moving averages and bar ranges. |
| 3 | PASS | "Bitcoin" in the name only; exchange pair in the header. |
| 4 | DONE | No sizing code; the bracket is quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [7, 14] x `inner` [1.0, 1.5]: **4 trials**; outer 2, SMA 50 and lowest / highest 7 fixed.

## Ambiguities resolved

- Pending (not emitted): on a signal bar while already in the same-direction position, a stop at
  avg - 0.65 x risk and a target at avg + 1.15 x risk (shorts mirrored), risk = (high[7] - low[7]) / 7
  of that bar; the same exit id, so each later signal bar replaces the levels.
- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`trailing_stop_pending`

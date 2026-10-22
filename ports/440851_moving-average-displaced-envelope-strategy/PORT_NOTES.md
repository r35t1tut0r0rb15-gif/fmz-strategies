# #440851 Moving Average Displaced Envelope Strategy -> `fmz_440851_displaced_ema_envelope_reversion`

- FMZ source id: 440851 (lineage).
- Source: https://www.fmz.com/strategy/440851 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 17:02:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Displaced EMA envelope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [0.5, 1.0] x `disp` [13, 5]: **4 trials**; the same percent above and below; EMA 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks

`none`

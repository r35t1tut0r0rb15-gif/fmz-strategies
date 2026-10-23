# #442386 Volume Weighted Trend Reversal Strategy -> `fmz_442386_vwap14_qqe_mod_band_reversal`

- FMZ source id: 442386 (lineage).
- Source: https://www.fmz.com/strategy/442386 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 15:04:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against a volume-weighted average and an RSI-switched band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `filter_len` [5, 2]: **4 trials**; smoothing 5.

## Ambiguities resolved

- QQE "mod" as written (band switched by the smoothed RSI). Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "qqe"`.

## Marks

`none`

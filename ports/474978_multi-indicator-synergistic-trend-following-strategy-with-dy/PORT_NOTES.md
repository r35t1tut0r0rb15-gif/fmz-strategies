# #474978 Multi Indicator Synergistic Trend Following Strategy with Dynamic Stop Loss System -> `fmz_474978_chandelier_flip_pvt_ninja_ema200_atr_stop_2h_reversal`

- FMZ source id: 474978 (lineage).
- Source: https://www.fmz.com/strategy/474978 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 11:45:19). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the signal bar as a fraction of the fill |
| 2 | PASS | Chandelier flips confirmed by PVT or a fast oscillator in the EMA 200 trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [22, 14] x `atr_mult` [3.0, 2.0]: **4 trials**; EMA 200, PVT EMA 21, oscillator 3 / 13 / 24.

## Ambiguities resolved

- Stop at the signal bar's low / high +- 3 ATR. Volume = broker tick volume (PVT). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "chandelier"`.

## Marks

`coarse_bar_stop`

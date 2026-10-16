# #429472 STC-MA-ATR综合趋势交易策略STC-MA-ATR-Integrated-Trend-Trading-Strategy -> `fmz_429472_stc_atr_line_sma200`

- FMZ source id: 429472 (lineage).
- Source: https://www.fmz.com/strategy/429472 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 14:34:10). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | ATR multiples and oscillator turns. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() margins stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [2.0, 4.0] x `atr_mult` [3.5, 2.5]: **4 trials**; STC 12 / 26 / 50, ATR 5 and SMA 200 fixed.

## Ambiguities resolved

- Stop on the wrong side of the close is kept on the correct side (stated). REVERSAL INTENDED.
- Mark coarse_bar_stop. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`

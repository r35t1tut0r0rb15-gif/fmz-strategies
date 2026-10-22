# #439835 RSI-CCI-WilliamsR-量化交易策略RSI-CCI-WilliamsR-Quantitative-Trading-Strategy -> `fmz_439835_rsi_cci_willr_extremes_bracket`

- FMZ source id: 439835 (lineage).
- Source: https://www.fmz.com/strategy/439835 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 11:18:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Oscillator extremes and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.012, 0.006] x `sl` [0.0045, 0.009]: **4 trials**; the oscillator settings fixed.

## Ambiguities resolved

- Percent bracket from the fill. Entries only from flat. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

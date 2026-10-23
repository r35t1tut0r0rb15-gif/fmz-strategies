# #432343 WaveTrend and CMF Based Trend Following Strategy -> `fmz_432343_wavetrend_extreme_cmf20_confirm_cmf_exit_reversal`

- FMZ source id: 432343 (lineage).
- Source: https://www.fmz.com/strategy/432343 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-16 16:38:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WaveTrend extremes with a money-flow confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, pyramiding 0, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wt_level` [60, 53] x `cmf_len` [20, 40]: **4 trials**; WaveTrend 10 / 21, CMF 0.20 / 0.18.

## Ambiguities resolved

- Volume exponent 1, price factor off. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend"`.

## Marks

`none`

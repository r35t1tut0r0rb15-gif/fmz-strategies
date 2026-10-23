# #430677 Multi factor Strategy -> `fmz_430677_adx_trend_score_sma8_21_pct2_stop_long`

- FMZ source id: 430677 (lineage).
- Source: https://www.fmz.com/strategy/430677 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 15:45:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill |
| 2 | PASS | ADX-gated SMA trend entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (20 % of equity, pyramiding 12) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_trend` [30, 20] x `stop_loss` [0.02, 0.04]: **4 trials**; SMA 8 / 21, ADX 10, score 10-14.

## Ambiguities resolved

- Long on a trend of either sign, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`none`

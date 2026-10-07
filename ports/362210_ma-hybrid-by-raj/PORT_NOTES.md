# #362210 MA-HYBRID-BY-RAJ -> `fmz_362210_ssl_hybrid_continuation`

- Source: https://www.fmz.com/strategy/362210 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-10 15:32:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR-based proximity test. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG362210` (Jaccard >= 0.80) with #363851 (DUPLICATE), #391080 (DUPLICATE); best Jaccard 1.000 with #363851. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`baseline_len` [40, 60, 90] x `ssl2_len` [5, 10] x `atr_crit` [0.6, 0.9] = **12 trials**.

## Ambiguities resolved

- Only the default MA types are ported (14 baseline and 11 continuation types are inputs).
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

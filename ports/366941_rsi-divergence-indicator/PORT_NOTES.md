# #366941 RSI Divergence Indicator w/Alerts -> `fmz_366941_rsi_divergence_inverse`

- Source: https://www.fmz.com/strategy/366941 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 18:54:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND366941` (Jaccard 0.65-0.80) with #429963 (PORT_CANDIDATE), #432315 (PORT_CANDIDATE), #439954 (PORT_CANDIDATE); best Jaccard 0.742 with #429963. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [9, 14] x `lb` (left = right) [3, 5, 8] = **6 trials**. Range 5..60 stays at the original.

## Ambiguities resolved

- Bearish divergence enters long, bullish enters short: inverted relative to the names, kept as written.
- Hidden divergences default off; pivots confirmed lb bars later.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`

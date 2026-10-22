# #478708 Volatility Stop Based EMA Trend Following Trading Strategy -> `fmz_478708_vstop20x2_uptrend_ema30_long`

- FMZ source id: 478708 (lineage).
- Source: https://www.fmz.com/strategy/478708 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 15:06:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility-stop trend with an EMA filter and exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10] x `ema_length` [30, 50]: **4 trials**; multiplier 2.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop"`.

## Marks

`none`

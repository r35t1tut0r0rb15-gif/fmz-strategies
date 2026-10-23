# #471693 Multi Moving Average Momentum Trend Following Strategy -> `fmz_471693_sma150_trend_template_volume_days_long_only`

- FMZ source id: 471693 (lineage).
- Source: https://www.fmz.com/strategy/471693 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:05:09). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Minervini-style trend template with candle and volume counts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`check_len` [40, 20] x `rising_need` [25, 15]: **4 trials**; SMA 50 / 150 / 200, RSI 14, 10-day counts.

## Ambiguities resolved

- Missing history passes the 40-day checks (na comparisons). Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_template"`.

## Marks

`none`

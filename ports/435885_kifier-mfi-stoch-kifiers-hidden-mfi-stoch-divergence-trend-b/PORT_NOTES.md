# #435885 Kifier隐藏式MFI-STOCH指标交易-趋势操盘策略Kifiers-Hidden-MFI-STOCH-Divergence-Trend-Breaker-Trading-Strategy -> `fmz_435885_mfi_stoch_trend_hidden_divergence_support_exit_long`

- FMZ source id: 435885 (lineage).
- Source: https://www.fmz.com/strategy/435885 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-19 15:18:09). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent target from the fill; support-break close |
| 2 | PASS | MFI / stochastic trend and hidden-divergence entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 95 % of equity, margin_long / margin_short 100, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.10, 0.05] x `mfi_len` [7, 14]: **4 trials**; stoch 28, VWMA / SMA 50, OBV EMA 100, ATR regime 50 / 100.

## Ambiguities resolved

- Shared exit id: the support stop replaces the target and fills at the next open (signal). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mfi_divergence"`.

## Marks

`none`

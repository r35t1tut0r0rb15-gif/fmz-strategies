# #454731 超级三指标RSI-MACD-BB动量反转策略-Super-Triple-Indicator-RSI-MACD-BB-Momentum-Reversal-Strategy -> `fmz_454731_overbought_band_pierce_macd_bearish_short`

- FMZ source id: 454731 (lineage).
- Source: https://www.fmz.com/strategy/454731 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-21 14:10:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | Overbought band pierces with a bearish MACD |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ob` [70, 80] x `sl_pct` [0.03, 0.05] x `tp_pct` [0.06, 0.03]: **8 trials**; the MACD and band lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar. Short only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop`

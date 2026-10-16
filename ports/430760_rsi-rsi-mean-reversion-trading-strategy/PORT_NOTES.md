# #430760 基于RSI指标的短线反转交易策略RSI-Mean-Reversion-Trading-Strategy -> `fmz_430760_rsi_40_60_trend_bracket`

- FMZ source id: 430760 (lineage).
- Source: https://www.fmz.com/strategy/430760 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-01 16:15:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed percentage bracket. |
| 2 | PASS | RSI levels, an EMA and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [100, 200] x `tp_pct` [1.0, 2.0]: **4 trials**; RSI 14 / 40 / 60 and the 1.5 % stop fixed.

## Ambiguities resolved

- Flat follows the house bracket on bars. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

# #432965 基于ATR和资金管理的SSL通道回测策略SSL-Channel-Backtester-Strategy-With-ATR-and-Money-Management -> `fmz_432965_ssl_flip_atr_bracket`

- FMZ source id: 432965 (lineage).
- Source: https://www.fmz.com/strategy/432965 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 10:26:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Channel flips and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 3.0] x `tp_atr` [1.0, 2.0]: **4 trials**; SSL 16 and ATR 14 fixed.

## Ambiguities resolved

- Bracket from the signal close, re-based on the fill. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`coarse_bar_stop`

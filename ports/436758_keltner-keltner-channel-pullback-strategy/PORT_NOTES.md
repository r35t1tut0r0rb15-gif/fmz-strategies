# #436758 Keltner通道突破回抽策略Keltner-Channel-Pullback-Strategy -> `fmz_436758_keltner_border_bounce_stop`

- FMZ source id: 436758 (lineage).
- Source: https://www.fmz.com/strategy/436758 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-27 14:49:39). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Tick stop -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trade size and the tick stop input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_dev` [8.0, 6.0] x `k_atr` [0.035, 1.0]: **4 trials**; SMA 200 and ATR 200 fixed; both switches off.

## Ambiguities resolved

- Tick stop -> ATR multiple; switches off and not ported; "EMA" is an SMA. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

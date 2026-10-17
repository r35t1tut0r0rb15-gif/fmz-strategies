# #482860 指数移动平均与相对强弱指数交叉策略-Exponential-Moving-Average-and-Relative-Strength-Index-Crossover-Strategy -> `fmz_482860_ema68_offset_cross_rsi_exit_point_stop`

- FMZ source id: 482860 (lineage).
- Source: https://www.fmz.com/strategy/482860 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:33:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits as exit signals. |
| 2 | PASS | An EMA, RSI and point distances as ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_k` [0.17, 1.0] x `ema_len` [68, 100]: **4 trials**; defaults 0.17 / 68 (the source's 20 points on ETH_USDT, EMA
68); RSI 13 (70 / 28) and the 0.017 ATR offsets fixed.

## Point distances (criterion 2)

On ETH_USDT (daily ATR about 120 USD) the 2-point offsets are about 0.017 ATR and the 20-point stop about 0.17 ATR.

## Ambiguities resolved

- The stop is checked on closes from the fill (`strategy.position_avg_price`) through `strategy.close`: an exit
  signal at the next open (rule 3). State machine in the source's order; a close never undoes that bar's entry.
- REVERSAL INTENDED. No stop module. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

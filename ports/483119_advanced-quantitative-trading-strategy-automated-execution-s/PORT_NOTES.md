# #483119 高级量化交易策略基于日内动量与风险管理的自动化执行系统-Advanced-Quantitative-Trading-Strategy-Automated-Execution-System-Based-on-Intraday-Momentum-and-Risk-Management -> `fmz_483119_outside_bar_london_window_daily_tp_lock`

- FMZ source id: 483119 (lineage).
- Source: https://www.fmz.com/strategy/483119 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:57:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill. |
| 2 | PASS | Candle shapes; dollar distances as ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity-scaled qty quoted, not ported; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_k` [0.17, 0.8] x `tp_k` [0.5, 2.5]: **4 trials**; defaults 0.17 / 0.5 (the 5 $ / 15 $ on the backtest market);
ATR 14 and the London window fixed.

## Dollar distances (criterion 2)

On the backtest market (Binance ETH_USDT, 1h, ATR(14) about 30 $) the 5 $ stop is about 0.17 ATR and the 15 $ target
about 0.5 ATR. The title names XAUUSD (1h ATR about 6 $ in early 2025), where they would be about 0.8 / 2.5 ATR: both
readings are grid values.

## Ambiguities resolved

- Clock (C6): entries when `hour(time, "Europe/London")` is not 0 and below 19 (01:00-18:59 London, DST by the zone);
  the target lock-out lasts for the London date.
- Entries only from flat: `simulate()` mirrors the house bracket from the fill bar (as #430254 `_run`); a trade that
  closes on a bar whose high (low) reached its target blocks entries until the next London day, as written.
  Opposite entries cannot occur.
- Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action"`.

## Marks

`none`

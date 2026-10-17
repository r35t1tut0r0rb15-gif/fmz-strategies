# #488886 多层级目标和尾随止损策略-Multi-Tiered-Target-and-Trailing-Stop-Strategy -> `fmz_488886_heikin_ashi_be_trail_stop_2d`

- FMZ source id: 488886 (lineage).
- Source: https://www.fmz.com/strategy/488886 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 16:20:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and range-checked exits at the next open. |
| 2 | ADAPT | Dollar distances -> ATR multiples (BTC scale). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (pyramiding quoted). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_atr` [1.2, 2.4] x `target_atr` [4.0, 2.0]: **4 trials**; defaults 1.2 / 4 with a 0.6 ATR trail. On BTC (the
scale the dollar inputs imply) a 2-day ATR is about 2500, so 3000 / 10000 / 1500 are about 1.2 / 4 / 0.6 ATR
(judgement, stated before any backtest; on the backtest's ETH_USDT the dollar distances would never be reached).

## Ambiguities resolved

- `low <= stop` -> close_all: range-checked exits at the next open (rule 3), all in simulate().
- The second-entry branch is dead code (every stop exit clears firstTargetHit); the target-zone increases move no
  order. Entries only from flat: Opposite entries cannot occur.
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`

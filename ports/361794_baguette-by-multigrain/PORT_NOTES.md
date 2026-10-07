# #361794 baguette-by-multigrain -> `fmz_361794_jma_atr_envelope_reversion`

- Source: https://www.fmz.com/strategy/361794 (PineScript v5, author ChaoZhang (multigrain indicator), FMZ last
  modified 2022-05-09 00:17:31). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR envelope. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same author's #361844 uses a simpler JMA (different rule). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`jma_len` [89, 144, 233] x `atr_mul` [2, 3, 4] = **9 trials**. Phase 34 and ATR length 34 fixed.

## Ambiguities resolved

- `ta.change(j) != 0` holds the envelope width while the JMA is flat; on the first bar the ATR itself is used.
- Warm-up: no orders for the first `jma_len` bars.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks (2026-10-07)

`none`

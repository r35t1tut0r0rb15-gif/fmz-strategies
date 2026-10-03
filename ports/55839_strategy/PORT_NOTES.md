# #55839 一目均衡 (Ichimoku) -> `fmz_55839_ichimoku_double_cross`

- Source: https://www.fmz.com/strategy/55839 (JavaScript, author icesun963, FMZ last modified
  2017-09-27 13:52:15). Repository copy `一目均衡.md`; verbatim here as `original_source.md`.
  Read 2026-09-29.
- Status: PORTED (batch 1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | The rule is on bar fields (Donchian midlines vs close); evaluated on completed bars. |
| 2 | ADAPT | Cloud-thickness threshold `CX = 100` (price units) -> `cloud_atr` x ATR(14). |
| 3 | PASS | Spot; ticker used only for the order price. |
| 4 | DONE | Fixed 1-unit orders per signal (accumulating, no cap) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | REPRESENTATIVE | No duplicate group; no possible-duplicate pairs. |
| 7 | IGNORED | The description says "tested over one to two months"; no result is quoted and none is used. |

## Declared grid (criterion 5)

`tenkan` [6, 9, 12] x `kijun` [18, 24, 36] x `cloud_atr` [0.5, 1, 2] = **27 trials**.
`span_b` stays at the original 51 and `atr_length` at 14 (fixed, not searched).

- `tenkan`/`kijun`: the originals 9 and 24, bracketed.
- `cloud_atr`: `CX` has no fixed ATR equivalent; 0.5/1/2 ATR spans thin to thick.

## Ambiguities resolved

- Buy/sell mapped to long/short with reversal intended (the original nets 1-unit trades, which is
  sizing).
- The crossing test uses strict inequalities exactly as `cross()` (lines 47-61), so a bar where
  close equals the line is not a cross.
- Hull MA and displaced cloud are plot-only in the original and are not ported.
- `FREQ = "1h"` from the description ("小时线为基准") and the one-hour loop sleep.

# #429149 Mini Pullback Supertrend Strategy -> `fmz_429149_supertrend_pullback_filters`

- FMZ source id: 429149 (lineage).
- Source: https://www.fmz.com/strategy/429149 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-13 15:49:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-placement pending). |
| 2 | PASS | ATR multiples and oscillator levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [2.0, 3.0] x `look_for` [5, 3]: **4 trials**; ATR 14, EMAs, MACD, RSI, stoch-RSI and the 1.5 / 3 ATR bracket fixed.

## Ambiguities resolved

- Pending (not emitted): a later buy signal while long moves the stop / limit to that bar's
  close -/+ 1.5 / 3 ATR(14).
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

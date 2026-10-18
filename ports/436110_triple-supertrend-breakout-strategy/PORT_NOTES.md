# #436110 Triple Supertrend Breakout Strategy -> `fmz_436110_triple_supertrend_alignment_long`

- FMZ source id: 436110 (lineage).
- Source: https://www.fmz.com/strategy/436110 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 12:05:07). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Supertrend alignment, an EMA filter and an ATR ratchet |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multi` [2, 3] x `ema_len` [233, 100]: **4 trials**; the three Supertrends and ATR 26 fixed.

## Ambiguities resolved

- Close-based ratchet and gated exit; entry only from flat. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

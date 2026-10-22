# #482802 Multi Level Take Profit and Dynamic Stop Loss Enhanced Quantitative Strategy -> `fmz_482802_tester_defaults_flat_short_prev_low_target`

- FMZ source id: 482802 (lineage).
- Source: https://www.fmz.com/strategy/482802 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:56:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous-low target as a fraction of the fill |
| 2 | PASS | Template defaults: always-short with a prior-low target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin 100 / 100 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- The template's default sources make it short-only, as written. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`

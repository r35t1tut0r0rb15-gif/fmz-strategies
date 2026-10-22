# #442973 Short term Breakthrough Strategy Based on Golden Crossover -> `fmz_442973_rsi3_pullback_sma200_long_bracket`

- FMZ source id: 442973 (lineage).
- Source: https://www.fmz.com/strategy/442973 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 17:46:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed from the fill |
| 2 | PASS | RSI pullbacks against the trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`malong` [200, 100] x `mashort` [21, 50]: **4 trials**; the RSI levels and the bracket fixed.

## Ambiguities resolved

- Long bracket only, from the fill bar. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

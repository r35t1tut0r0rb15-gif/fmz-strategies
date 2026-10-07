# #188499 KRT凯尔特纳通道 -> `fmz_188499_krt_keltner_reverse`

- Source: https://www.fmz.com/strategy/188499 (MyLanguage, author cyberking, FMZ last modified
  2020-03-05 11:41:52). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model on daily bars. |
| 2 | PASS | Band width is an EMA of H-C (price range), volatility-scaled. |
| 3 | PASS | Huobi spot in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same author's #188507 is a different channel (percent bands). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n` [5, 10, 20, 30] = **4 trials**.

## Ambiguities resolved

- **Source typo**: `DX:=H+L+C)/3;` (unbalanced parenthesis). Ported as the typical price
  `(H+L+C)/3`, which the line's comment names. If FMZ parsed it some other way, the original's
  behaviour cannot be recovered from the text; flagged in the worker report.
- The width uses H-C (the upper wick plus body of down bars), not H-L; kept as written.
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"` (as #42283 KingKeltner).

## Marks (2026-10-07)

`none`

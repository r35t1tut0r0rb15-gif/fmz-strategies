# #426889 Multi Indicator Quantitative Strategy for Cryptocurrencies -> `fmz_426889_bagheri_ig`

- Source: https://www.fmz.com/strategy/426889 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 11:58:36). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426889` (Jaccard >= 0.80) with #431957 (DUPLICATE); best Jaccard 0.918 with #431957. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [2, 5, 10]: **3 trials**, stop 3443 / 3000 of the target (the source's ratio); default 10 (3000 ticks is about 10 ATR on the 4-minute header bars); indicator settings fixed.

## Ambiguities resolved

- While ma[185] is na, nz() makes sroc 100 (short-side ROC test holds), as written.
- BoP is na on a zero-range bar; rma re-seeds from an SMA after na (Pine).
- Criterion 2 (ADAPT): tick bracket -> ATR(14) multiples at the signal bar.
- Entries do not depend on the position: no mirroring.
- FREQ = "4min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`

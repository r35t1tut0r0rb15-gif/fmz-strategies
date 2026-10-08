# Cloud worker A: FMZ porting report (2026-10-07)

Branch `survey`. Rules of 2026-10-07 (SURVEY_README.md). Static work only: nothing was run, backtested or optimised. Per-batch detail and resume points: `reports/cloud_porting_A_LOG_2026-10-07.md`.

## Counts (worker A, ids 126968 and up)

- Ported: **251** (24 with stops(): 361786, 361969, 362167, 362842, 364518, 365600, 365668, 365892, 380245, 385745, 391341, 395962, 396182, 400134, 402455, 425773, 426142, 426145, 426300, 426359, 426477, 426487, 426506, 426511)
- Rejected on reading: **34** (criterion 1: 32, criterion 2: 2)
- Exact duplicate on reading (set aside, rule 7): **1** (128126 of 127691)
- Last id reached: **426516**; next id in the queue: **426521**
- Existing batch-1 ports re-marked under rule 1 (logic unchanged): 11604, 42283, 42451, 119038 (bar_size_pending 4)

### Marks on worker A ports

| Mark | Ports |
|---|---|
| bar_size_pending | 18 |
| trailing_stop_pending | 8 |
| coarse_bar_stop | 6 |
| stop_is_entry_condition | 0 |

### Rejections (criterion, id, reason)

- 170557 (criterion 1): Inventory-ratio ladder (grid-like): buys/sells 10-20 % of equity whenever the tick price is 3 % beyond a 30-min channel midpoint or 7 % from the last trade price, keeping cash between 10 % and 90 %. The position is a continuously rebalanced inventory driven by tick prices and the last fill, not entries/exits on bars.
- 170842 (criterion 1): Not a signal strategy: an OKEx futures order-API demo (opens two buy orders once, then only logs orders and positions).
- 177631 (criterion 1): Inventory-ratio ladder: every 15 minutes buys or sells 5-20 % of equity when the tick price moves between Bollinger-relative zones of the daily bars, keeping cash between 10 % and 90 %. The position is a continuously rebalanced inventory, not entries/exits (the hourly band width is also undefined in the code).
- 187874 (criterion 2): Entries and exits fire on hard-coded BTC price levels (REF(C,1) < 6725 buys, > 10000 sells, 'Gann levels'). Without them only an MA(10/30) cross remains, which would be a different strategy.
- 191622 (criterion 1): Order-level ladder on perpetual swaps: opens on a daily-range test of > 20 price units, then keeps resting limit orders k = 11 price units above/below the fill, averaging in and martingale-style profit targets; fills inside the bar at set prices (also hard-coded price units, criterion 2).
- 201007 (criterion 1): Coin-flip strategy: entries and exits are drawn from Math.random(); no deterministic signal to port. (Its trailing take-profit and stop are attached to random entries.)
- 205469 (criterion 1): One-direction accumulation ladder on a perpetual swap: buys (or sells) a fixed USD slice on every bar the MA filter holds, doubles it after two counter bars, scales out after three with-trend bars, caps total size; no exit other than a live-only bar-count stop. Position size is the strategy.
- 255502 (criterion 1): Two concurrent sub-systems (CMI shock / trend) each holding its own hedged futures position with ATR-step scale-in or scale-out ladders, extra-lot counters and departure callbacks. The outcome is defined by the ladder of partial exits, which cannot be reduced to one net position's entry/exit signals without changing the strategy.
- 266142 (criterion 1): Pure 50/50 coin/cash rebalancing (buy or sell 1 % / 10 % slices when the coin share leaves 0.49-0.51); no entry or exit signal.
- 299799 (criterion 2): AHR999 dollar-cost averaging: the indicator is a Bitcoin-only model (price vs a log-price curve fitted to days since the 2009 genesis block); the code throws for any other pair. Also periodic accumulation, not entries/exits.
- 361719 (criterion 1): Signals come from request.security(syminfo.tickerid, '18000', src)[1]: '18000' is not a valid Pine resolution (minutes? seconds?), so the higher timeframe the counts run on is undefined. Porting would mean choosing a bar size (rule 1 forbids); needs the project to define it.
- 363557 (criterion 1): Pivots come from request.security(syminfo.tickerid, '240', get_phpl(), lookahead_on) without [1]: on historical bars the 4 h pivot is visible from the first 5 m bar of the 4 h bar that confirms it, i.e. it reads the future (SURVEY_README request.security rule).
- 363572 (criterion 1): Both MA series are read through request.security(..., stratRes, lookahead_on) without [1] (alternate resolution on by default, 3x the chart period): on historical bars the higher-timeframe values are visible before that bar closes, i.e. they read the future.
- 365389 (criterion 1): The exit is a two-step ladder: 50 % of the position at a 150-tick profit (qty_percent=50), the rest at 400 ticks or a pivot stop; a partial exit cannot be expressed as one net position's signals, and tick distances are instrument-specific (an MT4 alert template; criterion 2 too).
- 368717 (criterion 1): Long entries only (inverted hammer below EMA 10), with no exit, stop or reversal anywhere: after the first signal the position is held for the rest of the data, so there is no repeatable entry/exit rule to test (as #62163).
- 368734 (criterion 1): The orders test bar counts as booleans: `if brick_red` (non-green bars among the last 40) is true unless 40 green bars in a row, so the script is long on practically every bar; the brick cross it labels never reaches the orders. No defined signal to test.
- 369999 (criterion 1): The orders test a float and a plot handle as booleans: `if diosc` (DI+ - DI-, true whenever non-zero) -> long, `else if p2` (a plot id) -> short. Long on practically every bar; the short branch depends on how the runtime casts a plot handle. No defined signal to test.
- 370728 (criterion 1): The orders read a nested request: security(heikinashi(ticker), 'D', x) where x is itself security(ticker, 'D', open[1], lookahead_on). Which daily bar (and whether Heikin-Ashi or regular prices) reaches the orders depends on how the runtime resolves a nested request on a different ticker; the higher-timeframe values are undefined without choosing (as #361719).
- 380446 (criterion 1): The exit is a four-step take-profit ladder (25 % of the position at +3 %, +5 %, +7 %, the rest at +10 %, all with a 15 % stop, in ticks): partial exits cannot be expressed as one net position's signals (as #365389).
- 380530 (criterion 1): strategy.order (not entry) adds a unit on every bar whose hour equals an hour estimated from cumulative ROC x hour statistics since the first bar, with no exit or reversal: the position is a running sum of orders, so the size path is the strategy.
- 392636 (criterion 1): The exit is a partial take-profit ladder (10 % of the position at +2 %, 50 % at +5 %, the rest on a close below an ATR stop): partial exits cannot be expressed as one net position's signals (as #365389). pyramiding=2 also stacks entries.
- 395966 (criterion 1): A Pine documentation example: two pyramided units opened on Monday / Tuesday and closed by entry id on Thursday / Friday; the outcome is a position-size ladder by weekday, not entries/exits of one net position.
- 416875 (criterion 1): Martingale: every second it buys or sells a growing bet according to the last candle's colour, multiplying the size after wins and losses and stopping after four losses. The position size sequence is the strategy (tick loop as well).
- 422794 (criterion 1): Martingale ladder: pyramiding=6 and strategy.order adds strategy.position_size * martinFactor to a losing position (lines 55-67); the position size depends on fills, not on a bar rule (as #395966, #416875).
- 425798 (criterion 1): The entry and exit tests read BKVOL <> 1 / BKVOL = 1 / SKVOL = 1 (exactly one lot held), so the rules change with the sizing formula LOTS; and the stop multiplier LIQKA is a plain (non-VARIABLE) MyLanguage name decremented each held bar (lines 102-108), whose persistence across bars is undefined. No defined signal to test.
- 426261 (criterion 1): The opening range and the entry window come from session strings ('0930-1100', '0930-1000', '1000-1100') read through time() and security() at 1- and 30-minute resolutions on the 1h header chart: the exchange time zone of a crypto pair and what a lower-resolution time()/security() returns per chart bar are undefined, so the bars that may trade are not defined (as #361719).
- 426302 (criterion 1): 3Commas DCA bot: up to 6 safety orders add strategy.position_size * 1.55 below the entry (strategy.order), and the stop / target are fractions of the averaged position price; the position ladder is the strategy (as #422794).
- 426334 (criterion 1): The whole signal is SCORE, which calls ta.ema(close, n) for n = 1..21 inside one for-loop call site: the EMA's recursive state (its [1] value) is shared across the 21 calls, so what each length reads is defined by the runtime, not the script. Also a trailing stop order from highs and buys blocked for the rest of the calendar day after any fill.
- 426361 (criterion 1): The only exit is strategy.exit('close', 'buy') with no profit / loss / stop / limit / trail argument (an error on TradingView, no exit level on any runtime), so a long entered on the MA crossing 40 has no defined exit (as #368717).
- 426364 (criterion 1): KD inventory model: strategy.order adds or removes one default unit per bar until the position reaches a target share count (0.33 steps of 20 / -10 shares); the position size path is the strategy (as #380530).
- 426455 (criterion 1): Four strategy.exit calls share the id 'Exit' with no from_entry: two set a 300-tick stop with a 150 / 50-tick trailing stop, two (when= buy / sell) set no exit level at all. Which exit order is live on a bar depends on how the runtime merges re-issued ids; the exits are undefined.
- 426461 (criterion 1): pyramiding = 10 with entries repeated on every signal bar, the first long rule adding only below strategy.position_avg_price: a pyramided averaging ladder (as #395966, #422794).
- 426478 (criterion 1): The signal is a crossover of security(tickerid, '375', close) and security(..., open) on the daily header chart: a 375-minute resolution below the chart's, whose value per daily bar (and 375-minute block alignment on a 24 h market) is undefined (as #426261).
- 426509 (criterion 1): pyramiding = 5 with entries repeated on every signal bar, the long rule adding only below strategy.position_avg_price: a pyramided averaging ladder (as #426461).

### Commits (newest first)

- `eae5f89 survey A batch A21: 8 ports, 5 rejected (ids 426361-426478)`
- `3d6d6cf survey A batch A20: 10 ports, 3 rejected (ids 426261-426360)`
- `d296684 survey A batch A19: 11 ports, 2 rejected (ids 422794-426259)`
- `4bf67b5 survey A batch A18: 8 ports, 5 rejected (ids 380446-416875)`
- `7cd1890 survey A batch A17: 12 ports, 1 rejected (ids 370728-380396)`
- `8fc418c survey A batch A16: 10 ports, 3 rejected (ids 367643-370711)`
- `1c121fa survey A batch A15: 13 ports (ids 366641-367572)`
- `8d1813b survey A batch A14: 13 ports (ids 365858-366430)`
- `a0358a3 survey A batch A13: 13 ports (ids 365419-365727)`
- `a625008 survey A batch A12: 12 ports, 1 rejected (ids 365078-365389)`
- `70754b7 survey A batch A11: 13 ports (ids 363848-365075)`
- `344c9f9 survey A batch A10: 13 ports (ids 363582-363847)`
- `a9d6425 survey A batch A9: 11 ports, 2 rejected (ids 362667-363579); rule-7 group ids in notes`
- `8f62b3b survey A: interim final report (regenerated by survey_tools/report_a.py each batch)`
- `f252a14 survey A batch A8: 13 ports (ids 362427-362664)`
- `0b7843c survey A batch A7: 13 ports (ids 362103-362418)`
- `7617e69 survey A batch A6: 13 ports (ids 361880-362092)`
- `2ef3770 survey A batch A5: 12 ports, 1 rejected (ids 361718-361847)`
- `f98a858 survey A batch A4: 13 ports (ids 345289-361689), Pine rules in SURVEY_README`
- `e7ceef7 survey A batch A3: 9 ports, 4 rejected (ids 205469-345036)`
- `f63a58e survey A batch A2: 9 ports, 4 rejected (ids 177631-201007)`
- `d85cd82 survey A batch A1: 10 ports, 2 rejected, 1 duplicate on reading (ids 126968-171038)`
- `f17d01e survey A: no_bar_size.csv corrected to 484 files (MyLanguage/Python backtest header forms)`
- `0caedb8 survey A: no_bar_size.csv (539 of 5,806 files have no bar size)`
- `fc81097 survey A: near_duplicate_groups.csv (exhaustive candidate check) and DUPLICATE count explained`
- `cf80b57 survey A: rules 2026-10-07 in SURVEY_README; check_ports marks/pending FREQ/stop-Series timing`

## Kept as written

- direction inverted relative to the source's own names or colours: 207157, 361675, 361689, 361996, 362004, 362031, 362172, 362418, 362427, 362649, 362654, 362664, 362898, 363582, 363590, 365080, 365381, 366941, 366946
- formula slip kept: 188499, 192353, 345036
- exit bound to a mis-typed entry id (so one side has no bracket): 426300

## For the project chat

**Finished**

- Task 1: rules 2026-10-07 in SURVEY_README.md; check_ports.py extended (Marks line, bar_size_pending only with its mark, stop Series shifted inside stops(), coarse_bar_stop, left-labelled resampling); all ports pass.
- Task 2: DUPLICATE 251 explained (reports/near_duplicates_2026-10-07.md); near_duplicate_groups.csv over all 3,747 PORT_CANDIDATE rows (5-token shingles, exact Jaccard; >= 0.80 none new, 0.65-0.80 band grouped as ND).
- Task 3: no_bar_size.csv: 484 of 5,806 files have no bar size (85 with stop logic).
- Task 4: 251 ported, 34 rejected, 1 duplicate on reading, ids 126968 to 426516.

**Failed / not done**

- Task 4 is not complete: the queue continues at 426521; worker B's branch `survey-b` did not exist on origin at any batch start, so the stop condition was never reached.
- Rule 5 module (1) ("exactly as written") cannot be expressed by the contract; no stop_is_entry_condition port exists.

**Decisions owed**

1. Rule 7 re-opening: SURVEY_SUMMARY's 251 DUPLICATE rows include only 7 exact copies; the other 244 are near-duplicates that rule 7 would now port. Re-open them as PORT_CANDIDATE or keep them set aside? (reports/near_duplicates_2026-10-07.md)
2. Rule 5: the contract cannot express "stop=/limit= as entry condition" (stops() takes only sl_stop/tp_stop/max_hold_time; entries fill at the next open). The 468 screened files with strategy.entry(stop=/limit=) were REJECTED at screening; re-open them for the second ("as meant") module only, or extend the contract with entry-price orders?
3. FMZ TA.Highest/TA.Lowest are read as excluding the current element (ports 171038, 192353, 200131, 271523, 55839); confirm against the FMZ library.
4. Ports kept as written although the source looks like a slip (see "Kept as written" below): keep, or add a corrected variant per rule 5-style dual porting?
5. 333269 has no numeric defaults in the source (grid chosen from the argument table only).
6. 200131 and 361827 compute the indicator change as a log return (as the source does).
7. 361719 rejected: request.security resolution "18000" is undefined; the project would have to define it before it can be ported.
8. 370728 rejected: nested request.security on a Heikin-Ashi ticker (undefined which daily values reach the orders); same kind of decision as 361719.
9. 426261 rejected: session windows read through time()/security() at 1- and 30-minute resolutions on an hourly chart (time zone and lower-resolution semantics undefined); same kind of decision as 361719. 426334 rejected: ta.ema called with 21 lengths at one loop call site (runtime-defined state). 426478 rejected likewise (375-minute security on daily bars).
10. 426368: an opposite cross issues a reversing entry plus close_all; the port fills them in issue order (the bar ends flat). If close_all is sized at issue time the reversal would stand (always-in). Confirm the broker-emulator reading.
11. Multi-day header periods: 426502 (3d) is built from broker days in fixed 3-date blocks counted from 1970-01-01, 426516 (7d) from calendar weeks of broker-day dates. Confirm the block phase.
12. Session / weekday rules on crypto pairs are read in UTC (426511, TradingView's Binance time zone); FMZ's exchange time zone is not documented.
13. 426483 (unit strategy.order on alternating crosses) holds +1 / 0 or -1 / 0 depending on the first cross in the data: data-start dependence as 366388 / 370711.
14. strategy.exit with no price arguments is read as "no exit" (426361 rejected, 426455 rejected for re-issued exit ids).
15. 362214 is one-sided as written (the source never opens the other side).
16. 55839 keeps FREQ "1h" (author states hourly bars in the text); 103070 keeps PERIOD_M15 from the code. Bar sizes requested in code (GetRecords(PERIOD_xx)) are treated as the source's bar size, not as a choice.
17. FAMILY values are proposals ("user to confirm") in every port.
18. Sources whose orders are degenerate were rejected on reading (criterion 1): 368717 (long entries, no exit at all), 368734 and 369999 (a count / plot handle tested as a boolean, so long on almost every bar). Confirm that "no testable rule" is a valid rejection, or port them as written.
19. Some ports depend on where the data starts (Pine cum() / bar_index running means: 366388 cancels it, 370711 does not); acceptable?

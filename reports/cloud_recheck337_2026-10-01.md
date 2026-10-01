# Cloud re-check of the 337 "probable" coarse-bar stop strategies, and the 5G-A owed 3 count

- Repository: `r35t1tut0r0rb15-gif/fmz-strategies`, branch `claude/peaceful-turing-keqi5r` (fast-forwarded onto
  `cloud-batch5f-2026-10-01`, so the batch 5f report and CSV it builds on are included).
- Work done: 2026-10-01 (UTC), Claude Code cloud session.
- Scope: read-only static analysis of the original FMZ source files. Nothing was executed, backtested or changed. No
  strategy file was edited.
- Files added: this report; `cloud_recheck337_2026-10-01.csv` (the 337 rows); `cloud_owed3_counts_2026-10-01.csv`
  (1,257 rows); `cloud_recheck337_tools/` (the scripts and the hand-review list, so the result can be re-run).

---

## 1. What "the 337" were, and why they mattered

Cloud batch 5f counted FMZ strategies on bars longer than 60 minutes that use stops: **1,015 "confirmed"** (a Pine
`strategy.exit` call with a stop, target or trailing argument) and **337 "probable"** (stop-like words appear in the
code, but no such call). It warned that the probable tier included display-only inputs and needed a check before use.

That count feeds the open question **Y14 (c)** (PROJECT_CHAT_START_HERE §5 B): stop costs are chosen by the bar's
timestamp, a daily bar is stamped at the rollover, so a stop that fills *inside* a daily bar is charged the expensive
rollover cost. The proper fix (finding the minute the stop was hit) is pending this count.

The point that decides which strategies Y14 (c) touches: **only a stop that fills inside the bar is affected.** A stop
written as "if the close is below the stop, close the trade" is read at the bar's close and fills at the next bar's
open, which is exactly where the rollover cost belongs. So each of the 337 was put in one of these classes:

| class | what it means | how the stop fills | Y14 (c) affected |
|---|---|---|---|
| `intrabar_order` | a stop/limit **exit order** (`strategy.order(..., stop=/limit=)` closing the position) | inside the bar | **yes** |
| `live_price_stop` | JavaScript: the live price is checked on every poll | inside the bar | **yes** (once converted to bars) |
| `close_based_stop` | a stop/target **level** read at the bar's close, then `strategy.close` / `close_all` | next bar's open | no |
| `stop_and_reverse` | the stop level flips the position with an opposite `strategy.entry` (SuperTrend, UT Bot, …) | next bar's open | no |
| `stop_entry` | `strategy.entry(..., stop=SL, limit=TP)`: the author meant a stop-loss and take-profit, but in Pine this makes the **entry** a stop-limit order. There is no stop exit | no stop exit | no |
| `no_stop_exit` | stop/target names exist but never reach an order (plotted, unused, or a different meaning) | no stop exit | no |

## 2. Result for the 337

| class | files | hand-checked or overridden | automatic only |
|---|---:|---:|---:|
| `intrabar_order` | 9 | 9 | 0 |
| `live_price_stop` | 7 | 7 | 0 |
| `close_based_stop` | 204 | 65 | 139 |
| `stop_and_reverse` | 22 | 22 | 0 |
| `stop_entry` | 32 | 14 | 18 |
| `no_stop_exit` | 63 | 62 | 1 |
| **total** | **337** | **179** | **158** |

- **Affected by Y14 (c): 16 of the 337** (9 Pine stop/limit exit orders + 7 JavaScript live-price stops; 14 daily,
  1 each 3h and 4h). Every one was read by hand.
- **A working stop exit that fills at the next bar's open: 226** (204 close-based + 22 stop-and-reverse).
- **No stop exit at all: 95** (63 + 32). Of these, 70 are daily.
- The 10 JavaScript files were all read by hand (§5).

### The Y14 (c) population, revised

| bar | confirmed (5f) | from the 337 | **total affected** | (batch 5f total, for comparison) |
|---|---:|---:|---:|---:|
| 2h | 116 | 0 | 116 | 155 |
| 3h | 68 | 1 | 69 | 83 |
| 4h | 82 | 1 | 83 | 105 |
| 5h–15h | 15 | 0 | 15 | 18 |
| 1d | 678 | 14 | **692** | 923 |
| 2d–6d | 56 | 0 | 56 | 68 |
| **total** | **1,015** | **16** | **1,031** | 1,352 |

**1,031 files (1,030 strategy ids; id 405725 is two identical files) have a stop that fills inside a coarse bar**,
692 of them daily. The batch 5f upper bound was 1,352. As a cross-check, the same classifier run on the 1,015 confirmed
rows puts all 1,015 in `intrabar_order`, matching batch 5f.

### Also found
- **32 `stop_entry` strategies have a stop-loss/take-profit that does nothing as a stop.** `strategy.entry(...,
  stop=stopLoss, limit=takeProfit)` is a common mistake in the newer FMZ descriptions. A faithful conversion would
  copy the bug, and a "fixed" conversion would be a different strategy. Both are worth knowing before converting them.
- **Stops that are off by default.** A stop gated by an input that defaults to off is still classified by what the
  code can do. Four rows carry a `stop_default_off` marker (`check: <input names>` is a heuristic hint, not a verdict).
  One of them, id 311968 (JavaScript grid), is confirmed: both its stop and its take-profit default to off.

## 3. How the classification was done

`cloud_recheck337_tools/classify337.py`, static analysis of each Pine source:
1. The `/*backtest*/` block, comments and strings are removed. Input titles are kept for step 3, but tooltips are not.
2. Lines are joined into statements (open brackets, trailing operators, Pine's continuation indent, strings that run
   over lines).
3. **Seeds:** variables whose name is stop-like, judged on whole words so that "slow", "slope" and "output" don't
   count (stop, sl, tp, trail, target, profit, loss, 止损, 止盈 …). Also seeded: inputs titled that way, and anything
   computed from the entry price (`strategy.position_avg_price`, `openprofit`, `*entryPrice*`). **Not** seeds:
   backtest date windows (`testStopYear`, "Backtest Stop Month"), colours, labels, loss-streak counters, and on/off
   switches (a "use stop loss" switch gates a stop but is not one; the level itself must reach the order).
4. **Taint:** a value computed from a seed is tainted, through assignments, through `if` blocks (a value set inside
   `if close < stop` depends on the stop), and through user-defined functions, including helpers that place the
   orders themselves.
5. Every `strategy.*` order call is tested with its arguments and every enclosing `if` condition. A priced
   `strategy.exit`, or a priced `strategy.order` that closes the open position (its quantity or condition uses the open
   `position_size`, or its label names a stop/exit/target), is an inside-the-bar exit whatever its variables are called.
   A `strategy.exit` with no price argument is treated as placing no exit (Pine needs one; not verified by running Pine
   here).
6. `finalize.py` applies the hand review: 13 overrides with a reason each, the JavaScript review, and the list of
   hand-checked ids.

### How far to trust it
- **Hand-checked:** all 16 Y14 (c)-affected rows, all 22 stop-and-reverse, 62 of 63 no-stop, 14 of 32 stop-entry,
  65 of 204 close-based. That is 179 of 337 in total.
- **Random audits of the unreviewed rows.** A first sample of 20 found 2 errors. Both were fixed by general rule changes
  (the switch rule and the priceless-exit rule), which moved 5 rows, all checked. A **fresh** sample of 20 after those
  fixes found **2 errors** (an oscillator's lowest value named `sl`; an RSI level named `takeProfitLevel`). Both were
  false "stop" calls, now overridden.
- **So among the 158 rows still classified automatically, roughly 1 in 10 may be a false "stop"** (2 of 20; plausible
  range about 3–30 %). These sit in `close_based_stop` / `stop_entry`, which do not count toward Y14 (c) either way.
  The **16 affected is unaffected**; the 226 "next-bar-open" figure may be 10–25 too high.
- **Known misses the method cannot see:** a stop level with no stop-like name and no entry-price link (one found and
  overridden: id 438036, an unnamed level plotted as "StopLoss"). The semantic edge cases were decided by hand:
  SuperTrend/OTT/UT Bot lines named `longStop`/`xATRTrailingStop` count as trailing stops.

## 4. 5G-A owed 3: reversals, time exits, same-bar entry and exit

The start-here file (§5 D) recommends asking the cloud session to count, together with Y14 (c), how many strategies
use the three things the exact re-check cannot handle. Population: the **1,257 coarse-bar files with a working stop
exit** (1,015 confirmed + 242 from the 337); 1,248 of them are Pine. Static and approximate.

| what | count | how it was found |
|---|---:|---|
| can **reverse** (opposite `strategy.entry` while a position is open) | **893** of 1,248 Pine | both long and short `strategy.entry` calls, and no `allow_entry_in` restricting to one side. In Pine an opposite entry reverses automatically. |
| **time-based exit**, likely | **24** | bars-since-entry arithmetic, `entry_bar_index`, `opentrades.entry_time`, names like `maxHoldingPeriod`, `bars_since_entry` |
| time-based exit, possible | 33 | `barssince(<entry-like signal>)`, often signal timing rather than an exit |
| **same-bar entry and exit** possible | **1,023** | every strategy with an inside-the-bar exit order can fill entry and stop on one bar. Whether it *does* depends on the data, so it cannot be counted without running. |

Per-file flags are in `cloud_owed3_counts_2026-10-01.csv`. `max_bars_back` (a Pine memory setting) was excluded after
it produced 29 false time-exit matches.

## 5. The 10 JavaScript files (all hand-read)

FMZ JavaScript strategies run a polling loop. The `period` in their backtest block is the bar used for indicators, but
stops are checked against the live price on every poll.

| id | class | what the code does |
|---|---|---|
| 12348 | live_price_stop (SL) | ticker bid/ask vs entry × (1 ± StopLossRatio) |
| 275287 | live_price_stop (TP) | closes at a profit step; losses **add** to the position (martingale), no stop-loss |
| 299799 | no_stop_exit | DCA; sells when the ahr999 index falls below a line |
| 311968 | live_price_stop (SL+TP) | account floating-PnL stop and take-profit, **both off by default** |
| 339344 | close_based_stop | uses the last *closed* bar's close vs hold price × (1 ± stopLoss) |
| 353659 | intrabar_order (TP) | resting limit sell at position price + profitTarget |
| 356471 | live_price_stop (SL+TP) | position profit vs target; stops out when the loss exceeds the margin |
| 394112 | live_price_stop (SL+TP) | order-book best bid/ask vs stop/target prices |
| 405725 (×2, identical) | live_price_stop (SL+TP) | the forming bar's close (live price) vs an hl2 ± ATR grid, every few seconds |

## 6. Re-running

```
cd reports/cloud_recheck337_tools
python3 classify337.py ../cloud_coarse_bar_stops_2026-10-01.csv recheck.csv   # automatic classes
python3 finalize.py ../cloud_recheck337_2026-10-01.csv                         # + hand review -> deliverable
python3 owed3.py                                                                # -> ../cloud_owed3_counts_2026-10-01.csv
```
Python 3.9+, standard library only. Re-running reproduces the committed CSVs byte for byte.

CSV columns (`cloud_recheck337_2026-10-01.csv`): `strategy_id, bar_size, language, base_period, batch5f_stop_type,
recheck_class, recheck_stop_kind, stop_fills, y14c_affected, stop_default_off, review (auto | hand-checked |
hand-override), note, evidence (the order call, with its line number in the source block), file`.

---

## For the project chat

### Finished
- **The 337 re-checked.** 16 have a stop that fills inside the bar (Y14 (c) affected), 226 have a stop that fills at
  the next bar's open (not affected), and 95 have no working stop exit. Every affected row was read by hand.
- **Y14 (c) population: 1,031 files / 1,030 ids, 692 of them daily** (batch 5f's upper bound was 1,352 / 923 daily).
- **5G-A owed 3 counted** (static): 893 of 1,248 can reverse; 24 likely + 33 possible time exits; same-bar entry and
  exit possible for 1,023 and not countable without running.
- **New:** 32 strategies whose "stop-loss / take-profit" is a Pine entry-order mistake with no stop effect; 4 with
  stops off by default (1 confirmed, 3 to check).

### Failed / not done
- The population is still the **original FMZ sources**, not converted strategies: Q1 (where the conversion output
  went) is unanswered, and nothing converted exists on the fork.
- 158 rows rest on the automatic classification alone (about 1 in 10 may be a false "stop"; none of them changes the
  Y14 (c) count).

### Decisions owed
1. **Y14 (c) size.** About 1,030 coarse-bar strategies (about 690 daily) would get the wrong stop cost until the
   minute-data fix exists. **Recommend:** the minute-data fix is worth building before mining FMZ daily-bar stop
   strategies at scale. It touches about 18 % of the 5,806 sources (about 12 % daily). Until then, keep marking.
2. **Stop-entry strategies (32).** Convert as written (the stop does nothing), or convert as the author meant (a real
   stop-loss and take-profit)? **Recommend:** as written, marked. The registered trial must be the code that exists,
   and "as meant" is a new strategy that can be registered on its own.
3. **5G-A owed 3.** Reversals are common (about 7 in 10 stop strategies can reverse); time exits are rare (about 2–5 %).
   **Recommend:** if the exact re-check is extended, do **reversals first**, not time exits as the 5G-A report
   suggested. This count reverses that order.
4. **Next-bar-open stops (226 here, plus any among the 5,806 not in this population).** These are unaffected by Y14 (c),
   but only if the conversion keeps them as close-based exits. **Recommend:** the strategy-authoring contract should
   say that a Pine close-based stop is converted as a close-based exit, never as `sl_stop`. Otherwise it silently joins
   the Y14 (c) population.

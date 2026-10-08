"""Per-port data used by make_port_files.py.

SIZING: fmz_id -> list of (label, first_line, last_line), 1-based inclusive line numbers in the
original corpus file (identical to ports/<slug>/original_source.md, which is a byte copy).
These blocks are copied verbatim into original_sizing.txt (criterion 4).

REJECTED_ON_READING: fmz_id -> (criterion, reason). Files the screen marked PORT_CANDIDATE
but reading showed they fail; written to review_decisions.csv.

DUPLICATE_ON_READING: fmz_id -> (ported fmz_id, reason). Candidates whose logic AND defaults are
identical to a port (exact duplicates in behaviour, set aside under rule 7, 2026-10-07).

An empty SIZING list means the source has no sizing or money-management code.
"""

SIZING = {
    11604: [
        ("Parameter row: order price offset SlidePrice", 21, 21),
        ("Quantity rounding helper", 32, 34),
        ("Entry execution: all-in buy / sell-all, SlidePrice offsets, min-stock guard", 112, 137),
        ("Cover execution: buy back / sell only the stocks traded since entry", 151, 182),
    ],
    42283: [
        ("Parameters: trailing stop %, slippage (trailingPrcnt is ported as a signal exit)", 26, 30),
        ("Quantity rounding helper", 31, 33),
        ("Minimum balance guard", 75, 75),
        ("Entry execution: all-in buy at ticker.Last + SlidePrice, minMoney guard", 104, 117),
        ("Exit execution: sell all at ticker.Last - SlidePrice (trailing condition ported as signal)", 118, 131),
    ],
    42451: [
        ("Parameters: unused trailingPrcnt, slippage", 27, 29),
        ("Quantity rounding helper", 30, 32),
        ("Minimum balance guard", 72, 72),
        ("Entry/exit execution: all-in buy, sell all, SlidePrice offsets", 108, 131),
    ],
    55839: [
        ("Fixed 1-unit market orders at ticker.Last on every signal (units accumulate; no position cap)", 213, 230),
    ],
    103070: [
        ("Parameter row: Slippage", 30, 30),
        ("Entry execution: 99% of balance at ask + Slippage, min amount 0.1, cancel if pending", 65, 73),
        ("Exit execution: sell all stocks at bid - Slippage, min amount 0.1, cancel if pending", 74, 82),
    ],
    119038: [
        ("Parameters: stop/target distances (ported via stops), start size, risk limit, leverage, contract, multiplier", 23, 32),
        ("updatePositions: stop-loss / take-profit checks against ticker bid/ask, martingale reverse at "
         "AMP x size up to RISK_LIMIT (lines 185-193 are the RSI-slope entry the port uses)", 116, 195),
        ("Order helpers: floor amounts, +/-1% marketable limit prices, futures direction", 197, 247),
        ("Contract type and leverage set-up", 257, 259),
    ],
    # ---- worker A, batch A1 (2026-10-07)
    126968: [
        ("Argument: RATIO (equity fraction per unit)", 42, 42),
        ("Lot formula (1 % of equity per ATR), unit size TC, 4-unit cap MTC", 65, 68),
        ("Pyramid adds every 0.5 ATR up to MTC (kept in the port only as the stop reference)", 78, 79),
        ("TRADE_AGAIN / MULTSIG execution settings", 86, 87),
    ],
    127101: [
        ("Order-price type for BK", 59, 59),
        ("Order-price type for SK", 61, 61),
    ],
    127691: [],
    128249: [
        ("Backtest header: TradeAmount", 66, 66),
        ("Open statements without AUTOFILTER: a repeated BK/SK adds a lot", 84, 85),
        ("Close statements close the whole volume (SP(BKVOL), BP(SKVOL))", 86, 89),
    ],
    128250: [
        ("Close statements close the whole volume (SP(BKVOL), BP(SKVOL))", 86, 89),
    ],
    128418: [
        ("Backtest header: TradeAmount", 64, 64),
    ],
    132298: [
        ("Lot formula (1 % of equity per ATR), unit size TC, 4-unit cap MTC", 198, 201),
        ("Pyramid adds every 0.5 ATR up to MTC (kept in the port only as the stop reference)", 206, 207),
        ("TRADE_AGAIN execution setting", 212, 212),
    ],
    146391: [
        ("Order execution: 10 % of balance / stocks per signal, unbounded position counter", 72, 91),
    ],
    156699: [],
    171038: [
        ("monkeyOper: inventory trading at +/-3 % from the last price (commented out in the source)", 50, 97),
        ("bullOper: cancel shorts, close shorts, buy 20 %/30 % up to half the account", 99, 141),
        ("bearOper: cancel longs, close longs, sell 20 %/30 % up to half the account", 143, 185),
        ("Venue set-up: quarterly contract, 5x leverage", 248, 257),
    ],
    # ---- worker A, batch A2 (2026-10-07)
    183416: [
        ("Lot size liang (half of equity x previous close / 100)", 33, 33),
        ("Order statements: shorts at 2x liang, longs at liang", 42, 43),
    ],
    186598: [
        ("Unit = 1 % of portfolio per ATR, capped by balance; +100 price guard", 59, 71),
        ("Order execution: buy at ticker.Last+10, order history, sell all", 100, 115),
    ],
    188499: [],
    188507: [],
    192353: [
        ("Unit formula (1 % of equity per N) and equity from margin", 63, 77),
        ("set_position: reconcile long/short legs with +/-0.5 % limit prices", 104, 143),
        ("Venue: quarterly contract", 205, 205),
    ],
    193609: [
        ("Argument: Amount", 18, 18),
        ("Venue: XBTUSD contract", 26, 26),
        ("Order execution: fixed Amount at ticker prices", 47, 81),
    ],
    194224: [
        ("Arguments: SlidePrice, orderTimeout, MinStock (ac1/bc1/TrailingStop are ported)", 18, 23),
        ("Order helpers: sliced buy with timeouts, sell loop, rounding", 31, 141),
        ("Execution: buy with the whole balance, sell all, profit log", 184, 197),
    ],
    200131: [
        ("Argument: Amount", 174, 174),
        ("Venue: XBTUSD contract", 191, 191),
        ("Order execution: fixed Amount at ticker prices", 300, 338),
    ],
    200625: [
        ("Venue: quarterly contract", 37, 37),
        ("Order execution: close opposite, vol lots (2x vol on shorts), +/-1 % prices", 101, 123),
    ],
    # ---- worker A, batch A3 (2026-10-07)
    207157: [
        ("Lot liang (equity x previous close / 100)", 38, 38),
        ("Order statements with lot sizes", 45, 49),
    ],
    224799: [
        ("Arguments: Amount (time_interval is the bar size)", 34, 35),
        ("Venue set-up: contract type, 1x margin", 61, 69),
        ("Order execution: fixed Amount at ticker prices", 93, 126),
    ],
    262467: [
        ("Venue: quarterly contract", 29, 29),
        ("Order execution: one contract per order, repeated on later polls", 62, 85),
    ],
    271523: [
        ("Exposure levels: all-in buy, all-out sell, 50/50 rebalancing ladder (1 % and 10x steps)", 96, 181),
    ],
    288889: [
        ("Order execution: 1 % slices of coins / cash on every loop, 4-minute pause", 18, 42),
    ],
    301620: [
        ("Argument: buyVolume", 36, 36),
        ("Open(): fixed buyVolume market orders", 89, 107),
    ],
    318486: [
        ("Argument: Amount", 18, 18),
        ("Venue: swap contract", 34, 34),
        ("Order execution: fixed Amount at ticker prices", 62, 96),
    ],
    333269: [
        ("Argument: amount", 22, 22),
        ("Cancel-all and cover helpers", 53, 82),
    ],
    345036: [
        ("Argument: slide_price", 40, 40),
        ("Order cancelling helper", 101, 112),
        ("Order execution: buy with all cash at Last+slide, sell all at Last-slide", 127, 145),
    ],
    # ---- worker A, batch A4 (2026-10-07)
    345289: [
        ("Argument: splide_price", 18, 18),
        ("Order cancelling helper", 50, 61),
        ("Order execution: all cash at Last+slide, all coins at Last-slide, 0.1 minimum", 84, 99),
    ],
    356844: [],
    359806: [
        ("strategy(): 50 % of equity per order", 66, 66),
    ],
    360536: [
        ("strategy(pyramiding=4) and risk/unit inputs (RiskRatio, ContractUnit, MinStock)", 41, 49),
        ("Turtle unit size from equity / N", 68, 68),
        ("Pyramid adds with qty=turtelUnits (kept in the port only as the stop reference)", 115, 119),
        ("Short-side pyramid adds", 130, 134),
    ],
    361360: [],
    361508: [],
    361521: [],
    361532: [],
    361554: [],
    361565: [
        ("Commented-out strategy() line (25 % of equity, calc_on_every_tick; not active)", 49, 49),
    ],
    361567: [],
    361675: [],
    361689: [],
    # ---- worker A, batch A5 (2026-10-07)
    361718: [], 361725: [], 361783: [], 361785: [],
    361786: [
        ("Commented-out strategy() line: 100 % of equity, commission (not active)", 63, 63),
        ("Risk settings: % risk, fixed/dynamic SL switch, RRR", 72, 81),
        ("Risk-based entry quantity (equity x risk / stop distance)", 176, 177),
        ("Short-side risk-based quantity", 193, 194),
    ],
    361794: [], 361802: [],
    361827: [
        ("qty = equity / close", 53, 53),
    ],
    361834: [], 361839: [], 361844: [], 361847: [],
    # ---- worker A, batch A6 (2026-10-07)
    361880: [],
    361969: [
        ("Risk management input: account percent loss per trade", 138, 138),
        ("Risk-based quantity: equity x risk / stop distance", 555, 557),
        ("Long entry with qty", 560, 560),
        ("Short entry with qty", 567, 567),
    ],
    361974: [], 361977: [], 361996: [], 362000: [], 362004: [], 362031: [], 362055: [],
    362059: [
        ("strategy(): margin_long = margin_short = 0", 55, 55),
    ],
    362060: [], 362089: [], 362092: [],
    # ---- worker A, batch A7 (2026-10-07): no sizing code in these sources
    362103: [], 362163: [], 362167: [], 362168: [], 362172: [], 362178: [], 362210: [], 362214: [], 362223: [], 362256: [], 362327: [], 362403: [], 362418: [],
    # ---- worker A, batch A8 (2026-10-07)
    362427: [],
    362430: [
        ("strategy(): default_qty_value = 750", 58, 58),
    ],
    362443: [], 362457: [], 362497: [], 362499: [], 362542: [], 362572: [], 362637: [], 362638: [], 362649: [],
    362654: [], 362664: [],
    # ---- worker A, batch A9 (2026-10-07)
    362667: [], 362671: [],
    362842: [
        ("Commented-out strategy(): 100 % of equity, initial capital 1000 (not active)", 60, 60),
    ],
    362868: [], 362870: [], 362887: [], 362898: [],
    363001: [
        ("Trading-the-equity-curve sizing: initial % equity, equity SMAs, size adjustment", 76, 108),
    ],
    363002: [], 363562: [], 363579: [],
    # ---- worker A, batch A10 (2026-10-07)
    363582: [],
    363588: [
        ("Commented-out strategy(): cash 1000 per order, initial capital 10000 (not active)", 78, 79),
    ],
    363590: [], 363749: [],
    363766: [
        ("Commented-out strategy(): 100 % of equity, pyramiding 1, commission (not active)", 93, 93),
    ],
    363793: [],
    363797: [
        ("Commented-out strategy() and the table's balance / allocation / commission inputs", 64, 70),
    ],
    363803: [], 363807: [], 363824: [], 363825: [], 363829: [], 363847: [],
    # ---- worker A, batch A11 (2026-10-07): no sizing code in these sources
    363848: [], 363980: [], 363997: [], 364001: [], 364037: [], 364518: [], 364527: [], 364535: [], 364536: [],
    364540: [], 365028: [], 365059: [], 365075: [],
    # ---- worker A, batch A12 (2026-10-07): no sizing code in these sources
    365078: [], 365080: [], 365127: [], 365128: [], 365283: [], 365314: [], 365315: [], 365320: [], 365345: [],
    365359: [], 365373: [], 365381: [],
    # ---- worker A, batch A13 (2026-10-07)
    365419: [],
    365600: [
        ("strategy(): pyramiding 2, qty 500, commission 0.2 %, initial capital 10000", 92, 94),
    ],
    365642: [],
    365668: [
        ("strategy(): cash qty 10000, initial capital 10000", 47, 47),
    ],
    365671: [], 365691: [], 365695: [], 365706: [],
    365711: [
        ("strategy(): pyramiding 0, initial capital 100000", 61, 61),
        ("Target 1 / target 2 trade sizes (qty 10000)", 272, 280),
    ],
    365713: [], 365719: [], 365722: [],
    365727: [
        ("strategy(): 100 % of equity, pyramiding 1, commission 0", 56, 56),
    ],
    # ---- worker A, batch A14 (2026-10-07/08)
    365858: [],
    365859: [
        ("strategy(): commission 0.025 %, cash quantity", 52, 52),
        ("Optional stop loss / take profit (off by default)", 157, 168),
    ],
    365892: [
        ("strategy(): 100 % of equity, initial capital 10000, commission", 85, 85),
    ],
    365898: [], 365905: [], 365907: [], 366385: [], 366388: [], 366389: [], 366391: [], 366404: [], 366407: [],
    366430: [],
    # ---- worker A, batch A15 (2026-10-08): no sizing code in these sources
    366641: [], 366930: [], 366936: [], 366941: [], 366942: [], 366943: [], 366946: [], 366947: [], 366948: [],
    366966: [], 367476: [], 367565: [], 367572: [],
    # ---- worker A, batch A16 (2026-10-08): no sizing code in these sources
    367643: [], 368715: [], 368736: [], 368738: [], 368749: [], 368777: [], 369392: [], 370653: [], 370655: [],
    370711: [],
    # ---- worker A, batch A17 (2026-10-08)
    376314: [],
    379757: [
        ("strategy(): cash qty 1000, pyramiding 0", 41, 41),
        ("Optional stop loss / take profit (off by default)", 92, 103),
    ],
    379760: [], 380007: [], 380219: [], 380245: [],
    380251: [
        ("strategy(): initial capital 1000", 39, 39),
    ],
    380277: [
        ("strategy(): 100 % of equity, initial capital 1000000", 34, 34),
    ],
    380291: [
        ("Long entry with qty 100", 55, 55),
        ("Short entry with qty 100", 62, 62),
    ],
    380331: [
        ("strategy(): 100 % of equity, margin 1, commission", 42, 42),
    ],
    380369: [], 380396: [],
    # ---- worker A, batch A18 (2026-10-08)
    380525: [],
    385745: [
        ("Order amount input", 156, 156),
        ("Long entry / exit with amount", 165, 166),
        ("Short entry / exit with amount", 168, 169),
    ],
    391341: [
        ("Order quantity input and entries with it", 170, 177),
    ],
    395962: [], 396182: [],
    400134: [
        ("Commented-out strategy(): 100 % of equity (not active)", 20, 20),
    ],
    402455: [],
    410112: [
        ("Order amount (quote currency)", 27, 27),
        ("Buy amount and order", 52, 54),
        ("Sell amount and order", 59, 61),
    ],
    # ---- worker A, batch A19 (2026-10-08)
    425773: [],
    425796: [
        ("LOTS: percent of money over margin and unit", 47, 47),
        ("Entries with LOTS", 73, 74),
        ("Exits with the held volume", 76, 77),
    ],
    425797: [
        ("LOTS: percent of money over margin and unit", 49, 49),
        ("Entries with LOTS", 69, 71),
        ("Exits with the held volume", 73, 75),
    ],
    425882: [
        ("Commented-out strategy(): 100 cash per order (not active)", 78, 78),
    ],
    426136: [
        ("strategy(): margin_long / margin_short 100", 60, 60),
    ],
    426137: [
        ("Long entry with qty 1", 81, 81),
    ],
    426141: [
        ("strategy(): 100 % of equity", 53, 53),
    ],
    426142: [],
    426145: [
        ("Commented-out strategy(): pyramiding 5, qty 100 (not active)", 45, 45),
    ],
    426249: [
        ("Commented-out strategy(): qty 100, initial capital (not active)", 67, 69),
    ],
    426259: [],
    # ---- worker A, batch A20 (2026-10-08)
    426262: [], 426300: [], 426322: [], 426335: [],
    426298: [
        ("Commented-out strategy(): pyramiding 100, qty 1e8 (not active)", 78, 78),
        ("Martingale qty stacking (doubling per signal)", 161, 172),
        ("isAdding input and the qty-sized entries it selects (off by default)", 159, 159),
        ("Entries with qty=stacking when isAdding", 247, 249),
    ],
    426338: [
        ("strategy(): margin_long / margin_short 100", 87, 87),
    ],
    426339: [
        ("strategy(): 100 % of equity", 52, 52),
    ],
    426340: [
        ("strategy(): 100 % of equity, pyramiding 0", 62, 62),
        ("Entries with qty 0 when a side is disabled", 87, 90),
    ],
    426359: [
        ("strategy(): margin 100, pyramiding 10, percent of equity", 105, 105),
    ],
    426360: [
        ("Commented-out strategy(): 3500 % of equity (not active)", 66, 66),
    ],
    # ---- worker A, batch A21 (2026-10-08)
    426367: [], 426376: [], 426377: [], 426460: [], 426477: [],
    426363: [
        ("Leverage input (unused by the orders)", 89, 89),
    ],
    426368: [
        ("Commented-out strategy(): 20 % of equity, commission (not active)", 67, 67),
    ],
    426391: [
        ("Commented-out strategy(): 100 % of equity (not active)", 60, 60),
    ],
    # ---- worker A, batch A22 (2026-10-08)
    426489: [], 426498: [], 426506: [], 426511: [],
    426482: [
        ("Commented-out strategy(): 20 % of equity (not active)", 116, 116),
    ],
    426483: [
        ("Commented-out strategy(): initial capital, commission (not active)", 105, 105),
        ("Unit orders (qty 1)", 131, 132),
    ],
    426486: [
        ("Commented-out strategy(): qty 10000 (not active)", 105, 105),
    ],
    426487: [
        ("strategy(): initial capital 1000, slippage", 112, 112),
        ("Risk per trade input", 117, 119),
        ("Lot sizes from equity risk and the EMA 100 distance", 180, 181),
        ("Entries with qty lotB / lotS", 187, 193),
    ],
    426500: [
        ("strategy(): 100 % of equity, commission", 112, 112),
    ],
    426502: [
        ("Commented-out strategy(): 100 % of equity (not active)", 106, 106),
        ("Risk input and commented-out max intraday loss", 126, 127),
    ],
    426510: [
        ("strategy(): 100 % of equity, commission", 112, 112),
    ],
    426516: [
        ("strategy(): 100 % of equity", 103, 103),
    ],
}

REJECTED_ON_READING = {
    179: ("1", "Entries and exits are a tick-price state machine (ticker.Last vs tick-tracked highs/lows, "
               "percent pull-backs); only the EMA regime is bar-based. Cannot be evaluated once per completed bar "
               "without changing the rule."),
    21104: ("1", "Python spot trading class library (template exporting ext.* functions), not a signal strategy."),
    21369: ("1", "Entry needs the consecutive-cross count to shrink while still negative, which only happens through the "
                 "forming bar's changing values; exit also requires price > entry + 4 currency units (hard-coded price "
                 "distance)."),
    21370: ("2", "Linear SVM trained on raw Open/Close price levels with an absolute 2-unit label threshold: the model is "
                 "tied to the instrument's price scale. Also predicts the forming bar from its first tick (criterion 1)."),
    23531: ("1", "R-Breaker: entries/exits trigger when the tick price crosses pivot levels inside the bar "
                 "(intraday level-break fills)."),
    23874: ("1", "R-Breaker variant: same tick-price pivot level breaks inside the bar as #23531."),
    62163: ("1", "talib demo: sells once when three black crows appear on the forming bar, then throws; no exit, "
                 "not a trading strategy."),
    # ---- worker A, batch A1 (2026-10-07)
    170557: ("1", "Inventory-ratio ladder (grid-like): buys/sells 10-20 % of equity whenever the tick price is 3 % "
                  "beyond a 30-min channel midpoint or 7 % from the last trade price, keeping cash between 10 % and "
                  "90 %. The position is a continuously rebalanced inventory driven by tick prices and the last "
                  "fill, not entries/exits on bars."),
    170842: ("1", "Not a signal strategy: an OKEx futures order-API demo (opens two buy orders once, then only logs "
                  "orders and positions)."),
    # ---- worker A, batch A2 (2026-10-07)
    177631: ("1", "Inventory-ratio ladder: every 15 minutes buys or sells 5-20 % of equity when the tick price "
                  "moves between Bollinger-relative zones of the daily bars, keeping cash between 10 % and 90 %. The "
                  "position is a continuously rebalanced inventory, not entries/exits (the hourly band width is "
                  "also undefined in the code)."),
    187874: ("2", "Entries and exits fire on hard-coded BTC price levels (REF(C,1) < 6725 buys, > 10000 sells, "
                  "'Gann levels'). Without them only an MA(10/30) cross remains, which would be a different strategy."),
    191622: ("1", "Order-level ladder on perpetual swaps: opens on a daily-range test of > 20 price units, then keeps "
                  "resting limit orders k = 11 price units above/below the fill, averaging in and martingale-style "
                  "profit targets; fills inside the bar at set prices (also hard-coded price units, criterion 2)."),
    201007: ("1", "Coin-flip strategy: entries and exits are drawn from Math.random(); no deterministic signal "
                  "to port. (Its trailing take-profit and stop are attached to random entries.)"),
    # ---- worker A, batch A3 (2026-10-07)
    205469: ("1", "One-direction accumulation ladder on a perpetual swap: buys (or sells) a fixed USD slice on every "
                  "bar the MA filter holds, doubles it after two counter bars, scales out after three with-trend bars, "
                  "caps total size; no exit other than a live-only bar-count stop. Position size is the strategy."),
    255502: ("1", "Two concurrent sub-systems (CMI shock / trend) each holding its own hedged futures position with "
                  "ATR-step scale-in or scale-out ladders, extra-lot counters and departure callbacks. The outcome is "
                  "defined by the ladder of partial exits, which cannot be reduced to one net position's entry/exit "
                  "signals without changing the strategy."),
    266142: ("1", "Pure 50/50 coin/cash rebalancing (buy or sell 1 % / 10 % slices when the coin share leaves "
                  "0.49-0.51); no entry or exit signal."),
    299799: ("2", "AHR999 dollar-cost averaging: the indicator is a Bitcoin-only model (price vs a log-price curve "
                  "fitted to days since the 2009 genesis block); the code throws for any other pair. Also periodic "
                  "accumulation, not entries/exits."),
    # ---- worker A, batch A5 (2026-10-07)
    361719: ("1", "Signals come from request.security(syminfo.tickerid, '18000', src)[1]: '18000' is not a valid "
                  "Pine resolution (minutes? seconds?), so the higher timeframe the counts run on is undefined. "
                  "Porting would mean choosing a bar size (rule 1 forbids); needs the project to define it."),
    # ---- worker A, batch A9 (2026-10-07)
    363557: ("1", "Pivots come from request.security(syminfo.tickerid, '240', get_phpl(), lookahead_on) without "
                  "[1]: on historical bars the 4 h pivot is visible from the first 5 m bar of the 4 h bar that "
                  "confirms it, i.e. it reads the future (SURVEY_README request.security rule)."),
    363572: ("1", "Both MA series are read through request.security(..., stratRes, lookahead_on) without [1] "
                  "(alternate resolution on by default, 3x the chart period): on historical bars the "
                  "higher-timeframe values are visible before that bar closes, i.e. they read the future."),
    # ---- worker A, batch A12 (2026-10-07)
    365389: ("1", "The exit is a two-step ladder: 50 % of the position at a 150-tick profit (qty_percent=50), the "
                  "rest at 400 ticks or a pivot stop; a partial exit cannot be expressed as one net position's "
                  "signals, and tick distances are instrument-specific (an MT4 alert template; criterion 2 too)."),
    # ---- worker A, batch A16 (2026-10-08)
    368717: ("1", "Long entries only (inverted hammer below EMA 10), with no exit, stop or reversal anywhere: after "
                  "the first signal the position is held for the rest of the data, so there is no repeatable "
                  "entry/exit rule to test (as #62163)."),
    368734: ("1", "The orders test bar counts as booleans: `if brick_red` (non-green bars among the last 40) is "
                  "true unless 40 green bars in a row, so the script is long on practically every bar; the "
                  "brick cross it labels never reaches the orders. No defined signal to test."),
    369999: ("1", "The orders test a float and a plot handle as booleans: `if diosc` (DI+ - DI-, true whenever "
                  "non-zero) -> long, `else if p2` (a plot id) -> short. Long on practically every bar; the short "
                  "branch depends on how the runtime casts a plot handle. No defined signal to test."),
    # ---- worker A, batch A17 (2026-10-08)
    370728: ("1", "The orders read a nested request: security(heikinashi(ticker), 'D', x) where x is itself "
                  "security(ticker, 'D', open[1], lookahead_on). Which daily bar (and whether Heikin-Ashi or "
                  "regular prices) reaches the orders depends on how the runtime resolves a nested request on "
                  "a different ticker; the higher-timeframe values are undefined without choosing (as #361719)."),
    # ---- worker A, batch A18 (2026-10-08)
    380446: ("1", "The exit is a four-step take-profit ladder (25 % of the position at +3 %, +5 %, +7 %, the rest at "
                  "+10 %, all with a 15 % stop, in ticks): partial exits cannot be expressed as one net "
                  "position's signals (as #365389)."),
    380530: ("1", "strategy.order (not entry) adds a unit on every bar whose hour equals an hour estimated from "
                  "cumulative ROC x hour statistics since the first bar, with no exit or reversal: the position "
                  "is a running sum of orders, so the size path is the strategy."),
    392636: ("1", "The exit is a partial take-profit ladder (10 % of the position at +2 %, 50 % at +5 %, the rest "
                  "on a close below an ATR stop): partial exits cannot be expressed as one net position's "
                  "signals (as #365389). pyramiding=2 also stacks entries."),
    395966: ("1", "A Pine documentation example: two pyramided units opened on Monday / Tuesday and closed by "
                  "entry id on Thursday / Friday; the outcome is a position-size ladder by weekday, not "
                  "entries/exits of one net position."),
    416875: ("1", "Martingale: every second it buys or sells a growing bet according to the last candle's colour, "
                  "multiplying the size after wins and losses and stopping after four losses. The position "
                  "size sequence is the strategy (tick loop as well)."),
    # ---- worker A, batch A19 (2026-10-08)
    422794: ("1", "Martingale ladder: pyramiding=6 and strategy.order adds strategy.position_size * martinFactor "
                  "to a losing position (lines 55-67); the position size depends on fills, not on a bar rule "
                  "(as #395966, #416875)."),
    425798: ("1", "The entry and exit tests read BKVOL <> 1 / BKVOL = 1 / SKVOL = 1 (exactly one lot held), so "
                  "the rules change with the sizing formula LOTS; and the stop multiplier LIQKA is a plain "
                  "(non-VARIABLE) MyLanguage name decremented each held bar (lines 102-108), whose persistence "
                  "across bars is undefined. No defined signal to test."),
    # ---- worker A, batch A20 (2026-10-08)
    426261: ("1", "The opening range and the entry window come from session strings ('0930-1100', "
                  "'0930-1000', '1000-1100') read through time() and security() at 1- and 30-minute "
                  "resolutions on the 1h header chart: the exchange time zone of a crypto pair and what a "
                  "lower-resolution time()/security() returns per chart bar are undefined, so the bars "
                  "that may trade are not defined (as #361719)."),
    426302: ("1", "3Commas DCA bot: up to 6 safety orders add strategy.position_size * 1.55 below the entry "
                  "(strategy.order), and the stop / target are fractions of the averaged position price; the "
                  "position ladder is the strategy (as #422794)."),
    426334: ("1", "The whole signal is SCORE, which calls ta.ema(close, n) for n = 1..21 inside one for-loop "
                  "call site: the EMA's recursive state (its [1] value) is shared across the 21 calls, so "
                  "what each length reads is defined by the runtime, not the script. Also a trailing stop "
                  "order from highs and buys blocked for the rest of the calendar day after any fill."),
    # ---- worker A, batch A21 (2026-10-08)
    426361: ("1", "The only exit is strategy.exit('close', 'buy') with no profit / loss / stop / limit / trail "
                  "argument (an error on TradingView, no exit level on any runtime), so a long entered on "
                  "the MA crossing 40 has no defined exit (as #368717)."),
    426364: ("1", "KD inventory model: strategy.order adds or removes one default unit per bar until the "
                  "position reaches a target share count (0.33 steps of 20 / -10 shares); the position "
                  "size path is the strategy (as #380530)."),
    426455: ("1", "Four strategy.exit calls share the id 'Exit' with no from_entry: two set a 300-tick stop "
                  "with a 150 / 50-tick trailing stop, two (when= buy / sell) set no exit level at all. "
                  "Which exit order is live on a bar depends on how the runtime merges re-issued ids; the "
                  "exits are undefined."),
    426461: ("1", "pyramiding = 10 with entries repeated on every signal bar, the first long rule adding only "
                  "below strategy.position_avg_price: a pyramided averaging ladder (as #395966, #422794)."),
    426478: ("1", "The signal is a crossover of security(tickerid, '375', close) and security(..., open) on "
                  "the daily header chart: a 375-minute resolution below the chart's, whose value per daily "
                  "bar (and 375-minute block alignment on a 24 h market) is undefined (as #426261)."),
    # ---- worker A, batch A22 (2026-10-08)
    426509: ("1", "pyramiding = 5 with entries repeated on every signal bar, the long rule adding only below "
                  "strategy.position_avg_price: a pyramided averaging ladder (as #426461)."),
}

DUPLICATE_ON_READING = {
    128126: (127691, "Same rules and defaults as #127691 (SLOSS 2, N 200, M 4; parameters as arguments instead "
                     "of constants, HHV/LLV inline instead of named). Exact duplicate in behaviour (rule 7)."),
}

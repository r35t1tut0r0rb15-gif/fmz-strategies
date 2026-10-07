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
}

DUPLICATE_ON_READING = {
    128126: (127691, "Same rules and defaults as #127691 (SLOSS 2, N 200, M 4; parameters as arguments instead "
                     "of constants, HHV/LLV inline instead of named). Exact duplicate in behaviour (rule 7)."),
}

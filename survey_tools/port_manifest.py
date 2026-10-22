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
    # ---- worker A, batch A23 (2026-10-08)
    426557: [], 426571: [], 426579: [], 426587: [],
    426521: [
        ("Commented-out strategy(): pyramiding 3, percent of equity (not active)", 103, 103),
    ],
    426561: [
        ("Commented-out strategy(): 100 % of equity, commission, slippage (not active)", 96, 96),
    ],
    426581: [
        ("strategy(): 100 % of equity, commission, pyramiding 0", 116, 116),
    ],
    426593: [
        ("Hard-coded capital and position size", 83, 84),
        ("Trailing stop: offset input, tracked extreme and strategy.exit(trail_price, trail_offset)", 79, 107),
        ("Entries with qty = positionSize", 111, 120),
    ],
    426598: [
        ("strategy(): 100 % of equity", 66, 66),
    ],
    426604: [
        ("strategy(): 100 % of equity, initial capital 200", 82, 82),
        ("Take profit re-issued at 1.3 % of the current close", 107, 107),
    ],
    # ---- worker A, batch A24 (2026-10-08)
    426612: [], 426618: [], 426774: [], 426776: [],
    426613: [
        ("strategy(): initial capital, percent of equity", 80, 80),
    ],
    426616: [
        ("strategy(): 100 % of equity, pyramiding 0", 96, 96),
        ("Leverage input", 101, 101),
        ("Lot = equity / close x leverage, held while in position", 138, 138),
        ("Entries with qty lot (0 when a side is disabled)", 145, 151),
    ],
    426619: [
        ("strategy(): 100 % of equity", 90, 90),
    ],
    426625: [
        ("Entries with qty 0", 83, 84),
    ],
    426626: [
        ("strategy(): initial capital 20000, 100 % of equity, commission", 93, 93),
    ],
    426778: [
        ("strategy(): initial capital 50000", 140, 140),
    ],
    426779: [
        ("2 % of equity position size (computed, unused by the order)", 104, 104),
        ("Bracket from the signal close, re-issued at each 16:00 bar", 98, 107),
    ],
    # ---- worker A, batch A25 (2026-10-08)
    426780: [], 426794: [], 426799: [], 426807: [], 426810: [],
    426783: [
        ("strategy(): initial capital 100000", 117, 117),
    ],
    426786: [
        ("strategy(): 100 % of equity", 123, 123),
    ],
    426797: [
        ("strategy(): initial capital 1000, 100 % of equity", 121, 121),
    ],
    426801: [
        ("Entries with qty 1", 147, 152),
    ],
    426806: [
        ("strategy(): cash 10000 per order, initial capital 10000", 127, 127),
    ],
    426808: [
        ("Commented-out strategy(): qty 10000 (not active)", 135, 135),
    ],
    # ---- worker A, batch A26 (2026-10-08)
    426812: [], 426816: [],
    426824: [
        ("Commented-out strategy(): cash 10000 (not active)", 126, 126),
        ("Stop input (unused) and Q", 185, 187),
    ],
    426829: [
        ("strategy(): initial capital, 100 % of equity, pyramiding 1, commission", 141, 144),
    ],
    426834: [
        ("strategy(): 100 % of equity, initial capital, commission", 132, 132),
        ("Risk input", 136, 136),
        ("Long contracts from equity risk and the stop distance", 177, 178),
        ("Short contracts from equity risk and the stop distance", 189, 190),
    ],
    426836: [
        ("strategy(): initial capital 10000, 30 % of equity", 118, 118),
    ],
    426838: [
        ("strategy(): cash 1000, initial capital 1000", 191, 199),
    ],
    426842: [
        ("Stop loss / target in $ inputs", 146, 147),
        ("openprofit thresholds in the close conditions (balance checks)", 178, 181),
    ],
    426843: [
        ("strategy(): cash 1000, pyramiding 0, commission", 122, 123),
        ("Entry qty = equity / close", 136, 136),
        ("Basis points input (tick scaling of the target)", 127, 127),
    ],
    426844: [
        ("strategy(): initial capital 100, 100 % of equity, commission", 125, 125),
    ],
    426847: [
        ("Initial capital, balance and floating P/L", 143, 143),
        ("Balance / floating P/L, risk and equity-protection inputs", 181, 185),
        ("Equity protector and risk-based lot size", 191, 204),
    ],
    # ---- worker A, batch A27 (2026-10-08)
    426852: [], 426854: [], 426879: [], 426883: [], 426885: [],
    426848: [
        ("Commented-out strategy(): initial capital (not active)", 152, 152),
        ("Exit profit / loss in ticks scaled by 10", 203, 211),
    ],
    426855: [
        ("strategy(): percent of equity, pyramiding 0", 133, 133),
        ("Leverage input and lot = equity / close x leverage", 138, 182),
    ],
    426856: [
        ("strategy(): cash 100000, pyramiding 1", 139, 139),
        ("Position factors (trend 1, mean reversion 0.5)", 145, 146),
        ("Factor choice and entry qty", 170, 176),
    ],
    426884: [
        ("strategy(): fixed qty 1, pyramiding 1", 118, 118),
    ],
    426886: [
        ("strategy(): 10 % of equity, pyramiding 0", 150, 150),
    ],
    426461: [
        ("strategy(): 100 % of equity, pyramiding 10", 158, 158),
        ("Entries with qty 0 when a side is disabled", 236, 246),
    ],
    426509: [
        ("strategy(): 100 % of equity, pyramiding 5", 116, 116),
        ("Entries with qty 0 when a side is disabled", 177, 181),
    ],
    426588: [
        ("strategy(): 100 % of equity, initial capital 100, pyramiding 2, commission", 82, 87),
    ],
    # ---- worker A, batch A28 (2026-10-08)
    426888: [], 426891: [], 426894: [], 426902: [], 426904: [], 426906: [], 426908: [],
    426889: [
        ("strategy(): margin_long / margin_short 100", 136, 136),
        ("Take profit / stop loss in ticks", 138, 139),
    ],
    426895: [
        ("strategy(): 100 % of equity", 143, 143),
    ],
    426901: [
        ("strategy(): initial capital 10000, commission", 179, 179),
    ],
    426905: [],
    426923: [
        ("strategy(): initial capital 1000", 151, 151),
        ("Stop / target inputs", 199, 200),
        ("Balance, risk and lot size", 210, 220),
        ("Bracket in ticks from the current close", 269, 270),
    ],
    426925: [
        ("strategy(): initial capital 10000, percent of equity", 129, 129),
    ],
    # ---- worker A, batch A29 (2026-10-08)
    426933: [], 426993: [],
    426928: [("Commented-out strategy(): qty 15 (not active)", 156, 156)],
    426929: [("strategy(): 100 % of equity, commission", 100, 100)],
    426932: [("Trade size 1 and entries with it", 83, 91)],
    426990: [("strategy(): percent of equity", 133, 133)],
    426991: [("Commented-out strategy() (not active)", 141, 141)],
    426995: [
        ("strategy(): percent of equity", 142, 142),
        ("Entries with qty 0 against the trend / when a side is disabled", 189, 193),
    ],
    426996: [("Commented-out strategy(): qty 100 (not active)", 152, 153)],
    427001: [("strategy(): percent of equity; the qty-0 closing entry", 143, 158)],
    427017: [
        ("Commented-out strategy(): calc_on_order_fills (not active)", 173, 173),
        ("Order delay inputs (off by default)", 179, 222),
    ],
    # ---- FMZ-C, batch C1 (2026-10-15)
    427064: [
        ("strategy(): pyramiding = 2", 154, 154),
        ("Pyramid add: a second entry while long when RSI crosses above 10 (not ported)", 203, 204),
        ("Stop value from the averaged price (ported as a close-based exit on the entry fill)", 206, 207),
        ("TP / SL closes with qty = position_size", 245, 251),
    ],
    427065: [],
    427067: [],
    427071: [],
    427090: [
        ("strategy(): 100 % of equity per trade, pyramiding 0", 118, 118),
    ],
    427120: [
        ("strategy(): 100 % of equity per trade, pyramiding 0; per-side qty 0 switch", 174, 174),
        ("Entries with qty switched off by needlong / needshort", 228, 234),
    ],
    427122: [],
    427123: [
        ("Commented-out strategy(): pyramiding 50, cash qty 1000, calc_on_every_tick (not active)", 147, 147),
        ("TP / SL inputs and levels from the averaged price (ported via stops())", 170, 174),
        ("Bracket and RSI exit orders", 182, 184),
    ],
    427125: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 1, initial capital 100", 117, 117),
        ("Backtest date window (dropped)", 122, 126),
    ],
    427136: [],
    # ---- FMZ-C, batch C2 (2026-10-15)
    427142: [],
    427157: [],
    427162: [],
    427164: [
        ("strategy(): pyramiding 2, 50 % of equity per unit, commission", 201, 202),
        ("Backtest month / year window inputs (dropped)", 231, 236),
    ],
    427185: [
        ("strategy(): 100 % of equity per trade, pyramiding 0", 150, 150),
        ("Entries with qty 0 against the trend (needct off) and the year window", 214, 221),
    ],
    427187: [
        ("Lot size from ATR (investment / ATR x 0.1; computed, never passed to an order)", 156, 172),
        ("Moving take-profit limit re-issued every bar (ported as a fixed tp_stop, mark trailing_stop_pending)", 190, 196),
    ],
    427188: [],
    427189: [
        ("strategy(): 100 % of equity per trade, pyramiding 0", 158, 158),
        ("Percent stop inputs and levels (off by default: needstops false)", 163, 164),
        ("Stop levels and stop exits", 234, 245),
    ],
    # ---- FMZ-C, batch C3 (2026-10-16)
    427186: [
        ("strategy(): cash qty 5000 EUR per trade", 163, 163),
        ("Initial stop at the averaged price / 1.08 (x 1.08 for shorts), ported via stops()", 243, 245),
    ],
    427197: [
        ("strategy(): pyramiding 0, commission 0.0675 %", 197, 197),
    ],
    427239: [
        ("Take-profit / stop-loss / trailing inputs in ticks (TP and SL ported as ATR multiples via stops())", 227, 239),
        ("Bracket exits per side (trail_offset na: no trailing)", 259, 260),
    ],
    427257: [],
    427258: [
        ("strategy(): 100 % of equity, pyramiding 0", 174, 174),
        ("Entries with qty 0 when a side is off; the close_all of the backtest window", 198, 205),
    ],
    427260: [],
    427261: [],
    427264: [],
    427266: [
        ("strategy(): pyramiding 1, cash qty 10000", 189, 189),
        ("Trailing stop percent input", 203, 204),
        ("Trailing stop level on closes (ported natively as the house percent trail, anchor close)", 222, 228),
        ("Stop exit order", 243, 244),
    ],
    427267: [
        ("strategy(): initial capital 1000", 192, 192),
        ("Entries with qty 1", 210, 211),
    ],
    427269: [],
    427272: [
        ("Commented-out strategy(): percent of equity sizing (not active)", 159, 159),
    ],
    427274: [],
    # ---- FMZ-C, batch C4 (2026-10-16)
    427275: [
        ("Backtest window switch and dates (isPeriod is the constant true: never acts)", 278, 297),
    ],
    427276: [],
    427280: [],
    427281: [],
    427282: [],
    427290: [
        ("strategy(): 100 % of equity, initial capital 100, commission 0.075 %", 162, 162),
    ],
    427291: [
        ("strategy(): initial capital 1 BTC, commission", 160, 160),
    ],
    427292: [
        ("Trailing / take-profit / stop-loss / pyramiding inputs in price units / 10000 (TP / SL ported as ATR multiples)", 200, 204),
        ("Leverage input and liquidation levels (not ported: sizing)", 270, 274),
        ("Close orders (liquidation, TP, SL, trailing)", 280, 287),
    ],
    427298: [],
    427300: [],
    427301: [
        ("Percent trailing stop input, levels and stop orders (pending: ratchets on 2-hour closes)", 158, 182),
    ],
    427302: [],
    427303: [],
    # ---- FMZ-C, batch C5 (2026-10-16)
    427304: [
        ("strategy(): 100 % of equity, commission 0.075 %", 179, 179),
        ("ATR stop inputs and levels (ported via stops(), re-based on each fill)", 265, 273),
        ("Orders and stop exits", 276, 280),
    ],
    427305: [
        ("strategy(): 100 % of equity, initial capital 1000", 177, 177),
    ],
    427308: [
        ("strategy(): 100 % of equity, per-contract commission", 183, 183),
    ],
    427309: [],
    427310: [
        ("Take-profit / stop-loss inputs in pips (ported as ATR multiples)", 178, 180),
        ("Close-based TP / SL exits from the averaged price", 195, 196),
    ],
    427312: [
        ("Equity / drawdown display lines (no orders)", 132, 139),
    ],
    427313: [
        ("strategy(): 10 % of equity, pyramiding 0", 124, 124),
    ],
    427314: [
        ("Pyramiding, stop and trailing inputs in pips", 158, 161),
        ("Per-unit bookkeeping for the pyramiding gate", 164, 353),
        ("Entries and the stop / trailing exits in ticks (ported as ATR stop + house volatility trail)", 358, 362),
    ],
    427342: [],
    427346: [],
    427347: [
        ("strategy(): 100 % of equity, pyramiding 0", 125, 125),
    ],
    427348: [],
    # ---- FMZ-C, batch C6 (2026-10-16)
    427367: [
        ("strategy(): pyramiding 2, fixed qty 3, initial capital", 154, 154),
        ("Add while below the average price (not ported)", 186, 186),
    ],
    427369: [
        ("strategy(): 100 % of equity, commission 0.1 %", 164, 164),
        ("Pyramiding gate inputs (section counters)", 264, 266),
    ],
    427370: [],
    427372: [
        ("strategy(): pyramiding 100, commission 0.25 %", 152, 152),
        ("Entry qty 1 with the averaging protection; the gain-protected close_all", 183, 184),
    ],
    427375: [],
    427381: [],
    427382: [
        ("strategy(): 100 % of equity, initial capital 1000", 164, 164),
    ],
    427383: [
        ("strategy(): 100 % of equity, initial capital", 166, 166),
        ("ATR stop inputs and levels (ported via stops())", 224, 231),
    ],
    427384: [],
    427385: [
        ("Orders with qty 1 (strategy.order nets units)", 252, 253),
    ],
    427386: [
        ("Order size floor(50000 / close)", 216, 216),
        ("Entries with the order size and the 100 % closes", 218, 238),
    ],
    # ---- FMZ-C, batch C7 (2026-10-16)
    427387: [],
    427388: [
        ("Entry with qty 1", 175, 175),
    ],
    427390: [
        ("strategy(): 75 % of equity, initial capital 100", 170, 170),
        ("Stop-loss percent input", 171, 171),
        ("Orders and the 3 % stop exits (ported via stops())", 322, 328),
    ],
    427391: [
        ("Leverage input and the leveraged contract quantity", 215, 221),
        ("Orders with the quantity", 222, 228),
    ],
    427396: [],
    427397: [],
    427398: [
        ("strategy(): pyramiding 100", 198, 198),
    ],
    427399: [
        ("strategy(): cash qty 50000, initial capital 50000", 210, 210),
    ],
    427436: [],
    427437: [
        ("strategy(): 100 % of equity, per-order commission, slippage", 126, 126),
    ],
    427438: [],
    427440: [
        ("strategy(): 100 % of equity, pyramiding 5", 140, 140),
    ],
    427445: [],
    # ---- FMZ-C, batch C8 (2026-10-16)
    427449: [
        ("strategy(): 100 % of equity, initial capital, commission 0.1 %", 121, 121),
    ],
    427453: [],
    427455: [
        ("strategy(): pyramiding 1; the add while long", 141, 141),
        ("Entry / add and the trailing-line close", 187, 202),
    ],
    427458: [],
    427460: [],
    427461: [
        ("strategy(): pyramiding 2, cash qty", 165, 165),
        ("Two entries with cash quantities 30000 / close and 20000 / close", 192, 198),
        ("Profit-gated stop on openprofit in cash", 205, 205),
    ],
    427467: [],
    427468: [],
    427470: [
        ("strategy(): commission 0.075 %", 121, 121),
    ],
    427471: [],
    427479: [],
    427482: [],
    # ---- FMZ-C, batch C9 (2026-10-16)
    427483: [],
    427485: [],
    427487: [
        ("Commented-out strategy(): pyramiding 50, cash qty 20, commission 0.25 %", 203, 203),
        ("Entry with the averaging protection and the gain-protected close_all", 217, 218),
    ],
    427506: [
        ("strategy(): 100 % of equity, pyramiding 0", 196, 196),
        ("Percent stop inputs (off by default)", 201, 202),
        ("Orders, stops and the window close_all", 264, 276),
    ],
    427507: [
        ("strategy(): pyramiding 20, initial capital", 212, 213),
    ],
    427508: [
        ("Stop-loss / take-profit inputs and levels (never used by an order)", 224, 228),
    ],
    427510: [],
    427512: [
        ("strategy(): 10 % of equity", 192, 192),
        ("Max intraday loss input and the commented-out risk rule", 202, 204),
    ],
    427513: [
        ("Capital, position, commission, pyramiding, tick settings", 185, 199),
    ],
    427516: [],
    427526: [
        ("strategy(): pyramiding 0, initial capital, commission", 197, 197),
        ("Entries with qty 4 / 1 and the closes", 314, 320),
    ],
    427528: [
        ("strategy(): 100 % of equity, initial capital, commission", 156, 156),
    ],
    # ---- FMZ-C, batch C10 (2026-10-16)
    427529: [
        ("strategy(): 100 % of equity, initial capital, commission", 243, 243),
        ("Leverage and percent-of-equity inputs", 245, 246),
        ("Leveraged quantity and the entries", 349, 354),
    ],
    427588: [
        ("Commented-out strategy(): pyramiding 100", 207, 207),
    ],
    427591: [
        ("Commented-out strategy(): default quantity 100", 210, 210),
        ("Take-profit / stop-loss inputs in ticks", 222, 223),
        ("Bracket exits", 264, 268),
    ],
    427592: [
        ("strategy(): 10 % of equity, initial capital, commission", 218, 218),
        ("Entries with the leveraged capital quantity", 267, 270),
        ("Stop and trailing exits", 274, 275),
    ],
    427593: [],
    427607: [
        ("strategy(): 100 % of equity, pyramiding 0", 160, 160),
        ("Short entry with the only-long quantity", 183, 183),
    ],
    427613: [
        ("Stop-loss exit in ticks", 267, 267),
    ],
    427614: [
        ("strategy(): 10 % of equity", 161, 161),
    ],
    427615: [
        ("Commented-out strategy(): BTC capital, 1 % of equity, commission, slippage", 177, 177),
        ("Open-profit close-all thresholds", 191, 193),
    ],
    427616: [],
    427666: [
        ("strategy(): 100 % of equity, initial capital, commission", 144, 144),
        ("Trailing take-profit exits", 186, 187),
    ],
    427671: [],
    # ---- FMZ-C, batch C11 (2026-10-16)
    427672: [],
    427673: [],
    427674: [
        ("strategy(): 100 % of equity, initial capital", 223, 223),
        ("Bracket exits with prices passed as tick counts", 242, 245),
    ],
    427679: [],
    427680: [
        ("strategy(): 100 % of equity, initial capital, commission", 215, 215),
    ],
    427683: [],
    427684: [],
    427727: [
        ("Commented-out strategy(): pyramiding 2, fixed quantity 100, commission", 176, 179),
        ("USD profit / stop goals", 273, 276),
        ("Bracket exits", 293, 298),
    ],
    427729: [
        ("Leverage input", 179, 179),
        ("Leveraged position size and the entries", 205, 222),
        ("Take-profit exits in ticks", 237, 244),
    ],
    427733: [
        ("Commented-out strategy(): 10 % of equity, pyramiding 2, commission", 174, 179),
        ("Percent stop inputs and the stop exits", 230, 250),
    ],
    427806: [],
    427809: [],
    # ---- FMZ-C, batch C12 (2026-10-16)
    427810: [
        ("strategy(): initial capital", 200, 200),
    ],
    427811: [
        ("Take-profit / stop / trail inputs (0 = off)", 266, 276),
        ("Exits with the off inputs", 292, 293),
    ],
    427813: [],
    427814: [
        ("strategy(): 100 % of equity, pyramiding 0", 221, 221),
        ("Entries with the long / short switch quantities", 270, 273),
    ],
    427816: [
        ("Commented-out strategy() line", 186, 186),
    ],
    427821: [
        ("Stop / take-profit percent inputs and levels", 185, 191),
        ("Bracket exit", 195, 195),
    ],
    # ---- FMZ-C, batch C13 (2026-10-16)
    427822: [
        ("strategy(): 10 % of equity, initial capital, commission, pyramiding 0", 206, 206),
        ("Take-profit / stop inputs", 222, 223),
        ("Bracket exits re-issued on each signal bar", 293, 299),
    ],
    427823: [
        ("strategy(): pyramiding 100, 100 % of equity, initial capital, commission", 220, 221),
        ("Trailing stop inputs", 495, 500),
        ("Stop-loss inputs", 594, 597),
        ("Pips correction and the trailing exits", 770, 775),
    ],
    427861: [
        ("strategy(): 100 % of equity, initial capital", 165, 165),
    ],
    427862: [],
    427871: [
        ("Commented-out strategy(): 75 % of equity, initial capital, commission", 116, 116),
        ("Percent stop inputs, levels and the stop exits", 163, 211),
    ],
    427878: [],
    427881: [
        ("Commented-out strategy(): 20 % of equity, pyramiding 0, commission", 132, 132),
    ],
    427883: [],
    427884: [],
    427886: [
        ("strategy(): pyramiding 2, 50 % of equity, initial capital", 192, 192),
    ],
    427893: [],
    427894: [
        ("Quantity, position cap and exit inputs", 189, 219),
        ("Exit levels and the trail variable", 227, 234),
        ("Risk rules, the entry quantity and the exit", 275, 291),
    ],
    # ---- FMZ-C, batch C14 (2026-10-16)
    427895: [],
    427910: [
        ("Commented-out strategy(): 10 % of equity, commission, slippage", 300, 302),
    ],
    427921: [
        ("strategy(): 100 % of equity, initial capital", 237, 237),
        ("Stop / take-profit inputs", 241, 244),
        ("Stop / take-profit exits", 350, 351),
    ],
    427923: [
        ("strategy(): 100 % of equity, initial capital, commission", 178, 178),
    ],
    427925: [
        ("strategy(): 100 % of equity", 153, 153),
    ],
    427930: [],
    427932: [],
    427933: [],
    427985: [],
    427986: [
        ("strategy(): margin settings", 179, 179),
    ],
    427987: [
        ("strategy(): 100 % of equity", 155, 155),
    ],
    # ---- FMZ-C, batch C15 (2026-10-16)
    427989: [
        ("strategy(): 100 % of equity, initial capital, commission", 192, 192),
        ("Direction rule and swing stop / target inputs", 194, 216),
        ("Swing exits (off by default)", 251, 253),
    ],
    427990: [
        ("strategy(): pyramiding 0, percent of equity, slippage, commission", 146, 146),
        ("Percent stop / target inputs, levels and exits", 237, 249),
    ],
    427992: [],
    427994: [],
    427998: [
        ("strategy(): cash quantity 10000, initial capital, commission", 142, 142),
    ],
    428000: [
        ("Initial capital", 191, 191),
        ("TP / SL tick inputs", 223, 224),
        ("Risk-based lot size", 230, 238),
        ("Entries with the tick exits", 240, 252),
    ],
    428051: [
        ("strategy(): 100 % of equity, pyramiding 0", 195, 195),
        ("Martingale and capital inputs", 200, 201),
        ("Profit, martingale multiplier and lot", 248, 250),
    ],
    428052: [
        ("strategy(): 100 % of equity, commission", 176, 176),
        ("Stop / target inputs", 182, 183),
        ("Percent exits", 297, 300),
    ],
    428053: [],
    428056: [
        ("Risk, AutoView and account inputs", 209, 214),
        ("Conversion security and position-size functions", 248, 272),
        ("Stop / target levels", 276, 282),
        ("Exits", 330, 331),
    ],
    428059: [],
    428060: [
        ("strategy(): initial capital", 209, 211),
        ("Order stake input", 219, 219),
        ("Order size, trailing stop and orders", 263, 282),
    ],
    # ---- FMZ-C, batch C16 (2026-10-16)
    428067: [
        ("strategy(): 100 % of equity", 199, 200),
        ("Profit / stop point inputs", 261, 262),
        ("Point exits", 308, 309),
    ],
    428068: [],
    428071: [],
    428075: [],
    428081: [
        ("strategy(): pyramiding 0, 100 % of equity, initial capital, commission", 170, 178),
        ("Stop inputs (off by default)", 185, 186),
        ("Stop levels and exits", 206, 210),
    ],
    428083: [],
    428084: [],
    428086: [
        ("strategy(): pyramiding 0, 100 % of equity, initial capital, slippage, commission", 163, 176),
    ],
    428088: [
        ("strategy(): pyramiding 9, initial capital, percent of equity", 183, 183),
    ],
    428089: [],
    428093: [],
    428100: [
        ("Equity-based order size and the entries", 241, 244),
    ],
    # ---- FMZ-C, batch C17 (2026-10-16)
    428101: [
        ("Exit, margin and leverage inputs (exits off)", 206, 218),
        ("Tick exits", 220, 229),
        ("RSI exits with the profit read-outs (off)", 232, 241),
    ],
    428103: [],
    428106: [
        ("Commented-out strategy(): cash quantity, initial capital, commission", 157, 164),
    ],
    428575: [],
    428577: [],
    428578: [],
    428579: [
        ("strategy(): initial capital, commission", 172, 172),
        ("Leverage and the fixed USD position size", 184, 202),
        ("Position size at entry", 289, 289),
    ],
    428581: [],
    428582: [],
    428583: [
        ("Commented-out strategy() settings", 179, 197),
    ],
    428608: [
        ("strategy(): 100 % of equity, initial capital", 128, 129),
    ],
    # ---- FMZ-C, batch C18 (2026-10-16)
    428616: [],
    428619: [
        ("Commented-out strategy(): initial capital, quantity", 202, 202),
    ],
    428625: [
        ("Commented-out strategy() line", 182, 182),
        ("Take-profit / stop inputs", 197, 198),
        ("Percent exits", 317, 336),
    ],
    428626: [],
    428629: [],
    428630: [
        ("Commented-out strategy() line", 140, 140),
        ("Martingale and capital inputs", 145, 146),
        ("Profit, martingale multiplier and lot", 197, 199),
    ],
    428681: [
        ("Commented-out strategy(): initial capital, quantity", 156, 156),
    ],
    428683: [],
    428684: [
        ("strategy(): 100 % of equity, initial capital, commission", 216, 216),
    ],
    428691: [],
    428692: [
        ("strategy(): pyramiding 0, cash quantity 20000, initial capital", 145, 145),
        ("Tick target / stop and quantity percent", 166, 168),
        ("Tick exits", 172, 173),
    ],
    # ---- FMZ-C, batch C19 (2026-10-16)
    428693: [],
    428696: [],
    428698: [
        ("Commented-out strategy(): initial capital, quantity", 195, 195),
        ("Quantity input", 197, 197),
    ],
    428699: [
        ("Commented-out strategy(): 100 % of equity, pyramiding, commission, capital, intrabar settings", 179, 179),
    ],
    428700: [
        ("strategy(): initial capital, cash quantity, slippage, commission, pyramiding", 186, 186),
    ],
    428703: [
        ("Capital, position, commission, pyramiding and intrabar constants", 131, 138),
        ("Commented-out strategy()", 141, 142),
    ],
    428704: [],
    428705: [],
    428706: [],
    428708: [],
    428719: [],
    428756: [
        ("strategy(): pyramiding 5", 55, 55),
        ("Take-profit / stop multipliers (inert as written)", 59, 60),
        ("Long exit or add, with the level variables", 98, 112),
        ("Short exit or add, with the level variables", 114, 128),
    ],
    # ---- FMZ-C, batch C20 (2026-10-16)
    428782: [
        ("strategy(): pyramiding, 100 % of equity, initial capital", 279, 285),
    ],
    428783: [
        ("Commented-out strategy(): initial capital, quantity", 157, 157),
    ],
    428785: [
        ("Commented-out strategy(): 100 % of equity, capital", 198, 198),
    ],
    428790: [],
    428793: [],
    428794: [
        ("strategy(): pyramiding, commission, 100 % of equity", 155, 155),
    ],
    428795: [
        ("Take-profit / stop / trailing inputs and their na handling", 194, 206),
        ("strategy.exit with profit / loss / trail_points / trail_offset", 226, 227),
    ],
    428797: [],
    428801: [
        ("strategy(): pyramiding 1, commission, capital", 169, 169),
    ],
    428802: [],
    428805: [
        ("strategy(): 100 % of equity", 184, 184),
        ("Stop-loss / take-profit inputs", 193, 194),
        ("strategy.exit, percent of the close in ticks", 205, 205),
    ],
    428810: [
        ("strategy(): 100 % of equity, capital, commission", 231, 231),
        ("Pyramiding count inputs and conditions", 354, 359),
        ("Trailing stop, take profit, stop loss (off by default) and close signals", 427, 466),
    ],
    # ---- FMZ-C, batch C21 (2026-10-16)
    428811: [
        ("Take-profit / stop-loss inputs", 304, 305),
        ("strategy.exit with profit / loss when touch", 310, 311),
    ],
    428812: [
        ("Commented-out strategy(): capital, commission", 185, 185),
        ("Stop input", 269, 269),
        ("Money management: risk % of equity -> size", 296, 308),
        ("Orders: entries, time closes and stop exits", 311, 321),
    ],
    428813: [
        ("strategy(): capital, 100 % of equity, commission", 146, 147),
    ],
    428814: [],
    428816: [],
    428853: [
        ("Conditional stop exits (pending, not emitted)", 284, 292),
    ],
    428854: [
        ("Commented-out strategy(): pyramiding, quantity", 135, 135),
        ("Pyramiding count inputs and conditions", 226, 231),
        ("Trailing stop (off by default), take profit, stop loss and close signals", 299, 338),
    ],
    428855: [],
    428856: [
        ("strategy(): commission, capital, 100 % of equity", 187, 187),
        ("Take-profit / stop-loss inputs and levels (off by default)", 230, 245),
        ("TP / SL execution", 284, 290),
    ],
    428893: [],
    428966: [],
    # ---- FMZ-C, batch C22 (2026-10-16)
    428968: [],
    428969: [],
    428970: [
        ("strategy(): 100 % of equity, pyramiding", 162, 162),
    ],
    428973: [
        ("Commented-out strategy(): percent of equity", 254, 254),
        ("Stop-loss / take-profit inputs, levels and exits", 344, 357),
    ],
    428974: [
        ("strategy(): pyramiding, 100 % of equity, commission", 208, 208),
    ],
    428975: [],
    428981: [
        ("Commented-out strategy(): pyramiding, capital, 100 % of equity", 131, 131),
        ("Stop-loss / take-profit inputs", 138, 139),
        ("Entries with their exits", 160, 169),
    ],
    428982: [
        ("strategy(): 100 % of equity, pyramiding 5", 190, 190),
        ("Leverage input", 195, 195),
        ("Lot formula and sized entries", 240, 252),
    ],
    428985: [
        ("Commented-out strategy(): 100 % of equity, margins", 167, 167),
        ("Stop / take-profit / leverage inputs and quantity", 205, 213),
        ("Entries and bracket exits", 215, 227),
    ],
    428986: [
        ("Commented-out strategy(): capital, 100 % of equity, commission", 180, 180),
    ],
    429085: [
        ("strategy(): commission, capital, 100 % of equity", 210, 210),
    ],
    # ---- FMZ-C, batch C23 (2026-10-16)
    429086: [
        ("strategy(): margins", 173, 173),
        ("Risk-based bracket on signal bars (pending, not emitted)", 231, 249),
    ],
    429145: [
        ("Entries with their tick exits", 176, 182),
    ],
    429147: [
        ("Commented-out strategy(): capital, commission per contract", 246, 246),
        ("Strategy-tester inputs: sessions, loss limits, contract size, fixed TP / SL", 290, 301),
        ("Orders and the off-by-default TP / SL", 321, 352),
    ],
    429148: [
        ("Commented-out strategy(): fixed quantity, capital", 162, 162),
        ("ATR multipliers", 175, 176),
        ("Per-bar bracket and orders (bracket pending, not emitted)", 336, 353),
    ],
    429149: [
        ("strategy(): capital, 100 % of equity", 155, 155),
        ("ATR bracket and orders", 261, 266),
    ],
    429150: [
        ("Commented-out strategy(): 25 % of equity, commission", 214, 214),
    ],
    429159: [],
    429161: [
        ("Commented-out strategy(): 100 % of equity, capital", 212, 212),
    ],
    429333: [],
    429382: [
        ("Commented-out strategy(): 100 % of equity, intrabar settings", 182, 182),
    ],
    429383: [
        ("Take-profit / stop-loss inputs (off by default)", 157, 159),
        ("TP / SL closes (off by default)", 184, 188),
    ],
    429385: [
        ("Per-bar tick bracket (pending, not emitted)", 127, 138),
    ],
    # ---- FMZ-C, batch C24 (2026-10-16)
    429388: [
        ("strategy(): pyramiding 3", 219, 219),
        ("SAR trailing-stop inputs", 226, 229),
        ("SAR trailing-stop exits (pending, not emitted)", 263, 271),
    ],
    429389: [
        ("strategy(): 100 % of equity", 264, 264),
        ("Shorting / stop / trailing inputs (off by default)", 277, 284),
        ("Initial stop exits (off by default)", 315, 317),
    ],
    429390: [
        ("strategy(): capital, 100 % of equity, commission", 121, 121),
        ("ATR stop inputs, levels and exits", 183, 197),
    ],
    429392: [],
    429393: [
        ("Commented-out strategy(): cash quantity, capital, commission", 160, 160),
        ("Stop / target inputs and levels", 353, 358),
        ("Bracket exit", 386, 387),
    ],
    429459: [],
    429460: [
        ("strategy(): capital, 30 % of equity, commission", 133, 133),
    ],
    429464: [
        ("strategy(): capital, 100 % of equity, commission", 115, 115),
    ],
    429466: [],
    429467: [],
    # ---- FMZ-C, batch C25 (2026-10-16)
    429468: [
        ("strategy(): commission, pyramiding 1", 245, 245),
        ("Sized entries and the inert exits", 267, 271),
    ],
    429470: [
        ("Sized entry (10 units)", 146, 147),
    ],
    429471: [
        ("strategy(): 100 % of equity", 191, 191),
    ],
    429472: [
        ("strategy(): margins", 156, 156),
        ("Target / stop multipliers, early stop, stop level", 217, 224),
        ("Entries with their bracket and early closes", 229, 239),
    ],
    429478: [
        ("Capital, position, commission, pyramiding constants", 147, 151),
        ("strategy(): cash quantity, capital, commission", 153, 156),
        ("Stop / trail / buffer inputs", 163, 165),
        ("Inert stop-loss bookkeeping and exits", 193, 213),
    ],
    429479: [
        ("Money management: risk %, equity protection, ATR bracket, lot size", 368, 403),
        ("Orders: equity stop-out, entries, bracket exits, closes", 406, 417),
    ],
    429484: [
        ("strategy(): 100 % of equity, capital", 180, 180),
        ("TP / SL / trail inputs (off by default) and exits", 196, 218),
    ],
    429485: [],
    429488: [],
    429491: [
        ("strategy(): 100 % of equity", 119, 119),
    ],
    # ---- FMZ-C, batch C26 (2026-10-16)
    429489: [
        ("strategy(): capital, 10 % of equity", 204, 204),
        ("Entries with their bracket", 306, 315),
    ],
    429490: [
        ("strategy(): 100 % of equity", 175, 175),
    ],
    429493: [
        ("strategy(): capital", 139, 139),
    ],
    429494: [
        ("strategy(): capital, 100 % of equity", 153, 153),
        ("Stop input", 203, 203),
        ("Stop levels and exits", 211, 222),
    ],
    429496: [
        ("strategy(): pyramiding 1", 156, 156),
        ("Trailing stop level", 166, 177),
        ("Trailing stop exit", 213, 214),
    ],
    429497: [
        ("Commented-out strategy(): capital, 30 % of equity, process_orders_on_close", 146, 153),
        ("Trailing stop inputs and levels", 174, 191),
        ("Exit", 197, 197),
    ],
    429498: [
        ("Commented-out strategy(): cash quantity, capital", 195, 195),
        ("Risk / reward and pullback inputs", 203, 205),
        ("Entries with their bracket", 243, 254),
    ],
    429499: [
        ("Stop / target inputs", 131, 132),
        ("Levels, entries and the bracket exit", 148, 160),
    ],
    429502: [
        ("Lot input", 181, 181),
        ("Lot formula and sized entries", 199, 206),
    ],
    429504: [],
    # ---- FMZ-C, batch C27 (2026-10-16)
    429505: [
        ("Commented-out strategy(): 30 % of equity, commission, slippage", 202, 202),
    ],
    429506: [
        ("strategy(): capital, 100 % of equity, commission", 174, 174),
    ],
    429509: [
        ("Target / stop / lot inputs", 195, 198),
        ("Sized entries and the bracket exits", 213, 226),
    ],
    429512: [
        ("Sized entries and closes", 243, 254),
    ],
    429561: [],
    429564: [
        ("strategy(): 100 % of equity, capital, slippage", 166, 166),
        ("Stop / trail inputs", 205, 208),
        ("Entries and exits", 243, 249),
    ],
    429565: [],
    429569: [],
    # ---- FMZ-C, batch C28 (2026-10-16)
    429575: [
        ("strategy(): pyramiding 15", 219, 219),
    ],
    429576: [
        ("strategy(): close_entries_rule", 179, 179),
    ],
    429577: [],
    429651: [],
    429771: [],
    429777: [
        ("strategy(): capital, 25 % of equity, commission", 132, 132),
    ],
    # ---- FMZ-C, batch C29 (2026-10-16)
    429778: [
        ("TP / SL / trail inputs (off by default) and exits", 263, 292),
    ],
    429780: [
        ("Fixed-quantity entries (1 / 0)", 193, 194),
    ],
    429782: [
        ("strategy(): capital, 100 % of equity", 180, 180),
    ],
    429784: [],
    429786: [],
    429787: [],
    429948: [],
    429949: [
        ("strategy(): commission per contract", 155, 155),
        ("Sized entries and the limit exits (pending, not emitted)", 294, 303),
    ],
    429951: [],
    # ---- FMZ-C, batch C30 (2026-10-16)
    429953: [
        ("Exit criteria, trail, stop and target inputs", 321, 333),
        ("Trailing stop prices and bracket levels", 336, 355),
        ("Exit branches (default: SL + TGT%)", 360, 383),
    ],
    429954: [
        ("Repeated orders and the close", 214, 220),
    ],
    429956: [
        ("Stop-loss input (unused)", 103, 103),
    ],
    429958: [
        ("strategy(): 100 % of equity, pyramiding 100", 143, 143),
        ("Lot input and formula", 148, 148),
        ("Lot formula", 199, 199),
    ],
    429960: [],
    429963: [
        ("strategy(): pyramiding 1, fixed quantity 2, capital", 185, 185),
    ],
    429964: [],
    429967: [
        ("Spread, capital and order size", 193, 197),
        ("Static target inputs", 205, 206),
        ("Entries with their bracket exits", 212, 255),
    ],
    # ---- FMZ-C, batch C31 (2026-10-16)
    430007: [
        ("strategy(): 100 % of equity, pyramiding 0", 185, 185),
        ("Entries with the counter-trend qty 0", 239, 243),
    ],
    430009: [
        ("strategy(): 100 % of equity", 177, 177),
        ("Leverage input", 184, 184),
        ("Lot formula", 221, 221),
    ],
    430017: [
        ("strategy(): 100 % of equity, pyramiding 5", 184, 184),
    ],
    430020: [],
    430023: [],
    430036: [],
    430039: [],
    # ---- FMZ-C, batch C32 (2026-10-16)
    430044: [
        ("strategy(): 36,000 cash per order, pyramiding 1, commission", 175, 175),
        ("Stop input and the 5 % stop exit", 204, 209),
    ],
    430053: [
        ("Entries with the ATR bracket exits", 186, 196),
    ],
    430060: [
        ("Commented-out strategy(): 1,000 cash per order, commission", 243, 246),
    ],
    430065: [],
    430066: [
        ("strategy(): 100 % of equity, pyramiding 10", 182, 182),
        ("Capital % input", 185, 185),
        ("Lot fixed at the first entry", 226, 226),
    ],
    430067: [
        ("TP / SL inputs and the tick exits", 184, 196),
    ],
    430069: [],
    430117: [],
    430120: [
        ("Long entry size and close levels", 206, 211),
        ("Short entry size and close levels", 224, 229),
    ],
    430124: [],
    430125: [],
    430126: [],
    430142: [
        ("initial_capital and the entry quantity", 202, 203),
    ],
    # ---- FMZ-C, batch C33 (2026-10-16)
    430148: [
        ("strategy(): 15 % of equity", 130, 130),
    ],
    430150: [],
    430152: [],
    430162: [
        ("TP / stop / trail inputs", 210, 215),
        ("Entries with their bracket and trail exits", 320, 327),
    ],
    430164: [
        ("Fixed quantity 1 entries", 193, 194),
    ],
    430169: [
        ("strategy(): 10 % of equity, capital", 160, 160),
        ("Stop levels and exits", 199, 203),
    ],
    430170: [
        ("Commented-out strategy(): 10 % of equity, commission", 236, 237),
        ("TP / SL methods and levels", 254, 276),
        ("Bracket exits", 289, 294),
    ],
    430171: [
        ("Trailing size input and the (inert) stop exits", 204, 230),
    ],
    430174: [],
    430176: [],
    430244: [],
    # ---- FMZ-C, batch C34 (2026-10-16)
    430245: [
        ("Equity-based order size and entry", 231, 232),
    ],
    430254: [
        ("Risk input", 121, 121),
        ("Risk-based quantity and the bracket entry", 141, 150),
    ],
    430259: [
        ("strategy(): 100 % of equity, pyramiding 5", 154, 154),
        ("Lot % input", 159, 159),
        ("Lot fixed while in a position", 189, 190),
    ],
    430262: [
        ("strategy(): pyramiding 3", 192, 192),
    ],
    430264: [],
    430268: [],
    430269: [],
    430271: [],
    430276: [],
    430280: [
        ("strategy(): 100 % of equity", 186, 186),
        ("Stop % input", 191, 191),
        ("Stop levels", 206, 210),
    ],
    430285: [],
    430322: [
        ("Commented-out strategy(): order size, capital, pyramiding 1", 189, 189),
    ],
    # ---- FMZ-C, batch C35 (2026-10-16)
    430364: [
        ("strategy(): 100 % of equity", 163, 163),
        ("Stop / target levels and the exit", 176, 190),
    ],
    430366: [
        ("Buy quantity input (unused)", 177, 177),
        ("Equity-based order size and entry", 232, 235),
    ],
    430368: [
        ("Tick target / stop inputs and the exits", 154, 168),
    ],
    430372: [],
    430374: [
        ("strategy(): 100 % of equity", 178, 178),
        ("Stop option (off) and its level", 191, 206),
    ],
    430377: [
        ("strategy(): 100 % of equity", 185, 185),
        ("Stop / trailing options (off)", 201, 206),
        ("Stop exits (off)", 246, 248),
    ],
    430380: [
        ("Commented-out strategy(): 20 % of equity, commission", 210, 210),
    ],
    430383: [
        ("strategy(): 30 % of equity, commission", 276, 276),
        ("Stop / target levels and the close", 311, 317),
    ],
    430543: [],
    430544: [
        ("strategy(): 100 % of equity, commission", 184, 184),
        ("Loss tolerances and stop levels", 211, 215),
        ("Stop exits", 238, 239),
    ],
    430545: [],
    430549: [],
    # ---- FMZ-C, batch C36 (2026-10-16)
    430555: [],
    430556: [],
    430558: [
        ("Commented-out strategy(): 10,000 cash per order", 243, 243),
    ],
    430569: [
        ("Stop / target inputs and the shared-id exits", 191, 198),
    ],
    430570: [],
    430573: [
        ("Stop % input", 165, 165),
        ("Target and stop exits", 186, 190),
    ],
    430576: [
        ("Commented-out strategy(): 1,000 cash per order, pyramiding 1, commission", 173, 173),
    ],
    430583: [
        ("Take-profit / stop-loss inputs (price units)", 226, 227),
        ("Level checks", 238, 239),
    ],
    430585: [
        ("strategy(): 100 % of equity", 179, 179),
    ],
    # ---- FMZ-C, batch C37 (2026-10-16)
    430589: [
        ("Stop / target inputs and the bracket exit", 182, 190),
    ],
    430590: [],
    430592: [],
    430597: [],
    430598: [
        ("Commented-out strategy(): 10 % of equity, commission, pyramiding 0", 165, 165),
        ("Re-issued 5 % targets", 213, 217),
    ],
    430648: [],
    430651: [
        ("strategy(): 10 % of equity, commission", 175, 175),
    ],
    430658: [
        ("Stop % input", 168, 168),
        ("Shared-id stop exits", 190, 194),
    ],
    430662: [],
    430664: [
        ("strategy(): cash order, capital, commission", 184, 184),
        ("Fixed-ratio inputs", 204, 205),
        ("Fixed-ratio order sizing", 221, 245),
        ("Entry quantities", 264, 270),
    ],
    430667: [
        ("strategy(): 100 % of equity, commission", 200, 200),
    ],
    430669: [],
    # ---- FMZ-C, batch C38 (2026-10-16)
    430671: [
        ("strategy(): 100 % of equity, pyramiding 1, commission", 121, 121),
        ("Trailing exits", 169, 175),
    ],
    430672: [],
    430674: [
        ("Commented-out strategy(): cash order, pyramiding 10000", 184, 184),
        ("Maximum EMA distance input (price units)", 188, 188),
    ],
    430678: [
        ("Commented-out strategy()", 171, 171),
        ("Risk-management inputs", 189, 196),
        ("Stop / target lines", 257, 273),
    ],
    430740: [],
    430743: [
        ("Commented-out strategy(): cash order, commission", 157, 157),
        ("Stops, entries and the band-target exits", 181, 191),
    ],
    430744: [
        ("Commented-out strategy(): order size, capital", 141, 141),
        ("Price-unit SL / TP and the exits", 274, 280),
    ],
    430748: [],
    430749: [
        ("strategy(): capital, commission, slippage", 224, 224),
        ("Spread cap and stop / trailing inputs", 233, 240),
        ("Augmented entry size, stop and exits", 339, 359),
    ],
    430753: [
        ("Commented-out strategy(): order size, capital", 196, 196),
    ],
    430757: [],
    430760: [
        ("Take-profit / stop inputs and the exits", 184, 214),
    ],
    430761: [
        ("strategy(): 10,000 cash per entry", 192, 192),
        ("Stop / target options (off)", 244, 252),
    ],
    # ---- FMZ-C, batch C39 (2026-10-16)
    430763: [],
    430766: [],
    430767: [
        ("Commented-out strategy(): 30 % of equity, commission, process_orders_on_close", 158, 158),
    ],
    430768: [],
    430771: [],
    430772: [],
    430775: [],
    430777: [
        ("Entries (qty 1) and the percentage exits", 321, 337),
    ],
    430834: [
        ("strategy(): 10 % of equity", 228, 228),
    ],
    430836: [
        ("Trailing stop price and exit", 227, 234),
    ],
    430840: [
        ("strategy(): 100 % of equity, capital, commission", 191, 198),
        ("Stop / target inputs", 219, 227),
        ("ATR stop levels", 243, 253),
        ("Shared-id exits", 408, 410),
    ],
    # ---- FMZ-C, batch C40 (2026-10-16)
    430842: [
        ("strategy(): 100 % of equity, pyramiding 0, commission", 164, 164),
        ("Stop option (price units, off)", 181, 183),
    ],
    430843: [
        ("Commented-out strategy(): 10 % of equity, cash commission", 185, 185),
    ],
    430844: [
        ("strategy(): 100 % of equity, pyramiding 0", 141, 141),
    ],
    430846: [
        ("strategy(): 50 % of equity, pyramiding 1000, commission", 180, 181),
        ("Take-profit input and the exit", 224, 226),
        ("Entry and the re-issued target", 295, 296),
    ],
    430849: [
        ("strategy(): 100 % of equity, pyramiding 1", 179, 179),
        ("TP / SL inputs", 214, 215),
        ("Tick targets, entries and exits", 445, 470),
    ],
    430850: [],
    430853: [
        ("strategy(): 100 % of equity, pyramiding 0", 174, 174),
        ("Capital % input", 179, 179),
        ("Lot formula", 203, 204),
    ],
    430855: [
        ("strategy(): capital, pyramiding 0, commission", 201, 201),
    ],
    430858: [
        ("strategy(): 100 % of equity, pyramiding 1, commission", 147, 147),
    ],
    430859: [
        ("strategy(): 100 % of equity, pyramiding 0, commission", 192, 192),
    ],
    430860: [],
    # ---- FMZ-C, batch C41 (2026-10-17)
    430867: [
        ("strategy(): 10 % of equity, commission", 157, 163),
    ],
    430868: [],
    430871: [],
    430872: [
        ("Stop / take-profit tick inputs", 133, 134),
    ],
    430874: [
        ("strategy(): 100 % of equity, pyramiding 3", 175, 175),
        ("Capital % input", 180, 180),
        ("Lot formula", 214, 214),
    ],
    430876: [
        ("strategy(): 100 % of equity, pyramiding 1, commission", 132, 132),
    ],
    430877: [
        ("buyAmount input", 133, 133),
        ("strategy.order of buyAmount units", 196, 196),
    ],
    430878: [
        ("strategy(): 30 % of equity, commission", 153, 153),
    ],
    430880: [
        ("strategy(): 100 % of equity", 179, 179),
        ("Stop loss / take profit % inputs", 243, 244),
    ],
    430881: [
        ("strategy(): 100 % of equity", 220, 220),
        ("Stop loss / take profit % inputs", 299, 300),
    ],
    430887: [],
    430893: [
        ("Commented-out strategy(): 5 % of equity, commission", 184, 184),
    ],
    430896: [],
    # ---- FMZ-C, batch C42 (2026-10-17)
    430897: [
        ("Stop loss % inputs", 157, 158),
    ],
    430898: [
        ("strategy(): 100 % of equity", 182, 182),
    ],
    430899: [],
    430901: [],
    430902: [],
    430903: [],
    430977: [
        ("Tick take-profit / stop / trail inputs", 259, 261),
    ],
    430984: [],
    430988: [
        ("Risk amount input", 182, 182),
        ("Contract formulas", 198, 199),
        ("Risk-based contracts at the signal", 219, 219),
        ("Entry with qty = contracts", 225, 225),
    ],
    430998: [
        ("Point take-profit / stop inputs", 165, 166),
    ],
    431000: [
        ("Commented-out strategy(): 60 units, cash commission", 172, 172),
        ("Risk per trade input", 183, 183),
    ],
    # ---- FMZ-C, batch C43 (2026-10-17)
    431003: [],
    431010: [
        ("strategy(): 100 % of equity, commission", 147, 147),
    ],
    431210: [],
    431217: [
        ("strategy(): 30 % of equity, pyramiding 3", 196, 202),
    ],
    431221: [
        ("strategy(): 10 % of equity, pyramiding 5, commission", 158, 158),
    ],
    431223: [],
    431224: [
        ("strategy(): 15 % of equity", 173, 173),
    ],
    431226: [],
    431233: [],
    431235: [],
    431249: [
        ("strategy(): 100 % of equity", 227, 227),
    ],
    431250: [
        ("strategy(): 100 % of equity", 138, 138),
    ],
    # ---- FMZ-C, batch C44 (2026-10-17)
    431263: [
        ("MM block: capital / close lots", 233, 238),
    ],
    431264: [],
    431267: [],
    431272: [],
    431274: [
        ("Risk inputs", 157, 158),
        ("maxRiskValue", 163, 163),
    ],
    431278: [
        ("Account risk % input", 286, 286),
        ("Risk-based quantities", 423, 425),
    ],
    431280: [],
    431282: [
        ("Money management: risk lots and the equity protector", 221, 238),
    ],
    431284: [
        ("qty = equity / close (long)", 206, 206),
        ("qty = equity / close (short)", 222, 222),
    ],
    431286: [
        ("strategy(): initial capital, commission", 134, 134),
        ("qty = equity / close", 183, 183),
    ],
    431287: [],
    431392: [
        ("strategy(): 15 % of equity", 130, 130),
    ],
    431394: [],
    # ---- FMZ-C, batch C45 (2026-10-17)
    431396: [
        ("strategy(): 100 % of equity", 212, 212),
    ],
    431400: [
        ("Lot size input", 158, 158),
    ],
    431401: [
        ("strategy(): 100 % of equity, pyramiding 10", 276, 276),
        ("Capital % input", 282, 282),
        ("Lot formula (martingale multiplier)", 343, 345),
    ],
    431404: [],
    431407: [],
    431408: [],
    431409: [
        ("strategy(): 50 % of equity, commission", 201, 201),
    ],
    431410: [
        ("strategy(): 5 % of equity, pyramiding 1", 187, 187),
    ],
    431411: [],
    431413: [
        ("strategy(): 100 % of equity", 166, 166),
    ],
    431415: [
        ("Leverage input", 279, 279),
    ],
    431422: [
        ("Capital % input", 175, 175),
        ("Lot formula (martingale multiplier)", 229, 231),
    ],
    # ---- FMZ-C, batch C46 (2026-10-17)
    431426: [
        ("TP / SL pip inputs", 273, 274),
    ],
    431431: [],
    431494: [
        ("strategy(): 100 % of equity, commission", 155, 155),
    ],
    431498: [
        ("strategy(): 10000 cash per order", 199, 199),
    ],
    431502: [
        ("Capital % input", 216, 216),
        ("Lot formula", 258, 258),
    ],
    431662: [],
    431664: [],
    431666: [],
    431667: [
        ("strategy(): 100 % of equity, commission", 176, 184),
    ],
    431668: [
        ("Order size input (USDT)", 177, 177),
        ("Long entry qty", 253, 253),
        ("Short entry qty", 259, 259),
    ],
    431676: [],
    431678: [],
    431693: [
        ("Entries with qty 10", 261, 262),
    ],
    431885: [],
    # ---- FMZ-C, batch C47 (2026-10-17)
    431889: [],
    431891: [
        ("strategy(): 100 % of equity, pyramiding 5", 191, 191),
    ],
    431896: [
        ("Order size floor(capital / close)", 262, 263),
    ],
    431898: [],
    431901: [],
    431903: [],
    431911: [
        ("Lot input", 191, 191),
        ("Lot formula", 223, 225),
    ],
    431919: [
        ("strategy(): 3 % of equity, pyramiding 3", 212, 212),
    ],
    431923: [],
    431924: [
        ("strategy(): 100 % of equity, pyramiding 10", 155, 155),
        ("Capital % and martingale inputs", 160, 161),
        ("Lot formula (martingale multiplier)", 222, 224),
    ],
    431956: [],
    # ---- FMZ-C, batch C48 (2026-10-17)
    431960: [],
    431964: [],
    431966: [
        ("strategy(): 100 % of equity", 183, 183),
    ],
    431967: [],
    431971: [],
    431973: [
        ("strategy(): 100 % of equity", 145, 145),
    ],
    432076: [],
    432077: [],
    432092: [],
    432093: [
        ("Position sizing inputs", 141, 142),
        ("ATR risk quantity", 152, 154),
    ],
    432096: [
        ("strategy(): 100 % of equity", 182, 182),
    ],
    432099: [
        ("Entries with qty 1", 223, 227),
    ],
    432100: [],
    # ---- FMZ-C, batch C49 (2026-10-17)
    432110: [
        ("Long entry, target and close with qty 1", 205, 207),
        ("Short entry, target and close with qty 1", 213, 215),
    ],
    432111: [
        ("strategy(): 20 % of equity, pyramiding 1", 188, 188),
        ("Risk % and quantity stop inputs", 201, 202),
        ("Risk-based quantity", 261, 264),
        ("One-third partial cover", 276, 276),
    ],
    432112: [
        ("Risk input and size", 230, 231),
        ("Bracket orders (half-size first target, second target)", 234, 242),
    ],
    432114: [
        ("strategy(): margin settings", 219, 219),
    ],
    432117: [
        ("Exit orders (target, stop, trail)", 217, 218),
    ],
    432178: [
        ("strategy(): 100 % of equity", 126, 126),
        ("ATR bracket from the fill", 162, 172),
    ],
    432179: [],
    432180: [
        ("strategy(): pyramiding 4", 198, 198),
        ("Risk-based amount", 230, 237),
        ("Long entry and stop", 248, 251),
        ("Short entry and stop", 255, 258),
    ],
    432181: [
        ("strategy(): 100 % of equity, commission", 181, 181),
        ("Stop-loss inputs and levels", 243, 268),
        ("Stop orders", 278, 280),
    ],
    432182: [
        ("Entries with the tick bracket", 213, 219),
    ],
    432183: [
        ("strategy(): 100 % of equity, pyramiding 10", 184, 184),
        ("Martingale and capital % inputs", 189, 190),
        ("Lot formula (martingale multiplier)", 231, 233),
    ],
    432185: [
        ("strategy(): pyramiding 3", 210, 210),
        ("Risk-based amount", 250, 255),
        ("Long entry and stop", 268, 271),
        ("Short entry and stop", 275, 278),
    ],
    432207: [
        ("strategy(): 100 % of equity, commission", 192, 192),
    ],
    432210: [],
    # ---- FMZ-C, batch C50 (2026-10-17)
    432213: [],
    432215: [],
    432217: [
        ("strategy(): 1000 USD cash per trade", 187, 187),
        ("Percentage bracket from the fill", 356, 360),
    ],
    432219: [
        ("strategy(): 100 % of equity", 197, 197),
    ],
    432221: [],
    432225: [
        ("Close-checked 8 % stop", 259, 262),
    ],
    432228: [],
    432230: [
        ("strategy(): 100 % of equity", 174, 174),
        ("Short entry with qty 0 (needshort false)", 201, 202),
    ],
    432231: [],
    432232: [
        ("strategy(): 100 % of equity", 235, 235),
        ("Capital % input", 240, 240),
        ("Lot formula and entries with the lot", 264, 270),
    ],
    432234: [
        ("strategy(): 100 % of equity, slippage 5", 183, 183),
        ("Entries and exits (stop, trail)", 234, 240),
    ],
    432235: [
        ("Profit target and stop in ticks of the close", 206, 215),
    ],
    432237: [],
    # ---- FMZ-C, batch C51 (2026-10-17)
    432305: [],
    432309: [],
    432310: [],
    432315: [
        ("strategy(): fixed quantity 2, pyramiding 2", 177, 177),
    ],
    432330: [
        ("strategy(): fixed quantity, commission", 149, 149),
        ("Money management inputs", 198, 199),
        ("Fixed-ratio order amount", 232, 243),
        ("Long entry, stop and trail", 310, 317),
        ("Short entry, stop and trail", 329, 336),
    ],
    432332: [
        ("strategy(): margin settings", 136, 136),
        ("Long entry and stop", 161, 165),
    ],
    432333: [],
    432334: [
        ("strategy(): 100 % of equity, pyramiding 3, commission", 151, 151),
    ],
    432340: [
        ("strategy(): 100 % of equity", 244, 244),
        ("Entries with qty 0 against the trend", 293, 297),
    ],
    432342: [
        ("Entries with qty 10 and their exits", 262, 266),
    ],
    432346: [],
    # ---- FMZ-C, batch C52 (2026-10-17)
    432354: [
        ("strategy(): 100 % of equity", 201, 201),
    ],
    432356: [],
    432357: [
        ("strategy(): fixed quantity 5, commission", 197, 197),
    ],
    432358: [
        ("strategy(): 100 % of equity", 165, 165),
        ("Target / stop inputs (their exits are commented out)", 195, 202),
    ],
    432361: [
        ("Stop-loss input and order", 192, 204),
    ],
    432416: [
        ("strategy(): 100 % of equity, commission", 157, 157),
    ],
    432421: [
        ("strategy(): 10,000 USD cash per trade", 171, 171),
    ],
    432423: [],
    # ---- FMZ-C, batch C53 (2026-10-17)
    432657: [],
    432757: [],
    432759: [],
    432760: [],
    432763: [
        ("strategy(): 100 % of equity, commission", 123, 123),
    ],
    432766: [
        ("strategy(): 100 % of equity, commission", 114, 114),
        ("Direction setting (allow_entry_in)", 162, 163),
    ],
    432768: [
        ("strategy(): pyramiding 1, commission", 200, 200),
        ("Compounding and position size", 226, 229),
        ("Entries with the computed size", 242, 259),
        ("Long / short bracket orders", 267, 288),
    ],
    432775: [
        ("Bracket inputs and orders", 272, 294),
    ],
    432776: [
        ("Stop-loss inputs and orders", 203, 228),
    ],
    432778: [
        ("strategy(): 100 % of equity", 167, 168),
    ],
    432780: [
        ("Close-checked stop levels and closes", 164, 178),
    ],
    432782: [],
    # ---- FMZ-C, batch C54 (2026-10-17)
    432783: [],
    432784: [],
    432785: [
        ("Position size from equity and ATR", 310, 333),
    ],
    432786: [
        ("strategy(): 100 % of equity, pyramiding 10", 243, 243),
        ("Capital % input", 246, 246),
        ("Lot formula and entry with the lot", 280, 286),
    ],
    432788: [
        ("strategy(): pyramiding 1999, initial capital", 131, 131),
    ],
    432789: [
        ("ATR and fixed-percent exit orders", 200, 220),
    ],
    432797: [
        ("Stop / target inputs and orders re-placed every bar", 110, 113),
    ],
    432804: [
        ("Close-checked target and stop", 131, 141),
    ],
    432810: [],
    432811: [],
    432874: [
        ("Stop / target levels and their (unreachable) exit orders", 125, 156),
    ],
    432880: [
        ("strategy(): 100 % of equity", 113, 113),
    ],
    432883: [],
    # ---- FMZ-C, batch C55 (2026-10-17)
    432885: [],
    432886: [],
    432890: [
        ("strategy(): commission, slippage", 171, 174),
        ("Money management (risk-based lot)", 272, 285),
        ("Entries and tick exits", 289, 296),
    ],
    432896: [
        ("Entries with qty 1", 172, 177),
    ],
    432897: [],
    432898: [
        ("Stop-loss input and orders", 172, 208),
    ],
    432902: [],
    432908: [
        ("strategy(): 100 % of equity, commission", 138, 138),
        ("Stop-loss input and orders", 204, 219),
    ],
    432913: [
        ("Entries with qty 1 and their ATR tick exits", 172, 191),
    ],
    432914: [
        ("strategy(): 10 % of equity, commission", 149, 151),
    ],
    432920: [],
    432921: [],
    # ---- FMZ-C, batch C56 (2026-10-17)
    432923: [
        ("strategy(): 10000 SEK cash quantity", 124, 124),
    ],
    432965: [
        ("Risk management (money-management lot)", 211, 220),
        ("Entries with the lot and their ATR exits", 224, 233),
    ],
    432967: [],
    432969: [
        ("strategy(): fixed quantity 1", 131, 131),
    ],
    432970: [],
    432977: [],
    432979: [
        ("strategy(): 100 % of equity, commission", 134, 134),
        ("Stop / target inputs and exits", 194, 213),
    ],
    432989: [
        ("strategy(): 100 % of equity, commission", 96, 96),
    ],
    433002: [],
    433008: [
        ("strategy(): 100 % of equity, commission", 133, 133),
    ],
    433009: [],
    # ---- FMZ-C, batch C57 (2026-10-17)
    433010: [
        ("Money stop / target converted by position size", 152, 157),
    ],
    433011: [],
    433012: [],
    433013: [
        ("strategy(): commission", 124, 124),
    ],
    433017: [],
    433020: [
        ("strategy(): 100 % of equity, commission", 135, 135),
    ],
    433021: [],
    433022: [
        ("ATR bracket from the average entry price", 152, 172),
    ],
    433024: [
        ("Exit percentages, trail and bracket", 314, 341),
    ],
    433025: [
        ("strategy(): 100 % of equity", 175, 175),
    ],
    433029: [
        ("strategy(): 100 % of equity, commission", 145, 155),
    ],
    # ---- FMZ-C, batch C58 (2026-10-17)
    433068: [
        ("strategy(): 100 % of equity", 157, 157),
    ],
    433069: [],
    433075: [],
    433079: [],
    433094: [],
    433097: [],
    433101: [
        ("strategy(): 100 % of equity, commission", 178, 178),
    ],
    433104: [],
    433113: [
        ("Risk-based lot", 252, 269),
        ("Entries with qty 1 and their tick exits", 278, 282),
    ],
    433117: [
        ("Capital and reinvestment bookkeeping", 189, 215),
    ],
    433122: [
        ("strategy(): 20 % of equity, commission", 185, 193),
        ("Profit / loss parameters and exits", 211, 334),
    ],
    433123: [
        ("Stop / target inputs and exits", 166, 177),
    ],
    # ---- FMZ-C, batch C59 (2026-10-17)
    433124: [],
    433126: [
        ("Alert account / ticker / quantity and the tick bracket", 138, 156),
    ],
    433128: [
        ("Tick brackets per side", 160, 185),
    ],
    433137: [
        ("Open-profit close-outs ($)", 136, 169),
    ],
    433138: [],
    433148: [
        ("strategy(): 95 % of equity", 147, 149),
        ("Stop / target inputs and exits", 163, 266),
    ],
    433394: [],
    433398: [],
    433401: [],
    433403: [
        ("strategy(): 100 % of equity", 139, 139),
    ],
    # ---- FMZ-C, batch C60 (2026-10-17)
    433424: [],
    433425: [],
    433426: [
        ("strategy(): 100 % of equity; percent stop / target inputs and exits", 154, 225),
    ],
    433430: [],
    433431: [
        ("Tick level lines and the tick bracket", 190, 263),
    ],
    433433: [
        ("initial_capital / close quantity", 145, 147),
    ],
    433434: [
        ("strategy(): 1000 cash quantity", 213, 213),
    ],
    433439: [
        ("ATR stop / target inputs and exits", 178, 256),
    ],
    433441: [
        ("Lot % of equity and the commission", 183, 187),
        ("Lot formula", 244, 251),
    ],
    433442: [
        ("strategy(): pyramiding 5; percent TP / SL inputs and exits", 174, 356),
    ],
    433447: [
        ("Take profit / stop loss and exits", 259, 277),
    ],
    433452: [
        ("Tick stop / target / trail inputs and exits", 171, 260),
    ],
    # ---- FMZ-C, batch C61 (2026-10-17)
    433456: [
        ("strategy(): cash quantity, pyramiding 10", 144, 144),
        ("Fund x leverage quantity", 215, 226),
    ],
    433540: [],
    433544: [],
    433545: [
        ("strategy(): 100000 cash quantity", 135, 135),
        ("Box-width target / stop and exits", 141, 216),
    ],
    433547: [
        ("strategy(): 10 % of equity", 184, 184),
        ("Stop / trail inputs and exits", 205, 264),
    ],
    433548: [
        ("Quantity 1 and the per-contract commission", 118, 118),
        ("Tick stop / limit inputs and exits", 124, 162),
    ],
    433559: [
        ("Lot %, pyramiding 20 and the lot formula", 112, 168),
    ],
    433560: [],
    433561: [
        ("strategy(): 100 % of equity, commission", 138, 138),
    ],
    433562: [
        ("Quantity 1 and the unused stop / target variables", 124, 133),
    ],
    # ---- FMZ-C, batch C62 (2026-10-17)
    433569: [],
    433572: [
        ("Tick stop ladder and exits", 149, 201),
    ],
    433574: [],
    433575: [],
    433579: [
        ("Point value / margin / commission constants", 175, 180),
    ],
    433583: [],
    433585: [
        ("strategy(): 100 % of equity", 131, 131),
    ],
    433589: [],
    433590: [
        ("strategy(): 100 % of equity", 123, 123),
    ],
    433901: [
        ("strategy(): 100 % of equity, pyramiding 5", 171, 171),
    ],
    # ---- FMZ-C, batch C63 (2026-10-17)
    433910: [
        ("strategy(): 100 % of equity", 189, 189),
    ],
    433911: [],
    433912: [],
    433914: [],
    433922: [
        ("Swing stop in ticks and its exits", 297, 327),
    ],
    433923: [],
    433936: [],
    433946: [
        ("Decimal-scaled ATR bracket", 250, 341),
    ],
    # ---- FMZ-C, batch C64 (2026-10-17)
    433948: [],
    433949: [],
    433950: [],
    433959: [
        ("Pip take profit / stop loss options", 128, 180),
    ],
    433960: [
        ("Martingale lot variables", 174, 184),
    ],
    433966: [
        ("Secondary percent stop", 152, 192),
    ],
    433968: [
        ("Capital % lot", 178, 236),
    ],
    433970: [],
    433971: [
        ("strategy(): 10000 cash quantity", 129, 129),
        ("Tick bracket on the stacked entries", 141, 147),
    ],
    434159: [],
    # ---- FMZ-C, batch C65 (2026-10-17)
    434165: [],
    434166: [],
    434167: [
        ("Equity-risk unit count and opposite-size exit orders", 161, 197),
    ],
    434175: [],
    434183: [],
    434187: [],
    434192: [],
    434194: [],
    434196: [],
    434285: [
        ("strategy(): 100 % of equity, commission", 138, 138),
        ("Close-sized exits", 185, 194),
    ],
    434288: [
        ("strategy(): 100 % of equity; SL / TP options", 214, 499),
    ],
    434289: [],
    # ---- FMZ-C, batch C66 (2026-10-17)
    434293: [],
    434294: [
        ("strategy(): initial capital, commission", 117, 117),
    ],
    434295: [
        ("strategy(): 300 % of equity", 130, 130),
    ],
    434299: [
        ("strategy(): 100 % of equity, capital, commission", 158, 169),
    ],
    434304: [],
    434305: [
        ("Order size computed, never passed", 165, 165),
    ],
    434325: [],
    434326: [],
    434330: [],
    434332: [
        ("Risk-percent unit count", 148, 151),
    ],
    434336: [],
    434344: [],
    434345: [],
    # ---- FMZ-C, batch C67 (2026-10-17)
    434428: [],
    434434: [
        ("TP / SL percent inputs (exits in ticks of the close)", 246, 249),
    ],
    434445: [],
    434446: [
        ("Fixed-quantity entries (10)", 269, 282),
    ],
    434458: [],
    434466: [
        ("Tick bracket from the average price", 172, 173),
    ],
    434467: [],
    434470: [],
    434473: [
        ("Percent bracket on the average price", 148, 149),
    ],
    434478: [
        ("strategy(): 100 % of equity, capital", 122, 122),
    ],
    434480: [],
    434482: [],
    434484: [],
    # ---- FMZ-C, batch C68 (2026-10-17)
    434486: [
        ("strategy(): fixed quantity 1, capital", 187, 187),
        ("Stop loss in ticks", 222, 228),
    ],
    434487: [],
    434523: [],
    434525: [],
    434527: [],
    434551: [
        ("TP / SL percent inputs", 153, 155),
    ],
    434552: [],
    434556: [],
    434558: [
        ("Close-sized exits", 169, 177),
    ],
    434562: [
        ("Long bracket percent inputs", 159, 165),
    ],
    # ---- FMZ-C, batch C69 (2026-10-17)
    434581: [
        ("Fixed quantity 1 entries; the tick-sized max loss", 238, 247),
    ],
    434585: [],
    434586: [],
    434593: [
        ("Quantity and stop-loss inputs (ticks)", 143, 144),
        ("Fixed-quantity entries and exits", 162, 170),
    ],
    434598: [
        ("Fixed quantity 1 entries", 185, 192),
    ],
    434602: [
        ("Close-sized exits in ticks", 208, 225),
    ],
    434608: [],
    434609: [],
    434610: [
        ("strategy(): 100 % of equity", 152, 153),
    ],
    434611: [],
    # ---- FMZ-C, batch C70 (2026-10-17)
    434674: [],
    434675: [
        ("Money-per-trade quantity and the monetary stop", 167, 199),
    ],
    434678: [],
    434682: [],
    434687: [
        ("Profit / loss inputs (unused)", 170, 171),
    ],
    434691: [],
    434695: [
        ("strategy(): margins", 149, 149),
    ],
    434699: [
        ("Exit-order inputs (off by default)", 197, 205),
    ],
    434701: [
        ("Fixed quantity 1 entries and closes", 143, 158),
    ],
    434704: [
        ("strategy(): 100 % of equity", 181, 181),
    ],
    434705: [
        ("Stop level in ticks", 158, 174),
    ],
    434706: [],
    # ---- FMZ-C, batch C71 (2026-10-17)
    434708: [],
    434710: [
        ("strategy(): 100 % of equity", 117, 117),
    ],
    434711: [],
    434712: [],
    434713: [
        ("strategy(): 100 % of equity, capital, commission", 182, 188),
    ],
    434715: [],
    434718: [],
    434957: [],
    434960: [],
    434966: [],
    434968: [],
    # ---- FMZ-C, batch C72 (2026-10-17)
    434970: [],
    434976: [],
    434979: [],
    434981: [],
    434983: [
        ("Stop-loss and minimum-profit constants", 167, 168),
    ],
    434984: [
        ("strategy(): 100 % of equity, capital", 144, 144),
    ],
    434989: [],
    434995: [
        ("strategy(): 100 % of equity, capital, commission", 155, 155),
    ],
    434997: [],
    434998: [
        ("strategy(): 100 % of equity, capital, commission", 174, 181),
    ],
    434999: [],
    435002: [
        ("Tick bracket inputs", 161, 171),
    ],
    # ---- FMZ-C, batch C73 (2026-10-17)
    435003: [],
    435010: [
        ("strategy(): 20 % of equity, pyramiding 1", 107, 107),
    ],
    435017: [
        ("strategy(): 2 % of equity; tick bracket", 181, 207),
    ],
    435019: [
        ("strategy(): 100 % of equity", 110, 110),
    ],
    435020: [],
    435084: [],
    435096: [
        ("strategy(): pyramiding 10, commission; equity-sized quantity", 135, 187),
    ],
    435100: [],
    435101: [
        ("Per-pair quantity 1 / (close x count)", 235, 235),
    ],
    435103: [],
    435104: [
        ("strategy(): 100 % of equity, capital", 154, 154),
    ],
    # ---- FMZ-C, batch C74 (2026-10-17)
    435105: [],
    435106: [
        ("Risk-based lot sizes; slippage", 155, 219),
    ],
    435123: [],
    435124: [
        ("Capital-based quantity, leverage, compounding", 122, 179),
    ],
    435126: [
        ("strategy(): 100 % of equity; lot and martingale", 138, 212),
    ],
    435132: [
        ("Trailing-stop inputs (ticks of the close)", 176, 246),
    ],
    435133: [
        ("strategy(): 100 % of equity, commission", 160, 160),
    ],
    435134: [
        ("Fixed-ratio cash orders, commission", 160, 230),
    ],
    435139: [
        ("strategy(): 99 % of equity, commission", 173, 181),
    ],
    435143: [],
    435146: [
        ("strategy(): 100 % of equity, commission", 148, 148),
    ],
    435147: [
        ("Fixed quantity 2, commission, slippage", 155, 262),
    ],
    # ---- FMZ-C, batch C75 (2026-10-18)
    435151: [],
    435152: [],
    435155: [],
    435157: [],
    435158: [],
    435160: [
        ("Capital-based order size; tick bracket", 204, 222),
    ],
    435165: [],
    435169: [
        ("Percent bracket inputs", 196, 210),
    ],
    435232: [],
    435233: [
        ("strategy(): percent of equity", 120, 120),
    ],
    435234: [],
    # ---- FMZ-C, batch C76 (2026-10-18)
    435245: [
        ("Fixed order quantity 1", 187, 188),
    ],
    435246: [],
    435248: [],
    435249: [
        ("Tick bracket inputs", 188, 189),
    ],
    435250: [],
    435251: [],
    435252: [
        ("Stop loss price input", 208, 209),
    ],
    435260: [
        ("Price-unit bracket inputs", 174, 175),
    ],
    435264: [],
    435265: [
        ("strategy(): percent of equity, pyramiding 2", 180, 180),
    ],
    435266: [
        ("Risk-based quantity", 247, 247),
    ],
    # ---- FMZ-C, batch C77 (2026-10-18)
    435268: [],
    435269: [],
    435271: [],
    435272: [
        ("strategy(): percent of equity; trade_amount", 193, 193),
        ("Trade amount from capital and leverage", 210, 224),
        ("Fixed SL / PT tick inputs (off)", 301, 303),
    ],
    435280: [
        ("Equity-based lot", 173, 175),
    ],
    435283: [],
    435284: [],
    435285: [],
    435286: [],
    435288: [],
    435291: [],
    # ---- FMZ-C, batch C78 (2026-10-18)
    435463: [],
    435464: [
        ("strategy(): margin inputs", 114, 114),
        ("Price-unit stop and target", 134, 137),
    ],
    435468: [],
    435469: [
        ("strategy(): percent of equity, commission, pyramiding", 165, 170),
    ],
    435477: [
        ("strategy(): initial capital", 107, 107),
    ],
    435484: [
        ("strategy(): percent of equity 30", 128, 128),
    ],
    435485: [],
    435488: [],
    435492: [],
    435495: [],
    # ---- FMZ-C, batch C79 (2026-10-18)
    435487: [
        ("strategy(): initial capital", 230, 230),
    ],
    435502: [
        ("strategy(): percent of equity, commission", 127, 127),
        ("Stop loss / take profit inputs", 201, 205),
    ],
    435503: [
        ("strategy(): percent of equity", 150, 150),
    ],
    435505: [],
    435506: [
        ("strategy(): initial capital", 157, 157),
        ("Profit / loss tick inputs", 163, 164),
    ],
    435507: [
        ("strategy(): initial capital, percent of equity, commission", 202, 208),
        ("Stop loss / take profit inputs", 236, 237),
    ],
    435514: [],
    435519: [],
    435520: [],
    435522: [],
    # ---- FMZ-C, batch C80 (2026-10-18)
    435698: [],
    435699: [],
    435701: [],
    435703: [],
    435704: [],
    435705: [],
    435707: [
        ("strategy(): percent of equity, capital", 138, 138),
    ],
    435709: [],
    435713: [],
    435714: [],
    435717: [
        ("strategy(): cash order size, capital", 160, 160),
    ],
    435720: [],
    # ---- FMZ-C, batch C81 (2026-10-18)
    435722: [
        ("Cash order size, capital", 186, 191),
    ],
    435723: [],
    435724: [],
    435763: [],
    435767: [],
    435771: [
        ("Percent stop and target inputs", 171, 172),
    ],
    435772: [
        ("Take profit, stop and trailing-stop inputs", 184, 187),
    ],
    435774: [],
    435775: [],
    435828: [],
    # ---- FMZ-C, batch C82 (2026-10-18)
    435832: [
        ("Equity-based order size", 224, 226),
    ],
    435835: [],
    435837: [],
    435848: [
        ("Cash order size, risk-sizing inputs and quantity", 179, 192),
        ("Quantity from risk", 293, 298),
    ],
    435852: [],
    435863: [],
    435867: [],
    435868: [],
    435869: [
        ("Cash size, leverage and risk inputs", 126, 131),
        ("Entry quantity", 159, 162),
    ],
    435871: [
        ("Equity-based lot", 283, 285),
    ],
    435881: [
        ("strategy(): percent of equity, commission", 150, 150),
    ],
    # ---- FMZ-C, batch C83 (2026-10-18)
    435884: [],
    435888: [],
    435893: [],
    435895: [
        ("strategy(): percent of equity", 103, 103),
    ],
    435897: [],
    435903: [],
    435945: [
        ("Profit and stop inputs", 121, 122),
    ],
    435948: [
        ("strategy(): fixed size, capital, commission", 158, 158),
    ],
    435951: [],
    435953: [
        ("strategy(): percent of equity", 87, 87),
    ],
    435955: [
        ("Entry quantity 1", 123, 124),
    ],
    435957: [
        ("Tick bracket", 134, 137),
    ],
    435959: [
        ("strategy(): percent of equity", 153, 153),
    ],
    435960: [],
    # ---- FMZ-C, batch C84 (2026-10-18)
    435961: [
        ("Initial capital input", 146, 146),
    ],
    435962: [
        ("strategy(): commission", 125, 125),
    ],
    435963: [
        ("strategy(): percent of equity, pyramiding; trailing inputs", 179, 199),
    ],
    435965: [],
    435969: [
        ("Stop loss in pips input", 171, 171),
    ],
    435974: [],
    435979: [
        ("Equity-based quantity", 154, 161),
    ],
    435980: [],
    435981: [
        ("strategy(): percent of equity, capital, commission", 159, 167),
    ],
    435982: [],
    435984: [],
    435986: [
        ("Risk, stop and target inputs", 110, 112),
    ],
    435987: [
        ("Take profit, stop and tick-size inputs", 240, 256),
    ],
    435992: [
        ("Take-profit tick input", 207, 209),
    ],
    # ---- FMZ-C, batch C85 (2026-10-18)
    435993: [],
    435995: [
        ("Trade size and pip inputs", 116, 123),
    ],
    436006: [],
    436008: [],
    436009: [],
    436092: [],
    436094: [],
    436098: [],
    436099: [],
    436100: [
        ("strategy(): percent of equity, slippage", 164, 164),
    ],
    436102: [
        ("Equity-based lot", 191, 191),
        ("Lot from equity", 280, 282),
    ],
    436103: [
        ("Risk limits and risk-capped quantity", 164, 165),
        ("Entry contracts from equity", 243, 247),
    ],
    436108: [
        ("Fixed-ratio money management and cash order", 159, 199),
    ],
    # ---- FMZ-C, batch C86 (2026-10-18)
    436110: [],
    436112: [
        ("Tick loss and profit amounts", 153, 158),
    ],
    436113: [],
    436114: [],
    436117: [
        ("Initial balance", 195, 195),
    ],
    436119: [
        ("Quantity and USD trail offset", 191, 195),
    ],
    436120: [
        ("strategy(): pyramiding", 129, 129),
    ],
    436123: [],
    436133: [
        ("strategy(): cash size and capital", 139, 139),
    ],
    436136: [
        ("Quantity and starting amount", 188, 194),
    ],
    436137: [
        ("Quantities and pyramiding multiplier", 109, 112),
        ("Entry quantities", 145, 148),
    ],
    436140: [],
    436143: [],
    436145: [
        ("Take profit, stop and trail inputs", 165, 168),
        ("Exit orders", 205, 206),
    ],
    # ---- FMZ-C, batch C87 (2026-10-18)
    436146: [],
    436148: [],
    436211: [],
    436213: [
        ("Pip adjuster and ATR bracket inputs", 223, 232),
    ],
    436214: [],
    436215: [],
    436216: [],
    436218: [
        ("strategy(): percent of equity, pyramiding", 121, 121),
    ],
    436219: [],
    436220: [],
    436222: [
        ("Purchase quantity", 126, 126),
    ],
    436224: [
        ("strategy(): capital, percent of equity, pyramiding", 155, 155),
    ],
    436226: [
        ("strategy(): percent of equity", 128, 128),
    ],
    436228: [],
    # ---- FMZ-C, batch C88 (2026-10-18)
    436232: [],
    436237: [
        ("strategy(): percent of equity; bracket inputs", 136, 157),
    ],
    436238: [
        ("strategy(): percent of equity; off bracket inputs", 131, 149),
    ],
    436241: [
        ("Tick take profit, stop and trail inputs", 174, 183),
    ],
    436242: [],
    436243: [
        ("strategy(): pyramiding", 155, 155),
    ],
    436246: [],
    436251: [],
    436252: [
        ("Capital, martingale and lot", 217, 220),
        ("Lot from equity", 294, 296),
    ],
    436254: [],
    436261: [],
    436476: [
        ("strategy(): percent of equity, pyramiding", 161, 161),
    ],
    436479: [
        ("Entry quantity 1", 413, 420),
    ],
    # ---- FMZ-C, batch C89 (2026-10-18)
    436480: [],
    436485: [],
    436489: [
        ("strategy(): percent of equity, pyramiding", 122, 122),
    ],
    436490: [
        ("strategy(): percent of equity; Capital % input", 167, 172),
        ("Lot from equity", 210, 210),
    ],
    # ---- FMZ-C, batch C90 (2026-10-18)
    436491: [
        ("strategy(): cash quantity, pyramiding 1", 137, 137),
    ],
    436493: [
        ("strategy(): percent of equity, pyramiding 1", 36, 36),
    ],
    436497: [
        ("strategy(): percent of equity, pyramiding 1, slippage", 124, 126),
    ],
    436499: [
        ("strategy(): percent of equity", 139, 139),
        ("Take profit, stop and trailing inputs (off by default)", 155, 162),
    ],
    436500: [
        ("strategy(): percent of equity 10", 156, 162),
        ("Stop loss percent input", 176, 176),
    ],
    436502: [],
    436511: [
        ("strategy(): percent of equity, pyramiding 1", 212, 212),
    ],
    436514: [
        ("strategy(): percent of equity, pyramiding 0", 145, 145),
    ],
    # ---- FMZ-C, batch C91 (2026-10-18)
    436516: [],
    436519: [
        ("Take profit, stop, trail inputs (ticks)", 171, 173),
        ("Order size from equity", 178, 178),
    ],
    436527: [],
    436533: [],
    436540: [
        ("strategy(): percent of equity, pyramiding 0", 141, 141),
    ],
    # ---- FMZ-C, batch C92 (2026-10-18)
    436543: [
        ("strategy(): percent of equity, pyramiding 1", 128, 128),
    ],
    436593: [
        ("strategy(): percent of equity 20", 181, 181),
        ("Stop loss inputs (off by default)", 220, 246),
    ],
    436595: [
        ("Entry quantity 1", 157, 157),
    ],
    436597: [
        ("Stop loss percentage input", 136, 136),
    ],
    436598: [],
    436599: [
        ("Take profit and stop loss pip inputs", 137, 138),
    ],
    # ---- FMZ-C, batch C93 (2026-10-18)
    436604: [
        ("Investment value and quantity", 183, 185),
    ],
    436614: [
        ("strategy(): fixed size 1", 118, 118),
        ("Take profit and stop loss tick inputs", 160, 166),
    ],
    436617: [],
    436619: [
        ("Gamble sizing and quantity formula", 169, 214),
        ("strategy(): percent of equity 50", 183, 183),
        ("Quantity from equity", 290, 290),
    ],
    436623: [],
    436634: [],
    # ---- FMZ-C, batch C94 (2026-10-18)
    436640: [],
    436644: [],
    436647: [],
    436650: [
        ("strategy(): percent of equity, pyramiding 100", 187, 187),
        ("Entry ids and sequel trades", 196, 196),
    ],
    436652: [
        ("strategy(): percent of equity, commission", 129, 129),
    ],
    # ---- FMZ-C, batch C95 (2026-10-21)
    436754: [
        ("Risk lot formula (unused; size 1) and the pip inputs", 197, 213),
    ],
    436755: [],
    436757: [
        ("strategy(): 100 % of equity, capital", 124, 124),
    ],
    436758: [
        ("Stop loss in ticks input", 126, 126),
        ("Trade size input", 139, 139),
    ],
    436763: [
        ("Percent-of-portfolio input (not used by the orders)", 146, 146),
    ],
    436764: [
        ("Take-profit tick formula (off by default)", 141, 143),
    ],
    436765: [
        ("strategy(): 100 % of equity, capital, commission", 112, 113),
    ],
    436767: [],
    436770: [],
    436772: [],
    # ---- FMZ-C, batch C96 (2026-10-21)
    436779: [
        ("strategy(): 100 % of equity, capital", 152, 158),
    ],
    436781: [],
    436783: [
        ("Fixed quantity 1 on the entries", 125, 131),
    ],
    436786: [],
    436787: [
        ("Position-size input (not used by the orders)", 141, 141),
    ],
    436788: [
        ("Quantity = round(equity / close)", 125, 126),
    ],
    436791: [],
    436793: [],
    436797: [],
    436860: [],
    436872: [],
    # ---- FMZ-C, batch C97 (2026-10-21)
    436876: [],
    436877: [
        ("strategy(): margins and pyramiding 10", 155, 155),
    ],
    436878: [],
    436900: [
        ("Take-profit, stop-loss and combined-exit tick inputs", 143, 149),
    ],
    436903: [],
    436904: [],
    436910: [],
    436984: [],
    436987: [],
    436988: [
        ("strategy(): percent of equity, pyramiding 1, commission", 115, 115),
        ("Leverage quantity", 135, 142),
    ],
    436992: [
        ("Take-profit / stop-loss pip inputs", 181, 182),
    ],
    436994: [],
    # ---- FMZ-C, batch C98 (2026-10-21)
    436908: [
        ("strategy(): capital, 90 % of equity, commission", 282, 282),
    ],
    436997: [],
    437004: [
        ("Percent bracket inputs (tp / sl)", 311, 312),
    ],
    437007: [
        ("strategy(): 100 % of equity, commission", 143, 143),
        ("Trailing-stop inputs", 150, 158),
        ("Trailing exits (trail_points / trail_offset)", 340, 354),
    ],
    437010: [
        ("strategy(): capital, 100 % of equity, commission", 135, 135),
    ],
    437018: [],
    437022: [
        ("strategy(): capital, cash quantity, commission", 117, 124),
    ],
    437025: [
        ("Capital % input", 115, 115),
        ("Equity-based lot", 143, 145),
    ],
    # ---- FMZ-C, batch C99 (2026-10-21)
    437029: [],
    437031: [],
    437035: [],
    437036: [
        ("Profit target / stop loss point inputs", 197, 198),
        ("Every-bar bracket exits", 213, 217),
    ],
    437037: [],
    437040: [
        ("strategy(): pyramiding 0, 100 % of equity, capital", 204, 210),
    ],
    437043: [
        ("strategy(): 100 % of equity; capital % input", 162, 167),
        ("Equity-based lot", 222, 222),
    ],
    437044: [
        ("Stop-loss points and trail inputs", 166, 170),
        ("Exit orders with stop and trail", 194, 208),
    ],
    437045: [
        ("strategy(): capital, pyramiding 2, 100 % of equity", 126, 126),
    ],
    437376: [
        ("SL / PT level inputs (off)", 177, 178),
    ],
    437377: [],
    # ---- FMZ-C, batch C100 (2026-10-21)
    437034: [],
    437378: [],
    437381: [
        ("Per-setup entry quantities (1 / 100)", 185, 213),
    ],
    437383: [],
    437390: [
        ("strategy(): 100 % of equity, commission", 156, 156),
        ("Trailing-stop inputs and exits", 163, 193),
    ],
    437399: [
        ("strategy(): 100 % of equity, pyramiding 20; lot % input", 186, 191),
        ("Equity-based lot", 231, 231),
    ],
    437400: [],
    437403: [],
    437488: [],
    437490: [],
    # ---- FMZ-C, batch C101 (2026-10-21)
    437494: [
        ("strategy(): capital, 100 % of equity, commission", 146, 146),
    ],
    437499: [],
    437501: [
        ("strategy(): commission, capital, 100 % of equity", 143, 143),
    ],
    437503: [],
    437505: [
        ("strategy(): 100 % of equity, capital, commission", 142, 149),
        ("Stop and take-profit inputs", 165, 172),
    ],
    437506: [],
    437508: [],
    437515: [],
    437527: [],
    437539: [],
    437540: [],
    # ---- FMZ-C, batch C102 (2026-10-21)
    437507: [
        ("strategy(): capital, 100 % of equity, slippage, commission", 221, 222),
        ("Long stop / take-profit inputs", 360, 401),
    ],
    437542: [],
    437543: [
        ("Take-profit tick input", 162, 162),
    ],
    437547: [
        ("Trailing-stop and stop-loss percent inputs", 178, 186),
    ],
    437548: [
        ("strategy(): 100 % of equity, pyramiding 0; martingale and capital inputs", 157, 164),
        ("Lot and martingale", 273, 275),
    ],
    437550: [],
    437552: [],
    437553: [],
    437558: [
        ("strategy(): 100 % of equity; lot input", 148, 153),
        ("Equity-based lot", 221, 222),
    ],
    437565: [
        ("Fixed quantity 1", 163, 163),
    ],
    # ---- FMZ-C, batch C103 (2026-10-21)
    437632: [],
    437640: [],
    437644: [],
    437645: [
        ("strategy(): 10 % of equity, pyramiding 0, commission", 140, 140),
        ("Stop / take-profit factor inputs", 154, 156),
    ],
    437649: [],
    437651: [],
    437656: [],
    437658: [],
    437659: [],
    437663: [
        ("strategy(): pyramiding 1, 100 % of equity, margins, capital", 130, 130),
    ],
    437665: [
        ("strategy(): pyramiding 4", 104, 104),
    ],
    437672: [
        ("Take-profit / stop-loss tick inputs", 156, 157),
    ],
    # ---- FMZ-C, batch C104 (2026-10-21)
    437673: [],
    437674: [
        ("Risk-based size (unused), fixed quantity 1 and the tick inputs", 157, 191),
    ],
    437675: [
        ("strategy(): pyramiding 1, 100 % of equity, commission", 124, 124),
    ],
    437682: [
        ("Take-profit / stop-loss / minimum-body pip inputs", 140, 142),
    ],
    437684: [
        ("strategy(): pyramiding 7, capital, 20 % of equity, commission", 126, 126),
        ("Pyramiding entries 2-7 and their exits", 173, 194),
    ],
    437685: [],
    437689: [],
    437693: [],
    437694: [],
    437740: [
        ("strategy(): commission", 98, 98),
    ],
    # ---- FMZ-C, batch C105 (2026-10-21)
    437742: [],
    437746: [],
    437747: [
        ("Trailing-stop inputs and exits", 131, 186),
    ],
    437748: [],
    437751: [
        ("strategy(): 100 % of equity, capital, commission", 158, 158),
        ("Percent bracket inputs (as ticks)", 189, 192),
    ],
    437753: [
        ("strategy(): 10 % of equity; intraday-loss input", 136, 142),
    ],
    437759: [
        ("strategy(): 100 % of equity; lot input", 133, 138),
        ("Equity-based lot", 182, 184),
    ],
    437761: [
        ("strategy(): 100 % of equity", 143, 143),
    ],
    437765: [
        ("Tick bracket exit", 151, 151),
    ],
    437769: [],
    437773: [
        ("strategy(): capital", 135, 135),
    ],
    437774: [
        ("strategy(): 100 % of equity; stop / profit inputs", 159, 166),
    ],
    # ---- FMZ-C, batch C106 (2026-10-21)
    437783: [
        ("strategy(): capital; capital / close quantity", 187, 188),
    ],
    437785: [
        ("strategy(): 100 % of equity", 142, 142),
    ],
    437786: [
        ("strategy(): capital, 100 % of equity, commission", 183, 183),
    ],
    437789: [
        ("strategy(): capital", 194, 194),
        ("Dollar cost per position; static bracket inputs and levels", 235, 247),
        ("Entry quantities", 276, 280),
    ],
    437792: [
        ("Capital / close quantity", 151, 155),
    ],
    437794: [],
    437795: [],
    437800: [
        ("Percent bracket inputs and levels", 158, 172),
    ],
    437801: [],
    437808: [
        ("Unused capital variable", 186, 186),
    ],
    437811: [
        ("Tick bracket exits", 127, 130),
    ],
    # ---- FMZ-C, batch C107 (2026-10-22)
    438004: [
        ("strategy(): 1 % of equity", 206, 206),
        ("Quantity input", 330, 330),
        ("Entry quantities", 346, 352),
        ("Percentage, swing / supertrend and ATR exit inputs", 357, 362),
    ],
    438006: [
        ("strategy(): 100 % of equity; capital input", 171, 176),
        ("Equity-based lot and entry quantities", 200, 206),
    ],
    438007: [
        ("strategy(): 100 % of equity, pyramiding 5; lot input", 138, 141),
        ("Equity-based lot and entry quantity", 178, 181),
    ],
    438009: [],
    438010: [],
    438011: [],
    438012: [
        ("strategy(): 100 % of equity, capital, commission", 166, 173),
    ],
    438019: [
        ("strategy(): capital, commission, 100 % of equity, pyramiding 10", 161, 161),
    ],
    438020: [
        ("strategy(): 100 % of equity", 144, 144),
    ],
    438021: [],
    # ---- FMZ-C, batch C108 (2026-10-22)
    438022: [],
    438024: [],
    438026: [
        ("strategy(): 100 % of equity, capital, commission", 153, 160),
    ],
    438032: [],
    438033: [],
    438034: [
        ("Percent bracket inputs and levels", 143, 147),
    ],
    438036: [
        ("strategy(): 100 % of equity", 151, 151),
    ],
    438046: [
        ("strategy(): margins, quantity 1, capital", 132, 132),
    ],
    438047: [],
    438048: [
        ("Stop input and tick bracket", 139, 158),
    ],
    438051: [],
    # ---- FMZ-C, batch C109 (2026-10-22)
    438052: [
        ("Capital assignment for the P/L table", 215, 218),
    ],
    438053: [],
    438054: [
        ("strategy(): 15 % of equity; stop / profit amounts", 87, 93),
    ],
    438058: [
        ("strategy(): 100 % of equity; stop percent input", 179, 185),
        ("Stop levels and entry quantities", 252, 263),
    ],
    438059: [
        ("Long / short stop and target inputs", 212, 219),
        ("Bracket levels", 354, 357),
    ],
    438063: [],
    438064: [
        ("Trailing exits (ticks of 2 % of the close)", 178, 179),
    ],
    438067: [],
    438068: [
        ("Trail percent input and stop levels", 135, 149),
    ],
    438334: [
        ("strategy(): capital; pip inputs", 125, 139),
    ],
    438450: [],
    438451: [
        ("Target / stop inputs and levels", 182, 189),
    ],
    # ---- FMZ-C, batch C110 (2026-10-22)
    438456: [
        ("strategy(): 100 % of equity; capital input", 164, 169),
        ("Equity-based lot and entry quantities", 190, 199),
    ],
    438457: [],
    438458: [
        ("strategy(): 100 % of equity, capital, commission", 137, 137),
        ("Entry quantities 1", 199, 204),
    ],
    438459: [
        ("Stop / reward inputs and levels", 134, 158),
    ],
    438460: [],
    438463: [],
    438465: [
        ("Fixed risk inputs and levels", 255, 266),
    ],
    438466: [
        ("Trailing inputs and exits", 164, 193),
    ],
    438467: [],
    438468: [],
    438470: [
        ("strategy(): capital, 30 % of equity, commission", 124, 124),
    ],
    438473: [],
    # ---- FMZ-C, batch C111 (2026-10-22)
    438482: [],
    438483: [],
    438485: [
        ("strategy(): capital, cash quantity, commission", 101, 102),
        ("Unused bracket levels", 129, 144),
    ],
    438487: [],
    438492: [
        ("ATR stop / target variables", 157, 159),
    ],
    438498: [],
    438499: [],
    438505: [
        ("Trailing exits (offset only)", 141, 149),
    ],
    438506: [
        ("strategy(): percent of equity; stop / profit amounts", 155, 159),
    ],
    438507: [],
    # ---- FMZ-C, batch C112 (2026-10-22)
    438769: [],
    438771: [
        ("strategy(): capital", 181, 181),
    ],
    438773: [],
    438774: [],
    438775: [],
    438777: [],
    438782: [
        ("Tick stop and trail inputs and exits", 135, 204),
    ],
    438783: [
        ("strategy(): capital, 100 % of equity", 122, 122),
    ],
    438785: [
        ("strategy(): 20 % of equity, capital, pyramiding 1; risk inputs", 141, 162),
        ("Risk-based quantity", 198, 204),
    ],
    438787: [],
    438792: [],
    438794: [
        ("strategy(): capital, 100 % of equity", 155, 159),
    ],
    # ---- FMZ-C, batch C113 (2026-10-22)
    438795: [],
    438798: [],
    438799: [],
    438800: [
        ("Trailing stop inputs and exits", 205, 275),
    ],
    438802: [],
    438805: [
        ("Risk inputs, risk-based quantity and tick bracket", 192, 480),
    ],
    438807: [],
    438810: [],
    438816: [
        ("strategy(): cash 10000, capital, commission 0", 171, 171),
    ],
    438820: [
        ("Capital and capital / close quantities", 255, 266),
    ],
    438826: [
        ("strategy(): capital, 100 % of equity, commission", 182, 183),
    ],
    438929: [
        ("Tick risk inputs and exits", 386, 407),
    ],
    # ---- FMZ-C, batch C114 (2026-10-22)
    438931: [
        ("Buy quantity input", 158, 158),
    ],
    438933: [
        ("strategy(): 100 % of equity", 181, 181),
    ],
    438938: [
        ("strategy(): 10 % of equity", 134, 134),
    ],
    438940: [
        ("strategy(): 100 % of equity, commission", 133, 133),
    ],
    438944: [
        ("strategy(): capital, 25 % of equity, commission, pyramiding 1; stop input", 143, 154),
        ("Stop in ticks of the average price", 208, 212),
    ],
    438946: [],
    438947: [
        ("Daily investment, pyramiding and quantity", 259, 276),
    ],
    438948: [
        ("strategy(): quantity 1", 222, 222),
    ],
    438950: [
        ("Risk inputs and position size", 177, 200),
        ("Late bracket", 203, 211),
    ],
    438951: [],
    438972: [],
    438975: [],
    # ---- FMZ-C, batch C115 (2026-10-22)
    438978: [
        ("strategy(): 5 % of equity; SL / PT inputs", 169, 189),
    ],
    439036: [],
    439039: [],
    439047: [
        ("strategy(): 100 % of equity, commission", 169, 169),
    ],
    439048: [],
    439049: [
        ("Stop / take inputs and order prices; capital / close quantity", 129, 145),
    ],
    439050: [
        ("Point bracket inputs and levels", 138, 152),
    ],
    439051: [],
    439052: [
        ("Risk-based position size", 204, 205),
    ],
    439053: [
        ("Tick gap and bracket inputs", 168, 178),
    ],
    439064: [],
    439067: [],
    # ---- FMZ-C, batch C116 (2026-10-22)
    439074: [
        ("Contract sizes and adds", 159, 187),
    ],
    439075: [],
    439077: [
        ("strategy(): quantity 15, commission", 157, 157),
    ],
    439079: [],
    439080: [
        ("strategy(): 10 % of equity", 125, 125),
    ],
    439082: [],
    439083: [],
    439084: [
        ("strategy(): 100 % of equity, pyramiding 1, commission", 169, 169),
    ],
    439087: [],
    439089: [
        ("Per-bar bracket and unused take-profit variants", 175, 186),
    ],
    439094: [
        ("strategy(): capital, commission, slippage; risk sizing", 200, 219),
        ("Position size", 316, 319),
    ],
    439098: [
        ("strategy(): capital", 137, 137),
    ],
    # ---- FMZ-C, batch C117 (2026-10-22)
    439101: [],
    439104: [],
    439106: [
        ("strategy(): capital", 165, 165),
    ],
    439111: [
        ("strategy(): pyramiding 1000, cash 1000, commission", 137, 149),
    ],
    439181: [
        ("Pyramiding clauses and add signals", 172, 184),
    ],
    439183: [
        ("Stop input and exit", 125, 165),
    ],
    439188: [],
    439190: [
        ("Profit target and commission inputs; bracket", 132, 157),
    ],
    439193: [],
    439200: [
        ("Position size and leverage", 163, 182),
    ],
    439201: [],
    # ---- FMZ-C, batch C118 (2026-10-22)
    439202: [
        ("strategy(): percent of equity 100", 151, 155),
    ],
    439204: [],
    439207: [
        ("Order size from capital / close; pip inputs", 169, 200),
    ],
    439223: [
        ("strategy(): percent of equity, commission; position management", 149, 161),
        ("Position management sizes", 298, 305),
    ],
    439226: [
        ("Entry size 1", 268, 271),
    ],
    439227: [],
    439231: [
        ("Leverage input and lot", 127, 151),
    ],
    439233: [],
    439237: [],
    439240: [],
    439241: [
        ("strategy(): capital, percent of equity 30, commission", 127, 127),
    ],
    439243: [
        ("strategy(): cash 1000, commission", 116, 119),
    ],
    # ---- FMZ-C, batch C119 (2026-10-22)
    439244: [
        ("Capital, commission and the risk input", 204, 209),
        ("Risk-based quantity", 364, 366),
    ],
    439246: [
        ("strategy(): percent of equity 100", 151, 151),
    ],
    439248: [],
    439260: [],
    439262: [],
    439266: [
        ("strategy(): capital, pyramiding 0", 130, 130),
    ],
    439268: [],
    439273: [
        ("strategy(): margins, pyramiding 4; capital, risk and ATR quantity", 163, 200),
    ],
    439338: [],
    439339: [],
    439348: [
        ("Entry size 1", 191, 191),
    ],
    # ---- FMZ-C, batch C120 (2026-10-22)
    439349: [],
    439350: [],
    439351: [],
    439353: [],
    439354: [],
    439362: [
        ("Investment per condition and the per-buy quantity", 128, 159),
    ],
    439372: [],
    # ---- FMZ-C, batch C121 (2026-10-22)
    439373: [
        ("strategy(): capital, percent of equity 100, commission, pyramiding 1", 120, 120),
    ],
    439378: [
        ("strategy(): percent of equity 100, commission", 139, 139),
    ],
    439594: [
        ("strategy(): capital, percent of equity 100, pyramiding 1", 194, 194),
    ],
    439599: [],
    439601: [
        ("Capital and the dollar cost per position", 183, 240),
    ],
    439603: [
        ("Position size per trade", 127, 154),
    ],
    439605: [],
    439608: [
        ("Entry size 1", 170, 170),
    ],
    439611: [],
    439613: [
        ("strategy(): capital, percent of equity 100", 183, 183),
    ],
    # ---- FMZ-C, batch C122 (2026-10-22)
    439614: [],
    439620: [],
    439621: [],
    439622: [],
    439624: [],
    439625: [],
    439639: [],
    439643: [],
    439649: [],
    439693: [
        ("Stop and target percent inputs", 166, 170),
    ],
    439695: [
        ("Take-profit and stop percent inputs", 236, 237),
    ],
    439696: [
        ("strategy(): capital, percent of equity 100, commission, pyramiding 1", 131, 131),
    ],
    # ---- FMZ-C, batch C123 (2026-10-22)
    439701: [],
    439704: [],
    439705: [],
    439708: [],
    439710: [],
    439715: [],
    439717: [],
    439722: [],
    439734: [],
    439735: [],
    439737: [],
    # ---- FMZ-C, batch C124 (2026-10-22)
    439738: [],
    439741: [],
    439742: [],
    439744: [],
    439747: [],
    439751: [
        ("Trade size input", 336, 348),
    ],
    439756: [],
    439760: [
        ("strategy(): cash quantity", 169, 169),
    ],
    439764: [],
    439823: [],
    # ---- FMZ-C, batch C125 (2026-10-22)
    439830: [
        ("Stop / target percent or pips inputs (0)", 195, 226),
    ],
    439833: [
        ("Leverage, volatility target and compounding inputs; share count", 150, 192),
    ],
    439835: [
        ("Take-profit and stop percent inputs", 171, 172),
    ],
    439836: [],
    439837: [
        ("strategy(): percent of equity 100, pyramiding 0; stop input", 175, 181),
    ],
    439838: [],
    439839: [],
    439843: [],
    439854: [],
    439855: [],
    439859: [],
    # ---- FMZ-C, batch C126 (2026-10-22)
    439860: [],
    439862: [],
    439863: [],
    439870: [],
    439871: [
        ("strategy(): margins", 156, 156),
    ],
    439872: [
        ("strategy(): percent of equity 0.01", 168, 168),
    ],
    439875: [],
    439876: [],
    439877: [],
    439878: [],
    # ---- FMZ-C, batch C127 (2026-10-22)
    439899: [
        ("strategy(): percent of equity 5", 179, 179),
    ],
    439901: [],
    439938: [],
    439949: [
        ("Take-profit, stop and trailing point inputs", 415, 425),
    ],
    439954: [
        ("strategy(): pyramiding 2, fixed 2, capital", 163, 163),
    ],
    439957: [
        ("Risk inputs and the unused position-size function", 170, 180),
    ],
    439960: [
        ("Leverage and lot", 163, 230),
    ],
    439962: [],
    439963: [
        ("Equity / close amount", 148, 148),
    ],
    439964: [
        ("Tick bracket inputs", 152, 155),
    ],
    # ---- FMZ-C, batch C128 (2026-10-22)
    439970: [
        ("strategy(): percent of equity 25, capital, commission", 113, 115),
    ],
    439972: [],
    439973: [],
    439977: [],
    439978: [],
    439979: [
        ("Stop and target percent inputs", 241, 242),
    ],
    439981: [
        ("Leverage and portfolio share; quantity", 186, 217),
    ],
    439984: [
        ("Take-profit and stop percent inputs", 303, 306),
    ],
    439985: [],
    439988: [
        ("Stop percent and point inputs", 175, 178),
    ],
    439989: [],
    # ---- FMZ-C, batch C129 (2026-10-22)
    439991: [],
    439993: [
        ("Entry size 1", 189, 190),
    ],
    439994: [
        ("strategy(): capital, percent of equity 10; stop factor", 128, 142),
    ],
    440005: [],
    440056: [],
    440057: [],
    440062: [],
    440065: [],
    440066: [],
    440073: [],
    440075: [
        ("Stop and target percent inputs", 359, 366),
    ],
    # ---- FMZ-C, batch C130 (2026-10-22)
    440076: [
        ("strategy(): percent of equity 100, capital; pip inputs", 217, 221),
    ],
    440078: [],
    440080: [],
    440081: [
        ("10 x equity / close quantity", 162, 162),
    ],
    440087: [
        ("Quantity 1 and percent inputs", 165, 166),
    ],
    440090: [],
    440094: [],
    440095: [],
    440096: [],
    440097: [],
    # ---- FMZ-C, batch C131 (2026-10-22)
    440100: [],
    440102: [],
    440103: [],
    440104: [
        ("strategy.initial_capital 50000; equity > 0 gate", 762, 765),
    ],
    440107: [],
    440110: [],
    440292: [],
    440299: [],
    440300: [],
    # ---- FMZ-C, batch C132 (2026-10-22)
    440302: [],
    440303: [],
    440309: [],
    440310: [],
    440312: [],
    440313: [],
    440314: [],
    440320: [],
    440337: [
        ("strategy(): cash 25000, capital 25000, commission 0.15 %, slippage 3", 185, 185),
    ],
    440345: [],
    # ---- FMZ-C, batch C133 (2026-10-22)
    440348: [],
    440361: [],
    440362: [
        ("strategy(): capital 100, commission 0.0000005 %, 100 % of equity", 119, 119),
    ],
    440364: [],
    440366: [],
    440367: [],
    440368: [],
    440369: [],
    440373: [],
    440424: [],
    # ---- FMZ-C, batch C134 (2026-10-22)
    440426: [],
    440428: [
        ("positionSize 1", 193, 193),
    ],
    440429: [],
    440437: [
        ("initial capital 100000; qty 1; trade_size inputs", 142, 160),
    ],
    440439: [],
    440441: [],
    440443: [],
    440444: [],
    440449: [
        ("strategy(): capital 1000, 20 % of equity, commission 0.1", 200, 207),
    ],
    440451: [
        ("strategy(): 100 % of equity", 142, 142),
    ],
    # ---- FMZ-C, batch C135 (2026-10-22)
    440454: [
        ("strategy(): capital 100000, 100 % of equity, commission 0.01 %", 134, 137),
    ],
    440456: [],
    440458: [],
    440460: [
        ("strategy(): capital, 2 contracts, commission 0.075 %", 189, 193),
    ],
    440465: [
        ("strategy(): capital 10000, 100 % of equity, commission 0.04 %", 211, 212),
    ],
    440467: [],
    440503: [],
    440504: [],
    440505: [],
    440507: [],
    440509: [],
    # ---- FMZ-C, batch C136 (2026-10-22)
    440510: [],
    440517: [],
    440536: [
        ("entry qty 10", 199, 204),
    ],
    440537: [],
    440540: [],
    440542: [
        ("risk 1 % input (unused)", 140, 140),
    ],
    440545: [],
    440548: [],
    440550: [],
    # ---- FMZ-C, batch C137 (2026-10-22)
    440551: [],
    440553: [],
    440557: [
        ("strategy(): capital, per-order commission, slippage; risk-sized qty", 160, 212),
    ],
    440558: [
        ("strategy(): commission 0.06 %, 100 % of equity, capital 1000", 156, 156),
    ],
    440559: [
        ("strategy(): 100 % of equity", 141, 141),
    ],
    440562: [],
    440563: [],
    440564: [
        ("strategy(): capital 1000", 224, 224),
    ],
    440677: [],
    440679: [],
    # ---- FMZ-C, batch C138 (2026-10-22)
    440680: [],
    440684: [],
    440685: [],
    440690: [
        ("strategy(): capital, per-order commission, slippage; qty 1; position sizing input", 151, 226),
    ],
    440695: [],
    440698: [
        ("strategy(): capital, per-order commission, slippage", 149, 149),
    ],
    440700: [],
    440701: [],
    # ---- FMZ-C, batch C139 (2026-10-22)
    440713: [
        ("strategy(): capital 100, commission 0.05, qty 5", 181, 181),
    ],
    440717: [],
    440720: [],
    440724: [],
    440728: [],
    440794: [],
    440797: [
        ("strategy(): capital 1000, fixed qty 0.5, slippage 25", 132, 132),
    ],
    # ---- FMZ-C, batch C140 (2026-10-22)
    440798: [
        ("strategy(): capital 10000, cash 10000", 243, 243),
    ],
    440799: [],
    440800: [],
    440806: [
        ("leverage input (scales the stop only)", 163, 163),
    ],
    440808: [],
    440809: [],
    440810: [],
    440817: [
        ("lot size 1", 163, 163),
    ],
    440829: [],
    440831: [],
    440832: [
        ("strategy(): capital 1000, 30 % of equity, commission 0.1 %", 118, 118),
    ],
    440833: [],
    # ---- FMZ-C, batch C141 (2026-10-22)
    440845: [],
    440847: [
        ("strategy(): 10 % of equity, capital 5000", 146, 146),
    ],
    440849: [],
    440851: [],
    440853: [],
    440862: [
        ("order size floor(initial capital / close)", 185, 186),
    ],
    440863: [],
    440864: [
        ("strategy(): capital, commission, slippage; capital-percentage order quantity", 319, 727),
    ],
    440866: [],
    440871: [],
    440878: [],
    # ---- FMZ-C, batch C142 (2026-10-22)
    440952: [
        ("strategy(): cash 10000, capital 10000, commission 0.03 %", 162, 162),
    ],
    440955: [],
    440957: [],
    440964: [],
    440965: [],
    440976: [],
    440977: [],
    440979: [],
    # ---- FMZ-C, batch C143 (2026-10-22)
    440980: [],
    440982: [],
    440983: [],
    440985: [],
    440986: [],
    440988: [],
    440990: [],
    440994: [],
    440995: [
        ("strategy(): 10 % of equity", 179, 179),
    ],
    440996: [
        ("strategy(): 100 % of equity, capital 1000, commission 0.1", 140, 140),
    ],
    # ---- FMZ-C, batch C144 (2026-10-22)
    440997: [],
    440998: [],
    440999: [
        ("strategy(): 100 % of equity, pyramiding 0", 131, 131),
    ],
    441002: [
        ("strategy(): capital 10000 USD", 132, 132),
    ],
    441003: [
        ("strategy.entry qty = 1 (long20)", 145, 145),
        ("strategy.entry qty = 1 (long60)", 154, 154),
    ],
    441010: [],
    441013: [],
    441042: [],
    441043: [
        ("strategy(): default_qty_value 1", 112, 112),
    ],
    441044: [],
    441048: [],
    # ---- FMZ-C, batch C145 (2026-10-22)
    441052: [],
    441055: [],
    441057: [],
    441058: [],
    441062: [],
    441067: [
        ("strategy(): 10 % of equity", 161, 161),
        ("strategy.entry qty = 1 % of capital 100000 / (2 atr(14))", 196, 196),
    ],
    441068: [],
    441073: [
        ("strategy(): 100 % of equity, capital 1000", 124, 124),
    ],
    441074: [],
    441076: [],
    # ---- FMZ-C, batch C146 (2026-10-22)
    441077: [],
    441078: [],
    441082: [],
    441083: [],
    441084: [],
    441092: [],
    441097: [],
    441100: [
        ("strategy(): 100 % of equity, capital 1000, commission 0.01 %", 192, 192),
    ],
    441102: [],
    441103: [],
    441132: [],
    # ---- FMZ-C, batch C147 (2026-10-22)
    441133: [],
    441137: [
        ("strategy(): default_qty_type cash", 106, 106),
        ("strategy.entry qty = 5 % of equity / close (x 2, x 4 for the refused adds)", 124, 135),
    ],
    441138: [],
    441141: [],
    441142: [
        ("strategy.entry qty = 1", 195, 195),
    ],
    441143: [],
    441144: [],
    441152: [
        ("strategy.entry qty = 1", 160, 160),
    ],
    441157: [],
    441158: [],
    441160: [],
    # ---- FMZ-C, batch C148 (2026-10-22)
    441163: [],
    441164: [],
    441178: [],
    441182: [],
    441185: [],
    441955: [],
    441958: [],
    441959: [],
    # ---- FMZ-C, batch C149 (2026-10-22)
    441961: [],
    441962: [
        ("strategy(): 100 % of equity, capital 10000, commission 0.04", 187, 194),
    ],
    441963: [
        ("strategy(): 80 % of equity, capital 1000", 140, 140),
    ],
    441965: [],
    441991: [],
    441997: [],
    442000: [
        ("strategy(): 100 % of equity, capital 5000", 158, 158),
    ],
    442004: [
        ("strategy.entry qty = equity / (close x count)", 153, 177),
    ],
    442006: [],
    442010: [],
    # ---- FMZ-C, batch C150 (2026-10-22)
    442013: [],
    442014: [],
    442077: [],
    442078: [
        ("strategy(): 100 % of equity, commission 0.1 %", 146, 146),
    ],
    442082: [
        ("strategy.entry qty = 1", 144, 144),
    ],
    442085: [],
    442090: [],
    442091: [],
    442097: [
        ("strategy(): capital 1000, cash quantity, commission 0.02 %", 256, 256),
        ("entryQty = 1 % of equity / sl %", 698, 705),
    ],
    # ---- FMZ-C, batch C151 (2026-10-22)
    442100: [],
    442108: [],
    442113: [],
    442116: [],
    442117: [],
    442118: [],
    442119: [
        ("strategy(): 100 % of equity, capital 1000", 115, 115),
    ],
    442120: [],
    442122: [
        ("strategy(): 100 % of equity, capital 100000, commission 0.1 %", 146, 146),
    ],
    # ---- FMZ-C, batch C152 (2026-10-22)
    442126: [
        ("strategy(): 100 % of equity", 145, 145),
    ],
    442127: [
        ("lots = risk x (capital + net profit) / SL points", 249, 251),
    ],
    442206: [],
    442207: [],
    442211: [],
    442214: [
        ("strategy(): 100 % of equity, capital 5000", 195, 195),
    ],
    442221: [],
    442225: [
        ("strategy(): capital 10000, commission 1", 106, 106),
    ],
    442228: [],
    442230: [],
    # ---- FMZ-C, batch C153 (2026-10-22)
    442233: [],
    442234: [],
    442236: [],
    442250: [],
    442254: [],
    442256: [],
    442257: [
        ("strategy(): 100 % of equity, pyramiding 1", 102, 102),
    ],
    442259: [],
    442264: [],
    442273: [],
    442275: [],
    # ---- FMZ-C, batch C154 (2026-10-22)
    442341: [],
    442342: [
        ("strategy(): 100 % of equity, capital 100, commission 0.15 %", 108, 108),
    ],
    442346: [],
    442347: [],
    442349: [],
    442361: [],
    442363: [],
    442365: [],
    442367: [],
    442368: [],
    442369: [],
    # ---- FMZ-C, batch C155 (2026-10-22)
    442372: [],
    442377: [],
    442381: [
        ("strategy.entry qty = auto-compounding size (equity / 10000 steps, max 25)", 151, 177),
    ],
    442383: [
        ("strategy(): 100 % of equity, capital 100, commission 0.25", 148, 148),
    ],
    442387: [],
    442388: [],
    442389: [],
    442397: [
        ("strategy.entry qty = Quantity (1)", 158, 158),
    ],
    442399: [],
    442401: [],
    # ---- FMZ-C, batch C156 (2026-10-22)
    442402: [
        ("strategy(): 100 % of equity, capital 100000, commission 0.1", 152, 152),
    ],
    442403: [
        ("strategy(): 100 % of equity, capital 100, commission 0.03", 132, 132),
    ],
    442410: [],
    442502: [],
    442506: [],
    442507: [],
    442508: [
        ("strategy(): 100 % of equity, capital 100000, commission 0.025", 179, 179),
    ],
    442509: [],
    442511: [],
    442512: [],
    442516: [
        ("strategy(): margin_long 100, margin_short 100", 133, 133),
    ],
    442517: [],
    # ---- FMZ-C, batch C157 (2026-10-22)
    442519: [],
    442520: [],
    442523: [
        ("strategy(): 100 % of equity", 145, 145),
    ],
    442526: [],
    442527: [
        ("strategy(): 100 % of equity, capital 1000, commission 0.03", 123, 123),
        ("strategy.entry qty = (equity - position_size x close) / close", 169, 169),
    ],
    442532: [],
    442536: [],
    442537: [
        ("strategy(): 100 % of equity, capital 1000000, commission 0.075, slippage 3", 167, 169),
    ],
    442538: [
        ("strategy(): 100 % of equity, capital 10000, commission 0.075", 156, 156),
    ],
    442539: [
        ("qty = floor(strategy.equity / close)", 183, 183),
    ],
    # ---- FMZ-C, batch C158 (2026-10-22)
    442540: [],
    442543: [],
    442551: [
        ("strategy(): 25 % of equity, capital 10000, commission 0.03", 141, 141),
    ],
    442553: [],
    442556: [],
    442558: [],
    442561: [],
    442567: [],
    442618: [
        ("strategy(): capital 10000, commission 0.05", 113, 117),
        ("QtyTrade = equity (InitialBalance + netprofit[1]) x (1 + MarginFactor) / close[1] or 3.5 contracts", 123, 129),
    ],
    # ---- FMZ-C, batch C159 (2026-10-22)
    442621: [
        ("strategy(): 100 % of equity", 178, 178),
    ],
    442623: [],
    442624: [
        ("strategy(): 100 % of equity, pyramiding 0", 130, 130),
    ],
    442625: [],
    442626: [],
    442628: [],
    442635: [
        ("strategy(): 10 % of equity, capital 1000", 129, 129),
    ],
    442637: [
        ("strategy(): 100 % of equity", 95, 95),
    ],
    442639: [],
    442641: [
        ("strategy(): 100 % of equity, capital 1000, commission 0", 157, 157),
    ],
    442643: [],
    442644: [
        ("lots = 1 (exit qty)", 137, 137),
    ],
    # ---- FMZ-C, batch C160 (2026-10-22)
    442646: [
        ("strategy(): 100 % of equity, capital 1000, commission 0.1", 163, 163),
    ],
    442648: [],
    442651: [
        ("strategy(): 99 % of equity, pyramiding 1", 146, 146),
    ],
    442652: [
        ("strategy(): margin_long / margin_short 100, capital 2000", 137, 137),
    ],
    442653: [],
    442656: [
        ("contractsQty = 5", 146, 146),
    ],
    442657: [],
    442809: [],
    442810: [],
    442812: [],
    442813: [],
    # ---- FMZ-C, batch C161 (2026-10-22)
    442814: [
        ("strategy(): cash 50000 per trade, capital 500000", 152, 152),
    ],
    442815: [],
    442817: [],
    442820: [
        ("strategy.entry qty = size (1)", 154, 155),
    ],
    442823: [],
    442834: [],
    442835: [],
    442837: [],
    # ---- FMZ-C, batch C162 (2026-10-22)
    442838: [],
    442839: [
        ("strategy.entry qty = 1", 191, 200),
    ],
    442842: [],
    442847: [],
    442861: [],
    442863: [],
    442864: [],
    442921: [],
    442923: [],
    442924: [],
    # ---- FMZ-C, batch C163 (2026-10-22)
    442927: [],
    442928: [],
    442929: [
        ("strategy(): 100 % of equity, capital 1000", 117, 117),
    ],
    442930: [
        ("strategy(): margin 100, qty 1, capital 100", 211, 211),
    ],
    442935: [],
    442936: [],
    442937: [],
    442939: [],
    442946: [],
    442947: [],
    442953: [
        ("positionSize = strategy.equity x 2 / close", 158, 159),
    ],
    # ---- FMZ-C, batch C164 (2026-10-22)
    442954: [
        ("strategy(): 100 % of equity, capital 100, commission 0.1", 181, 181),
    ],
    442955: [
        ("strategy(): qty 1, capital 25000, commission 3.02 per contract", 135, 135),
    ],
    442957: [],
    442959: [],
    442961: [],
    442964: [],
    442966: [
        ("strategy(): margin_long / margin_short 100", 144, 144),
    ],
    442967: [],
    442971: [
        ("strategy(): cash quantity, capital 1000, commission 0.01", 186, 186),
        ("risk-based quantity: equity x 3 % / stop percent", 409, 411),
    ],
    442973: [
        ("strategy(): 100 % of equity", 124, 124),
    ],
    442975: [],
    442979: [],
    # ---- FMZ-C, batch C165 (2026-10-22)
    443034: [],
    443035: [],
    443036: [],
    443038: [],
    443039: [],
    443041: [],
    443042: [
        ("strategy(): commission 0.04", 134, 134),
    ],
    443043: [],
    443092: [
        ("positionSize = strategy.equity x 2 / close", 141, 142),
    ],
    443093: [],
    443094: [],
    # ---- FMZ-C, batch C166 (2026-10-22)
    443096: [],
    443099: [],
    443104: [],
    443106: [
        ("strategy(): percent of equity", 123, 123),
    ],
    443108: [],
    443118: [],
    443119: [],
    443121: [],
    443123: [
        ("strategy(): 20 % of equity, commission 0.005 per contract", 111, 111),
    ],
    443124: [],
    443125: [
        ("strategy(): 100 % of equity", 157, 157),
    ],
    # ---- FMZ-C, batch C167 (2026-10-22)
    443133: [],
    443135: [],
    443136: [
        ("strategy(): 100 % of equity", 126, 126),
    ],
    443139: [
        ("strategy.entry qty = 1 (risk-based contracts unused)", 207, 207),
    ],
    443228: [],
    443229: [],
    443230: [],
    443231: [],
    443239: [
        ("strategy(): fixed qty 1, capital 20000", 117, 117),
    ],
    443241: [
        ("strategy(): 100 % of equity, commission 0.1", 144, 144),
    ],
    443243: [],
    # ---- FMZ-C, batch C168 (2026-10-22)
    443246: [],
    443247: [],
    443643: [],
    443682: [
        ("exchange.Buy amount = 95 % of the balance / price; Sell all stocks", 50, 53),
    ],
    443985: [],
    443988: [
        ("strategy(): 100 % of equity, capital 50000, commission 0.005 per contract", 135, 141),
    ],
    443992: [],
    443993: [],
    443997: [],
    444001: [],
    # ---- FMZ-C, batch C169 (2026-10-22)
    444003: [
        ("strategy.entry / close qty = 5", 127, 137),
    ],
    444004: [
        ("strategy(): 100 % of equity, capital 1000; short qty 0.001", 137, 166),
    ],
    444006: [],
    444007: [
        ("strategy(): fixed qty 1 (entries qty 2), capital 1000, commission 0.35 per contract", 122, 129),
    ],
    444009: [
        ("strategy(): 100 % of equity, capital 500, commission 0.08, pyramiding 2", 141, 141),
    ],
    444011: [],
    444013: [
        ("qty = (capital + netprofit) x 20 % / 10 / close, capped at 10000", 203, 206),
    ],
    444016: [],
    444018: [],
    444020: [],
    444025: [],
    # ---- FMZ-C, batch C170 (2026-10-22)
    444034: [],
    444040: [],
    444042: [],
    444336: [
        ("strategy(): 100 % of equity, capital 10000, pyramiding 1, slippage 2", 132, 132),
    ],
    444338: [],
    444341: [],
    444344: [
        ("Trailing stop percent and levels (0.20 of the close)", 127, 150),
    ],
    444350: [
        ("strategy(): 100 % of equity", 114, 114),
    ],
    444352: [
        ("strategy(): 100 % of equity", 134, 134),
    ],
    444363: [
        ("strategy(): margin_long 100, margin_short 100", 150, 150),
    ],
    # ---- FMZ-C, batch C171 (2026-10-22)
    444383: [],
    444387: [
        ("strategy(): margin_long 100, margin_short 100", 138, 138),
    ],
    444959: [
        ("strategy(): 100 % of equity; take profit / stop / trailing tick inputs", 146, 156),
    ],
    444963: [],
    444968: [],
    444971: [
        ("strategy(): 80 % of equity, capital 1000, pyramiding 0", 194, 194),
    ],
    444973: [],
    444975: [],
    444977: [],
    444985: [
        ("qty = 50000 / close; stop low[1], target close x 1.5", 113, 121),
    ],
    444988: [],
    # ---- FMZ-C, batch C172 (2026-10-22)
    445438: [],
    445449: [
        ("fixedAmount 1000; qty = 1000 / close", 140, 164),
    ],
    445451: [
        ("strategy(): margin_long 100, margin_short 100", 152, 152),
    ],
    445464: [],
    445467: [
        ("strategy(): 10 % of equity", 132, 132),
    ],
    445468: [],
    445784: [
        ("strategy(): 100 % of equity; initial stop 6 % of the close", 174, 197),
    ],
    445786: [
        ("strategy(): 100 % of equity, capital 100000; stop / take-profit percent of the average price", 131, 139),
    ],
    445788: [
        ("strategy(): capital 30000, commission 7.5 per order; loss 100 points", 151, 157),
    ],
    445802: [],
    445803: [
        ("strategy(): 100 % of equity, capital 100, commission 0.15", 141, 141),
    ],
    445804: [
        ("strategy(): 5 % of equity, capital 10000, commission 0.02 %", 142, 142),
    ],
    # ---- FMZ-C, batch C173 (2026-10-22)
    445814: [],
    445817: [
        ("Stop loss percent and risk / reward inputs", 152, 174),
    ],
    445819: [],
    445821: [],
    445823: [],
    445824: [],
    445825: [],
    445832: [
        ("Tick size, trailing stop and stop loss inputs", 198, 239),
    ],
    445833: [
        ("Take profit avg x stopLuse 1.04", 272, 361),
    ],
    445836: [
        ("qty = initial_capital / 10000 (initial_capital set to 50000)", 196, 222),
    ],
    445840: [],
    # ---- FMZ-C, batch C174 (2026-10-22)
    446232: [],
    446428: [],
    446433: [],
    446438: [
        ("strategy(): margin_long 100, margin_short 100", 100, 100),
    ],
    446440: [],
    446441: [
        ("Risk / reward, lookback, break-even and daily loss inputs", 179, 186),
    ],
    446444: [],
    446453: [],
    446456: [
        ("strategy(): 100 % of equity, margin_long 100", 97, 97),
    ],
    446457: [
        ("strategy(): 100 % of equity, capital 10000, margins 100 / 100", 117, 117),
    ],
    446458: [
        ("stopLossPercentage 1.5", 107, 123),
    ],
    446460: [
        ("position_size input 1 (qty)", 133, 162),
    ],
    # ---- FMZ-C, batch C175 (2026-10-22)
    446461: [
        ("strategy(): 100 % of equity, capital 10000, commission 0.1 %", 117, 117),
    ],
    446465: [
        ("strategy(): 100 % of equity, capital 100000, pyramiding 0", 115, 115),
    ],
    446468: [
        ("entry qty 15; stop 20 / target 150 points; margins 100 / 100", 96, 157),
    ],
    446522: [
        ("strategy(): 100 % of equity", 101, 101),
    ],
    446525: [
        ("qty = floor(equity x 1 % / stop distance); bracket ATR 14 x 1.5, risk : reward 1", 162, 194),
    ],
    446526: [
        ("qty = equity x 10 % x leverage / close; percent stops / targets", 196, 263),
    ],
    446537: [
        ("qty = 50000 x 2.5 % / stop distance", 174, 257),
    ],
    446541: [],
    446542: [],
    446546: [],
    # ---- FMZ-C, batch C176 (2026-10-22)
    446549: [
        ("strategy(): 70 % of equity, capital 1000", 107, 111),
    ],
    446552: [
        ("strategy(): margin_long 100, margin_short 100; ATR target / stop multipliers", 93, 167),
    ],
    446553: [],
    446554: [
        ("DCA quantities 50000 / close x 1.2 / 1.3 / 1.5 / 1.5", 116, 121),
    ],
    446555: [
        ("strategy(): 100 % of equity, capital 1000, commission 0.1 %, slippage 3", 98, 98),
    ],
    446556: [
        ("Take profit / stop loss percent inputs (drawn only); Bybit level", 122, 155),
    ],
    446558: [
        ("Take profit / stop loss percent of the average price", 127, 136),
    ],
    446560: [
        ("Stop / target percent of the average price", 140, 143),
    ],
    446561: [],
    446567: [
        ("Stop / target 300 ticks from each close", 158, 173),
    ],
    446752: [],
    # ---- FMZ-C, batch C177 (2026-10-22)
    446756: [],
    446757: [
        ("strategy(): 20 % of equity", 119, 119),
    ],
    446758: [
        ("qty = (100000 + cumulative profit) / close", 134, 160),
    ],
    446761: [
        ("riskPercent 0.005 stop, ATR target", 134, 157),
    ],
    446764: [
        ("ATR bracket re-sent every bar", 186, 193),
    ],
    446765: [],
    446782: [],
    446963: [
        ("stop 2 % / target 10 % of the current close", 136, 139),
    ],
    446984: [
        ("qty = equity x 1 % / (2 x ATR); ATR bracket multipliers", 120, 156),
    ],
    446986: [],
    446991: [],
    # ---- FMZ-C, batch C178 (2026-10-22)
    448061: [],
    448066: [],
    448070: [
        ("qty = 1; take profit high + 0.3", 126, 149),
    ],
    448076: [
        ("qty = initial capital / close x 10 % x leverage; percent stop / target", 115, 133),
    ],
    448771: [
        ("Stop loss 1.5 % of the current close", 118, 160),
    ],
    448772: [],
    448774: [
        ("risk 2 % (unused); ATR stop / target multipliers", 114, 123),
    ],
    448778: [],
    # ---- FMZ-C, batch C179 (2026-10-22)
    449446: [
        ("Take profit / stop loss percent inputs (exits commented out)", 107, 108),
    ],
    449506: [],
    449508: [
        ("strategy(): 1000 % of equity, margins 1/10 x 50, commission 0.05 %; trail / loss tick inputs", 110, 123),
    ],
    449510: [],
    449518: [],
    449519: [
        ("Targets avg x 1.6 / x 0.75", 128, 131),
    ],
    449520: [],
    # ---- FMZ-C, batch C180 (2026-10-22)
    449526: [
        ("qty = 5000 x 10 %; stop 2 % of the signal close", 169, 204),
    ],
    449552: [],
    449553: [],
    449698: [],
    449709: [],
    449710: [
        ("strategy(): 100 % of equity, pyramiding 0", 115, 115),
    ],
    449711: [
        ("strategy(): cash 10000, capital 10000, commission 0.1 %, slippage 1", 121, 122),
    ],
    449713: [],
    449714: [],
    449715: [],
    449724: [],
    449810: [],
    # ---- FMZ-C, batch C181 (2026-10-22)
    449811: [
        ("qty 1; margins 100 / 100; stop / target percent of the signal low", 112, 138),
    ],
    449812: [],
    449815: [
        ("strategy(): 100 % of equity, capital 100000; stop / target percent of the average price", 147, 158),
    ],
    449816: [
        ("Stop / target percent of the average price; trailing percent", 110, 133),
    ],
    449817: [],
    449818: [],
    449843: [
        ("strategy(): 10 % of equity", 97, 97),
    ],
    449844: [
        ("strategy(): 10 % of equity, capital 10000, commission 0.1 %, slippage 1", 127, 129),
    ],
    449846: [],
    449851: [
        ("Stop 100 / target 200 points", 117, 127),
    ],
    449941: [
        ("lot size 0.4", 118, 155),
    ],
    449942: [],
    # ---- FMZ-C, batch C182 (2026-10-22)
    449947: [],
    449948: [
        ("strategy(): 100 % of equity, commission 0.035 %", 109, 109),
    ],
    449949: [
        ("qty = 1000 / close; target 5 % of the entry close", 100, 138),
    ],
    449954: [
        ("qty = equity x leverage 3 / close", 131, 171),
    ],
    449955: [],
    449956: [
        ("strategy(): 10 % of equity; ATR stop / target multipliers", 100, 127),
    ],
    449957: [],
    449958: [
        ("qty 1; stop 2 % of the signal close", 123, 152),
    ],
    449961: [],
    449965: [],
    449967: [
        ("TP / SL fractions 0.01", 113, 116),
    ],
    449968: [],
    # ---- FMZ-C, batch C183 (2026-10-22)
    449969: [
        ("Profit target 150 ticks", 125, 137),
    ],
    449970: [],
    449971: [],
    450857: [],
    450860: [
        ("strategy(): 10 % of equity", 101, 101),
    ],
    450868: [
        ("Target 1.5 % / stop 1 % of the average price", 126, 170),
    ],
    451023: [],
    451026: [
        ("qty 1; margin inputs (unused)", 119, 153),
    ],
    451027: [
        ("strategy(): 100 % of equity", 92, 92),
    ],
    451029: [],
    # ---- FMZ-C, batch C184 (2026-10-22)
    451030: [],
    451032: [],
    451071: [
        ("strategy(): 10 % of equity, capital 1000; TP / SL percents scaled by leverage 10", 96, 135),
    ],
    451072: [
        ("Martingale quantity 0.01 doubled up to 3 times; capital 100", 102, 145),
    ],
    451074: [
        ("Stop gain / loss 100 ticks", 187, 192),
    ],
    451076: [],
    451387: [
        ("Bracket 2 % of the signal close", 114, 119),
    ],
    451389: [],
    451391: [
        ("Stop 1 % / target 2 % of the average price; risk per trade 2 %", 130, 157),
    ],
    451393: [],
    451395: [
        ("Stop 0.5 % / target 1 % close tests (on a never-entered id)", 105, 122),
    ],
    451396: [
        ("strategy(): margin_long 100, margin_short 100", 93, 93),
    ],
    # ---- FMZ-C, batch C185 (2026-10-22)
    451399: [],
    451401: [
        ("Risk 0.5 % of the initial capital per trade over the stop distance; RR 1.5", 192, 221),
    ],
    451413: [
        ("Stop 1 % / target 2 % of the average price (both ids)", 146, 153),
    ],
    451487: [],
    451488: [
        ("strategy(): 10 % of equity", 142, 142),
    ],
    451490: [
        ("strategy(): 10 % of equity, capital 10000, commission 0.1 %, slippage 1; TP 15 % / SL 10 % (off)", 91, 105),
    ],
    451492: [],
    451516: [
        ("Buy 0.99 x the balance at the last price; sell all stocks", 56, 61),
    ],
    451526: [],
    451527: [
        ("SL 18 % / TP 18 % of the entry close (off by default)", 103, 106),
    ],
    # ---- FMZ-C, batch C186 (2026-10-22)
    451528: [],
    451698: [
        ("Risk 1 % of equity over the ATR as the quantity; stop / take-profit 'percentages' used as ATR multiples", 107, 144),
    ],
    451700: [],
    451702: [],
    451703: [
        ("Exit loss 5 / profit 10 ticks", 132, 136),
    ],
    451704: [
        ("strategy(): 80 % of equity, capital 10000, commission 0.01 %", 89, 89),
    ],
    451705: [],
    451706: [],
    451712: [
        ("strategy(): margin_long 100, margin_short 100", 90, 90),
    ],
    451713: [],
    451715: [
        ("Stop loss / take profit 500 ticks; trailing start 200 ticks, give-back 50 %", 97, 100),
    ],
    451723: [],
    # ---- FMZ-C, batch C187 (2026-10-22)
    451727: [],
    451729: [
        ("Buy quantity input 1 (unused by the orders)", 91, 91),
    ],
    451730: [],
    451733: [
        ("Stop loss 2 % of the signal close", 116, 138),
    ],
    452275: [],
    452280: [
        ("strategy(): initial capital 1000", 82, 82),
    ],
    452355: [],
    # ---- FMZ-C, batch C188 (2026-10-22)
    452359: [],
    452360: [
        ("Take profit 1 % of the signal close", 99, 134),
    ],
    452361: [
        ("Stop 0.90 x close / 0.85 x the highest close (bar-close tests)", 165, 196),
    ],
    452363: [],
    452364: [],
    452365: [],
    452615: [
        ("Quantity 1.0, or 0.5 / 0 by the SMA conditions", 147, 158),
    ],
    452685: [
        ("strategy(): 10 % of equity; risk-reward 3, stop buffer 0.01", 92, 120),
    ],
    452689: [],
    452691: [
        ("strategy(): margin_long 100, margin_short 100", 105, 105),
    ],
    452692: [
        ("strategy(): margin_long 100, margin_short 100; stop 16 %, targets 8 / 16 / 32 % of the fill", 98, 235),
    ],
    # ---- FMZ-C, batch C189 (2026-10-22)
    452699: [],
    452701: [],
    452712: [
        ("strategy(): margin_long 100, margin_short 100", 87, 87),
    ],
    452713: [],
    452714: [
        ("Stop 2 % of the signal close; minimum hold 10 bars (compared in milliseconds)", 106, 136),
    ],
    452716: [
        ("Stop 2 ATR beyond the line (on never-entered ids)", 96, 136),
    ],
    452736: [
        ("Targets high x 1.0012 / low x 0.994; stops max(low3 x 0.997, avg x 0.995) / min(high3 x 1.003, avg x 1.005)", 118, 151),
    ],
    452739: [],
    452741: [],
    452742: [],
    452743: [],
    # ---- FMZ-C, batch C190 (2026-10-22)
    452819: [
        ("Stop 0.5 % / target 1 % of the signal close; risk 1 % of equity over the stop distance", 135, 159),
    ],
    452820: [
        ("Target 8 % / stop 2.5 % of the average price", 126, 156),
    ],
    452821: [
        ("Quantity 1; take profit close + 6 (stop close - 2 in the alert only)", 103, 118),
    ],
    452822: [
        ("Take profit 5 % / stop 2 % of the current close, re-sent every bar", 86, 139),
    ],
    452824: [
        ("Stop 2 % of the signal close", 103, 128),
    ],
    452827: [
        ("Stop close - 1.5 ATR / target close + 3 ATR; risk 1 % (unused)", 85, 114),
    ],
    452829: [
        ("strategy(): 30 % of equity, capital 10000, margin 10, commission 0.1 %; trail 3 ATR 5", 95, 175),
    ],
    452830: [],
    453212: [
        ("Quantity floor(equity x 100 % / close)", 118, 215),
    ],
    453223: [
        ("strategy(): 10 % of equity", 122, 122),
    ],
    # ---- FMZ-C, batch C191 (2026-10-22)
    453232: [],
    453234: [
        ("strategy(): initial capital 25000", 101, 101),
    ],
    453235: [
        ("Stop 50 / target 200 points from the average price", 104, 156),
    ],
    453237: [],
    453238: [
        ("strategy(): margin_long 100, margin_short 100; stop ATR + body, target 1.2 x", 98, 166),
    ],
    453242: [
        ("strategy(): 10 % of equity, capital 10000, commission 0.1 %, slippage 1; TP 30 % / SL 20 % (off)", 76, 101),
    ],
    453244: [],
    453246: [
        ("Stop 1 % beyond the 10-bar close extreme, re-sent every bar", 100, 126),
    ],
    453264: [
        ("Quantity 1; stop 11 % under close[1] (low test)", 93, 116),
    ],
    # ---- FMZ-C, batch C192 (2026-10-22)
    453267: [
        ("Target 1000 points; stop at the trigger bar's high / low", 92, 175),
    ],
    453271: [],
    453273: [
        ("Quantity 1; capital 100000 / risk 1 % (label only)", 94, 119),
    ],
    453276: [],
    453287: [
        ("strategy(): 100 % of equity, capital 10000, commission 0.01 %", 98, 98),
    ],
    453645: [],
    453646: [
        ("strategy(): fixed quantity 1, capital 1000, commission 0", 88, 88),
    ],
    453647: [],
    453648: [],
    453650: [
        ("strategy(): 10 % of equity, capital 100000, commission 0.1 %; stop 5 % / target 20 % (close tests)", 104, 149),
    ],
    # ---- FMZ-C, batch C193 (2026-10-22)
    453277: [],
    453653: [],
    453655: [],
    453656: [
        ("strategy(): margin_long 100, margin_short 100; quantity balance / close (balance 1000)", 100, 138),
    ],
    453657: [
        ("strategy(): 10 % of equity", 84, 84),
    ],
    453661: [
        ("TP / SL 60 ticks", 102, 151),
    ],
    453665: [
        ("strategy(): margin_long 100, margin_short 100", 101, 101),
    ],
    453668: [
        ("strategy(): 100 % of equity; stop 1 % beyond the bar's extreme, target 3 %", 109, 162),
    ],
    454137: [
        ("Quantity riskMultiplier / lowest close x 1000 x equity / capital; capital 1000, commission 0.01 %, slippage 3", 91, 127),
    ],
    454141: [],
    # ---- FMZ-C, batch C194 (2026-10-22)
    454143: [
        ("Stop 0.7 % / target 0.5 % of the average price", 100, 136),
    ],
    454144: [
        ("strategy(): capital 20, commission 0.1 %; order size 20 USDT; stop 1 %; max duration 24 h", 98, 160),
    ],
    454145: [
        ("Lot 1; stop close -+ 1.00, target close +- 16", 119, 127),
    ],
    454146: [
        ("Stop 2 ATR / target 4 ATR from the signal close", 142, 154),
    ],
    454147: [
        ("TP / SL 10 pips x mintick", 115, 165),
    ],
    454150: [
        ("Quantity 1 % of a 100 balance over the bar range, x 1.1 / 0.9 by net profit", 100, 138),
    ],
    454151: [],
    454334: [
        ("Quantity 1; stop / target 2 ATR; risk 0.01 % (unused)", 108, 137),
    ],
    454339: [],
    454341: [],
    454351: [
        ("Stop 2 % / target 5 % of the signal close (close tests)", 92, 122),
    ],
    454352: [
        ("Stop 1 ATR / target 2 ATR beyond the bar's low / high, every bar", 118, 141),
    ],
    # ---- FMZ-C, batch C195 (2026-10-22)
    454362: [],
    454364: [],
    454366: [],
    454368: [],
    454369: [
        ("Stop at the averaged 78.6 % level, target 2R from the average price (every bar)", 114, 152),
    ],
    454371: [],
    454727: [
        ("Stop 1 % of the signal close", 163, 186),
    ],
    454728: [
        ("Take profit 5 % / stop 3 % of the signal close (close tests)", 126, 167),
    ],
    454730: [],
    # ---- FMZ-C, batch C196 (2026-10-22)
    454731: [
        ("Stop 3 % / target 6 % of the average price", 205, 229),
    ],
    454732: [],
    454733: [],
    454735: [],
    454737: [],
    454738: [],
    454740: [],
    454741: [],
    454742: [],
    454743: [],
    454746: [],
    # ---- FMZ-C, batch C197 (2026-10-22)
    454761: [],
    454762: [],
    454765: [],
    454767: [
        ("Stop / target 1.5 ATR 5 from the signal close", 184, 212),
    ],
    455353: [],
    455354: [
        ("SL / TP 11 / 33 pips x 0.1 from the average price (repeat signals only)", 211, 268),
    ],
    455357: [],
    455358: [
        ("Quantity 1; inventory limit 100", 158, 179),
    ],
    455359: [],
    455361: [],
    455364: [
        ("Stop 1 ATR / target 2 ATR from the current close (every bar)", 170, 181),
    ],
    # ---- FMZ-C, batch C198 (2026-10-22)
    455366: [],
    457776: [
        ("Stop 5.5 x ATR[1] from the signal close", 278, 330),
    ],
    457777: [
        ("strategy(): 10 % of equity; target 1 x body, stop 100 ticks", 181, 216),
    ],
    457792: [],
    457796: [],
    457811: [
        ("Exit band 0.2 % of the signal close", 164, 243),
    ],
    458023: [
        ("Max loss 20 % from the signal bar's low (close test)", 160, 180),
    ],
    458026: [
        ("Quantity 1, +1 when the open profit reaches 150 % of the last mark; capital 24000; stop 20 / target 50 points (every bar)", 161, 200),
    ],
    458027: [
        ("Target 100 / stop 50 points from the average price", 180, 208),
    ],
    458031: [],
    # ---- FMZ-C, batch C199 (2026-10-22)
    458033: [
        ("Target 0.08955 % / stop 0.04477 % of the average price", 157, 195),
    ],
    458034: [
        ("Stop / target 2 ATR from the signal bar's low", 174, 209),
    ],
    458036: [],
    458040: [
        ("Stop 1.5 ATR, target 5R from the average price (signal bars only)", 163, 193),
    ],
    458041: [
        ("strategy(): 100 % of equity", 230, 230),
    ],
    458043: [
        ("Quantity (capital + net profit) / close; trailing stop 2 stdev", 166, 197),
    ],
    458044: [
        ("strategy(): margin_long 100, margin_short 100", 249, 249),
    ],
    458047: [],
    # ---- FMZ-C, batch C200 (2026-10-22)
    458049: [
        ("Stop EMA 50 -+ 100 pips, target close +- 200 pips (x mintick)", 178, 223),
    ],
    458051: [
        ("Stop 90 / target 270 ticks from the signal close", 144, 171),
    ],
    458054: [
        ("Stop 2 % / target 5 % of the signal close", 253, 264),
    ],
    458056: [
        ("Exit band 0.2 % of the signal close", 183, 274),
    ],
    458057: [
        ("Trade size 2 lots; profit target 2000 USD", 201, 235),
    ],
    458058: [],
    458059: [
        ("Target 40 / stop 20 points from the average price", 260, 276),
    ],
    458061: [
        ("Target 1 % of the average price", 246, 251),
    ],
    458062: [],
    458063: [],
    458064: [
        ("Target 2 % / stop 0.5 % of the reference close (close tests)", 208, 258),
    ],
    # ---- FMZ-C, batch C201 (2026-10-22)
    458067: [
        ("Stop 0.1 % / target 0.1 % of the current close (re-sent every bar)", 241, 278),
    ],
    458069: [
        ("Target 1 % / stop 1 % of the signal close", 201, 222),
    ],
    458070: [],
    458071: [
        ("Target 20 % / stop 10 % of the average price", 230, 269),
    ],
    458074: [],
    458076: [
        ("Risk 2 % of equity (unused); fixed 1 contract; stop 10 / target 15 ticks", 177, 218),
    ],
    458077: [
        ("Stop 1 % / target 2 % of the signal close", 186, 221),
    ],
    458078: [
        ("Risk 3 % / 1.5 % of equity over the stop distance; stop 1 ATR under the signal close", 202, 300),
    ],
    458079: [],
    458128: [],
    458133: [],
    458134: [
        ("Risk 1 % of a 50000 capital over the ATR; stop 1.5 / target 3 ATR", 173, 226),
    ],
    # ---- FMZ-C, batch C202 (2026-10-22)
    458136: [],
    458137: [
        ("Gap threshold 150 / target 50 points (price units)", 308, 342),
    ],
    458140: [],
    458142: [],
    458144: [],
    458145: [
        ("Stop and target 2 ATR from the current close (re-sent every bar)", 187, 196),
    ],
    458146: [],
    458171: [
        ("Stop 2 % / target 4 % of the current close (re-sent every bar)", 235, 240),
    ],
    458174: [
        ("Stop 1 % / target 2 % of the current close (re-sent every bar)", 201, 208),
    ],
    458176: [],
    458178: [
        ("strategy(): order size 10 (cash)", 137, 137),
    ],
    # ---- FMZ-C, batch C203 (2026-10-22)
    458179: [
        ("Target 1 % / stop 0.5 % of the entry price (close tests); backtest dates", 181, 235),
    ],
    458182: [],
    458183: [],
    458184: [],
    458185: [],
    458192: [],
    458194: [],
    458197: [],
    458200: [
        ("Risk 1 % of equity over a 2 % stop; max 5 positions; stop 2 % of the average price", 210, 246),
    ],
    458201: [],
    458232: [],
    # ---- FMZ-C, batch C204 (2026-10-22)
    458233: [],
    458234: [
        ("strategy(): 10 % of equity, initial capital 10000", 161, 161),
    ],
    458237: [
        ("Profit 100 / loss 20 ticks; qty 1", 215, 231),
    ],
    458240: [],
    458242: [
        ("Trail 1 tick after 1 tick of profit", 229, 245),
    ],
    458247: [
        ("Target 2 % / stop 1 % of the average price", 162, 209),
    ],
    458249: [
        ("Target 1 % of the signal close; stop low[1] / high[1] (dynamic 1 % off)", 186, 241),
    ],
    458250: [
        ("Target / stop 1.5 % of the signal close (bar-close tests)", 183, 278),
    ],
    458252: [],
    458254: [
        ("Stop 1 % / target 2 % of the signal close", 192, 241),
    ],
    # ---- FMZ-C, batch C205 (2026-10-22)
    458255: [
        ("Target / stop 1.5 ATR from the signal close", 180, 208),
    ],
    458256: [
        ("Stop SMA 200 x 0.999 / 1.001; target close +- 7.5 (price units)", 163, 183),
    ],
    458264: [
        ("1 share per entry", 210, 350),
    ],
    458266: [
        ("Target 100 / stop 50 points from the average price", 224, 256),
    ],
    458268: [
        ("Stop: close under 98 % of the average price", 267, 289),
    ],
    458269: [],
    458270: [
        ("Target / stop = 20-bar high / low at the signal (close tests)", 215, 287),
    ],
    458271: [],
    458272: [],
    458273: [],
    458274: [
        ("strategy(): 100 % of equity; max position size 1; target / stop 1 %", 224, 253),
    ],
    # ---- FMZ-C, batch C206 (2026-10-22)
    458276: [
        ("Targets 100 / 150, stops 100 / 1500 / 150 (price units)", 178, 232),
    ],
    458277: [
        ("Stop 5 % / target 10 % (computed, never sent)", 203, 255),
    ],
    458278: [],
    458279: [],
    468299: [
        ("Stop / target 0.5 % of the signal close", 190, 230),
    ],
    468302: [
        ("Target 50 / stop 20 points from the current close (re-sent every bar)", 276, 277),
    ],
    468305: [
        ("Stop at the 5-bar swing, target 3 x the risk; trail_offset 0", 269, 299),
    ],
    468308: [],
    468309: [
        ("Stop 2 ATR from the average price; trailing stops (na)", 118, 172),
    ],
    468316: [
        ("Fixed quantities 1 / 2 / 3 / 4 (scale-in)", 121, 131),
    ],
    # ---- FMZ-C, batch C207 (2026-10-22)
    468319: [
        ("Stop 1.5 ATR / target 3 ATR from the average price", 121, 165),
    ],
    468320: [
        ("Slope threshold 0.5 (price units)", 129, 132),
    ],
    468322: [
        ("Target 3.5 % / stop 1.4 % (unused) of the signal close; add-on qty 3", 154, 195),
    ],
    468323: [
        ("Stop 2 ATR / target 3 ATR from the average price", 150, 154),
    ],
    468324: [
        ("Target 55 / stop 30 ticks; trail_offset 25 x mintick", 169, 217),
    ],
    468325: [
        ("strategy(): 100 % of equity; brackets 1.5 / 0.5 % and 0.5 / 0.2 % of the entry price", 157, 285),
    ],
    468328: [
        ("Stop SMA 90 of the signal bar; target 1.5 x the risk", 146, 216),
    ],
    468330: [],
    468331: [],
    468333: [
        ("Stop 1.25 / target 37.5 (price units); 2 contracts", 142, 185),
    ],
    468334: [
        ("Stop 1.5 ATR / target 2 ATR from the signal close", 115, 145),
    ],
    468335: [
        ("Risk 2.5 % of equity over a stop 1.5 % under the SMA 200 (size only)", 125, 139),
    ],
    # ---- FMZ-C, batch C208 (2026-10-22)
    468336: [
        ("Stops at the current outer band (re-sent every bar)", 160, 167),
    ],
    468338: [
        ("qty 1; stop ref / 70, target ref / 140; trailing exits 150 points away", 140, 198),
    ],
    468349: [],
    468350: [
        ("strategy(): 10 % of equity; target 50 / stop 20 pips", 128, 222),
    ],
    468351: [
        ("Target / stop 2 % of the current close (re-sent every bar)", 202, 212),
    ],
    468352: [],
    469615: [],
    469617: [],
    469618: [
        ("strategy(): margin 100 / 100; target 3 % / stop 1 % of the average price", 123, 171),
    ],
    # ---- FMZ-C, batch C209 (2026-10-22)
    469622: [
        ("Stop 1 ATR from the signal close", 140, 180),
    ],
    471659: [],
    471661: [
        ("strategy(): 10 % of equity, commission 0.02 %, slippage 1, capital 10000", 109, 109),
    ],
    471662: [],
    471671: [
        ("strategy(): pyramiding 3, capital 100000; trade size 1 ETH", 98, 165),
    ],
    471672: [],
    471686: [
        ("Stop 2 ATR / target 4 ATR from the current close (re-sent every bar)", 129, 181),
    ],
    471687: [
        ("Stop 10 ATR from the signal close", 108, 144),
    ],
    471688: [],
    471689: [
        ("Risk 2 % of equity over a 1 ATR stop; target 0.75 ATR", 133, 173),
    ],
    471690: [
        ("Target 2 % / stop 1 % of the current close (re-sent every bar)", 95, 133),
    ],
    # ---- FMZ-C, batch C210 (2026-10-22)
    471691: [
        ("Target one pattern range beyond the break; stop 1 % of the current close", 178, 209),
    ],
    471694: [
        ("Break-even stop at the close", 148, 166),
    ],
    471695: [],
    471696: [],
    471697: [
        ("Bracket from the average price x risk / reward 2", 113, 132),
    ],
    471698: [],
    471702: [],
    471703: [
        ("Stop 1 % of the average price (off)", 135, 163),
    ],
    471704: [
        ("10 contracts", 104, 131),
    ],
    471707: [
        ("Target 1.5 ATR x risk / reward 2 from the signal close", 104, 165),
    ],
    471709: [
        ("Target 2 % / stop 1 % of the average price", 111, 216),
    ],
    # ---- FMZ-C, batch C211 (2026-10-22)
    471713: [
        ("Target 5 % / stop 2 % of the average price; date window", 142, 165),
    ],
    471714: [
        ("Stop = 7-bar low; target 2 x the risk", 104, 116),
    ],
    471715: [],
    471719: [
        ("Stop 1.5 ATR / target 3 ATR from the signal close", 101, 168),
    ],
    471720: [],
    471725: [],
    471729: [
        ("Stop 2.5 % / target 4 % of the signal close (close tests)", 103, 125),
    ],
    472246: [
        ("Stop 1 % / target 2 % of the signal close; capital 10000", 94, 145),
    ],
    472248: [
        ("Stop 50 / target 100 ticks", 110, 144),
    ],
    # ---- FMZ-C, batch C212 (2026-10-22)
    472251: [
        ("Target 30 / stop 10 pips (pip = mintick x 10)", 92, 165),
    ],
    472252: [],
    472933: [
        ("Bracket from the average price x risk / reward 1.5", 98, 123),
    ],
    472934: [
        ("Target 1.5 % / stop 1 % of the signal close", 108, 121),
    ],
    472936: [
        ("Stop 2 % of the average price", 118, 132),
    ],
    472938: [
        ("Stop 1 ATR / ratcheting target 1.5 ATR", 116, 197),
    ],
    472939: [
        ("Target / stop / trail modes (off)", 114, 198),
    ],
    472951: [
        ("Trailing stop 1.5 ATR / target 2 ATR (sent on reversal bars)", 128, 182),
    ],
    472971: [],
    472973: [
        ("Target 30 % of the average price", 127, 156),
    ],
    472974: [],
    # ---- FMZ-C, batch C213 (2026-10-22)
    473121: [
        ("ATR 14 x 2 exit bands around the close", 127, 152),
    ],
    473122: [
        ("Risk 1 % of a 100000 balance over the swing stop distance; band target and swing stop", 105, 188),
    ],
    473123: [
        ("Trade size 5 ETH; target 9 % / stop 9.9 % of the average price", 88, 154),
    ],
    473124: [],
    473125: [
        ("Stop 2 ATR / target 3 ATR from the average price", 120, 122),
    ],
    473128: [],
    473131: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 3", 93, 93),
    ],
    473132: [],
    473134: [],
    473136: [],
    473140: [
        ("qty = equity / close", 125, 132),
    ],
    473141: [],
    # ---- FMZ-C, batch C214 (2026-10-22)
    473145: [
        ("Stop 7 / target 100 / trail 15 points from the current close", 111, 178),
    ],
    473147: [
        ("Stop 1.5 % / target 3 % of the average price", 108, 126),
    ],
    473148: [
        ("Stop = low - ATR; target = 10-bar high", 123, 145),
    ],
    473153: [
        ("DCA size 1 % of equity (unused); target 5 % of the current close", 140, 178),
    ],
    473154: [
        ("Trailing stop 1.5 ATR / target 2 ATR", 133, 151),
    ],
    473155: [
        ("Target 1.23 % of the average price; trail_offset 0.6 % (price in ticks)", 94, 117),
    ],
    473157: [
        ("qty 1 (MyQty unused)", 108, 118),
    ],
    473233: [],
    473234: [],
    473235: [
        ("strategy(): 20 % of equity, capital 30", 104, 104),
    ],
    473236: [
        ("Stop at the cloud edge of the signal bar", 154, 203),
    ],
    # ---- FMZ-C, batch C215 (2026-10-22)
    473238: [
        ("strategy(): 100 % of equity, capital 10000", 90, 90),
    ],
    473245: [],
    473246: [],
    473248: [
        ("Lot 1; stop 300 / target 600 ticks from the current close", 102, 131),
    ],
    473250: [
        ("Target 0.4 % / stop 2.5 % of the average price", 99, 125),
    ],
    473252: [
        ("Loss 100 / profit 200 ticks", 107, 138),
    ],
    473262: [
        ("Take-profit 1.5 % (computed, never sent)", 106, 131),
    ],
    473263: [
        ("strategy(): 10 % of equity, commission 0.1 %, slippage 1; partial TPs (off)", 96, 179),
    ],
    473265: [
        ("Stop 1.5 ATR / target 3.5 ATR from the signal close", 121, 133),
    ],
    473266: [],
    473268: [
        ("Stop low x 0.98 / limit high x 1.04 (re-sent every bar)", 134, 137),
    ],
    # ---- FMZ-C, batch C216 (2026-10-22)
    473269: [],
    473270: [
        ("Stop 0.5 % / target 1.5 % of the average price (na from flat)", 122, 126),
    ],
    473271: [
        ("strategy(): 100 % of equity", 89, 89),
    ],
    473272: [
        ("Target 10 % / stop 5 % of the average price (na from flat)", 164, 178),
    ],
    473318: [
        ("Limit 0.98 % from the current close (re-sent every bar)", 131, 159),
    ],
    473319: [
        ("strategy(): cash size, commission 0.03 %", 139, 139),
    ],
    473321: [
        ("Target 5 % of the average price / stop 1 % of the signal close", 91, 138),
    ],
    473324: [
        ("strategy(): percent of equity; stop 40 / target 80 ticks from the signal close", 87, 122),
    ],
    473344: [],
    473346: [
        ("Stop 2 % of the signal close; target = 50-bar high", 103, 152),
    ],
    473350: [
        ("strategy(): 100 % of equity, capital 100000; TP 7 % of the current close re-sent every bar", 93, 187),
    ],
    473351: [],
    # ---- FMZ-C, batch C217 (2026-10-22)
    473353: [
        ("Stop 1 % / target 2 % of the average price on the signal bar; trail_offset 1.5", 122, 149),
    ],
    473354: [
        ("strategy(): 100 % of equity, capital 1000", 105, 105),
    ],
    473356: [],
    473360: [
        ("Target close +/- 250 points; trail_offset 25", 124, 128),
    ],
    473361: [
        ("strategy(): fixed qty 1; qty = equity x 20 / close, doubled on repeat entries (pyramiding 1)", 96, 154),
    ],
    473364: [
        ("Stop 10 / target 15 x pointvalue from the signal close", 96, 148),
    ],
    473365: [
        ("Stop 1 % / target 2 % of the average price on the signal bar; trail_offset 1.5", 93, 121),
    ],
    473366: [
        ("Capital 100, risk 1 %, TP 2 %, SL 1 % (labels only); stop close x 0.99 after 5 % profit", 107, 142),
    ],
    473367: [
        ("Stop / target 1 % of the current close (every bar)", 103, 130),
    ],
    473371: [
        ("strategy(): 10 % of equity", 127, 127),
    ],
    473372: [
        ("Stop 100 / target 150 points (off); commission 0.05 per contract", 90, 126),
    ],
    # ---- FMZ-C, batch C218 (2026-10-22)
    473383: [],
    473385: [
        ("Stop 1 % beyond the signal bar's low / high; 1 % close ratchet", 114, 162),
    ],
    473386: [
        ("qty 1; commission 0.1 %, slippage 3", 87, 134),
    ],
    473387: [
        ("strategy(): 10 % of equity", 89, 89),
    ],
    473396: [
        ("strategy(): 100 % of equity; stop 5 % / target 10 % of avg", 87, 136),
    ],
    473397: [],
    473398: [],
    473399: [
        ("Stop 2 / target 6 in price from the signal close", 91, 126),
    ],
    473401: [
        ("Target 2 % / stop 1 % of avg", 91, 124),
    ],
    # ---- FMZ-C, batch C219 (2026-10-22)
    473402: [],
    473404: [],
    473405: [],
    473410: [
        ("strategy(): capital 2000, slippage 3; stop at the DSL band, target 1.5 R", 97, 282),
    ],
    473411: [],
    473412: [
        ("Target 2 ATR / stop 1 ATR from the signal close", 117, 125),
    ],
    473706: [
        ("strategy(): 10 % of equity; stop 1 % / target 2 % of the signal close", 87, 128),
    ],
    473709: [
        ("Stop 4 ATR / target 2 (2.237) ATR from the current close, every bar", 135, 137),
    ],
    473935: [],
    473936: [
        ("Stop = previous low / high; target 1 : 1", 114, 136),
    ],
    473937: [
        ("Stop 16 % / target 9.5 % of avg", 99, 173),
    ],
    # ---- FMZ-C, batch C220 (2026-10-22)
    473943: [],
    473944: [],
    473945: [
        ("strategy(): fixed qty 1; qty = equity x 20 / close, doubled on repeat entries (pyramiding 1)", 101, 173),
    ],
    474020: [
        ("strategy(): 10 % of equity", 99, 100),
    ],
    474022: [
        ("Size = equity x 1 % / (2 ATR); stop 2 ATR / target 4 ATR, trail_offset 1.5 ATR", 142, 171),
    ],
    474025: [
        ("strategy(): 2 % of equity; size by 1 % risk; stop 1.5 ATR / target 3 ATR", 91, 151),
    ],
    474030: [],
    474037: [
        ("strategy(): capital 25000", 105, 105),
    ],
    474038: [
        ("SL / TP1 / TP2 from the signal bar's high / low", 143, 171),
    ],
    474049: [],
    474050: [
        ("strategy(): 10 % of equity; stop at the 5-bar extreme, target 2 R", 101, 169),
    ],
    # ---- FMZ-C, batch C221 (2026-10-22)
    474051: [
        ("strategy(): 100 % of equity; stop 5 % / target 10 % of avg", 103, 156),
    ],
    474052: [
        ("Size from a typed balance, risk 1.5 %, leverage 2; target 4 ATR / stop 2 ATR", 94, 135),
    ],
    474053: [],
    474058: [
        ("Stop 1.5 % / target 3 % of avg on the signal bar", 112, 169),
    ],
    474061: [
        ("strategy(): 10 % of equity", 95, 95),
    ],
    474062: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 3", 99, 99),
    ],
    474065: [],
    474075: [
        ("Stop 2 % / target 2 % x 2 of the signal close", 107, 151),
    ],
    474630: [],
    # ---- FMZ-C, batch C222 (2026-10-22)
    474631: [],
    474632: [],
    474634: [
        ("Stop / target 5000 ticks from the signal low / high", 118, 144),
    ],
    474635: [],
    474668: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 3; target trigger 20 %, stop 12 % of the signal close", 149, 240),
    ],
    474670: [
        ("Size = 1000 / R; target avg + 3 R; trailing stop", 111, 173),
    ],
    474672: [],
    474679: [
        ("strategy(): 100 % of equity; target / stop 50 points", 96, 133),
    ],
    474681: [],
    474682: [
        ("Stop 2 % / target 4 % of avg", 97, 137),
    ],
    474683: [],
    474684: [
        ("Target 10 % / stop 0.10 % of the current close (every bar)", 186, 198),
    ],
    # ---- FMZ-C, batch C223 (2026-10-22)
    474690: [],
    474704: [
        ("Stop close x 0.995 / limit close x 1.9999", 130, 136),
    ],
    474706: [
        ("Trigger / target 107 pips (pip = mintick x 10)", 94, 127),
    ],
    474707: [
        ("Target 3 % of the stored buy price", 118, 164),
    ],
    474708: [
        ("Stop 1 %, target 2 R from the signal close", 101, 138),
    ],
    474717: [
        ("strategy(): fixed qty 1; contract size 1; stop 1 %, TP ratio 2", 99, 202),
    ],
    474720: [
        ("Target 2.0 points / stop 1 ATR from the signal close", 110, 131),
    ],
    474722: [],
    474804: [
        ("strategy(): 100 % of equity; size by 1 % risk of 10000; stop 1.5 ATR / target 3 ATR from avg", 100, 151),
    ],
    # ---- FMZ-C, batch C224 (2026-10-22)
    474806: [],
    474808: [],
    474810: [
        ("qty = equity x 3 / close; stop at the signal bar's low / high; commission 0.04 %", 92, 137),
    ],
    474815: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 3", 89, 89),
    ],
    474833: [
        ("Target 2 % / stop 1 % of the signal close", 111, 141),
    ],
    474834: [],
    474838: [
        ("Exit at the 100-bar high / low (every bar)", 147, 150),
    ],
    474839: [
        ("Fixed size 1", 124, 134),
    ],
    474840: [
        ("strategy(): margin 100 %", 95, 95),
    ],
    474843: [
        ("strategy(): 10 % of equity; target 10 % / stop 5 % of the current close", 87, 140),
    ],
    # ---- FMZ-C, batch C225 (2026-10-22)
    474846: [
        ("strategy(): 100 % of equity, capital 10000", 117, 117),
    ],
    474847: [
        ("strategy(): 100 % of equity", 99, 99),
    ],
    474849: [
        ("Size = capital x 1 % / stop distance (min 1)", 129, 141),
    ],
    474859: [],
    474860: [
        ("Fixed qty 1", 238, 241),
    ],
    474862: [],
    474864: [
        ("Stop 2 ATR / target 4 ATR from the signal close", 142, 158),
    ],
    474865: [
        ("strategy(): fixed qty 1; buy / sell quantity 1", 117, 171),
    ],
    474869: [],
    474874: [
        ("Stop 1 % / target 2 % of the current close (every bar)", 99, 138),
    ],
    474876: [
        ("strategy(): 100 % of equity; ATR stop / target x 2 (when=)", 92, 162),
    ],
    # ---- FMZ-C, batch C226 (2026-10-22)
    474880: [
        ("Take profit 5 % / stop 2 % of the stored max price", 201, 224),
    ],
    474881: [],
    474883: [],
    474884: [
        ("Lot size by 1 % risk of equity; stop 2 ATR / target 6 ATR from the current close", 104, 167),
    ],
    474885: [
        ("qty 1", 125, 128),
    ],
    474953: [],
    474955: [],
    474958: [
        ("strategy(): 30 % of equity; stop at previous opens, target 2 R", 87, 121),
    ],
    474959: [
        ("Stop 1.1 ATR / target 2 ATR from avg", 130, 144),
    ],
    # ---- FMZ-C, batch C227 (2026-10-22)
    474961: [],
    474962: [
        ("Contracts 1 per id; stop / target 25 points from avg; trail 25 / 25", 104, 139),
    ],
    474964: [
        ("Stop at the 5-bar low / high, target 2 R", 194, 222),
    ],
    474965: [
        ("Stop 50 %, target 5 %, trail activation 3 %, offset close x 2 % ticks", 103, 156),
    ],
    474967: [],
    474971: [
        ("strategy(): 200 % of equity, capital 100000", 90, 90),
    ],
    474972: [
        ("strategy(): 200 % of equity; stop 5 / target 10 pips from avg", 96, 186),
    ],
    474976: [
        ("Stop 1.5 ATR / target 3 ATR from avg", 110, 135),
    ],
    474977: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 3", 115, 115),
    ],
    474980: [
        ("strategy(): 100 % of equity", 123, 123),
    ],
    # ---- FMZ-C, batch C228 (2026-10-22)
    474984: [
        ("Stop / target 2 % of avg", 130, 155),
    ],
    475313: [],
    475589: [
        ("Size by 1 % risk of equity; stop 1 % / target 2 % of the signal close; trail_offset", 92, 119),
    ],
    475590: [
        ("Stop 2.5 ATR / target 4 ATR from avg", 107, 169),
    ],
    475595: [],
    475596: [
        ("Commission 0.1 %, slippage 3", 93, 93),
    ],
    475597: [
        ("Stop 1 % / target 0.5 % of the signal close", 104, 122),
    ],
    475598: [],
    475604: [
        ("$50000 per dip (qty = amount / close)", 112, 154),
    ],
    # ---- FMZ-C, batch C229 (2026-10-22)
    475606: [],
    475619: [],
    475624: [
        ("strategy(): capital 100000", 104, 104),
    ],
    475627: [
        ("Stop at the last red low under EMA 100, target 3 R; break-even at +2 %", 110, 122),
    ],
    475628: [],
    475630: [],
    475633: [
        ("qty 0.5 per id; stop / TP1 / TP2 from the 20-bar low", 103, 144),
    ],
    475635: [
        ("Stop 1 % / target 2 % of the signal close", 107, 148),
    ],
    475636: [],
    475637: [
        ("5 contracts; stop 1 ATR / target 1.5 ATR", 105, 138),
    ],
    # ---- FMZ-C, batch C230 (2026-10-22)
    476240: [],
    476242: [
        ("Stop 2 % / target 4 % of the current close", 148, 152),
    ],
    476243: [
        ("ATR 12 x 1.8 stop / target from the current close", 118, 138),
    ],
    476244: [],
    476248: [
        ("Stop 1 % / target 2 % of the current close", 129, 132),
    ],
    476252: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 3", 92, 98),
    ],
    476254: [
        ("Stop 2 % / target 4 % of the current close; risk 1 % (unused)", 100, 133),
    ],
    476255: [
        ("Hard stop 50 ticks x tick size 1.0", 105, 106),
    ],
    # ---- FMZ-C, batch C231 (2026-10-22)
    476256: [],
    476259: [
        ("Stop 3 % of strategy.position_avg_price", 180, 188),
    ],
    476260: [
        ("strategy(): 10 % of equity", 97, 97),
    ],
    476262: [],
    476263: [
        ("strategy(): 100 % of equity; TP 10 / SL 5 %, dynamic TP 20 / SL 2.5 %", 97, 174),
    ],
    476265: [
        ("Stop 2 % (drawn only)", 95, 129),
    ],
    476268: [],
    476269: [],
    476270: [
        ("strategy(): capital 86; qty = 86 USDT / close", 89, 110),
    ],
    476273: [
        ("strategy(): commission 0.1 %, slippage 3", 93, 93),
    ],
    # ---- FMZ-C, batch C232 (2026-10-22)
    476277: [],
    476278: [
        ("Stop 1.2 % / target 1.8 % of strategy.position_avg_price", 95, 128),
    ],
    476279: [],
    476280: [],
    476281: [],
    476283: [
        ("strategy(): 10 % of equity; ATR 1.5 / 2.0 bracket from the avg price", 92, 151),
    ],
    476284: [
        ("qty 1", 167, 167),
    ],
    477511: [
        ("TP multipliers 0.5-2.0 of the signal bar's range; stop 3 % of the close", 123, 182),
    ],
    477513: [
        ("Stop 1.5 % / target 3 % of the current close", 137, 147),
    ],
    477516: [
        ("strategy(): capital 50000, qty 1; stop 1 % / target 2 %", 108, 165),
    ],
    477519: [],
    477521: [
        ("capital 50000 x 100 % / close as qty; exit after 20 ticks", 120, 183),
    ],
    # ---- FMZ-C, batch C233 (2026-10-22)
    477524: [],
    477528: [
        ("Stop 1.5 % / target 3 % of strategy.position_avg_price", 162, 170),
    ],
    477529: [],
    477530: [],
    477533: [
        ("Stop 1 %, risk-reward 2", 105, 141),
    ],
    477535: [
        ("Fixed stop 1 %, risk-reward 2", 141, 182),
    ],
    477537: [
        ("strategy(): capital 1000, margin 20 %, 100 % of equity; qty = equity / close x leverage 4.5", 97, 193),
    ],
    477549: [],
    477550: [
        ("qty = 10 % of equity / close", 169, 169),
    ],
    477552: [
        ("strategy(): 100 % of equity", 85, 85),
    ],
    477553: [],
    # ---- FMZ-C, batch C234 (2026-10-22)
    477554: [],
    477555: [
        ("strategy(): commission 0.1 %, slippage 3; close at 2 % over the avg price", 131, 169),
    ],
    477556: [
        ("pip value 0.10 x mintick (stop levels never sent)", 104, 134),
    ],
    477560: [
        ("TP 2 x ATR / SL 1 x ATR from the signal close", 87, 118),
    ],
    477561: [],
    477562: [],
    477564: [
        ("Stop 2 % of strategy.position_avg_price", 111, 140),
    ],
    477567: [
        ("ATR threshold 1.0 (price)", 98, 98),
    ],
    477569: [],
    477579: [
        ("strategy(): capital 100000, commission 0.1 %, slippage 3; qty 1", 96, 134),
    ],
    477580: [
        ("strategy(): capital 10000, fixed qty 1; swing stop, 2 R / 3 R targets", 105, 208),
    ],
    # ---- FMZ-C, batch C235 (2026-10-22)
    477581: [
        ("Target 4 % / stop 0.5 % of strategy.position_avg_price (long formulas for both sides)", 109, 144),
    ],
    477583: [
        ("strategy(): 200 % of equity", 127, 127),
    ],
    477587: [],
    477590: [],
    477592: [
        ("Stop 1 %, R:R 1:1 / 1:4 / 1:8", 124, 171),
    ],
    477593: [
        ("qty 1; take profit 0.02 / stop 0.01 (fractions)", 96, 128),
    ],
    477595: [
        ("ATR 14 x 1.5 stop / x 2.5 target", 122, 157),
    ],
    477596: [],
    477597: [
        ("qty 1; stop 5 % of the avg price; trailing inputs unused", 198, 219),
    ],
    477598: [
        ("qty = equity x 200 % / close; ATR 14 x 1.5 stop / target; risk tolerance unused", 94, 128),
    ],
    # ---- FMZ-C, batch C236 (2026-10-22)
    477604: [
        ("Stop at the 3-bar low / high, R:R 1.5", 97, 132),
    ],
    477605: [
        ("strategy(): 100 % of equity, capital 50000", 95, 101),
    ],
    477606: [],
    477608: [
        ("ATR 14 x 1 stop / target", 106, 145),
    ],
    477609: [
        ("Stop at the 5-bar swing, target 2 R", 97, 140),
    ],
    477611: [
        ("Stop 0.1 % / target 0.25 %; break-even at +0.1 %", 106, 144),
    ],
    477612: [
        ("Stop 1 %, TP1 2 %, TP2 3 %; capital 10000 and risk 2 % unused", 109, 146),
    ],
    477613: [],
    477614: [],
    477943: [],
    # ---- FMZ-C, batch C237 (2026-10-22)
    477944: [
        ("Stop 10 % / target 26 % of strategy.position_avg_price", 103, 156),
    ],
    477945: [
        ("qty = equity x 1 % / (ATR x R:R); ATR stop / 2 ATR target", 104, 141),
    ],
    477946: [
        ("Target +25 % / stop -10 % of the avg price", 125, 131),
    ],
    477949: [],
    477951: [],
    477952: [
        ("strategy(): capital 50000, commission 0.05 per contract, slippage 1", 83, 83),
    ],
    477955: [
        ("Stop 1 % / target 2 % of strategy.position_avg_price", 98, 114),
    ],
    477956: [
        ("qty 1; TP 10 x ATR, SL 3 x ATR", 108, 153),
    ],
    477960: [],
    477961: [
        ("strategy(): capital 100000, commission 0.001425, slippage 1; ATR 2 stop / 2 target", 107, 205),
    ],
    # ---- FMZ-C, batch C238 (2026-10-22)
    477973: [
        ("qty 1 (contract size); risk-reward TP / SL, R:R 2; tick / dollar modes off", 105, 184),
    ],
    477974: [
        ("strategy(): 100 % of equity; stop 25 % under the highest high", 100, 148),
    ],
    477975: [
        ("Stop 50 / target 100 x mintick from the current close", 151, 155),
    ],
    477977: [],
    478685: [
        ("Trailing 5 % of the close (bar-close ratchet)", 109, 144),
    ],
    478686: [],
    478687: [],
    478690: [],
    478694: [
        ("strategy(): 100 % of equity; stop 50 / trail 70 points", 101, 158),
    ],
    # ---- FMZ-C, batch C239 (2026-10-22)
    478695: [
        ("TP 0.5 x / SL 1.0 x the outside bar height", 133, 152),
    ],
    478700: [
        ("strategy(): 100 % of equity", 99, 99),
    ],
    478701: [],
    478705: [],
    478706: [
        ("strategy(): 100 % of equity; risk 2 %; ATR 1.5 stop / 2.0 target", 124, 166),
    ],
    478707: [],
    478708: [],
    478712: [
        ("strategy(): 200 % of equity; SL 2 ATR, TP 1.5 x SL", 89, 151),
    ],
    478720: [
        ("strategy(): 200 % of equity; ATR 1.5 stop / 2 target", 99, 170),
    ],
    478721: [
        ("TP 1 % / SL 5 % of strategy.position_avg_price", 118, 179),
    ],
    # ---- FMZ-C, batch C240 (2026-10-22)
    478724: [],
    478725: [
        ("Stop 2 %; target 6 % (trend) / 4 % (range) of the signal close", 91, 161),
    ],
    478727: [
        ("strategy(): capital 100000, 200 % of equity; 5-bar stop, TP 3.5 R from the avg price", 102, 185),
    ],
    478733: [],
    478734: [
        ("strategy(): 200 % of equity", 123, 123),
    ],
    478736: [
        ("strategy(): 200 % of equity; stop 1 % / target 1.5 % of the current close", 107, 148),
    ],
    478737: [
        ("Target 0.618 of the price, stop buffer 0.5 %", 112, 151),
    ],
    478740: [
        ("Stop at the previous low / high + body / 5; target 1.8 bodies", 170, 209),
    ],
    478742: [
        ("qty 20 / close (20 % of equity default); stop 1 % / target 2 %", 107, 145),
    ],
    478743: [],
    478744: [],
    478747: [
        ("strategy(): 200 % of equity; stop 1 % / target 2 %", 119, 161),
    ],
    # ---- FMZ-C, batch C241 (2026-10-22)
    478748: [
        ("ATR 14 x 1.5 stop / x 3 target from the current close", 131, 139),
    ],
    481093: [
        ("qty = min(equity x 0.5 % / ATR 22, equity x 0.5 / close); commission 0.1 %", 103, 220),
    ],
    481094: [],
    481097: [
        ("strategy(): 200 % of equity", 97, 97),
    ],
    481100: [
        ("Stop at the candle low / high, R:R 1:2", 141, 157),
    ],
    481103: [],
    481104: [
        ("strategy(): margin 100 %; trail 1.5 x ATR", 104, 145),
    ],
    481105: [
        ("strategy(): 200 % of equity", 101, 101),
    ],
    481347: [
        ("capital 15000, risk 1000, target 5000, lot 1; stop 30 points", 107, 152),
    ],
    481349: [
        ("strategy(): 200 % of equity; ATR 1.5 stop / 2 target", 135, 174),
    ],
    # ---- FMZ-C, batch C242 (2026-10-22)
    481350: [
        ("strategy(): margin 100 %; stop 2 % / target 4 % of the avg price", 93, 136),
    ],
    481351: [],
    481352: [],
    481354: [],
    481355: [
        ("strategy(): capital 100000, 200 % of equity; target / stop 30 points", 91, 175),
    ],
    481362: [
        ("Stop 1.5 % of the avg price (danger-armed)", 119, 155),
    ],
    481364: [
        ("strategy(): 200 % of equity", 147, 147),
    ],
    481365: [
        ("strategy(): capital 1000, 200 % of equity, commission 0.1 %; stop 2 %, R:R 1.5", 97, 151),
    ],
    481370: [
        ("SL 300 $ / TP 1000 $ (off) from the avg price; bars till close 10", 115, 182),
    ],
    481393: [],
    # ---- FMZ-C, batch C243 (2026-10-22)
    481394: [],
    482241: [],
    482242: [
        ("strategy(): capital 100000, 200 % of equity", 108, 109),
    ],
    482419: [
        ("strategy(): 300 % of equity; stop 1 % / target 2 %", 97, 205),
    ],
    482424: [
        ("strategy(): 250 % of equity; stop 1 % / target 2 % of the avg price", 129, 162),
    ],
    482426: [
        ("strategy(): 250 % of equity, commission 0.1 %", 101, 101),
    ],
    482427: [],
    482428: [
        ("strategy(): capital 100000, 250 % of equity; trailing stop at the previous low / high", 91, 173),
    ],
    # ---- FMZ-C, batch C244 (2026-10-22)
    482434: [],
    482437: [
        ("input: trade size 1", 93, 93),
    ],
    482441: [
        ("strategy(): 250 % of equity", 119, 119),
    ],
    482443: [],
    482445: [],
    482447: [
        ("strategy(): fixed qty 1", 101, 101),
    ],
    482450: [
        ("capital 15000, risk 1000, target 5000, lot size 1", 108, 111),
        ("entries with qty = lot size", 148, 152),
    ],
    482451: [
        ("strategy(): capital 10000, 200 % of equity, commission 0.1 %", 91, 91),
    ],
    482453: [
        ("strategy(): capital 10000, 100 % of equity", 103, 103),
    ],
    # ---- FMZ-C, batch C245 (2026-10-22)
    482457: [],
    482458: [],
    482459: [
        ("strategy(): 200 % of equity", 102, 102),
    ],
    482460: [],
    482461: [],
    482463: [],
    482466: [
        ("strategy(): capital 100000, 100 % of equity, pyramiding 0", 93, 99),
    ],
    482468: [],
    482472: [],
    482473: [],
    482474: [
        ("strategy(): cash 50000, slippage 1, commission 0.01", 85, 87),
    ],
    482477: [],
    # ---- FMZ-C, batch C246 (2026-10-22)
    482489: [
        ("strategy(): margin 100 / 100", 87, 87),
    ],
    482500: [],
    482502: [
        ("strategy(): capital 10000, 200 % of equity", 97, 97),
    ],
    482510: [
        ("strategy(): 100 % of equity", 79, 79),
    ],
    482512: [],
    482515: [],
    482590: [],
    # ---- FMZ-C, batch C247 (2026-10-22)
    482591: [],
    482592: [
        ("strategy(): 200 % of equity", 89, 89),
    ],
    482593: [],
    482594: [],
    482595: [
        ("strategy(): 200 % of equity, pyramiding 0", 133, 133),
    ],
    482600: [],
    482602: [
        ("strategy(): 200 % of equity", 99, 99),
    ],
    482644: [],
    482645: [],
    482669: [],
    482670: [
        ("strategy(): 2 % of equity", 105, 105),
        ("tradeSize from strategy.equity x 2 % / atrSL, minimum 1", 160, 163),
        ("entries with qty = tradeSize", 171, 178),
    ],
    # ---- FMZ-C, batch C248 (2026-10-22)
    482673: [
        ("strategy(): 10 % of equity", 99, 99),
    ],
    482678: [],
    482684: [
        ("strategy(): 5 % of equity, commission 0.1, slippage 2", 89, 94),
    ],
    482687: [],
    482764: [],
    482769: [],
    482771: [],
    482773: [],
    482774: [
        ("strategy(): capital 100000, 100 % of equity", 114, 114),
    ],
    482775: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    482778: [
        ("strategy(): margin 100 / 100", 111, 111),
    ],
    # ---- FMZ-C, batch C249 (2026-10-22)
    482779: [
        ("strategy(): 10 % of equity", 106, 106),
    ],
    482786: [
        ("strategy(): capital 100000, 100 % of equity, commission 0.1 %, margin 100 / 100, pyramiding 1", 98, 98),
    ],
    482787: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    482788: [],
    482789: [],
    482792: [
        ("strategy(): 100 % of equity, commission 0.1, slippage 3", 91, 91),
    ],
    482793: [],
    482800: [],
    482802: [
        ("strategy(): margin 100 / 100", 84, 84),
    ],
    482803: [
        ("strategy(): capital 100000, 10 % of equity", 99, 99),
    ],
    # ---- FMZ-C, batch C250 (2026-10-22)
    482804: [],
    482805: [
        ("strategy(): 10 % of equity", 107, 107),
    ],
    482806: [],
    482809: [
        ("strategy(): 10 % of equity", 109, 109),
    ],
    482816: [
        ("strategy(): 10 % of equity", 97, 97),
    ],
    482817: [
        ("strategy(): 100 % of equity, margin 100 / 100", 98, 98),
        ("fixed_investment = 30000 USDT per trade", 101, 101),
        ("qty_long / qty_short = fixed_investment / close", 122, 123),
    ],
    482820: [],
    482822: [
        ("strategy(): 100 % of equity", 115, 115),
    ],
    482826: [],
    482830: [
        ("strategy(): 100 % of equity, commission 0.1 %, slippage 0", 121, 121),
    ],
    482831: [
        ("strategy(): 10 % of equity", 132, 132),
    ],
    482832: [],
    # ---- FMZ-C, batch C251 (2026-10-22)
    482833: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    482836: [
        ("riskPercent input (feeds nothing)", 118, 118),
    ],
    482837: [],
    482838: [],
    482841: [],
    482843: [
        ("strategy(): 10 % of equity", 105, 105),
    ],
    482846: [],
    482848: [
        ("strategy(): capital 10000, 5 % of equity, commission 0.1 %, slippage 1", 130, 130),
        ("riskPercent input (feeds nothing)", 142, 142),
    ],
    482849: [
        ("strategy(): 10 % of equity", 93, 93),
        ("RiskPercent quantity: equity x 1 % / stop distance", 99, 124),
    ],
    482859: [],
    # ---- FMZ-C, batch C252 (2026-10-22)
    482861: [
        ("strategy(): 10 % of equity", 111, 111),
    ],
    482863: [],
    482870: [],
    482872: [
        ("strategy(): 10 % of equity", 111, 111),
    ],
    482873: [
        ("strategy(): capital 10000, 10 % of equity", 111, 111),
    ],
    482878: [
        ("strategy(): 10 % of equity, pyramiding 0", 97, 97),
    ],
    482879: [
        ("strategy(): 1 % of equity", 99, 99),
    ],
    482886: [
        ("strategy(): 1 % of equity", 106, 106),
    ],
    482887: [],
    482889: [],
    482890: [
        ("strategy(): 10 % of equity, capital 5000", 103, 105),
    ],
    482891: [
        ("strategy(): capital 300, 10 % of equity, commission 0.1 %", 96, 96),
    ],
    # ---- FMZ-C, batch C253 (2026-10-22)
    482895: [
        ("strategy(): 10 % of equity", 85, 85),
    ],
    482897: [
        ("strategy(): 1 % of equity", 139, 139),
        ("lotSize = 0.1 per entry", 142, 142),
    ],
    482901: [],
    482904: [
        ("strategy(): capital 10000, 100 % of equity, commission 0.1 %", 105, 112),
    ],
    482906: [
        ("strategy(): capital 10000, 10 % of equity", 90, 91),
    ],
    482917: [
        ("strategy(): capital 10000, 10 % of equity", 105, 105),
    ],
    482919: [
        ("strategy(): 10 % of equity", 107, 107),
    ],
    482920: [
        ("strategy(): pyramiding 0, capital 10000, 100 % of equity", 96, 96),
    ],
    482921: [
        ("strategy(): capital 100000, 100 % of equity, pyramiding 0", 98, 104),
    ],
    # ---- FMZ-C, batch C254 (2026-10-22)
    483020: [
        ("strategy(): capital 100000, 10 % of equity", 99, 99),
    ],
    483021: [],
    483023: [
        ("strategy(): capital 10000", 101, 101),
    ],
    483026: [
        ("riskAmount = equity x 1 % (feeds no order)", 117, 117),
    ],
    483027: [],
    483029: [
        ("strategy(): 2 % of equity", 94, 94),
    ],
    483032: [],
    483034: [],
    483035: [],
    483037: [
        ("strategy(): 2 % of equity", 101, 101),
    ],
    483038: [],
    # ---- FMZ-C, batch C255 (2026-10-22)
    483040: [],
    483042: [],
    483044: [],
    483045: [],
    483047: [],
    483048: [
        ("strategy(): capital 1000, 1000 % of equity", 100, 100),
    ],
    483050: [
        ("strategy(): capital 100000, 100 % of equity, pyramiding 0", 92, 98),
    ],
    483052: [],
    483054: [],
    483055: [],
    483061: [],
    # ---- FMZ-C, batch C256 (2026-10-22)
    483063: [
        ("strategy(): 100 % of equity", 82, 82),
    ],
    483064: [
        ("strategy(): capital 1000, 100 % of equity, commission 0.1 %", 100, 100),
    ],
    483066: [],
    483072: [],
    483073: [
        ("strategy(): margin 100 / 100", 120, 120),
    ],
    483080: [],
    483082: [
        ("strategy(): 10 % of equity", 95, 95),
        ("positionSize = equity x 2 % / (0.5 % x close)", 115, 138),
    ],
    483087: [],
    483089: [
        ("strategy(): margin 100 / 100", 108, 108),
    ],
    483092: [
        ("strategy(): capital 10000, 1 % of equity", 103, 103),
    ],
    # ---- FMZ-C, batch C257 (2026-10-22)
    483096: [],
    483102: [],
    483103: [
        ("strategy(): 10 % of equity", 119, 119),
    ],
    483106: [],
    483108: [
        ("entries with qty = 1", 124, 143),
    ],
    483111: [],
    483112: [
        ("strategy(): pyramiding 1, capital 100000, 100 % of equity", 116, 118),
    ],
    483113: [
        ("strategy(): 100 % of equity", 108, 108),
    ],
    483114: [
        ("strategy(): margin 100 / 100", 93, 93),
    ],
    483115: [
        ("strategy(): 10 % of equity", 106, 106),
    ],
    483116: [],
    483117: [
        ("strategy(): 100 % of equity", 105, 105),
    ],
    # ---- FMZ-C, batch C258 (2026-10-22)
    483120: [],
    483121: [
        ("strategy(): 10 % of equity", 86, 86),
    ],
    483122: [],
    483123: [
        ("strategy(): margin 100 / 100", 97, 97),
    ],
    483124: [
        ("strategy(): capital 10000, 10 % of equity, commission 0.1 %", 138, 138),
    ],
    483126: [
        ("strategy(): capital 100000, 10 % of equity", 103, 103),
    ],
    483130: [
        ("strategy(): margin 100 / 100, pyramiding 1", 93, 93),
        ("risk-sized quantity: equity x 1 % / stop distance", 121, 124),
    ],
    483495: [
        ("strategy(): capital 100000, 10 % of equity", 91, 91),
    ],
    # ---- FMZ-C, batch C259 (2026-10-22)
    483503: [
        ("risk-sized quantity: equity x 1 % / stop distance", 97, 135),
    ],
    483504: [
        ("strategy(): 100 % of equity, commission 0.01", 93, 93),
        ("qty = equity x leverage 5 / close", 95, 98),
    ],
    483505: [
        ("strategy(): capital 1000, 100 % of equity", 97, 97),
    ],
    483509: [
        ("strategy(): capital 100000, 10 % of equity", 91, 91),
    ],
    483510: [],
    483514: [],
    483518: [],
    483525: [],
    483528: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    483674: [],
    # ---- FMZ-C, batch C260 (2026-10-22)
    483676: [
        ("strategy(): capital 100000", 205, 205),
    ],
    483679: [
        ("strategy(): 10 % of equity", 169, 169),
    ],
    483682: [
        ("position_size = equity x 1 % / (2 atr), capped at equity", 184, 185),
    ],
    483790: [
        ("strategy(): 100 % of equity", 161, 161),
    ],
    483791: [
        ("strategy(): 10 % of equity", 179, 179),
    ],
    483793: [
        ("strategy(): 10 % of equity", 179, 179),
    ],
    483794: [
        ("strategy(): capital 100000", 274, 274),
    ],
    484090: [],
    484092: [
        ("strategy(): 2 % of equity", 213, 213),
    ],
    484094: [],
    # ---- FMZ-C, batch C261 (2026-10-22)
    484096: [],
    484098: [
        ("strategy(): 100 % of equity", 173, 173),
    ],
    484101: [],
    484109: [
        ("strategy(): 1 % of equity", 150, 150),
        ("positionSize = equity x 0.5 % / stop distance", 183, 185),
    ],
    484571: [
        ("strategy(): margin 100 / 100", 183, 183),
    ],
    484578: [
        ("strategy(): capital 100000, 100 % of equity, commission 0.01 %", 192, 192),
    ],
    484580: [],
    484582: [
        ("strategy(): 10 % of equity, commission 0.1 %", 190, 190),
    ],
    484583: [
        ("strategy(): capital 10000, 2 % of equity", 185, 185),
    ],
    484584: [],
    484589: [],
    # ---- FMZ-C, batch C262 (2026-10-22)
    484592: [
        ("strategy(): commission 0.1 %", 205, 205),
    ],
    484595: [],
    484771: [
        ("defaultQuantity = 2 per entry", 261, 261),
    ],
    484773: [
        ("strategy(): 10 % of equity", 200, 200),
    ],
    484911: [
        ("strategy(): capital 10000, 10 % of equity", 206, 206),
    ],
    484912: [
        ("strategy(): 1 % of equity", 188, 188),
    ],
    484919: [],
    484921: [
        ("strategy(): 10 % of equity", 324, 324),
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
    426478: ("1", "The signal is a crossover of security(tickerid, '375', close) and security(..., open) on "
                  "the daily header chart: a 375-minute resolution below the chart's, whose value per daily "
                  "bar (and 375-minute block alignment on a 24 h market) is undefined (as #426261)."),
    # ---- worker A, batch A22 (2026-10-08)
    # ---- worker A, batch A23 (2026-10-08)
    426556: ("1", "Weekend range bot on 2-day header bars: the reference is security(ticker, 'D', "
                  "close[days_since_friday]), a daily (lower-than-chart) resolution whose value per 2-day "
                  "bar is undefined (as #426261), and the weekday rules (Saturday / Sunday entries, Monday "
                  "close) cannot be resolved on 2-day bars. (Its averaging adds and openprofit exit "
                  "would be sizing; re-worded in A27.)"),
    426570: ("1", "Turtle short with pyramiding = 5: up to five 'P' adds every pyramidInput x N below the last "
                  "add, with the stop and the win / loss bookkeeping driven by the averaged price of the "
                  "stacked units (a pyramided ladder, as #395966)."),
    # ---- worker A, batch A24 (2026-10-08)
    426610: ("1", "Exits are a partial take-profit ladder (strategy.exit qty_percent 20 % at +15 % and 20 % "
                  "at +30 %) plus a full close: partial exits cannot be expressed as one net position's "
                  "signals (as #365389)."),
    426621: ("1", "CoinFlip: the direction is int(math.random() + 0.5), a random draw each bar, so there is "
                  "no deterministic rule to test (the ATR-scaled qty and bracket only frame the coin flip)."),
    # ---- worker A, batch A25 (2026-10-08)
    426781: ("1", "pyramiding = 2 with two long entry ids ('Fast Enter', 'Slow Enter') that fill together "
                  "and exit separately (each with its own RSI exit and a 10 % stop under the averaged "
                  "price): each unit leaves on its own exit, i.e. partial exits of the net position (as "
                  "#365389)."),
    426811: ("3", "The signal is a monthly SMA cross of another instrument (security('BMFBOVESPA:IBOV', 'M', "
                  "close)): the strategy trades the chart symbol on the Bovespa index, which the project's "
                  "bars do not carry."),
    # ---- worker A, batch A26 (2026-10-08)
    426825: ("1", "The only exit is strategy.exit(stop = buyStop / sellStop), a level recomputed every bar "
                  "whose ratchet reads strategy.position_size (a moving stop, rule 2), and the entry rule "
                  "itself reads that level (close - 3 ATR > buyStop). The position path cannot be produced "
                  "until moving stops are expressible; port it then (decision owed)."),
    426832: ("3", "The signal is the SMA of the ratio of the chart symbol to a second instrument "
                  "(security('BTC_USDT:swap', close)): a spread between two contracts the project's "
                  "single-symbol bars do not carry."),
    # ---- worker A, batch A27 (2026-10-08)
    426849: ("1", "Exits are a partial take-profit (strategy.exit qty_percent = tp1 % at TP1) plus a "
                  "second exit, with the stop moved to the entry price after the partial fill: partial "
                  "exits cannot be expressed as one net position's signals (as #365389)."),
    426850: ("1", "Exits are a three-step partial take-profit ladder (Exit1-Exit3 with qty 10 / 15 / 20 % "
                  "at +5 / +10 / +15 %) plus the remainder: partial exits (as #365389)."),
    426882: ("1", "Every exit tests strategy.position_size >= 1 (at least one whole unit held), and the "
                  "risk-based qty is a fraction of a coin on BTC, so whether any exit can fire depends on "
                  "the sizing formula (as #425798)."),
    # ---- worker A, batch A29 (2026-10-08)
    426936: ("1", "Dollar-cost averaging: strategy.order buys int(200 / close) units on every bar and sells "
                  "the accumulated position on bar_index == last_bar_index - 2 (a read of where the data "
                  "ends); the position is an accumulation, not a signal (as #380530)."),
    427063: ("1", "Exits include strategy.close(qty = position_size / 3) (a partial close) and adds via "
                  "strategy.order below the average price, with stops on unit counts "
                  "(position_size >= 1): partial exits (as #365389)."),
    # ---- FMZ-C, batch C1 (2026-10-15)
    427066: ("1", "Reads the future: Pine v2 security(syminfo.tickerid, 'D', close) without [1] "
              "behaves as lookahead_on (the v2-to-v3 converter adds lookahead_on to keep it), so "
              "on every intraday bar 'today' is the final close of the current day, which is not "
              "known until the day ends (SURVEY_README request.security rule, as #363557). Its "
              "DG427066 partner #428082 is read on its own."),
    427119: ("1", "The only exit is strategy.exit('SL', limit = the signal bar's close) for both "
              "sides: a resting limit at the signal close, which relative to the next-open fill "
              "is at or beyond the market half of the time (an immediate exit on the fill bar) "
              "and otherwise a tiny target. It cannot be expressed as a positive tp_stop fraction "
              "of the fill, and the trade path depends on the open gap; named 'SL', the author "
              "probably meant a breakeven stop (decision owed if the project wants that version)."),
    427127: ("1", "The stop is low[barsSinceEntry] x (1 - range / avg price), i.e. built from the "
              "ENTRY (fill) bar's own low and range, and it is placed only at that bar's close "
              "(active from the next bar). A stop derived from the fill bar's data cannot be "
              "expressed (skill section 7: a stop must be known at the fill bar's open); "
              "trail_price without trail_offset adds no trailing. Porting it would change the "
              "exit."),
    # ---- FMZ-C, batch C2 (2026-10-15)
    427139: ("1", "The exit 'stoploss' tests strategy.openprofit against a share of strategy.equity "
              "(it depends on the sizing), and the signals read security(ticker, '98', ...) on a "
              "2-minute chart in Pine v2 (lookahead_on: a 98-minute bar's values are seen from "
              "its first chart bar) shifted by sampling = resInteger / timeframe.period, an "
              "integer divided by a string. The higher-timeframe values and the history offset "
              "are undefined (as #361719)."),
    427158: ("1", "Exits include strategy.exit(qty_percent = 50 %) at a take-profit plus a second "
              "stop for the rest: partial exits cannot be expressed as one net position's signals "
              "(as #365389); the risk-based entry quantity is also used by the exits."),
    427161: ("1", "Exits are strategy.exit('XPartLong', qty_percent = 50, profit = 150 ticks) plus a "
              "second exit for the rest at 400 ticks or a pivot stop: partial exits (as #365389); "
              "tick distances are also instrument-specific."),
    427182: ("1", "Two scripts pasted into one file: a Pine v5 breakout snippet (entries 'Enter Long' "
              "/ 'Enter Short' on 5-bar highs / lows) placed before the strategy() line of a v3 "
              "EMA 10/21 script (entry 'Buy', closed by id 'Buy'). Both act on one position and "
              "the close only targets the 'Buy' id, so the position path depends on per-id "
              "accounting that a net-position port cannot reproduce, and which script is meant is "
              "undefined."),
    # ---- FMZ-C, batch C5 (2026-10-16)
    427306: ("1", "Both signal lines are request.security(syminfo.tickerid, '30', ...) on the daily "
              "header chart: a 30-minute resolution below the chart's, whose value per daily bar "
              "is undefined (as #426261 / #426478)."),
    # ---- FMZ-C, batch C6 (2026-10-16)
    427366: ("1", "The stop, target and trailing distances are set on the bar the position appears "
              "(strategy.position_size changes, i.e. the FILL bar), from that bar's ta.lowest(14) "
              "/ ta.highest(14) and ATR, and the trailing points are scaled by 100000 (5-digit FX "
              "points). A stop built from the fill bar's own data cannot be expressed (skill "
              "section 7; as #427127)."),
    427379: ("1", "The stop and target come from valuewhen(position_size changed, lowest(20) / "
              "highest(20), 0), i.e. the 20-bar swing measured on the FILL bar itself (its own "
              "low / high included), and are active from the next bar: a stop from the fill bar's "
              "data cannot be expressed (as #427127)."),
    # ---- FMZ-C, batch C8 (2026-10-16)
    427477: ("2", "The signal is the distance to a round-number price level built in ticks "
              "(roundLevel = close[1] / mintick rounded to 500 ticks, distance in 100 ticks, "
              "10-bar lows / highs against that level): hard-coded price levels and tick "
              "distances specific to the instrument and its tick size. Re-expressing them would "
              "remove the round-number idea itself. The exit is a trail_points-only strategy.exit "
              "(no offset)."),
    # ---- FMZ-C, batch C9 (2026-10-16)
    427518: ("1", "The index adds security(syminfo.tickerid, '60', close[1] / open[1]) on the daily "
              "header chart: a 60-minute resolution below the chart's, whose value per daily bar "
              "is undefined (as #426261 / #426478)."),
    # ---- FMZ-C, batch C13 (2026-10-16)
    427890: ("1", "The buy / sell filter is security(syminfo.tickerid, '60', swap4[1], lookahead_on) "
              "on the 3-hour header chart: a 60-minute resolution below the chart's, whose value "
              "per 3-hour bar is undefined (as #427518)."),
    # ---- FMZ-C, batch C14 (2026-10-16)
    427899: ("1", "The signals use security(syminfo.tickerid, TF_, close, lookahead_off) with TF_ = "
              "\"1\" (the if-chain uses == instead of :=, so TF_ never changes) on the 1-hour "
              "header chart: a 1-minute resolution below the chart's, whose value per bar is "
              "undefined (as #427518)."),
    427926: ("1", "Both DEMAs are request.security(syminfo.tickerid, '120', ...) on the daily header "
              "chart: a 120-minute resolution below the chart's, whose value per daily bar is "
              "undefined (as #427518)."),
    # ---- FMZ-C, batch C15 (2026-10-16)
    427997: ("1", "Every open and close rule (30 band / %B / band-width events) defaults to 'Not "
              "Used', so at the defaults the strategy places no order; choosing rules would be "
              "authoring a new strategy, not a port."),
    # ---- FMZ-C, batch C16 (2026-10-16)
    428066: ("1", "Exits include strategy.exit('XPartLong', qty_percent = 50, profit = 150 ticks) "
              "plus a second exit for the rest: partial exits cannot be expressed as one net "
              "position (as #427161)."),
    # ---- FMZ-C, batch C17 (2026-10-16)
    428102: ("1", "The higher-timeframe RSIs are request.security(syminfo.tickerid, '3' / '5', "
              "rsi[1], lookahead_on) on the daily header chart: 3- and 5-minute resolutions below "
              "the chart's, whose value per daily bar is undefined (as #427518)."),
    428611: ("1", "The TSI runs on request.security(syminfo.tickerid, '15', close) on the daily "
              "header chart: a 15-minute resolution below the chart's, whose value per daily bar "
              "is undefined (as #427518)."),
    # ---- FMZ-C, batch C18 (2026-10-16)
    428618: ("1", "The stop and target come from valuewhen(bought, ohlc4 - 3 atr(14), 0) with bought "
              "= position size changed, i.e. the FILL bar's own ohlc4 and ATR (as #427127); "
              "swing-stop option likewise."),
    428624: ("1", "The entries use request.security(syminfo.tickerid, '1', hist) on the 1-hour header "
              "chart: a 1-minute resolution below the chart's, whose value per bar is undefined "
              "(as #427518)."),
    # ---- FMZ-C, batch C19 (2026-10-16)
    428718: ("1", "DCA ladder: pyramiding 100 (commented-out strategy()), a new long about every 240 "
              "bars after an EMA-CD crossover, and the only exit is strategy.close_all() on "
              "barstate.islast, the last bar of the data; the ladder held to the data's end is "
              "the strategy (as #426302)."),
    # ---- FMZ-C, batch C21 (2026-10-16)
    428894: ("1", "The short supertrend uses request.security(syminfo.tickerid, '60', ...) on the "
              "4-hour header chart: a 1-hour resolution below the chart's, whose value per bar is "
              "undefined (as #427518)."),
    # ---- FMZ-C, batch C23 (2026-10-16)
    429163: ("1", "Grid ladder: up to 7 long lots (pyramiding 14, close_entries_rule ANY), one bought "
              "below each of 8 grid lines from a 250-bar high / low band and closed one line "
              "higher; the position ladder is the strategy (as #426302)."),
    # ---- FMZ-C, batch C24 (2026-10-16)
    429387: ("1", "Leverage ladder: up to 25 stacked longs (pyramiding 25), opened while "
              "strategy.opentrades is below 10 / (ATR ratio) and closed last-in-first-out above "
              "it; the position size is the whole strategy (as #426302)."),
    429401: ("1", "The source does not have a defined structure: `if useMartin` (line 68) has no "
              "body, and the martingale-add and exit lines (70-73, 80-83) sit at inconsistent "
              "indentation under unindented ifs, so which statements belong to which condition is "
              "undefined; the exits also pass prices as tick counts and the adds are a martingale "
              "ladder (ND422794)."),
    # ---- FMZ-C, batch C25 (2026-10-16)
    429483: ("1", "The MACD condition uses request.security(syminfo.tickerid, '1', Macdhist) on the "
              "3-hour header chart: a 1-minute resolution below the chart's, whose value per bar "
              "is undefined (as #427518)."),
    # ---- FMZ-C, batch C27 (2026-10-16)
    429566: ("1", "The open series is request.security(syminfo.tickerid, '120', DEMA(open, 14)) on "
              "the 1-day header chart: a 2-hour resolution below the chart's, whose value per bar "
              "is undefined (as #427518)."),
    429568: ("1", "Incremental-size ladder: up to ten long and short entries of growing quantity (1, "
              "2, 4, 8, 5 ... 10; pyramiding 10) at Fibonacci levels, with per-tranche closes; "
              "the position ladder is the strategy (as #426302)."),
    # ---- FMZ-C, batch C28 (2026-10-16)
    429581: ("1", "Partial exits: each entry places three exits of 25 % / 25 % / the rest at three "
              "targets with a shared stop (qty_percent); a partial scale-out cannot be expressed "
              "by the all-or-nothing contract (as #427161)."),
    # ---- FMZ-C, batch C31 (2026-10-16)
    429969: ("1", "Exits are strategy.exit('Long TP / SL', qty_percent = 50, limit = TP, stop = SL) "
              "plus a second exit for the rest at the stop, with a SuperTrend-flip close and "
              "risk-based quantities: partial exits (as #365389)."),
    430011: ("1", "The signal is crossover(request.security(syminfo.tickerid, '720', close), "
              "request.security(syminfo.tickerid, '720', open)) on the 1-day header chart: a "
              "12-hour resolution below the chart's, whose value per bar is undefined (as "
              "#427518)."),
    430022: ("1", "Every moving-average and oscillator vote of the rating is "
              "request.security(syminfo.tickerid, '240', ...) on the 1-day header chart: a 4-hour "
              "resolution below the chart's, whose value per bar is undefined (as #427518)."),
    430030: ("1", "Entries only from flat (strategy.opentrades < 1) with every exit commented out: "
              "after the first signal the position is held for the rest of the data, so there is "
              "no repeatable entry/exit rule to test (as #368717)."),
    430034: ("1", "Alert-message demo: the position flips long / short on the parity of bar_index "
              "(long on even bars, short on odd), which depends only on where the data starts; no "
              "market rule (as #62163)."),
    430040: ("1", "The Heikin Ashi candles are request.security(heikinashi, '30', ...) and the EMA "
              "source request.security(heikinashi, '180', ...) on the 3-hour header chart: a "
              "30-minute resolution below the chart's, whose value per bar is undefined (as "
              "#427518)."),
    # ---- FMZ-C, batch C32 (2026-10-16)
    430113: ("1", "The trend filter is request.security(syminfo.tickerid, '240', sma(close, 200)) on "
              "the 1-day header chart: a 4-hour resolution below the chart's, whose value per bar "
              "is undefined (as #427518)."),
    # ---- FMZ-C, batch C33 (2026-10-16)
    430149: ("1", "The trend filter is request.security(syminfo.tickerid, tostring(60), close / "
              "sma(close, 20)) on the 1-day header chart: a 1-hour resolution below the chart's, "
              "whose value per bar is undefined (as #427518)."),
    430178: ("1", "Exits are strategy.exit('TP1/SL', qty_percent = 50, limit = TP1) plus a second "
              "exit for the rest at TP2, with the stop moved to the entry price after the partial "
              "fill (and price-unit targets): partial exits (as #365389)."),
    430180: ("1", "Dollar-cost averaging: strategy.entry adds investmentAmount / close on every bar "
              "the position did not shrink (pyramiding 5), with percentage closes of the whole "
              "position; the position is a running sum of orders, so the size path is the "
              "strategy (as #426302)."),
    # ---- FMZ-C, batch C34 (2026-10-16)
    430248: ("1", "Mode 8 is a ladder of strategy.order buys of 1 / 2 / 4 / 8 / 16 units at "
              "successive 5 % bands under the SMA 28 and matching unit sells above it: the "
              "position size path is the strategy (as #426302)."),
    # ---- FMZ-C, batch C35 (2026-10-16)
    430384: ("1", "On the 1-day header chart the entries need hour > 2 and hour < 13 of the bar's "
              "time, which a daily bar never has (its hour is the session start), so the script "
              "as written never trades; the author's M30 / M15 notes are not the declared chart "
              "(no repeatable rule at the source's bar size)."),
    # ---- FMZ-C, batch C36 (2026-10-16)
    430557: ("1", "Exits are four strategy.exit orders with qty_percent = 5 % each at TP1-TP4 plus a "
              "stop and a close_all: partial exits cannot be expressed as one net position's "
              "entry / exit signals (as #365389)."),
    430577: ("1", "An entry on every bar with strategy.exit('Take Profit 1 Long', limit = close x "
              "1.12, qty_percent = 50): a partial exit (as #365389), and the trailing stops are "
              "at 0 % (inert)."),
    430587: ("1", "The signals use request.security(syminfo.tickerid, '5' / '15' / '1', ...) on the "
              "1-hour header chart: resolutions below the chart's, whose value per bar is "
              "undefined (as #427518); the position is also a doubling add ladder."),
    # ---- FMZ-C, batch C37 (2026-10-16)
    430596: ("1", "Positions are built with strategy.order('Rsi long' / 'Rsi short', qty 1), which "
              "adds or removes one unit per signal instead of entering or reversing, each with a "
              "1600-tick bracket: the net position is a running sum of orders (as #426364)."),
    430661: ("1", "Reads the future: Pine v2 request.security(syminfo.tickerid, 'D', hl2) without [1] "
              "behaves as lookahead_on, so on every intraday bar the day's hl2 is the final value "
              "of the current day, not known until the day ends (SURVEY_README request.security "
              "rule, as #427066)."),
    # ---- FMZ-C, batch C38 (2026-10-16)
    430742: ("3", "The signal is a WMA 200 of request.security('BTC_USDT:swap', timeframe.period, "
              "hlc3): a crypto-exchange perpetual contract used as the signal source for the "
              "chart symbol, which the project's single-symbol bars do not carry (as #426832). "
              "Stored in flagged/ (rule C7)."),
    # ---- FMZ-C, batch C39 (2026-10-16)
    430762: ("1", "Dollar-cost averaging: strategy.order('DCA', long, contribution / close) every N "
              "bars by bar_index modulo and chart timeframe; the position is a running sum of "
              "orders, so the size path is the strategy (as #430180)."),
    430765: ("1", "The EMA filters are security(syminfo.tickerid, '15', ema(...)) on the 1-hour "
              "header chart: a 15-minute resolution below the chart's, whose value per bar is "
              "undefined (as #427518)."),
    430776: ("1", "The three exits share the id 'SELL' and are re-issued every bar, the last bound to "
              "entry 'Pump' (as read in #426300): a position opened by the 'Cross' or 'MACD' "
              "entry has no exit and, with no pyramiding, is held for the rest of the data, so "
              "there is no repeatable entry / exit rule (as #368717)."),
    # ---- FMZ-C, batch C40 (2026-10-16)
    430841: ("1", "The ATR stop distance is request.security(syminfo.tickerid, '15', atr(14)) on the "
              "1-hour header chart: a 15-minute resolution below the chart's, whose value per bar "
              "is undefined (as #427518)."),
    430847: ("2", "The oscillator is the distance from the price to the nearest prime number of the "
              "price itself (integer steps of the quote unit): a property of the quote's numeric "
              "scale, not of the market (on fractional prices it is always 0); it cannot be made "
              "generic."),
    430856: ("1", "The signal is crossover(request.security(syminfo.tickerid, '370', close), "
              "request.security(..., '370', open)) on the 1-day header chart: a 370-minute "
              "resolution below the chart's, whose value per bar is undefined (as #427518)."),
    # ---- FMZ-C, batch C41 (2026-10-17)
    430864: ("1", "Each side exits 0.5 % of the position at +9 % (strategy.exit with qty_percent = "
              "0.5) and the rest at +21 %, and the entry is a fixed qty of 10 units: a partial "
              "exit cannot be expressed as one net position's signals (as #365389)."),
    # ---- FMZ-C, batch C42 (2026-10-17)
    430974: ("1", "The take-profit exit closes q1 = 5 % of the position at +1 % (strategy.exit with "
              "qty_percent = q1) and the rest leaves on the SuperTrend exit: a partial exit "
              "cannot be expressed as one net position's signals (as #365389). Its momentum line "
              "also uses ta.vwma (volume, check 8)."),
    430985: ("2", "The second signal is a band of the nearest prime numbers above / below the high "
              "and low (integer steps of the quote unit): a property of the quote's numeric "
              "scale, not of the market (as #430847)."),
    430992: ("1", "A template whose take-profit exit closes 50 % of the position (qty_percent = "
              "takeProfitQuantityPerc) with a trailing order and leaves the rest to a stop: a "
              "partial exit cannot be expressed as one net position's signals (as #365389)."),
    # ---- FMZ-C, batch C43 (2026-10-17)
    431005: ("1", "The long exits in steps: TP1 closes 15 % of the position at +4.5 % (qty_percent = "
              "15), TP2 the rest at +20 %, beside a close-checked exit: a partial exit cannot be "
              "expressed as one net position's signals (as #365389)."),
    431018: ("1", "Positions of 2 units are closed one unit at a time (strategy.exit with qty = 1 at "
              "point targets, the rest with qty = 2): a partial exit cannot be expressed as one "
              "net position's signals (as #365389); the targets are also point distances."),
    # ---- FMZ-C, batch C44 (2026-10-17)
    431270: ("1", "The take-profit orders are strategy.order sells of 25 % of the long (LTP1 / LTP2, "
              "mirror for shorts) on MA colour changes, beside the full entries and a stop: "
              "partial exits cannot be expressed as one net position's signals (as #365389)."),
    # ---- FMZ-C, batch C45 (2026-10-17)
    431419: ("1", "The signal needs HMA rises from request.security(tickerid, '60' / '240', ...) on "
              "the 1-day header chart: resolutions below the chart's, whose value per bar is "
              "undefined (as #427518)."),
    # ---- FMZ-C, batch C47 (2026-10-17)
    431888: ("1", "The TDI lines come from request.security(tickerid, '15', ...) on the 1-day header "
              "chart: a 15-minute resolution below the chart's, whose value per bar is undefined "
              "(as #427518)."),
    431926: ("3", "The Coppock curve is computed on another instrument (security('SPY', 'D', close)): "
              "the strategy trades the chart symbol on the S&P 500 ETF, which the project's bars "
              "do not carry (as #426811)."),
    431958: ("1", "The exit orders are mis-bound: 'S1 SL Exit' names the entry 'Short1', which never "
              "exists, and 'S2 Exit' has no from_entry, so it binds every open entry, longs "
              "included, to a stop above the price; the net effect depends on how the broker "
              "emulator treats a sell stop above the market (as #426455)."),
    # ---- FMZ-C, batch C48 (2026-10-17)
    432078: ("1", "The profit-taking exit compares strategy.openprofit (account currency, with a "
              "fixed qty of 10 units) with 10 % of the initial capital, and shorts are added to "
              "on a further 4.5 % rise: the exit and the position path depend on the order size "
              "(as #426882)."),
    # ---- FMZ-C, batch C50 (2026-10-17)
    432224: ("1", "Both entries are long (strategy.entry('Short', 1, ...) passes long = 1, i.e. true) "
              "and every exit is commented out: after the first signal the position is held for "
              "the rest of the data (as #430030)."),
    # ---- FMZ-C, batch C51 (2026-10-17)
    432308: ("1", "Besides the full exits, strategy.close(qty_percent = 30) takes 30 % of the long "
              "off at a target: a partial exit cannot be expressed as one net position (as "
              "#428066)."),
    432339: ("2", "The signal is a min-max scaling of pow(close x 5, -close): it depends on the "
              "absolute price level and underflows to a constant for prices above a few hundred "
              "(BTC on the header), so scaleMinimax divides 0 by 0; not generic across "
              "instruments."),
    432341: ("1", "The signal averages request.security(tickerid, '1' / '5' / '15' / '30' / '45' / "
              "'60', vwma(rsi, 15)) on the 1-hour header chart: resolutions below the chart's, "
              "whose value per bar is undefined (as #430587); it also weights by volume (vwma)."),
    # ---- FMZ-C, batch C52 (2026-10-17)
    432350: ("3", "The signal is the RSI of request.security('CRYPTOCAP:TOTAL2', '120', close[1]) (a "
              "crypto market-cap index) divided by the chart's RSI: crypto-market index data the "
              "project's single-symbol bars do not carry (as #430742). Stored in flagged/ (rule "
              "C7)."),
    432351: ("2", "A fixed grid: ten buy levels 1 % apart below a hard-coded starting price of 40,500 "
              "and their sell levels, each its own entry id: absolute price levels (and a ladder "
              "of stacked entries), not generic."),
    432362: ("1", "The trend filters are request.security(syminfo.tickerid, '1' / '5' / '15' / '30' / "
              "'60', ema(...)) on the 1-day header chart: resolutions below the chart's, whose "
              "value per bar is undefined (as #430587)."),
    432363: ("1", "Every entry needs strategy.equity >= ema(strategy.equity, 40): an equity-curve "
              "filter on the account's own P&L, which depends on the order size and the "
              "commission (as #427139)."),
    432420: ("1", "The only exit is strategy.exit('Exit', limit = close) placed when the close "
              "condition holds: a resting limit at the signal bar's close, filled inside the next "
              "bar at its own price (as #427119)."),
    # ---- FMZ-C, batch C53 (2026-10-17)
    432781: ("1", "The only exit is strategy.close('long', qty_percent = 20): a partial exit that "
              "takes 20 % of the position off at a time cannot be expressed as one net position "
              "(as #428066)."),
    # ---- FMZ-C, batch C54 (2026-10-17)
    432807: ("1", "Reads the future: the HTF high / low are security(tickerid, '3M', high[0] / "
              "low[0], lookahead = barmerge.lookahead_on) (the lookahead input is true): without "
              "[1], lookahead_on hands every daily bar the final high and low of its three-month "
              "bar (as #430661)."),
    # ---- FMZ-C, batch C55 (2026-10-17)
    432894: ("1", "Positions are built with strategy.order('Long Signal' / 'Short Signal'), which "
              "adds or removes one unit per signal instead of entering or reversing: the position "
              "path depends on the order size (as #430596)."),
    432900: ("1", "The MACD filters are request.security(syminfo.tickerid, '5' / '15' / '60', "
              "macdLine) on the 1-day header chart: resolutions below the chart's, whose value "
              "per bar is undefined (as #430587)."),
    # ---- FMZ-C, batch C56 (2026-10-17)
    432974: ("3", "The alpha and beta are measured against request.security('BTC_USDT:swap', "
              "timeframe.period, close), a crypto-exchange perpetual contract used as the "
              "benchmark for the chart symbol, which the project's single-symbol bars do not "
              "carry (as #430742). Stored in flagged/ (rule C7)."),
    432988: ("1", "Reads the future: Pine v2 request.security(syminfo.tickerid, '1440', high) without "
              "[1] behaves as lookahead_on, so on every 45-minute bar the oscillator uses the "
              "final high of the current day, not known until the day ends (SURVEY_README "
              "request.security rule, as #430661)."),
    432992: ("1", "pyramiding = 4: further entries are added while the price is below the "
              "averaged-down level, and the stop, target and add levels are all measured from "
              "strategy.position_avg_price of the stacked units (a pyramided ladder, as #426570)."),
    # ---- FMZ-C, batch C57 (2026-10-17)
    433015: ("1", "pyramiding = 10: the long and short signals add further units only while the close "
              "is beyond strategy.position_avg_price of the stacked position (useus), so the "
              "signals depend on the averaged price of the ladder (a pyramided ladder, as "
              "#426570)."),
    # ---- FMZ-C, batch C58 (2026-10-17)
    433074: ("1", "The signals compare the close with request.security(syminfo.tickerid, '1', ...) "
              "and request.security(syminfo.tickerid, '5', ...) supertrends on the 1-hour header "
              "chart: resolutions below the chart's, whose value per bar is undefined (as "
              "#430587)."),
    433108: ("1", "Entries are strategy.order('多(buy)' / '空(sell)') calls on four grid levels with no "
              "pyramiding limit, so each level touched adds a unit and an opposite order reduces "
              "rather than reverses: the position path depends on the order sizes (as #430596)."),
    # ---- FMZ-C, batch C59 (2026-10-17)
    433125: ("1", "After the minimum hold the reverse-order flag is armed on every bar (unless the "
              "over-band test clears it), so the opposite entry fires on the bar after the "
              "position goes flat, which is usually when the ratcheting EMA - 2 ATR stop order "
              "fills inside a bar: the entries depend on an intrabar stop fill the house trail "
              "cannot express."),
    433400: ("1", "Entries are allowed only while strategy.netprofit < 150000 (a profit target of the "
              "account), so the signals depend on the position size and the P&L path (as "
              "#427139); the bracket is 3 / 8 ticks."),
    # ---- FMZ-C, batch C60 (2026-10-17)
    433448: ("1", "The trend filter reads request.security(syminfo.tickerid, '120', ...) on the 1-day "
              "header chart: a resolution below the chart's, whose value per bar is undefined (as "
              "#430587); the bracket is also in ticks."),
    # ---- FMZ-C, batch C61 (2026-10-17)
    433521: ("1", "The only exit is strategy.exit(profit = close x 1.20, loss = close x 0.95) in "
              "ticks, placed only once the exit condition fires (12 % / 9.5 % at BTC's 0.1 tick, "
              "a different size on any other tick): a bracket armed by a later signal, from the "
              "entry price, which the stops (live from the entry) cannot express, and whose size "
              "depends on the symbol's tick."),
    433539: ("1", "The take-profits close 3/4 or 1/2 of the position at four RSI levels "
              "(strategy.close with qty), with pyramiding 2: partial exits cannot be expressed as "
              "one net position's signals (as #365389)."),
    433541: ("1", "strategy.order entries with a 50 % partial exit at half the target and the rest at "
              "the full target (qty_percent): partial exits of the net position (as #365389)."),
    # ---- FMZ-C, batch C62 (2026-10-17)
    433565: ("1", "The signals are the candle colours of request.security(syminfo.tickerid, '3' / '5' "
              "/ '15' / '30', open / close) on the 1-hour header chart: resolutions below the "
              "chart's, whose value per bar is undefined (as #430587)."),
    433581: ("1", "Three long entries ('long_D', 'long_W', 'long_M', one unit each, pyramiding 3) "
              "open and close on their own daily, weekly and monthly P-signals: each unit leaves "
              "on its own exit, i.e. partial exits of the net position (as #426781)."),
    433588: ("1", "pyramiding 5 with trend entries allowed only while the close is beyond "
              "strategy.position_avg_price of the stacked position: the signals depend on the "
              "averaged price of the ladder (as #426570, #433015)."),
    # ---- FMZ-C, batch C63 (2026-10-17)
    433904: ("1", "Two long entry ids with different exits: the pullback entry's target and trailing "
              "stop are re-placed every bar a fixed number of ticks around the latest close, and "
              "the initial entry's exit is a resting stop at the close of the exit-signal bar; "
              "the exit rule depends on which id opened the position, with moving tick levels, "
              "which one module's signals and stops cannot express."),
    433916: ("1", "No exit: strategy.exit('Sell', 'Buy', bar_index[30]) passes bar_index[30] as a "
              "quantity with no price or time level, so the first entry is held to the end of the "
              "data, a single buy-and-hold trade (as #428718)."),
    433918: ("1", "The exit order 'Close Long' is a 2000-tick target outside 10:00-16:00 and is "
              "replaced by a 500-tick stop inside that window (same id, re-issued by the clock), "
              "so the bracket of an open trade switches by time of day, which fixed per-trade "
              "stops cannot express."),
    433920: ("1", "Grid ladder: fifteen entry ids on levels around an SMA 300, each bought below its "
              "level and closed above the next one; the position is a sum of grid units (as "
              "#430596)."),
    433932: ("1", "Four exits close 25 % / 25 % / 25 % / the rest at 1 / 2 / 3 / 4 % (qty_percent): "
              "partial exits of the net position (as #365389)."),
    # ---- FMZ-C, batch C64 (2026-10-17)
    433951: ("1", "pyramiding 3 with adds allowed only while the close is below "
              "strategy.position_avg_price minus a sum of ATRs (an averaging-down ladder keyed on "
              "the averaged price, as #426570), and the only exit is a resting limit at the "
              "signal close (as #427119)."),
    434164: ("1", "pyramiding 15 cash adds, and the strategy's sell signal requires "
              "strategy.openprofit / (position_avg_price x position_size) above a threshold, so "
              "the exit depends on the averaged price and P&L of the stacked units (as #426570); "
              "the trailing stop arms at the averaged price + 15 %."),
    # ---- FMZ-C, batch C65 (2026-10-17)
    434185: ("1", "Grid ladder: pyramiding 1000 with up to 15 buy and sell levels around a monthly "
              "pivot, each buying a cash quantity and selling a contract count, with the levels "
              "re-anchored on the average price of the stacked buys; the position is a sum of "
              "grid units (as #430596)."),
    # ---- FMZ-C, batch C68 (2026-10-17)
    434485: ("1", "Reads the future: Pine v2 security(syminfo.tickerid, '180', close) without [1] "
              "behaves as lookahead_on, so on every 5-minute bar the 3-hour close is the final "
              "close of the current 3-hour bar, not known until it ends (SURVEY_README "
              "request.security rule, as #427066)."),
    434549: ("2", "The second signal is the distance from the close to the nearest prime number of "
              "the price itself (integer steps of the quote unit): a property of the quote's "
              "numeric scale, not of the market; it cannot be made generic (as #430847)."),
    434575: ("1", "DCA ladder: up to 5 safety orders averaging down at thresholds keyed on the first "
              "entry price, with growing volumes, and a take profit on the averaged position "
              "price; the position is a sum of grid units (as #426570)."),
    # ---- FMZ-C, batch C69 (2026-10-17)
    434594: ("1", "The '5-minute EMA' is an ema() called only on bars whose bar_index is a multiple "
              "of 5, so its value depends on how many bars the chart holds before the first trade "
              "(the phase of the count), and the exits are a 7-tick target with a stop re-placed "
              "every bar at the EMA 50 (above the price for some longs, which fills at once); the "
              "signal is not defined independently of the chart's start."),
    434600: ("1", "Coin flip: the direction is coinLabel = random(1, 10) and the gap between flips is "
              "round(random(3, 25)), new draws each run; no deterministic signal to port (as "
              "#426621)."),
    # ---- FMZ-C, batch C70 (2026-10-17)
    434679: ("1", "Partial exits: two take-profit orders close 50 % and then the rest of the position "
              "(qty_percent 50 / 100), with levels re-placed every bar from the current high / "
              "low (as #365389)."),
    # ---- FMZ-C, batch C71 (2026-10-17)
    434707: ("1", "Pyramiding 3 with adds when the close is under the averaged position price, and a "
              "stop and exits keyed on that averaged price; the position is a sum of units (as "
              "#426570)."),
    434936: ("1", "Partial exits: the long is scaled out with limit orders for 33.3 %, then 50 %, "
              "then the rest (qty_percent), driven by counters of the script's own take-profit "
              "levels (as #365389)."),
    # ---- FMZ-C, batch C73 (2026-10-17)
    435081: ("3", "The signals are computed on request.security('BTC_USDT:swap', timeframe.period, "
              "close / open / high / low) (\"correlation candles\" on by default): a "
              "crypto-exchange perpetual contract used as the signal source for the chart symbol "
              "(as #430742). Stored in flagged/ (rule C7)."),
    435088: ("1", "The momentum values are request.security(syminfo.tickerid, '180', rsi(...)) on the "
              "daily header chart: a 180-minute resolution below the chart's, whose value per "
              "daily bar is undefined (as #427518)."),
    # ---- FMZ-C, batch C74 (2026-10-17)
    435138: ("1", "The trend lines are request.security(syminfo.tickerid, '15' / '30' / '60' / '120', "
              "...) on the 4-hour header chart: resolutions below the chart's, whose value per "
              "4-hour bar is undefined (as #427518)."),
    # ---- FMZ-C, batch C75 (2026-10-18)
    435153: ("1", "Matrix ladder: the position is resized up and down around grid levels 2 % apart "
              "(increase / decrease / reset orders keyed on the entry price and the level count); "
              "the position is a sum of grid units (as #430596)."),
    435154: ("2", "The entries need close > entrybar, where entrybar is a var set to the first bar's "
              "close and never updated: a fixed price level set by where the chart's data starts."),
    # ---- FMZ-C, batch C76 (2026-10-18)
    435256: ("2", "The entries need the close divided by 4 to leave no remainder (close % 4 == 0 by "
              "default): an exact test of the price against a multiple of a price-unit divisor, "
              "so the trigger is a fixed price level grid that means something different on every "
              "instrument and at every price scale; the stops are also built from valuewhen "
              "levels of the entry bar."),
    435262: ("2", "The stop level is set ABOVE the entry close (close x (1 + 0.5 %)) and kept in a "
              "var; the exits close the long whenever the close is under that level (true at once "
              "and on every later bar until the next signal) or at or over a target level, and "
              "strategy.exit is handed the price levels as loss / profit tick distances: the "
              "rules compare the close with price levels carried from the last signal and, as "
              "written, open and close on the same open or never hold, so no signal rule can be "
              "separated from the price-level bookkeeping."),
    # ---- FMZ-C, batch C77 (2026-10-18)
    435275: ("1", "The relative-strength half compares the chart symbol with a second symbol read "
              "through security(b, timeframe.period, close) (the input default is the BTC swap "
              "itself, a ratio of 1.0) and tests the ratio's 10-bar average against price-ratio "
              "bands 0.9988 / 0.9960 / 0.9975: a two-instrument pair signal, outside the "
              "single-instrument interface."),
    435278: ("1", "The orders read the 4-hour MACD histogram through security(syminfo.tickerid, "
              "'240', hist, gaps_off, lookahead_on) with 'Use The Future?' true by default, so on "
              "the 5-minute chart each 4-hour bar's final histogram is seen from its first bar: "
              "it reads the future (SURVEY_README request.security rule); the other branch is the "
              "same logic without lookahead and is only a switch."),
    # ---- FMZ-C, batch C78 (2026-10-18)
    435473: ("1", "The entry opens 2 units and the exits are two separate 1-unit partial closes "
              "(strategy.close with qty = 1 on a cross under the ema of H4 and another on the ema "
              "of L3): the position is half-closed on the first exit signal and the rest on the "
              "second, a scale-out the all-in / all-out signal interface cannot express; the ATR "
              "trailing level is only plotted."),
    435486: ("2", "Entries need a 09:35-14:30 session test (time(timeframe.period, session)) on the "
              "DAILY chart of the backtest header, where the bar's own time is not inside the "
              "session, so the entry condition is a clock-time filter that is undefined (probably "
              "never true) on the chart it was tested on; the exit is a stop re-sent each bar at "
              "close - 10 ATR (a close-relative level, not a ratchet) and the 14:57 end-of-day "
              "close never occurs on daily bars."),
    # ---- FMZ-C, batch C79 (2026-10-18)
    435511: ("1", "The exits are four partial exits of the position (strategy.exit with qty_percent "
              "25 / 25 / 25 and the rest at profit levels 2 / 4 / 6 / 8 % of the average price, "
              "tick-converted) and the rule reads a weekly RSI of a held week-open close through "
              "time('W'): a scale-out in four parts that the all-in / all-out signal interface "
              "cannot express."),
    # ---- FMZ-C, batch C80 (2026-10-18)
    435721: ("1", "The default Trend mode adds martingale orders (strategy.order Long2 / Short2 with "
              "qty = last size x 2 once the price has moved a point range against the entry), "
              "takes profit when strategy.openprofit reaches a currency amount (tp_pnl = 1 "
              "dollar, close_all) and sizes the percent stops by ticks: the exits and adds depend "
              "on the position size and its dollar profit, which the all-in signal interface "
              "cannot express."),
    # ---- FMZ-C, batch C81 (2026-10-18)
    435725: ("1", "The long and short each carry strategy.exit with qty_percent = 50 at a take-profit "
              "level of the channel line plus / minus 15 % (a scale-out of half the position) "
              "while the channel line itself is the highest / lowest of the monthly OPEN taken "
              "over 21 chart bars: the half-position exit cannot be expressed by the all-in / "
              "all-out signal interface."),
    435766: ("1", "Positions are built and cut by quantity: strategy.order buys 25 % of equity on "
              "each MACD-cross-after-oversold signal (pyramiding 10) and sells one third of the "
              "open position size (qty = posSize / 3) on each cross after overbought: scale-in "
              "and a stepped scale-out that the all-in / all-out signal interface cannot express."),
    435773: ("1", "Two take-profit exits take 10 % and 50 % of the position at +1 % and +5 % "
              "(qty_percent), the rest following the ZLEMA slope exit: partial exits (a "
              "scale-out) that the all-in / all-out signal interface cannot express."),
    435831: ("1", "The long's stop is an exit order armed only when the short condition appears "
              "during the trade (strategy.exit with stop = a ratcheted level computed from every "
              "bar's close, re-sent only on those bars, and enterShort needs strategy.openprofit "
              "> 0): an exit placed mid-trade at a level that depends on the position's open "
              "profit, outside the entry-fill bracket the stop interface supports."),
    # ---- FMZ-C, batch C82 (2026-10-18)
    435839: ("1", "Each entry also sends strategy.exit with qty_percent = 10 at a profit target (a 10 "
              "% partial take profit; the 15 % and 20 % tiers are declared and unused) and the "
              "stop is a custom ratchet on bar closes: a partial exit that the all-in / all-out "
              "signal interface cannot express."),
    435845: ("1", "A 3Commas dollar-cost-averaging bot: strategy.order adds safety orders "
              "(volume-scaled quantities, up to a set count) on deviations below the average "
              "price while a base order is open, with take profit and stop on the average of the "
              "combined position: a ladder of adds whose size depends on the position, which the "
              "all-in / all-out signal interface cannot express."),
    435850: ("1", "The moving averages are read through security(tickerid, '5D', sma(hlc3, 16), "
              "gaps_off, lookahead_on) and the matching EMA with lookahead_on and no [1]: on "
              "historical bars the 5-day values are seen from the first bar of the 5-day period, "
              "so the rule reads the future (SURVEY_README request.security rule)."),
    # ---- FMZ-C, batch C84 (2026-10-18)
    435964: ("1", "The exit orders are re-sent every bar with levels computed from the CURRENT bar's "
              "extremes (sl = high + 50 ticks, tp = low - 100 ticks for a short; the mirror for a "
              "long): a moving bracket that follows each new bar rather than a level fixed at the "
              "entry fill, in tick units, which the stop interface (levels fixed at the entry "
              "fill or a declared trail) cannot express."),
    # ---- FMZ-C, batch C85 (2026-10-18)
    436093: ("2", "The entry needs the close over a fixed RESISTANCE price (200) and the exit a close "
              "under a fixed SUPPORT price (100): price levels typed in as inputs, which mean "
              "something different at every price scale and on every instrument."),
    436096: ("1", "The orders are strategy.order calls with a quantity of 1 in each direction (a "
              "'buy' and a 'sel' order, each with its own tick bracket): strategy.order adds to "
              "and nets against the open position instead of reversing it, so a sell order while "
              "long only takes the position to flat and repeated signals stack units: "
              "net-position arithmetic that the all-in / all-out signal interface cannot express."),
    # ---- FMZ-C, batch C86 (2026-10-18)
    436142: ("1", "The signals combine daily and 15-minute request.security reads inside while loops "
              "with break (high[_bar] / low[_bar] of several earlier bars, including the index 0 "
              "bar which on the 1-minute chart is the still-forming day), choosing which earlier "
              "range the previous close broke out of; which value each read returns on a "
              "historical bar depends on the runtime's handling of in-progress higher bars, and "
              "the stop sits at a structural 15-minute low."),
    # ---- FMZ-C, batch C87 (2026-10-18)
    436217: ("1", "The entry filter reads atr(14) through security(tickerid, 'D', ...) and then a "
              "moving average of the percent ATR through a second security call whose expression "
              "is the variable atrp, itself built from the first security result and the chart "
              "close: a nested request.security whose evaluation context (daily versus chart "
              "bars) depends on how the runtime resolves the inner variable; the take profit "
              "(3000 %) and the 50 % trail are inert."),
    # ---- FMZ-C, batch C88 (2026-10-18)
    436245: ("1", "A dollar-cost-averaging emulator: after the base order it adds safety orders "
              "(strategy.entry with growing cash quantities, volume scale 2, up to 10 levels, "
              "pyramiding 99) every time the price falls a step under the first entry, and closes "
              "everything at +1.5 % of the average price: a ladder of adds whose size depends on "
              "the position, which the all-in / all-out signal interface cannot express."),
    436475: ("2", "Every trade is gated by a 03:00-11:00 session test (time(timeframe.period, "
              "session) != 0) on the DAILY chart of the backtest header, where a bar's own time "
              "is not inside the session, so the condition is a clock-time filter that is "
              "undefined (probably never true) on the chart it was tested on; close_all is also "
              "sent whenever the session is false."),
    # ---- FMZ-C, batch C89 (2026-10-18)
    436482: ("1", "A flag-breakout finder whose only exit is strategy.exit with stop=supertrend: a "
              "stop level that moves every bar with the Supertrend line (re-sent each bar), a "
              "trailing level that is not a fraction of the fill price and cannot be expressed by "
              "the house stop interface; the flag and pole detection also depends on many "
              "persistent var indices tied to bar positions."),
    436483: ("2", "The long's stop sits above its own entry price and the limit target also sits "
              "above it, so with the fill at the next open the stop and the limit are both "
              "already crossed: trades open and close at the same open, the strategy has no "
              "defined result as a signal system."),
    436515: ("1", "A 50/50 dynamic balancing strategy that sends strategy.order calls to rebalance "
              "the position toward half the equity at each step: the size changes every bar "
              "depending on the position and equity, which the all-in / all-out signal interface "
              "cannot express."),
    # ---- FMZ-C, batch C91 (2026-10-18)
    436524: ("1", "An RSI-crossing strategy with pyramiding 5 whose exits are two strategy.exit "
              "orders for half of the position each (qty_percent 50 / 50, targets +3 % and +5 %, "
              "stop 5 %), and entries that stack up to five units; the position is built and "
              "unwound in parts, which the all-in / all-out signal interface cannot express."),
    436528: ("1", "Orders are sent with strategy.order (one unit BUY after a bullish crossing above "
              "the 100-bar average, one unit SELL after a bearish crossing below it), not "
              "strategy.entry: each order adds to or subtracts from the net position without any "
              "direction logic, so a filtered-out crossing leaves the net at 0, +1, -1, -2 ...; "
              "the unit-by-unit accumulation cannot be expressed as flat / long / short signals."),
    # ---- FMZ-C, batch C93 (2026-10-18)
    436603: ("2", "The stop and the target are written as strategy.exit(loss = low - 5.70, profit = "
              "close + 11.40): price levels of one instrument passed as TICK counts, so the real "
              "distances are (price - 5.7) x tick size, an instrument-specific and nearly "
              "meaningless bracket (about 10 % at a 0.1 tick on a 40000 price, about 1 % at "
              "0.01); the author's intended USD levels are tied to a single price scale, so there "
              "is no generic reading."),
    # ---- FMZ-C, batch C94 (2026-10-18)
    436653: ("1", "A leverage and margin-call management script: the position size is a leverage "
              "multiple of one unit, entries are blocked and strategy.close_all is sent when "
              "strategy.equity falls to a margin value (25000), and the trigger reads the high / "
              "low of the 4-hour bar through a lower-timeframe security call from a daily chart; "
              "the margin rule depends on the account equity, which the signal interface cannot "
              "see."),
    # ---- FMZ-C, batch C95 (2026-10-21)
    436659: ("2", "Every signal is computed on security(sym, '', close / high / low) where sym is an "
              "input whose default is BINANCE:BTCUSDT: a named external instrument used as the "
              "signal source for whatever chart is traded (SURVEY_README: another symbol -> "
              "criterion 2), with the entries sized from strategy.equity."),
    436773: ("2", "The stop, the target and the break-even exit are written as strategy.exit(loss = "
              "close x 0.99, profit = close x 1.02) and exit(loss = close x 1.01): price levels "
              "passed as TICK counts, so the real distances are (price x 0.99) x tick size, an "
              "instrument-specific and nearly meaningless bracket (about 10 % at a 0.1 tick on a "
              "42000 price, about 1 % at 0.01); these are the only exits, so there is no generic "
              "reading (as #436603)."),
    # ---- FMZ-C, batch C96 (2026-10-21)
    436776: ("1", "An intraday square-off script run on the daily header chart: entries are sent only "
              "while barInSession('0915-1455') is true, and every daily bar opens at its session "
              "start (00:00 UTC on the backtest exchange, 17:00 New York on broker days), outside "
              "09:15-14:55, so no order can ever be sent and the square-off closes nothing; the "
              "bracket is also computed from strategy.position_avg_price before the entry fills "
              "(na when flat)."),
    436859: ("1", "Reads the future: Pine v2 request.security(syminfo.tickerid, 'D' / '5D' / '15D' / "
              "'45D', open / close) without [1] behaves as lookahead_on, so on every 1-hour bar "
              "the candle colours use the final close of the current day, 5-day, 15-day and "
              "45-day bars, not known until they end (SURVEY_README request.security rule, as "
              "#432988)."),
    # ---- FMZ-C, batch C98 (2026-10-21)
    437027: ("1", "Each trade is closed in two halves: strategy.exit(qty_percent = 50) at TP 1 (6 %) "
              "and the rest at TP 2 (12 %), both with a 3 % stop, and once the high reaches TP 1 "
              "the second half's stop is cancelled and re-placed at the entry price; partial "
              "exits and a stop moved after a partial fill are outside the single-position signal "
              "interface (as #436524)."),
    # ---- FMZ-C, batch C99 (2026-10-21)
    437048: ("2", "The only exits are strategy.exit(profit = 0.02 x close, loss = 0.01 x close): "
              "percents of the close in PRICE units passed as TICK counts, so the real distances "
              "are 2 % / 1 % of the price times the tick size (0.2 % / 0.1 % at a 0.1 tick on "
              "BTC, 2 % / 1 % at a 1.0 tick), an instrument-specific bracket with no generic "
              "reading (as #436603, #436773)."),
    # ---- FMZ-C, batch C100 (2026-10-21)
    437411: ("1", "The only stop is strategy.exit(loss = 0.001 x lastDayOpen x tradeSize) with "
              "tradeSize = strategy.equity / 3500: the stop distance in ticks grows with the "
              "account equity, so the exit depends on the account state, which the signal "
              "interface cannot see (as #436653's equity-dependent rule); the order size is also "
              "taken from the equity."),
    437487: ("1", "Entries require strategy.position_size == 0, and the only exits are an exit(limit, "
              "stop) whose stop ratchets every bar on max(low - ATR(5), previous stop) (a trail "
              "on lows the house trail cannot express) together with a limit set from that stop's "
              "distance: whether the strategy is flat, and so whether it may enter, depends on an "
              "exit the port cannot model; the candle and midline tests are also in forex pips (x "
              "0.0001) on a BTC chart."),
    # ---- FMZ-C, batch C102 (2026-10-21)
    437544: ("1", "An intraday buy-at-the-close script on the daily header chart: the buy window "
              "time(period, '1429-1500') and the sell window '0925-0935' never contain a daily "
              "bar's open (00:00 UTC on the backtest exchange, 17:00 New York on broker days), so "
              "no entry is ever sent (as #436776)."),
    437557: ("1", "The take profit is strategy.exit(profit = 8, qty_percent = 50), a half-position "
              "exit, and the remainder closes on an SMA cross only on the bar the take profit is "
              "placed (quantityRemainder resets every bar): partial exits are outside the "
              "single-position signal interface (as #436524)."),
    # ---- FMZ-C, batch C104 (2026-10-21)
    437677: ("2", "Apart from the reversing entries, the exits are strategy.exit(loss = close - 1 % x "
              "ATR, profit = close + 1 % x ATR): price LEVELS passed as TICK counts, so the real "
              "distances are about the whole price times the tick size (about 10 % at a 0.1 tick "
              "on a 42000 price), an instrument-specific bracket with no generic reading (as "
              "#436603, #436773)."),
    437738: ("2", "The exits are strategy.exit(loss = close - 1 ATR, profit = close + 3 ATR): price "
              "LEVELS passed as TICK counts, so the real distances are about the whole price "
              "times the tick size, an instrument-specific bracket with no generic reading (as "
              "#436603, #437677)."),
    # ---- FMZ-C, batch C106 (2026-10-21)
    437787: ("2", "The only exits are strategy.exit(loss = close, profit = close + 2 x ATR / close + "
              "3 x ATR): price LEVELS passed as TICK distances, so the real distances are the "
              "price itself times the tick size (an instrument-specific bracket with no generic "
              "reading, as #437048), and the two exits close 50 % and 100 % of the position "
              "(partial exits, criterion 1, as #436524). The Blackflag FTS value is always 50 (up "
              "and down are the same sum), so its filter is constant."),
    # ---- FMZ-C, batch C107 (2026-10-22)
    438016: ("1", "The only exits are three take-profit limits closing 25 %, 50 % and 25 % of the "
              "position (strategy.exit qty_percent): partial exits, which the house engine cannot "
              "hold (one position, all-in or all-out; as #436524)."),
    438017: ("1", "pastLow / pastHigh = request.security(tickerid, \"D\", low / high, lookahead = "
              "barmerge.lookahead_on) with the [1] applied on the 1-hour chart, not inside the "
              "call: from the second hour of a day the value is that same day's final low / high, "
              "known only at the day's end (look-ahead)."),
    # ---- FMZ-C, batch C108 (2026-10-22)
    438025: ("2", "The bands are the nearest prime numbers above the high and below the low (integer "
              "steps of the quote unit; on fractional prices the price itself): a property of the "
              "quote's numeric scale, not of the market (as #430985, #430847)."),
    # ---- FMZ-C, batch C111 (2026-10-22)
    438481: ("1", "Exits close half and three quarters of the position on RSI crossings "
              "(strategy.close with qty = position_size x 1/2, x 3/4): partial exits, which the "
              "house engine cannot hold (as #436524)."),
    438495: ("1", "monthclose / weekclose / dayclose = request.security(tickerid, 'M' / 'W' / 'D', "
              "close, lookahead = barmerge.lookahead_on): on a daily chart the month's and week's "
              "FINAL close is used from their first bar (look-ahead); the entry requires "
              "monthclose > monthopen and weekclose > weekopen."),
    # ---- FMZ-C, batch C119 (2026-10-22)
    439275: ("2", "The only stop is strategy.exit(loss = trailStop) with trailStop = close - 2 x "
              "ATR(14): a price LEVEL passed as a TICK distance, so the real distance is the "
              "price itself times the tick size (about 10 % of the price at a 0.1 tick on BTC, "
              "the whole price at a 1.0 tick), an instrument-specific bracket with no generic "
              "reading (as #437048, #437787). The daily supply / demand zones only colour the "
              "background."),
    # ---- FMZ-C, batch C120 (2026-10-22)
    439360: ("1", "Every trade is closed by two exits: exit1 (qty_percent = 1, at SL1 / TP1) closes 1 "
              "% of the position and exit2 the rest at SL2 / TP2 with a stop that moves after "
              "TP1: partial exits (criterion 1, as #436524). The pip distance is also an input "
              "times ten ticks."),
    439361: ("2", "Apart from the reversing entries, the exits are strategy.exit(loss = close - 4 x "
              "0.0001, profit = close + 8.4 x 0.0001): price LEVELS passed as TICK counts, so the "
              "real distances are about the whole price times the tick size, an "
              "instrument-specific bracket with no generic reading (as #437677, #437048). The "
              "entry tests close + 9 > 0 and close - 9 < 0 are price-unit thresholds (shorts only "
              "below a price of 9)."),
    439363: ("1", "Every signal reads request.security(\"M\" / \"1D\", [...], lookahead_on) on a daily "
              "chart: the monthly Heikin-Ashi values come from the month still in progress (its "
              "final close), so the rules use the future (criterion 1, as #438495)."),
    439364: ("2", "Apart from the reversing entries, the exits are strategy.exit(loss = close x 1 / "
              "100, profit = close x 1 / 100): percents of the close in PRICE units passed as "
              "TICK counts, so the real distances are 1 % of the price times the tick size (0.1 % "
              "at a 0.1 tick on BTC, 1 % at a 1.0 tick), an instrument-specific bracket with no "
              "generic reading (as #437048, #437677)."),
    439366: ("2", "The only exit is strategy.exit(loss = stopLossLevel) with stopLossLevel = "
              "lowest(low, 2)[1] - ATR(14): a price LEVEL passed as a TICK distance, so the real "
              "distance is about the whole price times the tick size, an instrument-specific stop "
              "with no generic reading (as #437787, #439275); strategy.close(\"Sell\") names an id "
              "that is never entered."),
    # ---- FMZ-C, batch C121 (2026-10-22)
    439607: ("1", "The only exit is strategy.close(\"Long Position\", qty_percent = 50): every close "
              "takes half of the position, so trades end in partial exits (criterion 1, as "
              "#436524)."),
    439610: ("2", "The take-profit exit trails with trail_price = 0.03 (a price LEVEL, met at once) "
              "and trail_offset = 0.03 TICKS: the intended 3 % trail is passed as a tick count, "
              "so the real trail is 0.03 x the tick size behind the best price, an "
              "instrument-specific trail with no generic reading (as #437048); the 5 % stop and "
              "10 % target are re-sent every bar from the current close."),
    # ---- FMZ-C, batch C123 (2026-10-22)
    439709: ("1", "Positions are built with strategy.order('BUY' / 'SELL'), which adds or removes "
              "units instead of entering or reversing, and both orders and the close_all are "
              "gated on strategy.openprofit in account currency (> -1 to trade, > 3000 to close "
              "all) with a cash order size: the net position and the exits depend on the order "
              "size (as #430596, #432078)."),
    # ---- FMZ-C, batch C124 (2026-10-22)
    439752: ("1", "On the 1-day header chart every entry needs istradingsession = time('1', "
              "'0800-1600') to be defined, and a daily bar opens outside that session (its time "
              "is the session start), so the script as written never enters; an intraday reading "
              "is not the declared chart (as #430384)."),
    439753: ("1", "As written (Long, 'Grid - reentry', every filter and exit '---'), the grid level "
              "starts at 0, so the second bar of the data already moves it up and enters; no exit "
              "is ever sent and pyramiding blocks further entries: a buy-and-hold from the start "
              "of whatever data is loaded, with no repeatable rule at the source's settings (as "
              "#430384). The 500 base-currency grid gap is also an instrument-specific price "
              "distance."),
    # ---- FMZ-C, batch C125 (2026-10-22)
    439844: ("2", "Apart from the reversing entries, the exits are strategy.exit(profit = close x "
              "0.15, loss = close x 0.20): percents of the close in PRICE units passed as TICK "
              "counts, so the real distances are 15 % / 20 % of the price times the tick size "
              "(1.5 % / 2 % at a 0.1 tick on BTC, 15 % / 20 % at a 1.0 tick), an "
              "instrument-specific bracket with no generic reading (as #437048, #437677)."),
    # ---- FMZ-C, batch C126 (2026-10-22)
    439881: ("1", "The entries are a pseudo-random sequence (rd_number_entry = 16708 x previous mod "
              "2147483647 mod 17, counted from the first bar, so it depends on where the data "
              "starts) and each trade is three entries closed one by one at 1 / 2 / 3 ATR targets "
              "(partial exits, criterion 1, as #436524); the time-based exit test (== 22 of a "
              "value mod 17) can never pass."),
    439883: ("2", "Apart from the reversing entries, the only stop is strategy.exit(loss = "
              "stop_loss_level) with stop_loss_level = close -/+ 1.5 ATR: a price LEVEL passed as "
              "a TICK distance, so the real distance is about the whole price times the tick "
              "size, an instrument-specific stop with no generic reading (as #437677, #439275)."),
    # ---- FMZ-C, batch C127 (2026-10-22)
    439950: ("1", "pyramiding 2 with an 'Add' entry below the average price and "
              "strategy.close(qty_percent = 20) partial profit-taking when the RSI crosses under "
              "80: the position path and the exits are partial (criterion 1, as #436524)."),
    439958: ("1", "pyramiding = 1000 with a 1-unit buy on every RSI 2 crossover and no exit until a "
              "fixed end date (30 Nov 2023), after which every bar closes: an accumulation whose "
              "size path is the strategy (as #430762, #430248)."),
    # ---- FMZ-C, batch C128 (2026-10-22)
    439974: ("1", "Both MA series are read through security(tickerid, '7D' (7 x the chart period), "
              "..., lookahead = barmerge.lookahead_on): on the daily chart the 7-day values are "
              "seen from the first bar of the 7-day period, so every crossing uses the future "
              "(criterion 1, as #438495)."),
    # ---- FMZ-C, batch C129 (2026-10-22)
    440058: ("1", "A leveraged martingale: after the first buy, each 1 % drop adds a 'Double Long' "
              "entry sized trade size x leverage x 2^n up to 10 times, and close_all fires on a "
              "take-profit of the size-weighted average price net of fees: the position size path "
              "is the strategy (as #435721)."),
    # ---- FMZ-C, batch C130 (2026-10-22)
    440084: ("3", "Every signal is the RSI 7 of request.security('BTC_USDT:swap', '', open) (the "
              "author's Bitfinex shorts series, replaced by a crypto-exchange perpetual): a "
              "separate instrument used as the signal source for the chart symbol, which the "
              "project's single-symbol bars do not carry (as #430742). Stored in flagged/ (rule "
              "C7)."),
    440085: ("1", "Each side has three take-profit exits closing 30 % of the position each "
              "(qty_percent = 30 at 1 / 2 / 6 units of the average price): partial exits "
              "(criterion 1, as #436524)."),
    # ---- FMZ-C, batch C131 (2026-10-22)
    440098: ("1", "Each entry has a strategy.exit closing 50 % of the position (qty_percent = 50 when "
              "the high or low touches the fast channel): partial exits (criterion 1, as "
              "#436524)."),
    440109: ("1", "The only exit is a 10 % limit / 1 % stop bracket placed from the close of a later "
              "sell-signal bar (any of the three supertrends turning up), not from the entry, and "
              "kept while later entries are ignored; the house stops (fractions of the entry "
              "fill) cannot express it, and without it the script is one long held from the first "
              "signal to the end (as #430384)."),
    440118: ("1", "Orders are strategy.order calls whose quantities are built from "
              "strategy.position_size (running sums of 1 / 2 / 4 base units plus the held size), "
              "and close_all is called on every bar: position-size-driven order sizing (criterion "
              "1, as #430596)."),
    # ---- FMZ-C, batch C132 (2026-10-22)
    440334: ("2", "The trail offsets are strategy.position_avg_price x 0.05 passed to trail_offset, "
              "which is in ticks, with no /mintick (and negative for the long side): a price "
              "amount passed as a tick count (criterion 2, as #437048, #437677)."),
    440336: ("1", "An equity protector closes all trades when the open loss (strategy.openprofit) "
              "exceeds 30 % of the balance (initial capital plus netprofit): an account-state "
              "gate the signal-only port cannot express (criterion 1, as #432078)."),
    # ---- FMZ-C, batch C133 (2026-10-22)
    440354: ("1", "The script averages down: while the open loss is 10 % or more it adds 50 % of the "
              "held size to the long (pyramiding through strategy.position_size and "
              "position_avg_price) and holds until a 10 % gain on the average price: accumulation "
              "(criterion 1, as #435721, #430762)."),
    # ---- FMZ-C, batch C134 (2026-10-22)
    440430: ("1", "Up to seven long entries (Entry 1 .. Entry 7) are added while the RSI stays "
              "oversold, one per strategy.opentrades count, each with its own exit: pyramiding "
              "accumulation (criterion 1, as #430762)."),
    440436: ("2", "The stop is strategy.exit(loss = close x (1 - 1 %)): a price level passed to loss, "
              "which is in ticks (criterion 2, as #437048, #437677)."),
    # ---- FMZ-C, batch C135 (2026-10-22)
    440502: ("1", "Two take-profit exits close 15 % and then the rest of the position (qty_percent = "
              "15 at 4.5 %, 100 at 20 %): partial exits (criterion 1, as #436524)."),
    # ---- FMZ-C, batch C136 (2026-10-22)
    440533: ("1", "Each signal adds contribution / close units with strategy.order (dollar-cost "
              "averaging, the close order is commented out): the position is a running sum of "
              "orders (criterion 1, as #430596)."),
    440544: ("1", "Both entries test the close against request.security(syminfo.tickerid, 'D', [open, "
              "close], lookahead = barmerge.lookahead_on): the current day's final close on every "
              "intraday bar, a higher-timeframe value with lookahead (criterion 1)."),
    440546: ("2", "The exits are strategy.exit(loss = close - close x 1 %, profit = close + close x 2 "
              "%): price levels passed to loss and profit, which are in ticks (criterion 2, as "
              "#437048, #437677)."),
    # ---- FMZ-C, batch C137 (2026-10-22)
    440565: ("1", "Every entry comes on a bar where Trend changes, and the 'if change(Trend): "
              "strategy.close_all()' written after the entries leaves that bar flat (the "
              "close_all-after-entry convention, as #430380): as written no position is ever held "
              "(as #430384)."),
    440675: ("2", "The exits are strategy.exit(loss = atr(14), profit = 2 atr(14)): ATR price amounts "
              "passed to loss / profit, which are in ticks, with no /mintick (criterion 2, as "
              "#437048, #437677)."),
    # ---- FMZ-C, batch C138 (2026-10-22)
    440683: ("2", "The exit is strategy.exit(loss = close x (1 - 1 %), profit = close x 2): price "
              "levels passed to loss / profit, which are in ticks (criterion 2, as #437048, "
              "#437677)."),
    440691: ("1", "The entry condition is always true and its block resets the trailing level to 95 % "
              "of the current bar's high on every bar, so the long only closes on a single "
              "1-minute bar with a 5 % range and re-enters at once: a buy-and-hold from the data "
              "start (criterion 1, as #430384)."),
    440692: ("1", "There is no exit of any kind: the first doji (body under 0.05 price units) opens "
              "one long that is held to the end of the data, a buy-and-hold from near the data "
              "start (criterion 1, as #430384)."),
    440711: ("1", "Pyramiding 3 with repeated 'Long' / 'Short' entries of an equity-based lot, and "
              "exits sent as qty-0 'Close' entries: accumulation with position-size-dependent "
              "orders (criterion 1, as #430762)."),
    # ---- FMZ-C, batch C139 (2026-10-22)
    440715: ("2", "The exits pass strategy.position_avg_price +/- 50 / 100 x mintick (price levels) "
              "to profit and loss, which are in ticks (criterion 2, as #437048, #437677)."),
    440719: ("1", "The first take-profit closes 50 % of the position (strategy.close with qty_percent "
              "= 50) and moves the stop to break-even: partial exits (criterion 1, as #436524)."),
    440727: ("1", "strategy.close_all() is called unconditionally on every bar after the entries (in "
              "both option blocks), so every entry bar ends flat (as #430380): as written no "
              "position is ever held (as #430384)."),
    440729: ("1", "The entries test the close against request.security(syminfo.tickerid, 'D', close, "
              "lookahead = barmerge.lookahead_on): the current day's final close on every "
              "intraday bar, a higher-timeframe value with lookahead (criterion 1)."),
    440793: ("2", "The exits are strategy.exit(profit = close x (50 + 0.01)) and similar: price "
              "amounts passed to profit, which is in ticks (criterion 2, as #437048, #437677)."),
    # ---- FMZ-C, batch C141 (2026-10-22)
    440874: ("2", "The stop is strategy.exit(loss = strategy.position_avg_price x (1 - 2 %)): a price "
              "level passed to loss, which is in ticks (criterion 2, as #437048, #437677)."),
    # ---- FMZ-C, batch C142 (2026-10-22)
    440949: ("1", "The take-profit exits close TP1Yuzde = 50 % of the position (strategy.exit with "
              "qty_percent = 50): partial exits (criterion 1, as #436524)."),
    440954: ("1", "strategy.close_all() is called unconditionally on every bar after the entries, so "
              "every entry bar ends flat (as #430380): as written no position is ever held (as "
              "#430384)."),
    440975: ("1", "The only exit (default ATR trail) is a ratcheting stop at the 7-bar swing low "
              "minus one ATR(14), which the house trail (best high or close) cannot express, and "
              "entries need a flat position; without it the first long is held to the end (as "
              "#440109, #430384)."),
    440978: ("1", "The only exit is a bracket sent on entry-signal bars from "
              "strategy.position_avg_price; on the signal bar the position is flat (average na) "
              "so nothing is placed, and the bracket is armed only by a later crossover while "
              "long: a delayed level the house stops (fixed at the fill) cannot express; without "
              "it the long is held (as #440109)."),
    # ---- FMZ-C, batch C143 (2026-10-22)
    440981: ("1", "pyramiding = 100 with fixed qty-1 entries repeated on every signal while a "
              "position is open: the position accumulates units (criterion 1, as #430762)."),
    440992: ("1", "A DCA ladder: repeated qty-1 \"Buy\" entries as each fib level fills, and a qty-0 "
              "\"Close ALL\" entry at the average-price target: the position accumulates units "
              "(criterion 1, as #430762)."),
    # ---- FMZ-C, batch C144 (2026-10-22)
    441049: ("1", "The long's exits close 50 % of the position (strategy.close with qty_percent = 50) "
              "on an open-profit test: partial exits (criterion 1, as #436524)."),
    # ---- FMZ-C, batch C145 (2026-10-22)
    441065: ("1", "Reads the future: Pine v2 security(syminfo.tickerid, '120', ...) without [1] "
              "behaves as lookahead_on, so on every 5-minute bar the main SuperTrend uses the "
              "final close and ATR bands of the current 2-hour bar, not known until it ends "
              "(SURVEY_README request.security rule, as #434485)."),
    # ---- FMZ-C, batch C146 (2026-10-22)
    441086: ("2", "The only exit, strategy.exit(profit = target_price, loss = stop_loss_price), "
              "passes price levels (close + range x 2, low[1] - 100) where the call takes tick "
              "distances, with no /mintick: the target and stop are undefined as written "
              "(criterion 2, as #437048, #437677)."),
    # ---- FMZ-C, batch C147 (2026-10-22)
    441159: ("2", "The exits strategy.exit(profit = tpbuyval, loss = slbuyval) pass price levels "
              "(valuewhen(buy, close) +- 0.2 %) where the call takes tick distances, with no "
              "/mintick: the targets and stops are undefined as written (criterion 2, as #437048, "
              "#437677)."),
    # ---- FMZ-C, batch C148 (2026-10-22)
    441174: ("1", "pyramiding = 10 with three long entry ids (MacdLE 1st in, 2nd in, all in) at 33 % "
              "of equity each, each closed by its own signal: the position accumulates units "
              "(criterion 1, as #430762)."),
    441177: ("1", "The first target closes Target1_exit_qty = 50 % of the position (strategy.exit "
              "with qty_percent = 50): partial exits (criterion 1, as #436524)."),
    441954: ("1", "pyramiding = 2 with repeated qty-1 \"Long\" / \"Short\" entries from two signal sets, "
              "adding to an open position on the way to the target: the position accumulates "
              "units (criterion 1, as #430762)."),
    441960: ("1", "pyramiding = 10 and the entries fire while a position is open whenever the close "
              "is beyond the average price (martingale-style adds): the position accumulates "
              "units (criterion 1, as #430762)."),
    # ---- FMZ-C, batch C149 (2026-10-22)
    441998: ("2", "The exits strategy.exit(loss = stop_loss, profit = take_profit) pass price levels "
              "(close -/+ pips x mintick) where the call takes tick distances: the stop and "
              "target are undefined as written (criterion 2, as #437048, #437677)."),
    442007: ("1", "A monthly DCA with pyramiding = 500 (five band entries each month) and partial "
              "limit exits (qty_percent 6.67 / 14.28 / 25 / 44.44): accumulation and partial "
              "exits (criterion 1, as #430762, #436524)."),
    # ---- FMZ-C, batch C150 (2026-10-22)
    442076: ("2", "The exits strategy.exit(loss = close - atr, profit = close + 1.5 atr) pass price "
              "levels where the call takes tick distances, with no /mintick: the stop and target "
              "are undefined as written (criterion 2, as #437048, #437677)."),
    442080: ("1", "Reads the future: request.security(HTF, count(), lookahead = "
              "barmerge.lookahead_on) with the default Lookahead input on, HTF = 'W' on a daily "
              "chart, so every daily bar uses the current week's final MACD score (SURVEY_README "
              "request.security rule)."),
    442089: ("1", "Reads the future: Pine v2 request.security(syminfo.tickerid, '10D' / '15D' / "
              "'30D', open / close) without [1] behaves as lookahead_on, so every daily bar uses "
              "the final close of the current multi-day bar (SURVEY_README request.security rule, "
              "as #427066)."),
    # ---- FMZ-C, batch C151 (2026-10-22)
    442110: ("1", "The only bracket is sent on the signal bar from strategy.position_avg_price: on a "
              "first entry the position is flat (na, nothing placed) and on every later, "
              "reversing entry the levels come from the previous position's average price, a "
              "level the house stops (fractions of the new fill) cannot express (criterion 1, as "
              "#440109, #440978)."),
    442112: ("1", "pyramiding = 3 with repeated \"botsell20\" / \"botbuy20\" entries on every large "
              "candle while a position is open: the position accumulates units (criterion 1, as "
              "#430762)."),
    442115: ("2", "The only exits pass trail_points = trail_offset = atr x 1.5, a price amount, where "
              "the call takes ticks, with no /mintick: the trailing stop is undefined as written "
              "(criterion 2, as #437048, #437677)."),
    # ---- FMZ-C, batch C152 (2026-10-22)
    442229: ("1", "A DCA that buys on the close of every bar with pyramiding = 999 and cash sizes "
              "from remaining capital: the position accumulates units (criterion 1, as #430762)."),
    # ---- FMZ-C, batch C153 (2026-10-22)
    442261: ("1", "longCondition and shortCondition are both the constant true, so every bar sends a "
              "long entry then a short entry; the last entry wins (as #437773), so as written the "
              "position is short from the first bar on, churning each bar: a sell-and-hold from "
              "the data start (criterion 1, as #430384)."),
    # ---- FMZ-C, batch C154 (2026-10-22)
    442343: ("1", "The take profit closes TP1Yuzde = 50 % of the position (strategy.exit with "
              "qty_percent = 50): partial exits (criterion 1, as #436524)."),
    # ---- FMZ-C, batch C155 (2026-10-22)
    442378: ("1", "The take profit is a limit at entry_price x 1.005 with entry_price the input "
              "default 0, i.e. a sell limit at 0, which fills as soon as each long opens: as "
              "written no position is held beyond its fill (criterion 1, as #430384)."),
    442382: ("2", "The exit strategy.exit(loss = stopLoss, profit = takeProfit) passes price levels "
              "where the call takes tick distances, with no /mintick: the stop and target are "
              "undefined as written (criterion 2, as #437048, #437677)."),
    # ---- FMZ-C, batch C157 (2026-10-22)
    442525: ("2", "The signal source is request.security('NIFTY50', 'D', close), a named external "
              "instrument (the Nifty 50 index, read as its open interest) used as the signal for "
              "whatever chart is traded (SURVEY_README: another symbol -> criterion 2, as "
              "#436659); the support and resistance levels 15000 / 16000 are also fixed index "
              "prices."),
    442528: ("1", "There is no exit of any kind: the first close crossing back over the previous "
              "day's low opens one long that is held to the end of the data, a buy-and-hold from "
              "near the data start (criterion 1, as #440692)."),
    # ---- FMZ-C, batch C158 (2026-10-22)
    442542: ("2", "The only stops, strategy.exit(loss = close x 0.02), pass a price amount (2 % of "
              "the close) where the call takes ticks, with no /mintick: the stop is undefined as "
              "written (criterion 2, as #442115, #437048)."),
    442546: ("1", "Orders are strategy.order('Buy' / 'Sell') with the default quantity, which add or "
              "remove units instead of entering or reversing: each repeated signal changes the "
              "net position by one unit, a running sum of orders (criterion 1, as #440533, "
              "#430596)."),
    442550: ("1", "Reads the future: Pine v2 security(syminfo.tickerid, 'W', ...) without [1] on the "
              "4-hour chart behaves as lookahead_on, so every bar's two DEMA lines use the final "
              "values of the current week, not known until it ends (SURVEY_README "
              "request.security rule, as #441065, #434485)."),
    # ---- FMZ-C, batch C160 (2026-10-22)
    442645: ("1", "pyramiding = 3 with repeated \"Long\" / \"Short\" entries on every new fast-RSI "
              "crossing while a position is open (the exits are limit orders at the close that "
              "need not fill): the position accumulates units (criterion 1, as #442112, #430762)."),
    # ---- FMZ-C, batch C161 (2026-10-22)
    442816: ("2", "The exits strategy.exit(loss = close - 1.5 atr or close -+ 2 atr, profit = close + "
              "2 atr) pass price levels where the call takes tick distances, with no /mintick: "
              "the stops and targets are undefined as written (criterion 2, as #442076, #437048)."),
    442822: ("1", "The only exits close when strategy.openprofit divided by the equity (initial "
              "capital plus netprofit) reaches +2 % or -1 %: an account-state gate whose price "
              "move depends on the position size against the equity, which the signal-only port "
              "cannot express (criterion 1, as #440336)."),
    442833: ("1", "pyramiding = 4 with a fixed quantity of 2 and repeated RSI-divergence entries "
              "while a position is open: the position accumulates units (criterion 1, as #442112, "
              "#430762)."),
    442836: ("1", "The pinbar test is replaced by star = true, so on every confirmed bar while flat "
              "the script sends a new short (its filters are computed but never used) and re-sets "
              "the bracket from that bar: a constant-true entry, a short re-entered whenever flat "
              "(criterion 1, as #442261)."),
    # ---- FMZ-C, batch C162 (2026-10-22)
    442860: ("1", "Exits close parts of the position (qty_percent = 50 on the short) and every profit "
              "and stop exit is gated on strategy.openprofit over a cash order value of 1000: "
              "partial exits and cash-ratio exits (criterion 1, as #436524)."),
    442926: ("1", "pyramiding = 2 with a short entry on every new 2 % one-bar rally while a short is "
              "open: the position accumulates units (criterion 1, as #441954, #430762)."),
    # ---- FMZ-C, batch C163 (2026-10-22)
    442940: ("2", "The exits strategy.exit(loss = stopLossLevel, profit = targetPrice) pass price "
              "levels where the call takes tick distances, and the entries test the close against "
              "the fixed prices 100 / 200 (always above 200 on the BTC reading): undefined exits "
              "and instrument-specific levels (criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C165 (2026-10-22)
    443044: ("1", "is_uptrend (close > hlc3 - 3 ATR) and is_downtrend (close < hlc3 + 3 ATR) both "
              "hold on nearly every bar, so trend_changed is nearly always true and both entries "
              "fire together; the later Short wins (as #437773): a sell-and-hold from near the "
              "data start (criterion 1, as #442261)."),
    # ---- FMZ-C, batch C166 (2026-10-22)
    443110: ("1", "pyramiding = 3 with repeated \"Lungo\" / \"Corto\" entries on each new stochastic "
              "crossing while a position is open (the trail_points-only exits place no trail): "
              "the position accumulates units (criterion 1, as #442112, #430762)."),
    # ---- FMZ-C, batch C167 (2026-10-22)
    443238: ("1", "pyramiding = 5 with the long entry allowed again whenever the close is under the "
              "average price (and the short whenever above it): averaging into a losing position, "
              "the position accumulates units (criterion 1, as #430762)."),
    # ---- FMZ-C, batch C168 (2026-10-22)
    443252: ("2", "The exits strategy.exit(profit = close x (1 + 0.5 %), loss = close x (1 - 3 %)) "
              "pass price levels where the call takes tick distances, with no /mintick: the "
              "target and stop are undefined as written (criterion 2, as #442115, #437048)."),
    443990: ("2", "The exits strategy.exit(loss = close x (1 - 0.5 %), profit = close x (1 + 1 %)) "
              "pass price levels where the call takes tick distances, with no /mintick: the stops "
              "and targets are undefined as written (criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C169 (2026-10-22)
    444024: ("1", "pyramiding = 10 with level entries (close between the EMAs with the stochastic RSI "
              "under 25 / over 85) re-sent on every bar the condition holds: the position "
              "accumulates units (criterion 1, as #442112, #430762)."),
    # ---- FMZ-C, batch C170 (2026-10-22)
    444028: ("1", "pyramiding = 5 with a new long on each SAR crossover while a long is open (the "
              "short needs a 2 % down bar): the position accumulates units (criterion 1, as "
              "#442112, #430762)."),
    444355: ("1", "pyramiding = 10000 with a 10 % of equity buy on every green Heikin Ashi candle "
              "after a red one until the RSI exit: dollar-cost averaging that accumulates units "
              "(criterion 1, as #442229, #430762)."),
    # ---- FMZ-C, batch C171 (2026-10-22)
    444961: ("2", "The exits strategy.exit(loss = 0.01 x close, profit = 0.02 x close) pass price "
              "amounts where the call takes tick distances, with no /mintick: the stop and target "
              "are undefined as written (criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C173 (2026-10-22)
    445808: ("2", "The exits pass strategy.exit(loss = 100, profit = targetPriceLong / "
              "targetPriceShort): a price level where the call takes a tick distance, with no "
              "/mintick, so the target is undefined as written; the entry levels are absolute "
              "prices (close > 100 and close > 70) that are always true on the listed pair "
              "(criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C175 (2026-10-22)
    446523: ("2", "The exits strategy.exit(profit = 1.5 x atr, loss = atr) pass price amounts where "
              "the call takes tick distances, with no /mintick: the stop and target are undefined "
              "as written (criterion 2, as #442076, #437048)."),
    446539: ("2", "The exits strategy.exit(loss = 30 x atr, profit = 30 x atr) pass price amounts "
              "where the call takes tick distances, with no /mintick: the stop and target are "
              "undefined as written (criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C176 (2026-10-22)
    446755: ("1", "The exits are four strategy.exit calls with qty_percent 5 / 8 / 13 / 21 at "
              "take-profit levels of 13-34 % of the average price: partial exits, which the house "
              "engine cannot hold (one position, all-in or all-out; as #436524)."),
    # ---- FMZ-C, batch C177 (2026-10-22)
    446760: ("1", "After the first TD buy setup, valuewhen(buy, high, 0) is a positive price, so 'if "
              "TDbuyh' is true on every later bar: the long entry is re-sent forever and the "
              "short branch never runs again, one long held from the first buy (constant-true "
              "entry, criterion 1, as #442261)."),
    # ---- FMZ-C, batch C178 (2026-10-22)
    448059: ("2", "Every exit passes profit = close x 500 and loss = close x 200, price amounts where "
              "strategy.exit takes tick distances, with no /mintick: the stops and targets are "
              "undefined as written (criterion 2, as #442076, #437048)."),
    448060: ("1", "'if strategy.opentrades < pyramiding' (5) re-sends the long entry on every bar and "
              "is called after the RSI entries, so the long wins every bar and the short never "
              "holds: a constant-true entry (criterion 1, as #442261)."),
    448080: ("1", "'if strategy.opentrades < pyramiding' (5) re-sends the long entry on every bar and "
              "is called after the band entries, so the long wins every bar and the short never "
              "holds: a constant-true entry (criterion 1, as #442261)."),
    448767: ("2", "The exits pass trail_offset = 0.005, a fraction where the call takes ticks, and "
              "stop = 10, a price of 10 meant as points, with no /mintick: the trailing stop and "
              "the stop are undefined as written (criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C179 (2026-10-22)
    449445: ("1", "The only exit is strategy.close('L', qty_percent = 70), a partial close of the "
              "position: partial exits, which the house engine cannot hold (one position, all-in "
              "or all-out; as #436524)."),
    449497: ("1", "'if strategy.opentrades < pyramiding' (10) re-sends the long entry on every bar "
              "and is called after the band entries, so the long wins every bar and the short "
              "never holds: a constant-true entry (criterion 1, as #442261)."),
    449507: ("1", "Each entry's bracket is strategy.exit(qty_percent = 50, ...), closing half the "
              "position, and the rest closes on the SMA turn: partial exits, which the house "
              "engine cannot hold (as #436524)."),
    449516: ("1", "The only exits are four take-profit limits with qty_percent 25 % each (0.25 as "
              "written): partial exits, which the house engine cannot hold (one position, all-in "
              "or all-out; as #436524)."),
    449521: ("2", "The stops pass loss = close x 0.9 and loss = close x 1.1, price amounts where "
              "strategy.exit takes tick distances, with no /mintick: the stops are undefined as "
              "written (criterion 2, as #442076, #437048)."),
    # ---- FMZ-C, batch C183 (2026-10-22)
    451024: ("1", "The only close is strategy.close('Venda'), an id that is never entered, so it "
              "never acts: the long entries have no exit at all (criterion 1, as #440692)."),
    451028: ("1", "The levels are strict 7-bar pivots of the daily close requested on hourly bars, a "
              "series that stays flat for each day, so no pivot ever forms and no order can be "
              "sent (criterion 1)."),
    # ---- FMZ-C, batch C185 (2026-10-22)
    451411: ("1", "Every entry needs the London window (hour 13 to 15, or 16:00 exactly) on the bar's "
              "UTC open hour, and the header's 6-hour bars open at 0, 6, 12 and 18 UTC only: no "
              "order can fire as written (criterion 1, as #435514)."),
    451493: ("1", "Both exits set stop = limit = the bar's close (take profit and stop loss 0 %), "
              "attached to each entry: the long's sell limit under or sell stop over the fill "
              "fills at the entry open itself (the short's likewise), so every trade opens and "
              "closes at one price; the martingale entries are refused by pyramiding 1 (criterion "
              "1, constant / never-trading)."),
    # ---- FMZ-C, batch C187 (2026-10-22)
    451724: ("2", "strategy.exit(profit = targetLevel, loss = stopLevel) passes price levels (both "
              "equal the bar's close) where the call takes tick distances: the stop and target "
              "are undefined as written (criterion 2, as #441086, #442076)."),
    451726: ("1", "The session start is ta.change(hour(time, 'D')) != 0 on the header's daily bars, "
              "where the hour never changes: the first-candle high / low are never set (or only "
              "from the data's first bar), so the breakouts never fire as written (criterion 1, "
              "as the daily clock tests of C170-C175 and #430384)."),
    452281: ("1", "The five averages are request.security(syminfo.tickerid, '5' / '30' / '60' / '480' "
              "/ '720', ..., lookahead_on) on the daily header chart: resolutions below the "
              "chart's, whose value per daily bar is undefined (criterion 1, as #427518)."),
    452282: ("1", "The only exit is strategy.close('sell'), an id never entered, so the EMA 5 / 20 "
              "cross-up long is never closed: one long held from the first signal with no exit "
              "(criterion 1, as #440692)."),
    452353: ("1", "Sixteen take-profit exits close qty_percent = 5 % each (partial exits), and the "
              "trailing multiplier switches on the count of closed trades: partial-position and "
              "trade-history-dependent exits (criterion 1, as #436524)."),
    # ---- FMZ-C, batch C188 (2026-10-22)
    452358: ("1", "strategy.entry('Short') is sent on every bar with no open trade "
              "(strategy.opentrades == 0) and the exits only end it after 7 bars or a price move: "
              "a short re-entered from the data start onwards with no signal (criterion 1, "
              "constant-true entry, as #442261)."),
    # ---- FMZ-C, batch C189 (2026-10-22)
    452698: ("1", "On the daily header chart every bar is a new day, so a long is opened on the "
              "second bar and each take-profit close is followed on the same bar by a new long "
              "entry (the short is opened only when no long is): one long held from the data "
              "start (criterion 1, buy-and-hold from the data start, as #430384)."),
    # ---- FMZ-C, batch C190 (2026-10-22)
    453228: ("1", "pyramiding = 3 with strategy.entry('Long') on every bar the close stays over the "
              "10-bar high (and the short likewise): the position accumulates units (criterion 1, "
              "as #442112, #430762)."),
    453230: ("1", "Every entry is gated by dayofmonth(timenow) != dayofmonth(lastTradeDay), where "
              "timenow is the wall-clock time the script runs at and lastTradeDay stores a day "
              "number read back as a timestamp: whether any trade happens depends on the day of "
              "the run, not on the data (criterion 1)."),
    # ---- FMZ-C, batch C191 (2026-10-22)
    453233: ("1", "The trend filter is request.security(syminfo.tickerid, '240', ..., lookahead_on) "
              "on the 6-hour header chart: a 4-hour resolution below the chart's, whose value per "
              "chart bar is undefined (criterion 1, as #427518)."),
    453247: ("1", "Positions are opened and flattened with strategy.order (qty = the held size), so "
              "which side the strategy trades for the whole run depends on the first one-shot "
              "signal of the data, and the bracket levels are computed before the signals are "
              "re-assigned: strategy.order position bookkeeping (criterion 1, as #430596)."),
    453266: ("2", "The exits strategy.exit(profit = takeProfit) / (loss = stopLoss) pass price "
              "amounts (a price level and 5 % of the close) where the call takes tick distances: "
              "the exits are undefined as written (criterion 2, as #442076, #442115)."),
    # ---- FMZ-C, batch C192 (2026-10-22)
    453281: ("1", "The breakout levels are request.security(syminfo.tickerid, '60', high / low / "
              "close) on the daily header chart: a 1-hour resolution below the chart's, whose "
              "value per daily bar is undefined (criterion 1, as #427518)."),
    # ---- FMZ-C, batch C193 (2026-10-22)
    453654: ("1", "Every bar closes all positions once timenow is past 15:15 of the day the script "
              "runs (exitTime is built from timenow's own date): with the wall-clock time of the "
              "run deciding whether any trade is held, the result depends on when the backtest is "
              "run, not on the data (criterion 1, as #453230)."),
    453662: ("1", "close_all fires when the day's equity change reaches -125 or +1000 currency units "
              "(strategy.equity against the day's start): a size-dependent equity gate on every "
              "trade (criterion 1, as #440336)."),
    # ---- FMZ-C, batch C195 (2026-10-22)
    454359: ("1", "The only exit arms when strategy.netprofit (closed-trade profit in currency) "
              "reaches 1.2 x the average price (a price level): a size- and history-dependent "
              "gate on the stop, with no other exit for the long (criterion 1, as #440336)."),
    454361: ("1", "The target is close + 0.001 (a forex-pip amount) on BTC: the limit sits at, or "
              "within a fraction of a cent of, the entry, so every long and short is closed at "
              "about its own fill price (criterion 1, as #451493)."),
    454721: ("1", "The 'Markov' state is overwritten by a counter that cycles 0-9 from the first bar "
              "of the data, so which bars buy, sell or close depends on where the data starts "
              "rather than on prices alone; the source also names no bar size (criterion 1)."),
    # ---- FMZ-C, batch C196 (2026-10-22)
    454736: ("1", "The take-profit steps strategy.exit(qty_percent = 12 / 8 / 4 %) close parts of the "
              "position at 6 / 12 / 18 %: partial exits (criterion 1, as #436524)."),
    # ---- FMZ-C, batch C197 (2026-10-22)
    454747: ("1", "The close condition includes strategy.netprofit / strategy.equity x 100 >= 20: "
              "once the closed profit reaches 20 % of equity every bar closes the long, a size- "
              "and history-dependent equity gate (criterion 1, as #440336)."),
    # ---- FMZ-C, batch C198 (2026-10-22)
    456143: ("3", "Pairs grid on two OKX perpetual swaps: exchange positions, the OKX account equity "
              "(Info.data[0].totalEq), contract values (CtVal) and iceberg limit orders off the "
              "live bid / ask in a timed loop, two instruments at once (criterion 3). Stored in "
              "flagged/ (rule C7)."),
    458029: ("1", "pyramiding = 2 with the 'Long' / 'Short' entries sent again on a later crossing "
              "while the trade is still open (a cross back that opens nothing in between): the "
              "position adds units (criterion 1, as #442112, #430762)."),
    # ---- FMZ-C, batch C199 (2026-10-22)
    458035: ("1", "Both 'pivots' are high[1] + low[1] + close[1] / 3 (about 2.3 times the price, "
              "operator precedence), so low <= pivotLow holds on every bar: a long sent on every "
              "bar and no short ever (criterion 1, constant-true entry, as #442261)."),
    458037: ("1", "The take-profit target is solved from the script's own balance bookkeeping "
              "(CurrentBalance, Accom, PositionTarget of a 1000 USDT start, 90 % position size), "
              "so where a trade closes depends on the position size and the history of past "
              "trades (criterion 1, size- and history-dependent exit, as #440336)."),
    458038: ("1", "Entries stop for good once the strategy's own equity drawdown from its peak "
              "reaches 40 % (end_strategy): a size- and history-dependent equity gate on every "
              "trade (criterion 1, as #440336)."),
    458045: ("1", "strategy.exit with qty = 0.75 / 0.25 x the trade size takes partial profits (and "
              "the stop moves to the entry): partial exits (criterion 1, as #436524)."),
    # ---- FMZ-C, batch C200 (2026-10-22)
    458066: ("1", "The only exit closes when strategy.opentrades.profit (currency, for a 10 % of "
              "equity position) reaches 0.30 x the entry price (a price): where the trade ends "
              "depends on the position size (criterion 1, size-dependent exit, as #440336)."),
    # ---- FMZ-C, batch C202 (2026-10-22)
    458170: ("1", "pyramiding = 3: each stochastic-RSI cross-up in oversold adds another entry while "
              "the long is held, up to three, all closed together by close_all when the "
              "stochastic RSI reaches 99 (no stop): the position size path is the strategy "
              "(criterion 1, as #430762, #439950)."),
    # ---- FMZ-C, batch C203 (2026-10-22)
    458198: ("2", "The 50 / 30 pips are passed to strategy.exit as limit= / stop= PRICES (pip = "
              "mintick x 10, so the levels are the absolute prices 50 and 30): at any BTC price "
              "the long's sell limit and the short's buy stop are marketable at the fill, so "
              "every trade would close at its own fill, and the 30-candle gap divides "
              "milliseconds by 1000 x mintick; both are instrument-specific price units "
              "(criterion 2, as #441086)."),
    # ---- FMZ-C, batch C204 (2026-10-22)
    458243: ("1", "Every RSI-under-30 bar at least 30 days after the last buy sends strategy.entry "
              "plus a strategy.order buy (the order is not limited by pyramiding), and nothing "
              "ever sells: a dollar-cost accumulation whose size path is the strategy (criterion "
              "1, as #439958, #430762)."),
    458245: ("1", "The long's limit and stop are the same price (wave1 = wave3 = valuewhen(wave_trend "
              "== 1, close, 0)) and the short's too (wave2 = wave4), sent on every bar including "
              "the signal bar: one of each pair is always marketable at the fill, so every trade "
              "closes at the open it fills at and no position is ever held as written (criterion "
              "1, zero-length trades as #452827)."),
    # ---- FMZ-C, batch C205 (2026-10-22)
    458265: ("1", "The trades follow math.random() draws (each bar's 'next state' is chosen by random "
              "numbers against fixed probabilities): no reproducible rule, and every run of the "
              "script trades differently (criterion 1)."),
    # ---- FMZ-C, batch C206 (2026-10-22)
    468306: ("1", "strategy.netprofit >= 200 (the 'daily' target is the cumulative net profit in "
              "currency) closes every position on every later bar: once the running profit of the "
              "sized trades passes 200 the strategy stops trading, so the trades depend on the "
              "position size and the account history (criterion 1, equity / net-profit gate)."),
    # ---- FMZ-C, batch C208 (2026-10-22)
    468340: ("1", "The breakout levels are the high and low of the first 5 bars of whatever data is "
              "loaded (bar_index < 5), held for ever: where the trades fall depends on where the "
              "data starts (criterion 1, data-start-dependent levels)."),
    469612: ("1", "pyramiding = 10 with up to 10 stacked entries per side whose quantities step 1, 2, "
              "4, 8, 5 ... 10 as the same signals repeat, and closes per entry id: the "
              "position-size path is the strategy (criterion 1, as #430762, #439950)."),
    # ---- FMZ-C, batch C209 (2026-10-22)
    471673: ("1", "The take-profits are strategy.exit qty_percent = 33 / 66 / 100 partial exits (TP 1 "
              "/ 2 / 3 at 5 / 10 / 15 %): the position is closed in parts, so the size path is "
              "part of the strategy (criterion 1, qty_percent partial exits, as #439950)."),
    # ---- FMZ-C, batch C210 (2026-10-22)
    471708: ("1", "Entries are allowed only while time >= timenow minus 2500 days (a window measured "
              "back from the moment the script runs), with qty = equity / close: which trades "
              "exist depends on the run date (criterion 1, timenow gate)."),
    # ---- FMZ-C, batch C211 (2026-10-22)
    471710: ("1", "Besides the 28-bar exit, the stop closes when strategy.opentrades.profit(0) <= "
              "-1600 (currency, for a 10 % of equity position): where trades end depends on the "
              "position size and account (criterion 1, size-dependent exit, as #458066)."),
    471711: ("1", "close_all fires when hour(timenow) == 15 and minute(timenow) == 25, i.e. on the "
              "clock of the machine running the script, not the bar's time; the stop / target are "
              "fixed 100 / 150 price units from the average price (criterion 1, timenow gate)."),
    471718: ("1", "The strategy trades only while bar_index >= last_bar_index - 499 (the last 500 "
              "bars of whatever data is loaded) and has no market signal, only a timed long / "
              "short rotation: where it trades depends on where the data ends (criterion 1, "
              "data-end-dependent window)."),
    # ---- FMZ-C, batch C212 (2026-10-22)
    472253: ("2", "The exits pass ATR distances as prices (limit = 2 x atr, stop = 1 x atr): for BTC "
              "those are prices far under the market, so the long's sell limit and the short's "
              "buy stop are marketable at every fill and each trade would close at its own fill "
              "(criterion 2, distances as absolute prices, as #458198)."),
    # ---- FMZ-C, batch C214 (2026-10-22)
    473237: ("1", "The exits are strategy.exit qty_percent = 50 partial closes (half the position at "
              "the stop / target, re-sent every bar): the position is closed in parts, so the "
              "size path is part of the strategy (criterion 1, qty_percent partial exits, as "
              "#439950)."),
    # ---- FMZ-C, batch C215 (2026-10-22)
    473242: ("2", "The bracket passes percentages of the close as tick counts (loss = 0.01 x close, "
              "profit = 0.02 x close in strategy.exit's tick fields): a price amount in a tick "
              "field, so the distance in price depends on the instrument's tick size (criterion "
              "2, as #442115)."),
    # ---- FMZ-C, batch C217 (2026-10-22)
    473362: ("1", "The TRAMA's var seed (tramaPrev) is set once, to the first bar's close, and never "
              "updated, so trama = 0.8 x close + 0.2 x the first bar's close and its crossings "
              "are crossings of the first bar's close: half of the entries (the bracketed Long / "
              "Short ids) are set by where the data starts (criterion 1, a data-window level, as "
              "#468340)."),
    # ---- FMZ-C, batch C218 (2026-10-22)
    473377: ("2", "strategy.exit's profit / loss fields take tick counts but receive prices (avg x "
              "1.015 / avg x 0.99): a price amount in a tick field, so the distance in price "
              "depends on the instrument's tick size and price level (criterion 2, as #442115)."),
    473389: ("1", "pyramiding = 2 with a long sent on every bar the RSI 8 is under 28: a second unit "
              "is added inside the trade, so the size path is part of the strategy (criterion 1, "
              "pyramiding >= 2 repeats)."),
    473391: ("1", "The stop is strategy.close when strategy.openprofit < -1 % of strategy.equity: an "
              "exit set by the position's money size against the equity (criterion 1, "
              "equity-share openprofit exits)."),
    # ---- FMZ-C, batch C219 (2026-10-22)
    473406: ("1", "useTakeProfit is on by default and exits in four qty_percent steps (25 / 20 / 10 / "
              "15 % at 3 / 6 / 12 / 21 %): the position is closed in parts, so the size path is "
              "part of the strategy (criterion 1, qty_percent partial exits, as #436524)."),
    # ---- FMZ-C, batch C220 (2026-10-22)
    473942: ("2", "strategy.exit's profit / loss fields take tick counts but receive ATR price "
              "amounts (profit = 3 x ATR, loss = ATR): a price amount in a tick field, so the "
              "distance in price depends on the instrument's tick size (criterion 2, as #442115)."),
    # ---- FMZ-C, batch C221 (2026-10-22)
    474055: ("1", "The S/R level is refreshed only on bars where bar_index % 21 == 0, counted from "
              "the first bar of the loaded data, and the entries compare it with the "
              "double-bottom levels: which bars set the level depends on where the data starts "
              "(criterion 1, a data-start schedule, as #430034 / #468340)."),
    474057: ("1", "Martingale pyramiding: up to 5 additions to the open position (strategy.entry on "
              "the same id with qty = initial x multiplier^n after a drop and rebound), so the "
              "size path is part of the strategy (criterion 1, stepped adds, as #430762)."),
    474064: ("1", "Multi-step take-profit on by default: seven qty_percent partial exits (10 % each "
              "at ATR and percent levels): the position is closed in parts, so the size path is "
              "part of the strategy (criterion 1, qty_percent partial exits, as #436524)."),
    # ---- FMZ-C, batch C223 (2026-10-22)
    474709: ("1", "The target and stop are close +/- 0.0020 / 0.0040 in price (FX-sized, \"40 pips\"): "
              "on the header pair's 0.1 tick both levels sit at the signal close, so one of them "
              "is always at or through the fill open and every trade closes at its own fill "
              "(criterion 1, a zero-width bracket, as #451493)."),
    474712: ("1", "A qty_percent partial exit (50 % at 1 R) on every trade, with a risk-sized "
              "quantity: the position is closed in parts, so the size path is part of the "
              "strategy (criterion 1, qty_percent partial exits, as #436524)."),
    474803: ("1", "The trailing exit has trail_price = close x 0.98 (under the market, so armed at "
              "once) and trail_offset = 0.02 ticks (0.002 in price), re-sent every bar: it stops "
              "every trade at the first tick against it, so trades end at their entry price "
              "(criterion 1, a zero-width exit, as #451493)."),
    # ---- FMZ-C, batch C224 (2026-10-22)
    474822: ("1", "Partial closes: entries of qty 0.5 and strategy.close(\"Buy\", qty = 0.1 / 0.5) on "
              "the basis re-cross and the lower-band break: the position is closed in parts, so "
              "the size path is part of the strategy (criterion 1, partial exits, as #436524)."),
    474837: ("1", "Multi-step take-profit on by default: six qty_percent partial exits (ATR and "
              "percent levels) per trade: the position is closed in parts, so the size path is "
              "part of the strategy (criterion 1, qty_percent partial exits, as #436524)."),
    # ---- FMZ-C, batch C225 (2026-10-22)
    474870: ("1", "The trailing exit has trail_price = avg x (1 - 2 / 89500) (at the entry price, so "
              "armed at once) and trail_offset = (2 / 89500) x close ticks (under one tick of "
              "0.1): it stops each trade at the first tick against it, so trades end at their "
              "entry price (criterion 1, a zero-width exit, as #451493)."),
    # ---- FMZ-C, batch C226 (2026-10-22)
    474879: ("1", "Dollar-cost averaging: strategy.order('DCA Buy', long, investment / close) on "
              "every cross under the lower band, with no exit until a fixed close date: the "
              "position is a running sum of orders, so the size path is the strategy (criterion "
              "1, DCA accumulation, as #430762)."),
    474956: ("1", "No exit, and the entry test passes on the first bars of the data (its averages are "
              "still na and comparisons with na are false, so the 'clean' loop finds nothing to "
              "block): the first bar's long is held to the end of the data, a single buy-and-hold "
              "trade (criterion 1, as #433916)."),
    474960: ("2", "strategy.exit's profit / loss fields take tick counts but receive price amounts "
              "(close x 2.4 % / close x 1.2 %): a price amount in a tick field, so the distance "
              "in price depends on the instrument's tick size (criterion 2, as #442115)."),
    # ---- FMZ-C, batch C227 (2026-10-22)
    474981: ("1", "pyramiding = 3 with an entry on every bar whose body exceeds 1.91 % of the close: "
              "up to three units are added on the same side, so the size path is part of the "
              "strategy (criterion 1, pyramiding >= 2 repeats)."),
    474983: ("1", "The daily RSI is requested with lookahead_on and no [1] offset, so every intraday "
              "bar reads the day's final RSI before the day ends (criterion 1, higher time frame "
              "with lookahead, as #427518)."),
    # ---- FMZ-C, batch C228 (2026-10-22)
    475588: ("2", "strategy.exit's profit / loss fields take tick counts but receive the percent "
              "inputs (profit = 1.5, loss = 0.5): 1.5 / 0.5 ticks instead of 1.5 % / 0.5 %, a "
              "unit mismatch, so the distance depends on the instrument's tick size (criterion 2, "
              "as #442115)."),
    475592: ("1", "Partial take-profits: two strategy.exit orders each for qty = position_size x 0.5 "
              "(TP1 / TP2) plus a moved stop: the position is closed in parts, so the size path "
              "is part of the strategy (criterion 1, partial exits, as #436524). The header also "
              "says \"all rights reserved\"."),
    475593: ("1", "The take-profit and stop are money amounts ($200 / $100) turned into ticks by "
              "dividing by the open position size: the exit distance depends on the position's "
              "size (criterion 1, size-dependent exits)."),
    # ---- FMZ-C, batch C229 (2026-10-22)
    475605: ("2", "strategy.exit's profit / loss fields take tick counts but receive price amounts (3 "
              "% x close / 1 % x close): a price amount in a tick field, so the distance in price "
              "depends on the instrument's tick size (criterion 2, as #442115)."),
    475634: ("1", "strategy.close_all when the drawdown of strategy.equity from its peak exceeds 30 "
              "%: an exit set by the account's equity path (criterion 1, equity gates, as "
              "#453662)."),
    # ---- FMZ-C, batch C230 (2026-10-22)
    476239: ("1", "strategy.close when (close - avg price) x position size reaches a fixed money "
              "target (1500 / 1000 INR): an exit that depends on the position's size (criterion "
              "1, size-dependent money exits)."),
    476245: ("1", "On a stop the script reverses with qty = the held size x 2 (capped at 1e12): a "
              "martingale doubling of the position (criterion 1, martingale adds)."),
    476250: ("1", "The weekly MACD and signal come from request.security(\"W\", ..., "
              "lookahead=barmerge.lookahead_on) on a daily chart: the week's final values are "
              "read before the week ends (criterion 1, lookahead_on for a higher time frame)."),
    476253: ("1", "pyramiding=200 and strategy.entry on every bar the Stochastic RSI condition holds: "
              "repeat entries add to the position (criterion 1, pyramiding >= 2 with repeat "
              "entries)."),
    # ---- FMZ-C, batch C231 (2026-10-22)
    476261: ("1", "Three strategy.exit targets with qty_percent 50 / 30 / 20 scale the position out "
              "in parts (criterion 1, partial exits)."),
    476264: ("1", "Five entry ids (Step1-3, Pullback, Above50) add 20 % / 40 % parts to the long and "
              "the EMA 5 / 13 cross-down closes only one part: staged adds and partial closes "
              "(criterion 1, DCA adds and partial exits)."),
    # ---- FMZ-C, batch C233 (2026-10-22)
    477534: ("2", "The only exits pass trail_points = atr x 1.5 and trail_offset = atr x 0.75, price "
              "amounts, where the call takes ticks, with no /mintick: the trailing stop is "
              "undefined as written (criterion 2, as #442115)."),
    # ---- FMZ-C, batch C234 (2026-10-22)
    477565: ("1", "Every entry needs the bar inside the 07:00-10:00 kill-zone session "
              "(time(timeframe.period, session)), which a 2-day bar starting at the day boundary "
              "never is: the strategy never trades on its own chart (criterion 1, intraday time "
              "windows on a multi-day chart, as #437544)."),
    # ---- FMZ-C, batch C235 (2026-10-22)
    477584: ("2", "The bracket's trail_points = atr x 2.0 is a price amount where the call takes "
              "ticks, with no /mintick: the trailing stop is undefined as written (criterion 2, "
              "as #442115)."),
    477600: ("1", "A grid: the first bar buys with no market signal (active_trade false) and every "
              "profit close re-buys on the next bar, with a \"Rebuy\" add on each 5 % drop (ignored "
              "only by pyramiding 1): an always-invested buy from the first bar with DCA adds by "
              "design (criterion 1, as #433916 and the DCA rule)."),
    # ---- FMZ-C, batch C236 (2026-10-22)
    477610: ("2", "The trailing exits pass trail_points = atr x 1.5 and trail_offset = atr x 1.0, "
              "price amounts, where the call takes ticks, with no /mintick: the trailing stop is "
              "undefined as written (criterion 2, as #442115)."),
    # ---- FMZ-C, batch C237 (2026-10-22)
    477950: ("2", "The exits pass trail_offset = atr x 2.0, a price amount, where the call takes "
              "ticks, with no /mintick: the trailing exit is undefined as written (criterion 2, "
              "as #442115)."),
    477953: ("1", "Every signal sends strategy.order (not strategy.entry) for 1 unit, which ignores "
              "pyramiding and nets with the open position: up to four buys or sells a bar "
              "accumulate units (criterion 1, repeat adds)."),
    # ---- FMZ-C, batch C238 (2026-10-22)
    477970: ("1", "pyramiding=2 with repeat \"Buy\" / \"Sell\" entries, and every entry gated by the "
              "drawdown of strategy.equity from its peak: units add and the account's equity path "
              "gates trading (criterion 1, pyramiding >= 2 with repeat entries and equity gates)."),
    477976: ("1", "\"Scale Buy\" / \"Scale Sell\" entries add 1 unit each time the close moves a point "
              "against the average price: averaging down (criterion 1, DCA adds)."),
    478691: ("1", "The long and short each send a \"Partial Take Profit\" exit with qty_percent=50 and "
              "a break-even move for the other half: partial exits (criterion 1)."),
    # ---- FMZ-C, batch C239 (2026-10-22)
    478711: ("1", "The Fibonacci levels use the lowest low and highest high since the first bar of "
              "the chart (var levels widened on every bar): levels set by the data window's start "
              "(criterion 1, data-window levels, as #430034)."),
    478713: ("1", "The long entry needs close > request.security(higher time frame, sma(close, 20), "
              "lookahead_on): the higher bar's final value is read before it closes (criterion 1, "
              "lookahead_on for a higher time frame)."),
    # ---- FMZ-C, batch C241 (2026-10-22)
    481345: ("1", "The entry reads daily EMAs from request.security(\"D\", ..., "
              "lookahead=barmerge.lookahead_on) on an hourly chart: the day's final values are "
              "used before the day ends (criterion 1, lookahead_on for a higher time frame)."),
    481346: ("1", "strategy.close_all when the drawdown of strategy.equity from its peak reaches 10 "
              "%: an exit set by the account's equity path (criterion 1, equity gates, as "
              "#453662)."),
    # ---- FMZ-C, batch C242 (2026-10-22)
    481356: ("1", "The first take-profit sends strategy.order for a part of the position (firstTpQty, "
              "50 % by input) before close_all at the second target: partial exits (criterion 1)."),
    481371: ("1", "A grid: \"Long Grid n\" / \"Short Grid n\" entries add base size x 1.5^n each time "
              "price moves a grid step against the position, with daily equity profit targets and "
              "an openprofit drawdown close: martingale adds and equity gates (criterion 1)."),
    # ---- FMZ-C, batch C243 (2026-10-22)
    482420: ("1", "The open / close MA series come from request.security at the alternate resolution "
              "with lookahead=barmerge.lookahead_on (useRes on by default): higher-bar values are "
              "read before the bar closes (criterion 1, lookahead_on for a higher time frame)."),
    482430: ("2", "The exits pass trail_points = atr x 2.5, a price amount, where the call takes "
              "ticks, with no /mintick: the trailing exit is undefined as written (criterion 2, "
              "as #442115)."),
    482432: ("1", "Three exits per entry close 30 % / 50 % / 20 % of the position (qty_percent): "
              "partial exits (criterion 1)."),
    # ---- FMZ-C, batch C244 (2026-10-22)
    482444: ("1", "The Fibonacci levels come from the highest and lowest close since the first bar of "
              "the data (cumulative over every up bar): data-window levels that change with where "
              "the data starts (criterion 1, as #478711 / #430034)."),
    482456: ("1", "Each entry is qty 2 with two exits of qty 1 at separate targets and break-even "
              "exits for the rest: partial exits (criterion 1)."),
    # ---- FMZ-C, batch C246 (2026-10-22)
    482499: ("1", "Each entry has a take-profit exit for half the position (qty_percent = 50) beside "
              "a close_all stop: partial exits (criterion 1)."),
    482501: ("2", "The exits pass profit = close + (close - low) x 3, a price, where the call takes "
              "ticks, with no /mintick: the target is undefined as written (criterion 2, as "
              "#442115)."),
    482504: ("2", "The exits pass trail_points = atr x 1.5, a price amount, where the call takes "
              "ticks, with no /mintick: the trailing exit is undefined as written (criterion 2, "
              "as #442115)."),
    482506: ("1", "pyramiding = 50 with up to four separate long entries per week at the S1-S4 "
              "levels, each with its own target: grid adds (criterion 1)."),
    # ---- FMZ-C, batch C247 (2026-10-22)
    482672: ("1", "pyramiding = 999 with up to 30 safety orders added as the price falls (scaled DCA "
              "averaging down): DCA adds (criterion 1)."),
    # ---- FMZ-C, batch C248 (2026-10-22)
    482767: ("2", "The exit passes trail_points = atr x 0.5 and trail_offset = atr x 0.3, price "
              "amounts, where the call takes ticks, with no /mintick: the trailing exit is "
              "undefined as written (criterion 2, as #442115)."),
    # ---- FMZ-C, batch C249 (2026-10-22)
    482783: ("1", "strategy.order buys are added on each 5 % drop with the quantity doubled each "
              "time, up to 10 doublings: martingale adds (criterion 1)."),
    482785: ("1", "The open / close MA series come from request.security at the alternate resolution "
              "(3 x the chart) with lookahead=barmerge.lookahead_on (useRes on by default): "
              "higher-bar values are read before the bar closes (criterion 1, lookahead_on for a "
              "higher time frame, as #482420)."),
    # ---- FMZ-C, batch C250 (2026-10-22)
    482824: ("2", "The exits pass trail_offset = atr x 0.5, a price amount, where the call takes "
              "ticks, with no /mintick: the trailing exit is undefined as written (criterion 2, "
              "as #482767)."),
    # ---- FMZ-C, batch C251 (2026-10-22)
    482835: ("1", "The model prediction is math.random() (a random number each bar): the trades are "
              "random, not a rule (criterion 1, as the C204-C206 math.random readings)."),
    482840: ("2", "initial_stop_loss_points = 20 and trail_distance = 10 are price amounts added to "
              "the entry price for the stop levels, with no scale (criterion 2, as #473377)."),
    482860: ("2", "buyOffset / sellOffset = 2 are price amounts added to the EMA for the entry "
              "levels, and stopLossPoints = 20 is a price amount from the average price "
              "(criterion 2, as #473377)."),
    # ---- FMZ-C, batch C252 (2026-10-22)
    482876: ("2", "The exits pass trail_offset = trailingStopPerc x close, a price amount, where the "
              "call takes ticks, with no /mintick: the trailing exit is undefined as written "
              "(criterion 2, as #482767)."),
    # ---- FMZ-C, batch C253 (2026-10-22)
    482899: ("2", "The trailing exit passes trail_points = close x 0.005 and trail_offset = close x "
              "0.002, price amounts, where the call takes ticks, with no /mintick: the trailing "
              "exit is undefined as written (criterion 2, as #482767)."),
    482902: ("2", "The exits are stop = low - 10 / high + 10 and limit = high + 10 / low - 10: fixed "
              "price amounts with no scale (criterion 2, as #473377)."),
    482909: ("1", "DCA accumulation: up to four buys of a risk-sized quantity while RSI < 30, with "
              "the exit level taken from the average of the buy closes (as the C204-C206 DCA "
              "readings, criterion 1)."),
    482916: ("1", "Pyramided buys gated on position_size against equity x 0.066 x 15 (a "
              "size-dependent gate) and a 50 % partial close (qty_percent): criterion 1, as "
              "#436524."),
    # ---- FMZ-C, batch C254 (2026-10-22)
    483022: ("1", "The 'Fear and Greed' values are a fixed demo array of eight numbers cycled by "
              "bar_index: the trades follow the bar count, not the market (criterion 1)."),
    483033: ("1", "The trading window is timestamp(year(timenow), month(timenow), "
              "dayofmonth(timenow), ...): it is built from the run's wall clock, so only bars of "
              "the day the script runs can trade (criterion 1, as #453230)."),
    # ---- FMZ-C, batch C255 (2026-10-22)
    483049: ("1", "A 50 % partial take-profit (strategy.exit qty_percent = 50) with a risk-sized "
              "quantity: criterion 1, as #436524."),
    483051: ("1", "buyCondition is valuewhen(longLiq, longLiq, 0..2), the value of longLiq at its own "
              "last three occurrences, which is always true once three have occurred: a buy sent "
              "on every later bar (constant-true, criterion 1, as #442261)."),
    # ---- FMZ-C, batch C256 (2026-10-22)
    483067: ("2", "The exits pass trail_points = 2 % x avgPrice, a price amount, where the call takes "
              "ticks, with no /mintick: the trailing exit is undefined as written (criterion 2, "
              "as #482767)."),
    483081: ("2", "stopLoss = 100 'points' is added to and subtracted from the close as a price "
              "amount for the stop, target and trailing tests (criterion 2, as #473377)."),
    483086: ("1", "Five partial take-profits of 20 % of the position each (qty = position_size x 0.2) "
              "with adds allowed: criterion 1, as #436524."),
    # ---- FMZ-C, batch C257 (2026-10-22)
    483104: ("2", "The exit passes loss = atr x 1.5 and profit = atr x 2.5, price amounts, where "
              "loss= / profit= take ticks (criterion 2, as #473377)."),
    # ---- FMZ-C, batch C258 (2026-10-22)
    483118: ("2", "The trailing exit passes trail_points = atr x 1.5 and trail_offset = atr x 1.5, "
              "price amounts, where the call takes ticks, with no /mintick (criterion 2, as "
              "#482767)."),
    483119: ("2", "Stop loss 5 and take profit 15 are dollar amounts added to the average price "
              "(criterion 2, as #473377)."),
    483125: ("1", "As written it can never trade: todayLow includes the current bar, so close <= "
              "min(prevDayLow, todayLow) - buffer is impossible (the close is never under the "
              "bar's own low), and likewise for the short (criterion 1, as #430384)."),
    483496: ("2", "The exits pass loss = longSL / shortSL and profit = longTP / shortTP, which are "
              "price LEVELS, where loss= / profit= take ticks (criterion 2, as #473377)."),
    483498: ("1", "A 50 % partial take-profit (qty_percent = 50) beside a trail whose trail_points / "
              "trail_offset are price amounts (riskValue x 0.8): criterion 1, as #436524 (the "
              "trail also fails criterion 2)."),
    # ---- FMZ-C, batch C259 (2026-10-22)
    483500: ("1", "Three partial take-profits of 33 % / 33 % / 34 % (qty_percent): criterion 1, as "
              "#436524."),
    483508: ("1", "The only exit is strategy.close(\"MacdLE\"), an id that is never entered, so nothing "
              "ever closes the long (criterion 1, as #440692)."),
    483526: ("1", "A partial close of half the lots (strategy.close qty = 0.01 of 0.02) at a "
              "tick-based profit: criterion 1, as #436524."),
    # ---- FMZ-C, batch C260 (2026-10-22)
    483681: ("1", "Two 50 % partial take-profits (qty_percent = 50) with a fixed 0.1 quantity: "
              "criterion 1, as #436524."),
    483937: ("1", "Two-tranche exits: a 50 % partial take-profit (qty = entry qty / 2) then a "
              "break-even and trailing remainder keyed on the position size shrinking: criterion "
              "1, as #436524."),
    483943: ("1", "Pyramided strategy.order entries (up to five, gated on opentrades counts) with 50 "
              "% partial exits (qty_percent) per tranche: criterion 1, as #436524 / #442261."),
    # ---- FMZ-C, batch C261 (2026-10-22)
    484095: ("1", "A 50 % partial take-profit (qty_percent = 50) beside a trail whose trail_points is "
              "a price amount (atr x 10): criterion 1, as #436524 (the trail also fails criterion "
              "2)."),
    484588: ("1", "Seven partial take-profits of 14.28 % each (qty_percent): criterion 1, as #436524."),
    # ---- FMZ-C, batch C262 (2026-10-22)
    484769: ("2", "The Renko brick size 3.0 is a fixed price amount and the script has no backtest "
              "header to scale it (criterion 2)."),
    484914: ("1", "Turtle unit adding (Add Long / Add Short while held) gated on position_size / "
              "unitsSize, a size-dependent gate: criterion 1, as #442261 / #473389."),
    484915: ("1", "pyramiding = 2 with repeated dollar-cost-averaging entries (a new entry whenever "
              "the price is lower than the last): criterion 1, as #473389."),
    484920: ("1", "Martingale additions (up to 7 entries with the size doubled each time) on a VWMA / "
              "EMA filter: criterion 1, as #482783."),
    484924: ("2", "The take-profit and stop are fixed price amounts (50 / 30 'pips' x 0.1 = 5.0 / "
              "3.0, hard-coded for gold), added to the close (criterion 2, as #473377)."),
}

DUPLICATE_ON_READING = {
    128126: (127691, "Same rules and defaults as #127691 (SLOSS 2, N 200, M 4; parameters as arguments instead "
                     "of constants, HHV/LLV inline instead of named). Exact duplicate in behaviour (rule 7)."),
}

# FMZ-C (2026-10-16): candidates that read as volume users (rule 8 / skill check 8): held, not ported;
# written to review_decisions.csv as HELD_NEEDS_VOLUME.
HELD_ON_READING = {
    # ---- FMZ-C, batch C10 (2026-10-16)
    427574: ("8", "The trend filter uses vwma(close, 55) and vwma(close, 144): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C11 (2026-10-16)
    427734: ("8", "The combined condition uses DEVWRSI = ema(ema(vwma(rsi, 7), 7), 7): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C24 (2026-10-16)
    429461: ("8", "The moving-average rating includes vwma(close, 10/20/50/100/200): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C27 (2026-10-16)
    429562: ("8", "The trend filter compares vwma(close, 30) with vwma(close, 200): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C34 (2026-10-16)
    430278: ("8", "The trend line is vwma(k + k_two, 30): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C35 (2026-10-16)
    430385: ("8", "The trend line is vwma(hl2, 400): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C36 (2026-10-16)
    430551: ("8", "The grid lines are vwma(highest / lowest, 14): volume-weighted averages (check 8, held with the other volume users)."),
    430588: ("8", "The trend line is vwma(hl2, 400): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C45 (2026-10-17)
    431414: ("8", "The trend line is vwma(close, 33) and its RSI: a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C52 (2026-10-17)
    432347: ("8", "The band basis is vwma(hlc3, 50): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C53 (2026-10-17)
    432773: ("8", "The fast line is vwma(close, 3): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C64 (2026-10-17)
    433969: ("8", "The slow line is vwma(high, 7): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C69 (2026-10-17)
    434606: ("8", "One of the five averages is vwma(close, 136): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C72 (2026-10-17)
    434977: ("8", "The long and short exits test the close against vwma(close, 20): a volume-weighted average (check 8, held with the other volume users). (Also, on the 1-hour header chart no bar opens inside the 09:15-09:16 session window, so the day-range anchor is never set.)"),
    # ---- FMZ-C, batch C95 (2026-10-21)
    436658: ("8", "The long and short entries test the Hull line against rvwma3 = vwma(close, 42): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C117 (2026-10-22)
    439103: ("8", "The moving-average rules use ma20 / ma50 / ma100 = vwma(close, 20 / 50 / 100): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C133 (2026-10-22)
    440372: ("8", "The default moving-average type is VWMA: vwma(close, 66) against vwma(open, 66), volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C145 (2026-10-22)
    441075: ("8", "The MA rating includes vwma(close, 20): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C152 (2026-10-22)
    442220: ("8", "The channel averages include vwma(high, 12) and vwma(low, 12): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C206 (2026-10-22)
    468315: ("licence", "Held for Austin: the source says 'Copyright 2024 TRADINGWITHKAY. All rights reserved. Unauthorized use, distribution, and modification of this code are strictly prohibited.' The rules themselves are portable (RSI 14 zones 20 / 30 / 70 / 80 reversing, a 50-pip bracket = 50 price units at mintick x 10, 2-day bars). Port or reject on Austin's word; the review CSV labels every held row HELD_NEEDS_VOLUME (tool label)."),
    # ---- FMZ-C, batch C208 (2026-10-22)
    468337: ("8", "The trend filter compares vwma(close, 20) with vwma(close, 50): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C236 (2026-10-22)
    477603: ("8", "The default moving average of the wick length is ta.vwma: a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C243 (2026-10-22)
    482422: ("8", "The entry and exit lines are ta.vwma(close, 25) and ta.vwma(close, 8): volume-weighted averages (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch C244 (2026-10-22)
    482454: ("licence", "Held for Austin: the source carries a CC BY-NC-SA 4.0 licence (non-commercial, share-alike; the Andean Oscillator by alexgrover), so it is not ported until Austin decides (as #468315)."),
    # ---- FMZ-C, batch C246 (2026-10-22)
    482509: ("8", "The entry line is ta.vwma(close, 200) and the filters are weekly and daily VWMAs: volume-weighted averages (check 8, held with the other volume users)."),
}

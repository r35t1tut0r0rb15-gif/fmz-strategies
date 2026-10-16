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
}

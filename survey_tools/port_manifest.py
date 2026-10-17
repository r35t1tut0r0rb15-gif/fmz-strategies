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
    # ---- FMZ-C, batch L1 (2026-10-17)
    491038: [],
    491505: [],
    491506: [
        ("strategy(): 1 % of equity", 169, 169),
        ("Risk-reward, stop and trades-per-day inputs", 175, 177),
        ("Entries with the bracket and the daily count", 213, 223),
    ],
    491508: [
        ("strategy(): 10 % of equity", 197, 197),
        ("SL / TP percent", 207, 208),
        ("Bracket levels from the signal bar", 221, 224),
        ("Entries with the bracket", 227, 233),
    ],
    491514: [
        ("strategy(): 100 % of equity", 158, 158),
        ("TP / SL percent inputs", 164, 165),
        ("Bracket re-issued every bar", 191, 197),
    ],
    491890: [
        ("strategy(): 1 % of equity", 121, 121),
        ("Stop / target / capital / lot / trail inputs", 128, 132),
        ("Option-lot position size", 158, 158),
        ("Entries with the quantity", 161, 174),
        ("Close-checked trail, reversal, target and stop exits; daily counter reset", 177, 250),
    ],
    491891: [
        ("strategy(): 100 % of equity, initial capital 10", 93, 93),
        ("Risk and exit settings", 96, 103),
        ("Risk-based size, bracket and trail distances", 120, 133),
        ("Entries with the bracket and trail", 136, 142),
    ],
    491892: [
        ("strategy(): 100 % of equity", 116, 116),
    ],
    491897: [
        ("Risk input and ATR multiplier", 110, 117),
        ("Risk-based quantity, entries and bracket", 158, 168),
    ],
    491914: [
        ("strategy(): 10 % of equity", 98, 98),
        ("ATR trail distances", 114, 119),
        ("Entries with the trailing exits", 157, 164),
    ],
    492007: [
        ("strategy(): 10 % of equity", 120, 120),
        ("SL / TP method inputs", 133, 143),
        ("Moving stop / target, re-issued every bar", 182, 211),
    ],
    492009: [
        ("strategy(): 100 % of equity", 151, 151),
        ("Trailing stop + price-unit take profit, every bar", 199, 206),
    ],
    # ---- FMZ-C, batch L2 (2026-10-17)
    490060: [
        ("strategy(): 10 % of equity, commission 0.01 %", 179, 179),
        ("Profit factor", 185, 185),
        ("Swing stops and targets", 205, 213),
        ("Entries with the bracket", 224, 230),
    ],
    490517: [
        ("strategy(): 100 % of equity", 212, 212),
    ],
    490570: [
        ("strategy(): fixed quantity, initial capital 4000, commission", 184, 193),
        ("Trail, lock-in, ATR spacing, cooldown and order-size inputs", 203, 223),
        ("Base order with a USD quantity", 248, 252),
        ("Safety orders 1 / 2 (averaging in)", 257, 283),
        ("Close-checked trails and the exit", 288, 343),
    ],
    490787: [
        ("strategy(): fixed cash 10000", 179, 183),
        ("Risk amount and reward ratio inputs", 191, 192),
        ("Stops and risk-based position size", 254, 260),
        ("Entries with quantity and bracket", 263, 269),
    ],
    490794: [
        ("strategy(): 10 % of equity, no margin", 152, 152),
    ],
    490795: [],
    490798: [
        ("strategy(): 10 % of equity", 218, 218),
        ("Pip offset", 221, 222),
        ("Entries with the zone bracket", 296, 306),
    ],
    490804: [
        ("strategy(): 100 % of equity", 164, 164),
        ("Target and trail inputs", 168, 170),
        ("Entries with target and trail", 188, 194),
    ],
    490805: [
        ("strategy(): 10 % of equity", 173, 173),
        ("SL / TP pip inputs", 178, 180),
        ("Pip distances", 196, 198),
        ("Flat-only entries with the bracket", 204, 212),
    ],
    490914: [
        ("strategy(): 10 % of equity, commission 0.75 %", 173, 173),
    ],
    491035: [
        ("strategy(): 100 % of equity", 208, 208),
        ("Risk-reward and trail inputs", 216, 217),
        ("Trail distance in ticks", 242, 244),
        ("Entries with band stop, target and trail", 250, 258),
    ],
    # ---- FMZ-C, batch L3 (2026-10-17)
    489651: [
        ("strategy(): fixed quantity 375", 177, 177),
        ("Point distances", 194, 196),
        ("15:24 exit time", 199, 199),
        ("Entries with the bracket", 208, 215),
        ("Close-all at 15:24", 218, 219),
    ],
    489653: [
        ("strategy(): 20 % of equity", 173, 173),
        ("Tick trail re-placed every bar", 217, 226),
    ],
    489654: [
        ("strategy(): initial capital", 228, 228),
        ("0.5 %-risk position size", 254, 257),
        ("Flat-only entries with the open stop", 265, 278),
    ],
    489656: [
        ("Target and trail re-placed every bar", 196, 206),
    ],
    489658: [
        ("strategy(): 100 % of equity", 204, 204),
        ("TP / SL percent inputs", 215, 216),
        ("Entries with the bracket", 229, 235),
    ],
    489734: [
        ("strategy(): 100 % of equity, commission", 196, 196),
    ],
    489737: [
        ("strategy(): 20 % of equity, slippage 5", 242, 242),
        ("Tick trail re-placed every bar", 289, 300),
    ],
    489742: [
        ("Martingale inputs", 193, 195),
        ("Martingale bet", 206, 220),
        ("Entries with the bet", 223, 229),
    ],
    489966: [
        ("strategy(): 10 % of equity", 179, 179),
        ("ATR stop / target inputs", 189, 191),
        ("Bracket re-computed every bar", 235, 245),
    ],
    489975: [
        ("5 %-of-equity quantity", 247, 250),
        ("Entries with the quantity", 253, 256),
    ],
    490042: [
        ("strategy(): 10 % of equity", 211, 211),
        ("Stop / target / trail inputs", 219, 222),
        ("Bracket from the average price with the tick trail, every bar", 258, 262),
    ],
    # ---- FMZ-C, batch L4 (2026-10-17)
    489300: [
        ("strategy(): 10 % of equity, commission", 126, 126),
    ],
    489301: [
        ("strategy(): 100 % of equity, commission, slippage", 142, 142),
    ],
    489304: [
        ("strategy(): 25 % of equity, pyramiding 4", 117, 117),
    ],
    489309: [
        ("Stop / target tick inputs", 135, 138),
        ("Entries with the tick bracket", 205, 217),
    ],
    489311: [
        ("strategy(): 100 % of equity", 151, 151),
    ],
    489324: [],
    489332: [
        ("strategy(): 10 % of equity", 247, 247),
        ("Stop pips and TP ratio inputs", 272, 273),
        ("Stop / target levels", 276, 277),
        ("Entries with the bracket", 280, 286),
    ],
    489333: [
        ("strategy(): 2 % of equity", 177, 177),
        ("Risk-reward, stop pips and trail inputs", 180, 182),
        ("Pip size and stop", 201, 202),
        ("Entries with the bracket", 204, 210),
    ],
    489634: [
        ("strategy(): 10 % of equity", 173, 173),
        ("ATR stop / target inputs", 183, 185),
        ("Bracket re-computed every bar", 205, 215),
    ],
    489638: [
        ("strategy(): 100 % of equity", 186, 186),
        ("Entry with previous-low stop, 10 R target and break-even (ported as close-checked signals)", 204, 224),
    ],
    489646: [
        ("strategy(): 100 % of equity, pyramiding 0", 175, 175),
    ],
    489650: [
        ("Capital, risk and ATR multiplier inputs", 194, 197),
        ("Risk-based lot size", 200, 206),
        ("Entries with lot and bracket", 227, 234),
    ],
    # ---- FMZ-C, batch L5 (2026-10-17)
    489187: [
        ("strategy(): 10 % of equity", 141, 141),
        ("Fibonacci targets and stops", 164, 178),
        ("Entries with the bracket", 184, 190),
    ],
    489189: [
        ("strategy(): 1 % of equity", 182, 182),
        ("Stop / target percent inputs", 192, 193),
        ("Flat-only entries with the bracket", 228, 235),
    ],
    489198: [],
    489281: [
        ("Fixed-loss cap", 215, 215),
        ("Short setup: levels, quantity, entry", 218, 226),
        ("Short break-even stop and target", 229, 234),
        ("Long setup: levels, quantity, entry", 237, 245),
        ("Long break-even stop and target", 248, 253),
    ],
    489284: [
        ("strategy(): 10 % of equity", 210, 210),
        ("ATR stop and trail inputs", 223, 225),
        ("Stop and trail re-issued every bar", 255, 261),
    ],
    489285: [
        ("strategy(): 100 % of equity", 157, 157),
        ("Risk, reward, capital and ATR inputs", 160, 163),
        ("Stop distance and risk-based size", 169, 175),
        ("Entries with qty and the (inert) exits", 222, 228),
    ],
    489288: [
        ("strategy(): 1 % of equity", 181, 181),
        ("Swing stops and 2 R targets", 204, 211),
        ("Entries and exits re-issued every bar", 218, 222),
    ],
    489289: [
        ("strategy(): 100 % of equity", 198, 198),
        ("Stop / target percent inputs", 210, 211),
        ("Bracket from the average price with the entry", 235, 241),
    ],
    489292: [],
    489294: [
        ("Stop / break-even / target / trail inputs", 182, 185),
        ("Exit levels", 219, 231),
        ("Entries and exits re-issued every bar", 234, 240),
    ],
    489295: [
        ("strategy(): 10 % of equity", 180, 180),
        ("SL / TP percent", 183, 184),
        ("Entries with loss / profit", 233, 239),
    ],
    489296: [],
    489297: [
        ("strategy(): 100 % of equity", 177, 177),
    ],
    # ---- FMZ-C, batch L6 (2026-10-17)
    489056: [
        ("Pip inputs", 168, 170),
        ("Pip distances", 173, 175),
        ("Stop and (na) target levels", 196, 200),
        ("Flat-only entries with the bracket", 203, 209),
    ],
    489133: [],
    489149: [
        ("strategy(): margin settings", 166, 166),
        ("Stop / target / risk inputs and leverage", 176, 179),
        ("Risk-based, leveraged position size", 215, 218),
        ("Entry with the bracket", 224, 234),
    ],
    489152: [
        ("strategy(): 100 % of equity, initial capital", 159, 159),
        ("ATR stop and reward inputs", 165, 167),
        ("Bracket re-issued every bar", 195, 212),
    ],
    489153: [
        ("strategy(): 100 % of equity", 202, 202),
        ("3 % target from the average price", 224, 224),
    ],
    489154: [
        ("Risk-reward, stop and target levels", 198, 206),
        ("Entries with the bracket", 209, 216),
    ],
    489156: [
        ("strategy(): 100 % of equity, commission, slippage", 163, 163),
    ],
    489157: [
        ("strategy(): 100 % of equity", 187, 187),
    ],
    489158: [
        ("Stop / target percent inputs", 231, 232),
        ("Bracket re-issued every bar", 234, 234),
    ],
    489186: [],
    # ---- FMZ-C, batch L7 (2026-10-17)
    489007: [],
    489009: [
        ("strategy(): 10 % of equity, pyramiding 0", 125, 125),
    ],
    489010: [
        ("Long band-distance trail", 222, 225),
        ("Short band-distance trail", 239, 242),
    ],
    489016: [
        ("Risk multiplier input", 180, 180),
        ("Stop / target levels", 183, 187),
        ("Entries with the bracket", 190, 196),
    ],
    489017: [],
    489018: [
        ("Trail multiplier input", 168, 168),
        ("Close-checked trail (ported as signals)", 206, 217),
    ],
    489031: [
        ("strategy(): initial capital, margin", 161, 161),
        ("Risk input", 166, 166),
        ("Risk-based quantity", 186, 186),
        ("Entries with the bracket", 189, 195),
    ],
    489032: [
        ("Entries with the stored ATR levels", 224, 235),
        ("Exits at the stored levels", 239, 244),
    ],
    489034: [
        ("strategy(): 100 % of equity, initial capital", 110, 110),
    ],
    489035: [],
    489039: [
        ("strategy(): margin settings", 235, 235),
        ("Stop / target / risk inputs and leverage", 245, 248),
        ("Risk-based, leveraged position size", 299, 302),
        ("Entries with the bracket", 309, 320),
    ],
    489041: [
        ("strategy(): 10 % of equity", 161, 161),
        ("ATR, reward and multiplier inputs", 167, 169),
        ("Stop / target levels", 189, 190),
        ("Entry with the bracket", 193, 195),
    ],
    # ---- FMZ-C, batch L8 (2026-10-17)
    488848: [
        ("Trail and target tick inputs", 227, 228),
        ("Close-checked tick trail", 231, 256),
        ("Price-unit stop and entries with the bracket", 259, 270),
    ],
    488850: [
        ("strategy(): 10 % of equity", 176, 180),
        ("Entries with the 3 R bracket", 209, 229),
    ],
    488883: [
        ("ATR bracket levels", 220, 224),
        ("Entries with the bracket", 227, 233),
    ],
    488886: [
        ("strategy(): pyramiding 100", 170, 170),
        ("Dollar target / stop / trail inputs", 174, 190),
        ("Stop, break-even and trail management", 223, 336),
    ],
    488889: [
        ("Full-equity quantity", 221, 221),
        ("Entries with the quantity", 230, 236),
    ],
    488901: [
        ("ATR multiplier inputs", 144, 147),
        ("Target, trail, stop and break-even levels", 189, 200),
        ("Entries with the two exits", 203, 211),
    ],
    488907: [],
    488909: [
        ("strategy(): 100 % of equity", 143, 143),
        ("TP / SL factor inputs", 150, 151),
        ("Flat-only entries with the zone bracket", 196, 208),
    ],
    # ---- FMZ-C, batch L9 (2026-10-17)
    488537: [
        ("strategy(): margin, capital, equity percentage", 115, 115),
    ],
    488541: [
        ("TP / SL percent inputs", 145, 146),
        ("Bracket levels from the average price", 149, 152),
        ("Exits re-issued every bar", 155, 156),
    ],
    488543: [
        ("strategy(): equity percentage", 107, 107),
        ("Stop / target inputs", 114, 115),
        ("Stop and target distances", 136, 137),
        ("Gated entries with the bracket", 143, 156),
    ],
    # ---- FMZ-C, batch L10 (2026-10-17)
    488283: [
        ("Short tick bracket", 216, 222),
        ("Long tick bracket", 225, 228),
        ("Asia short tick bracket", 231, 234),
    ],
    488284: [
        ("strategy(): 100 % of equity", 172, 172),
        ("RR / SL inputs", 177, 178),
        ("ATR bracket levels", 191, 196),
        ("Entries with the bracket", 199, 205),
    ],
    488288: [
        ("Emergency stop input", 211, 211),
        ("Emergency stop", 239, 241),
    ],
    488382: [
        ("strategy(): 10 % of equity", 184, 184),
        ("Entries with the bracket", 213, 227),
    ],
    488417: [],
    488517: [
        ("strategy(): 100 % of equity", 176, 176),
        ("Trail / target / hard stop inputs", 289, 305),
        ("Hard stop and target levels", 438, 457),
        ("Trail updates", 460, 488),
        ("Exits with the trail", 502, 532),
    ],
    488518: [],
    488521: [
        ("ATR bracket inputs", 228, 231),
        ("Entries with the bracket", 234, 240),
    ],
    488523: [
        ("strategy(): 100 % of equity", 137, 137),
        ("RR / ATR inputs", 146, 148),
        ("ATR bracket levels", 181, 185),
        ("Entries with the bracket", 188, 194),
    ],
    488527: [
        ("strategy(): 10 % of equity", 171, 171),
    ],
    488536: [
        ("Stop / target tick inputs", 121, 123),
        ("Tick levels and close-checked exits (Both)", 265, 290),
        ("Tick levels and exits (Bullish Only)", 305, 316),
        ("Tick levels and exits (Bearish Only)", 331, 342),
    ],
    # ---- FMZ-C, batch L11 (2026-10-17)
    488140: [],
    488143: [
        ("MT4 lot input", 161, 161),
        ("strategy(): 5 % of equity", 173, 173),
    ],
    488152: [
        ("strategy(): 1 % of equity", 153, 153),
        ("Risk / ATR / RR / trail inputs", 156, 161),
        ("Stop, target and lot size", 175, 180),
        ("Bracket and trail exits re-issued every bar", 190, 196),
    ],
    488156: [
        ("strategy(): 1 % of equity", 177, 177),
        ("ATR stop input", 185, 185),
        ("Entries with the bracket", 212, 217),
    ],
    488165: [
        ("Tick target / stop", 204, 205),
        ("Entries with the tick bracket", 207, 215),
    ],
    488239: [
        ("strategy(): 100 % of equity", 186, 186),
    ],
    488241: [],
    488244: [],
    488268: [
        ("ATR stop / target multipliers", 220, 222),
        ("Entries with the locked-ATR bracket", 235, 249),
    ],
    488273: [
        ("strategy(): 10 % of equity", 170, 170),
        ("ATR bracket levels", 189, 193),
        ("Bracket exits re-issued every bar", 218, 221),
    ],
    488275: [
        ("strategy(): pyramiding 5", 219, 219),
        ("Stop / target / trail inputs", 224, 229),
        ("Fixed qty 5", 254, 255),
        ("Trail or bracket exits", 270, 288),
    ],
    488276: [],
    # ---- FMZ-C, batch L12 (2026-10-17)
    486571: [
        ("ATR inputs", 251, 253),
        ("Bracket levels", 274, 277),
        ("Exits re-issued every bar", 280, 281),
    ],
    486573: [],
    487999: [
        ("strategy(): cash quantity", 210, 210),
        ("Risk / leverage inputs", 216, 217),
        ("Leveraged quantity and stop distance", 238, 239),
        ("Entries with qty, stop and trail", 242, 256),
    ],
    488004: [
        ("ATR multiplier input", 144, 144),
        ("Bracket levels", 160, 164),
        ("Entries with the bracket", 171, 177),
    ],
    488008: [
        ("Decaying ATR stop / target", 174, 179),
        ("Entries with the bracket", 182, 188),
    ],
    488010: [
        ("strategy(): initial capital", 153, 153),
    ],
    488014: [
        ("Risk-based quantity", 185, 188),
        ("Entry with qty and the candle-low stop", 195, 197),
    ],
    488020: [
        ("strategy(): margin", 232, 232),
        ("Risk / leverage / fee / hold inputs", 238, 241),
        ("Risk-based quantity", 272, 276),
        ("Stop levels and ratchet", 279, 294),
        ("Time exit", 297, 299),
        ("Entries with qty and the stop", 302, 308),
    ],
    488021: [
        ("ATR stop inputs", 166, 167),
        ("Stop / target distances", 195, 196),
        ("Entries with the bracket", 199, 205),
    ],
    488023: [],
    488034: [
        ("strategy(): cash quantity", 186, 186),
        ("Wallet / TP / SL inputs", 190, 200),
        ("Bracket levels", 274, 278),
        ("Entries with qty and the bracket", 281, 288),
    ],
    488129: [
        ("strategy(): 100 % of equity", 207, 213),
    ],
    488133: [
        ("strategy(): 10 % of equity", 292, 292),
        ("15 % stop", 313, 313),
        ("Stop re-issued every bar", 329, 330),
    ],
    488134: [],
    # ---- FMZ-C, batch L13 (2026-10-17)
    485123: [
        ("Entries with qty 1", 259, 267),
    ],
    485125: [
        ("strategy(): 100 % of equity", 174, 174),
    ],
    485126: [
        ("strategy(): 10 % of equity", 138, 138),
    ],
    485283: [
        ("SL / TP inputs", 186, 187),
        ("Bracket re-issued every bar", 208, 212),
    ],
    485288: [
        ("Profit target input", 165, 165),
        ("Profit-target closes", 176, 177),
    ],
    485293: [],
    486561: [
        ("strategy(): 10 % of equity", 183, 183),
        ("SuperTrend stop and 2 R target (long)", 208, 209),
        ("SuperTrend stop and 2 R target (short)", 217, 218),
        ("Exits with the bracket", 222, 226),
    ],
    486564: [],
    486566: [
        ("Take-profit inputs (half position off)", 176, 178),
        ("Take-profit level", 211, 211),
        ("Partial / full take-profit closes", 218, 224),
    ],
    486567: [],
    # ---- FMZ-C, batch L14 (2026-10-17)
    484589: [
        ("Entries with the 10-bar extreme stop", 285, 290),
    ],
    484592: [],
    484595: [],
    484771: [
        ("Stop / target ticks and quantity", 259, 261),
        ("Entries with quantity", 278, 284),
        ("Tick bracket re-issued every bar", 287, 294),
        ("15:00 close-all", 297, 298),
    ],
    484773: [
        ("strategy(): 10 % of equity", 200, 200),
    ],
    484911: [
        ("strategy(): 10 % of equity", 206, 206),
    ],
    484912: [
        ("strategy(): 1 % of equity", 188, 188),
    ],
    484914: [
        ("Risk / units / stop inputs", 186, 193),
        ("Unit size and add-on conditions", 217, 222),
        ("Entries with qty and add-ons", 233, 246),
        ("Stop levels and trailing exits", 255, 269),
    ],
    484915: [
        ("strategy(): 50 % of equity, pyramiding 2", 184, 184),
        ("Entry distance / duration inputs", 193, 194),
        ("Entries, distance rule and time exits", 227, 259),
    ],
    484919: [],
    484921: [
        ("strategy(): 10 % of equity", 324, 324),
        ("ATR stop / target levels", 346, 352),
        ("Entries with the bracket", 355, 361),
    ],
    484924: [
        ("TP / SL pip inputs", 182, 187),
        ("Entries with the bracket", 634, 641),
    ],
    # ---- FMZ-C, batch L15 (2026-10-17)
    484101: [
        ("ATR bracket", 229, 232),
        ("Entries with the bracket", 239, 245),
    ],
    484109: [
        ("strategy(): 1 % of equity", 150, 150),
        ("Risk / SL / TP inputs", 153, 155),
        ("Risk-based quantity", 183, 185),
        ("Entries with qty and the bracket", 188, 194),
    ],
    484571: [
        ("strategy(): margin", 183, 183),
        ("Trail offset input", 186, 186),
        ("Trail levels", 211, 236),
        ("Trail exits", 251, 252),
    ],
    484578: [
        ("strategy(): 100 % of equity", 192, 192),
        ("ATR stop input", 197, 198),
        ("Entries with the bracket", 224, 237),
    ],
    484580: [
        ("ATR / RR inputs", 190, 191),
        ("Bracket levels", 205, 208),
        ("Entries with the bracket", 211, 217),
    ],
    484583: [
        ("strategy(): 2 % of equity", 185, 185),
        ("SL / TP inputs", 198, 201),
        ("Entries with the bracket", 225, 251),
    ],
    484584: [],
    # ---- FMZ-C, batch L16 (2026-10-17)
    484090: [
        ("Stop / delay inputs", 219, 220),
        ("Stop and delayed exits", 255, 267),
    ],
    484092: [
        ("strategy(): 2 % of equity", 213, 213),
        ("Bracket levels re-issued every bar", 241, 249),
    ],
    484094: [
        ("ATR bracket", 224, 227),
        ("Entries with the bracket", 271, 277),
    ],
    484096: [
        ("SL / TP pip inputs", 257, 262),
        ("Entries with the pip bracket", 314, 332),
    ],
    484098: [
        ("strategy(): 100 % of equity", 173, 173),
        ("ATR stop / target re-issued every bar", 227, 231),
    ],
    # ---- FMZ-C, batch L17 (2026-10-17)
    483791: [
        ("strategy(): 10 % of equity", 179, 179),
        ("ATR multipliers", 191, 193),
        ("Bracket levels", 200, 203),
        ("Entries with the bracket", 206, 212),
    ],
    483793: [
        ("strategy(): 10 % of equity", 179, 179),
        ("RR / SL tick inputs", 182, 183),
        ("Entries with the tick bracket", 205, 218),
    ],
    483794: [
        ("strategy(): initial capital", 274, 274),
    ],
    # ---- FMZ-C, batch L18 (2026-10-17)
    483509: [
        ("strategy(): 10 % of equity", 91, 91),
        ("Entries with the bracket", 130, 148),
        ("Bracket re-placed at +0.8 %", 152, 170),
    ],
    483510: [
        ("strategy(): defaults", 106, 106),
    ],
    483514: [
        ("strategy(): defaults", 130, 130),
        ("Exits at the stored zones", 178, 188),
    ],
    483518: [
        ("strategy(): defaults", 93, 93),
        ("SL / TP inputs", 101, 102),
        ("Exits re-issued every bar", 123, 131),
    ],
    483525: [
        ("strategy(): defaults", 99, 99),
        ("SL / TP from position_avg_price", 143, 152),
    ],
    483528: [
        ("strategy(): 10 % of equity", 103, 103),
        ("TP / SL inputs", 113, 114),
        ("Entry with the bracket", 144, 146),
    ],
    483674: [
        ("strategy(): defaults", 173, 173),
    ],
    483676: [
        ("strategy(): initial capital", 205, 205),
    ],
    483679: [
        ("strategy(): 10 % of equity", 169, 169),
        ("SL / TP / break-even inputs", 181, 183),
        ("Bracket levels from position_avg_price", 202, 212),
        ("Entries with the exits", 215, 221),
    ],
    483682: [
        ("Bracket levels", 178, 181),
        ("Risk-based qty", 184, 185),
        ("Entries and exits", 188, 196),
    ],
    483790: [
        ("strategy(): 100 % of equity", 161, 161),
        ("Tick SL / TP / break-even inputs", 169, 171),
        ("Entries with the bracket", 200, 208),
        ("Break-even exits", 211, 218),
    ],
    # ---- FMZ-C, batch L19 (2026-10-17)
    483121: [
        ("strategy(): 10 % of equity", 86, 86),
        ("SL / TP inputs", 94, 95),
        ("Entries with the bracket", 113, 125),
    ],
    483122: [
        ("strategy(): defaults", 95, 95),
    ],
    483123: [
        ("strategy(): defaults", 97, 97),
        ("Entries with the bar-extreme bracket", 126, 136),
    ],
    483124: [
        ("strategy(): 10 % of equity", 138, 138),
        ("TP / SL inputs", 143, 144),
        ("Exits from position_avg_price", 188, 198),
    ],
    483126: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    483130: [
        ("Risk input", 102, 102),
        ("ATR bracket", 115, 118),
        ("Risk-based qty", 121, 124),
        ("Entries with the bracket", 127, 133),
    ],
    483495: [
        ("strategy(): 10 % of equity", 91, 91),
    ],
    483496: [
        ("SL / RR inputs", 128, 130),
        ("Tick bracket from position_avg_price", 132, 139),
    ],
    483503: [
        ("Risk per trade input", 97, 97),
        ("Band stops and risk-based qty", 118, 129),
        ("Entries and band stops", 132, 139),
    ],
    483504: [
        ("strategy(): 100 % of equity", 93, 93),
        ("Leverage qty", 95, 98),
        ("Entries with the qty", 100, 104),
    ],
    483505: [
        ("strategy(): 100 % of equity", 97, 97),
        ("Stop / target inputs", 105, 106),
        ("Exits from position_avg_price", 186, 191),
    ],
    # ---- FMZ-C, batch L20 (2026-10-17)
    483103: [
        ("strategy(): 10 % of equity", 119, 119),
        ("Bracket levels and exit", 187, 191),
    ],
    483104: [
        ("strategy(): 10 % of equity", 99, 99),
        ("ATR multiplier inputs", 106, 107),
        ("Entry with the tick exit", 142, 144),
    ],
    483106: [
        ("strategy(): defaults", 101, 101),
    ],
    483108: [
        ("strategy(): commission / slippage", 101, 101),
        ("Entries with qty = 1", 123, 144),
    ],
    483111: [
        ("Stop / target sizes", 164, 165),
        ("Entries with the exits", 168, 183),
        ("16:00 close_all", 184, 185),
    ],
    483112: [
        ("strategy(): 100 % of equity", 116, 118),
    ],
    483113: [
        ("strategy(): 100 % of equity", 108, 108),
    ],
    483114: [
        ("Bracket levels", 118, 119),
        ("Entries with the bracket", 144, 150),
    ],
    483115: [
        ("strategy(): 10 % of equity", 106, 106),
        ("ATR / RR inputs", 109, 111),
        ("Bracket distances", 115, 117),
        ("Entries with the bracket", 129, 135),
    ],
    483116: [
        ("strategy(): defaults", 106, 106),
    ],
    483117: [
        ("strategy(): 100 % of equity", 105, 105),
    ],
    483118: [
        ("Risk per trade input", 110, 110),
        ("Risk-based qty", 122, 123),
        ("Trailing exit", 131, 131),
        ("Entry with the qty", 134, 135),
    ],
    483119: [
        ("SL / TP dollar inputs", 100, 101),
        ("Equity-scaled lot size", 104, 104),
        ("Entries with the lot size", 188, 192),
        ("Exits from position_avg_price", 199, 206),
    ],
    483120: [
        ("SL / target inputs", 105, 106),
        ("Entries with the bracket", 110, 123),
    ],
    # ---- FMZ-C, batch L21 (2026-10-17)
    483064: [
        ("strategy(): 100 % of equity", 100, 100),
    ],
    483066: [
        ("Swing targets and stops", 111, 122),
        ("Entries with the bracket", 129, 135),
    ],
    483072: [
        ("Stop / trail inputs", 101, 103),
        ("Stop and trailing levels", 124, 135),
    ],
    483073: [
        ("strategy(): margin settings", 120, 120),
    ],
    483080: [
        ("strategy(): defaults", 102, 102),
    ],
    483081: [
        ("Point stop and 3 R", 152, 153),
        ("Entries with the bracket", 155, 161),
        ("Trailing exits", 167, 176),
    ],
    483082: [
        ("strategy(): 10 % of equity", 95, 95),
        ("SL / RR / risk inputs", 113, 115),
        ("Risk-based qty and levels", 138, 140),
        ("Entries with the bracket", 143, 149),
    ],
    483087: [
        ("strategy(): defaults", 89, 89),
    ],
    483089: [
        ("TP / SL inputs", 113, 114),
        ("Entry with the bracket", 166, 169),
    ],
    483092: [
        ("strategy(): 1 % of equity", 103, 103),
        ("SL / RR inputs", 106, 107),
        ("Entries with the tick bracket", 137, 148),
    ],
    483096: [
        ("Swing stops and 2 R targets", 129, 132),
        ("Entries with the bracket", 135, 141),
    ],
    483102: [
        ("SL / TP pip inputs", 211, 212),
        ("Tick bracket levels", 215, 218),
        ("Entries with the bracket", 224, 230),
    ],
    # ---- FMZ-C, batch L22 (2026-10-17)
    483040: [
        ("strategy(): defaults", 101, 101),
    ],
    483042: [
        ("strategy(): defaults", 92, 92),
    ],
    483044: [
        ("ATR inputs", 89, 90),
        ("Stop levels", 114, 118),
        ("Entries with the stop", 125, 131),
    ],
    483045: [
        ("strategy(): defaults", 130, 130),
    ],
    483047: [
        ("strategy(): defaults", 86, 86),
    ],
    483048: [
        ("strategy(): 1000 % of equity", 100, 100),
    ],
    483050: [
        ("strategy(): 100 % of equity", 92, 98),
    ],
    483051: [
        ("strategy(): defaults", 103, 103),
    ],
    483052: [
        ("strategy(): defaults", 117, 117),
    ],
    483054: [
        ("Stop % input", 124, 124),
        ("Entries with the stop levels", 156, 170),
    ],
    483055: [
        ("strategy(): defaults", 116, 116),
    ],
    483061: [
        ("Channel stop levels", 171, 172),
        ("Exits re-issued every bar", 182, 183),
    ],
    483063: [
        ("strategy(): 100 % of equity", 82, 82),
        ("ATR inputs", 87, 88),
        ("Bracket levels", 104, 107),
        ("Entries with the bracket", 110, 116),
    ],
    # ---- FMZ-C, batch L23 (2026-10-17)
    482921: [
        ("strategy(): 100 % of equity", 98, 104),
        ("ATR bracket levels", 181, 184),
        ("Entries with the bracket", 189, 195),
    ],
    483020: [
        ("strategy(): 10 % of equity", 99, 99),
    ],
    483021: [
        ("strategy(): defaults", 137, 137),
    ],
    483023: [
        ("strategy(): initial capital", 101, 101),
    ],
    483026: [
        ("Risk percentage input", 102, 102),
        ("Stop / target / risk amount", 113, 117),
        ("Entries with the bracket", 124, 134),
    ],
    483027: [
        ("strategy(): defaults", 107, 107),
    ],
    483029: [
        ("strategy(): 2 % of equity", 94, 94),
        ("RR / trailing inputs", 103, 105),
        ("Entries with the exits", 126, 132),
    ],
    483032: [
        ("SL / TP multipliers", 132, 133),
        ("Bracket levels", 147, 150),
        ("Entries with the bracket", 153, 167),
    ],
    483035: [
        ("strategy(): defaults", 103, 103),
    ],
    483037: [
        ("strategy(): 2 % of equity", 101, 101),
        ("Trailing stop tick inputs", 117, 119),
        ("Trailing exits", 140, 142),
    ],
    483038: [
        ("strategy(): defaults", 90, 90),
    ],
    # ---- FMZ-C, batch L24 (2026-10-17)
    482890: [
        ("strategy(): 10 % of equity", 103, 105),
    ],
    482891: [
        ("strategy(): 10 % of equity", 96, 96),
        ("Stop % input", 110, 110),
        ("Close-based stops", 143, 151),
    ],
    482895: [
        ("strategy(): 10 % of equity", 85, 85),
        ("SL / TP inputs", 91, 92),
        ("Bracket levels and entries", 110, 123),
    ],
    482897: [
        ("strategy(): 1 % of equity", 139, 139),
        ("Lot size input", 142, 142),
        ("Entries with the lot size", 180, 184),
    ],
    482899: [
        ("strategy(): 100 % of equity, pyramiding 100", 94, 96),
        ("Stop / trail inputs", 101, 103),
        ("Trailing exits", 127, 130),
    ],
    482901: [
        ("strategy(): defaults", 101, 101),
        ("Target / stop levels", 122, 123),
        ("Entry with the bracket", 126, 128),
    ],
    482902: [
        ("strategy(): defaults", 102, 102),
        ("Point stop / target exits", 195, 196),
    ],
    482904: [
        ("strategy(): 100 % of equity", 105, 112),
        ("Trailing stop and exits", 166, 181),
    ],
    482906: [
        ("strategy(): 10 % of equity", 90, 91),
    ],
    482909: [
        ("Risk sizing and DCA settings", 124, 130),
        ("Buys with the qty", 139, 145),
        ("Take-profit close", 159, 165),
    ],
    482917: [
        ("strategy(): 10 % of equity", 105, 105),
        ("SL / TP inputs", 127, 128),
        ("Exits from position_avg_price", 209, 213),
    ],
    482919: [
        ("strategy(): 10 % of equity", 107, 107),
    ],
    482920: [
        ("strategy(): 100 % of equity", 96, 96),
    ],
    # ---- FMZ-C, batch L25 (2026-10-17)
    482878: [
        ("strategy(): 10 % of equity", 97, 97),
        ("Entries with the bracket", 129, 147),
    ],
    482879: [
        ("strategy(): 1 % of equity", 99, 99),
        ("RR / SL inputs", 109, 110),
        ("Bracket distances and levels", 136, 142),
        ("Entries with the bracket", 145, 151),
    ],
    482886: [
        ("strategy(): 1 % of equity", 106, 106),
    ],
    482887: [
        ("strategy(): defaults", 129, 129),
    ],
    482889: [
        ("SL / TP inputs", 106, 107),
        ("Entries with the bracket", 151, 166),
    ],
    # ---- FMZ-C, batch L26 (2026-10-17)
    482870: [
        ("Swing targets and stops", 122, 133),
        ("Entries with the bracket", 140, 146),
    ],
    482872: [
        ("strategy(): 10 % of equity", 111, 111),
        ("TP / SL inputs", 115, 116),
        ("Entries with the bracket", 149, 156),
    ],
    482873: [
        ("strategy(): 10 % of equity", 111, 111),
    ],
    482876: [
        ("strategy(): 10 % of equity", 108, 108),
        ("SL / TP / trail inputs", 127, 129),
        ("Entries with the exits", 150, 156),
    ],
    # ---- FMZ-C, batch L27 (2026-10-17)
    482849: [
        ("strategy(): 10 % of equity", 93, 93),
        ("RR / risk inputs", 98, 99),
        ("Stops, targets and risk qty", 114, 124),
        ("Entries with the bracket", 127, 134),
    ],
    482861: [
        ("strategy(): 10 % of equity", 111, 111),
        ("SL / TP inputs", 116, 117),
        ("Entries with the bracket", 134, 146),
    ],
    # ---- FMZ-C, batch L28 (2026-10-17)
    482859: [
        ("SL / TP inputs", 106, 107),
        ("Levels from position_avg_price", 139, 143),
        ("Entries with the bracket", 146, 152),
    ],
    482860: [
        ("Offset / stop point inputs", 96, 98),
        ("Point stops and RSI exits", 113, 130),
    ],
    482863: [
        ("SL / TP factors", 129, 130),
        ("Bracket levels", 134, 138),
        ("Entries with the exits", 141, 145),
    ],
    # ---- FMZ-C, batch L29 (2026-10-17)
    482838: [
        ("strategy(): defaults", 99, 99),
    ],
    482843: [
        ("strategy(): 10 % of equity", 105, 105),
    ],
    482846: [
        ("SL / TP inputs", 98, 99),
        ("Entry with the exit", 114, 119),
    ],
    482848: [
        ("strategy(): 5 % of equity", 130, 130),
        ("Risk / RR / stop inputs", 142, 144),
        ("Exits from the entry price", 176, 200),
    ],
    # ---- FMZ-C, batch L30 (2026-10-17)
    482820: [
        ("strategy(): defaults", 115, 115),
        ("Bracket re-issued every bar", 155, 160),
    ],
    482822: [
        ("strategy(): 100 % of equity", 115, 115),
        ("Profit stages and inert closes", 162, 201),
    ],
    482824: [
        ("strategy(): 1 % of equity", 117, 117),
        ("Stop / trail inputs", 147, 155),
        ("Entries with the exits", 158, 164),
    ],
    482826: [
        ("strategy(): defaults", 92, 92),
    ],
    482830: [
        ("strategy(): 100 % of equity, 0.1 % commission", 121, 121),
    ],
    482831: [
        ("strategy(): 10 % of equity", 132, 132),
    ],
    482832: [
        ("strategy(): defaults", 162, 162),
    ],
    482833: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    482836: [
        ("strategy(): defaults", 101, 101),
        ("Risk inputs", 117, 122),
        ("Entries with the bracket", 156, 171),
    ],
    482840: [
        ("strategy(): defaults", 102, 102),
        ("Point stop inputs (inert)", 106, 107),
        ("Exits (never placed)", 133, 146),
    ],
    482841: [
        ("strategy(): defaults", 101, 101),
        ("ATR stop inputs", 121, 122),
        ("Entries with the stops", 163, 177),
    ],
    # ---- FMZ-C, batch L31 (2026-10-17)
    482786: [
        ("strategy(): 100 % of equity, 0.1 % commission", 98, 98),
    ],
    482787: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    482788: [
        ("strategy(): defaults", 107, 107),
    ],
    482789: [
        ("strategy(): defaults", 93, 93),
    ],
    482792: [
        ("strategy(): 100 % of equity, commission 0.1, slippage 3", 91, 91),
    ],
    482793: [
        ("strategy(): defaults", 101, 101),
        ("Swing-low stop", 142, 148),
    ],
    482800: [
        ("strategy(): defaults", 90, 90),
    ],
    482803: [
        ("strategy(): 10 % of equity", 99, 99),
        ("Entry with the exit", 151, 156),
    ],
    482804: [
        ("strategy(): defaults", 107, 107),
    ],
    482805: [
        ("strategy(): 10 % of equity", 107, 107),
    ],
    482806: [
        ("strategy(): defaults", 125, 125),
    ],
    482809: [
        ("strategy(): 10 % of equity", 109, 109),
    ],
    482816: [
        ("strategy(): 10 % of equity", 97, 97),
        ("Stop / target inputs", 105, 107),
        ("Bracket from the average price", 134, 155),
    ],
    # ---- FMZ-C, batch L32 (2026-10-17)
    482678: [
        ("strategy(): defaults", 108, 108),
        ("RR / buffer inputs", 112, 113),
        ("Entries with the bracket", 130, 140),
    ],
    482684: [
        ("strategy(): 5 % of equity, commission, slippage", 89, 94),
        ("TP / SL multipliers", 105, 106),
        ("Entries with the bracket", 123, 129),
    ],
    482687: [
        ("strategy(): defaults", 29, 29),
    ],
    482764: [
        ("strategy(): defaults", 96, 96),
    ],
    482767: [
        ("strategy(): 10 % of equity, 0.1 % commission", 104, 104),
        ("ATR inputs", 116, 118),
        ("Entry with bracket and trail", 147, 151),
    ],
    482769: [
        ("strategy(): defaults", 109, 109),
    ],
    482771: [
        ("strategy(): defaults", 106, 106),
        ("Bar-extreme stops", 194, 198),
    ],
    482773: [
        ("strategy(): defaults", 97, 97),
        ("ATR target / stop inputs", 105, 106),
        ("Levels and close-based exits", 140, 150),
    ],
    482774: [
        ("strategy(): 100 % of equity", 114, 114),
        ("ATR / target inputs", 119, 121),
        ("Stop and target every bar", 132, 153),
    ],
    482775: [
        ("strategy(): 10 % of equity", 103, 103),
    ],
    482778: [
        ("strategy(): defaults, margin 100", 111, 111),
        ("Entries with the bracket", 140, 150),
    ],
    482779: [
        ("strategy(): 10 % of equity", 106, 106),
        ("ATR inputs", 111, 112),
        ("Bracket every bar", 125, 141),
    ],
    482785: [
        ("strategy(): 10 % of equity, pyramiding 0", 82, 87),
        ("SL / TP point inputs (0 = off)", 99, 100),
        ("Exit (inert at 0)", 190, 191),
    ],
    # ---- FMZ-C, batch L33 (2026-10-17)
    482590: [
        ("strategy(): defaults", 97, 97),
        ("SL / TP inputs and entries with the bracket", 142, 158),
    ],
    482591: [
        ("strategy(): defaults", 99, 99),
    ],
    482592: [
        ("strategy(): 200 % of equity", 89, 89),
        ("ATR", 97, 98),
        ("Stops and point targets", 107, 151),
    ],
    482593: [
        ("strategy(): defaults", 85, 85),
    ],
    482594: [
        ("strategy(): defaults", 99, 99),
        ("SL / TP inputs", 102, 103),
        ("Entries with the bracket", 148, 167),
    ],
    482595: [
        ("strategy(): 200 % of equity, pyramiding 0", 133, 133),
        ("Entries with the bracket", 161, 173),
    ],
    482600: [
        ("strategy(): defaults", 99, 99),
        ("ATR / target inputs", 110, 117),
        ("Exits every bar", 145, 149),
    ],
    482602: [
        ("strategy(): 200 % of equity", 99, 99),
        ("Entries with the bracket", 126, 132),
    ],
    482644: [
        ("strategy(): defaults", 99, 99),
        ("Entries with the bracket", 128, 143),
    ],
    482645: [
        ("strategy(): defaults", 99, 99),
    ],
    482669: [
        ("strategy(): defaults", 83, 83),
        ("Stop from the average price", 116, 122),
    ],
    482670: [
        ("strategy(): 2 % of equity", 105, 105),
        ("Per-ticker SL / TP table and 2 % risk sizing", 143, 163),
        ("Entries with the bracket", 170, 182),
    ],
    482673: [
        ("strategy(): 10 % of equity", 99, 99),
        ("ATR stop inputs", 106, 107),
        ("Entries with the stop", 125, 133),
    ],
    # ---- FMZ-C, batch L34 (2026-10-17)
    482473: [
        ("strategy(): defaults", 117, 117),
        ("Entries with the bracket", 155, 181),
    ],
    482474: [
        ("strategy(): 50000 cash per trade", 85, 87),
    ],
    482477: [
        ("strategy(): defaults", 121, 121),
        ("ATR stop inputs", 125, 126),
        ("Stop every bar", 148, 155),
    ],
    482489: [
        ("strategy(): defaults, margin 100", 87, 87),
        ("Bracket levels and entries", 111, 123),
    ],
    482500: [
        ("strategy(): defaults", 113, 113),
        ("SL / TP inputs", 120, 121),
        ("Entries with the bracket", 146, 152),
    ],
    482501: [
        ("strategy(): defaults, margin 100", 107, 107),
        ("Tick body and RR inputs", 111, 112),
        ("Entries with the stop and tick target", 177, 183),
    ],
    482502: [
        ("strategy(): 200 % of equity", 97, 97),
    ],
    482504: [
        ("strategy(): defaults", 99, 99),
        ("Risk inputs", 107, 111),
        ("Risk sizing and entries with the bracket", 128, 158),
    ],
    482510: [
        ("strategy(): 100 % of equity", 79, 79),
        ("SL / TP inputs and entries with the bracket", 99, 115),
    ],
    482512: [
        ("strategy(): defaults", 89, 89),
        ("Entry and cooldown", 160, 163),
        ("Take-profit options", 178, 207),
    ],
    482515: [
        ("strategy(): defaults", 136, 136),
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
    # ---- FMZ-C, batch L1 (2026-10-17)
    491510: ("1", "time windows shorter than the bars: a 90-second opening window and a 600-second "
              "hold measured from 09:30 GMT-4 on 7-minute bars; no 7-minute bar starts at 09:30 "
              "GMT-4, so as written it never trades"),
    # ---- FMZ-C, batch L2 (2026-10-17)
    490908: ("1", "1-minute security on a daily chart (request.security(..., \"1\", stoch(...))); as "
              "#430765"),
    490919: ("1", "the long target is the slow RMA, below the price whenever a long fires (RMA 9 > 21 "
              "> 50 and the close crossing above the mid RMA), shorts mirrored, so every trade "
              "exits at its own fill; the contract cannot express an exit at the entry fill "
              "(10-tick stop in price units too)"),
    # ---- FMZ-C, batch L3 (2026-10-17)
    489893: ("1", "5-minute security on a daily chart (request.security(..., \"5\", close) for the RSI "
              "and the bands); as #430765"),
    490059: ("1", "partial exits: strategy.order takes 25 % and 50 % of the position at two targets "
              "(qty fractions); as #430864"),
    # ---- FMZ-C, batch L4 (2026-10-17)
    489320: ("1", "1-, 5- and 15-minute securities on a daily chart (request.security for the KDJ "
              "inputs and the ATR); as #430765"),
    # ---- FMZ-C, batch L6 (2026-10-17)
    489135: ("1", "partial exits (strategy.exit qty_percent = 50 at the first target) and 15- / "
              "60-minute securities on a 2-day chart (lower timeframes; as #430765)"),
    489150: ("1", "grid / averaging-in with partial exits: strategy.close(\"Buy\", qty=...) sells part "
              "of the position at each grid step"),
    # ---- FMZ-C, batch L7 (2026-10-17)
    489006: ("1", "5- and 15-minute securities on a 2-day chart (request.security(..., \"5\" / \"15\", "
              "sma(close, 50))); as #430765"),
    # ---- FMZ-C, batch L8 (2026-10-17)
    488908: ("1", "partial exits: four strategy.exit tranches with qty = 25 % each at different "
              "targets"),
    # ---- FMZ-C, batch L10 (2026-10-17)
    488280: ("1", "pyramiding 5: each fair-value-gap retest opens its own entry with its own stop and "
              "2 R target, so the net position leaves in tranches at different levels, a partial "
              "exit (as #365389); the 15:15 close_all never matches the 2-day bars"),
    488287: ("1", "partial exits: strategy.close(qty_percent = 25) at the 2 ATR target and again when "
              "overextended, the rest at the SMA 10 cross (as #365389)"),
    488513: ("1", "time('1', '0930-1600:1234567') is na outside the 09:30-16:00 session, so hour(t) "
              "and minute(t) never equal 9:15-9:20 and the opening range is never established: as "
              "written it never trades (as #430384)"),
    # ---- FMZ-C, batch L11 (2026-10-17)
    488136: ("1", "strategy.entry('Buy', when = buy_signal) with no exit of any kind: the first long "
              "is held for the rest of the data, so there is no repeatable entry / exit rule (as "
              "#430776)"),
    488279: ("1", "the trend bias is request.security(syminfo.tickerid, '240', high / low) on the "
              "1-day header chart: a 4-hour resolution below the chart's, whose value per bar is "
              "undefined (as #430765)"),
    # ---- FMZ-C, batch L13 (2026-10-17)
    485292: ("1", "the trend test is request.security(syminfo.tickerid, '15', close) on the 1-day "
              "header chart: a 15-minute resolution below the chart's, whose value per bar is "
              "undefined (as #430765)"),
    486562: ("1", "the trend filter is request.security(syminfo.tickerid, '15', close > ta.sma(close, "
              "50)) on the 1-hour header chart: a 15-minute resolution below the chart's, whose "
              "value per bar is undefined (as #430765)"),
    486563: ("1", "the only exits are a 20-price-unit target and a 10-unit stop on the author's ~12 "
              "USD TRUMP_USDT (about 400 / 200 two-minute ATRs: inert there, as #490798); with "
              "them dropped a long is never closed, so there is no repeatable exit rule (as "
              "#430776)"),
    486570: ("1", "the daily and weekly RSI filters are request.security(..., 'D' / 'W', "
              "ta.rsi(close, 14), lookahead = barmerge.lookahead_on) without [1]: on every 3-hour "
              "bar they hold the current day's / week's final RSI, not known until it closes "
              "(reads the future, as #430661)"),
    # ---- FMZ-C, batch L14 (2026-10-17)
    484769: ("2", "a 3.0-price-unit Renko brick with no backtest header (no market or bar size to "
              "judge it against as an ATR multiple), and history offsets by the float brick size "
              "([3.0] bars): no generic, repeatable reading"),
    # ---- FMZ-C, batch L15 (2026-10-17)
    484582: ("1", "smoothK is var 0.0 but its first update takes ta.stoch's na (no 14-bar history "
              "yet) and na never recovers in the recursion, so bullZone / bearZone are never true "
              "and as written it never trades (as #430384)"),
    484588: ("1", "partial exits: seven strategy.exit take-profit tranches with qty_percent = 14.28 "
              "each at +0.5 % steps (as #365389)"),
    # ---- FMZ-C, batch L16 (2026-10-17)
    483937: ("1", "partial exits: the first tranche (qty = half the entry) leaves at entry + 1 ATR "
              "and the rest on a moving stop (as #365389)"),
    483943: ("1", "partial exits (strategy.exit qty_percent = 50 at a 1 R target for each tranche) on "
              "a ladder of up to five strategy.order adds: the size path is the strategy (as "
              "#365389, #426302)"),
    484095: ("1", "partial exits: strategy.exit('TP1', qty_percent = 50) at 1 ATR with the rest on a "
              "3 ATR target and a trail (as #365389)"),
    # ---- FMZ-C, batch L18 (2026-10-17)
    483508: ("1", "never exits as written: the only exit, strategy.close('MacdLE'), names no entry "
              "(the entry id is '多头'), and there are no shorts, so the strategy enters once and "
              "holds forever"),
    483526: ("1", "partial exits: strategy.close(qty = partialLot), half the position, at a 200-tick "
              "profit, the rest on the opposite cross (as #365389)"),
    483681: ("1", "partial exits: strategy.exit('TP1', qty_percent = 50) at 1.5 ATR and 'TP2' "
              "(qty_percent = 50) at 3 ATR (as #365389)"),
    # ---- FMZ-C, batch L19 (2026-10-17)
    483125: ("1", "never trades as written: the long needs close <= min(previous-day low, today's "
              "lowest low including this bar) - 10 points, but the close is never below its own "
              "bar's low (the short mirrored), so neither condition can be true"),
    483498: ("1", "partial exits: strategy.exit('Long_TP1', qty_percent = 50) at 1 R with the rest on "
              "a trail (as #365389)"),
    483500: ("1", "partial exits: three strategy.exit take-profits with qty_percent 33 / 33 / 34 at "
              "1.5 / 3 / 4.5 % (as #365389)"),
    # ---- FMZ-C, batch L21 (2026-10-17)
    483067: ("1", "the exits come from a stale price: avgPrice is a var updated only while a position "
              "is open, so on an entry from flat the stop, target and breakeven stop are set from "
              "the PREVIOUS trade's average price (the long's breakeven sell stop at 1.01 x that "
              "price can sit above the market); not a bracket of this trade, and the trail_points "
              "without trail_offset is inert"),
    483086: ("1", "partial exits: five strategy.exit take-profits of 20 % each (qty = position_size x "
              "0.2) plus adds while held (allowAddToPosition) (as #365389)"),
    # ---- FMZ-C, batch L22 (2026-10-17)
    483049: ("1", "partial exits: strategy.exit('Partial Exit', qty_percent = 50) at 5 ATR with the "
              "rest at 10 ATR or the stop (as #365389)"),
    # ---- FMZ-C, batch L23 (2026-10-17)
    483022: ("1", "not a market strategy: the 'fear and greed' values are a hard-coded 8-number "
              "placeholder array cycled by bar_index, so the signals are a fixed 8-bar cycle "
              "unrelated to prices"),
    483033: ("1", "never trades on history as written: the 07:00-09:15 window is built with "
              "timestamp(year(timenow), month(timenow), dayofmonth(timenow), ...), i.e. only on "
              "the day the script runs; also tick distances on DOGE_USDT"),
    483034: ("1", "the exits are re-placed on every bar from the CURRENT close with a 0 % stop "
              "(stoppct = 0): the long's stop and the short's limit sit at the latest close, so "
              "every trade ends at the next touch of the previous close; a 0 % stop of the fill "
              "is not a bracket the house engine can express"),
    # ---- FMZ-C, batch L24 (2026-10-17)
    482916: ("1", "pyramiding adds (up to 15 entries) and a partial close: strategy.close('Buy', "
              "qty_percent = 50) at the target (as #365389, #490570)"),
    # ---- FMZ-C, batch L30 (2026-10-17)
    482817: ("1", "a LOWER timeframe on a higher chart: the spike test runs through "
              "request.security(..., '60', ...) on the 3-hour chart (as #430765); the bracket "
              "also comes from strategy.position_avg_price"),
    482835: ("1", "not a market strategy: the signal is prediction = math.random() x 2 - 1, so the "
              "entries are random draws, not reproducible (as #483022)"),
    482837: ("1", "a LOWER timeframe on a higher chart: the higher-timeframe stochastic is "
              "request.security(..., '30', ...) on the 1-day chart (as #430765)"),
    # ---- FMZ-C, batch L31 (2026-10-17)
    482802: ("1", "not a strategy: a strategy-tester template whose entries, targets and stop are "
              "input.source links to other indicators; with the defaults (close > 0) every bar is "
              "both a long and a short entry from flat, with the targets at the signal bar's high "
              "/ low"),
    # ---- FMZ-C, batch L32 (2026-10-17)
    482783: ("1", "martingale adds: strategy.order doubles the quantity on every bar 5 % below the "
              "15-bar high close, the take-profit sits 5 % above the quantity-weighted average of "
              "those adds and a forced close comes after 10 adds; without the adds (sizing, not "
              "ported) the exits have no meaning (as #483086)"),
    # ---- FMZ-C, batch L33 (2026-10-17)
    482672: ("1", "no entry signal: a DCA bot that buys whenever flat and adds up to 30 scaled safety "
              "orders (pyramiding 999, sizing) and takes profit 1 % above their average; without "
              "the adds (not ported) nothing but a buy-and-take-1 % loop remains (as #483086)"),
    # ---- FMZ-C, batch L34 (2026-10-17)
    482499: ("1", "partial exits: strategy.exit('止盈一半', qty_percent = 50) takes half at the 50-bar "
              "extreme (as #430864)"),
    482506: ("1", "adds with per-add exits: pyramiding 50, up to four long entries a week at fixed "
              "point offsets (155-775) below the weekly pivot, each with its own limit target; "
              "the net position is closed piece by piece (partial exits, as #430864); the point "
              "offsets are also price units"),
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
    # ---- FMZ-C, batch L6 (2026-10-17)
    489134: ("8", "The basis is vwma(hlc3, 200): a volume-weighted average (check 8, held with the other volume users)."),
    # ---- FMZ-C, batch L14 (2026-10-17)
    484920: ("8", "The signal is the close crossing vwma(close, 100) with vwma(close, 100) > ema(close, 200): a volume-weighted average (check 8, held with the other volume users); the entries are also a martingale add ladder."),
    # ---- FMZ-C, batch L34 (2026-10-17)
    482509: ("8", "The entry and exit use vwma(close, 200) and a weekly vwma(close, 50): volume-weighted averages (check 8, held with the other volume users)."),
}

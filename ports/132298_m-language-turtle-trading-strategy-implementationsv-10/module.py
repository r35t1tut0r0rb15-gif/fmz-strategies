"""Turtle 20-bar channel breakout with 10-bar channel exit and 2-ATR close stop (V1.0 demo).
Port of FMZ strategy #132298 "M-Language-Turtle-Trading-strategy-implementationsV-10".

Source
    https://www.fmz.com/strategy/132298 (MyLanguage, author "发明者量化-小小梦", FMZ last modified
    2019-01-28 11:16:10). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 196-212)
    ATR = MA(TR,26); HH = HV(H,20); LL = LV(L,20)          (prior bars, current excluded)
    CROSSUP(C,HH) && ISLASTBK=0 && ISLASTSK=0 && BARPOS>=26 -> BK
    CROSSDOWN(C,LL) && ISLASTBK=0 && ISLASTSK=0 -> SK
    C >= BKPRICE+0.5*ATR && BKVOL<4 units && ISLASTBK -> BK (add; short mirror)
    C <= BKPRICE-2*ATR && BKVOL>0 -> SP;   C >= SKPRICE+2*ATR && SKVOL>0 -> BP
    CROSSUP(H,HV(H,10)) && SKVOL>0 -> BP;  CROSSDOWN(L,LV(L,10)) && BKVOL>0 -> SP

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Daily bars (backtest period 1d) are broker days (17:00 New York); close-price model, one
      signal per bar in source order.
    * Adds are sizing (not ported) but move BKPRICE, which the 2-ATR stop uses, so the add rule
      is kept as state: on an add bar, ref := C, up to 4 units; being earlier in the source, an
      add bar is that bar's one signal (the exits are checked from the next bar).
    * The BARPOS>=26 guard is on the long entry only, as written.
    * Entries only from flat. Opposite entries cannot occur; portfolio_kwargs also returns
      upon_opposite_entry="ignore" (rule 6).
    * Lot formula (1 % of equity per ATR), MTC cap, TRADE_AGAIN -> original_sizing.txt.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_132298_turtle_20_breakout_v10"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_period": [10, 20, 30],
    "exit_period": [5, 10, 15],
    "stop_atr": [1.5, 2.0, 3.0],
}
DEFAULT_PARAMS = {"entry_period": 20, "exit_period": 10, "atr_period": 26, "stop_atr": 2.0,
                  "add_atr": 0.5, "max_units": 4}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _true_range(bars):
    prev_close = bars["close"].shift(1)
    return pd.concat([bars["high"] - bars["low"],
                      (prev_close - bars["high"]).abs(),
                      (prev_close - bars["low"]).abs()], axis=1).max(axis=1, skipna=False)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    high, low, close = (bars_df[k] for k in ("high", "low", "close"))
    atr = _true_range(bars_df).rolling(int(p["atr_period"])).mean().to_numpy()
    hh = high.rolling(int(p["entry_period"])).max().shift(1).to_numpy()   # HV(H,20)
    ll = low.rolling(int(p["entry_period"])).min().shift(1).to_numpy()
    xh = high.rolling(int(p["exit_period"])).max().shift(1).to_numpy()    # HV(H,10)
    xl = low.rolling(int(p["exit_period"])).min().shift(1).to_numpy()
    c, h, lo = close.to_numpy(), high.to_numpy(), low.to_numpy()

    def up(a, b, i):
        return i > 0 and a[i] > b[i] and a[i - 1] <= b[i - 1]

    def down(a, b, i):
        return i > 0 and a[i] < b[i] and a[i - 1] >= b[i - 1]

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, units = 0, np.nan, 0
    for i in range(m):
        if pos == 0:
            if up(c, hh, i) and i + 1 >= int(p["atr_period"]):
                le[i], pos, ref, units = True, 1, c[i], 1
            elif down(c, ll, i):
                se[i], pos, ref, units = True, -1, c[i], 1
            continue
        if units < p["max_units"] and pos * (c[i] - ref) >= p["add_atr"] * atr[i]:
            ref, units = c[i], units + 1      # add bar: moves the stop reference only
            continue
        if pos == 1 and (c[i] <= ref - p["stop_atr"] * atr[i] or down(lo, xl, i)):
            lx[i], pos = True, 0
        elif pos == -1 and (c[i] >= ref + p["stop_atr"] * atr[i] or up(h, xh, i)):
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}

"""Turtle channel breakout (20/55-bar entry, 10-bar exit, 2-ATR close stop, skip-after-win filter).
Port of FMZ strategy #126968 "麦语言海龟策略体验" (MyLanguage turtle strategy demo).

Source
    https://www.fmz.com/strategy/126968 (MyLanguage, author "Zero", FMZ last modified
    2021-10-27 12:32:17). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 59-87)
    TR as usual; ATR = MA(TR, 20)  (simple MA of true range)
    HH = HV(H,20), LL = LV(L,20), HHH = HV(H,55), LLL = LV(L,55)   (prior bars, current excluded)
    flat: CROSSUP(C,HH) && ISLASTFAILURE -> BK;  CROSSDOWN(C,LL) && ISLASTFAILURE -> SK
          CROSSUP(C,HHH) -> BK;                CROSSDOWN(C,LLL) -> SK
    add:  C >= BKPRICE + 0.5*ATR && BKVOL < 4 units -> BK (pyramid; short mirror)
    NEEDSTOP  = long: C <= BKPRICE - 2*ATR   short: C >= SKPRICE + 2*ATR
    NEEDLEAVE = long: CROSSDOWN(L, LV(L,10)) short: CROSSUP(H, HV(H,10))
    NEEDSTOP or NEEDLEAVE -> CLOSEOUT;  ISLASTFAILURE := NEEDSTOP (starts at 1)

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Daily bars (backtest period 1d) are broker days (17:00 New York).
    * The script sets MULTSIG (intrabar signals); the port evaluates every rule once on the
      completed bar (house rule for scripts that poll the forming bar).
    * BKPRICE is the close of the latest BK signal bar. The pyramid adds are sizing (not
      ported: no size changes), but they move BKPRICE, which the 2-ATR stop refers to, so the
      port keeps the add rule as state: on a bar where C >= ref + add_atr*ATR and fewer than
      max_units units are on, ref := C. If an exit fires on a bar, it wins over an add.
    * ATR in the stop is the current bar's (as written). ATR multiples are already
      volatility-normalised (criterion 2 PASS).
    * Entries only from flat (ISLASTBK=0 && ISLASTSK=0); after an exit, the next entry is
      evaluated from the following bar. Opposite entries cannot occur; portfolio_kwargs also
      returns upon_opposite_entry="ignore" (rule 6).
    * Lot sizing (1 % of equity per ATR), unit cap, TRADE_AGAIN/MULTSIG counts -> original_sizing.txt.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_126968_turtle_20_55_breakout"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_period": [10, 20, 30],
    "long_period": [40, 55, 80],
    "stop_atr": [1.5, 2.0, 3.0],
}
DEFAULT_PARAMS = {"short_period": 20, "long_period": 55, "exit_period": 10, "atr_period": 20,
                  "stop_atr": 2.0, "add_atr": 0.5, "max_units": 4}


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
    hh = high.rolling(int(p["short_period"])).max().shift(1).to_numpy()    # HV(H,20)
    ll = low.rolling(int(p["short_period"])).min().shift(1).to_numpy()
    hhh = high.rolling(int(p["long_period"])).max().shift(1).to_numpy()   # HV(H,55)
    lll = low.rolling(int(p["long_period"])).min().shift(1).to_numpy()
    xh = high.rolling(int(p["exit_period"])).max().shift(1).to_numpy()    # HV(H,10)
    xl = low.rolling(int(p["exit_period"])).min().shift(1).to_numpy()
    c, h, lo = close.to_numpy(), high.to_numpy(), low.to_numpy()

    def up(a, b, i):
        return i > 0 and a[i] > b[i] and a[i - 1] <= b[i - 1]

    def down(a, b, i):
        return i > 0 and a[i] < b[i] and a[i - 1] >= b[i - 1]

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, units, last_failure = 0, np.nan, 0, True
    for i in range(m):
        if pos == 0:
            if (up(c, hh, i) and last_failure) or up(c, hhh, i):
                le[i], pos, ref, units = True, 1, c[i], 1
            elif (down(c, ll, i) and last_failure) or down(c, lll, i):
                se[i], pos, ref, units = True, -1, c[i], 1
            continue
        stop = c[i] <= ref - p["stop_atr"] * atr[i] if pos == 1 else c[i] >= ref + p["stop_atr"] * atr[i]
        leave = down(lo, xl, i) if pos == 1 else up(h, xh, i)
        if stop or leave:
            (lx if pos == 1 else sx)[i] = True
            pos, last_failure = 0, bool(stop)
            continue
        if units < p["max_units"] and pos * (c[i] - ref) >= p["add_atr"] * atr[i]:
            ref, units = c[i], units + 1   # pyramid add: moves the stop reference only

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}

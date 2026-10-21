"""Up / down true-range WMA spread turning up from below zero, broker days, long only: from flat, the first bar of a rising run of the smoothed fast-minus-slow spread (two rises, still under 0) buys; a falling
run above 0 closes the long while it is in profit.
Port of FMZ strategy #439074 "True Range Based Weighted Moving Average Cross Period Strategy" (Rangos [https://t.me/Bitcoin_Maclen]).

FMZ source id: 439074

Source
    https://www.fmz.com/strategy/439074 (PineScript v5, FMZ last modified 2024-01-17 15:09:28).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 131-191), WMA 10 / 30, smoothing 10; contract base 50000 / (16 x close); take 6.5 % and safety -6 % (adds); window true
    sube = close > close[1] ? tr : 0, baja = close < close[1] ? tr : 0;  ind = wma(wma(sube, 10) - wma(baja, 10) - (wma(sube, 30) - wma(baja, 30)), 10)
    long = ind rising two bars and ind < 0;  flat and long and not long[1] -> entry BUY1;  BUY2-BUY5 adds at -6 % (2x, 4x, 8x sizes);  short (falling two bars, above 0) and open profit > 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() default pyramiding (one entry per direction) blocks the BUY2-BUY5 adds, and they
      are sizing in any case: the port holds one position. The open-profit test reads the close against
      the fill price. tr is na on the first bar. window is true. Long only. The contract sizes are sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested profit exit.
    2 generic: PASS, true-range WMA spread turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the contract sizes and the add levels stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439074_true_range_wma_spread_turn_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "corto": [10, 5],
    "largo": [30, 60],
}
DEFAULT_PARAMS = {"corto": 10, "largo": 30, "suavizado": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    sube = tr.where(c > pc, 0.0).where(tr.notna())
    baja = tr.where(c < pc, 0.0).where(tr.notna())
    a, b = int(p["corto"]), int(p["largo"])
    fast = _wma(sube, a) - _wma(baja, a)
    slow = _wma(sube, b) - _wma(baja, b)
    ind = _wma(fast - slow, int(p["suavizado"]))
    long_ = ((ind.shift(1) < ind) & (ind.shift(2) < ind.shift(1)) & (ind < 0)).to_numpy()
    short_ = ((ind.shift(1) > ind) & (ind.shift(2) > ind.shift(1)) & (ind > 0)).to_numpy()
    first_long = long_ & ~np.concatenate(([False], long_[:-1]))
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_e, pend_x, ep = 0, False, False, np.nan
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e, ep = 1, False, ov[i]
        if pos == 0 and first_long[i] and i + 1 < m:
            le[i], pend_e = True, True
        elif pos == 1 and short_[i] and cv[i] > ep:
            lx[i], pend_x = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

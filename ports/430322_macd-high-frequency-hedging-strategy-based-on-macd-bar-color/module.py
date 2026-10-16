"""Sonic R channel with a linear-regression line and MACD colours, broker days: the regression (89) crossing up through the
EMA 34 of lows while rising arms longs, and a green bar closing above the regression inside the channel (MACD histogram
not falling below zero) goes long; the mirror goes short; the opposite channel crosses disarm and close.
Port of FMZ strategy #430322 "基于MACD柱色和线性回归的高频对冲策略High-Frequency-Hedging-Strategy-Based-on-MACD-Bar-Color-and-Linear-Regression" (Sonic R + Linear Reg + Kumo Cloud + Barcolor MACD).

FMZ source id: 430322

Source
    https://www.fmz.com/strategy/430322 (PineScript v2, FMZ last modified 2023-10-27 10:42:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 188-256), EMA 89, channel EMA 34 of high / low / close, linreg 89, MACD 12 / 26 / 9
    linereg = linreg(close, 89, 0); pacL / pacH = ema(low / high, 34); signalMA = ema(close, 89)
    conbuy  = crossover(linereg, pacL) and rising(linereg, 5) ? 1 : crossover(linereg, pacH) or
              (crossunder(linereg, pacL) and pacL < signalMA) ? -1 : conbuy[1]
    consell = crossunder(linereg, pacH) and falling(linereg, 5) ? 1 : crossunder(linereg, pacL) or
              (crossover(linereg, pacH) and pacH > signalMA) ? -1 : consell[1]
    golong = conbuy == 1 and close > open and open < pacH and close > linereg and hisdown != 1 -> entry long
    goshort = consell == 1 and close < open and open > pacL and close < linereg and hisup != 1 -> entry short
    conbuy == -1 -> close long;  consell == -1 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * hisup / hisdown are the source's MACD-histogram colour states (delta = MACD - EMA 9 of MACD).
      rising(x, 5) is x above each of its previous 5 values (falling mirrored). linreg(close, 89, 0)
      is the least-squares line's value at the current bar.
    * A close acts on the position held at the start of the bar unless the bar's entry reverses it.
      The ichimoku cloud only plots; the TP / SL block is commented out. The strategy() line is
      commented out in the corpus copy: orders read as written (as #429505).
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages, a regression line and MACD states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out order size stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430322_sonic_r_linreg_macd"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_signal": [89, 50],
    "hilo_len": [34, 20],
}
DEFAULT_PARAMS = {"ema_signal": 89, "hilo_len": 34, "fast": 12, "slow": 26, "macd_len": 9}


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


def _linreg(y, n):
    """ta.linreg(y, n, 0): the least-squares line over the last n values, evaluated at the current bar."""
    w = np.arange(n, dtype=float) - (n - 1) / 2
    ww = float(np.dot(w, w))
    slope = y.rolling(n).apply(lambda a: np.dot(a, w) / ww, raw=True)
    return y.rolling(n).mean() + slope * (n - 1) / 2


def _states(up, dn):
    m = len(up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n, hl = int(p["ema_signal"]), int(p["hilo_len"])
    pac_l = lo.ewm(span=hl, adjust=False).mean()
    pac_h = h.ewm(span=hl, adjust=False).mean()
    sig_ma = c.ewm(span=n, adjust=False).mean()
    lr = _linreg(c, n)
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["macd_len"]), adjust=False).mean()
    d1 = delta.shift(1)
    hisup = _states(((delta > d1) & (delta > 0)).to_numpy(), (delta < d1).to_numpy())
    hisdown = _states(((delta < d1) & (delta < 0)).to_numpy(), (delta > d1).to_numpy())
    rising = lr > lr.shift(1).rolling(5).max()
    falling = lr < lr.shift(1).rolling(5).min()
    xo_l = (lr > pac_l) & (lr.shift(1) <= pac_l.shift(1))
    xu_l = (lr < pac_l) & (lr.shift(1) >= pac_l.shift(1))
    xo_h = (lr > pac_h) & (lr.shift(1) <= pac_h.shift(1))
    xu_h = (lr < pac_h) & (lr.shift(1) >= pac_h.shift(1))
    conbuy = _states((xo_l & rising).to_numpy(), (xo_h | (xu_l & (pac_l < sig_ma))).to_numpy())
    consell = _states((xu_h & falling).to_numpy(), (xu_l | (xo_h & (pac_h > sig_ma))).to_numpy())
    golong = (conbuy == 1) & (c > o).to_numpy() & (o < pac_h).to_numpy() & (c > lr).to_numpy() & (hisdown != 1)
    goshort = (consell == 1) & (c < o).to_numpy() & (o > pac_l).to_numpy() & (c < lr).to_numpy() & (hisup != 1)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if golong[i]:
            pos = 1
        elif goshort[i]:
            pos = -1
        if start == 1 and pos == 1 and conbuy[i] == -1:
            pos = 0
        if start == -1 and pos == -1 and consell[i] == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

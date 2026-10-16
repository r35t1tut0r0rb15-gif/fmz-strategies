"""Bollinger-width expansion in the EMA trend with chandelier exits, broker days: the 40-bar Bollinger width rising
more than 9 % in a bar while EMA 20 is above EMA 50 goes long (mirror short); the close crossing below the
22-bar high minus 4 ATR closes a long (mirror for shorts).
Port of FMZ strategy #429576 "EMA Oscillation Reversal System Strategy" (CHI).

FMZ source id: 429576

Source
    https://www.fmz.com/strategy/429576 (PineScript v4, FMZ last modified 2023-10-18 12:23:13).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 181-257), chandelier 22 x 4, EMA 50 / 20, BB 40 x 2, widen 9 %
    width = (upper - lower) / basis (BB 40 x 2); cross = crossover(change(width) / width[1] x 100, 9)
    ema20 > ema50 and cross -> entry long; ema20 < ema50 and cross -> entry short
    crossunder(close, highest(high,22) - 4 atr(22)) -> close long; crossover(close, lowest(low,22) + 4 atr(22)) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * close[barstate.islast ? 1 : 0] is the close on every historical bar (the last-bar switch is a
      real-time artifact). The MA type input defaults to EMA.
    * An entry on the other side reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, band-width changes and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_429576_bb_width_expansion_chandelier"
FAMILY = "volatility_squeeze"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "thresh": [9.0, 5.0],
    "f": [4.0, 3.0],
}
DEFAULT_PARAMS = {"n": 22, "f": 4.0, "period": 50, "period2": 20, "bb_period": 40, "bb_mult": 2.0, "thresh": 9.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["n"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n)
    lstop = h.rolling(n).max() - atr * p["f"]
    sstop = lo.rolling(n).min() + atr * p["f"]
    m1 = c.ewm(span=int(p["period"]), adjust=False).mean()
    m2 = c.ewm(span=int(p["period2"]), adjust=False).mean()
    nb = int(p["bb_period"])
    basis, dev = c.rolling(nb).mean(), c.rolling(nb).std(ddof=0) * p["bb_mult"]
    width = (2 * dev) / basis
    roc = (width - width.shift(1)) / width.shift(1) * 100
    cross = (roc > p["thresh"]) & (roc.shift(1) <= p["thresh"])
    lc, sc = (cross & (m2 > m1)).to_numpy(), (cross & (m2 < m1)).to_numpy()
    out_l = ((c < lstop) & (c.shift(1) >= lstop.shift(1))).to_numpy()
    out_s = ((c > sstop) & (c.shift(1) <= sstop.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        elif pos == 1 and out_l[i]:
            pos = 0
        elif pos == -1 and out_s[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}

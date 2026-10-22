"""Two SuperTrends (14 x 3 and 14 x 6) with a smoothed CCI 20, daily bars: the close under the tight line but over the wide one with the SMA 5 of the CCI under -100 goes long, the mirror short; the close
leaving that band, or the raw CCI past the opposite 100 level, closes; reversing.
Port of FMZ strategy #442810 "超趋势和CCI策略的短线交易Supertrend-and-CCI-Scalping-Strategy" (Supertrend & CCI Strategy Scalp).

FMZ source id: 442810

Source
    https://www.fmz.com/strategy/442810 (PineScript v5, FMZ last modified 2024-02-26 10:39:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-228), SuperTrend 14 / 3 and 14 / 6; CCI 20 on hlc3 (mean deviation); smoothing SMA 5; level 100
    long = st1 > close and st2 < close and sma(cci, 5) < -100 -> entry Long, isLong;  short = st1 < close and st2 > close and sma(cci, 5) > 100 -> entry Short, isShort
    isLong: st1 < close or st2 > close or cci > 100 -> close Long;  isShort: st1 > close or st2 < close or cci < -100 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags follow the latest entry signal; each close acts only on its own held id. ta.dev is the
      mean absolute deviation. The CCI level input only labels; the conditions use 100 as written.
      Ported in call order with one position at a time. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend band with a CCI extreme.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442810_supertrend_band_cci_extreme_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor2": [6.0, 4.0],
    "cci_len": [20, 14],
}
DEFAULT_PARAMS = {"factor2": 6.0, "cci_len": 20, "factor1": 3.0, "atr1": 14, "atr2": 14, "smooth": 5}


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


def _supertrend(h, lo, c, factor, n):
    """Pine's ta.supertrend(factor, atrPeriod): (line, direction), direction -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return st, d


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * md)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s1 = pd.Series(_supertrend(h, lo, c, float(p["factor1"]), int(p["atr1"]))[0], index=c.index)
    s2 = pd.Series(_supertrend(h, lo, c, float(p["factor2"]), int(p["atr2"]))[0], index=c.index)
    cci = _cci((h + lo + c) / 3, int(p["cci_len"]))
    sm = cci.rolling(int(p["smooth"])).mean()
    lg = ((s1 > c) & (s2 < c) & (sm < -100)).to_numpy()
    sh = ((s1 < c) & (s2 > c) & (sm > 100)).to_numpy()
    xl = ((s1 < c) | (s2 > c) | (cci > 100)).to_numpy()
    xs = ((s1 > c) | (s2 < c) | (cci < -100)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held, is_l, is_s = 0, False, False
    for i in range(m):
        new = held
        if lg[i]:
            if new != 1:
                new = 1
            is_l, is_s = True, False
        if sh[i]:
            if new != -1:
                new = -1
            is_l, is_s = False, True
        if is_l and xl[i] and held == 1 and new == 1:
            new = 0
        if is_s and xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}

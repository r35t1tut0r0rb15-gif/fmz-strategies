"""Momentum-RSI trend entries with a SuperTrend exit, broker days: from flat, with the EMA 50 / 150 / 200 stacked up, the SuperTrend (10, 3) up, the EMA 12 above its 1 % trail line and the RSI of 10-bar momentum
above 60, the script goes long; the mirror goes short; a close through the SuperTrend line closes.
Port of FMZ strategy #439601 "Momentum Oscillator Trend Tracking Strategy" (The Flash-Strategy (Momentum-RSI, EMA-crossover, ATR)).

FMZ source id: 439601

Source
    https://www.fmz.com/strategy/439601 (PineScript v5, FMZ last modified 2024-01-22 10:08:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-300), Mom-RSI 10, limit 60; SuperTrend ATR 10 x 3; EMA 12 with a 1 % trail; EMA 50 / 150 / 200; both directions; version 1 (dynamic stop) on, version 2 off
    buy = Trail1 > Trail2 and supertrend up and rsi(mom 10, 10) > 60;  long_cond = close > ema150 and ema50 > ema150 > ema200;  entry Long_0 when buy, long_cond, not short_cond, close >= supertrend, no open trade
    if close < supertrend: exit(Long_Close, stop = supertrend);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent only once the close is under (over) the SuperTrend line, so its stop sits on the
      wrong side of the market and fills at the next open: the port closes on that bar's signal (as the
      house rule for such stops). Trail2 is the script's 1 % EMA trail recursion. Entries only from
      flat: Opposite entries cannot occur. The dollar-per-position quantity is sizing. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the wrong-side stop read as a close signal.
    2 generic: PASS, EMA stack, SuperTrend, EMA trail and RSI of momentum.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the dollar-per-position quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND437789 (2 members, best partner #437789, Jaccard 0.707); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439601_flash_mom_rsi_supertrend_exit"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mom_rsi_val": [60, 50],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"mom_rsi_val": 60, "factor": 3.0, "len": 10, "atr_period": 10, "ap2": 12, "af2": 1.0}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len"])
    rm = _rsi(c - c.shift(n), n).to_numpy()
    st, dr = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    t1 = c.ewm(span=int(p["ap2"]), adjust=False).mean().to_numpy()
    af = float(p["af2"]) / 100
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    t2 = np.zeros(m)
    for i in range(m):
        prev = t2[i - 1] if i > 0 else 0.0
        t1p = t1[i - 1] if i > 0 else np.nan
        sl2 = t1[i] * af
        iff1 = t1[i] - sl2 if t1[i] > prev else t1[i] + sl2
        iff2 = min(prev, t1[i] + sl2) if (t1[i] < prev and t1p < prev) else iff1
        t2[i] = max(prev, t1[i] - sl2) if (t1[i] > prev and t1p > prev) else iff2
    e50, e150, e200 = (c.ewm(span=k, adjust=False).mean().to_numpy() for k in (50, 150, 200))
    lim = float(p["mom_rsi_val"])
    buy = (t1 > t2) & (dr < 0) & (rm > lim)
    sell = (t1 < t2) & (dr > 0) & (rm > lim)
    lc = (cv > e150) & (e50 > e150) & (e150 > e200)
    sc = (cv < e150) & (e50 < e150) & (e150 < e200)
    below, above = cv < st, cv > st
    le_c = buy & lc & ~sc & ~below
    se_c = sell & sc & ~lc & ~above
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1:
            if below[i]:
                lx[i], pos = True, 0
        elif pos == -1:
            if above[i]:
                sx[i], pos = True, 0
        elif le_c[i]:
            le[i], pos = True, 1
        elif se_c[i]:
            se[i], pos = True, -1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

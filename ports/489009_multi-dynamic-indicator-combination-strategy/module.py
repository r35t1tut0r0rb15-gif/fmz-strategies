"""A wick-based SuperTrend (ATR 22 x 3 on hl2) flip, 2-day bars: the flip up goes long and the flip down goes short; a long closes at a close at or over the upper Bollinger band 20 / 2, a short at or under the lower band; reversing.
Port of FMZ strategy #489009 "Multi Dynamic Indicator Combination Strategy" (Combined BB & New SuperTrend Strategy).

FMZ source id: 489009

Source
    https://www.fmz.com/strategy/489009 (PineScript v6, FMZ last modified 2025-04-01 10:12:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-247), BB 20 / 2 (SMA); SuperTrend ATR 22 x 3, hl2, wicks on; capital 100000, 10 % of equity
    longStop = hl2 - 3 atr, ratcheted up while low[1] > previous (kept on 4-price doji);  shortStop mirror;  dir flips up when high > previous shortStop, down when low < previous longStop
    flip up -> close Short, entry Long;  flip down -> close Long, entry Short;  long and close >= upper -> close Long;  short and close <= lower -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend stops and direction follow the script's own recursion (nz of the previous stop), in a
      loop. The band exits act only on a held position (from the bar after the entry signal). Each flip
      closes the other side and enters: REVERSAL INTENDED. Bars are blocks of two broker days (17:00
      America/New_York) counted from 1970-01-01, stamped with their first minute. FREQ = "2D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend flips with Bollinger band exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: capital 100000, 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489009_wick_supertrend22_3_flip_bb_band_exit_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_mult": [3.0, 2.0],
    "st_length": [22, 10],
}
DEFAULT_PARAMS = {"st_mult": 3.0, "st_length": 22, "lengthBB": 20, "multBB": 2.0, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = (_rma(tr, int(p["st_length"])) * float(p["st_mult"])).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    ls, ss, dr = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    d = 1
    for i in range(m):
        raw_l, raw_s = src[i] - atr[i], src[i] + atr[i]
        pl = ls[i - 1] if i >= 1 and not np.isnan(ls[i - 1]) else raw_l
        ps = ss[i - 1] if i >= 1 and not np.isnan(ss[i - 1]) else raw_s
        doji = ov[i] == cv[i] and ov[i] == lv[i] and ov[i] == hv[i]
        if raw_l > 0:
            ls[i] = pl if doji else (max(raw_l, pl) if i >= 1 and lv[i - 1] > pl else raw_l)
        else:
            ls[i] = pl
        if raw_s > 0:
            ss[i] = ps if doji else (min(raw_s, ps) if i >= 1 and hv[i - 1] < ps else raw_s)
        else:
            ss[i] = ps
        if d == -1 and hv[i] > ps:
            d = 1
        elif d == 1 and lv[i] < pl:
            d = -1
        dr[i] = d
    dir_ = pd.Series(dr, index=c.index)
    le = (dir_ == 1) & (dir_.shift(1) == -1)
    se = (dir_ == -1) & (dir_.shift(1) == 1)
    n = int(p["lengthBB"])
    basis = c.rolling(n).mean()
    dev = float(p["multBB"]) * c.rolling(n).std(ddof=0)
    lx = (c >= basis + dev) & ~le & ~se
    sx = (c <= basis - dev) & ~se & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}

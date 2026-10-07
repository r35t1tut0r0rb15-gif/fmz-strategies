"""Trading ABC (LonesomeTheBlue): in an MA-cloud trend (price on one side of all six MAs for two
bars), an ABC pull-back on the zigzag (B-C retracement 0.382-0.618 +- 5 %) followed within six
bars by a bounce off one of the MAs that has not broken point C goes long (or short).
Port of FMZ strategy #365127 "Trading ABC".

Source
    https://www.fmz.com/strategy/365127 (PineScript v4, FMZ last modified 2022-05-24 10:13:47).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 82-300), zigzag period 8, fibo 0.382..0.618, error 5 %,
SMA 50/100/150/200, EMA 20/40
    trend = 1 when all valid MAs sit at or below min(open, close) on this and the previous bar,
            -1 when all sit at or above max(open, close) on both, else unchanged
    zigzag: ph = high is the 8-bar high, pl = low the 8-bar low; dir; up to 5 points
    on a new zigzag point with >= 3 points, trend 1, dir -1, low < max(MAs) (short mirrors):
        rate = (A - B) / (C - B) in [0.382 * 0.95, 0.618 * 1.05] -> ABC found
    last_zz_point = A when found; abc_bar_count = bars since found
    lbounced = some MA with min(low, low[1]) <= MA < close and close > open (sbounced mirrors)
    long  = trend == 1 and abc_bar_count <= 6 and lbounced and lowest(count + 1) >= last_zz_point
    short = trend == -1 and abc_bar_count <= 6 and sbounced and highest(count + 1) <= last_zz_point
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars(high, 8) == 0 is read as high equal to the 8-bar high (ties go to the current
      bar). array.max / array.min of the MAs ignore MAs that do not exist yet.
    * The labels, lines and the stochastic (lstoch / sstoch) do not reach the orders.
    * The zigzag only uses completed bars; points are revised as in the source (the last point
      moves while the swing extends), which is what the script sees on each bar close.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365127_trading_abc_pullback"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [5, 8, 13],
    "error_rate": [0.05, 0.10],
}
DEFAULT_PARAMS = {"prd": 8, "fibo_up": 0.618, "fibo_dn": 0.382, "error_rate": 0.05, "max_bars": 6}
SMA_LENS = (50, 100, 150, 200)
EMA_LENS = (20, 40)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    cs = bars_df["close"]
    mas = np.column_stack([cs.rolling(n).mean().to_numpy() for n in SMA_LENS]
                          + [cs.ewm(span=n, adjust=False).mean().to_numpy() for n in EMA_LENS])
    top, bot = np.maximum(o, c), np.minimum(o, c)
    upper = (mas >= top[:, None]).sum(axis=1)
    lower = ((mas <= bot[:, None]) & ~(mas >= top[:, None])).sum(axis=1)
    with np.errstate(all="ignore"):
        ma_max, ma_min = np.nanmax(mas, axis=1), np.nanmin(mas, axis=1)
    prd = int(p["prd"])
    is_ph = (bars_df["high"] >= bars_df["high"].rolling(prd).max()).to_numpy()
    is_pl = (bars_df["low"] <= bars_df["low"].rolling(prd).min()).to_numpy()
    lo1 = np.concatenate([[np.nan], l[:-1]])
    hi1 = np.concatenate([[np.nan], h[:-1]])
    lb = ((np.minimum(l, lo1)[:, None] <= mas) & (c[:, None] > mas) & (c > o)[:, None]).any(axis=1)
    sb = ((np.maximum(h, hi1)[:, None] >= mas) & (c[:, None] < mas) & (c < o)[:, None]).any(axis=1)
    lo_rate = p["fibo_dn"] - p["fibo_dn"] * p["error_rate"]
    hi_rate = p["fibo_up"] + p["fibo_up"] * p["error_rate"]

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    trend = 0
    d = 0
    d_prev = None
    zz = []  # [value, bar, value, bar, ...] newest first, at most 10 entries
    z_prev = 0.0
    last_zz = 0.0
    count = 0
    for i in range(m):
        if i:
            if lower[i] > 0 and upper[i] == 0 and lower[i - 1] > 0 and upper[i - 1] == 0:
                trend = 1
            elif lower[i] == 0 and upper[i] > 0 and lower[i - 1] == 0 and upper[i - 1] > 0:
                trend = -1
        ph = h[i] if is_ph[i] else np.nan
        pl = l[i] if is_pl[i] else np.nan
        has_ph, has_pl = not np.isnan(ph), not np.isnan(pl)
        if has_ph and not has_pl:
            d = 1
        elif has_pl and not has_ph:
            d = -1
        if has_ph or has_pl:
            v = ph if d == 1 else pl
            if d_prev is not None and d != d_prev:
                zz[0:0] = [v, i]
                del zz[10:]
            elif not zz:
                zz[0:0] = [v, i]
            elif (d == 1 and v > zz[0]) or (d == -1 and v < zz[0]):
                zz[0], zz[1] = v, i
        d_prev = d
        z_now = zz[0] if zz else 0.0
        found = False
        if z_now != z_prev and len(zz) > 5 and (
                (has_pl and trend == 1 and d == -1 and l[i] < ma_max[i])
                or (has_ph and trend == -1 and d == 1 and h[i] > ma_min[i])):
            a, b, cc = zz[0], zz[2], zz[4]
            rate = (a - b) / (cc - b) if cc != b else np.nan
            found = lo_rate <= rate <= hi_rate
        z_prev = z_now
        if len(zz) > 2 and found:
            last_zz = zz[0]
        count = 0 if found else count + 1
        lll = l[max(0, i - count):i + 1].min()
        hhh = h[max(0, i - count):i + 1].max()
        le[i] = trend == 1 and count <= p["max_bars"] and lb[i] and lll >= last_zz
        se[i] = trend == -1 and count <= p["max_bars"] and sb[i] and hhh <= last_zz
    return _always_in(le, se & ~le, bars_df.index)


def portfolio_kwargs(**params):
    return {}

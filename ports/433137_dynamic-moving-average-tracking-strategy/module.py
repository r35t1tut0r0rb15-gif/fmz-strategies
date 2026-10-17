"""UT Bot on the open price, broker days, long only by default: an ATR 11 trailing line follows the bar's open; an HMA 2
of the open crossing above the line (with the open above it) goes long, the mirror cross closes it (shorts are off).
Port of FMZ strategy #433137 "Dynamic Moving Average Tracking Strategy" (UT Bot v5).

FMZ source id: 433137

Source
    https://www.fmz.com/strategy/433137 (PineScript v5, FMZ last modified 2023-11-24 16:59:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 127-173), source open, HMA 2, sensitivity 1, ATR 11; buys on, sells off; TP / SL 50000 $ of open profit
    trail = the UT Bot ratchet: src above the previous trail on both bars -> max(prev, src - a atr); below on both -> min(prev, src + a atr); else flip
    buy = src > trail and crossover(hma(src, 2), trail);  sell = src < trail and crossover(trail, hma(src, 2))
    sell and not AllowSell -> close buy;  buy and AllowBuy -> entry buy;  openprofit > 50000 or < -50000 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source is the bar's own open (known at the bar's start). hma(src, 2) is 2 src - wma(src, 2)
      (the outer wma of length round(sqrt 2) = 1 changes nothing).
    * The open-profit close-outs (+/- 50000 $) depend on the position size and are out of reach of
      the default sizing: dropped (sizing). Heikin Ashi signals are off.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR trailing line and an average cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the open-profit close-outs and 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433137_ut_bot_open_hma"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sens": [1.0, 2.0],
    "atr_len": [11, 22],
}
DEFAULT_PARAMS = {"sens": 1.0, "atr_len": 11}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    nloss = (float(p["sens"]) * tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()).to_numpy()
    src = o.to_numpy(dtype=float)
    m = len(src)
    trail = np.zeros(m)
    for i in range(m):
        pt = trail[i - 1] if i > 0 else 0.0
        s1 = src[i - 1] if i > 0 else np.nan
        if src[i] > pt and s1 > pt:
            trail[i] = max(pt, src[i] - nloss[i])
        elif src[i] < pt and s1 < pt:
            trail[i] = min(pt, src[i] + nloss[i])
        else:
            trail[i] = src[i] - nloss[i] if src[i] > pt else src[i] + nloss[i]
    s = pd.Series(src, index=o.index)
    hma = 2 * s - (2 * s + s.shift(1)) / 3
    t = pd.Series(trail, index=o.index)
    buy = ((s > t) & (hma > t) & (hma.shift(1) <= t.shift(1))).to_numpy()
    sell = ((s < t) & (t > hma) & (t.shift(1) <= hma.shift(1))).to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            pos = 0
        if buy[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}

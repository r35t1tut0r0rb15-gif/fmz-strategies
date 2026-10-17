"""Parabolic SAR side inside the Bollinger bands, broker days: a close above the SAR and below the upper band goes long,
leaving when the close falls below the SAR or reaches the upper band; a close below the SAR and above the lower band
goes short, leaving on the mirror conditions.
Port of FMZ strategy #488417 "抛物线停损反转与布林带趋势识别量化交易策略-Parabolic-SAR-and-Bollinger-Bands-Trend-Identification-Quantitative-Trading-Strategy" (Parabolic SAR + Bollinger Bands Strategy).

FMZ source id: 488417

Source
    https://www.fmz.com/strategy/488417 (PineScript v5, FMZ last modified 2025-03-27 14:20:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 178-221), SAR (0.02, 0.2, 0.2), BB 20 x 2
    sar = ta.sar(sar_step, sar_max, sar_max)  (the increment is sar_max, as written)
    long = close > sar and close < upper;  exitLong = close < sar or close >= upper
    short = close < sar and close > lower;  exitShort = close > sar or close <= lower
    entry Buy; close Buy; entry Sell; close Sell (in this order)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar as TradingView documents it (as #428699), with the increment equal to the maximum as written.
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850): a long
      signal while short reverses (the close of the short is the reversal). REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR and bands.
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

NAME = "fmz_488417_sar_side_inside_bollinger"
FAMILY = "parabolic_sar"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_max": [0.2, 0.1],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"sar_step": 0.02, "sar_max": 0.2, "bb_length": 20, "bb_mult": 2.0}


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


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar), as #428699."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sar = _sar_pine(bars_df, p["sar_step"], p["sar_max"], p["sar_max"])
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    go_l = ((c > sar) & (c < up)).to_numpy()
    go_s = ((c < sar) & (c > lo)).to_numpy()
    x_l = ((c < sar) | (c >= up)).to_numpy()
    x_s = ((c > sar) | (c <= lo)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if x_l[i] and start == 1 and pos == 1:
            pos = 0
        if go_s[i]:
            pos = -1
        if x_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}

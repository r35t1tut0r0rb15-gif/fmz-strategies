"""Three-way trend agreement (connor2279), broker days: RSI 14 at or over its SMA 50, a normalised MACD (EMA 12 / 21) above
its WMA 10 trigger and the close at or over the SMA 10 goes long (all three reversed goes short); any cross of the close
and SMA 10, the trigger and the MACD, or the RSI and its average closes the position.
Port of FMZ strategy #432099 "Multi Timeframe Trend Tracking Strategy" (SPX Strategy).

FMZ source id: 432099

Source
    https://www.fmz.com/strategy/432099 (PineScript v5, FMZ last modified 2023-11-14 14:29:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-231), SMA 10, normalised MACD 12 / 21 over 50 bars, WMA trigger 10, RSI 14 vs SMA 50
    Mac = EMA ratio - 1 (2 - ratio - 1 when ema12 > ema21); MacNorm = 2 (Mac - lowest(Mac, 50)) / (range + 1e-6) - 1
    buy = rsi >= sma(rsi, 50) and wma(MacNorm, 10) < MacNorm and close >= sma10;  short = all three reversed
    sellSignal = cross(close, sma10) or cross(trigger, MacNorm) or cross(rsi, sma(rsi, 50)) -> close long and short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are written after the entries; a close acts on the position held at the bar's start
      and does not undo a reversal on the same bar. qty 1 is sizing. The comment's 1-minute SPX chart
      is not the header's. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA, MACD-ratio and RSI comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored in original_sizing.txt.
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

NAME = "fmz_432099_three_way_trend_agreement"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [10, 20],
    "np_len": [50, 25],
}
DEFAULT_PARAMS = {"sma_len": 10, "np_len": 50}


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
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: (a * w).sum() / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    out1 = c.rolling(int(p["sma_len"])).mean()
    sh, lo_ = c.ewm(span=12, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    ratio = np.minimum(sh, lo_) / np.maximum(sh, lo_)
    mac = pd.Series(np.where(sh > lo_, 2 - ratio - 1, ratio - 1), index=c.index).where(ratio.notna())
    n = int(p["np_len"])
    mn, mx = mac.rolling(n).min(), mac.rolling(n).max()
    norm = (mac - mn) / (mx - mn + 0.000001) * 2 - 1
    trig = _wma(norm, 10)
    ch = c.diff()
    up, dn = _rma(ch.clip(lower=0), 14), _rma((-ch).clip(lower=0), 14)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0)
    mr = rsi.rolling(50).mean()
    buy = ((rsi >= mr) & (trig < norm) & (c >= out1)).to_numpy()
    shs = ((rsi < mr) & (trig >= norm) & (c < out1)).to_numpy()

    def cross(a, b):
        return (((a > b) & (a.shift(1) <= b.shift(1))) | ((a < b) & (a.shift(1) >= b.shift(1)))).to_numpy()
    sell = cross(c, out1) | cross(trig, norm) | cross(rsi, mr)
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if shs[i]:
            pos = -1
        if sell[i] and start != 0 and pos == start:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

"""Broker days, long only: a higher 5-bar closing low than the previous bar's with the WaveTrend line (10 / 21) falling and an up close goes long with a stop 1.5 ATR 14 under that bar's low; the bearish mirror closes it.
Port of FMZ strategy #452697 "基于BTC15分钟图表的技术交易策略-Technical-Trading-Strategy-for-BTC-15-minute-Chart" (PipShiesty Swagger).

FMZ source id: 452697

Source
    https://www.fmz.com/strategy/452697 (PineScript v5, FMZ last modified 2024-05-28 11:15:29).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 87-160), WaveTrend 10 / 21; ATR 14 x 1.5 stop; risk 1 % (doubled) sizing
    bullishDivergence = lowest(close, 5) > lowest(close[1], 5) and wt1 < wt1[1] and close > close[1] -> entry Buy, exit("Sell", stop = low - 1.5 atr)
    bearishDivergence = highest(close, 5) < highest(close[1], 5) and wt1 > wt1[1] and close < close[1] -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent on each bullish bar from that bar's low and ATR; a repeated bullish bar while
      long moves it, so the port fixes it at the entry signal (mark trailing_stop_pending), as a fraction
      of the fill (1e-6 floor); the signals follow it, so a stopped trade can re-enter on the next
      bullish bar. The title says 15 minutes, the header runs daily bars. The "VWAP" (a VWMA
      10) and the levels only plot: volume is not used. Long only. The risk sizing is sizing. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at the signal bar as a fraction of the fill.
    2 generic: PASS, WaveTrend / price divergences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 1 % / stop distance x 2, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG452697 (2 members, best partner #452745, Jaccard 0.831); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452697_wavetrend_divergence_atr_stop_long_only"
FAMILY = "wavetrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "n1": [10, 9],
    "stop_atr": [1.5, 2.5],
}
DEFAULT_PARAMS = {"n1": 10, "n2": 21, "stop_atr": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _stop_level(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    return lo - float(p["stop_atr"]) * _rma(tr, 14)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ap = (h + lo + c) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d).where(d != 0)
    wt1 = ci.ewm(span=int(p["n2"]), adjust=False).mean()
    bull = ((c.rolling(5).min() > c.shift(1).rolling(5).min()) & (wt1 < wt1.shift(1)) & (c > c.shift(1))).to_numpy()
    bear = ((c.rolling(5).max() < c.shift(1).rolling(5).max()) & (wt1 > wt1.shift(1)) & (c < c.shift(1))).to_numpy()
    lvl = _stop_level(bars_df, p).to_numpy()
    lv = lo.to_numpy(dtype=float)
    m = len(bull)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, sl_px = 0, False, np.nan
    for i in range(m):
        if pend:
            pos, pend = 1, False
        if pos == 1 and lv[i] <= sl_px:                 # the stop ends the trade inside the bar
            pos = 0
        if pos == 0 and not pend and bull[i] and i + 1 < m:
            le[i], pend, sl_px = True, True, lvl[i]
        elif pos == 1 and bear[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    level = _stop_level(bars_df, p)
    sl_f = (1 - level.shift(1) / o).where(le.shift(1, fill_value=False))
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}

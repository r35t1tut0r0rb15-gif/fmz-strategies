"""EMA 9 / 15 crossings on the side of the EMA 50, daily bars, long only: the cross up with the close over the EMA 50 buys with a 100-tick stop and 200-tick target; the cross down with the close under it sells.
Port of FMZ strategy #473252 "Triple EMA Crossover Trading Strategy with Dynamic Stop Loss and Take Profit" (EMA Crossover Strategy with 50 EMA Filter).

FMZ source id: 473252

Source
    https://www.fmz.com/strategy/473252 (PineScript v5, FMZ last modified 2024-11-28 15:54:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-147), EMA 9 / 15 / 50; loss 100, profit 200 ticks (sent on the signal bar)
    crossover(ema9, ema15) and close > ema50 -> entry Buy + exit(loss = 100, profit = 200);  crossunder and close < ema50 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 100 / 200 ticks are 10 / 20 at the 0.1 tick, ported as ATR multiples at the daily reading
      (~1000): 0.01 / 0.02 ATR 14 from the bar before the fill. Long only. Stop module: portfolio_kwargs
      {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, EMA crossings with a trend filter and a tick bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473252_ema9_15_cross_ema50_filter_tick_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.01, 1.0],
    "tp_atr": [0.02, 2.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.01, "tp_atr": 0.02, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    c = bars_df["close"]
    a, b, t = (c.ewm(span=n, adjust=False).mean() for n in (9, 15, 50))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (c > t)
    lx = (a < b) & (a.shift(1) >= b.shift(1)) & (c < t)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}

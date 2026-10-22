"""Pullbacks between the EMA 21 and EMA 50 in a stacked EMA 20 / 50 / 100 / 200 uptrend, daily bars, long only: from flat, a close at or under the EMA 21 and at or over the EMA 50 buys, with a 1.5 ATR stop and 3.5 ATR target from the signal close.
Port of FMZ strategy #473265 "多均线趋势跟踪与ATR动态目标策略-Multi-EMA-Trend-Following-Strategy-with-Dynamic-ATR-Targets" (EMA Crossover and ATR Target Strategy).

FMZ source id: 473265

Source
    https://www.fmz.com/strategy/473265 (PineScript v5, FMZ last modified 2024-11-28 17:11:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-142), EMA 20 / 50 / 100 / 200 and EMA 21 (constants); ATR 14: stop 1.5 x, target 3.5 x
    stack up and ema50 <= close <= ema21 and flat -> stop = close - 1.5 atr, target = close + 3.5 atr, entry Buy;  while long: exit(limit = target, stop = stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only from flat, so each trade's levels are its signal bar's: ported as ATR multiples of the
      signal bar shifted into the fill (active from the fill bar, #440797). Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at entry.
    2 generic: PASS, EMA-stack pullbacks with an ATR bracket.
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

NAME = "fmz_473265_ema_stack_pullback_21_50_atr_bracket_long"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 3.0],
    "tp_atr": [3.5, 7.0],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "tp_atr": 3.5, "atr_len": 14}


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
    e20, e50, e100, e200, e21 = (c.ewm(span=n, adjust=False).mean() for n in (20, 50, 100, 200, 21))
    stack = (e20 > e50) & (e50 > e100) & (e100 > e200)
    le = stack & (c <= e21) & (c >= e50)
    le.iloc[:1] = False                          # bar_index > 0
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}

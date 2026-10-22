"""Pullbacks to the EMA 20 in a stacked EMA 20 / 50 / 100 / 200 uptrend with rising momentum, 1-hour bars, long only: a close within 1 % of the EMA 20 while the EMAs are stacked up, the 20-bar momentum is positive and rising and the weekly-series momentum is positive and rising buys, with a 1.5 ATR stop and 3 ATR target from the signal close.
Port of FMZ strategy #471719 "Multi Timeframe EMA Trend Momentum Trading Strategy" (Swing Trading with EMA Alignment and Custom Momentum).

FMZ source id: 471719

Source
    https://www.fmz.com/strategy/471719 (PineScript v5, FMZ last modified 2024-11-12 16:35:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-170), EMA 20 / 50 / 100 / 200; ATR 14 (stop 1.5 x, target 3 x); momentum = linreg(close - (mid of 20-bar range + SMA 20) / 2, 20); weekly momentum from request.security("W", [high, low, close]); pullback 1 %
    ema stack up and momentum > 0 rising and weekly momentum > 0 rising and |close - ema20| <= 1 % -> stop = close - 1.5 atr, target = close + 3 atr, entry Long
    while long: exit(stop, limit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly request without lookahead is read as the last completed broker week (Monday label,
      #437508), built from the module's own bars; the source then applies its 20-length highest /
      lowest / SMA / linreg to that series on the chart's own 1-hour bars (not 20 weeks), as written, so
      the weekly momentum is mostly 0 and turns positive only for up to 20 bars after a week changes.
      The levels are fixed on each signal bar: ported as ATR multiples of the signal bar shifted into the
      fill; a repeat signal while held re-sets them, which stops() cannot express (opening levels kept,
      as #434428, mark trailing_stop_pending). Long only. Stop module: portfolio_kwargs {} (driver D4).
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks; ATR bracket at entry.
    2 generic: PASS, EMA-stack pullbacks with momentum filters and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471719_ema_stack_pullback_daily_weekly_momentum_atr_bracket_long"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pullback_pct": [1.0, 2.0],
    "sl_atr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"pullback_pct": 1.0, "sl_atr": 1.5, "tp_atr": 3.0, "atr_len": 14, "kc_len": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _linreg_end(s, n):
    n = int(n)
    w = np.arange(n, dtype=float) - (n - 1) / 2.0
    sxx = float(np.dot(w, w))
    return s.rolling(n).apply(lambda a: float(a.mean() + np.dot(w, a) / sxx * (n - 1) / 2.0), raw=True)


def _momentum(h, lo, c, n):
    avg = (h.rolling(n).max() + lo.rolling(n).min()) / 2
    return _linreg_end(c - (avg + c.rolling(n).mean()) / 2, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["kc_len"])
    e20, e50, e100, e200 = (c.ewm(span=k, adjust=False).mean() for k in (20, 50, 100, 200))
    aligned = (e20 > e50) & (e50 > e100) & (e100 > e200)
    dm = _momentum(h, lo, c, n)
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")         # the Monday of the broker week
    wk = pd.DataFrame({"h": h.to_numpy(), "l": lo.to_numpy(), "c": c.to_numpy()}, index=week)
    g = wk.groupby(level=0).agg({"h": "max", "l": "min", "c": "last"}).shift(1)   # last completed week
    wh = pd.Series(g["h"].reindex(week).to_numpy(), index=c.index)
    wl = pd.Series(g["l"].reindex(week).to_numpy(), index=c.index)
    wc = pd.Series(g["c"].reindex(week).to_numpy(), index=c.index)
    wm = _momentum(wh, wl, wc, n)                               # on the chart's own bars, as written
    k = float(p["pullback_pct"]) / 100
    pull = (c <= e20 * (1 + k)) & (c >= e20 * (1 - k))
    le = aligned & (dm > 0) & (dm > dm.shift(1)) & (wm > 0) & (wm > wm.shift(1)) & pull
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}

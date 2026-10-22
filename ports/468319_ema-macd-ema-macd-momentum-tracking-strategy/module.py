"""EMA 9 / 21 and MACD crossings on the same bar, daily bars: both crossing up goes long, both crossing down goes short; each trade has a 1.5 ATR stop and 3 ATR target from the fill; reversing.
Port of FMZ strategy #468319 "EMA-MACD-动量跟踪策略EMA-MACD-Momentum-Tracking-Strategy" (EMA and MACD Strategy for 5-Min Chart).

FMZ source id: 468319

Source
    https://www.fmz.com/strategy/468319 (PineScript v5, FMZ last modified 2024-09-26 15:31:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-171), EMA 9 / 21; MACD 12 / 26 / 9; ATR 14 x 1.5 stop, x 3 target from the average price (re-sent every bar with that bar's ATR)
    crossover(ema9, ema21) and crossover(macd, signal) -> entry Long;  both crossunders -> entry Short
    long: exit(stop = avg - 1.5 atr, limit = avg + 3 atr);  short: exit(stop = avg + 1.5 atr, limit = avg - 3 atr)  (every bar while held)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The title names a 5-minute chart; the backtest header runs daily bars and is followed. The
      levels come from the average (fill) price but move with each bar's ATR: ported with the ATR of the
      bar before the fill as fractions of the fill (active from the fill bar, #440797); the bar-by-bar
      ATR movement cannot be expressed (mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR levels from the fill.
    2 generic: PASS, EMA and MACD crossings together with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_468319_ema9_21_and_macd_cross_atr_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [9, 5],
    "slow": [21, 34],
    "atr_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "atr_mult": 1.5, "atr_len": 14}


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
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (2 * f).shift(1)}


def portfolio_kwargs(**params):
    return {}

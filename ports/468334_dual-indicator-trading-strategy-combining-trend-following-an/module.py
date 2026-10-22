"""MACD zero-line crossings on the side of the SMA 50, daily bars: the MACD crossing over zero with the close over the SMA 50 goes long, crossing under zero with the close under it goes short, each with a 2 ATR target and 1.5 ATR stop from the signal close; reversing.
Port of FMZ strategy #468334 "Dual Indicator Trading Strategy Combining Trend Following and Momentum" (NNFX Trendilo + Zero MACD Strategy).

FMZ source id: 468334

Source
    https://www.fmz.com/strategy/468334 (PineScript v5, FMZ last modified 2024-09-26 16:14:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-154), MACD 12 / 26 / 9 line vs 0; "Trendilo" = SMA 50; ATR 14: stop 1.5 x, target 2 x
    crossover(macd, 0) and close > sma50 -> entry Buy + exit(limit = close + 2 atr, stop = close - 1.5 atr);  crossunder(macd, 0) and close < sma50 -> entry Sell + exit (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Trendilo" is a plain SMA 50 here. The bracket is sent once on the signal bar: ported as ATR
      multiples of the signal bar shifted into the fill. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at entry.
    2 generic: PASS, MACD zero crossings with an SMA filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_468334_macd_zero_cross_sma50_side_atr_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trend_len": [50, 100],
    "sl_mult": [1.5, 3.0],
    "tp_mult": [2.0, 4.0],
}
DEFAULT_PARAMS = {"trend_len": 50, "sl_mult": 1.5, "tp_mult": 2.0, "atr_len": 14}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    t = c.rolling(int(p["trend_len"])).mean()
    le = (macd > 0) & (macd.shift(1) <= 0) & (c > t)
    se = (macd < 0) & (macd.shift(1) >= 0) & (c < t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_mult"]) * a).shift(1), "tp_stop": (float(p["tp_mult"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}

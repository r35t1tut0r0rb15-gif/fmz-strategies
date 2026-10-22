"""Engulfing candles, daily bars: a bullish engulfing bar goes long with a target one body over the close and a 100-tick stop (0.01 ATR at the daily reading); a bearish one goes short (mirror); reversing.
Port of FMZ strategy #457777 "4小时时间框架上的吞没形态交易策略与动态止盈止损优化-4-Hour-Timeframe-Engulfing-Pattern-Trading-Strategy-with-Dynamic-Take-Profit-and-Stop-Loss-Optimization" (4H Engulfing Candle Strategy).

FMZ source id: 457777

Source
    https://www.fmz.com/strategy/457777 (PineScript v5, FMZ last modified 2024-07-26 15:06:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 180-223), engulfing: close > open[1] and open < close[1] and open <= open[1] and close >= close[1] (mirror); target 1 x body; stop 100 ticks; 10 % of equity
    bullish engulfing -> entry Buy, exit(limit = close + body, stop = close - 100 ticks);  bearish engulfing -> entry Sell, exit(limit = close - body, stop = close + 100 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The engulfing tests imply a green (red) bar. The target is fixed on the signal bar from its close
      and body: ported as the fraction body / close of the signal bar; the 100-tick stop is 10 at the
      0.1 tick, ported as an ATR multiple at the daily reading (~1000): 0.01 ATR 14 from the bar before
      the fill. A repeat signal inside a trade re-issues the levels, which stops() cannot express: the
      opening levels are kept and the module is marked trailing_stop_pending (as #434428). The title's
      4 hours is not the header's period. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: mark coarse_bar_stop. The 10 % of equity is sizing. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the body target and tick stop as fractions; re-issued levels pending (mark).
    2 generic: PASS, engulfing candles with a body target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_457777_engulfing_body_target_tick_stop_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_mult": [1.0, 2.0],
    "sl_atr": [0.01, 1.0],
}
DEFAULT_PARAMS = {"tp_mult": 1.0, "sl_atr": 0.01, "atr_len": 14}


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


def _signals(bars_df):
    o, c = bars_df["open"], bars_df["close"]
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c > o1) & (o < c1) & (o <= o1) & (c >= c1)
    bear = (c < o1) & (o > c1) & (o >= o1) & (c <= c1)
    return bull, bear


def simulate(bars_df, **params):
    bull, bear = _signals(bars_df)
    false = pd.Series(False, index=bars_df.index)
    return bull & ~bear, false, bear, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    bull, bear = _signals(bars_df)
    body = (c - o).abs()
    tp = (float(p["tp_mult"]) * body / c).where(bull | bear)
    sl = float(p["sl_atr"]) * _atr(bars_df, p["atr_len"]) / c
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}

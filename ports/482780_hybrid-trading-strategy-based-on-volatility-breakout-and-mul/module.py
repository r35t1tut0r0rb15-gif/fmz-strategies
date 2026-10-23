"""Broker days, long only: a close above the upper Bollinger band (20, 2) on a bar where the close crosses over the SMA 50 or the SMA 10 crosses over the SMA 50, on volume over 1.5 x its 20-day average, goes long with a 1.5 ATR 14 stop and a 2 ATR target from the signal close; such a crossing bar without the breakout closes it.
Port of FMZ strategy #482780 "Hybrid Trading Strategy Based on Volatility Breakout and Multiple Technical Indicators" (Hybrid Money Making Trading Strategy).

FMZ source id: 482780

Source
    https://www.fmz.com/strategy/482780 (PineScript v6, FMZ last modified 2025-02-20 15:01:24).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 106-154), BB 20 x 2; SMA 10 / 50 crossings; volume SMA 20 x 1.5; ATR 14; SL 1.5 ATR, TP 2 ATR
    buy_signal = close > bb_upper and (crossover(close, sma50) or crossover(sma10, sma50)) and volume > 1.5 x vol_avg -> entry Long, exit("TakeProfit", "Long", stop = close - 1.5 atr, limit = close + 2 atr)
    sell_signal = not (close > bb_upper) and (crossover(close, sma50) or crossover(sma10, sma50)) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "sell" is a bullish crossing bar without the band breakout, as written (weird case). The
      bracket is sent on signal bars only, as levels from that close: ported as fractions of the fill,
      exact (1e-6 floor). A buy and a sell never meet on one bar. The cumulative VWAP and the TWAP only
      plot. Long only. No sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, Bollinger breakouts on SMA crossings and high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482780_bb_breakout_sma_cross_volume_atr_bracket_long_only"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 2.0],
    "tp_atr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "tp_atr": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    c, v = bars_df["close"], bars_df["volume"]
    up = c.rolling(20).mean() + 2 * c.rolling(20).std(ddof=0)
    s10, s50 = c.rolling(10).mean(), c.rolling(50).mean()
    pattern = _xo(c, s50) | _xo(s10, s50)
    brk = c > up
    buy = brk & pattern & (v > 1.5 * v.rolling(20).mean())
    sell = ~brk & pattern
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf = le.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}

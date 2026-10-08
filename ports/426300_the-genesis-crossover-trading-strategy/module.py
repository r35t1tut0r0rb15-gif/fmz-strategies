"""GENESIS EMA 20 / 50 cross: EMA 20 crossing above EMA 50 goes long, crossing below goes short;
only shorts carry a bracket (target 5x the stop distance), longs run to the next short.
Port of FMZ strategy #426300 "The Genesis Crossover Trading Strategy".

Source
    https://www.fmz.com/strategy/426300 (PineScript v5, FMZ last modified 2023-09-10 21:38:32).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 56-75), EMA 20 / 50
    crossover(ema20, ema50) -> entry "long";  crossover(ema50, ema20) -> entry "short"
    strategy.exit("Exit", "Long", profit = 10, loss = 2)    (ticks)
    strategy.exit("Exit", "short", profit = 10, loss = 2)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: the first exit names entry "Long", but the long entry's id is "long" (Pine ids
      are case-sensitive), and the second call re-issues the same exit id "Exit" for "short".
      So only shorts are bracketed; a long ends at the next short entry.
    * Criterion 2: 10 / 2 ticks are instrument-specific (on BTC 1 / 0.2 USDT, a fraction of a
      tick of ATR). They become sl_atr x ATR(14) at the signal bar and a target 5 x that (the
      source's ratio), as sl_stop / tp_stop fractions shifted one bar, NaN (none) for longs.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
      Stops on daily bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426300_genesis_ema_cross_short_bracket"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)
TP_RATIO = 5.0  # profit 10 / loss 2 ticks

GRID = {
    "sl_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "sl_atr": 0.25}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _crosses(bars_df, p):
    c = bars_df["close"]
    d = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    d1 = d.shift(1)
    return (d > 0) & (d1 <= 0), (d < 0) & (d1 >= 0)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _crosses(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, dn = _crosses(bars_df, p)
    frac = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(dn)
    return {"sl_stop": frac.shift(1), "tp_stop": (TP_RATIO * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}

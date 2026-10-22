"""MACD 12 / 26 / 9 cross-ups while a 12-times-slower MACD (144 / 312 / 108) histogram is positive, daily bars, long only; each trade has a 100-tick target and 20-tick stop from the fill.
Port of FMZ strategy #458237 "双重MACD趋势确认交易系统-Dual-MACD-Trend-Confirmation-Trading-System" (MACD5分IN,一時間足強弱判定).

FMZ source id: 458237

Source
    https://www.fmz.com/strategy/458237 (PineScript v5, FMZ last modified 2024-07-31 11:17:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-234), MACD 12 / 26 / 9 and 144 / 312 / 108; profit 100, loss 20 ticks; qty 1
    crossover(macd, signal) and hist(144 / 312 / 108) > 0 -> entry long (qty 1);  every bar: exit(from long, profit = 100, loss = 20)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The comments describe 5-minute bars, but the backtest header runs daily bars; the header is
      followed. profit / loss are ticks from the entry price: 10 / 2 at the 0.1 tick, ported as ATR
      multiples at the daily reading (~1000): 0.01 / 0.002 ATR 14 from the bar before the fill. The fixed
      1-unit quantity is not ported (sizing is the optimisation layer's). Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, MACD cross-ups with a slow-MACD filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed 1-unit quantity stored, not ported.
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

NAME = "fmz_458237_macd_cross_slow_macd_hist_filter_tick_bracket_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.01, 2.0],
    "sl_atr": [0.002, 1.0],
}
DEFAULT_PARAMS = {"tp_atr": 0.01, "sl_atr": 0.002, "atr_len": 14}


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


def _macd(c, f, s, g):
    m = c.ewm(span=f, adjust=False).mean() - c.ewm(span=s, adjust=False).mean()
    return m, m.ewm(span=g, adjust=False).mean()


def simulate(bars_df, **params):
    c = bars_df["close"]
    m, sg = _macd(c, 12, 26, 9)
    m1, sg1 = _macd(c, 144, 312, 108)
    le = (m > sg) & (m.shift(1) <= sg.shift(1)) & ((m1 - sg1) > 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}

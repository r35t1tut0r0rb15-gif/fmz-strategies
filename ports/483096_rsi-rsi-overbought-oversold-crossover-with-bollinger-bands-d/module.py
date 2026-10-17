"""RSI 14 leaving oversold (overbought) with the 10-bar swing extreme as the stop and a 2 R target, daily
(broker-day) bars: RSI crossing above 30 goes long (stop the 10-bar low, target close + 2 x (close - stop)); RSI crossing
below 70 goes short (mirrored with the 10-bar high).
Port of FMZ strategy #483096 "RSI超买超卖交叉结合布林带动态止盈止损策略-RSI-Overbought-Oversold-Crossover-with-Bollinger-Bands-Dynamic-Stop-Loss-Strategy" (RSI Oversold Crossover Strategy).

FMZ source id: 483096

Source
    https://www.fmz.com/strategy/483096 (PineScript v5, FMZ last modified 2025-02-21 13:29:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 117-141), RSI 14 (30 / 70), swing 10, RR 2
    long = crossover(rsi, 30); entry + exit(stop = lowest(low, 10), limit = close + 2 (close - stop))
    short = crossunder(rsi, 70); mirrored with highest(high, 10)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: sl = (close - lowest low 10) / close, tp = 2 x sl
      ((highest high 10 - close) / close for a short), picked by the signal's side, shifted one bar inside stops() and
      re-based on the fill (house rule). A signal whose stop is not beyond the close emits no entry (as #490798). A
      same-side signal while held re-places it: mark trailing_stop_pending.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00
      America/New_York) stamped with their first minute (as #430984); stops on daily bars: coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, RSI and rolling swing extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_483096_rsi_exit_extreme_swing_stop_2r"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 3.0],
    "swing_len": [10, 20],
}
DEFAULT_PARAMS = {"rsi_len": 14, "overbought": 70.0, "oversold": 30.0, "swing_len": 10, "rr": 2.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["swing_len"])
    d_long, d_short = (c - lo.rolling(n).min()) / c, (h.rolling(n).max() - c) / c
    os_, ob = p["oversold"], p["overbought"]
    long_e = ((rsi > os_) & (rsi.shift(1) <= os_) & (d_long > 0)).astype(bool)
    short_e = ((rsi < ob) & (rsi.shift(1) >= ob) & (d_short > 0)).astype(bool)
    return long_e, short_e, d_long, d_short


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, d_long, d_short = _signals(bars_df, p)
    sl = d_long.where(long_e, d_short)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}

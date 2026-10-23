"""Broker days, long only: the EMA 9 crossing over the WMA 30 with the MACD line (12 / 26 / 9) above its signal goes long; the long closes after two straight closes under the EMA 9 with the latest close under the WMA 30, or on a MACD bearish crossing.
Port of FMZ strategy #458275 "增强型EMA-WMA交叉策略与综合退出条件Enhanced-EMA-WMA-Crossover-Strategy-with-Comprehensive-Exit-Conditions" (EMA9/WMA30 Crossover Strategy with Enhanced Exit Conditions).

FMZ source id: 458275

Source
    https://www.fmz.com/strategy/458275 (PineScript v5, FMZ last modified 2024-07-31 14:47:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 158-215), EMA 9, WMA 30; MACD 12 / 26 / 9; counters of closes under EMA 9 / WMA 30
    buySignal = crossover(EMA9, WMA30) and macdLine > signalLine -> entry Buy
    belowEMA9Count := close < EMA9 ? +1 : 0;  belowWMA30Count likewise
    position_size > 0 and (belowEMA9Count >= 2 and belowWMA30Count >= 1 or crossunder(macd, signal)) -> close Buy, both counters := 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close tests the position held at the bar's close, so it acts from the bar after the fill; a
      buy signal while long adds nothing and the close still acts. The counters reset to 0 after a close
      (they then count again from the next bar). The points goals, the SMA 200, EMA 21 and VWAP are unused
      (VWAP only plots: held for volume, not used). Long only. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA / WMA crossings confirmed by MACD with close-count and MACD exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_458275_ema9_wma30_cross_macd_close_count_exit_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [30, 40],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 30}


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


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = c.ewm(span=int(p["fast"]), adjust=False).mean()
    w = _wma(c, int(p["slow"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = ((e > w) & (e.shift(1) <= w.shift(1)) & (macd > sig)).to_numpy()
    bear = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    be, bw = (c < e).to_numpy(), (c < w).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, n_e, n_w = 0, 0, 0
    for i in range(m):
        new = pos
        if buy[i] and pos == 0:
            new = 1
        n_e = n_e + 1 if be[i] else 0
        n_w = n_w + 1 if bw[i] else 0
        if pos == 1 and ((n_e >= 2 and n_w >= 1) or bear[i]):
            new, n_e, n_w = 0, 0, 0
        if new != pos:
            if new == 1:
                le[i] = True
            else:
                lx[i] = True
            pos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

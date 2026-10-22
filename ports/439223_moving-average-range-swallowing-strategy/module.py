"""Close / EMA 9 crossings with a swing stop, 45-minute bars: the close crossing over the EMA 9 goes long with a stop at the 10-bar low, crossing under goes short with a stop at the 10-bar high; reversing.
Port of FMZ strategy #439223 "Moving Average Range Swallowing Strategy" (4 MA Strat).

FMZ source id: 439223

Source
    https://www.fmz.com/strategy/439223 (PineScript v4, FMZ last modified 2024-01-18 14:56:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-346), direction 0 (both); position management off; swing stop on, lookback 10, expander 0; MA4 filter off; x close, y MA1 (EMA 9)
    BUY = crossover(close, MA1);  SELL = crossunder(close, MA1);  entry long on BUY, entry short on SELL
    LSL = valuewhen(position changed, lowest(10)) - 0;  SSL = valuewhen(position changed, highest(10));  exit(longexit, stop = LSL), exit(shortexit, stop = SSL) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script fixes the swing level on the bar the position changes (the fill bar, read at its close)
      and keeps the previous trade's level on the fill bar itself. The port takes the 10-bar low (high)
      of the signal bar, as #434998: sl_stop = its distance from the signal close as a fraction, shifted
      one bar inside stops() and re-based on the fill; a level that is not below (above) the close places
      no stop. MA2-MA4 only feed the plots and the filter, which is off. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size is
      sizing. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop from the signal bar.
    2 generic: PASS, close / EMA crossings and swing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the risk input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439223_close_ema9_cross_swing_stop"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma1": [9, 21],
    "swing": [10, 20],
}
DEFAULT_PARAMS = {"ma1": 9, "swing": 10}


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


def _cross(bars_df, p):
    c = bars_df["close"]
    e = c.ewm(span=int(p["ma1"]), adjust=False).mean()
    up = (c > e) & (c.shift(1) <= e.shift(1))
    dn = (c < e) & (c.shift(1) >= e.shift(1))
    return up, dn


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _cross(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _cross(bars_df, p)
    c = bars_df["close"]
    n = int(p["swing"])
    dl = ((c - bars_df["low"].rolling(n).min()) / c).to_numpy()
    ds = ((bars_df["high"].rolling(n).max() - c) / c).to_numpy()
    sl = np.where(up.to_numpy(), dl, np.where(dn.to_numpy(), ds, np.nan))
    sl = np.where(sl > 0, sl, np.nan)
    return {"sl_stop": pd.Series(sl, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}

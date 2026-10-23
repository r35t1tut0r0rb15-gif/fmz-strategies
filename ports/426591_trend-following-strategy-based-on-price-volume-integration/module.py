"""A rising Hull average of volume (HMA 15) together with a rising Hull average of the close (HMA 15), broker days, long only: both rising with the close over its SMA 10 goes long; either one not rising or the close under the SMA 10 closes.
Port of FMZ strategy #426591 "Trend Following Strategy Based on Price Volume Integration" (VOLLY PRICE CONVERGE).

FMZ source id: 426591

Source
    https://www.fmz.com/strategy/426591 (PineScript v5, FMZ last modified 2023-09-13 15:25:20).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 67-95), HMA 15 of volume and of close; SMA 10 of close (SMA 20 / 50 unused); qty = equity / close
    signal = (hma(volume, 15) > hma(volume, 15)[1]) + (hma(close, 15) > hma(close, 15)[1])
    signal == 2 and close > sma(close, 10) -> entry Long;  signal == 1 or signal == 0 or close < sma(close, 10) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.hma is wma(2 wma(x, n / 2) - wma(x, n), floor(sqrt(n))) with n / 2 taken as an integer (as
      #376260). A bar whose Hull values are not yet defined counts as not rising. Long only. The
      equity / close quantity is sizing. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price and volume Hull-average agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity / close stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the rising test of hma(volume, 15); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426591_hma15_volume_and_close_rising_sma10_long"
FAMILY = "volume_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hma_len": [15, 9],
    "base_len": [10, 20],
}
DEFAULT_PARAMS = {"hma_len": 15, "base_len": 10}


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
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["hma_len"])
    hv, hc = _hma(v, n), _hma(c, n)
    sig = (hv > hv.shift(1)).astype(int) + (hc > hc.shift(1)).astype(int)
    base = c.rolling(int(p["base_len"])).mean()
    le = (sig == 2) & (c > base)
    lx = (sig <= 1) | (c < base)
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}

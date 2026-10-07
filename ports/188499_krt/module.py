"""Keltner-style channel (EMA of typical price +/- EMA of H-C) close breakout, stop-and-reverse.
Port of FMZ strategy #188499 "KRT凯尔特纳通道" (KRT Keltner channel).

Source
    https://www.fmz.com/strategy/188499 (MyLanguage, author "cyberking", FMZ last modified
    2020-03-05 11:41:52). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 30-36)
    ZF = H-C;  DX = H+L+C)/3   [sic]
    KRTHR = EMA(DX,10) + EMA(ZF,10);  KRTXR = EMA(DX,10) - EMA(ZF,10)
    C > KRTHR -> BPK;   C < KRTXR -> SPK;   AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * `DX:=H+L+C)/3` has an unbalanced parenthesis (also in the description). The port uses the
      evident typical price (H+L+C)/3, which the comment names ("典型价格").
    * Daily bars (backtest period 1d) are broker days (17:00 New York); close-price model.
    * BPK/SPK reverse in one bar: REVERSAL INTENDED (portfolio_kwargs {}; the engine's default
      opposite-entry reversal applies). Always in after the first signal.
    * The band width is an EMA of a price range, so it scales with volatility: criterion 2 PASS.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_188499_krt_keltner_reverse"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [5, 10, 20, 30],
}
DEFAULT_PARAMS = {"n": 10}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["n"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = ((h + lo + c) / 3).ewm(span=n, adjust=False).mean()
    width = (h - c).ewm(span=n, adjust=False).mean()
    warm = np.arange(len(c)) >= n - 1        # no signal before n bars exist
    long_sig = (warm & (c > mid + width)).to_numpy()
    short_sig = (warm & (c < mid - width)).to_numpy()

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if long_sig[i] and pos != 1:
            le[i], pos = True, 1
        elif short_sig[i] and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}

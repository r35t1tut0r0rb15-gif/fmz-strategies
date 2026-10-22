"""Pullbacks in an uptrend, daily bars, long only: from flat, the close above the SMA 280 but under the SMA 13, with the SMA 13 3 % to 27 % above the SMA 280, goes long; a close above the SMA 13 under the
previous low, or a close 7 % under the fill, closes.
Port of FMZ strategy #442929 "Pullback Trading Strategy Based on Dynamic Moving Average" (Profitable Pullback Trading Strategy).

FMZ source id: 442929

Source
    https://www.fmz.com/strategy/442929 (PineScript v5, FMZ last modified 2024-02-27 14:38:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-153), SMA 280 / 13; too deep 0.27, too thin 0.03; stop 0.07; 100 % of equity, capital 1000
    buy = close > ma280 and close < ma13 and flat and 0.03 < ma13 / ma280 - 1 < 0.27 -> entry Long;  buy[1] -> buy_price = open
    close > ma13 and long and close < low[1] -> close;  long and (buy_price - close) / close > 0.07 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * buy_price is the open of the bar after the signal, the fill price. The stop input is a fraction
      (0.07 = 7 %), as written. The closes are bar-close tests filled at the next open. Long only. The
      100 % of equity size and capital are sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA pullback band; close-vs-fill stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442929 (2 members, best partner #449852, Jaccard 0.850); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442929_sma280_13_pullback_fill_stop_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length1": [280, 200],
    "ma_length2": [13, 20],
}
DEFAULT_PARAMS = {"ma_length1": 280, "ma_length2": 13, "sl": 0.07, "too_deep": 0.27, "too_thin": 0.03}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    m1 = c.rolling(int(p["ma_length1"])).mean()
    m2 = c.rolling(int(p["ma_length2"])).mean()
    gap = m2 / m1 - 1
    go = ((c > m1) & (c < m2) & (gap < float(p["too_deep"])) & (gap > float(p["too_thin"]))).to_numpy()
    x1 = ((c > m2) & (c < lo.shift(1))).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    sl = float(p["sl"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fill = False, np.nan
    for i in range(m):
        if go[i] and not held:
            le[i] = True
            if i + 1 < m:
                fill = ov[i + 1]
        elif held and (x1[i] or (fill - cv[i]) / cv[i] > sl):
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

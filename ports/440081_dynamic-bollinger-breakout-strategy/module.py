"""Deep lower-band dips, long only, 1-hour bars: a close more than a fixed margin under the lower Bollinger band (20, 2) goes long; a close well above the lower band, or 1.25 % above the entry price, closes;
the price-unit margins are read as fractions.
Port of FMZ strategy #440081 "Dynamic Bollinger Breakout Strategy" (布林通道策略多5min).

FMZ source id: 440081

Source
    https://www.fmz.com/strategy/440081 (PineScript v5, FMZ last modified 2024-01-26 14:52:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-187), BB 20 x 2; buy threshold 58, exit threshold 470 (price units); "stop" -1.25 %; 10 x equity / close quantity
    buy = close < lower - 58 -> entry BuyLong;  exit = close > lower + 470 -> close BuyLong;  if long and (avg - close) / avg x 100 <= -1.25: close BuyLong

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 58 and 470 thresholds are price units; they become fractions of the close, 58 /
      42000 and 470 / 42000 (the BTC reading). The "stop" test is (avg - close) / avg <= -1.25 %, which
      is a close 1.25 % ABOVE the average (fill) price: a profit target at the bar close, as written.
      One position is held (pyramiding 1). The entry and the closes act on the position held at the bar
      close. Long only. The quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit band margins -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440081_deep_lower_band_dip_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_frac": [0.00138, 0.005],
    "exit_frac": [0.0112, 0.02],
}
DEFAULT_PARAMS = {"buy_frac": 0.00138, "exit_frac": 0.0112, "length": 20, "mult": 2.0, "gain": 1.25}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    lower = c.rolling(n).mean() - float(p["mult"]) * c.rolling(n).std(ddof=0)
    buy = (c < lower - float(p["buy_frac"]) * c).to_numpy()
    ex = (c > lower + float(p["exit_frac"]) * c).to_numpy()
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    g = float(p["gain"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ep = 0, np.nan
    for i in range(m):
        if pos == 1:
            if ex[i] or cv[i] >= ep * (1 + g):
                lx[i], pos = True, 0
        elif buy[i] and i + 1 < m:
            le[i], pos, ep = True, 1, ov[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

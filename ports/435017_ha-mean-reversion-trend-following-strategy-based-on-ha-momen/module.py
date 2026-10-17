"""Body-momentum breakouts in the SMA 20 / 200 trend, 45-minute bars: a green bar whose body is more than twice the average of
the last 5 bodies, closing above the SMA 20 with the SMA 20 above the SMA 200, goes long; the red mirror goes short
(reversing). Each trade carries a 500-tick stop and a 1500-tick target, re-expressed as ATR multiples.
Port of FMZ strategy #435017 "基于均线和HA动量突破的趋势跟踪策略Mean-Reversion-Trend-Following-Strategy-Based-on-HA-Momentum-Breakout" (HA Trend Following).

FMZ source id: 435017

Source
    https://www.fmz.com/strategy/435017 (PineScript v3, FMZ last modified 2023-12-11 16:56:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 181-207), MA 200 trend, SMA 20; body strength 2; loss 500 / profit 1500 ticks (regular candles, not Heikin-Ashi)
    mom = |open - close| / sma(|open - close|, 5);  close > sma20 > sma200 and mom > 2 and close > open -> entry long;  mirror -> entry short
    exit(loss = 500, profit = 1500) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Despite the name the candles are the chart's own. Criterion 2: 500 / 1500 ticks of 0.1 on
      45-minute BTC (50 / 150 USD) are about 0.33 / 1.0 x the Wilder ATR 14 of the signal bar
      (fractions of the signal close shifted one bar inside stops(), re-based on the fill).
    * strategy.entry reverses: REVERSAL INTENDED. The 2 % of equity is sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 2 % of equity stored; the tick bracket quoted in original_sizing.txt.
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

NAME = "fmz_435017_body_momentum_trend_bracket"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "strength": [2.0, 1.5],
    "sl_atr": [0.33, 1.0],
}
DEFAULT_PARAMS = {"trend_len": 200, "strength": 2.0, "sl_atr": 0.33, "tp_mult": 3.0, "atr_len": 14}


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
    o, c = bars_df["open"], bars_df["close"]
    rng = (o - c).abs()
    mom = rng / rng.rolling(5).mean().replace(0.0, np.nan)
    s20, sl_ = c.rolling(20).mean(), c.rolling(int(p["trend_len"])).mean()
    k = float(p["strength"])
    le = ((c > s20) & (s20 > sl_) & (mom > k) & (c - o > 0)).astype(bool)
    se = ((c < s20) & (s20 < sl_) & (mom > k) & (c - o < 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["sl_atr"])
    return {"sl_stop": f.shift(1), "tp_stop": (f * float(p["tp_mult"])).shift(1)}


def portfolio_kwargs(**params):
    return {}

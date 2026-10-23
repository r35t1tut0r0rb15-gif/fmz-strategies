"""One-minute bars: the price MACD above its signal, an altered-OBV MACD above its signal, and a rising volume-regression price prediction lying between the open and the close go long; a falling altered-OBV MACD under its signal with the price MACD under its signal and the close under the prediction goes short; reversing.
Port of FMZ strategy #435467 "线性MACD解锁交易视图中线性回归的魔力Linear-MACD-Unlocking-the-Magic-of-Linear-Regression-in-TradingView" (Linear On MACD (stocktechbot)).

FMZ source id: 435467

Source
    https://www.fmz.com/strategy/435467 (PineScript v5, FMZ last modified 2023-12-15 10:22:50).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 101-196), altered OBV MACD 12 / 26 / 9 (EMA); price MACD 12 / 26 / 9; regression lookback 21 (close on volume); risk tolerance LOW
    obvalt = cum(sign(chng) x volume) (chng as #432241);  macd / signal of obvalt;  predicted = a + b x volume from linregs(close, volume, 21)
    macdLine > signalLine and macd > signal and open < predicted < close and rising(predicted, 1) -> entry long;  falling(macd, 1) and macd < signal and macdLine < signalLine and close < predicted -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The altered OBV is the one of #432241 (same author); the regression prediction as #435270 (each
      bar's deviations from that bar's own 21-bar means, summed). Risk tolerance LOW uses the prediction
      itself as the short level. ta.rising(x, 1) / ta.falling(x, 1) compare with the previous value. Both
      are unit-free in the volume. REVERSAL INTENDED. margin settings are sizing. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, OBV MACD and volume-regression prediction filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): margin_long 100, margin_short 100, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the altered OBV MACD and the close-on-volume regression; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435467_obv_macd_volume_regression_prediction_1m_reversal"
FAMILY = "volume_regression"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "fast_len": [12, 8],
}
DEFAULT_PARAMS = {"length": 21, "fast_len": 12, "slow_len": 26, "signal_len": 9}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _predicted(c, v, n):
    """The source's linregs(close, volume, n): each bar's deviation from that bar's own n-bar means,
    summed over n bars (series arithmetic, as Pine evaluates it), then a + b x volume."""
    yb, xb = c.rolling(n).mean(), v.rolling(n).mean()
    den = ((v - xb) ** 2).rolling(n).sum()
    b = ((v - xb) * (c - yb)).rolling(n).sum() / den.where(den != 0)
    return yb - b * xb + b * v


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    pc = c.shift(1)
    chng = np.where((c < pc) & (o < c), 1.0, np.where(c > pc, 1.0, -1.0))
    obv = (pd.Series(chng, index=c.index) * v).cumsum()
    macd = _ema(obv, int(p["fast_len"])) - _ema(obv, int(p["slow_len"]))
    sig = _ema(macd, int(p["signal_len"]))
    pm = _ema(c, 12) - _ema(c, 26)
    ps = _ema(pm, 9)
    pr = _predicted(c, v, int(p["length"]))
    long_c = (pm > ps) & (macd > sig) & (o < pr) & (pr < c) & (pr > pr.shift(1))
    short_c = (macd < macd.shift(1)) & (macd < sig) & (pm < ps) & (c < pr)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return long_c & ~short_c, false, short_c & ~long_c, false.copy()


def portfolio_kwargs(**params):
    return {}

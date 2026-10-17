"""HPotter STARC bands, 2-hour bars: a close above SMA 5 + 1.33 ATR 15 goes long, a close below SMA 5 - 1.33 ATR 15 goes
short; the side is held in between and reverses on the opposite break.
Port of FMZ strategy #434325 "STARC通道回测策略STARC-Channel-Backtest-Strategy" (STARC Bands Backtest).

FMZ source id: 434325

Source
    https://www.fmz.com/strategy/434325 (PineScript v2, FMZ last modified 2023-12-05 14:52:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 172-188), MA 5, ATR 15, K 1.33, reverse false
    pos = close > sma(5) + 1.33 atr(15) ? 1 : close < sma(5) - 1.33 atr(15) ? -1 : pos[1];  pos 1 -> entry long;  pos -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The side holds until the opposite break; strategy.entry reverses: REVERSAL INTENDED. reverse is
      false. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_434325_starc_band_side"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [5, 10],
    "k": [1.33, 2.0],
}
DEFAULT_PARAMS = {"ma_len": 5, "atr_len": 15, "k": 1.33}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    ma = c.rolling(int(p["ma_len"])).mean()
    up = (c > ma + atr * float(p["k"])).to_numpy()
    dn = (c < ma - atr * float(p["k"])).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}

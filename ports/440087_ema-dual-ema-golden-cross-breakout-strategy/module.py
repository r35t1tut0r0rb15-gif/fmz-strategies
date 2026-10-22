"""EMA 26 / 200 crosses and EMA 200 reclaims with a 2 % target, 1-hour bars: an EMA 26 cross over the EMA 200 with the close above both, or the close crossing over the EMA 200, goes long; an EMA cross down
with the close under both goes short; a close 2 % beyond the entry or the opposite EMA cross closes; reversing.
Port of FMZ strategy #440087 "双EMA黄金交叉突破策略Dual-EMA-Golden-Cross-Breakout-Strategy" (EMA Buy/Sell Signal).

FMZ source id: 440087

Source
    https://www.fmz.com/strategy/440087 (PineScript v5, FMZ last modified 2024-01-26 15:13:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-215), EMA 26 / 200; take profit 2 %, stop input 1 % (unused); qty 1
    long = (crossover(ema26, ema200) and close > both) or crossover(close, ema200) -> entry Buy;  close Buy when close >= avg x 1.02 or crossunder(ema26, ema200)
    short = crossunder(ema26, ema200) and close < both -> entry Sell;  close Sell when close <= avg x 0.98 or crossover(ema26, ema200)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target and the "stop" are bar-close tests (market closes at the next open), not orders. The
      average price is the fill open. The closes follow their side's entry: a short entry on an EMA
      cross down also closes a held long first and the short stands; a long entry reversing a short
      stands although the short's close follows (as #438020). The stop-loss input is never used.
      strategy.entry reverses: REVERSAL INTENDED. The quantity of 1 is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and a percent target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity and percent inputs stored.
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

NAME = "fmz_440087_ema26_200_cross_reclaim_target"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "take_profit": [0.02, 0.05],
    "ema1": [26, 50],
}
DEFAULT_PARAMS = {"take_profit": 0.02, "ema1": 26, "ema2": 200}


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
    a = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    b = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    xo = (a > b) & (a.shift(1) <= b.shift(1))
    xu = (a < b) & (a.shift(1) >= b.shift(1))
    cb = (c > b) & (c.shift(1) <= b.shift(1))
    le = ((xo & (c > a) & (c > b)) | cb).to_numpy()
    se = (xu & (c < a) & (c < b)).to_numpy()
    xo, xu = xo.to_numpy(), xu.to_numpy()
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    tp = float(p["take_profit"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, ep = 0, np.nan
    for i in range(m):
        new = pos
        if le[i] and pos != 1:
            new = 1
        if pos == 1 and new == 1 and (cv[i] >= ep * (1 + tp) or xu[i]):
            new = 0
        if se[i] and new != -1:
            new = -1
        if pos == -1 and new == -1 and (cv[i] <= ep * (1 - tp) or xo[i]):
            new = 0
        if new != pos and new != 0:
            ep = ov[i + 1] if i + 1 < m else np.nan
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}

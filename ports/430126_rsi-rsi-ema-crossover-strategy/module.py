"""EMA stack with an RSI band, 1-hour bars, long only: a close above the EMA 17, 35 and 142 with RSI 26 between 42 and 70
goes long; the EMA 17 crossing under the EMA 35, or the RSI crossing under 42, closes it.
Port of FMZ strategy #430126 "RSI均线交叉策略RSI-EMA-Crossover-Strategy" (EMA Cross V1).

FMZ source id: 430126

Source
    https://www.fmz.com/strategy/430126 (PineScript v5, FMZ last modified 2023-10-25 11:46:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 163-231), RSI 26, lines 42 / 70, EMA 17 / 35 / 142
    longC1 = close > emaF and close > emaM and close > emaS; co = rsi >= 42 and rsi < 70
    longC1 and co -> entry long
    crossunder(emaF, emaM) or crossunder(rsi, 42) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close is written after the entry: a bar that both qualifies and closes ends flat when
      already long, and long when flat (strategy.close has no open trade to close yet).
    * The 2011-2025 start / end inputs are the author's backtest window: dropped. Long only;
      Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430126_ema_stack_rsi_band_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [26, 14],
    "m_line": [42, 50],
}
DEFAULT_PARAMS = {"rsi_len": 26, "m_line": 42, "over_b": 70, "fast": 17, "medium": 35, "slow": 142}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ef, em, es = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "medium", "slow"))
    entry = ((c > ef) & (c > em) & (c > es) & (r >= p["m_line"]) & (r < p["over_b"])).to_numpy()
    xu_ema = (ef < em) & (ef.shift(1) >= em.shift(1))
    xu_rsi = (r < p["m_line"]) & (r.shift(1) >= p["m_line"])
    ex = (xu_ema | xu_rsi).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if entry[i]:
            pos = 1
        if ex[i] and start == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

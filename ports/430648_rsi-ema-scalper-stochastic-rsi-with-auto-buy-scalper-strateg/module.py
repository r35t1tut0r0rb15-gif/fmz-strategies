"""Stochastic RSI scalper, 1-hour bars, long only from flat: K under 17 and above D goes long; K over 90 turning down below
D, a close 1.5 % under the entry, or (after 1 % profit on hlc3) a turn of the hlc3 SMA 12 with K over 20 closes it.
Port of FMZ strategy #430648 "基于随机-RSI-和-EMA-的自主买入式震荡Scalper策略Stochastic-RSI-with-Auto-Buy-Scalper-Strategy" (Stochastic RSI W Auto Buy Scalper Scirpt III).

FMZ source id: 430648

Source
    https://www.fmz.com/strategy/430648 (PineScript v5, FMZ last modified 2023-10-31 11:34:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 118-158), RSI 14, stochastic 14, K 3, D 3; stop 1.5 %, profit 1 %
    flat and k < 17 and k > d -> entry long
    (k > 90 and k < d and falling(k, 2)) or close < entry x 0.985 -> close
    change(sma(hlc3, 12), 3) > 0 and hlc3 < hlc3[1] and k > 20 and hlc3 > entry x 1.01 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and the profit test read bar closes (hlc3) and close with strategy.close (market
      exits at the next open): exit signals, from the entry price = the fill (the next open after
      the signal). Exits are tested from the fill bar on.
    * falling(k, 2) is k below each of its previous 2 values. Long only; Opposite entries cannot
      occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, stochastic-RSI levels, moving averages and percentages.
    3 crypto-exchange-only: no ("BTCUSD" in the alert texts only; exchange pair in the header).
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

NAME = "fmz_430648_stochrsi_auto_buy_scalper_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_entry": [17, 25],
    "stop_pct": [1.5, 3.0],
}
DEFAULT_PARAMS = {"smooth_k": 3, "smooth_d": 3, "rsi_len": 14, "stoch_len": 14, "k_entry": 17, "stop_pct": 1.5,
                  "profit_pct": 1.0}


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
    h, lo, c, o = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["open"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    ll, hh = r.rolling(n).min(), r.rolling(n).max()
    k = (100 * (r - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    falling = k < pd.concat([k.shift(1), k.shift(2)], axis=1).min(axis=1, skipna=False)
    hlc3 = (h + lo + c) / 3
    sma12 = hlc3.rolling(12).mean()
    flip = ((sma12 - sma12.shift(3)) > 0) & (hlc3 < hlc3.shift(1))
    entry = ((k < p["k_entry"]) & (k > d)).to_numpy()
    turn = ((k > 90) & (k < d) & falling).to_numpy()
    flip_k = (flip & (k > 20)).to_numpy()
    cv, hv, ov = c.to_numpy(dtype=float), hlc3.to_numpy(dtype=float), o.to_numpy(dtype=float)
    sl, pr = float(p["stop_pct"]) / 100, float(p["profit_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg, pending = 0, np.nan, False
    for i in range(m):
        if pending:                                  # the entry fills at this bar's open
            avg, pending = ov[i], False
        if pos == 1 and (turn[i] or cv[i] < avg * (1 - sl) or (flip_k[i] and hv[i] > avg * (1 + pr))):
            pos, avg = 0, np.nan
        elif pos == 0 and entry[i]:
            pos, pending = 1, True
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

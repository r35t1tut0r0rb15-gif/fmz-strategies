"""RSI and Bollinger impulse (Spyfrat), 4-hour bars: RSI 30 between 52 and 65 with a %B-style impulse (the change of a
scaled band position) between 0.11 and 0.7 goes long, the mirror goes short; the source's tick target and stop become
ATR fractions.
Port of FMZ strategy #430977 "RSI-BB动量突破策略RSI-BB-Momentum-Breakout-Strategy" (Spyfrat Strat).

FMZ source id: 430977

Source
    https://www.fmz.com/strategy/430977 (PineScript v4, FMZ last modified 2023-11-03 15:02:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 230-269), BB 50 / 0.2, RSI 30 (rma), TP 2500 / SL 200 ticks, trail off
    bbr = close > upper ? (close - upper) / (upper - lower) / 10 : close < lower ? (close - lower) / (upper - lower) / 10 : 0.1
    bbi = bbr - nz(bbr[1])
    long = 52 < rsi < 65 and 0.11 < bbi < 0.7 -> entry long;  short = 35 < rsi < 48 and -0.7 < bbi < -0.11 -> entry short
    exit(profit = 250 x 10, loss = 20 x 10 ticks) for each side; trail_points 0 (off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the target and stop are 2500 / 200 ticks (250 / 20 USD on BTC_USDT at mintick 0.1);
      they become tp_atr / sl_atr x the Wilder ATR 14 of the signal bar, as fractions of its close
      (250 USD is about 0.8 ATR and 20 USD about 0.07 ATR on 4-hour BTC), fixed at entry.
    * Entries are re-issued on every qualifying bar; strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. stdev is the
      population deviation. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick target / stop -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430977_rsi_bb_impulse"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.07, 1.0],
    "tp_atr": [0.8, 2.0],
}
DEFAULT_PARAMS = {"length": 50, "mult": 0.2, "rsi_len": 30, "atr_len": 14, "sl_atr": 0.07, "tp_atr": 0.8}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + p["mult"] * sd, basis - p["mult"] * sd
    w = upper - lower
    bbr = pd.Series(np.where(c > upper, (c - upper) / w / 10, np.where(c < lower, (c - lower) / w / 10, 0.1)),
                    index=c.index).where(basis.notna())
    bbi = bbr - bbr.shift(1).fillna(0.0)
    r = _rsi(c, int(p["rsi_len"]))
    lg = (r > 52) & (r < 65) & (bbi > 0.11) & (bbi < 0.7)
    sh = (r < 48) & (r > 35) & (bbi < -0.11) & (bbi > -0.7)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return lg.astype(bool), sh.astype(bool), af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}

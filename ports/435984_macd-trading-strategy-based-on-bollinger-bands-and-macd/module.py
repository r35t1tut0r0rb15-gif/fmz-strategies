"""Lower-band touch and MACD rebound buys with a ratcheting close-based exit, 1-hour bars, long only, from flat: after a touch of the lower Bollinger
band with the MACD over its signal (or an expected rebound), buy; a ratchet at the close minus 2 ATR (never lowered) closes the long when
a close falls to it, as a take profit above the entry price or a stop loss below it (not on the entry bar's first bar).
Port of FMZ strategy #435984 "基于布林带和MACD的量化交易策略Trading-Strategy-Based-on-Bollinger-Bands-and-MACD" ([KL] BOLL + MACD Strategy v2).

FMZ source id: 435984

Source
    https://www.fmz.com/strategy/435984 (PineScript v4, FMZ last modified 2023-12-20 15:55:18).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 145-225), Bollinger 20 / 2; MACD 12 / 26 / 9; ATR 26 x 2; risk : reward mode off
    touched = low <= lower band (reset while long);  buy = touched and MACD > signal or (MACD > MACD[1] and |MACD - signal| < |MACD[1] - signal[1]|);  flat and buy -> entry long, entry_price = close, stop = close - 2 ATR
    stop = max(stop, close - 2 ATR at entry);  long and close <= stop: close > entry_price -> close (take profit), else close <= entry_price and bar_count -> close (stop loss)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the script's own level compared with closes, filled at the next open: a close-based
      exit signal, not a broker stop (no mark). While flat the level is the bar's low and the entry is
      taken from flat only. bar_count counts bars since the entry bar; a stop-level touch on the entry
      bar's first following bar with bar_count 0 does not close (as written). The reward-ratio exit is off.
      Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, band touch, MACD and an ATR ratchet.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435984_boll_macd_rebound_atr_ratchet"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multi": [2, 3],
    "boll_len": [20, 30],
}
DEFAULT_PARAMS = {"atr_multi": 2, "boll_len": 20, "boll_mult": 2.0, "atr_len": 26, "fast": 12, "slow": 26, "signal": 9}


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
    n = int(p["boll_len"])
    lower = c.rolling(n).mean() - float(p["boll_mult"]) * c.rolling(n).std(ddof=0)
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    amacd = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr_buf = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_multi"])).to_numpy()
    touched_in = (lo <= lower).fillna(False).to_numpy()
    rebound = ((macd > macd.shift(1)) & ((macd - amacd).abs() < (macd.shift(1) - amacd.shift(1)).abs())).fillna(False).to_numpy()
    above = (macd > amacd).fillna(False).to_numpy()
    cv, lv, ov = c.to_numpy(dtype=float), lo.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    pend = None
    touched = False
    entry_price = 0.0
    trailing = 0.0
    stop = 0.0
    bar_count = 0
    for i in range(m):
        if pend == "enter":
            pos = 1
        elif pend == "exit":
            pos = 0
        pend = None
        stop = max(stop, cv[i] - trailing)
        if pos == 0:
            stop = lv[i]
        if touched_in[i]:
            touched = True
        elif pos > 0:
            touched = False
        buy = (touched and above[i]) or rebound[i]
        if pos == 0 and buy and not np.isnan(atr_buf[i]):
            entry_price, trailing = cv[i], atr_buf[i]
            stop = cv[i] - atr_buf[i]
            le[i], pend = True, "enter"
            bar_count = 0
        elif pos > 0:
            bar_count += 1
        if pos > 0 and cv[i] <= stop:
            if cv[i] > entry_price:
                lx[i], pend = True, "exit"
                stop = 0.0
            elif cv[i] <= entry_price and bar_count:
                lx[i], pend = True, "exit"
                stop = 0.0
            bar_count = 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

"""Stochastic RSI cross entries in an EMA 50 / 100 / 200 stack, 1-minute bars: %K crossing over %D at or under 23 with the stack up and the low
over the EMA 200 goes long; %K crossing under %D at or over 77 with the stack down and the high under the EMA 200 goes short
(reversing); a long is closed by a %K cross over %D at or over 23 or the EMA 50 crossing under the EMA 100 (a short mirrors).
Port of FMZ strategy #435503 "Dual Moving Average Triple Exponential Indicator Trading Strategy" (5212 EMA Strategy).

FMZ source id: 435503

Source
    https://www.fmz.com/strategy/435503 (PineScript v5, FMZ last modified 2023-12-15 15:39:45).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 186-231), StochRSI 28 / 28 / K 6 / D 6; EMA 50 / 100 / 200; levels 23 / 77
    longCond = crossover(k, d) and k <= 23 and ema50 > ema100 and ema100 > ema200 and low > ema200;  shortCond = crossunder(k, d) and k >= 77 and ema50 < ema100 and ema100 < ema200 and high < ema200
    shortClose = crossover(k, d) and k >= 23 closes the LONG, or crossunder(ema50, ema100);  longClose = crossunder(k, d) and k <= 77 closes the SHORT, or crossover(ema50, ema100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The names are crossed in the script (a "shortClose" closes the long), ported as the orders
      read. The date range inputs (from 16 April 2021) only set unused variables: calcPeriod is true.
      The four orders (entry long, close long, entry short, close short) are filled in the script's
      call order at the next open, so a bar that both opens a position and closes it ends flat.
      The percent-of-equity size (10 %) is sizing. REVERSAL INTENDED. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic RSI and EMA stack.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_435503_stoch_rsi_ema_stack"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_rsi": [28, 14],
    "lo_level": [23, 30],
}
DEFAULT_PARAMS = {"length_rsi": 28, "length_stoch": 28, "smooth_k": 6, "smooth_d": 6, "lo_level": 23,
                  "e1": 50, "e2": 100, "e3": 200}


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
    n = int(p["length_rsi"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    ls = int(p["length_stoch"])
    with np.errstate(invalid="ignore", divide="ignore"):
        st = 100 * (rsi - rsi.rolling(ls).min()) / (rsi.rolling(ls).max() - rsi.rolling(ls).min())
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    e1, e2, e3 = (c.ewm(span=int(p[x]), adjust=False).mean() for x in ("e1", "e2", "e3"))
    xo = (k > d) & (k.shift(1) <= d.shift(1))
    xu = (k < d) & (k.shift(1) >= d.shift(1))
    lvl_lo = float(p["lo_level"])
    lvl_hi = 100.0 - lvl_lo
    ema_long = (e1 > e2) & (e2 > e3) & (lo > e3)
    ema_short = (e1 < e2) & (e2 < e3) & (h < e3)
    long_cond = (xo & (k <= lvl_lo) & ema_long).to_numpy()
    short_cond = (xu & (k >= lvl_hi) & ema_short).to_numpy()
    long_close = ((xo & (k >= lvl_lo)) | ((e1 < e2) & (e1.shift(1) >= e2.shift(1)))).to_numpy()
    short_close = ((xu & (k <= lvl_hi)) | ((e1 > e2) & (e1.shift(1) <= e2.shift(1)))).to_numpy()
    m = len(long_cond)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    e_l = c_l = e_s = c_s = False
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            if e_l and pos <= 0:
                pos = 1
            if c_l and pos == 1:
                pos = 0
            if e_s and pos >= 0:
                pos = -1
            if c_s and pos == -1:
                pos = 0
        held[i] = pos
        e_l, c_l, e_s, c_s = bool(long_cond[i]), bool(long_close[i]), bool(short_cond[i]), bool(short_close[i])
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}

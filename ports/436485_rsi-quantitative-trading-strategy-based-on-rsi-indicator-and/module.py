"""Fast / slow SMA crossings with RSI timing, 1-minute bars: an SMA 11 crossing over the SMA 82 buys when the RSI 14 is under 80 (otherwise it waits until the RSI falls under 75); crossing under sells
when the RSI is over 20 (otherwise waits for over 25); an RSI over 80 (long) or under 20 (short) closes with a profit and the position is re-opened once the RSI is back inside.
Port of FMZ strategy #436485 "基于RSI指标和移动平均线的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-Indicator-and-Moving-Average" (策略_RSI+移动揉搓线_).

FMZ source id: 436485

Source
    https://www.fmz.com/strategy/436485 (PineScript v4, FMZ last modified 2023-12-25 11:40:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 170-250), SMA 11 / 82; RSI 14; limits 80 / 20 (exit) and 75 / 25 (late entry)
    cross up: long_f = true, short_f = false; rsi < 80 -> entry long, rsi > 80 -> long_open_pending;  cross down: short_f = true; rsi > 20 -> entry short, rsi < 20 -> short_open_pending
    pending long and flat and rsi < 75 -> entry long;  pending short and flat and rsi > 25 -> entry short;  long and rsi > 80 -> close_all, long_rsi_over_buy;  short and rsi < 20 -> close_all, short_rsi_over_sell;  over-bought flag, flat and rsi < 80 -> entry long;  over-sold flag, flat and rsi > 20 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags are followed inside simulate; the conditions that read the position use the position at the
      bar's open. The eight rules of one bar are filled in the script's call order at the next open. REVERSAL
      INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings and RSI timing.
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

NAME = "fmz_436485_sma_cross_rsi_timing"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [11, 8],
    "slow": [82, 60],
}
DEFAULT_PARAMS = {"fast": 11, "slow": 82, "length": 14, "hi": 80, "lo": 20, "late_long": 75, "late_short": 25}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    n = int(p["length"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna()).to_numpy()
    cross_up = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False).to_numpy()
    cross_dn = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False).to_numpy()
    hi, lo, ll, ls = float(p["hi"]), float(p["lo"]), float(p["late_long"]), float(p["late_short"])
    m = len(rsi)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    long_f = short_f = lop = sop = lob = sos = False
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the order the script sent them
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "X" and pos != 0:
                    pos = 0
        held[i] = pos
        ops = []
        r = rsi[i]
        if cross_up[i]:
            sos = False
            long_f, short_f = True, False
            if r < hi:
                ops.append("eL")
            if r > hi:
                lop = True
        if cross_dn[i]:
            lob = False
            long_f, short_f = False, True
            if r > lo:
                ops.append("eS")
            if r < lo:
                sop = True
        if long_f and lop and pos == 0 and r < ll:
            ops.append("eL")
            lop = False
        if short_f and sop and pos == 0 and r > ls:
            ops.append("eS")
            sop = False
        if pos > 0 and long_f and r > hi:
            ops.append("X")
            lob = True
        if pos < 0 and short_f and r < lo:
            ops.append("X")
            sos = True
        if long_f and lob and pos == 0 and r < hi:
            lob = False
            ops.append("eL")
        if short_f and sos and pos == 0 and r > lo:
            sos = False
            ops.append("eS")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}

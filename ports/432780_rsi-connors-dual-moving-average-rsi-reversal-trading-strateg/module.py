"""Connors RSI 2 extremes in the SMA 200 trend, 1-hour bars: the RSI 2 under 5 above the SMA 200 goes long, over 95 below it
goes short; the close back across the SMA 5 closes the trade, and so does the "stop" test as written, which is true on
almost every bar (close at or above 97 % of the fill for a long), so most trades last one bar.
Port of FMZ strategy #432780 "康纳双均线RSI反转交易策略Connors-Dual-Moving-Average-RSI-Reversal-Trading-Strategy" (Connors RSI-MA Strategy).

FMZ source id: 432780

Source
    https://www.fmz.com/strategy/432780 (PineScript v5, FMZ last modified 2023-11-21 14:20:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 133-178), RSI 2, SMA 200, exit SMA 5, levels 5 / 95, stop 3 %
    rsi2 < 5 and close > sma200 -> entry long;  rsi2 > 95 and close < sma200 -> entry short
    close > sma5 or close >= avg x (1 - 3 %) -> close long;  close < sma5 or close <= avg x (1 + 3 %) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: the stop tests are inverted (>= / <= instead of < / >), so they close a trade at
      almost any close; the port keeps them (close-checked, rule 3) and the trade's fill price (the
      open after the entry signal). Listed with the as-written ports; the intended version (close
      below / above the 3 % level) is owed.
    * The closes act on the position held at the bar's start; an opposite entry reverses and a later
      close of the other side does not undo it: REVERSAL INTENDED. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, RSI levels, SMA trend and percentages of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the close-checked stop quoted in original_sizing.txt.
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

NAME = "fmz_432780_connors_rsi2_sma_as_written"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [2, 3],
    "exit_ma": [5, 10],
}
DEFAULT_PARAMS = {"rsi_len": 2, "ma_len": 200, "exit_ma": 5, "ob": 95, "os": 5, "sl_pct": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ma = c.rolling(int(p["ma_len"])).mean()
    mx = c.rolling(int(p["exit_ma"])).mean()
    bl = ((r < float(p["os"])) & (c > ma)).to_numpy()
    bs = ((r > float(p["ob"])) & (c < ma)).to_numpy()
    xl_ma, xs_ma = (c > mx).to_numpy(), (c < mx).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = float(p["sl_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        start = pos
        ep = ov[e_i] if start != 0 else np.nan
        if bl[i]:
            pos, e_i = (1, i + 1) if start != 1 else (pos, e_i)
        if bs[i]:
            pos, e_i = (-1, i + 1) if start != -1 else (pos, e_i)
        if start == 1 and pos == 1 and (xl_ma[i] or cv[i] >= ep * (1 - k)):
            pos = 0
        if start == -1 and pos == -1 and (xs_ma[i] or cv[i] <= ep * (1 + k)):
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}

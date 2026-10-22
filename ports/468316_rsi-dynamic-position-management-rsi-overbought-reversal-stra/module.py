"""Shorting two-bar RSI 2 overbought readings under the SMA 200, 2-hour bars, short only: with no open trade, a close under the SMA 200 and the RSI 2 over 75 on this bar and the one before sells short; an RSI 2 under 30 or the SMA 10 crossing over the SMA 30 covers.
Port of FMZ strategy #468316 "动态仓位管理RSI超买反转策略-Dynamic-Position-Management-RSI-Overbought-Reversal-Strategy" (TPS Short Strategy by Larry Conners).

FMZ source id: 468316

Source
    https://www.fmz.com/strategy/468316 (PineScript v5, FMZ last modified 2024-09-26 15:29:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-146), SMA 200 / 10 / 30; RSI 2 over 75 on two bars; exit RSI 2 under 30 or crossover(sma10, sma30); qty 1, scale-in entries Short2-4 (qty 2 / 3 / 4) when the close is over the entry price
    close < sma200 and rsi2[1] > 75 and rsi2 > 75 and no open trade -> entry Short (qty 1)
    close > entry price -> entry Short2, Short3, Short4;  rsi2 < 30 or crossover(sma10, sma30) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default pyramiding of 1 the scale-in entries never fill (#441137), so each trade is the
      first short alone, as the port has it. Entries only from flat; close_all acts only on a position
      held into the bar. The fixed quantities are not ported (sizing is the optimisation layer's). The
      title names the author's rule; the 200 / 10 / 30 lengths are bars of the 2-hour chart. Short only.
      FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI 2 overbought shorts under the SMA 200.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed quantities and scale-in sizes stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468316_rsi2_two_bar_overbought_below_sma200_short"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_long": [200, 100],
    "rsi_th": [75, 90],
    "exit_th": [30, 50],
}
DEFAULT_PARAMS = {"sma_long": 200, "rsi_th": 75, "exit_th": 30, "rsi_len": 2}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    th = float(p["rsi_th"])
    go = ((c < c.rolling(int(p["sma_long"])).mean()) & (r.shift(1) > th) & (r > th)).to_numpy()
    s10, s30 = c.rolling(10).mean(), c.rolling(30).mean()
    out = ((r < float(p["exit_th"])) | ((s10 > s30) & (s10.shift(1) <= s30.shift(1)))).to_numpy()
    m = len(c)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if go[i] and pos == 0:
            se[i], pos = True, -1
        elif out[i] and pos == -1:
            sx[i], pos = True, 0                 # close_all acts only on a position held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}

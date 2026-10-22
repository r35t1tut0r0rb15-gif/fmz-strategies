"""A stacked EMA 14 / 50 / 100 / 200 trend, 1-minute bars: from flat, EMA 14 over the other three with EMA 50 over EMA 100 goes long and EMA 14 crossing back under EMA 50 closes it; EMA 14 under all three with EMA 50 under EMA 200 and ATR 14 over its SMA goes short and EMA 14 over EMA 100 closes it.
Port of FMZ strategy #484584 "Multi Moving Average Trend Capture and Crossover Confirmation Trading System" (etude 9).

FMZ source id: 484584

Source
    https://www.fmz.com/strategy/484584 (PineScript v6, FMZ last modified 2025-03-03 10:11:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 201-321), EMA 14 / 25 (plot only) / 50 / 100 / 200; ATR 14 over its SMA (shorts); RSI and MACD computed but unused
    trending_up and not in_position -> entry Long;  in_position and long and ema14 < ema50 -> close Long
    trending_down and not in_position and atr > sma(atr, 14) -> entry Short;  in_position and short and ema14 > ema100 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The in_position / is_long flags are followed in a loop in the source's order: a long closed on a bar
      frees that bar for a short entry (a reversal); a short closed on a bar can only be followed by a
      long on a later bar. The RSI and MACD filters are computed but feed no order. No sizing code.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked EMA trend states with an ATR filter for shorts.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_484584_ema14_50_100_200_stack_flag_loop_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "instant": [14, 10],
    "longperiod": [200, 100],
}
DEFAULT_PARAMS = {"instant": 14, "longperiod": 200, "shortperiod": 50, "mediumperiod": 100, "atr_length": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    ins, sh, md, lg = ema(p["instant"]), ema(p["shortperiod"]), ema(p["mediumperiod"]), ema(p["longperiod"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    al = int(p["atr_length"])
    atr = _rma(tr, al)
    up = ((ins > sh) & (ins > md) & (ins > lg) & (sh > md)).to_numpy()
    dn = ((ins < sh) & (ins < md) & (ins < lg) & (sh < lg)).to_numpy()
    vol = (atr > atr.rolling(al).mean()).to_numpy()
    lclose = (ins < sh).to_numpy()
    sclose = (ins > md).to_numpy()
    m = len(up)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    in_pos = is_long = False
    for i in range(m):
        if up[i] and not in_pos:
            le[i], in_pos, is_long = True, True, True
        if in_pos and is_long and lclose[i]:
            lx[i], in_pos, is_long = True, False, False
        if dn[i] and not in_pos and vol[i]:
            se[i], in_pos, is_long = True, True, False
        if in_pos and not is_long and sclose[i]:
            sx[i], in_pos = True, False
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~le & ~se), S(se), S(sx & ~se & ~le)


def portfolio_kwargs(**params):
    return {}

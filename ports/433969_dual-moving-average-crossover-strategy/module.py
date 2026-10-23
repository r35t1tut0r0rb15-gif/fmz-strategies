"""15-minute bars, four entry rules in call order (the later one wins on a bar): the SMA 6 of the close crossing over the VWMA 7 of the high goes long, crossing under it goes short; the EMA 2 of the RSI 50 crossing over 32.6 goes long, crossing over 63 goes short; reversing.
Port of FMZ strategy #433969 "Dual Moving Average Crossover Strategy" (Bitlinc Entry v0.1 VWMA / SMA / MRSI SQQQ 94M).

FMZ source id: 433969

Source
    https://www.fmz.com/strategy/433969 (PineScript v4, FMZ last modified 2023-12-01 18:18:16).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 151-233), SMA 6 of close, VWMA 7 of high; RSI 50, EMA 2 / 27, oversold 32.6, overbought 63; window 2018 ..
    crossover(sma(close, 6), vwma(high, 7)) -> entry Long Entry;  crossover(vwma, sma) -> entry Short Entry
    crossover(ema(rsi(close, 50), 2), 32.6) -> entry MRSI Long Entry;  crossover(ema(rsi, 2), 63) -> entry MRSI Short Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * Four entry ids, two per side; with the default pyramiding a second same-side entry adds nothing, so
      each side is one position. On a bar where rules of both sides fire, the later call in the script
      (MRSI Short, then MRSI Long, then Short, then Long, from last to first) is taken. "exitLong" is used as
      the short entry, as written; there are no exits. ma2 (EMA 27) only feeds a commented plot. The 2018
      window is dropped. REVERSAL INTENDED. No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average and RSI-EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the slow line vwma(high, 7); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2018 .. 9999 window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433969_sma6_vwma7_high_cross_mrsi_cross_15m_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [6, 10],
    "slow_len": [7, 14],
}
DEFAULT_PARAMS = {"fast_len": 6, "slow_len": 7, "rsi_len": 50, "ema_len": 2, "oversold": 32.6, "overbought": 63.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c, v = bars_df["high"], bars_df["close"], bars_df["volume"]
    fast = c.rolling(int(p["fast_len"])).mean()
    n = int(p["slow_len"])
    vs = v.rolling(n).sum()
    slow = (h * v).rolling(n).sum() / vs.where(vs != 0)
    ma1 = _rsi(c, int(p["rsi_len"])).ewm(span=int(p["ema_len"]), adjust=False).mean()
    os_l = pd.Series(float(p["oversold"]), index=c.index)
    ob_l = pd.Series(float(p["overbought"]), index=c.index)
    rules = [(_xover(fast, slow), 1), (_xover(slow, fast), -1), (_xover(ma1, os_l), 1), (_xover(ma1, ob_l), -1)]
    tgt = np.zeros(len(c), dtype=np.int8)
    for cond, side in rules:                       # the later call wins
        tgt = np.where(cond.to_numpy(), side, tgt)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tgt == 1, index=ix), false, pd.Series(tgt == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}

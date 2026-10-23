"""Three-hour bars: the average of an RSI 21 and an MFI 21 (of hlc3) crossing above 70 while the EMA 5 rises goes long; the first bar of that average under 30 while the EMA 5 falls goes short; reversing.
Port of FMZ strategy #438930 "RMI Trend Sync Strategy" (RMI Trend Sync - Strategy [presentTrading]).

FMZ source id: 438930

Source
    https://www.fmz.com/strategy/438930 (PineScript v5, FMZ last modified 2024-01-16 14:10:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 165-260), RMI length 21; thresholds 70 / 30; trading direction Both; 8-hour supertrend settings (exits)
    positiveMomentum = rsiMfi[1] < 70 and rsiMfi > 70 and rsiMfi > 30 and change(ema(close, 5)) > 0;  negativeMomentum = rsiMfi < 30 and change(ema(close, 5)) < 0
    longCondition = positive and not positive[1] -> entry Long;  shortCondition = negative and not negative[1] -> entry Short;  exit("Exit Long", when = shortCondition, stop = ...);  exit("Exit Short", when = longCondition, stop = ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * positive / negative are na on bars with neither momentum; the edge test treats na as false, so
      longCondition is a positiveMomentum bar (it cannot repeat) and shortCondition the first of a run
      of negativeMomentum bars. The stop exits are sent only on bars that also enter the other side, so
      the reversal closes the position first and the exits never act (a close acts only on a position
      the bar's entries leave unchanged); the 8-hour security() ATR / close and the volume-weighted
      supertrend therefore feed nothing (its direction is never set: weird case). MFI as Pine's ta.mfi
      on hlc3. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI / MFI momentum crossings with an EMA slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the MFI 21; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438930_rsi_mfi_momentum_cross_ema5_slope_3h_reversal"
FAMILY = "mfi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 14],
    "pmom": [70, 65],
}
DEFAULT_PARAMS = {"length": 21, "pmom": 70, "nmom": 30, "ema_len": 5}


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


def _mfi(src, vol, n):
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length"])
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = (100 - 100 / (1 + up / dn.where(dn != 0))).where(up != 0, 0.0).where(dn != 0, 100.0)
    rsi = rsi.where(up.notna() & dn.notna())
    mf = _mfi((h + lo + c) / 3, v, n)
    rm = (rsi + mf) / 2
    ech = c.ewm(span=int(p["ema_len"]), adjust=False).mean().diff()
    pm, nm = float(p["pmom"]), float(p["nmom"])
    pos_m = ((rm.shift(1) < pm) & (rm > pm) & (rm > nm) & (ech > 0)).to_numpy()
    neg_m = ((rm < nm) & (ech < 0)).to_numpy()
    prev_neg = np.concatenate(([False], neg_m[:-1]))
    prev_pos = np.concatenate(([False], pos_m[:-1]))
    long_c = pos_m & ~prev_pos
    short_c = neg_m & ~prev_neg
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(long_c, index=ix), false, pd.Series(short_c, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}

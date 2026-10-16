"""Williams %R cross with an SMA 200 filter: %R(14) crossing above -60 with the close above SMA 200
goes long, crossing below -40 with the close below it goes short; a position is closed when the close
reaches a take-profit or stop-loss distance from the entry price.
Port of FMZ strategy #427310 "Williams R Crossover Strategy with Moving Average Filter".

FMZ source id: 427310

Source
    https://www.fmz.com/strategy/427310 (PineScript v5, FMZ last modified 2023-09-19 21:57:46).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 174-209), %R 14, cross 10, TP 30 "pips", SL 20 "pips"
    wr = (highest(high, 14) - close) / (highest - lowest) x -100; ma = sma(close, 200)
    crossover(wr, -60) and close > ma -> entry long; crossunder(wr, -40) and close < ma -> entry short
    close >= avg + 30 / mintick or close <= avg - 20 / mintick -> close long (short mirrors)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the take-profit / stop-loss distances are "pips / syminfo.mintick" (price units
      that depend on the instrument's tick, divided where a multiply was evidently meant). They
      become tp_atr / sl_atr x Wilder ATR(14) of the entry's signal bar.
    * The exits test the CLOSE against the entry price (the fill, next open after the signal):
      close-based exit signals (rule 3), not stops.
    * The %R threshold +-10 is in %R points (dimensionless), kept.
    * strategy.entry reverses: REVERSAL INTENDED; the opposite entry wins over a same-bar close.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-based exits.
    2 generic: ADAPT, price-unit distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427310_williams_r_cross_ma200"
FAMILY = "williams_r_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cross": [10, 20],
    "tp_atr": [1.5, 3.0],
    "sl_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"wr_length": 14, "cross": 10, "ma_length": 200, "tp_atr": 1.5, "sl_atr": 1.0, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n).to_numpy()


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["wr_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wr = (hh - c) / (hh - ll) * -100
    ma = c.rolling(int(p["ma_length"])).mean()
    lvl_l, lvl_s = -50 - p["cross"], -50 + p["cross"]
    long_c = ((wr > lvl_l) & (wr.shift(1) <= lvl_l) & (c > ma)).to_numpy()
    short_c = ((wr < lvl_s) & (wr.shift(1) >= lvl_s) & (c < ma)).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"]))
    o, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, pend, avg, tp, sl = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pend:                              # the entry fills at this bar's open
            avg, pend = o[i], 0
        new = pos
        if long_c[i] and pos != 1:
            new, tp, sl = 1, p["tp_atr"] * atr[i], p["sl_atr"] * atr[i]
        elif short_c[i] and pos != -1:
            new, tp, sl = -1, p["tp_atr"] * atr[i], p["sl_atr"] * atr[i]
        elif pos == 1 and (cv[i] >= avg + tp or cv[i] <= avg - sl):
            new = 0
        elif pos == -1 and (cv[i] <= avg - tp or cv[i] >= avg + sl):
            new = 0
        if new != pos:
            pend = 1 if new != 0 else 0
            pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

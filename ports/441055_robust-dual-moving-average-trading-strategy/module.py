"""RSI and ROC extremes against the SMA 5 above the SMA 200, 1-hour bars: the RSI 14 under 30 with ROC 14 under -0.01 % and the close under the SMA 5 but above the SMA 200 goes long, closed when the
close is back above the SMA 5; the mirror (RSI over 70, ROC over 0.01 %, close above the SMA 5 and the SMA 200) goes short, closed when the close is back under the SMA 5.
Port of FMZ strategy #441055 "Robust Dual Moving Average Trading Strategy" (GMS: RSI & ROC Strategy).

FMZ source id: 441055

Source
    https://www.fmz.com/strategy/441055 (PineScript v4, FMZ last modified 2024-02-05 10:57:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-323), defaults: Both sides, RSI and ROC both, trend filter Above; RSI 14 (70 / 30); ROC 14 (0.01 / -0.01); exit SMA 5 / 5; trend SMA 200
    (the active block for the defaults, lines 287 and 314) rsi < 30 and roc < -0.01 and close < sma5 and close > sma200 -> entry LONG;  close > sma5 -> close LONG
    rsi > 70 and roc > 0.01 and close > sma5 and close > sma200 -> entry SHORT;  close < sma5 -> close SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the block selected by the default inputs runs. Pine's roc is a percentage. A close acts only on
      the held position; the close written after a reversing entry leaves the reversal standing (as
      #438020). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI, ROC and SMA levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND439860 (2 members, best partner #439860, Jaccard 0.724); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441055_rsi_roc_extreme_sma5_revert_above_sma200"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 9],
    "trend_len": [200, 100],
}
DEFAULT_PARAMS = {"rsi_length": 14, "trend_len": 200, "rsi_upper": 70, "rsi_lower": 30, "roc_length": 14,
                  "roc_upper": 0.01, "roc_lower": -0.01, "exit_len": 5}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    k = int(p["roc_length"])
    roc = 100 * (c - c.shift(k)) / c.shift(k)
    sx_ = c.rolling(int(p["exit_len"])).mean()
    st = c.rolling(int(p["trend_len"])).mean()
    el = ((r < float(p["rsi_lower"])) & (roc < float(p["roc_lower"])) & (c < sx_) & (c > st)).to_numpy()
    xl = (c > sx_).to_numpy()
    es = ((r > float(p["rsi_upper"])) & (roc > float(p["roc_upper"])) & (c > sx_) & (c > st)).to_numpy()
    xs = (c < sx_).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if es[i] and new != -1:
            new = -1
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

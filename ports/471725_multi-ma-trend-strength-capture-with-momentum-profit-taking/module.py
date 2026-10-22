"""SMA 5 / 25 crossings on the side of the SMA 75 with an ADX filter, 2-hour bars: the cross up over the SMA 75 with the ADX over 20 goes long, the mirror goes short; any position closes after a one-bar close move of more than 0.6 %; reversing.
Port of FMZ strategy #471725 "Multi MA Trend Strength Capture with Momentum Profit Taking Strategy" (5SMA-25SMA Crossover Strategy with ADX Filter and Sudden Move Profit Taking).

FMZ source id: 471725

Source
    https://www.fmz.com/strategy/471725 (PineScript v5, FMZ last modified 2024-11-12 17:18:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-175), SMA 5 / 25 / 75; ADX 14 from rma of max(change(high), 0) and max(-change(low), 0) (the script's own); sudden move |change(close)| > 0.6 % of close[1]
    crossover(sma5, sma25) and close > sma75 and adx > 20 -> entry Long;  crossunder and close < sma75 and adx > 20 -> entry Short
    long and sudden move -> close Long;  short and sudden move -> close Short;  long and short signal -> close Long;  short and long signal -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DM terms are the script's own (no up-versus-down comparison), as written. The entries are
      called before the closes; a close acts only on a position held into the bar and not being
      reversed (#437773), so the signal-based closes only repeat the reversals. REVERSAL INTENDED. No
      sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with trend and ADX filters, sudden-move exits.
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

NAME = "fmz_471725_sma5_25_cross_sma75_adx_sudden_move_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "move_pct": [0.006, 0.01],
    "adx_th": [20, 25],
}
DEFAULT_PARAMS = {"move_pct": 0.006, "adx_th": 20, "adx_len": 14}


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
    n = int(p["adx_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # ta.tr(true)
    pdm = _rma(h.diff().clip(lower=0), n)
    mdm = _rma((-lo.diff()).clip(lower=0), n)
    trs = _rma(tr, n)
    pdi, mdi = 100 * pdm / trs, 100 * mdm / trs
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), n)
    s5, s25, s75 = c.rolling(5).mean(), c.rolling(25).mean(), c.rolling(75).mean()
    th = float(p["adx_th"])
    lc = ((s5 > s25) & (s5.shift(1) <= s25.shift(1)) & (c > s75) & (adx > th)).to_numpy()
    sc = ((s5 < s25) & (s5.shift(1) >= s25.shift(1)) & (c < s75) & (adx > th)).to_numpy()
    sudden = (c.diff().abs() > pc * float(p["move_pct"])).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if lc[i]:
            cur = 1
        if sc[i]:
            cur = -1
        if pos == 1 and cur == 1 and (sudden[i] or sc[i]):
            cur = 0                              # the close acts only on a long held, not reversed
        if pos == -1 and cur == -1 and (sudden[i] or lc[i]):
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

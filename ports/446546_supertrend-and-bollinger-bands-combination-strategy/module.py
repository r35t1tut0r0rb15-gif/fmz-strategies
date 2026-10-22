"""SuperTrend-line crossings outside the Bollinger bands, 5-minute bars: the close crossing over the SuperTrend up line while under the lower band (20, 2) goes long, crossing under the down line while over
the upper band goes short; the close crossing over the down line closes a long, under the up line closes a short; reversing.
Port of FMZ strategy #446546 "Supertrend and Bollinger Bands Combination Strategy" (ST_BB_Strategy (Supertrend & Bollinger Bands Strategy)).

FMZ source id: 446546

Source
    https://www.fmz.com/strategy/446546 (PineScript v4, FMZ last modified 2024-03-29 15:18:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-148), SuperTrend factor 3, rma(tr, 10) on hl2; BB 20 / 2
    up_trend = close[1] > up_trend[1] ? max(hl2 - 3 atr, up_trend[1]) : hl2 - 3 atr;  dn_trend mirrored (var, na seeds)
    crossover(close, up_trend) and close < lower -> entry Long;  crossunder(close, dn_trend) and close > upper -> entry Short;  crossover(close, dn_trend) -> close Long;  crossunder(close, up_trend) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines start na and a comparison with na is false, so each starts from its raw value, as
      written; trend is computed but never used. Calls run in order: a close acts only on a position
      held into the bar and not reversed by that bar's entry. Pine's stdev is the population deviation.
      REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend-line crossings outside the bands.
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

NAME = "fmz_446546_supertrend_line_cross_outside_bands_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "bb_len": [20, 50],
}
DEFAULT_PARAMS = {"factor": 3.0, "bb_len": 20, "atr_len": 10, "bb_dev": 2.0}


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
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan                               # v4 tr is na on the first bar
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    f = float(p["factor"])
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        us, ds = hl2[i] - f * atr[i], hl2[i] + f * atr[i]
        if i > 0 and cv[i - 1] > up[i - 1]:
            up[i] = np.nan if np.isnan(us) else max(us, up[i - 1])
        else:
            up[i] = us
        if i > 0 and cv[i - 1] < dn[i - 1]:
            dn[i] = np.nan if np.isnan(ds) else min(ds, dn[i - 1])
        else:
            dn[i] = ds
    n = int(p["bb_len"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    lower = (basis - float(p["bb_dev"]) * sd).to_numpy()
    upper = (basis + float(p["bb_dev"]) * sd).to_numpy()
    u1 = np.concatenate(([np.nan], up[:-1]))
    d1 = np.concatenate(([np.nan], dn[:-1]))
    c1 = np.concatenate(([np.nan], cv[:-1]))
    with np.errstate(invalid="ignore"):
        lc = (cv > up) & (c1 <= u1) & (cv < lower)
        sc = (cv < dn) & (c1 >= d1) & (cv > upper)
        xl = (cv > dn) & (c1 <= d1)
        xs = (cv < up) & (c1 >= u1)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and new != 1:
            le[i], new = True, 1
        if sc[i] and new != -1:
            se[i], le[i], new = True, False, -1
        if xl[i] and pos == 1 and new == 1:          # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if xs[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

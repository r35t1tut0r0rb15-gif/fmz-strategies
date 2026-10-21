"""Close crossings of a smoothed SMA-ATR band line with a Stochastic RSI filter, 10-minute bars: the close crossing over the 5-bar SMA of the band line inside the band with the Stochastic RSI under 80 goes
long, crossing under with it over 20 goes short; reversing; the opposite crossings close each side.
Port of FMZ strategy #439082 "Improved SuperTrend Strategy" (IST+StochRSI).

FMZ source id: 439082

Source
    https://www.fmz.com/strategy/439082 (PineScript v5, FMZ last modified 2024-01-17 15:55:15).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 181-232), ATR 14 (rma of rma of tr), multiplier 1.5; filter 5; Stochastic RSI 14, K 3
    band = sma(close, 14) +/- 1.5 x rma(rma(tr, 14), 14);  line = close < upper ? upper : close > lower ? lower : na;  filt = sma(line, 5)
    long = crossover(close, filt) and close > lower and stochRSI < 80;  short = crossunder(close, filt) and close < upper and stochRSI > 20;  crossunder and close > lower -> close Long;  crossover and close < upper -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR is an rma of the rma of the true range, as written. The line is the upper band whenever the
      close is under it (the down test overrides the up test). The closes on an entry bar act on trades
      the reversing entry already closed, so the reversal stands (as #438020). strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band line crossings and Stochastic RSI.
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

NAME = "fmz_439082_sma_atr_band_line_stochrsi"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [1.5, 3.0],
    "filter_len": [5, 10],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "filter_len": 5, "atr_len": 14, "stoch_len": 14, "smooth_k": 3}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["atr_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(_rma(tr, n), n)
    base = c.rolling(n).mean()
    k = float(p["atr_mult"])
    upper, lower = base + k * atr, base - k * atr
    is_up, is_dn = c > lower, c < upper
    line = upper.where(is_dn, lower.where(is_up))
    filt = line.rolling(int(p["filter_len"])).mean()
    r = _rsi(c, int(p["stoch_len"]))
    sl = int(p["stoch_len"])
    rl, rh = r.rolling(sl).min(), r.rolling(sl).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = (100 * (r - rl) / (rh - rl)).rolling(int(p["smooth_k"])).mean()
    xo = (c > filt) & (c.shift(1) <= filt.shift(1))
    xu = (c < filt) & (c.shift(1) >= filt.shift(1))
    lc = (xo & is_up & (st < 80)).to_numpy()
    sc = (xu & is_dn & (st > 20)).to_numpy()
    xl = (xu & is_up).to_numpy()
    xs = (xo & is_dn).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if lc[i] and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif sc[i] and pos != -1 and i + 1 < m:
            se[i], pos = True, -1
        elif pos == 1 and xl[i]:
            lx[i], pos = True, 0
        elif pos == -1 and xs[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

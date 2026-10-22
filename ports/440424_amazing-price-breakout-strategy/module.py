"""Engulfing candles with the SMA 15 and RSI 14, 1-hour bars: a bullish engulfing with the previous close above the SMA 15 and the RSI above 50 goes long, the bearish mirror short; each with a stop 0.75
ATR(14) from the signal close; reversing.
Port of FMZ strategy #440424 "Amazing Price Breakout Strategy" (Custom Strategy).

FMZ source id: 440424

Source
    https://www.fmz.com/strategy/440424 (PineScript v4, FMZ last modified 2024-01-30 15:07:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-139), ATR 14 x 0.75; SMA 15 (SMA 30 unused); RSI 14
    bullishEngulfing and close[1] > sma15 and rsi > 50 -> entry Buy, strategy.exit(stop = close - 0.75 atr);  bearishEngulfing and close[1] < sma15 and rsi < 50 -> entry Sell, strategy.exit(stop = close + 0.75 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent on the signal bar from its close: sl_stop = 0.75 ATR / close of the signal bar,
      shifted one bar inside stops() and re-based on the fill; a new same-direction signal while in the
      trade only moves the script's stop, which the port does not follow. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, engulfing candles, SMA and RSI.
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

NAME = "fmz_440424_engulfing_sma15_rsi_atr_stop"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [0.75, 2.0],
    "ma_len": [15, 30],
}
DEFAULT_PARAMS = {"mult": 0.75, "ma_len": 15, "length": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _setup(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    o1, c1 = o.shift(1), c.shift(1)
    n = int(p["length"])
    ma = c.rolling(int(p["ma_len"])).mean()
    r = _rsi(c, n)
    bull = (c1 < o1) & (c > o) & (c1 < o) & (c > o1)
    bear = (c1 > o1) & (c < o) & (c1 > o) & (c < o1)
    lsig = (bull & (c1 > ma) & (r > 50)).to_numpy()
    ssig = (bear & (c1 < ma) & (r < 50)).to_numpy()
    sl = float(p["mult"]) * _atr(bars_df, n) / c
    return lsig, ssig, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, sl_s = _setup(bars_df, p)
    sl = sl_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_ = True, -1, i + 1, sl[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _setup(bars_df, p)[2].shift(1)}


def portfolio_kwargs(**params):
    return {}

"""Schaff trend cycle turn with an ATR trailing-line and SMA 200 filter, 4-hour bars: the STC turning up while the
line is bullish and the close is above the SMA 200 goes long (mirror short); each trade has a stop at the line
and a 2 ATR target; the line turning against the position closes it.
Port of FMZ strategy #429472 "STC-MA-ATR综合趋势交易策略STC-MA-ATR-Integrated-Trend-Trading-Strategy" (My Strategy).

FMZ source id: 429472

Source
    https://www.fmz.com/strategy/429472 (PineScript v5, FMZ last modified 2023-10-17 14:34:10).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 159-239), STC 12 / 26 / 50 (factor 0.5), ATR line 5 x 3.5, SMA 200, target 2 ATR(5), stop at the line
    stc_sig = 1 when the STC turns up, -1 when it turns down; atr_sig = the UT-style ATR line is not bearish
    long = atr_sig and stc_sig == 1 and close >= sma200 -> entry long + exit(limit = close + 2 atr5, stop = line)
    short = not atr_sig and stc_sig == -1 and close < sma200 -> entry short + exit(limit = close - 2 atr5, stop = line)
    else if the line flips against the side -> close (early stop on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * STC as the source's function (MACD 26 / 50, two stochastic passes over 12 bars, each smoothed with
      factor 0.5, nz seeds). The ATR line as the source (close +/- 3.5 x Wilder ATR 5, ratcheted).
    * The bracket is fixed at entry from the signal bar: stop at the line (distance |close - line| /
      close), target 2 x ATR(5) / close, both shifted one bar inside stops() and re-based on the fill.
      Stated approximation: if the line is on the wrong side of the close at the signal bar, the source's
      stop would trigger at once; the port keeps the distance on the correct side.
    * strategy.entry reverses. Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED. Stops on
      4-hour bars: mark coarse_bar_stop. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ATR multiples and oscillator turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() margins stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429472_stc_atr_line_sma200"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_mult": [2.0, 4.0],
    "atr_mult": [3.5, 2.5],
}
DEFAULT_PARAMS = {"stc_len": 12, "fast": 26, "slow": 50, "atr_period": 5, "atr_mult": 3.5, "ma_len": 200,
                  "tp_mult": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _stc(c, n, fast, slow, factor=0.5):
    macd = (c.ewm(span=fast, adjust=False).mean() - c.ewm(span=slow, adjust=False).mean()).to_numpy()
    lo1 = pd.Series(macd).rolling(n).min().to_numpy()
    rg1 = pd.Series(macd).rolling(n).max().to_numpy() - lo1
    m = len(macd)
    c1, d1 = np.zeros(m), np.zeros(m)
    for i in range(m):
        c1[i] = (macd[i] - lo1[i]) / rg1[i] * 100 if rg1[i] > 0 else (c1[i - 1] if i >= 1 else 0.0)
        d1[i] = c1[i] if i == 0 else d1[i - 1] + factor * (c1[i] - d1[i - 1])
    lo2 = pd.Series(d1).rolling(n).min().to_numpy()
    rg2 = pd.Series(d1).rolling(n).max().to_numpy() - lo2
    c2, e2 = np.zeros(m), np.zeros(m)
    for i in range(m):
        c2[i] = (d1[i] - lo2[i]) / rg2[i] * 100 if rg2[i] > 0 else (c2[i - 1] if i >= 1 else 0.0)
        e2[i] = c2[i] if i == 0 else e2[i - 1] + factor * (c2[i] - e2[i - 1])
    return pd.Series(e2, index=c.index)


def _line(bars_df, n, mult):
    c = bars_df["close"]
    nl = (mult * _atr(bars_df, n)).to_numpy()
    s = c.to_numpy(dtype=float)
    m = len(s)
    ts = np.full(m, np.nan)
    pos = np.zeros(m, dtype=np.int8)
    for i in range(m):
        prev = ts[i - 1] if i >= 1 and not np.isnan(ts[i - 1]) else 0.0
        s1 = s[i - 1] if i >= 1 else np.nan
        if not np.isnan(nl[i]):
            if s[i] > prev and s1 > prev:
                ts[i] = max(prev, s[i] - nl[i])
            elif s[i] < prev and s1 < prev:
                ts[i] = min(prev, s[i] + nl[i])
            else:
                ts[i] = s[i] - nl[i] if s[i] > prev else s[i] + nl[i]
        q = pos[i - 1] if i >= 1 else 0
        if s1 < prev and s[i] > prev:
            q = 1
        elif s1 > prev and s[i] < prev:
            q = -1
        pos[i] = q
    return pd.Series(ts, index=c.index), pos


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    stc = _stc(c, int(p["stc_len"]), int(p["fast"]), int(p["slow"]))
    up = (stc > stc.shift(1)).to_numpy()
    upp = np.concatenate(([False], up[:-1]))
    sig = np.where(up & ~upp, 1, np.where(~up & upp, -1, 0))
    _, pos = _line(bars_df, int(p["atr_period"]), float(p["atr_mult"]))
    atr_ok = pos != -1
    ma_ok = ~(c < c.rolling(int(p["ma_len"])).mean()).to_numpy()
    long_c = atr_ok & (sig == 1) & ma_ok
    short_c = ~atr_ok & (sig == -1) & ~ma_ok
    idx = bars_df.index
    long_e = pd.Series(long_c, index=idx)
    short_e = pd.Series(short_c, index=idx)
    long_x = pd.Series(~long_c & ~atr_ok & ~short_c, index=idx)     # a short entry reverses instead
    short_x = pd.Series(~short_c & atr_ok & ~long_c, index=idx)
    return long_e, long_x, short_e, short_x


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ts, _ = _line(bars_df, int(p["atr_period"]), float(p["atr_mult"]))
    sl = ((c - ts).abs() / c).shift(1)
    tp = (p["tp_mult"] * _atr(bars_df, int(p["atr_period"])) / c).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}

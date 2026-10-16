"""Three-timeframe trend, 1-minute bars: with the 80-minute close above its SMA 50, a 20-minute stochastic neither
overbought nor oversold with K above D, and a 5-minute SMA 7 / 21 up cross, go long (mirror short); a 20-minute K / D
cross against the position closes it.
Port of FMZ strategy #429960 "Multiple Timeframe Trend Strategy" (TUX MTF).

FMZ source id: 429960

Source
    https://www.fmz.com/strategy/429960 (PineScript v2, FMZ last modified 2023-10-23 16:56:52).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 271-321), entry 5 min, medium 20 min, long 80 min; SMA 50; stochastic 18 / 14 / 14 (80 / 20); SMA 7 / 21
    trendDown = security(80, sma(close,50)) > security(80, close); k / d = security(20, sma(stoch 18, 14)) / sma(k, 14)
    bull = not trendDown and 20 < k, d < 80 and k > d and security(5, crossover(sma7, sma21)) -> entry long
    bear = trendDown and ... and k < d and security(5, crossunder(sma7, sma21)) -> entry short
    crossunder(k, d) -> close long; crossover(k, d) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each security() without lookahead is read as the last completed bar of its timeframe: 5-, 20- and
      80-minute bars built inside simulate() from the port's own minutes (epoch-anchored, left-labelled,
      gaps kept), shifted one bar of that timeframe and mapped onto the minutes. The source's value on the
      last minute of a higher bar already includes that bar (one minute earlier): stated approximation.
    * The higher-timeframe K / D are piecewise constant on the minutes, so the K / D cross exits happen on
      the first minute after a higher bar completes, as written.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe values from completed bars.
    2 generic: PASS, stochastic levels and moving-average crosses.
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

NAME = "fmz_429960_three_timeframe_trend"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_minutes": [5, 15],
    "ma_trend": [50, 100],
}
DEFAULT_PARAMS = {"entry_minutes": 5, "ma_trend": 50, "length": 18, "ob": 80, "os": 20, "smooth_k": 14,
                  "smooth_d": 14, "ma_sm": 7, "ma_md": 21}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _htf(bars_df, minutes):
    rule = f"{int(minutes)}min"
    b = bars_df.resample(rule, label="left", closed="left", origin="epoch").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    key = bars_df.index.floor(rule)
    return b, key


def _map(series_htf, key):
    return series_htf.shift(1).reindex(key).to_numpy()       # the last completed higher bar


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    e_min = int(p["entry_minutes"])
    b5, k5 = _htf(bars_df, e_min)
    b20, k20 = _htf(bars_df, e_min * 4)
    b80, k80 = _htf(bars_df, e_min * 16)
    trend_down = pd.Series(_map(b80["close"].rolling(int(p["ma_trend"])).mean() > b80["close"], k80), index=idx)
    trend_down = trend_down.astype(float)
    n = int(p["length"])
    ll, hh = b20["low"].rolling(n).min(), b20["high"].rolling(n).max()
    kk = (100 * (b20["close"] - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    dd = kk.rolling(int(p["smooth_d"])).mean()
    k = pd.Series(_map(kk, k20), index=idx)
    d = pd.Series(_map(dd, k20), index=idx)
    f, s = b5["close"].rolling(int(p["ma_sm"])).mean(), b5["close"].rolling(int(p["ma_md"])).mean()
    up5 = pd.Series(_map(((f > s) & (f.shift(1) <= s.shift(1))).astype(float), k5), index=idx) == 1
    dn5 = pd.Series(_map(((f < s) & (f.shift(1) >= s.shift(1))).astype(float), k5), index=idx) == 1
    mid = ~((k >= p["ob"]) | (d >= p["ob"])) & ~((k <= p["os"]) | (d <= p["os"]))
    bull = (trend_down == 0) & mid & (k > d) & up5
    bear = (trend_down == 1) & mid & (k < d) & dn5
    xl = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    xs = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    bl, br = bull.to_numpy(), bear.to_numpy()
    m = len(idx)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bl[i]:
            pos = 1
        elif br[i]:
            pos = -1
        if pos == 1 and xl[i] and not bl[i]:
            pos = 0
        elif pos == -1 and xs[i] and not br[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = pd.Series((tgt == 1) & (prev != 1), index=idx)
    lx = pd.Series((prev == 1) & (tgt == 0), index=idx)
    se = pd.Series((tgt == -1) & (prev != -1), index=idx)
    sx = pd.Series((prev == -1) & (tgt == 0), index=idx)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}

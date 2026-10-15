"""ATR trend lines and T3, long only: the close above two ATR trailing lines (5 x ATR 5 and 1 x
ATR 1 around hl2) and above a T3 moving average (25, volume factor 0.72) goes long; the long is
closed when hl2 falls below the lower T3 envelope.
Port of FMZ strategy #427067 "ATR and T3 Moving Average Strategy".

FMZ source id: 427067

Source
    https://www.fmz.com/strategy/427067 (PineScript v2, FMZ last modified 2023-09-17 18:30:48).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 151-235), shorts off, T3 25 / 0.72, envelope 5 %,
ATR lines 5 x 5 and 1 x 1
    T3 = c1 e6 + c2 e5 + c3 e4 + c4 e3 (six chained EMA 25 of close)
    TrendUp = close[1] > TrendUp[1] ? max(hl2 - F atr, TrendUp[1]) : hl2 - F atr (TrendDown mirrors)
    Trend = close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : Trend[1]; Tsl = Trend == 1 ? TrendUp : TrendDown
    close > Tsl and close > Tsl1 and close > T3 -> entry long
    hl2 < T3 - 5 % x T3 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 5 % envelope around T3 becomes T3 -/+ `env_atr` x Wilder ATR(14)
      (a percent distance from an average, as worker A ported envelopes). The grid brackets the
      source's width: on 5-minute bars 5 % is tens of ATRs, so the exit is rare as written.
    * Shorts are off by default ("shorts on?" false): long only, as the source runs.
    * Entries only from flat (pyramiding 0); the close exits the long; one signal per bar.
    * Recursive lines start from the first bar where ATR exists; nz(Trend[1], 1) starts at 1.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the 5 % envelope -> ATR multiple; ATR lines already volatility based.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (12 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8). (The T3 "volume factor" is a smoothing constant, not traded volume.)
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427067_atr_t3_long"
FAMILY = "supertrend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "t3_length": [25, 15],
    "factor": [5, 3],
    "env_atr": [10.0, 20.0, 35.0],
}
DEFAULT_PARAMS = {"t3_length": 25, "vfact": 0.72, "factor": 5, "atr_period": 5,
                  "factor1": 1, "atr_period1": 1, "env_atr": 20.0, "env_atr_length": 14}


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
    """Pine atr: rma of the true range (the first bar's true range is na in Pine v3/v4)."""
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _atr_line(bars, factor, n):
    """The classic SuperTrend recursion of the source (lines TrendUp / TrendDown / Trend)."""
    hl2 = ((bars["high"] + bars["low"]) / 2).to_numpy()
    a = _atr(bars, n).to_numpy()
    c = bars["close"].to_numpy(dtype=float)
    up_b, dn_b = hl2 - factor * a, hl2 + factor * a
    m = len(c)
    tu, td, tsl = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    trend = 1
    for i in range(m):
        if np.isnan(a[i]):
            continue
        tu[i] = max(up_b[i], tu[i - 1]) if i and not np.isnan(tu[i - 1]) and c[i - 1] > tu[i - 1] else up_b[i]
        td[i] = min(dn_b[i], td[i - 1]) if i and not np.isnan(td[i - 1]) and c[i - 1] < td[i - 1] else dn_b[i]
        if i and not np.isnan(td[i - 1]) and c[i] > td[i - 1]:
            trend = 1
        elif i and not np.isnan(tu[i - 1]) and c[i] < tu[i - 1]:
            trend = -1
        tsl[i] = tu[i] if trend == 1 else td[i]
    return pd.Series(tsl, index=bars.index)


def _t3(close, n, v):
    e = [close.ewm(span=n, adjust=False).mean()]
    for _ in range(5):
        e.append(e[-1].ewm(span=n, adjust=False).mean())
    c1 = -v ** 3
    c2 = 3 * v * v + 3 * v ** 3
    c3 = -6 * v * v - 3 * v - 3 * v ** 3
    c4 = 1 + 3 * v + v ** 3 + 3 * v * v
    return c1 * e[5] + c2 * e[4] + c3 * e[3] + c4 * e[2]


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    t3 = _t3(c, int(p["t3_length"]), float(p["vfact"]))
    t_dn = t3 - p["env_atr"] * _atr(bars_df, int(p["env_atr_length"]))
    tsl = _atr_line(bars_df, p["factor"], int(p["atr_period"]))
    tsl1 = _atr_line(bars_df, p["factor1"], int(p["atr_period1"]))
    entry = ((c > tsl) & (c > tsl1) & (c > t3)).to_numpy()
    exit_ = (hl2 < t_dn).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}

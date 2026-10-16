"""Bannos, as the script behaves: long only, at most one entry per calendar month: on the bar after
a pivot high (14 / 14) is confirmed, a close above a trend-adaptive moving average (TRAMA 99) goes
long; RSI(14) above 70 closes the long.
Port of FMZ strategy #427260 "Trend Breakout Strategy Based on Adaptive MA and Trendlines".

FMZ source id: 427260

Source
    https://www.fmz.com/strategy/427260 (PineScript v5, FMZ last modified 2023-09-19 15:49:37).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 155-233), TRAMA 99, pivots 14 / 14, slope 1.0, RSI 14
    hh = max(sign(change(highest(99))), 0); ll = max(sign(-change(lowest(99))), 0)
    tc = sma(hh or ll ? 1 : 0, 99)^2; ama = nz(ama[1] + tc (close - ama[1]), close)
    ph = pivothigh(14, 14); upper = 0.; slope_ph = 0.; slope_ph := ph ? 1.0 : slope_ph; upper := ph ? ph : upper - slope_ph
    close > ama and crossover(close, upper) and month(time) != month of the last entry -> entry long
    rsi > 70 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * `upper = 0.` and `slope_ph = 0.` are re-declared on every bar (not `var`), so
      `upper := ph ? ph : upper - slope_ph` reads the fresh 0: upper is the pivot high on a bar
      that confirms one and 0 on every other bar. crossover(close, upper) is therefore true exactly
      on the bar after a confirming bar (close > 0, and the previous close was under the pivot
      high). Ported as it behaves; the descending trendline the author evidently meant (with
      `var`, 1.0 price unit per bar) is not ported (decision owed; its slope would need an ATR
      re-expression, criterion 2).
    * pivothigh(14, 14) is known 14 bars after the pivot bar, at the confirming bar.
    * month(time) is the bar's month in the exchange time zone, UTC for the source's Binance pair:
      the port uses the UTC month of the bar's open time.
    * Long only; entries only from flat; one signal per bar.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots used only once confirmed.
    2 generic: PASS, bar counts only (the 1.0 slope never acts, see above).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: DG427260 (2 members, with #430051, Jaccard 0.940); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the once-a-month rule uses the UTC calendar month).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427260_bannos_trama_trendline_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_trama": [99, 50],
    "pivot": [14, 7],
    "rsi_exit": [70, 80],
}
DEFAULT_PARAMS = {"length_trama": 99, "pivot": 14, "rsi_length": 14, "rsi_exit": 70}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


def _pivot_high(h, k):
    """Pine pivothigh(k, k): at bar t, high[t-k] if it is strictly above the k bars on each side
    (the bars after it up to t); nan otherwise. Known at bar t (no future bar)."""
    m = len(h)
    out = np.full(m, np.nan)
    for t in range(2 * k, m):
        c = h[t - k]
        left, right = h[t - 2 * k:t - k], h[t - k + 1:t + 1]
        if np.all(c > left) and np.all(c > right):
            out[t] = c
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length_trama"])
    c = bars_df["close"]
    hh = np.maximum(np.sign(bars_df["high"].rolling(n).max().diff()), 0)
    ll = np.maximum(np.sign(-bars_df["low"].rolling(n).min().diff()), 0)
    flag = ((hh > 0) | (ll > 0)).astype(float)
    tc = (flag.rolling(n).mean() ** 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ama = np.full(m, np.nan)
    for i in range(m):
        prev = ama[i - 1] if i else np.nan
        val = prev + tc[i] * (cv[i] - prev)
        ama[i] = cv[i] if np.isnan(val) else val           # nz(..., close)
    ph = _pivot_high(bars_df["high"].to_numpy(dtype=float), int(p["pivot"]))
    upper = np.where(np.isnan(ph) | (ph == 0), 0.0, ph)    # re-declared 0 each bar, ph on pivot bars
    u1 = np.concatenate(([np.nan], upper[:-1]))
    c1 = np.concatenate(([np.nan], cv[:-1]))
    cross = (cv > upper) & (c1 <= u1)
    rsi = _rsi(c, int(p["rsi_length"]))
    months = (bars_df.index.year * 100 + bars_df.index.month).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, last_month = 0, None
    for i in range(m):
        cond = cv[i] > ama[i] and cross[i] and last_month != months[i]
        if cond:
            last_month = months[i]          # Pine records the month even when the entry is ignored
        if pos == 1 and rsi[i] > p["rsi_exit"]:
            lx[i], pos = True, 0
        elif pos == 0 and cond:
            le[i], pos = True, 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}

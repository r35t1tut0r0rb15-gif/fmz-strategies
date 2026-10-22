"""QQE threshold-channel exits with a trend-direction filter, 5-minute bars: the first bar of a smoothed RSI 6 run above 60 with the EMA 20 rising (3 bars) and the close above the SMA 50 goes long; the mirror
goes short; a change of the EMA 20's direction closes; reversing.
Port of FMZ strategy #439949 "基于趋势过滤的快速QQE交叉策略Fast-QQE-Crossover-Trading-Strategy-Based-on-Trend-Filter" ([STRATEGY][UL]QQE Cross v1.1).

FMZ source id: 439949

Source
    https://www.fmz.com/strategy/439949 (PineScript v2, FMZ last modified 2024-01-25 11:34:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 236-440), fast EMA 8, medium EMA 20, slow SMA 50; RSI 6, smoothing 3, QQE 2.618, threshold 10; MA filter off, direction filter on; take profit / stop 0, trailing points 100, trailing offset 0
    RSIndex = ema(rsi(close, 6), 3);  QQEclong = consecutive bars with RSIndex > 60;  direction = rising(ema20, 3) ? 1 : falling(ema20, 3) ? -1 : 0
    buy = first bar of QQEclong > 0 and direction > 0 and close > sma50 -> entry Buy;  close Buy when direction != direction[1];  sell mirror;  exit(trail_points = 100, no trail_offset)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The QQE bands (FastAtrRsiTL) only feed plots. rising / falling compare with each of the last 3
      values. The trailing exit has activation points but no trail offset and no other level, so it
      places nothing (take profit and stop inputs are 0). The closes come after the entries: a close of
      a position not held at the bar close does nothing; a held position meeting its close ends flat.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed RSI runs and MA direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point inputs stored.
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

NAME = "fmz_439949_qqe_threshold_direction_filter"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [10, 5],
    "len2": [20, 50],
}
DEFAULT_PARAMS = {"threshold": 10, "len2": 20, "len3": 50, "rsi_len": 6, "sf": 3}


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


def _first_of_runs(flag):
    """1 on the first bar of each run of True (Pine's counter == 1)."""
    prev = np.concatenate(([False], flag[:-1]))
    return flag & ~prev


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ri = _rsi(c, int(p["rsi_len"])).ewm(span=int(p["sf"]), adjust=False).mean()
    th = float(p["threshold"])
    mm = c.ewm(span=int(p["len2"]), adjust=False).mean()
    ms = c.rolling(int(p["len3"])).mean()
    rising = (mm > mm.shift(1)) & (mm > mm.shift(2)) & (mm > mm.shift(3))
    falling = (mm < mm.shift(1)) & (mm < mm.shift(2)) & (mm < mm.shift(3))
    dirn = np.where(rising, 1, np.where(falling, -1, 0))
    cv = c.to_numpy(dtype=float)
    msv = ms.to_numpy()
    with np.errstate(invalid="ignore"):
        bl = (ri > 50 + th).to_numpy() & (dirn > 0) & (cv > msv)
        sl = (ri < 50 - th).to_numpy() & (dirn < 0) & (cv < msv)
    buy, sell = _first_of_runs(bl), _first_of_runs(sl)
    chg = np.concatenate(([False], dirn[1:] != dirn[:-1]))
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and pos != 1:
            new = 1
        if pos == 1 and chg[i] and new == 1:
            new = 0
        if sell[i] and new != -1:
            new = -1
        if pos == -1 and chg[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}

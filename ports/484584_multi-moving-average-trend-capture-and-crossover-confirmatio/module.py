"""EMA ribbon trend entries from flat with EMA exits, 1-minute bars: flat, EMA 14 above EMA 50 / 100 / 200 with EMA 50
above EMA 100 goes long, and the trade closes when EMA 14 falls below EMA 50; flat, the bearish stack with ATR above
its average goes short, closing when EMA 14 rises above EMA 100.
Port of FMZ strategy #484584 "多重均线趋势捕捉与交叉确认交易系统-Multi-Moving-Average-Trend-Capture-and-Crossover-Confirmation-Trading-System" (etude9).

FMZ source id: 484584

Source
    https://www.fmz.com/strategy/484584 (PineScript v6, FMZ last modified 2025-03-03 10:11:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 210-306), EMA 14 / 25 / 50 / 100 / 200, ATR 14
    trending_up = ema14 > ema50, ema100, ema200 and ema50 > ema100;  trending_down = ema14 < all three and ema50 < ema200
    trending_up and not in_position -> entry long;  long and ema14 < ema50 -> close long
    trending_down and not in_position and atr > sma(atr, 14) -> entry short;  short and ema14 > ema100 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's in_position flags gate the entries (only from flat) and track the position. A long close and a short
      entry on one bar is a reversal (the entry is emitted alone). RSI and MACD are computed but unused.
    * FREQ = "1min" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and ATR.
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

NAME = "fmz_484584_ema_ribbon_flat_entries"
FAMILY = "ma_ribbon"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "instant": [14, 10],
    "long_period": [200, 100],
}
DEFAULT_PARAMS = {"instant": 14, "short_period": 50, "medium_period": 100, "long_period": 200, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    i_, s_, m_, l_ = (c.ewm(span=int(p[k]), adjust=False).mean()
                      for k in ("instant", "short_period", "medium_period", "long_period"))
    atr = _atr(bars_df, int(p["atr_len"]))
    up = ((i_ > s_) & (i_ > m_) & (i_ > l_) & (s_ > m_)).to_numpy()
    dn = ((i_ < s_) & (i_ < m_) & (i_ < l_) & (s_ < l_)).to_numpy()
    vol = (atr > atr.rolling(int(p["atr_len"])).mean()).to_numpy()
    out_l, out_s = (i_ < s_).to_numpy(), (i_ > m_).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if up[i] and pos == 0:
            pos = 1
        if pos == 1 and out_l[i]:
            pos = 0
        if dn[i] and pos == 0 and vol[i]:
            pos = -1
        if pos == -1 and out_s[i]:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}

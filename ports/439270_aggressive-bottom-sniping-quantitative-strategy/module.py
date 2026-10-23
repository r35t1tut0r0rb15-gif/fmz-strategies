"""One-minute bars, long only: a bar whose volume is above its 20-bar mean plus 2 standard deviations with an RSI 20 under 30 goes long; the position closes after 10 bars.
Port of FMZ strategy #439270 "Aggressive Bottom Sniping Quantitative Strategy" (Bottom catch strategy (footlz)).

FMZ source id: 439270

Source
    https://www.fmz.com/strategy/439270 (PineScript v4, FMZ last modified 2024-01-18 16:25:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 161-191), volume SMA 20, x 2 standard deviations; RSI 20 under 30; close after 10 bars
    long = volume > sma(volume, 20) + 2 * stdev(volume, 20) and rsi(close, 20) < 30 -> entry Long
    passed_time = bars with a position, counted from the fill bar (1);  passed_time >= 10 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * passed_time is 1 on the fill bar and adds one per bar while the position stays open, so the
      close is sent on the 10th bar of the position and fills at the next open. Pine's stdev is the
      population deviation. An entry while long adds nothing (pyramiding 0). Long only. No sizing code.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; time exit after 10 bars.
    2 generic: PASS, volume spikes into an oversold RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) against its 20-bar mean + 2 standard deviations; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439270_volume_spike_oversold_rsi20_10bar_hold_1m_long_only"
FAMILY = "pullback_time_exit"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [2.0, 1.5],
    "close_time": [10, 30],
}
DEFAULT_PARAMS = {"v_len": 20, "mult": 2.0, "rsi_len": 20, "oversold": 30.0, "close_time": 10}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["v_len"])
    upper = v.rolling(n).mean() + float(p["mult"]) * v.rolling(n).std(ddof=0)
    sig = ((v > upper) & (_rsi(c, int(p["rsi_len"])) < float(p["oversold"]))).to_numpy()
    k = int(p["close_time"])
    m = len(sig)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, fill = 0, False, -1
    for i in range(m):
        if pend:
            pos, pend, fill = 1, False, i
        if pos == 1 and i - fill + 1 >= k:
            lx[i], pos = True, 0
        elif pos == 0 and not pend and sig[i] and i + 1 < m:
            le[i], pend = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

"""RSI 14 extremes against the SMA 5 above the SMA 200, 5-minute bars: above the SMA 200, an RSI under 30 with the close under its SMA 5 goes long and a close above the SMA 5 closes it; an RSI over 70 with the
close above the SMA 5 goes short and a close under the SMA 5 closes it; reversing.
Port of FMZ strategy #439860 "利用RSI指标和均线指标的量化策略RSI-and-Moving-Average-Breakout-Strategy" (GMS: RSI Strategy).

FMZ source id: 439860

Source
    https://www.fmz.com/strategy/439860 (PineScript v4, FMZ last modified 2024-01-24 14:31:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-214), both sides; RSI 14, 70 / 30; exit SMA 5 / 5; trend filter "Above", SMA 200
    long = rsi < 30 and close < sma5 and close > sma200 -> entry LONG;  close LONG when close > sma5
    short = rsi > 70 and close > sma5 and close > sma200 -> entry SHORT;  close SHORT when close < sma5  (the long block runs first)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Above" both sides need the close above the SMA 200, as written. The long block runs first:
      a short entry on a bar whose close also closes the long leaves the bar short (close, then entry),
      and a long entry reversing a short stands although the short's close follows (as #438020); a held
      position meeting its close ends flat. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and SMA sides.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND439860 (2 members, best partner #441055, Jaccard 0.724); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439860_gms_rsi_sma5_exit_sma200_above"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "trend_length": [200, 100],
}
DEFAULT_PARAMS = {"rsi_length": 14, "trend_length": 200, "upper": 70, "lower": 30, "exit_len": 5}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    s5 = c.rolling(int(p["exit_len"])).mean()
    st = c.rolling(int(p["trend_length"])).mean()
    le = ((r < float(p["lower"])) & (c < s5) & (c > st)).to_numpy()
    se = ((r > float(p["upper"])) & (c > s5) & (c > st)).to_numpy()
    xl, xs = (c > s5).to_numpy(), (c < s5).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if le[i] and pos != 1:
            new = 1
        if pos == 1 and xl[i] and new == 1:
            new = 0
        if se[i] and new != -1:
            new = -1
        if pos == -1 and xs[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}

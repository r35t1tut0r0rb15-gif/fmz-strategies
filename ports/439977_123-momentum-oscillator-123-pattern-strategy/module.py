"""123 reversal and Chande-style dynamic momentum combo, 1-minute bars: long when the 123 state (two-bar close pattern with the stochastic 14) and the dynamic-period RSI state are both up, short when both are
down, flat when they disagree; the dynamic period is read on a BTC price scale.
Port of FMZ strategy #439977 "动量张弛指标与123形态策略Momentum-Oscillator-123-Pattern-Strategy" (Combo Backtest 123 Reversal & Dynamic Momentum Index).

FMZ source id: 439977

Source
    https://www.fmz.com/strategy/439977 (PineScript v4, FMZ last modified 2024-01-25 14:27:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-257), 123: 14 / 1 / 3 / 50; DMI: RSI 14 of the period series, zones 30 / 70, limits 30 / 5; reverse off
    DTime = round(14 / sma(stdev(close, 5), 10) - 0.5) clipped to 5 .. 30;  xRSI = rsi(DTime, 14);  DMI pos = xRSI > 30 ? 1 : xRSI < 70 ? -1 : previous
    both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 14 / stdev divides by a price-unit standard deviation; the port divides by stdev /
      close x 42000, the BTC reading near 42000. The RSI is taken of the clipped period series, as
      written (a constant period gives 100), and the zone test reads xRSI > 30 first, so the state is 1
      above 30 and -1 at or under it. The 123 test is read as written. The states are levels;
      disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit volatility period -> BTC-scale reading.
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

NAME = "fmz_439977_reversal123_dynamic_period_rsi_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "scale": [42000.0, 4200.0],
}
DEFAULT_PARAMS = {"length": 14, "scale": 42000.0, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "rsi_len": 14, "buy_zone": 30.0, "sell_zone": 70.0, "up_limit": 30, "lo_limit": 5, "reverse": False}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    sd = c.rolling(5).std(ddof=0).rolling(10).mean() / c * float(p["scale"])
    with np.errstate(divide="ignore", invalid="ignore"):
        dt = np.floor(14.0 / sd)                         # round(14 / x - 0.5)
    dt = dt.where(~(dt > float(p["up_limit"])), float(p["up_limit"]))
    dt = dt.where(~(dt < float(p["lo_limit"])), float(p["lo_limit"]))
    dt = dt.where(np.isfinite(dt))
    xr = _rsi(dt, int(p["rsi_len"])).to_numpy()
    bz, sz = float(p["buy_zone"]), float(p["sell_zone"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pd_ = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if xr[i] > bz:
            pd_ = 1
        elif xr[i] < sz:
            pd_ = -1
        tgt[i] = 1 if (p123 == 1 and pd_ == 1) else (-1 if (p123 == -1 and pd_ == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

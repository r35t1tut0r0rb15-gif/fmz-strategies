"""Kernel-smoothed moving-average ribbon with RSI and trend-strength filters and a 4-bar confirmation, always in, broker
days: when at least 3 of the 4 neighbouring pairs of five kernel MAs (20 / 100 / 150 / 200 / 250) are stacked upward,
RSI 7 is below 40 and the RSI 7 of the first MA is at least 50, for 4 bars in a row, the strategy goes long; mirrored
for shorts; the opposite signal reverses.
Port of FMZ strategy #488517 "基于核平滑多重均线的自适应趋势追踪系统-Adaptive-Trend-Following-System-with-Kernel-Smoothed-Multiple-Moving-Averages" (B4100 - NW Trend Ribbon Strategy).

FMZ source id: 488517

Source
    https://www.fmz.com/strategy/488517 (PineScript v5, FMZ last modified 2025-03-28 15:13:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 179-532), MAs Beta 20 / Gaussian 100 / Epanechnikov 150 / Beta 200 /
Gaussian 250 (alpha = beta = 3, bandwidth 0.3), crossovers required 3, RSI 7 (40 / 60), trend strength RSI 7 of MA1
(0.5 / 0.5), confirmation 4 bars
    kernel MA = sum(src[i] x w[i], i = 0 .. length - 1), w normalised over x = i / (length - 1)
    long count = number of i in 0..3 with ma[i] > ma[i + 1]; longCrossover = count >= 3
    long = longCrossover and rsi < 40 and trendStrength >= 0.5, held 4 bars in a row (counters reset each other)
    entry long / short every confirmed bar; exits: a 2 % / 1 % close-ratchet trail and an ATR(1) x 200 trail

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each kernel is the source's (i = 0 is the current bar); the MA is na until length bars exist.
    * The trail (rule 2, mark trailing_stop_pending): from the close of each bar in a long, once the close is 2 %
      above the average price, close x (1 - 1 %) ratchets up; an ATR(1) x 200 level (far below the price, inert on
      the author's market) competes with it; every confirmed signal bar resets the trail to na (no stop on that bar).
      A level built from bar closes and reset by signals is not expressible in the house trail: not emitted.
      Hard stop and ATR target are off by default (not ported).
    * Entries reverse (REVERSAL INTENDED); the two confirmations cannot hold on one bar.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail pending (mark).
    2 generic: PASS, kernel moving averages and oscillators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the trail quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488517_kernel_ma_ribbon_confirmed"
FAMILY = "ma_ribbon"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cross_req": [3, 4],
    "confirm": [4, 2],
}
DEFAULT_PARAMS = {"cross_req": 3, "confirm": 4, "rsi_len": 7, "rsi_ob": 60, "rsi_os": 40, "ts_len": 7,
                  "ts_min": 0.5, "ts_max": 0.5, "alpha": 3.0, "beta": 3.0, "bandwidth": 0.3}
MAS = (("Beta", 20), ("Gaussian", 100), ("Epanechnikov", 150), ("Beta", 200), ("Gaussian", 250))  # the source's


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _kernel(kind, n, alpha, beta, bw):
    x = np.arange(n, dtype=float) / (n - 1)
    if kind == "Beta":
        w = x ** (alpha - 1) * (1 - x) ** (beta - 1)
    elif kind == "Gaussian":
        w = np.exp(-0.5 * ((x - 0.5) / bw) ** 2)
    else:
        w = np.maximum(0.0, 1 - ((x - 0.5) / bw) ** 2)
    return w / w.sum()


def _kernel_ma(src, w):
    """sum(src[i] x w[i]) with i bars back (i = 0 the current bar); na until len(w) values exist."""
    v = src.to_numpy(dtype=float)
    out = np.convolve(v, w, mode="full")[:len(v)]
    out[:len(w) - 1] = np.nan
    return pd.Series(out, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mas = [_kernel_ma(c, _kernel(k, int(n), p["alpha"], p["beta"], p["bandwidth"])).to_numpy()
           for k, n in MAS]
    up_n = sum((mas[i] > mas[i + 1]).astype(int) for i in range(4))
    dn_n = sum((mas[i] < mas[i + 1]).astype(int) for i in range(4))
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    ts = (_rsi(pd.Series(mas[0], index=c.index), int(p["ts_len"])) / 100).to_numpy()
    cond_l = (up_n >= p["cross_req"]) & (rsi < p["rsi_os"]) & (ts >= p["ts_min"])
    cond_s = (dn_n >= p["cross_req"]) & (rsi > p["rsi_ob"]) & (ts <= p["ts_max"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lc = sc = 0
    for i in range(m):
        if cond_l[i]:
            lc, sc = lc + 1, 0
        else:
            lc = 0
        if cond_s[i]:
            sc, lc = sc + 1, 0
        else:
            sc = 0
        le[i] = lc >= p["confirm"]
        se[i] = sc >= p["confirm"]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}

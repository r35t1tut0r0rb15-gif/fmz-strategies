"""The average vote of 82 moving averages (SMA / EMA 10-200, ALMA, SMMA, LSMA, VWMA, DEMA, Hull, KAMA, FRAMA, VIDYA, JMA, TEMA, ZLEMA, TRIMA and T3 at 10 / 20 / 50 / 100 / 200, each +1 under the close and -1 over it) plus an Ichimoku vote, 1-minute bars: an average of 0.95 or more goes long, -0.75 or less goes short; reversing.
Port of FMZ strategy #429461 "Multi Moving Average Rating Trend Strategy" (Ultra Moving Average Rating Trend Strategy).

FMZ source id: 429461

Source
    https://www.fmz.com/strategy/429461 (PineScript v5, FMZ last modified 2023-10-17 13:11:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 166-1004), MA families at 10 / 20 / 50 / 100 / 200 (SMA / EMA also 30); KAMA 2 / 30; JMA power 2, phase 50; T3 0.7; Ichimoku 9 / 26 / 52; long >= 0.95, short <= -0.75; chart timeframe
    rating = mean over the defined MAs of (ma < close ? 1 : ma > close ? -1 : 0), with the Ichimoku vote (cloud, base and conversion-line pattern) added when defined
    rating >= 0.95 -> entry long;  rating <= -0.75 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each MA is the source's own function: KAMA, VIDYA and JMA start from nz(prev) = 0 and climb from
      zero, as written; FRAMA uses the highest / lowest of N / 2 - 1 bars for its first half and is the
      price for its first N + 1 bars; ZLEMA's lag (len - 1) / 2 is taken as an integer; TRIMA uses
      round((len + 1) / 2) twice. The Pine EMA-family lines are recursive from the first bar (house
      reading). Only defined MAs vote. The rating is requested on the chart's own timeframe. REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average vote thresholds.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the five VWMA votes (10 / 20 / 50 / 100 / 200); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429461_eighty_two_ma_vote_rating_thresholds_reversal"
FAMILY = "ma_rating"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rating_entry": [0.95, 0.8],
    "rating_exit": [0.75, 0.9],
}
DEFAULT_PARAMS = {"rating_entry": 0.95, "rating_exit": 0.75}
LENS = (10, 20, 50, 100, 200)


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


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


def _window(x, n, w):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return _window(x, n, w / w.sum())


def _alma(x, n, offset=0.85, sigma=6.0):
    m, s = offset * (n - 1), n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))
    return _window(x, n, w / w.sum())


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    return _window(x, n, w)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n))))


def _kama(x, n, k1=2, k2=30):
    ch = (x - x.shift(n)).abs()
    vol = x.diff().abs().rolling(n).sum()
    er = (ch / vol).where(vol != 0, 0.0).where(vol.notna())
    fast, slow = 2 / (k1 + 1), 2 / (k2 + 1)
    sc = ((er * (fast - slow) + slow) ** 2).to_numpy()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = 0.0
    for i in range(len(v)):
        out[i] = prev + sc[i] * (v[i] - prev)
        prev = 0.0 if np.isnan(out[i]) else out[i]
    return pd.Series(out, index=x.index)


def _vidya(x, n):
    mom = x.diff()
    up, dn = mom.clip(lower=0).rolling(n).sum(), (-mom).clip(lower=0).rolling(n).sum()
    k = (2 / (n + 1)) * ((up - dn) / (up + dn)).abs()
    kv, v = k.to_numpy(), x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = 0.0
    for i in range(len(v)):
        out[i] = v[i] * kv[i] + prev * (1 - kv[i])
        prev = 0.0 if np.isnan(out[i]) else out[i]
    return pd.Series(out, index=x.index)


def _jma(x, n, power=2.0, phase=50.0):
    pr = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100 + 1.5)
    beta = 0.45 * (n - 1) / (0.45 * (n - 1) + 2)
    alpha = beta ** power
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    ma1 = det0 = det1 = jma = 0.0
    for i in range(len(v)):
        ma1 = (1 - alpha) * v[i] + alpha * ma1
        det0 = (v[i] - ma1) * (1 - beta) + beta * det0
        ma2 = ma1 + pr * det0
        det1 = (ma2 - jma) * (1 - alpha) ** 2 + alpha ** 2 * det1
        jma = jma + det1
        out[i] = jma
        ma1, det0, det1, jma = (0.0 if np.isnan(q) else q for q in (ma1, det0, det1, jma))
    return pd.Series(out, index=x.index)


def _frama(b, n):
    """The source's getFRAMA (N made even; first half over N / 2 - 1 bars, as written)."""
    if n % 2 != 0:
        n += 1
    h, lo, c = b["high"], b["low"], b["close"]
    half = n // 2
    n3 = (h.rolling(n).max() - lo.rolling(n).min()) / n
    n1 = (h.rolling(half - 1).max() - lo.rolling(half - 1).min()) / half
    n2 = (h.shift(half).rolling(half).max() - lo.shift(half).rolling(half).min()) / half
    ok = (n1 > 0) & (n2 > 0) & (n3 > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        dim = ((np.log(n1 + n2) - np.log(n3)) / np.log(2)).where(ok, 0.0)
    alpha = np.clip(np.exp(-4.6 * (dim - 1)), 0.01, 1.0).to_numpy()
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        f = alpha[i] * v[i] + (1 - alpha[i]) * (1.0 if np.isnan(prev) else prev)
        if i < n + 1:
            f = v[i]
        out[i] = f
        prev = f
    return pd.Series(out, index=c.index)


def _t3(x, n, vf=0.7):
    e1 = _ema(x, n)
    e2 = _ema(e1, n)
    e3 = _ema(e2, n)
    e4 = _ema(e3, n)
    e5 = _ema(e4, n)
    e6 = _ema(e5, n)
    c1 = -vf ** 3
    c2 = 3 * vf ** 2 + 3 * vf ** 3
    c3 = -6 * vf ** 2 - 3 * vf - 3 * vf ** 3
    c4 = 1 + 3 * vf + vf ** 3 + 3 * vf ** 2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


def _rating(bars_df):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    mas = []
    for n in (10, 20, 30, 50, 100, 200):
        mas += [c.rolling(n).mean(), _ema(c, n)]
    for n in LENS:
        e = _ema(c, n)
        nm = int(np.floor((n + 1) / 2 + 0.5))
        lag = (n - 1) // 2
        mas += [_alma(c, n), _rma(c, n), _linreg(c, n), (c * v).rolling(n).sum() / v.rolling(n).sum(),
                2 * e - _ema(e, n), _hma(c, n), _kama(c, n), _frama(bars_df, n), _vidya(c, n), _jma(c, n),
                3 * (e - _ema(e, n)) + _ema(_ema(e, n), n), _ema(2 * c - c.shift(lag), n),
                c.rolling(nm).mean().rolling(nm).mean(), _t3(c, n)]
    cv = c.to_numpy(dtype=float)
    votes = []
    for ma in mas:
        a = ma.to_numpy(dtype=float)
        votes.append(np.where(np.isnan(a), np.nan, np.where(a == cv, 0.0, np.where(a < cv, 1.0, -1.0))))
    don = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2
    conv, base = don(9), don(26)
    l1, l2 = (conv + base) / 2, don(52)
    c1 = c.shift(1)
    buy = (l1 > l2) & (c > l1) & (c < base) & (c1 < conv) & (c > conv)
    sell = (l2 > l1) & (c < l2) & (c > base) & (c1 > conv) & (c < conv)
    defined = (l1.notna() & l2.notna() & c1.notna() & base.notna() & conv.notna()).to_numpy()
    votes.append(np.where(defined, np.where(buy, 1.0, np.where(sell, -1.0, 0.0)), np.nan))
    vm = np.vstack(votes)
    cnt = (~np.isnan(vm)).sum(axis=0)
    tot = np.nansum(vm, axis=0)
    return pd.Series(np.where(cnt > 0, tot / np.maximum(cnt, 1), np.nan), index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rating(bars_df)
    le = r >= float(p["rating_entry"])
    se = r <= -float(p["rating_exit"])
    false = pd.Series(False, index=bars_df.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}

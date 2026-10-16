"""drnkk fusion, broker days: long when the vortex indicator's smoothed rate of change favours VI+, a
fast RSI(2) (Fisher-squashed) is above its 80 line and the 2-bar price change is positive enough;
short on the mirror.
Port of FMZ strategy #428071 "Multivariate Indicator Fusion Strategy" (drnkk Strategy).

FMZ source id: 428071

Source
    https://www.fmz.com/strategy/428071 (PineScript v3, FMZ last modified 2023-09-28 12:01:57).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 146-206), VI 4 / 3, ROC-RSI 2 / 2
    VIP = sum(|high - low[1]|, 4) / sum(atr(1), 4); VIM = sum(|low - high[1]|, 4) / same
    wmaVI = wma(VI - 1, 3) x 10; roc = (wmaVI - wmaVI[3]) / 3; VI_long = roc_VIP > roc_VIM
    IF(x) = tanh(x); RSI_long = tanh(wma(0.1 (rsi(close, 2) - 50), 2)) x 100 > 80
    ROC_long = tanh(wma((close - close[2]) / 2, 2)) x 100 > 75   <- in PRICE units
    all three long -> entry long; all three short -> entry short (year >= 2018)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the ROC leg is a price-unit change (tanh > 0.75 means a 2-bar move above about
      0.97 price units: on BTC almost a sign test, on FX never). Ported as the same smoothed change
      in ATR(14) units against `roc_k` (default 0.001, about 0.97 USD on daily BTC); judgement
      before any backtest.
    * The year >= 2018 filter is a backtest window: dropped. strategy.entry reverses:
      REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit ROC -> ATR units.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428071_vortex_rsi_roc_fusion"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vi_pm": [4, 7],
    "roc_k": [0.001, 0.1],
}
DEFAULT_PARAMS = {"vi_pm": 4, "vi_ps": 3, "rsi_pm": 2, "rsi_ps": 2, "roc_k": 0.001, "atr_length": 14}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


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
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # atr(1) = tr
    n = int(p["vi_pm"])
    s_tr = tr.rolling(n).sum()
    vip = (h - lo.shift(1)).abs().rolling(n).sum() / s_tr
    vim = (lo - h.shift(1)).abs().rolling(n).sum() / s_tr
    ps = int(p["vi_ps"])
    wp, wm = _wma(vip - 1, ps) * 10, _wma(vim - 1, ps) * 10
    roc_p, roc_m = (wp - wp.shift(ps)) / ps, (wm - wm.shift(ps)) / ps
    k = int(p["rsi_pm"])
    d = c.diff()
    ru, rd = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + ru / rd)).where(ru != 0, 0.0).where(rd != 0, 100.0).where(ru.notna() & rd.notna())
    m2 = int(p["rsi_ps"])
    if_rsi = np.tanh(_wma(0.1 * (rsi - 50), m2)) * 100
    atr = _rma(tr, int(p["atr_length"]))
    roc_atr = _wma((c - c.shift(k)) / k, m2) / atr
    long_s = ((roc_p > roc_m) & (if_rsi > 80) & (roc_atr > p["roc_k"])).to_numpy()
    short_s = ((roc_m > roc_p) & (if_rsi < -80) & (roc_atr < -p["roc_k"])).to_numpy()
    m = len(long_s)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_s[i]:
            pos = 1
        elif short_s[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

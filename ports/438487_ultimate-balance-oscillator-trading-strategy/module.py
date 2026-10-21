"""Weighted blend of normalised ROC, RSI, CCI, Williams %R and ADX, broker days, long only: the blend crossing over 0.75 buys, crossing under 0.25 closes.
Port of FMZ strategy #438487 "Ultimate Balance Oscillator Trading Strategy" (Ultimate Balance Oscillator Strategy).

FMZ source id: 438487

Source
    https://www.fmz.com/strategy/438487 (PineScript v5, FMZ last modified 2024-01-12 14:08:33).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 194-295), weights ROC 2, RSI 0.5, CCI 2, %R 0.5, ADX 0.5; ROC 20, RSI 14, CCI 20 on daily hlc3, %R 14, ADX 14 / DI 14; levels 0.75 / 0.25
    ROC = change(close, 20) normalised over its 20-bar range;  RSI / 100;  CCI(hlc3, 20) over its 20-bar range;  %R(14) over its 14-bar range;  ADX / 50
    osc = weighted mean;  crossover(osc, 0.75) -> entry Buy;  crossunder(osc, 0.25) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("D", ...) on a daily chart returns the chart's own bars, so the CCI source is the bar's
      hlc3. The DI lines hold their last value when undefined (fixnan). Long only. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, normalised oscillators and ADX.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438487_ultimate_balance_oscillator_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ob_level": [0.75, 0.65],
    "os_level": [0.25, 0.35],
}
DEFAULT_PARAMS = {"ob_level": 0.75, "os_level": 0.25, "w_roc": 2.0, "w_rsi": 0.5, "w_cci": 2.0, "w_wr": 0.5,
                  "w_adx": 0.5, "roc_len": 20, "rsi_len": 14, "cci_len": 20, "wr_len": 14, "adx_len": 14,
                  "di_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _adx(h, lo, c, di_len, adx_len):
    up = h.diff()
    down = -lo.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index).where(down.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, di_len)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = _fixnan(100 * _rma(plus_dm, di_len) / trr)
        minus = _fixnan(100 * _rma(minus_dm, di_len) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def _norm(x, n):
    lo_, hi_ = x.rolling(n).min(), x.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        return (x - lo_) / (hi_ - lo_)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + c) / 3
    rl, cl, wl = int(p["roc_len"]), int(p["cci_len"]), int(p["wr_len"])
    roc = c - c.shift(rl)
    rsi = _rsi(c, int(p["rsi_len"]))
    dev = src.rolling(cl).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (src - src.rolling(cl).mean()) / (0.015 * dev)
        hh, ll = h.rolling(wl).max(), lo.rolling(wl).min()
        wr = -100 * (hh - c) / (hh - ll)
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    w = [float(p[k]) for k in ("w_roc", "w_rsi", "w_cci", "w_wr", "w_adx")]
    osc = (_norm(roc, rl) * w[0] + rsi / 100 * w[1] + _norm(cci, cl) * w[2] + _norm(wr, wl) * w[3]
           + adx / 50 * w[4]) / sum(w)
    ob, os_ = float(p["ob_level"]), float(p["os_level"])
    le = (osc > ob) & (osc.shift(1) <= ob)
    lx = (osc < os_) & (osc.shift(1) >= os_)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}

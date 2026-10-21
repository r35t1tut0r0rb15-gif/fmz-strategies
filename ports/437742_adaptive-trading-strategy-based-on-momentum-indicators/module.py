"""Squeeze-on DI crossings with squeeze momentum, broker days: inside a squeeze (the 1.5-sigma Bollinger band within the 1.5-ATR Keltner channel) a DI+ crossing over DI- with the squeeze momentum crossing over
zero goes long, the mirror goes short (reversing); the squeeze firing (bands outside the channel) closes either side.
Port of FMZ strategy #437742 "Adaptive Trading Strategy Based on Momentum Indicators" (DMI/ADX/SQZ).

FMZ source id: 437742

Source
    https://www.fmz.com/strategy/437742 (PineScript v4, FMZ last modified 2024-01-05 11:43:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 141-190), BB 20 (dev uses the KC factor 1.5, as coded), KC 20 x 1.5 with true range, DI 14
    sqzOn = lowerBB > lowerKC and upperBB < upperKC;  sqzOff = lowerBB < lowerKC and upperBB > upperKC;  val = linreg(close - avg(avg(highest 20, lowest 20), sma 20), 20, 0)
    entry Buy when sqzOn and crossover(DI+, DI-) and crossover(val, 0);  entry Sell mirror;  close Buy / Sell when sqzOff

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Bollinger deviation uses multKC (1.5) instead of the BB factor input (2), as coded. The DI lines
      carry their last value where the true range is zero (fixnan); the ADX value is computed but unused.
      Closes act on the position open at the bar's close (entries come first). REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility channels, DI and a regression momentum.
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

NAME = "fmz_437742_squeeze_di_momentum"
FAMILY = "volatility_regime"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "mult_kc": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult_kc": 1.5, "di_len": 14}


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


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _linreg0(x, n):
    sx = n * (n - 1) / 2
    sxx = (n - 1) * n * (2 * n - 1) / 6
    sxy = sum((n - 1 - k) * x.shift(k) for k in range(n))
    sy = x.rolling(n).sum()
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return (sy - slope * sx) / n + slope * (n - 1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["length"]), float(p["mult_kc"])
    basis = c.rolling(n).mean()
    dev = k * c.rolling(n).std(ddof=0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    rng = tr.rolling(n).mean()
    ukc, lkc = basis + rng * k, basis - rng * k
    sqz_on = ((basis - dev) > lkc) & ((basis + dev) < ukc)
    sqz_off = ((basis - dev) < lkc) & ((basis + dev) > ukc)
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + basis) / 2
    val = _linreg0(c - mid, n)
    up, down = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=c.index)
    mdm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=c.index)
    dl = int(p["di_len"])
    trr = _rma(tr, dl)
    with np.errstate(divide="ignore", invalid="ignore"):
        dip = _fixnan(100 * _rma(pdm, dl) / trr)
        dim = _fixnan(100 * _rma(mdm, dl) / trr)
    xo = (dip > dim) & (dip.shift(1) <= dim.shift(1))
    xu = (dip < dim) & (dip.shift(1) >= dim.shift(1))
    lc = (sqz_on & xo & (val > 0) & (val.shift(1) <= 0)).to_numpy()
    sc = (sqz_on & xu & (val < 0) & (val.shift(1) >= 0)).to_numpy()
    off = sqz_off.to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s, changed = pos, False
        if lc[i] and s != 1:
            s, changed = 1, True
        if sc[i] and s != -1:
            s, changed = -1, True
        if off[i] and pos != 0 and not changed:
            s = 0
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        elif s == 0 and pos == 1:
            lx[i] = True
        elif s == 0 and pos == -1:
            sx[i] = True
        pos = s
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}

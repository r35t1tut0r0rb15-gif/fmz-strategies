"""SuperTrend (ATR 10 x 3) direction with a KAMA 21, broker days, long only: an up-trend with the close above the KAMA buys; a down-trend with the close below the KAMA closes.
Port of FMZ strategy #476273 "Adaptive Trend Following Dynamic Trend Recognition Trading Strategy" (Supertrend + KAMA Long Strategy).

FMZ source id: 476273

Source
    https://www.fmz.com/strategy/476273 (PineScript v6, FMZ last modified 2024-12-27 15:41:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-147), KAMA 21 (fast 0.666, slow 0.0645); SuperTrend ATR 10 x 3; commission 0.1 %, slippage 3; date range always true
    kama := nz(kama[1]) + (er (0.666 - 0.0645) + 0.0645)^2 (close - nz(kama[1]));  [st, dir] = supertrend(3, 10);  dir < 0 and close > kama -> entry Long;  dir >= 0 and close < kama -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The KAMA is ported as written: it starts from 0 (nz of na) on the first bar and converges from
      there; the efficiency ratio is 0 while the 21-bar noise is na (Pine: na != 0 is false) or 0. The SuperTrend is Pine's
      reference ta.supertrend (direction -1 = up-trend). The entry repeats while the condition holds and
      is ignored while long. Long only. The commission and slippage settings are costs and are not ported
      (house cost model). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend direction with a KAMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: commission / slippage not ported; no sizing code.
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

NAME = "fmz_476273_supertrend10x3_kama21_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kama_length": [21, 10],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"kama_length": 21, "factor": 3.0, "atr_period": 10}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def _kama(c, n):
    """The script's KAMA: seeded from nz(na) = 0 on the first bar; the ratio is 0 until 21 diffs exist."""
    noise = c.diff().abs().rolling(n).sum()
    sig = (c - c.shift(n)).abs()
    ok = noise.notna() & (noise != 0)                 # Pine: na != 0 is false, so the ratio is 0
    er = (sig / noise.where(ok)).where(ok, 0.0)
    sm = (er * (0.666 - 0.0645) + 0.0645) ** 2
    cv, sv = c.to_numpy(dtype=float), sm.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        base = 0.0 if np.isnan(prev) else prev
        out[i] = base + sv[i] * (cv[i] - base)
        prev = out[i]
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    kama = _kama(c, int(p["kama_length"]))
    d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[1]
    le = (d < 0) & (c > kama)
    lx = (d >= 0) & (c < kama)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}

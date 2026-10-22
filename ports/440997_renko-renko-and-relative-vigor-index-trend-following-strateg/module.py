"""ATR renko bricks with an RVI exit, broker days, long only: a new up brick (the close at least one brick above the upper renko line) goes long; the 9-bar Relative Vigor Index crossing under its
signal line closes.
Port of FMZ strategy #440997 "基于Renko和相对活力指数的趋势跟踪策略Renko-and-Relative-Vigor-Index-Trend-Following-Strategy" (Lancelot RR Strategy).

FMZ source id: 440997

Source
    https://www.fmz.com/strategy/440997 (PineScript v3, FMZ last modified 2024-02-04 15:49:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-230), RVI length 9 (fixed); renko on TF "D" (the chart's own daily bars), ATR 9; SMA 5 and SMA 20 unused
    RVI = sum(swma(close - open), 9) / sum(swma(high - low), 9), RVIsig = swma(RVI);  renko lines RENKOUP / RENKODN from (high + low) / 2 +- ATR / 2, brick H = RENKOUP[1] - RENKODN[1]
    close >= RENKOUP[1] + 3H / 2H / H -> up brick (lines moved by 3 / 2 / 1 ATR);  close <= RENKODN[1] - 3H / 2H / H -> down brick;  UP -> entry Long;  crossunder(RVI, RVIsig) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security calls ask for "D" on a daily chart, the chart's own bars. The renko recursion is ported
      as written, including the line moves (an up move of k bricks sets RENKODN to the previous RENKOUP
      plus k - 1 ATR). Pine's atr is the RMA of the true range. A close acts only on a held long; an up
      brick while long does nothing. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, renko bricks and RVI crossings.
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

NAME = "fmz_440997_atr_renko_up_brick_rvi_exit_long"
FAMILY = "renko_bricks"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [9, 18],
    "rvi_len": [9, 14],
}
DEFAULT_PARAMS = {"atr_len": 9, "rvi_len": 9}


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


def _swma(x):
    return (x + 2 * x.shift(1) + 2 * x.shift(2) + x.shift(3)) / 6


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["rvi_len"])
    num = _swma(c - o).rolling(k).sum()
    den = _swma(h - lo).rolling(k).sum()
    rvi = (num / den.where(den != 0)).where(den != 0, 0.0).where(den.notna())
    sig = _swma(rvi)
    xl = ((rvi < sig) & (rvi.shift(1) >= sig.shift(1))).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    mid = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up = np.zeros(m, dtype=bool)
    ru = rd = np.nan
    for i in range(m):
        pru, prd = ru, rd
        if np.isnan(pru):
            ru, rd = mid[i] + atr[i] / 2, mid[i] - atr[i] / 2
        hh = (ru - rd) if (np.isnan(pru) or np.isnan(prd)) else (pru - prd)
        a = atr[i]
        if cv[i] >= pru + hh * 3:
            ru, rd, up[i] = pru + a * 3, pru + a * 2, True
        elif cv[i] >= pru + hh * 2:
            ru, rd, up[i] = pru + a * 2, pru + a, True
        elif cv[i] >= pru + hh:
            ru, rd, up[i] = pru + a, pru, True
        elif cv[i] <= prd - hh * 3:
            rd, ru = prd - a * 3, prd - a * 2
        elif cv[i] <= prd - hh * 2:
            rd, ru = prd - a * 2, prd - a
        elif cv[i] <= prd - hh:
            rd, ru = prd - a, prd
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xl[i]:
            lx[i], pos = True, 0
        elif pos == 0 and up[i] and i + 1 < m:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

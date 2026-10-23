"""Broker days, long only: the ATR 10 above its EMA 5, the ease of movement (SMA 10) above zero and the average of the vortex lines (10) above 1 goes long; all three on the other side closes it.
Port of FMZ strategy #442011 "基于ATREOM和VORTEX的长线趋势策略ATR-EOM-and-VORTEX-Based-Long-Trend-Strategy" (atr+eom+vortex strat (SoftKill21)).

FMZ source id: 442011

Source
    https://www.fmz.com/strategy/442011 (PineScript v4, FMZ last modified 2024-02-18 16:01:07).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 142-178), ATR 10, EMA 5; EOM 10 (divisor 10); vortex 10; shorts commented out
    eom = sma(10 * change(hl2) * (high - low) / volume, 10);  avg_vortex = (sum(|high - low[1]|, 10) + sum(|low - high[1]|, 10)) / sum(atr(1), 10) / 2
    long = atr > ema(atr, 5) and eom > 0 and avg_vortex > 1 -> entry long;  short = atr < ema_atr and eom < 0 and avg_vortex < 1 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the sign of the ease of movement is used, so its divisor does not matter; the volume weights
      each bar's move. atr(1) is the true range. The short entry is commented out. Long only. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility expansion with ease-of-movement and vortex agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the divisor of each bar's ease of movement; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442011_atr_expansion_eom_vortex_long_only"
FAMILY = "volatility_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 20],
    "vortex_len": [10, 20],
}
DEFAULT_PARAMS = {"atr_len": 10, "ema_atr": 5, "eom_len": 10, "vortex_len": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["atr_len"]))
    ema_atr = atr.ewm(span=int(p["ema_atr"]), adjust=False).mean()
    hl2 = (h + lo) / 2
    eom = (10 * hl2.diff() * (h - lo) / v.where(v != 0)).rolling(int(p["eom_len"])).mean()
    n = int(p["vortex_len"])
    vmp = (h - lo.shift(1)).abs().rolling(n).sum()
    vmm = (lo - h.shift(1)).abs().rolling(n).sum()
    s = tr.rolling(n).sum()
    avg_v = (vmp / s + vmm / s) / 2
    lg = ((atr > ema_atr) & (eom > 0) & (avg_v > 1)).to_numpy()
    sh = ((atr < ema_atr) & (eom < 0) & (avg_v < 1)).to_numpy()
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sh[i]:
            lx[i], pos = True, 0
        elif pos == 0 and lg[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

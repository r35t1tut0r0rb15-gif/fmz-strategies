"""A SuperTrend on hlc3 whose multiplier widens with the Vegas channel (SMA 100 +- 1 sd), daily bars: long while the trend is up, short while it is down; reversing at every trend change.
Port of FMZ strategy #449711 "Vegas SuperTrend Enhanced Strategy" (Vegas SuperTrend Enhanced - strategy [presentTrading]).

FMZ source id: 449711

Source
    https://www.fmz.com/strategy/449711 (PineScript v5, FMZ last modified 2024-04-28 13:43:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-190), ATR 10; Vegas window 100; multiplier 5 + 5 x channel width / SMA; direction Both; cash 10000, commission 0.1 %, slippage 1
    mult = 5 + 5 x (2 sd100 / sma100);  up = hlc3 - mult atr;  dn = hlc3 + mult atr;  trend = close > prevDn ? 1 : close < prevUp ? -1 : trend[1];  up / dn ratchet by trend
    trend == 1 -> entry Long;  trend == -1 -> entry Short;  trend changes -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's lines are named the other way round (superTrendUpper sits under the price) and
      start from nz() seeds; marketTrend starts at 1, so the strategy is long from the first bar until
      the first down trend. The close_all on a trend change comes after that bar's reversing entry and
      leaves the reversal (house call-order rule). The entries are levels, ignored while already on
      that side. REVERSAL INTENDED. The cash size is sizing; commission and slippage are costs (not
      ported). FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility-adjusted SuperTrend direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size stored; the commission and slippage are costs, not ported.
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

NAME = "fmz_449711_vegas_adjusted_supertrend_state_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "base_mult": [5.0, 3.0],
    "vol_adj": [5.0, 2.0],
}
DEFAULT_PARAMS = {"base_mult": 5.0, "vol_adj": 5.0, "atr_period": 10, "vegas": 100}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    w = int(p["vegas"])
    sma, sd = c.rolling(w).mean(), c.rolling(w).std(ddof=0)
    mult = (float(p["base_mult"]) + float(p["vol_adj"]) * (2 * sd / sma)).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_period"])).to_numpy()
    src = ((h + lo + c) / 3).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    trend = np.ones(m)
    prev_up = prev_dn = np.nan
    t = 1.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            up = src[i] - mult[i] * atr[i]
            dn = src[i] + mult[i] * atr[i]
            pu = up if np.isnan(prev_up) else prev_up      # nz(prev[1], current)
            pd_ = dn if np.isnan(prev_dn) else prev_dn
            if cv[i] > pd_:
                t = 1.0
            elif cv[i] < pu:
                t = -1.0
            trend[i] = t
            if t == 1:
                up = np.nan if (np.isnan(up) or np.isnan(pu)) else max(up, pu)
            if t == -1:
                dn = np.nan if (np.isnan(dn) or np.isnan(pd_)) else min(dn, pd_)
            prev_up, prev_dn = up, dn
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(trend == 1, index=ix), false, pd.Series(trend == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}

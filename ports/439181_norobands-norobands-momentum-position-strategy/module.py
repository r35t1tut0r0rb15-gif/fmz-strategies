"""Noro's Bands v1.5, broker days: in an uptrend of the 20-bar close channel (close above the upper distance band), a red bar or a close under the upper band with a lower body low goes long; so do a large red
"crypto bottom" bar and a fast RSI under 5; in a downtrend the mirror goes short; reversing.
Port of FMZ strategy #439181 "动量位置型NoroBands波段策略NoroBands-Momentum-Position-Strategy" (NoroBands str 1.5).

FMZ source id: 439181

Source
    https://www.fmz.com/strategy/439181 (PineScript v2, FMZ last modified 2024-01-18 10:58:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-196), period 20; colour bar, CryptoBottom, RSI, min/max and pyramiding on; long and short on
    center = (highest(close, 20) + lowest(close, 20)) / 2;  hd / ld = center +/- sma(|close - center|, 20);  trend = -1 if close < ld and high < hd, 1 if close > hd and low > ld, else trend[1]
    up = trend 1 and (red bar or close < hd) and min(open, close) < its previous value;  up2 = CryptoBottom (red, |close - sma 10| > 3 x its 100-bar mean, lower body low, fast RSI(2) < 10);  up3 = fast RSI < 5
    dn = trend -1 and (green bar or close > ld) and max(open, close) > its previous value;  up4 / dn4 and the average-price clauses only add (pyramiding)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() default pyramiding allows one entry per direction, so the average-price clauses and
      up4 / dn4 only matter for adds, which are blocked: the port takes each setup when not already on
      that side. On a flat bar with both setups the short entry comes last and stands (as #437773). The
      fast RSI uses rma(2) of the gains and losses. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel distance bands, bar colours, a fast RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; pyramiding clauses stored.
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

NAME = "fmz_439181_noro_bands_v15"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [20, 40],
    "use_cb": [True, False],
}
DEFAULT_PARAMS = {"len": 20, "use_cb": True, "use_rsi": True}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["len"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    ds = (c - center).abs().rolling(n).mean()
    hd, ld = center + ds, center - ds
    t_dn = ((c < ld) & (h < hd)).to_numpy()
    t_up = ((c > hd) & (lo > ld)).to_numpy()
    m = len(c)
    trend = np.full(m, np.nan)
    for i in range(m):
        prev = trend[i - 1] if i > 0 else np.nan
        trend[i] = -1.0 if t_dn[i] else (1.0 if t_up[i] else prev)
    d = c.diff()
    fu, fd = _rma(d.clip(lower=0), 2), _rma((-d).clip(lower=0), 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        frsi = 100.0 - 100.0 / (1.0 + fu / fd)
    frsi = frsi.where(fu != 0, 0.0).where(fd != 0, 100.0)
    frsi = frsi.where(fd.notna() & (fu.notna() | (fd == 0))).to_numpy()
    mn, mx = np.minimum(o, c), np.maximum(o, c)
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    up = (trend == 1) & (red | (c < hd).to_numpy()) & (mn < mn.shift(1)).to_numpy()
    dn = (trend == -1) & (green | (c > ld).to_numpy()) & (mx > mx.shift(1)).to_numpy()
    dist = (c - c.rolling(10).mean()).abs()
    up2 = (red & (dist > dist.rolling(100).mean() * 3).to_numpy() & (mn < mn.shift(1)).to_numpy()
           & (frsi < 10) & bool(p["use_cb"]))
    up3 = (frsi < 5) & bool(p["use_rsi"])
    long_c = up | up2 | up3
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if i + 1 >= m:
            break
        if dn[i] and pos != -1:
            se[i], pos = True, -1                        # the short entry comes last and stands
        elif long_c[i] and pos != 1:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}

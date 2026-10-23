"""Broker days, long only: ADX 14 above 30 with the Trend Thrust Indicator (volume-weighted MAs 13 / 26) above its 9-bar signal and the Volume Price Confirmation Indicator (5 / 25) above 0 goes long; the long closes when the VPCI falls below 0.
Port of FMZ strategy #458248 "Multi Indicator Trend Following with Volume Confirmation Strategy" (TASC 2024.08 Volume Confirmation For A Trend System (VCTS)).

FMZ source id: 458248

Source
    https://www.fmz.com/strategy/458248 (PineScript v5, FMZ last modified 2024-07-31 11:43:53).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 246-326), ADX 14 / 14; TTI 13 / 26 / 9; VPCI 5 / 25; ADX > 30
    ADX > 30 and TTI > signal and VPCI > 0 -> entry long;  VPCI < 0 -> close_all
    TTI = vwma13 x (vwma13 / vwma26)^2 - vwma26 / (vwma13 / vwma26)^2;  VPCI = (vwma25 - sma25) x (vwma5 / sma5) x (sma(volume, 5) / sma(volume, 25))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is the script's own: DI from Wilder RMAs of the directional moves over ta.atr (fixnan),
      then 100 x RMA of |DI+ - DI-| / (DI+ + DI-). vwma(x, n) = sma(x x volume, n) / sma(volume, n). An
      entry while long adds nothing; the entry needs VPCI > 0 and the close VPCI < 0, so they never meet.
      Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX trend filter with volume-weighted thrust and price-volume confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) in the VWMAs and the VPCI volume ratio; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458248_tasc_vcts_adx_tti_vpci_long_only"
FAMILY = "volume_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [30.0, 25.0],
    "long_vp": [25, 50],
}
DEFAULT_PARAMS = {"len_adx": 14, "smt": 14, "fast_tti": 13, "slow_tti": 26, "smt_tti": 9,
                  "short_vp": 5, "long_vp": 25, "adx_min": 30.0}


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


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _vwma(x, v, n):
    return (x * v).rolling(n).mean() / v.rolling(n).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["len_adx"])
    up_m, dn_m = h.diff(), -lo.diff()
    pdm = up_m.where((up_m > dn_m) & (up_m > 0), 0.0).where(up_m.notna())
    mdm = dn_m.where((dn_m > up_m) & (dn_m > 0), 0.0).where(dn_m.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n)
    pdi, mdi = _fixnan(100 * _rma(pdm, n) / atr), _fixnan(100 * _rma(mdm, n) / atr)
    adx = 100 * _rma(((pdi - mdi) / (pdi + mdi)).abs(), int(p["smt"]))
    fma, sma_ = _vwma(c, v, int(p["fast_tti"])), _vwma(c, v, int(p["slow_tti"]))
    mult = (fma / sma_) ** 2
    tti = fma * mult - sma_ / mult
    sig = tti.rolling(int(p["smt_tti"])).mean()
    nl, ns = int(p["long_vp"]), int(p["short_vp"])
    vpci = ((_vwma(c, v, nl) - c.rolling(nl).mean()) * (_vwma(c, v, ns) / c.rolling(ns).mean())
            * (v.rolling(ns).mean() / v.rolling(nl).mean()))
    entry = (adx > float(p["adx_min"])) & (tti > sig) & (vpci > 0)
    ex = vpci < 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}

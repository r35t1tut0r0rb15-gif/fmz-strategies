"""ADX-gated EMA 20 crosses, broker days: with the ADX 14 at or below 30, a close crossing above the EMA 20 goes long; with
the ADX at or above 30, a close crossing below it goes short; reversing on the next opposite signal.
Port of FMZ strategy #433936 "Holy Grail Strategy" (LAT Holy Grail v3).

FMZ source id: 433936

Source
    https://www.fmz.com/strategy/433936 (PineScript v3, FMZ last modified 2023-12-01 15:27:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 164-210), EMA 20; DI 14, ADX smoothing 14; target 30
    adx3 <= 30 and crossover(close, ema20) -> entry long;  adx3 >= 30 and crossunder(close, ema20) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The test-period function is defined but the entries do not use it, so the whole history trades,
      as written. ADX as in the source (rma, fixnan).
    * strategy.entry with one id in both directions reverses: REVERSAL INTENDED. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX level and EMA crosses.
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

NAME = "fmz_433936_holy_grail_adx_ema"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
    "target": [30, 20],
}
DEFAULT_PARAMS = {"ema_len": 20, "di_len": 14, "adx_len": 14, "target": 30}


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


def _fixnan(v):
    out = v.copy()
    last = np.nan
    for i in range(len(out)):
        if np.isnan(out[i]):
            out[i] = last
        else:
            last = out[i]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, an = int(p["di_len"]), int(p["adx_len"])
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    trur = tr.ewm(alpha=1 / n, adjust=False).mean()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    with np.errstate(invalid="ignore", divide="ignore"):
        plus = _fixnan((100 * pdm.ewm(alpha=1 / n, adjust=False).mean() / trur).replace(
            [np.inf, -np.inf], np.nan).to_numpy())
        minus = _fixnan((100 * mdm.ewm(alpha=1 / n, adjust=False).mean() / trur).replace(
            [np.inf, -np.inf], np.nan).to_numpy())
    s = plus + minus
    adx = 100 * pd.Series(np.abs(plus - minus) / np.where(s == 0, 1.0, s), index=c.index).ewm(
        alpha=1 / an, adjust=False).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    tgt_ = float(p["target"])
    le = ((adx <= tgt_) & (c > e) & (c.shift(1) <= e.shift(1))).astype(bool)
    se = ((adx >= tgt_) & (c < e) & (c.shift(1) >= e.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}

"""Smoothed momentum sign with a movement filter, broker days, with a stop: the second smoothing of the price-change oscillator over
its signal (d above zero) while the 30-bar rate of change is outside a band goes long; below zero goes short (reversing); each
trade carries a 2 % stop (the 5000 % target is out of reach and dropped).
Port of FMZ strategy #435502 "Momentum Indicator Decision Trading Strategy" (Decision BF).

FMZ source id: 435502

Source
    https://www.fmz.com/strategy/435502 (PineScript v4, FMZ last modified 2023-12-15 15:31:52).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 143-220), ohlc4 smoothed 31 then 20, signal EMA 9; ROC 30 smoothed 15 against +-3.5 %; stop 2 %, target 5000 %
    i = ohlc4 / nz(ohlc4[1], ohlc4) 100;  pmol2 = csf(i - 100, 31);  pmol = csf(10 pmol2, 20);  pmols = ema(pmol, 9);  d = pmol - pmols;  csf(x, n) = (x - nz(csf[1])) 2 / n + nz(csf[1])
    moving = ema(roc(close, 30), 15) > 3.5 or < -3.5;  long = d > 0 and moving;  short = d < 0 and moving;  long -> entry long;  short -> entry short;  exit(stop = avg (1 - 2 %), limit = avg (1 + 5000 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recursive smoothing starts from zero (nz of the first value), as written. The condition is
      re-sent every bar; vbt ignores a same-side signal while in a position, and after a stop exit the
      next bar enters again if the condition still holds (as Pine). The stop is a fraction of the
      fill price: sl_stop 0.02; the target (5000 %) cannot be reached and is not ported. The stop
      and target are only active from the bar after the signal change; the port's stop starts at
      the fill. Opposite entries reverse: REVERSAL INTENDED.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The
      percent-of-equity size and commission are sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, smoothed momentum, a rate-of-change band and a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430880 (3 members, best partner #432979, Jaccard 0.652); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435502_smoothed_momentum_roc_band_stop"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.02, 0.05],
    "length1": [31, 20],
}
DEFAULT_PARAMS = {"sl": 0.02, "length1": 31, "length2": 20, "sig": 9, "roc_len": 30, "pcnt": 7}


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


def _csf(x, length):
    """Pine calc_csf: csf = (x - nz(csf[1])) * 2 / length + nz(csf[1]), started from zero."""
    sm = 2.0 / length
    out = np.zeros(len(x))
    prev = 0.0
    for i in range(len(x)):
        v = x[i]
        prev = prev if np.isnan(v) else (v - prev) * sm + prev
        out[i] = prev
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = ((o + h + lo + c) / 4)
    prev = src.shift(1).where(src.shift(1).notna(), src)
    i = (src / prev * 100).to_numpy(dtype=float)
    pmol2 = _csf(i - 100, int(p["length1"]))
    pmol = _csf(10 * pmol2, int(p["length2"]))
    pmols = pd.Series(pmol, index=c.index).ewm(span=int(p["sig"]), adjust=False).mean()
    d = pd.Series(pmol, index=c.index) - pmols
    n = int(p["roc_len"])
    roc = 100 * (c - c.shift(n)) / c.shift(n)
    emaroc = roc.ewm(span=max(int(n / 2), 1), adjust=False).mean()
    band = float(p["pcnt"]) / 2
    moving = (emaroc > band) | (emaroc < -band)
    le = ((d > 0) & moving).fillna(False).astype(bool)
    se = ((d < 0) & moving).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}

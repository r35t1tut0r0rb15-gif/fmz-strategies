"""FRAMA of the weekly close with a FRAMA signal line, 30-minute bars: the FRAMA (fractal-adaptive average of the last
completed week's close, adapted on the weekly high / low) crossing above its own FRAMA goes long, crossing below goes
short.
Port of FMZ strategy #429778 "Trend Following Strategy with Moving Averages and SuperTrend".

FMZ source id: 429778

Source
    https://www.fmz.com/strategy/429778 (PineScript v4, FMZ last modified 2023-10-20 16:50:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-292), FRAMA 12 (FC 1, SC 200) on the 1W close / high / low; SuperTrend 3 / 7 rules off; exits off
    High / Low / source = security(tickerid, '1W', high / low / close)
    alpha from the fractal dimension of High / Low over 6 / 6 / 12 chart bars, clamped to [2/201, 1]
    frama = (1 - alpha) x frama[1] + alpha x source; signal = the same FRAMA of frama
    crossover(frama, signal) -> entry long; crossunder -> entry short (SuperTrend enter / exit off; TP / SL / trail inputs 0 -> na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('1W', x) without lookahead is read as the last completed week: weeks of broker days
      (17:00 America/New_York), Monday to Sunday, built inside simulate() from the port's own bars and
      shifted one week. The source's values on the last bar of a week already include that week (one bar
      earlier): stated approximation. The rolling windows then run over the chart's bars, as written.
    * `nz(dimen1[1])` keeps the previous raw dimension when a range is zero; frama starts from 0 (nz).
    * The SuperTrend rules default to off and the TP / SL / trail inputs to 0 (na): no other exits.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed broker weeks.
    2 generic: PASS, a fractal-dimension adaptive average of prices (scale-free alpha).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the off-by-default TP / SL / trail stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: weekly values on broker weeks (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429778_weekly_frama_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 24],
    "frama_sc": [200, 100],
}
DEFAULT_PARAMS = {"length": 12, "frama_fc": 1, "frama_sc": 200}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _frama(src, hi, lo, n, fc, sc):
    n1 = max(n // 2, 1)
    h1, l1 = hi.rolling(n1).max(), lo.rolling(n1).min()
    nn1 = (h1 - l1) / n1
    nn2 = (h1.shift(n1) - l1.shift(n1)) / n1
    nn3 = (hi.rolling(n).max() - lo.rolling(n).min()) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        d1 = ((np.log(nn1 + nn2) - np.log(nn3)) / np.log(2)).to_numpy()
    ok = ((nn1 > 0) & (nn2 > 0) & (nn3 > 0)).to_numpy()
    w = np.log(2.0 / (sc + 1))
    s = src.to_numpy(dtype=float)
    m = len(s)
    out = np.zeros(m)
    for i in range(m):
        dim = d1[i] if ok[i] else (d1[i - 1] if i >= 1 and not np.isnan(d1[i - 1]) else 0.0)
        a1 = np.exp(w * (dim - 1))
        oa = 1.0 if a1 > 1 else (0.01 if a1 < 0.01 else a1)
        on = (2 - oa) / oa
        nn = ((sc - fc) * (on - 1)) / (sc - 1) + fc
        a_ = 2 / (nn + 1)
        a = 2 / (sc + 1) if a_ < 2 / (sc + 1) else (1.0 if a_ > 1 else a_)
        prev = out[i - 1] if i >= 1 else 0.0
        out[i] = (1 - a) * prev + a * s[i]      # src has no na here (na weeks enter as 0, as nz)
    return pd.Series(out, index=src.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    wk = pd.DataFrame({"h": h.to_numpy(), "l": lo.to_numpy(), "c": c.to_numpy()}, index=week)
    agg = wk.groupby(level=0).agg({"h": "max", "l": "min", "c": "last"}).shift(1)   # the last completed week
    W = agg.reindex(week)
    hi = pd.Series(W["h"].to_numpy(), index=c.index)
    lw = pd.Series(W["l"].to_numpy(), index=c.index)
    src = pd.Series(W["c"].to_numpy(), index=c.index)
    n, fc, sc = int(p["length"]), float(p["frama_fc"]), float(p["frama_sc"])
    fr = _frama(src.fillna(0.0), hi, lw, n, fc, sc).where(src.notna())
    sig = _frama(fr.fillna(0.0), hi, lw, n, fc, sc).where(fr.notna())
    long_e = ((fr > sig) & (fr.shift(1) <= sig.shift(1))).astype(bool)
    short_e = ((fr < sig) & (fr.shift(1) >= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}

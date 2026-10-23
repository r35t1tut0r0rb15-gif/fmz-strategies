"""Broker days: the close at the last zero-crossing of the price-volume trend against the middle of its 200-bar range (VTY) is a level; the close crossing over it goes long, crossing under goes short; a long also closes when the EMA 2 crosses under VTY + 10 / 20 / 30 %, a short when it crosses over VTY - 10 / 20 / 30 %; reversing.
Port of FMZ strategy #439272 "Extended Price Volume Trend Strategy" (Extended Price Volume Trend).

FMZ source id: 439272

Source
    https://www.fmz.com/strategy/439272 (PineScript v5, FMZ last modified 2024-01-18 16:32:28).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 114-172), trend length 200; TP 10 / 20 / 30 %; EMA 2
    vt = cum(change(close) / close[1] * volume);  VTX = vt - (highest(vt, 200) + lowest(vt, 200)) / 2;  VTY = valuewhen(cross(VTX, 0), close, 0)
    crossover(close, VTY) -> entry Long;  close Long when crossunder(close, VTY) or crossunder(ema2, VTY x 1.1 / 1.2 / 1.3);  crossunder(close, VTY) -> entry Short;  close Short when crossover(close, VTY) or crossover(ema2, VTY x 0.9 / 0.8 / 0.7)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cumulative sum starts at the first change (the na first bar adds nothing). VTY is the close
      of the latest bar where VTX crossed zero either way. v5 int / int gives a fraction, so the levels are
      VTY x (1 +- 0.1 / 0.2 / 0.3). A close acts only on a position the bar's entries leave unchanged.
      The no-volume runtime error only fires on the last bar of a series without volume. REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-volume-trend pivot level crossings with ladder take-profits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the price-volume trend cum(change / close[1] x volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439272_extended_pvt_level_cross_ladder_tp_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [200, 100],
    "tp1": [10, 5],
}
DEFAULT_PARAMS = {"length": 200, "tp1": 10, "ema_len": 2}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _over(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _under(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    vt = (c.diff() / c.shift(1) * v).fillna(0.0).cumsum()
    vtx = vt - (vt.rolling(n).max() + vt.rolling(n).min()) / 2
    zero = pd.Series(0.0, index=c.index)
    crossed = (_over(vtx, zero) | _under(vtx, zero)).to_numpy()
    vty = _fixnan(pd.Series(np.where(crossed, c.to_numpy(dtype=float), np.nan), index=c.index))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    t = float(p["tp1"]) / 100
    lx_ = (_under(ema, vty * (1 + t)) | _under(ema, vty * (1 + 2 * t)) | _under(ema, vty * (1 + 3 * t))).to_numpy()
    sx_ = (_over(ema, vty * (1 - t)) | _over(ema, vty * (1 - 2 * t)) | _over(ema, vty * (1 - 3 * t))).to_numpy()
    lc = _over(c, vty).to_numpy()
    sc = _under(c, vty).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and new != 1:
            new = 1
        elif sc[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and (sc[i] or lx_[i]):
                new = 0
            elif pos == -1 and (lc[i] or sx_[i]):
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

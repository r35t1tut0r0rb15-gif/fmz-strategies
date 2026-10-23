"""Broker days, long only: a bar with volume above 1.5 x its SMA 20 while the ATR 14 sits within one standard deviation of its own 14-bar mean goes long; a low at or under a trailing line (the low minus 2 ATR 14, ratcheted up while long) closes at the next open.
Port of FMZ strategy #436906 "Relative Volume Price Strategy" ([KL] Relative Volume + ATR Strategy (DojiEmoji)).

FMZ source id: 436906

Source
    https://www.fmz.com/strategy/436906 (PineScript v4, FMZ last modified 2023-12-28 17:54:44).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 135-196), ATR 14 volatility band (mean +- 1 sd over 14); trailing line low - 2 x ATR 14; volume SMA 20 x 1.5; pyramiding 1
    stop_loss_price := flat ? low - 2 atr(14) : max(stop_loss_price, low - 2 atr(14));  long and low <= stop_loss_price -> close Long (before the entry)
    volume > 1.5 sma(volume, 20) and avg_atr - sd_atr < atr < avg_atr + sd_atr -> entry Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line is the script's bar-close ratchet and the exit a strategy.close, so it fills at
      the next open: ported in the signals. While flat the line is reset to 0 at the bar's end, so on the
      fill bar it restarts at that bar's low - 2 ATR. With pyramiding 1 an entry signal while long adds
      nothing; a bar that both closes and re-signals is ported as the close only (the script would refill
      at once; approximation). The relative volume compares the bar with its own SMA. Long only. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR trailing line in the signals.
    2 generic: PASS, relative-volume spikes in a normal volatility regime.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 1.5 x sma(volume, 20); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); the 2016 start dropped.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436906_relative_volume_normal_atr_trailing_low_long"
FAMILY = "volume_filter"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_mult": [1.5, 2.0],
    "tsl_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "tsl_len": 14, "tsl_mult": 2.0, "vol_len": 20, "vol_mult": 1.5}


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
    n = int(p["atr_len"])
    atr = _rma(tr, n)
    av, sd = atr.rolling(n).mean(), atr.rolling(n).std(ddof=0)
    calm = ((atr < av + sd) & (atr > av - sd)).to_numpy()
    spike = (v > v.rolling(int(p["vol_len"])).mean() * float(p["vol_mult"])).to_numpy()
    ent = calm & spike
    tsl = (lo - _rma(tr, int(p["tsl_len"])) * float(p["tsl_mult"])).to_numpy()
    lv = lo.to_numpy(dtype=float)
    m = len(lv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, stop = 0, False, 0.0
    for i in range(m):
        if pend:
            pos, pend = 1, False
        if pos == 0:
            stop = tsl[i]
        else:
            stop = max(stop, tsl[i]) if not np.isnan(tsl[i]) else stop
        if pos == 1 and lv[i] <= stop:
            lx[i], pos = True, 0
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i], pend = True, True
        if pos == 0:
            stop = 0.0                                    # CLEAN UP while flat (also on the signal bar)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

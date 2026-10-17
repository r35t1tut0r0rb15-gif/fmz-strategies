"""SSL channel crosses with an EMA 200 filter, broker days, from flat: the SSL up line crossing above the down line with
the close above the EMA 200 goes long (mirror short), with a stop at the signal bar's opposite SSL line; the reverse
SSL cross closes the position only while it is in profit.
Port of FMZ strategy #431284 "Dual SSL Strategy with EMA Stop Loss" (SSL Strategy + EMA 200 AND Stop Loss).

FMZ source id: 431284

Source
    https://www.fmz.com/strategy/431284 (PineScript v5, FMZ last modified 2023-11-06 16:52:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 150-232), SSL 10, EMA 200
    Hlv = close > sma(high, 10) ? 1 : close < sma(low, 10) ? -1 : Hlv[1]; sslDown / sslUp from Hlv
    flat and close > ema200 and crossover(sslUp, sslDown) -> entry long, SL = sslDown (the SMA of lows)
    long and crossunder(sslUp, sslDown) and close < avg x 1.1 and openprofit > 0.1 -> close
    long and SL -> exit(stop = SL) once, then SL := 0 (mirror short with SL = the SMA of highs)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is placed once, on the bar after the fill, at the signal bar's SSL line and kept: a
      fixed level, ported as a fraction of the signal close (sl_stop, shifted one bar; vbt applies it
      from the fill bar).
    * openprofit > 0.1 (account currency, with qty = equity / close) is read as the close beyond the
      entry price (the fill at the open after the signal); the long exit also needs the close under
      1.1 x the entry, as written. The cross exits are close-checked.
    * Entries only from flat ("flat" follows the house stop on bars). Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop fixed at entry.
    2 generic: PASS, SSL channel, an EMA and a profit test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity / close stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431284_ssl_ema200_stop"
FAMILY = "ssl_channel"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [10, 20],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"length": 10, "ema_len": 200}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    sh, sl = h.rolling(n).mean().to_numpy(), lo.rolling(n).mean().to_numpy()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    hlv = np.nan
    for i in range(m):
        hlv = 1 if cv[i] > sh[i] else (-1 if cv[i] < sl[i] else hlv)
        if not np.isnan(hlv):
            dn[i] = sh[i] if hlv < 0 else sl[i]
            up[i] = sl[i] if hlv < 0 else sh[i]
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_arr = np.full(m, np.nan)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(1, m):
        if pos != 0 and i >= entry_i:                    # house stop from the fill price
            e = ov[entry_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        x_up = up[i] > dn[i] and up[i - 1] <= dn[i - 1]
        x_dn = up[i] < dn[i] and up[i - 1] >= dn[i - 1]
        if pos == 0:
            if cv[i] > ema[i] and x_up and dn[i] < cv[i]:
                le[i], pos, entry_i, s_ = True, 1, i + 1, (cv[i] - dn[i]) / cv[i]
                sl_arr[i] = s_
            elif cv[i] < ema[i] and x_dn and dn[i] > cv[i]:
                se[i], pos, entry_i, s_ = True, -1, i + 1, (dn[i] - cv[i]) / cv[i]
                sl_arr[i] = s_
        elif i >= entry_i:
            e = ov[entry_i]
            if pos == 1 and x_dn and e < cv[i] < e * 1.1:
                lx[i], pos = True, 0
            elif pos == -1 and x_up and cv[i] < e:
                sx[i], pos = True, 0
    return le, lx, se, sx, sl_arr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": pd.Series(_run(bars_df, p)[4], index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}

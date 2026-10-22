"""Closes outside an EMA 3 +/- 1.5 ATR 3 or RMA 3 +/- 1 ATR 3 channel, broker days, from flat: a close over either upper band goes long, under either lower band goes short, with a stop at the signal bar's open; a low crossing over (high crossing under) the previous open closes.
Port of FMZ strategy #489654 "Triple EMA and Triple RMA Adaptive Channel Crossover Strategy" (EMA3 & RMA3 ATR Strategy).

FMZ source id: 489654

Source
    https://www.fmz.com/strategy/489654 (PineScript v5, FMZ last modified 2025-04-07 13:43:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 227-296), EMA 3 x 1.5 ATR 3; RMA 3 x 1.0 ATR 3; stop = signal open; risk 0.5 % sizing; capital 10000
    flat and (close > ema3 + 1.5 atr or close > rma3 + atr) -> entry Long (qty = 0.5 % equity / |close - open|) + exit(stop = open);  mirror -> entry Short
    long and crossover(low, open[1]) -> close Long;  short and crossunder(high, open[1]) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The quantity is na when the close equals the open, so no entry then. The stop is the signal bar's
      open, sent as a fraction of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256). Entries need a flat position at the bar's close, so a loop follows the stop on each
      bar's high / low (as #449508) and the open-crossing closes. If both sides fire from flat the short,
      placed later, wins (as #437773). Opposite entries cannot occur (entries only from flat). Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The risk-sized quantity is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-open stop as a fraction of the fill.
    2 generic: PASS, short-channel breakouts with an open-based stop and exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity and capital stored, not ported.
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

NAME = "fmz_489654_ema3_rma3_atr_channel_breakout_open_stop_flat"
FAMILY = "keltner_channel"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_mult": [1.5, 2.5],
    "atr_len": [3, 10],
}
DEFAULT_PARAMS = {"ema_mult": 1.5, "atr_len": 3, "ema_len": 3, "rma_len": 3, "rma_mult": 1.0}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_len"]))
    ev = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rv = _rma(c, int(p["rma_len"]))
    ke, kr = float(p["ema_mult"]), float(p["rma_mult"])
    buy = (((c > ev + atr * ke) | (c > rv + atr * kr)) & (c != o)).to_numpy()
    sell = (((c < ev - atr * ke) | (c < rv - atr * kr)) & (c != o)).to_numpy()
    o1, o2 = o.shift(1), o.shift(2)
    xo = ((lo > o1) & (lo.shift(1) <= o2)).to_numpy()
    xu = ((h < o1) & (h.shift(1) >= o2)).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, side = np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, sl_n = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl = pend, 0, sl_n
            if (pos == 1 and sl >= ov[i]) or (pos == -1 and sl <= ov[i]):
                if pos == 1:                     # a level through the fill: closed at the next open
                    lx[i] = True
                else:
                    sx[i] = True
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and lv[i] <= sl:
            pos = 0                              # the stop fills inside this bar
        elif pos == -1 and pend == 0 and hv[i] >= sl:
            pos = 0
        if pos == 0 and pend == 0:
            if sell[i]:
                sl_n = ov[i]
                se[i], pend, sl_sent[i], side[i] = True, -1, sl_n, -1
            elif buy[i]:
                sl_n = ov[i]
                le[i], pend, sl_sent[i], side[i] = True, 1, sl_n, 1
        elif pos == 1 and pend == 0 and xo[i]:
            lx[i], pend = True, 2
        elif pos == -1 and pend == 0 and xu[i]:
            sx[i], pend = True, 2
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, sd = sl_l.shift(1), sd.shift(1)    # the signal bar's level, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}

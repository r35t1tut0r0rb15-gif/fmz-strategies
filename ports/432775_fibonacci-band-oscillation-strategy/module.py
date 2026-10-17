"""Fibonacci ATR band breakouts from flat, broker days: the close above the previous bar's EMA 14 + 1.618 x ATR 14 band goes
long, the close below the previous bar's EMA 14 - 1 x ATR band goes short, each only from flat; a 4 % stop and a 1.5 %
target from the fill.
Port of FMZ strategy #432775 "Fibonacci Band Oscillation Strategy" (FIBONACCI BANDS Strategy (FBANDS)).

FMZ source id: 432775

Source
    https://www.fmz.com/strategy/432775 (PineScript v5, FMZ last modified 2023-11-21 13:47:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 181-294), EMA 14, ATR 14 (SMA of the true range), ratios 1.618 / 2.618 / 4.236, both sides, stop 4 %, TP 1.5 %
    long2 = close > FIBOTOP2[1] (the default option "close>FIBOTOP1" assigns FIBOTOP2, as written);  short2 = close < FIBOBOT1[1]
    flat and long2 -> entry long;  flat and short2 -> entry short
    in position: exit(stop = avg x (1 -+ 4 %), limit = avg x (1 +- 1.5 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default long option is labelled FIBOTOP1 but its branch reads FIBOTOP2: ported as written
      (EMA + 1.618 ATR); listed with the as-written ports. The bands of the previous bar are compared
      with the current close. The ATR is the SMA of the true range.
    * Entries only from flat (position_size == 0): the port's state machine follows the house bracket
      on bars, and an entry may follow a bracket exit in the same bar, so Opposite entries cannot
      occur. The bracket is a fixed fraction of the fill by side, live on the fill bar in the house
      engine (Pine places it from the fill bar's close; stated). The date window (2022-02-01 on) and
      the alert texts are dropped / unused.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; stops on
      daily bars: mark coarse_bar_stop. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ATR bands and percentage exits of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_432775_fibonacci_atr_band_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_ratio": [1.618, 1.0],
    "sl_pct": [4.0, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 14, "atr_len": 14, "long_ratio": 1.618, "short_ratio": 1.0, "sl_pct": 4.0, "tp_pct": 1.5}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.rolling(int(p["atr_len"])).mean()
    top = (e + atr * float(p["long_ratio"])).shift(1)
    bot = (e - atr * float(p["short_ratio"])).shift(1)
    el, es = (c > top).to_numpy(), (c < bot).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl_pct"]) / 100, float(p["tp_pct"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            ep = ov[e_i]
            if pos == 1 and (lv[i] <= ep * (1 - sl) or hv[i] >= ep * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= ep * (1 + sl) or lv[i] <= ep * (1 - tp)):
                pos = 0
        if pos == 0 and (el[i] or es[i]):
            pos = 1 if el[i] else -1
            e_i = i + 1
            ent[i] = pos
        tgt[i] = pos
    return tgt, ent


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, ent = _run(bars_df, p)
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1
    lx = (prev == 1) & (tgt == 0)
    se = ent == -1
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, ent = _run(bars_df, p)
    idx = bars_df.index
    on = pd.Series(ent != 0, index=idx)
    sl = pd.Series(np.where(on, float(p["sl_pct"]) / 100, np.nan), index=idx)
    tp = pd.Series(np.where(on, float(p["tp_pct"]) / 100, np.nan), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}

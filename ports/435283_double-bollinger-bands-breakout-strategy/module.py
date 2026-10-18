"""Double Bollinger breakout, broker days, long only: after two consolidating closes between the lower 2 sd band and the upper 1 sd
band, a close over the upper 1 sd band goes long; the long is closed when the low reaches an ATR trailing level
(low - 2 ATR, ratcheted up) or when the close falls back under the upper band while the entry price is above the level.
Port of FMZ strategy #435283 "Double Bollinger Bands Breakout Strategy" ([KL] Double BB Strategy).

FMZ source id: 435283

Source
    https://www.fmz.com/strategy/435283 (PineScript v4, FMZ last modified 2023-12-13 17:33:24).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 112-163), Bollinger 20 with 1 and 2 sd bands; ATR 14 x 2 trailing level on the low; pyramiding 1
    is_neutral = close < upper1 and close > lower2;  is_consol = is_neutral and is_neutral[2];  entry_signal = is_consol[1] and close > upper1
    stop = flat ? low - 2 ATR : max(stop, low - 2 ATR);  end_of_rally = close < upper1 and avg_price > stop;  long and (low <= stop or end_of_rally) -> close;  (flat or long and close > stop) and entry_signal -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The level and the end-of-rally test are the script's own, tested on bar closes; strategy.close
      fills at the next open: a close-based exit signal, not a broker stop (no mark). The position
      state is followed inside simulate (the fill is the next bar's open, which also gives the average
      price). pyramiding = 1 makes a second entry while long do nothing. A bar that closes the long
      and signals a new entry in the same bar (the low reaches the level while the close is back over
      the upper band) is a close then an entry at the same open in Pine; the port holds the long
      through it. The level is reset to 0 on flat bars and recomputed from the low each flat bar.
      stdev is the population deviation (Pine). Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, bands and an ATR trailing level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435283_double_bb_breakout_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [2.0, 3.0],
    "atr_len": [14, 21],
}
DEFAULT_PARAMS = {"boll_len": 20, "atr_mult": 2.0, "atr_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["boll_len"])
    ma = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    up1, lo2 = ma + sd, ma - 2 * sd
    neutral = (c < up1) & (c > lo2)
    consol = neutral & neutral.shift(2, fill_value=False)
    entry_sig = (consol.shift(1, fill_value=False) & (c > up1)).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr2 = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"])).to_numpy()
    cv, lv, ov, u1 = (x.to_numpy(dtype=float) for x in (c, lo, o, up1))
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg, stop = 0, np.nan, 0.0         # pos: the position as of this bar's open fills
    pend = None                             # None, "enter", "exit"
    for i in range(m):
        if pend == "enter":
            pos, avg = 1, ov[i]
        elif pend == "exit":
            pos, avg = 0, np.nan
        pend = None
        cand = lv[i] - atr2[i]
        if pos == 0:
            stop = cand
        else:
            stop = max(stop, cand)
        out = False
        if pos > 0:
            rally_end = (cv[i] < u1[i]) and (avg > stop)
            if lv[i] <= stop or rally_end:
                out = True
        enter = bool(entry_sig[i]) and (pos == 0 or (pos > 0 and cv[i] > stop))
        if pos == 0 and enter:
            pend = "enter"
        elif pos > 0 and out and not enter:
            pend = "exit"
        elif pos > 0 and out and enter:
            pend = "enter"                  # close then entry at one open: held through, entry price renewed
        if pos == 0:
            stop = 0.0
        tgt[i] = 1 if (pend == "enter" or (pos == 1 and pend != "exit")) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}

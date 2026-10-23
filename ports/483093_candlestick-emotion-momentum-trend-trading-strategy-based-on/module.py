"""Broker days, from flat only with a 10-bar cooldown: the average of three candle-pattern "emotion" oscillators crossing over 0.1 goes long, crossing over 0.2 goes short; a long closes on a high-volume green bar above its entry, after 20 bars if not below the entry, or after 10 bars if 2 % under it; shorts mirrored.
Port of FMZ strategy #483093 "Candlestick Emotion Momentum Trend Trading Strategy Based on Quantitative Indicators" (Candle Emotion Index Strategy (CEI)).

FMZ source id: 483093

Source
    https://www.fmz.com/strategy/483093 (PineScript v6, FMZ last modified 2025-02-21 13:23:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-303), lookback 14; indecision / fear / greed pattern scores (var, recursive); levels 0.1 / 0.2; volume SMA 14 x 1.5; cooldown 10; hold 20 / loss hold 10; loss 2 %
    each oscillator: var score; score := (score + count of the pattern over bars 1 .. 14) / 14  (per pattern, then averaged)
    longBuySignal = crossover(avgOsc, 0.1) and position_size == 0 and cooldown <= 0 -> entry Long;  shortBuySignal = crossover(avgOsc, 0.2) and the same -> entry Short
    long exits: green bar with volume > 1.5 x sma(volume, 14) and close > entry; hold >= 20 and close >= entry; hold >= 10 and close < entry x 0.98 -> close_all, cooldown := 10  (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pattern scores are var inside their functions, so each bar's score is (previous score + this
      bar's count) / 14, a recursive filter rather than a plain frequency, as written. Ratios with a zero
      denominator (a flat bar or a zero body) are na and count as false. The short signal is also a
      crossing OVER (0.2). Entries need a flat position and an expired cooldown, so opposite entries
      cannot occur. The hold counters start at the fill bar. Closes fill at the next open. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-pattern sentiment crossings with volume, time and loss exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 14 in the take-profit close; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat after the cooldown).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483093_candle_emotion_index_cooldown_time_loss_exits"
FAMILY = "candlestick_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_hold": [20, 40],
    "cooldown": [10, 5],
}
DEFAULT_PARAMS = {"length": 14, "max_hold": 20, "loss_hold": 10, "loss": 0.02, "cooldown": 10, "vol_mult": 1.5}


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


def _ratio(a, b):
    return a / b.where(b != 0)                 # division by zero is na (compares false)


def _rec_score(flags, n):
    """var score; score := (score + count of flags over bars 1 .. n) / n."""
    cnt = sum(flags.shift(i, fill_value=False).astype(float) for i in range(1, n + 1)).to_numpy()
    out = np.zeros(len(cnt))
    s = 0.0
    for i in range(len(cnt)):
        s = (s + cnt[i]) / n
        out[i] = s
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["length"])
    body, rng = (c - o).abs(), h - lo
    up_w, lo_w = h - np.maximum(o, c), np.minimum(o, c) - lo
    o1, c1, o2, c2 = o.shift(1), c.shift(1), o.shift(2), c.shift(2)
    br = _ratio(body, rng)
    doji = br < 0.1
    spin = (br < 0.3) & (br >= 0.1)
    star = (_ratio(up_w, body) > 0.5) & (lo_w < body)
    hang = (_ratio(lo_w, body) > 0.5) & (up_w < body)
    pb = (c1 - o1).abs()
    bear_e = (c < o1) & (o > c1) & (_ratio(body, pb) > 0.5)
    maru = br > 0.9
    hamm = (_ratio(lo_w, body) > 0.5) & (up_w < body)
    bull_e = (c > o1) & (o < c1) & (_ratio(body, pb) > 0.5)
    sold = (c > o) & (c1 > o1) & (c2 > o2) & (c > c1) & (c1 > c2)
    indec = (_rec_score(doji, n) + _rec_score(spin, n)) / 2
    fear = (_rec_score(star, n) + _rec_score(hang, n) + _rec_score(bear_e, n)) / 3
    greed = (_rec_score(maru, n) + _rec_score(hamm, n) + _rec_score(bull_e, n) + _rec_score(sold, n)) / 4
    avg = pd.Series((indec + fear + greed) / 3, index=c.index)
    lsig = ((avg > 0.1) & (avg.shift(1) <= 0.1)).to_numpy()
    ssig = ((avg > 0.2) & (avg.shift(1) <= 0.2)).to_numpy()
    hv = (v > v.rolling(n).mean() * float(p["vol_mult"])).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    cn = c.to_numpy(dtype=float)
    mh, lh, ls, cd = int(p["max_hold"]), int(p["loss_hold"]), float(p["loss"]), int(p["cooldown"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, held, cool, hl, hs, epl, eps = 0, 0, 0, 0, 0, np.nan, np.nan
    for i in range(m):
        held = tgt                           # position after this bar's open
        if lsig[i] and held == 0 and cool <= 0 and i + 1 < m:
            epl, hl, cool, tgt = cn[i], 0, cd, 1
            le[i] = True
        if held == 1:
            hl += 1
            if (green[i] and hv[i] and cn[i] > epl) or (hl >= mh and cn[i] >= epl) or \
               (hl >= lh and cn[i] < epl * (1 - ls)):
                lx[i], tgt, cool = True, 0, cd
        if ssig[i] and held == 0 and cool <= 0 and i + 1 < m:
            eps, hs, cool, tgt = cn[i], 0, cd, -1
            se[i] = True
        if held == -1:
            hs += 1
            if (red[i] and hv[i] and cn[i] < eps) or (hs >= mh and cn[i] <= eps) or \
               (hs >= lh and cn[i] > eps * (1 + ls)):
                sx[i], tgt, cool = True, 0, cd
        if cool > 0:
            cool -= 1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

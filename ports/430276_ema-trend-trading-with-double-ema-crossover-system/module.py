"""Vin's Playzone (CDC Action Zone variant), broker days: a fresh buy zone (EMA 12 over EMA 26, price over the fast line)
after a bearish phase, or a stochastic-RSI cross-up during a bullish phase, goes long (and closes a short); the
mirror sell zone or a cross-down in a bearish phase goes short (and closes a long).
Port of FMZ strategy #430276 "双EMA黄绿交易系统Trend-Trading-with-Double-EMA-Crossover-System" (Vin's Playzone).

FMZ source id: 430276

Source
    https://www.fmz.com/strategy/430276 (PineScript v4, FMZ last modified 2023-10-26 17:15:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 212-312), EMA 12 / 26 (daily, smoothed 2), price EMA 2; stochastic RSI 14 / 14, K 5, D 4, levels 20 / 80
    xcross = ema(close, 2); efast = ema(ema(close, 12), 2); eslow = ema(ema(close, 26), 2)   (daily = chart)
    G1 = efast > eslow and xcross > efast; R1 = efast < eslow and xcross < efast
    buywhen = G1 and not G1[1]; sellwhen = R1 and not R1[1]
    bullish = barssince(buywhen) < barssince(sellwhen); bearish = the reverse
    buy = bearish[1] and buywhen; sell = bullish[1] and sellwhen
    buymore = bullish and crossover(K, D) (2 under 20, 1 over); sellmore = bearish and crossunder(K, D)
    buy or buymore -> entry long, close short;  sell or sellmore -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Fixed timeframe" D on the 1-day header chart: security returns the chart's own EMAs (no
      higher timeframe, nothing looked ahead).
    * The long and short triggers exclude each other; each closes the other side and enters its own:
      REVERSAL INTENDED. The 2009-9999 window is the author's: dropped.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages and a stochastic RSI.
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

NAME = "fmz_430276_vins_playzone"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [12, 8],
    "ema_slow": [26, 50],
}
DEFAULT_PARAMS = {"ema_fast": 12, "ema_slow": 26, "smooth": 2, "smooth_k": 5, "smooth_d": 4, "rsi_len": 14,
                  "sto_len": 14}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _since(ev):
    out = np.full(len(ev), np.inf)
    last = -1
    for i in range(len(ev)):
        if ev[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sm = int(p["smooth"])
    xc = c.ewm(span=sm, adjust=False).mean()
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean().ewm(span=sm, adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean().ewm(span=sm, adjust=False).mean()
    g1 = ((ef > es) & (xc > ef)).to_numpy()
    r1 = ((ef < es) & (xc < ef)).to_numpy()
    g1p, r1p = np.concatenate(([False], g1[:-1])), np.concatenate(([False], r1[:-1]))
    bw, sw = g1 & ~g1p, r1 & ~r1p
    sb, ss = _since(bw), _since(sw)
    bull = sb < ss
    bear = ss < sb
    bull1, bear1 = np.concatenate(([False], bull[:-1])), np.concatenate(([False], bear[:-1]))
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["sto_len"])
    ll, hh = r.rolling(n).min(), r.rolling(n).max()
    k = (100 * (r - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    kxo = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    kxu = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    go_long = (bear1 & bw) | (bull & kxo)
    go_short = (bull1 & sw) | (bear & kxu)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if go_long[i]:
            pos = 1
        elif go_short[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

"""Daily Bollinger band extremes with an RSI filter, 1-hour bars, from flat: a close under the daily lower band (20, 2 sd) with the RSI 14 under 30 goes
long, over the upper band with the RSI over 70 goes short; the position closes at the daily middle band, or at a 2 % stop checked on closes.
Port of FMZ strategy #435979 "基于布林带和RSI的量化交易策略Quantitative-Trading-Strategy-Based-on-Bollinger-Bands-and-RSI" (BB + RSI Estrategia).

FMZ source id: 435979

Source
    https://www.fmz.com/strategy/435979 (PineScript v4, FMZ last modified 2023-12-20 15:39:19).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 134-190), daily Bollinger 20 / 2 sd; RSI 14 at 30 / 70; take profit at the central band; stop 2 %
    flat: close < lower_D and rsi < 30 -> entry long (SL = close 0.98);  close > upper_D and rsi > 70 -> entry short (SL = close 1.02)
    long: close >= middle_D -> close; close <= SL -> close;  short: close <= middle_D -> close; close >= SL -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands come from request.security(tickerid, "D", bb(close, 20, 2)) without lookahead: the bands of
      the last COMPLETED broker day, built inside precompute from the loader's minutes (population
      deviation) and shifted one day. The take profit and the stop are rules on bar closes, filled at the next
      open (close-based exit signals, not broker stops). Entries only from flat: the position is followed
      inside simulate; opposite entries cannot occur. The equity-based quantity is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe bands from completed days.
    2 generic: PASS, bands, RSI and percent rules.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily bands (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435979_daily_bollinger_rsi_fade"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "take_profit": ["Central", "Opposite"],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "take_profit": "Central", "stop_loss": 2.0, "rsi_length": 14,
                  "ob": 70, "os": 30}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    ohlc = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.resample(FREQ, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    lab_min = broker_day(ohlc.index)
    dclose = ohlc["close"].groupby(lab_min).last()
    n = int(p["length"])
    mid = dclose.rolling(n).mean()
    sd = dclose.rolling(n).std(ddof=0)
    daily = pd.DataFrame({"mid": mid, "up": mid + float(p["mult"]) * sd, "lo": mid - float(p["mult"]) * sd}).shift(1)  # last completed day
    lab_bar = broker_day(bars.index)
    for col in ("mid", "up", "lo"):
        bars["d_" + col] = daily[col].reindex(lab_bar).to_numpy()
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    mid, up, lo = (bars_df["d_" + k].to_numpy(dtype=float) for k in ("mid", "up", "lo"))
    r = int(p["rsi_length"])
    ch = bars_df["close"].diff()
    u_ = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    d_ = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = (100 - 100 / (1 + u_ / d_)).where(d_ != 0, 100.0).where(u_.notna()).to_numpy()
    sl = float(p["stop_loss"]) / 100.0
    central = p["take_profit"] == "Central"
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend, stop = 0, None, 0.0
    for i in range(m):
        if pend == "L":
            pos = 1
        elif pend == "S":
            pos = -1
        elif pend == "X":
            pos = 0
        pend = None
        if pos == 0:
            if c[i] < lo[i] and rsi[i] < float(p["os"]):
                le[i], pend, stop = True, "L", c[i] * (1 - sl)
            elif c[i] > up[i] and rsi[i] > float(p["ob"]):
                se[i], pend, stop = True, "S", c[i] * (1 + sl)
        elif pos == 1:
            tp = (c[i] >= mid[i]) if central else (c[i] >= up[i])
            if tp or c[i] <= stop:
                lx[i], pend = True, "X"
        elif pos == -1:
            tp = (c[i] <= mid[i]) if central else (c[i] <= lo[i])
            if tp or c[i] >= stop:
                sx[i], pend = True, "X"
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}

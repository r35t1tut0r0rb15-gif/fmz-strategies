"""Heikin Ashi candles with no lower (or upper) wick in the EMA 10 / 30 trend, daily bars, entries only from flat: a candle whose HA open is its low with the EMA 10 over the EMA 30 goes long, a candle whose HA open is its high with the EMA 10 under goes short; a long closes on the first HA candle with a lower wick, a short on one with an upper wick.
Port of FMZ strategy #468308 "Crossover Moving Average with Smoothed Candlestick Momentum Strategy" (EMA Crossover with Heiken Ashi).

FMZ source id: 468308

Source
    https://www.fmz.com/strategy/468308 (PineScript v5, FMZ last modified 2024-09-26 14:54:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-199), Heikin Ashi built by hand (ha_low = min(low, ha_open, ha_close)); EMA 10 / 30; one open trade at a time
    ema10 > ema30 and ha_open == ha_low and no open trade -> entry Long;  ha_low < ha_open -> close Long
    ema10 < ema30 and ha_open == ha_high and no open trade -> entry Short;  ha_high > ha_open -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The HA open starts from (open + close) / 2 and recurses. The long's exit test is the opposite of
      its entry's candle test, so a long closes on the first later HA candle with a lower wick. Entries
      only from flat (strategy.opentrades at the bar's close); a close acts only on a position held into
      the bar. Opposite entries cannot occur (entries only from flat). No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, wickless Heikin Ashi candles in an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468308_wickless_heikin_ashi_ema10_30_trend_from_flat"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    hac = (o + h + lo + c) / 4
    hao = np.full(m, np.nan)
    for i in range(m):
        hao[i] = (o[i] + c[i]) / 2 if i == 0 else (hao[i - 1] + hac[i - 1]) / 2
    hah = np.maximum(h, np.maximum(hao, hac))
    hal = np.minimum(lo, np.minimum(hao, hac))
    cs = bars_df["close"]
    ef = cs.ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    es = cs.ewm(span=int(p["slow"]), adjust=False).mean().to_numpy()
    lc, sc = (ef > es) & (hao == hal), (ef < es) & (hao == hah)
    lxc, sxc = hal < hao, hah > hao
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if lc[i] and pos == 0:
            cur = 1
        if lxc[i] and pos == 1:
            cur = 0
        if sc[i] and pos == 0:
            cur = -1
        if sxc[i] and pos == -1:
            cur = 0
        if cur == 1 and pos == 0:
            le[i] = True
        elif cur == -1 and pos == 0:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

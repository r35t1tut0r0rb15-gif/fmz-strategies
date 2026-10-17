"""Sonic R channel breaks with MACD colour states, broker days: a green bar closing above the EMA 34 of highs, with a body
under twice the channel width, a small upper wick, the MACD above zero with a rising positive histogram, and the buy
setup armed by an earlier falling or negative MACD state, goes long; the mirror goes short (reversing). The exit order
option is off.
Port of FMZ strategy #434699 "基于价格通道和MACD的多时间框架交易策略Price-Channel-and-MACD-Based-Multi-Timeframe-Trading-Strategy" (Sonic R + Barcolor MACD).

FMZ source id: 434699

Source
    https://www.fmz.com/strategy/434699 (PineScript v2, FMZ last modified 2023-12-08 15:15:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 160-205), channel EMA 34 of high / low; MACD 12 / 26 / 9 (EMA); look back 34 (unused trend); TP / SL off
    hisup = delta > delta[1] and delta > 0 ? 1 : delta < delta[1] ? -1 : hisup[1];  hisdown mirror;  conbuy = hisdown == 1 or MACD < 0 ? 1 : hisup[5] == 1 and MACD[5] > 0 ? -1 : conbuy[1]
    gobuy = conbuy == 1 and close - open < 2 W and high - close < W / 2 and hisup == 1 and MACD > 0 and close - pacH < 1.5 W and close > open and high - close < close - open and close > pacH   (W = pacH - pacL);  gosell mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * All tests are on the bar's own prices and the channel width, so they are scale-free. The
      trend and the commented exits are unused; the exit orders are off by default (no stop). Both
      setups on one bar end short (the short entry is issued last). strategy.entry reverses:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel-relative bar shapes and MACD states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the unused exit inputs quoted in original_sizing.txt.
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

NAME = "fmz_434699_sonic_r_macd_colour"
FAMILY = "macd_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hilo_len": [34, 89],
    "fast": [12, 6],
}
DEFAULT_PARAMS = {"hilo_len": 34, "fast": 12, "slow": 26, "signal": 9}


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
    n = int(p["hilo_len"])
    pl, ph = lo.ewm(span=n, adjust=False).mean(), h.ewm(span=n, adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    dl = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    dv, d1, mv = dl.to_numpy(), dl.shift(1).to_numpy(), macd.to_numpy()
    m = len(dv)
    hu, hd, cb, cs = (np.zeros(m) for _ in range(4))
    with np.errstate(invalid="ignore"):
        for i in range(m):
            hu[i] = 1 if (dv[i] > d1[i] and dv[i] > 0) else (-1 if dv[i] < d1[i] else (hu[i - 1] if i else 0))
            hd[i] = 1 if (dv[i] < d1[i] and dv[i] < 0) else (-1 if dv[i] > d1[i] else (hd[i - 1] if i else 0))
            j = i - 5
            if hd[i] == 1 or mv[i] < 0:
                cb[i] = 1
            elif j >= 0 and hu[j] == 1 and mv[j] > 0:
                cb[i] = -1
            else:
                cb[i] = cb[i - 1] if i else 0
            if hu[i] == 1 or mv[i] > 0:
                cs[i] = 1
            elif j >= 0 and hd[j] == 1 and mv[j] < 0:
                cs[i] = -1
            else:
                cs[i] = cs[i - 1] if i else 0
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    plv, phv = pl.to_numpy(), ph.to_numpy()
    w = phv - plv
    with np.errstate(invalid="ignore"):
        gb = (cb == 1) & (cv - ov < 2 * w) & (hv - cv < w / 2) & (hu == 1) & (mv > 0) & (cv - phv < 1.5 * w) & \
            (cv > ov) & (hv - cv < cv - ov) & (cv > phv)
        gs = (cs == 1) & (ov - cv < 2 * w) & (cv - lv < w / 2) & (hd == 1) & (mv < 0) & (plv - cv < 1.5 * w) & \
            (cv < ov) & (cv - lv < ov - cv) & (cv < plv)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(gb & ~gs, index=ix), false, pd.Series(gs, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}

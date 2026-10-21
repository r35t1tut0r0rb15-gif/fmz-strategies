"""Point-count trend entries with a daily Donchian baseline, 4-hour bars: from flat, at least 4 of 6 long points with the close above the previous day's 8-day Donchian midline goes long, at least 5 of 7 short
points goes short; a long closes on a double SMA cross down, a close under the 100-bar low, or a short setup, while the close is at or under the daily midline (shorts mirror).
Port of FMZ strategy #438820 "Myo_LS_D Quantitative Strategy" (Myo_LS_D).

FMZ source id: 438820

Source
    https://www.fmz.com/strategy/438820 (PineScript v5, FMZ last modified 2024-01-15 14:56:03).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 159-270), stop lengths 100 / 100; long SMAs 10 / 20, short SMAs 5 / 10; trend SMAs 400 / 300; averages 20 / 60 / 120; daily baseline 8, short baseline 26
    long points: low > lowest(low, 200), high > highest(high, 200), close > sma 400, rrr_L > 3, close > ShortAvg[20], close > MidAvg[60]; >= 4 and close > baseLine_D -> entry Long Open (flat only)
    short points: high < highest 200, low < lowest 200, close < sma 300, close < donchian(26), rrr_S > 3, close < ShortAvg[20], close < MidAvg[60]; >= 5 -> entry Short Open (flat only)
    long and (crossunder of close under SMA 10 and SMA 20, or close < lowest(low, 100)[1] x 0.995, or a short setup) and close <= baseLine_D -> close_all;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * baseLine_D = security("D", donchian(8)), version 5 without lookahead: the last completed broker
      day's 8-day Donchian midline, built from the module's own bars. high > highest(high, 200) and low <
      lowest(low, 200) include the current bar, so those points are never scored, as written.
    * Criterion 2: rrr_L = tp_target_L - sl_L / sl_L is the target price minus 1 (operator precedence)
      and rrr_S a sum of price levels; "> 3" compares PRICE units: the port tests them against
      rrr_frac x the close (1e-4 reads 4 on BTC near 42000: always true there), as written.
    * Entries are taken only from flat; when both setups hold on a flat bar the short entry comes last
      and stands (as #437773). The closes act on the position held at the bar close. Entries only from
      flat: Opposite entries cannot occur. The capital / close quantity is sizing. FREQ = "4h" from the
      backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days.
    2 generic: ADAPT, price-unit "> 3" tests -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / close quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily midline.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438820_myo_point_count_daily_baseline"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trend_l": [400, 200],
    "base_periods": [8, 20],
}
DEFAULT_PARAMS = {"trend_l": 400, "base_periods": 8, "trend_s": 300, "sl_len_l": 100, "sl_len_s": 100,
                  "sma1": 10, "sma2": 20, "sma1_s": 5, "sma2_s": 10, "short_len": 20, "mid_len": 60,
                  "base_short": 26, "rrr_frac": 1e-4}

RPHI = 0.6180339887498949


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    low200, high200 = lo.rolling(200).min(), h.rolling(200).max()
    min800, max800 = lo.rolling(800).min(), h.rolling(800).max()
    tp_l = min800 + (max800 - min800) * RPHI
    sl_l = low200 * (1 - 0.005)
    rrr_l = tp_l - sl_l / sl_l
    rrr_s = (min800 + max800 - min800 * RPHI / high200 + 0.005 * high200 - low200 - 0.005 * low200)
    thr = float(p["rrr_frac"]) * c
    day = broker_day(bars_df.index)
    dd = bars_df.groupby(day).agg({"high": "max", "low": "min"})
    bp = int(p["base_periods"])
    d_base = (dd["low"].rolling(bp).min() + dd["high"].rolling(bp).max()) / 2
    base_d = pd.Series(d_base.shift(1).reindex(day).to_numpy(), index=c.index)   # last completed day
    bs = int(p["base_short"])
    base_s = (lo.rolling(bs).min() + h.rolling(bs).max()) / 2
    sa, ma_ = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["mid_len"])).mean()
    sal, mal = sa.shift(int(p["short_len"])), ma_.shift(int(p["mid_len"]))
    pts_l = ((lo > low200).astype(int) + (h > high200).astype(int)
             + (c > c.rolling(int(p["trend_l"])).mean()).astype(int) + (rrr_l > thr).astype(int)
             + (c > sal).astype(int) + (c > mal).astype(int))
    long_open = ((pts_l >= 4) & (c > base_d)).to_numpy()
    pts_s = ((h < high200).astype(int) + (lo < low200).astype(int)
             + (c < c.rolling(int(p["trend_s"])).mean()).astype(int) + (c < base_s).astype(int)
             + (rrr_s > thr).astype(int) + (c < sal).astype(int) + (c < mal).astype(int))
    short_open = (pts_s >= 5).to_numpy()
    s1, s2 = c.rolling(int(p["sma1"])).mean(), c.rolling(int(p["sma2"])).mean()
    s1s, s2s = c.rolling(int(p["sma1_s"])).mean(), c.rolling(int(p["sma2_s"])).mean()
    con_f = (_xu(c, s1) & _xu(c, s2)).to_numpy()
    con_g = (c < lo.rolling(int(p["sl_len_l"])).min().shift(1) * (1 - 0.005)).to_numpy()
    con_6 = (_xo(c, s1s) & _xo(c, s2s)).to_numpy()
    con_7 = (c > h.rolling(int(p["sl_len_s"])).max().shift(1) * (1 + 0.005)).to_numpy()
    cv, bd = c.to_numpy(dtype=float), base_d.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and i + 1 < m:
            if short_open[i]:
                se[i], pos = True, -1                    # the short entry comes last and stands
            elif long_open[i]:
                le[i], pos = True, 1
        elif pos == 1 and (con_f[i] or con_g[i] or short_open[i]) and cv[i] <= bd[i]:
            lx[i], pos = True, 0
        elif pos == -1 and (con_6[i] or con_7[i] or long_open[i]) and cv[i] >= bd[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

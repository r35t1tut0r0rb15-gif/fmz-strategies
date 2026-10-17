"""Ichimoku trend entries with entry-price exits, broker days, long only: Tenkan at or above Kijun, a positive 25-bar
momentum, the close above the cloud drawn for today with a bullish future cloud, the close not stretched (under the Tenkan
+ 2 ATR and the Kijun + 3 ATR) and both lines above the cloud go long; a bearish state, a close under the Kijun after a
30 % gain, or a close 7 % under the entry price closes it.
Port of FMZ strategy #435158 "Ichimoku Trading Strategy With Money Management" (İchimoku Strategy With Money Management).

FMZ source id: 435158

Source
    https://www.fmz.com/strategy/435158 (PineScript v5, FMZ last modified 2023-12-12 17:32:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 145-238), Tenkan 9, Kijun 26, Senkou B 52, offsets 26; ATR 14; exits +30 % / -7 % of the entry price; dates 1980-2100
    bullish = tenkan >= kijun and mom(close, 25) > 0 and close > max(spanA[25], spanB[25]) and spanA > spanB and close > tenkan and close - tenkan < 2 atr and close - kijun < 3 atr and tenkan > ssAbove and kijun > ssAbove -> entry long
    bearish = tenkan <= kijun and close < ssAbove and mom < 0 or close < kijun or close < ssAbove;  bearish or (close > 1.3 entry and close < kijun) or close < 0.93 entry -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry price is the trade's fill price (strategy.opentrades.entry_price), known from the
      fill bar on; the exits are tested on bar closes (close-based exit signals). "Today's cloud" is
      the spans computed 25 bars ago, as the code reads them. An entry while long is ignored; the
      closes act on the position held on the bar. The date window is the author's: dropped.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes against the fill price.
    2 generic: PASS, Ichimoku lines, ATR stretch limits and percent exits.
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

NAME = "fmz_435158_ichimoku_entry_price_exits_long"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gain_exit": [1.30, 1.15],
    "loss_exit": [0.93, 0.85],
}
DEFAULT_PARAMS = {"ts": 9, "ks": 26, "ssb": 52, "cs_off": 26, "ss_off": 26, "gain_exit": 1.30, "loss_exit": 0.93}


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
    mid = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    ten, kij, sb = mid(int(p["ts"])), mid(int(p["ks"])), mid(int(p["ssb"]))
    sa = (ten + kij) / 2
    k = int(p["ss_off"]) - 1
    above = np.maximum(sa.shift(k), sb.shift(k))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    mom = c - c.shift(int(p["cs_off"]) - 1)
    bull = ((ten >= kij) & (mom > 0) & (c > above) & (sa > sb) & (c > ten) & (c - ten < 2 * atr)
            & (c - kij < 3 * atr) & (ten > above) & (kij > above)).to_numpy()
    bear = (((ten <= kij) & (c < above) & (mom < 0)) | (c < kij) | (c < above)).to_numpy()
    cv, kv, ov = c.to_numpy(dtype=float), kij.to_numpy(), o.to_numpy(dtype=float)
    g, l_ = float(p["gain_exit"]), float(p["loss_exit"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ep = 0, np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pos == 1 and np.isnan(ep):
                ep = ov[i]                               # the fill price (this bar's open)
            if pos == 1 and (bear[i] or (cv[i] > g * ep and cv[i] < kv[i]) or cv[i] < l_ * ep):
                lx[i], pos, ep = True, 0, np.nan
            elif pos == 0 and bull[i]:
                le[i], pos, ep = True, 1, np.nan
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}

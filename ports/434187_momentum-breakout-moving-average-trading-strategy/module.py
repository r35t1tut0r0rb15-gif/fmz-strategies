"""RSI 14 against RSI 21 with a price-versus-ATR test, broker days: the RSI 14 above the RSI 21 with the close above 1.5
ATR 14 goes long and the RSI 14 falling below the RSI 21 closes it; the short side needs the close under 1.5 ATR, which
a normal price never is, so in practice the strategy is long only.
Port of FMZ strategy #434187 "Momentum Breakout Moving Average Trading Strategy" (RSI, SuperTrend, and ATR Strategy).

FMZ source id: 434187

Source
    https://www.fmz.com/strategy/434187 (PineScript v5, FMZ last modified 2023-12-04 15:57:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-180), RSI 14 / 21; "supertrend" = 1.5 x ATR 14
    supertrend = atr(14) x 1.5 (a volatility, compared with the price);  long = rsi14 > rsi21 and close > supertrend;  short = rsi14 < rsi21 and close < supertrend
    long -> entry long;  short -> entry short;  long position and (rsi14 < rsi21 or close < supertrend) -> close;  short position and (rsi14 > rsi21 or close > supertrend) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the "supertrend" is an ATR, so close > 1.5 ATR holds whenever the price is more than
      1.5 ATR above zero (always, on every instrument the project carries): the shorts never fire and
      the price test never closes a long. Ported unchanged.
    * Each bar: the closes act on the position held at the start of the bar, then an entry wins.
      REVERSAL INTENDED (in principle). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI crosses (the price-versus-ATR test is ported as written).
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

NAME = "fmz_434187_rsi14_21_atr_test"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_fast": [14, 7],
    "rsi_slow": [21, 42],
}
DEFAULT_PARAMS = {"rsi_fast": 14, "rsi_slow": 21, "atr_len": 14, "mult": 1.5}


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
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r1, r2 = _rsi(c, int(p["rsi_fast"])), _rsi(c, int(p["rsi_slow"]))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    st = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["mult"])
    rl, rs_ = (r1 > r2).to_numpy(), (r1 < r2).to_numpy()
    sl, ss = (c > st).to_numpy(), (c < st).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and (rs_[i] or ss[i]):
            pos = 0
        elif pos == -1 and (rl[i] or sl[i]):
            pos = 0
        if rl[i] and sl[i]:
            pos = 1
        elif rs_[i] and ss[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}

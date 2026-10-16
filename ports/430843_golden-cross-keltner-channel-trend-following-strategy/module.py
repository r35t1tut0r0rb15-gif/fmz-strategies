"""Keltner breakouts in the golden-cross trend, broker days: the close crossing above the SMA 21 + 1 ATR 10 with the EMA 50
above the EMA 200 goes long (mirror short); a close beyond 4 ATR 21 from the basis takes profit and a close back past
the basis -/+ 1 ATR 21 stops out.
Port of FMZ strategy #430843 "Golden Cross Keltner Channel Trend Following Strategy" (Keltner Channel Strategy by OversoldPOS).

FMZ source id: 430843

Source
    https://www.fmz.com/strategy/430843 (PineScript v5, FMZ last modified 2023-11-02 14:31:10).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 184-295), SMA 21 basis, entry 1 x ATR 10, profit 4 x ATR 21, exit -1 x ATR 21, EMA 50 / 200
    crossover(close, basis + atr10) and ema50 > ema200 -> entry long;  crossunder(close, basis - atr10) and ema50 < ema200 -> entry short
    close > basis + 4 atr21 or close < basis - 1 atr21 -> close long
    close < basis - 4 atr21 or close > basis + 1 atr21 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are close tests with strategy.close (market exits at the next open): exit signals.
      A close written after an entry acts on the position held at the start of the bar unless the
      bar's entry reverses it.
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, Keltner channels and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 10 % of equity stored in original_sizing.txt.
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

NAME = "fmz_430843_keltner_golden_cross"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "profit_mult": [4.0, 2.0],
}
DEFAULT_PARAMS = {"length": 21, "entry_mult": 1.0, "profit_mult": 4.0, "exit_mult": -1.0, "ma_short": 50,
                  "ma_long": 200}


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


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    a10, an = _atr(bars_df, 10), _atr(bars_df, n)
    up_e, dn_e = basis + p["entry_mult"] * a10, basis - p["entry_mult"] * a10
    trend_up = c.ewm(span=int(p["ma_short"]), adjust=False).mean() > c.ewm(span=int(p["ma_long"]), adjust=False).mean()
    trend_dn = c.ewm(span=int(p["ma_short"]), adjust=False).mean() < c.ewm(span=int(p["ma_long"]), adjust=False).mean()
    le = ((c > up_e) & (c.shift(1) <= up_e.shift(1)) & trend_up).to_numpy()
    se = ((c < dn_e) & (c.shift(1) >= dn_e.shift(1)) & trend_dn).to_numpy()
    lx = ((c > basis + p["profit_mult"] * an) | (c < basis + p["exit_mult"] * an)).to_numpy()
    sx = ((c < basis - p["profit_mult"] * an) | (c > basis - p["exit_mult"] * an)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if le[i]:
            pos = 1
        if se[i]:
            pos = -1
        if start == 1 and pos == 1 and lx[i]:
            pos = 0
        if start == -1 and pos == -1 and sx[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

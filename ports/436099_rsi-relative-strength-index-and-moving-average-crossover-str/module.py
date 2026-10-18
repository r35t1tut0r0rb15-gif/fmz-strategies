"""RSI against its SMA with extreme overrides, broker days: the RSI 13 crossing over its SMA 9 goes long, under it goes short; an RSI over 90 goes short and
under 10 goes long (the overrides are sent after the cross rules, as written); every signal first closes the position (reversal).
Port of FMZ strategy #436099 "RSI指标与平均线交叉策略Relative-Strength-Index-and-Moving-Average-Crossover-Strategy" (Relative Strength Index (RSI + MA cross)).

FMZ source id: 436099

Source
    https://www.fmz.com/strategy/436099 (PineScript v3, FMZ last modified 2023-12-21 11:30:27).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 140-172), RSI 13, SMA 9 of the RSI; extremes 90 / 10
    close_all on any cross(rsi, ma) and on rsi > 90 or rsi < 10;  entry "Short Overbought" (rsi > 90), "Buy Overbought" (rsi < 10), "Long Cross" (rsi crosses over ma while above it), "Short Cross" (crosses under while below it)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every signal is a close_all followed by an entry, so the position reverses; while the RSI stays over
      90 (or under 10) Pine closes and re-enters at every bar (a trade per bar): not modelled, the
      position is simply kept. When two entries fire on one bar the last sent stands (cross entries after the
      extreme entries). The date range input is the author's window: dropped. REVERSAL INTENDED. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI cross and extremes.
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

NAME = "fmz_436099_rsi_ma_cross_extremes"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [13, 7],
    "ma_len": [9, 5],
}
DEFAULT_PARAMS = {"len": 13, "ma_len": 9, "ob": 90, "os": 10}


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
    c = bars_df["close"]
    n = int(p["len"])
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=c.index)
    ma = rsi.rolling(int(p["ma_len"])).mean()
    cross_up = ((rsi > ma) & (rsi.shift(1) <= ma.shift(1))).fillna(False).to_numpy()
    cross_dn = ((rsi < ma) & (rsi.shift(1) >= ma.shift(1))).fillna(False).to_numpy()
    ob = (rsi > float(p["ob"])).fillna(False).to_numpy()
    os_ = (rsi < float(p["os"])).fillna(False).to_numpy()
    m = len(ob)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if ob[i]:
            q = -1
        if os_[i]:
            q = 1
        if cross_up[i]:
            q = 1
        if cross_dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}

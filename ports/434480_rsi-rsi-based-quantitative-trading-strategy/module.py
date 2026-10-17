"""Fast / slow RSI crosses with signal-close exits, broker days: the EMA-based RSI 55 crossing above the RSI 126 goes long,
crossing below goes short (each also closes the other side); a long is closed when a bar's high reaches 0.9 % above the
last long signal's close or its low 3 % below it, a short mirrors that.
Port of FMZ strategy #434480 "基于RSI的量化交易策略RSI-Based-Quantitative-Trading-Strategy" (Relative Strength Index).

FMZ source id: 434480

Source
    https://www.fmz.com/strategy/434480 (PineScript v2, FMZ last modified 2023-12-06 17:17:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 110-144), RSI 55 / 126 (EMA of gains / losses); TP 0.9 %, SL 3 % of the signal close
    long = crossover(rsi55, rsi126);  short = crossunder;  vall = valuewhen(long, close, 0);  vals = valuewhen(short, close, 0)
    high >= vall (1 + 0.9 %) or low <= vall (1 - 3 %) or short -> close long;  low <= vals (1 - 0.9 %) or high >= vals (1 + 3 %) or long -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSIs smooth gains and losses with EMAs (not Wilder), as written. The exits are tested on
      the bar's own high / low against the signal close and act at the next open: close-based exit
      signals, not broker stops (no mark). They act on the position held on the bar; an entry on the
      same bar wins (the short entry is issued last). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI crosses and percent exit signals.
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

NAME = "fmz_434480_dual_rsi_cross_signal_exits"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slen": [55, 14],
    "tp": [0.009, 0.03],
}
DEFAULT_PARAMS = {"slen": 55, "llen": 126, "tp": 0.009, "sl": 0.03}


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


def _ema_rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(span=n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(span=n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    return r.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r1, r2 = _ema_rsi(c, int(p["slen"])), _ema_rsi(c, int(p["llen"]))
    lg = ((r1 > r2) & (r1.shift(1) <= r2.shift(1))).to_numpy()
    sh = ((r1 < r2) & (r1.shift(1) >= r2.shift(1))).to_numpy()
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, vall, vals = 0, np.nan, np.nan
    for i in range(m):
        if lg[i]:
            vall = cv[i]
        if sh[i]:
            vals = cv[i]
        new = pos
        if pos == 1 and (hv[i] >= vall * (1 + tp) or lv[i] <= vall * (1 - sl) or sh[i]):
            new = 0
        if pos == -1 and (lv[i] <= vals * (1 - tp) or hv[i] >= vals * (1 + sl) or lg[i]):
            new = 0
        if lg[i]:
            new = 1
        if sh[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}

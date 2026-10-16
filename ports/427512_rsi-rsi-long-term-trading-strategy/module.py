"""Bar-body momentum, broker days: three large up-bodies with a small latest body go long; three large
down-bodies after a large down-move 4-6 days ago, with an RSI filter, go short (always in the market
after the first signal).
Port of FMZ strategy #427512 "RSI Long Term Trading Strategy".

FMZ source id: 427512

Source
    https://www.fmz.com/strategy/427512 (PineScript v2, FMZ last modified 2023-09-21 20:54:08).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 192-211)
    rsi = rsi(sum(close, 20) + sum(open, 20), 20); s3 = sum((close - open) x 100000, 3)
    up = (close - open) x 100000 < 35; down = sum of bodies of bars [4], [5], [6] x 100000 < -400
    s3 > 350 and up -> entry long; s3 < -200 and down and rsi > 30.1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the thresholds are 5-digit FX points (x 100000: 350 points = 35 pips). They
      become multiples of Wilder ATR(14) of the same bar: 350 -> 0.5, 35 -> 0.05, -200 -> -0.3,
      -400 -> -0.6 ATR (on a daily EUR/USD ATR of about 70 pips; judgement, stated before any
      backtest). The RSI of the 20-bar sums is dimensionless and kept.
    * The max-intraday-loss risk rule is commented out (and would be sizing).
    * strategy.entry reverses: REVERSAL INTENDED (no other exit).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, point thresholds -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427512_body_momentum_daily"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "up_sum_atr": [0.5, 1.0],
    "down_sum_atr": [0.3, 0.6],
    "atr_length": [14, 28],
}
DEFAULT_PARAMS = {"up_sum_atr": 0.5, "small_body_atr": 0.05, "down_sum_atr": 0.3, "down_move_atr": 0.6,
                  "rsi_floor": 30.1, "atr_length": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    ch = x.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["atr_length"]))
    body = c - o
    s3 = body.rolling(3).sum() / atr
    small = body / atr < p["small_body_atr"]
    down = (body.shift(6) + body.shift(5) + body.shift(4)) / atr < -p["down_move_atr"]
    rsi = _rsi(c.rolling(20).sum() + o.rolling(20).sum(), 20)
    long_c = ((s3 > p["up_sum_atr"]) & small).to_numpy()
    short_c = ((s3 < -p["down_sum_atr"]) & down).to_numpy() & (rsi > p["rsi_floor"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

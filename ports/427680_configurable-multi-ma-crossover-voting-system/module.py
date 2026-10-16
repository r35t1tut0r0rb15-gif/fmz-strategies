"""Multi-MA vote, broker days, long only: go long when every fast/slow WMA pair of the high (2x4, 3x5,
4x6) is bullish; while held, close once the pairs are no longer unanimous and the bar's range has
touched the target (close + 10 ATR) or the stop (close - 5 ATR) set at the signal.
Port of FMZ strategy #427680 "Configurable Multi MA Crossover Voting System" (levieux).

FMZ source id: 427680

Source
    https://www.fmz.com/strategy/427680 (PineScript v5, FMZ last modified 2023-09-23 15:52:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 214-267), config "2x4,3x5,4x6", source high, WMA, ATR 14, 10 / 5
    longVotes = count of pairs with ma(high, fast) > ma(high, slow)
    longCondition = all pairs vote long and flat -> entry long
    profitPrice = close + 10 atr, lossPrice = close - 5 atr, frozen while long
    longVotes < count and long and (high > profitPrice or low < lossPrice) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are frozen from the signal bar (position_size is still 0 there), as written.
    * The close is an exit signal on the bar's range, filled at the next open (it is not a stop
      order: Pine's strategy.close is a market order), and only when the vote is not unanimous.
    * `ma_type` 1 = WMA (default), 2 = SMA; the VWMA option uses volume and is not ported (check 8).
    * The pair config is fixed at the source's default. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the VWMA option is left out.
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427680_multi_ma_vote_atr_exit_long"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

PAIRS = ((2, 4), (3, 5), (4, 6))
GRID = {
    "profit_atr": [10.0, 5.0],
    "loss_atr": [5.0, 2.5],
    "ma_type": [1, 2],
}
DEFAULT_PARAMS = {"profit_atr": 10.0, "loss_atr": 5.0, "ma_type": 1, "atr_period": 14}


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


def _ma(x, n, kind):
    if kind == 2:
        return x.rolling(n).mean()
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    kind = int(p["ma_type"])
    votes = sum((_ma(h, f, kind) > _ma(h, s, kind)).astype(int) for f, s in PAIRS).to_numpy()
    allv = votes == len(PAIRS)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["atr_period"])).to_numpy()
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, pp, lp = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:                       # long from the fill bar on
            if not allv[i] and (hv[i] > pp or lv[i] < lp):
                lx[i] = True
                pos = 0
                continue
        if pos == 0 and allv[i]:
            tp_, sl_ = cv[i] + p["profit_atr"] * atr[i], cv[i] - p["loss_atr"] * atr[i]
            if tp_ > 0:
                le[i] = True
                pos, entry_i, pp, lp = 1, i + 1, tp_, sl_
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}

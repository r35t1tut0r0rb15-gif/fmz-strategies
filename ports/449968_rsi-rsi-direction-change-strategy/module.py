"""One-bar RSI 14 jumps, daily bars: an RSI rise of 10 or more goes long, a fall of 10 or more (or a 1 % price drop) goes short; any RSI move of 5 or more closes a held position; reversing.
Port of FMZ strategy #449968 "RSI变动方向改变策略-RSI-Direction-Change-Strategy" (RSI Direction Change).

FMZ source id: 449968

Source
    https://www.fmz.com/strategy/449968 (PineScript v5, FMZ last modified 2024-04-30 17:29:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-153), RSI 14; change threshold 10; exit threshold 5; price reverse 1 %
    rsi - rsi[1] >= 10 -> entry Buy;  rsi - rsi[1] <= -10 or close / close[1] - 1 <= -1 % -> entry Sell;  |rsi change| >= 5 or sell -> close Buy;  |rsi change| >= 5 or buy -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in the script's order: a close acts only on a position held into the bar and not
      reversed by that bar's entry, so a fresh entry survives its own bar and a held position closes on
      the next RSI move of 5 or more. When both entries fire, the later short wins (as #437773).
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI jumps with an RSI-move exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449968_rsi_jump_entry_rsi_move_exit_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "change": [10.0, 15.0],
    "exit_move": [5.0, 10.0],
}
DEFAULT_PARAMS = {"change": 10.0, "exit_move": 5.0, "rsi_len": 14, "price_rev": 1.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ch = r - r.shift(1)
    chg, ex = float(p["change"]), float(p["exit_move"])
    with np.errstate(invalid="ignore"):
        buy = (ch >= chg).to_numpy()
        sell = ((ch <= -chg) | ((c - c.shift(1)) / c.shift(1) * 100 <= -float(p["price_rev"]))).to_numpy()
        move = (ch.abs() >= ex).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            le[i], new = True, 1
        if sell[i] and new != -1:
            se[i], le[i], new = True, False, -1
        if (move[i] or sell[i]) and pos == 1 and new == 1:     # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if (move[i] or buy[i]) and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}

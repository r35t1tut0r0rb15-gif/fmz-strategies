"""HPotter displaced EMA envelope with an ATR trailing-line filter, broker days: the envelope side turns up after a close
above the EMA 9 of 13 bars ago plus 0.5 % and down after a close below it less 0.5 %; while it is up a close above the
2 x ATR 15 trailing line goes (or stays) long and a close under it closes a long; the down side mirrors that for shorts.
Port of FMZ strategy #434708 "Quantitative Trading Based on Moving Average Envelope and ATR Trailing Stop" (Moving Average Displaced Envelope & ATRTS).

FMZ source id: 434708

Source
    https://www.fmz.com/strategy/434708 (PineScript v5, FMZ last modified 2023-12-08 15:53:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 178-229), EMA 9 on close, +/- 0.5 %, displacement 13; ATR TS 15 x 2; direction Both; reverse false
    pos = close < bott ? -1 : close > top ? 1 : pos[1];  trail = Vervoort ATR trailing stop (close vs trail[1], 2 x atr(15))
    pos 1: close > trail -> entry long, else (long) -> close_all;  pos -1: close < trail -> entry short, else (short) -> close_all;  pos 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "else" branches close only a position on the same side (a short stays open while the
      envelope side is up and the close is under the line), as written; the ATR filter input is
      unused (the filter always applies). The trailing line is the strategy's signal line on
      closes (no broker stop). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a percent envelope and an ATR trailing line.
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

NAME = "fmz_434708_made_atr_trail_filter"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pct": [0.5, 1.0],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"period": 9, "pct": 0.5, "disp": 13, "atr_len": 15, "atr_mult": 2.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = c.ewm(span=int(p["period"]), adjust=False).mean().shift(int(p["disp"]))
    pc = float(p["pct"])
    top, bott = (e * (100 + pc) / 100).to_numpy(), (e * (100 - pc) / 100).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    nl = float(p["atr_mult"]) * tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    tgt = np.zeros(m, dtype=np.int8)
    side, pos = 0, 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            t1 = ts[i - 1] if i > 0 and not np.isnan(ts[i - 1]) else 0.0
            cp = cv[i - 1] if i > 0 else np.nan
            if cv[i] > t1 and cp > t1:
                ts[i] = max(t1, cv[i] - nl[i])
            elif cv[i] < t1 and cp < t1:
                ts[i] = min(t1, cv[i] + nl[i])
            else:
                ts[i] = cv[i] - nl[i] if cv[i] > t1 else cv[i] + nl[i]
            if cv[i] < bott[i]:
                side = -1
            elif cv[i] > top[i]:
                side = 1
            new = pos
            if side == 1:
                if cv[i] > ts[i]:
                    new = 1
                elif pos > 0:
                    new = 0
            elif side == -1:
                if cv[i] < ts[i]:
                    new = -1
                elif pos < 0:
                    new = 0
            else:
                new = 0
            tgt[i] = new
            pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}

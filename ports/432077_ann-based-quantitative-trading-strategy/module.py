"""A fixed small neural network on the change from the previous day's ohlc4, 1-hour bars: the network's output above zero
holds a long, below zero holds a short (the weights are the author's, hard-coded).
Port of FMZ strategy #432077 "ANN based Quantitative Trading Strategy" (ANN Strategy v2).

FMZ source id: 432077

Source
    https://www.fmz.com/strategy/432077 (PineScript v2, FMZ last modified 2023-11-14 11:22:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 133-207), 1 input, 5 / 33 tanh units, 1 output; timeframe 1D
    x = (ohlc4 - security(tickerid, '1D', ohlc4[1])) / security(...);  l1 = tanh(x w1), l2 = tanh(l1 W2), out = tanh(l2 w3)
    buying = out > 0 ? true : out < 0 ? false : buying[1];  buying -> entry long, else entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('1D', ohlc4[1]) without lookahead is read as the last completed broker day's ohlc4 (as
      #428790), built inside simulate() from the port's own bars; "today" is the bar's own ohlc4. The
      weights are copied from the source (parsed, not retyped). The threshold input is unused, as
      written: no parameter reaches the orders (1 trial).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a fixed function of a percentage change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily ohlc4 (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432077_fixed_ann_daily_change"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}

W1 = [0.8446488687, -0.5674069006, 0.8676766445, 0.5200611473, -0.2215499554]
W2 = [
    [0.3341657935, -2.0060003664, 0.8606354375, 0.9184846912, -0.8531172267],
    [-0.0394076437, -0.4720374911, 0.2900968524, 1.0653326022, 0.3000188806],
    [-0.559307785, -0.9353655177, 1.2133832962, 0.1952686024, 0.8552068166],
    [-0.4293220754, 0.8484259409, -0.7154087313, 0.1102971055, 0.2279392724],
    [0.9111779155, 0.2801691115, 0.0039982713, -0.5648257117, 0.3281705155],
    [-0.2963954503, 0.4046532178, 0.2460580977, 0.6608675819, -0.8732022547],
    [0.8810811932, 0.6903706878, -0.5953059103, -0.3084040686, -0.4038498853],
    [-0.5687101164, 0.2736758588, -0.2217360382, 0.8742950972, 0.2997583987],
    [0.0708459913, 0.8221730616, -0.7213265567, -0.3810462836, 0.0503867753],
    [0.4880140595, 0.9466627196, 1.0163097961, -0.9500386514, -0.6341709382],
    [1.3402207103, 0.0013395288, 3.4813009133, -0.8636814677, 41.3171047132],
    [1.2388217292, -0.6520886912, 0.3508321737, 0.6640560714, 1.5936220597],
    [-0.1800525171, -0.2620989752, 0.056675277, -0.5045395315, 0.2732553554],
    [-0.7776331454, 0.1895231137, 0.5384918862, 0.093711904, -0.3725627758],
    [-0.3181583022, 0.2467979854, 0.4341718676, -0.7277619935, 0.1799381758],
    [-0.5558227731, 0.3666152536, 0.1538243225, -0.8915928174, -0.7659355684],
    [0.6111516061, -0.5459495224, -0.5724238425, -0.8553500765, -0.8696190472],
    [0.6843667454, 0.408652181, -0.8830470112, -0.8602324935, 0.1135462621],
    [-0.1569048216, -1.4643247888, 0.5557152813, 1.0482791924, 1.4523116833],
    [0.5207514017, -0.2734444192, -0.3328660936, -0.7941515963, -0.3536051491],
    [-0.4097807954, 0.3198619826, 0.461681627, -0.1135575498, 0.7103339851],
    [-0.8725014237, -1.0312091401, 0.2267643037, -0.6814258121, 0.7524828703],
    [-0.3986855003, 0.4962556631, -0.7330224516, 0.7355772164, 0.3180141739],
    [-1.083080442, 1.8752543187, 0.3623326265, -0.348145191, 0.1977935038],
    [-0.0291290625, 0.0612906199, 0.1219696687, -1.0273685429, 0.0872219768],
    [0.931791094, -0.313753684, -0.3028724837, 0.7387076712, 0.3806140391],
    [0.2630619402, -1.9827996702, -0.7741413496, 0.1262957444, 0.2248777886],
    [-0.2666322362, -1.124654664, 0.7288282621, -0.1384289204, 0.2395966188],
    [0.6611845175, 0.0466048937, -0.1980999993, 0.8152350927, 0.0032723211],
    [-0.3150344751, 0.1391754608, 0.5462816249, -0.7952302364, -0.7520712378],
    [-0.0576916066, 0.3678415302, 0.6802537378, 1.1437036331, -0.8637405666],
    [0.7016273068, 0.3978601709, 0.3157049654, -0.2528455662, -0.8614146703],
    [1.1741126834, -1.4046408959, 1.2914477803, 0.9904052964, -0.6980155826],
]
W3 = [-0.1366382003, 0.8161960822, -0.9458773183, 0.4692969576, 0.0126710629, -0.0403001012, -0.0116244898,
      -0.4874816289, -0.6392241448, -0.410338398, -0.1181027081, 0.1075562037, -0.5948728252, 0.5593677345,
      -0.3642935247, -0.2867603217, 0.142250271, -0.0535698019, -0.034007685, -0.3594532426, 0.2551095195,
      0.4214344983, 0.8941621336, 0.6283377368, -0.7138020667, -0.1426738249, 0.172671223, 0.0714824385,
      -0.3268182144, -0.0078989755, -0.2032828145, -0.0260631534, 0.4918037012]


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    lab = broker_day(bars_df.index)
    g = pd.DataFrame({"o": o.to_numpy(), "h": h.to_numpy(), "l": lo.to_numpy(), "c": c.to_numpy()}, index=lab)
    d = g.groupby(level=0).agg({"o": "first", "h": "max", "l": "min", "c": "last"})
    d4 = ((d["o"] + d["h"] + d["l"] + d["c"]) / 4).shift(1)            # the last completed broker day
    y = d4.reindex(lab).to_numpy()
    today = ((o + h + lo + c) / 4).to_numpy()
    x = (today - y) / y
    l1 = np.tanh(np.outer(x, np.asarray(W1)))
    l2 = np.tanh(l1 @ np.asarray(W2).T)
    out = np.tanh(l2 @ np.asarray(W3))
    m = len(out)
    tgt = np.zeros(m, dtype=np.int8)
    buying = False
    for i in range(m):
        if out[i] > 0:
            buying = True
        elif out[i] < 0:
            buying = False
        tgt[i] = 1 if buying else -1
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}

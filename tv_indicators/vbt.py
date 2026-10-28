"""vectorbt ``IndicatorFactory`` classes for every registered indicator.

    from tv_indicators.vbt import BBANDS, RSI
    bb = BBANDS.run(close, length=[20, 50], mult=[2.0, 2.5], param_product=True)
    entries = bb.close_crossed_below(bb.lower)   # auto-generated helpers
    rsi = RSI.run(close, length=14)

Class names are the registry names (``tv_indicators.REGISTRY``). Inputs that
are optional in the function API (``volume`` for MA/BBANDS/BBWP, only needed
for VWMA) are left out of the factory and filled with NaN.
"""

import inspect

import numpy as np
import vectorbt as vbt

from ._core import REGISTRY, f2d


def _make_factory(name, public):
    sig = inspect.signature(public.core)
    required = [i for i in public.inputs if sig.parameters[i].default is inspect.Parameter.empty]
    params = list(public.params)
    n_req = len(required)

    def apply_func(*args):
        given = dict(zip(required, args[:n_req]))
        arrays = []
        for inp in public.inputs:
            if inp in given:
                arrays.append(f2d(given[inp]))
            else:
                arrays.append(np.full(arrays[0].shape, np.nan))
        res = public.core(*arrays, **dict(zip(params, args[n_req:])))
        return res

    factory = vbt.IndicatorFactory(
        class_name=name,
        short_name=name.lower(),
        input_names=required,
        param_names=params,
        output_names=list(public.outputs),
    )
    cls = factory.from_apply_func(apply_func, **public.params)
    cls.__doc__ = public.core.__doc__
    return cls


FACTORIES = {name: _make_factory(name, fn) for name, fn in REGISTRY.items()}
globals().update(FACTORIES)

__all__ = sorted(FACTORIES)

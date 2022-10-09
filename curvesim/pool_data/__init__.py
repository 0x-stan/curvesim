__all__ = ["from_address", "from_symbol", "get", "queries", "Pool", "MetaPool"]

from ..pool.metapool import MetaPool
from ..pool.pool import Pool
from . import queries
from .queries import from_address, from_symbol


def get(address_or_symbol, chain="mainnet", src="cg", balanced=(True, True), days=60):
    if address_or_symbol.startswith("0x"):
        from_x = from_address
    else:
        from_x = from_symbol

    params = from_x(address_or_symbol, chain, balanced=balanced)

    pool_data = PoolData(params)

    return pool_data


class PoolData(dict):
    def pool(self, balanced=(True, True)):
        def bal(kwargs, balanced):
            reserves = kwargs.pop("reserves")
            if not balanced:
                kwargs.update({"D": reserves})
            return kwargs

        kwargs = bal(self["init_kwargs"].copy(), balanced[0])

        if self["basepool"]:
            bp_kwargs = bal(self["basepool"]["init_kwargs"], balanced[1])
            kwargs.update({"basepool": Pool(**bp_kwargs)})
            pool = MetaPool(**kwargs)
        else:
            pool = Pool(**kwargs)

        pool.metadata = self

        return pool

    def coins(self):
        if not self["basepool"]:
            c = self["coins"]["addresses"]
        else:
            c = self["coins"]["addresses"][:-1] + self["basepool"]["coins"]["addresses"]
        return c

    def volume(self, days=60):
        address = self["address"]
        chain = self["chain"]

        bp = None
        if self["basepool"]:
            bp = self["basepool"]["address"]

        vol = queries.volume(address, chain, bp_address=bp, days=days)

        return vol

    def redemption_prices(self, n=1000):
        address = self["address"]
        chain = self["chain"]

        r = queries.redemption_prices(address, chain, n=n)

        return r

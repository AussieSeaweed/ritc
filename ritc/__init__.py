"""``ritc`` - A Python library for interactions with Rotman Interactive
Trader Market Simulator Client Application via REST exchange API
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from time import sleep
from typing import Any, Literal, Optional, Protocol, Union, overload

from requests import Session

__all__ = (
    'Asset',
    'CancellationResult',
    'Case',
    'Error',
    'Limit',
    'News',
    'Order',
    'RIT',
    'Security',
    'SuccessResult',
    'Tender',
    'Ticker',
    'Trader',
)


@dataclass(frozen=True)
class _NestedSequence(Sequence[Any]):
    __sequence: Sequence[Any]

    @overload
    def __getitem__(self, key: int) -> Any:
        pass

    @overload
    def __getitem__(self, key: slice) -> Sequence[Any]:
        pass

    def __getitem__(self, key: Union[int, slice]) -> Any:
        item = self.__sequence[key]

        if not isinstance(item, str) and isinstance(item, Sequence):
            item = _NestedSequence(item)
        elif isinstance(item, Mapping):
            item = _NestedMapping(item)

        return item

    def __len__(self) -> int:
        return len(self.__sequence)

    def __repr__(self) -> str:
        return repr(self.__sequence)


@dataclass(frozen=True)
class _NestedMapping(Mapping[Any, Any]):
    __mapping: Mapping[Any, Any]

    def __getitem__(self, key: Any) -> Any:
        item = self.__mapping[key]

        if not isinstance(item, str) and isinstance(item, Sequence):
            item = _NestedSequence(item)
        elif isinstance(item, Mapping):
            item = _NestedMapping(item)

        return item

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__mapping)

    def __len__(self) -> int:
        return len(self.__mapping)

    def __getattr__(self, name: Any) -> Any:
        return self[name]

    def __repr__(self) -> str:
        return repr(self.__mapping)


class Error(Protocol):
    """This class is for error data."""
    code: str
    message: str
    wait: float


class Case(Protocol):
    """This class is for cases."""

    class Status(str, Enum):
        """This class is for case statuses."""
        ACTIVE: str = 'ACTIVE'
        PAUSED: str = 'PAUSED'
        STOPPED: str = 'STOPPED'

    name: str
    period: int
    tick: int
    ticks_per_period: int
    total_periods: int
    status: Status
    is_enforce_trading_limits: bool


class Trader(Protocol):
    """This class is for traders."""
    trader_id: str
    first_name: str
    last_name: str
    nlv: float


class Limit(Protocol):
    """This class is for limits."""
    name: str
    gross: float
    net: float
    gross_limit: int
    net_limit: int
    gross_fine: float
    net_fine: float


class News(Protocol):
    """This class is for news."""
    news_id: int
    period: int
    tick: int
    ticker: str
    headline: str
    body: str


class Ticker(Protocol):
    """This class is for tickers."""

    class Quantity(Protocol):
        """This class is for ticker quantities."""
        ticker: str
        quantity: float

    class Price(Protocol):
        """This class is for ticker prices."""
        ticker: str
        price: float


class Asset(Protocol):
    """This class is for assets."""

    class Type(str, Enum):
        """This class is for asset types."""
        CONTAINER: str = 'CONTAINER'
        PIPELINE: str = 'PIPELINE'
        SHIP: str = 'SHIP'
        REFINERY: str = 'REFINERY'
        POWER_PLANT: str = 'POWER_PLANT'
        PRODUCER: str = 'PRODUCER'

    class History(Protocol):
        """This class is for asset histories."""
        ticker: str
        tick: int
        action: str
        cost: float
        convert_from: Sequence[Ticker.Quantity]
        convert_to: Sequence[Ticker.Quantity]
        convert_from_price: Sequence[Ticker.Price]
        convert_to_price: Sequence[Ticker.Price]

    class Lease(Protocol):
        """This class is for asset leases."""
        id: int
        ticker: str
        type: Asset.Type
        start_lease_period: int
        start_lease_tick: int
        next_lease_period: int
        next_lease_tick: int
        convert_from: Sequence[Ticker.Quantity]
        convert_to: Sequence[Ticker.Quantity]
        containment_usage: int

    ticker: str
    type: Type
    description: str
    total_quantity: int
    available_quantity: int
    lease_price: float
    convert_from: Sequence[Ticker.Quantity]
    convert_to: Sequence[Ticker.Quantity]
    containment: Ticker.Quantity
    ticks_per_conversion: int
    ticks_per_lease: int
    is_available: bool
    start_period: int
    stop_period: int


class Order(Protocol):
    """This class is for orders."""

    class Type(str, Enum):
        """This class is for order types."""
        MARKET: str = 'MARKET'
        LIMIT: str = 'LIMIT'

    class Action(str, Enum):
        """This class is for order actions."""
        BUY: str = 'BUY'
        SELL: str = 'SELL'

    class Status(str, Enum):
        """This class is for order statuses."""
        OPEN: str = 'OPEN'
        TRANSACTED: str = 'TRANSACTED'
        CANCELLED: str = 'CANCELLED'

    order_id: int
    period: int
    tick: int
    trader_id: str
    ticker: str
    type: Type
    quantity: float
    action: Action
    price: float
    quantity_filled: float
    vwap: float
    status: Status


class SuccessResult(Protocol):
    """This class is for success results."""
    success: bool


class CancellationResult(Protocol):
    """This class is for cancellation requests."""
    cancelled_order_ids: Sequence[int]


class Security(Protocol):
    """This class is for securities."""

    class Type(str, Enum):
        """This class is for security types."""
        SPOT: str = 'SPOT'
        FUTURE: str = 'FUTURE'
        INDEX: str = 'INDEX'
        OPTION: str = 'OPTION'
        STOCK: str = 'STOCK'
        CURRENCY: str = 'CURRENCY'
        BOND: str = 'BOND'
        RATE: str = 'RATE'
        FORWARD: str = 'FORWARD'
        SWAP: str = 'SWAP'
        SWAP_BOM: str = 'SWAP_BOM'
        SPRE: str = 'SPRE'

    class Limit(Protocol):
        """This class is for security limits."""
        name: str
        units: float

    class Book(Protocol):
        """This class is for security books."""
        bid: Sequence[Order]
        ask: Sequence[Order]
        bids: Sequence[Order]
        asks: Sequence[Order]

    class History(Protocol):
        """This class is for security histories."""
        tick: int
        open: float
        high: float
        low: float
        close: float

    class TAS(Protocol):
        """This class is for security times and sales."""
        id: int
        period: int
        tick: int
        price: float
        quantity: float

    ticker: str
    type: Type
    size: int
    position: float
    vwap: float
    nlv: float
    last: float
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    volume: float
    unrealized: float
    realized: float
    currency: str
    total_volume: float
    limits: Sequence[Limit]
    interest_rate: float
    is_tradeable: bool
    is_shortable: bool
    start_period: int
    stop_period: int
    description: str
    unit_multiplier: int
    display_unit: str
    start_price: float
    min_price: float
    max_price: float
    quoted_decimals: int
    trading_fee: float
    limit_order_rebate: float
    min_trade_size: float
    max_trade_size: float
    required_tickers: str
    underlying_tickers: Sequence[str]
    bond_coupon: float
    interest_payments_per_period: int
    base_security: str
    fixing_ticker: str
    api_orders_per_second: int
    execution_delay_ms: int
    interest_rate_ticker: float
    otc_price_range: float


class Tender(Protocol):
    """This class is for tenders."""
    tender_id: int
    period: int
    tick: int
    expires: int
    caption: str
    ticker: str
    quantity: float
    action: Order.Action
    is_fixed_bid: bool
    price: float


@dataclass(frozen=True)
class RIT:
    """This class contains various methods that interact with the RIT
    Client Application.

    The method names reflect the request method used, and the request
    path used. The positional arguments are used as part of the path,
    while the keyword arguments are used as parameters to the request.

    For example :meth:`RIT.get_case` sends a ``GET`` request to the
    ``/case`` path.
    """

    x_api_key: str
    """The X-API-Key of the RITC web server."""
    hostname: str = 'localhost'
    """The hostname of the RITC web server. Defaults to ``localhost``."""
    port: int = 9999
    """The port of the RITC web server. Defaults to ``9999``."""
    __session: Session = field(default_factory=Session, init=False)

    def __post_init__(self) -> None:
        self.__session.headers.update({'X-API-Key': self.x_api_key})

    @overload  # type: ignore[misc]
    def get_case(self) -> Case:
        pass

    def get_case(self, **kwargs: Any) -> Any:
        """Get an information about the current case.

        >>> rit = RIT('G4DNIZ5D')
        >>> case = rit.get_case()
        >>> case
        {'name': 'RITC 2023 Algo Case - practice', 'period': 1, ...}
        >>> case.tick
        83
        >>> case['tick']
        83
        >>> case.status == Case.Status.ACTIVE
        True

        :return: The current case.
        """
        return self.__get('/v1/case', kwargs)

    @overload  # type: ignore[misc]
    def get_trader(self) -> Trader:
        pass

    def get_trader(self, **kwargs: Any) -> Any:
        """Get an information about the currently signed in trader.

        >>> rit = RIT('G4DNIZ5D')
        >>> trader = rit.get_trader()
        >>> trader
        {'trader_id': 'AussieSeaweed', 'first_name': 'Juho', ...}
        >>> trader.trader_id
        'AussieSeaweed'
        >>> trader['trader_id']
        'AussieSeaweed'

        :return: The current trader.
        """
        return self.__get('/v1/trader', kwargs)

    @overload  # type: ignore[misc]
    def get_limits(self) -> Sequence[Limit]:
        pass

    def get_limits(self, **kwargs: Any) -> Any:
        """Get trading limits for the current case.

        >>> rit = RIT('G4DNIZ5D')
        >>> limits = rit.get_limits()
        >>> limits
        [{'name': 'LIMIT-STOCK', 'gross': 32500.0, 'net': -32500.0, ...}, ...]
        >>> limits[0].name
        'LIMIT-STOCK'
        >>> limits[0]['name']
        'LIMIT-STOCK'

        :return: The trading limits.
        """
        return self.__get('/v1/limits', kwargs)

    @overload
    def get_news(
            self,
            *,
            since: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[News]:
        pass

    @overload
    def get_news(
            self,
            *,
            after: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[News]:
        pass

    def get_news(self, **kwargs: Any) -> Any:
        """Gets the most recent news.

        The parameter named ``since`` was renamed to ``after`` in RIT
        REST API ``v1.0.4``.

        For RIT Client applications with REST API ``v1.0.3`` or lower,
        the user must use ``since`` instead of ``after`` if he/she
        wishes to use that parameter, and vice versa.

        >>> rit = RIT('G4DNIZ5D')
        >>> news = rit.get_news()
        >>> news
        [{'news_id': 1, 'period': 1, 'tick': 0, 'ticker': '', ...}, ...]
        >>> news[0].headline
        'Welcome to RITC 2022 Algo Case - Practice Case'
        >>> news[0]['headline']
        'Welcome to RITC 2022 Algo Case - Practice Case'

        :param since: Retrieve only news items *after* a particular
                      :attr:`News.news_id`. Renamed to ``after`` in
                      ``v1.0.4``.
        :param after: Retrieve only news items *after* a particular
                      :attr:`News.news_id`. Introduced in ``v1.0.4``.
        :param limit: Result set limit, counting backwards from the most
                      recent news item. Defaults to ``20``.
        :return: The most recent news.
        """
        return self.__get('/v1/news', kwargs)

    @overload  # type: ignore[misc]
    def get_assets(self, *, ticker: Optional[str] = None) -> Sequence[Asset]:
        pass

    def get_assets(self, **kwargs: Any) -> Any:
        """Gets a list of available assets.

        >>> rit = RIT('G4DNIZ5D')
        >>> assets = rit.get_assets()
        >>> assets
        [{'ticker': 'ETF-Creation', 'type': 'REFINERY', ...}, ...]
        >>> assets = rit.get_assets(ticker='ETF-Creation')
        >>> assets
        [{'ticker': 'ETF-Creation', 'type': 'REFINERY', ...}]
        >>> assets[0].type
        'REFINERY'
        >>> assets[0]['type']
        'REFINERY'

        :param ticker: The optional asset ticker. A full list of assets
                       is returned if unspecified.
        :return: The list of available assets.
        """
        return self.__get('/v1/assets', kwargs)

    @overload  # type: ignore[misc]
    def get_assets_history(
            self,
            *,
            ticker: Optional[str] = None,
            period: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[Asset.History]:
        pass

    def get_assets_history(self, **kwargs: Any) -> Any:
        """Get the activity log for assets.

        This API was introduced in RIT REST API ``v1.0.3``.

        The way ``limit`` parameter is interpreted is RIT REST API
        version dependent.

        In ``v1.0.3``, the ``limit`` is interpreted as the result set
        limit, counting backwards from the most recent tick. This
        defaults to retrieving the entire period.

        In ``v1.0.4``, the ``limit`` is interpreted as the result set
        limit, counting backwards from the most recent item. This
        defaults to ``20``.

        >>> rit = RIT('G4DNIZ5D')
        >>> histories = rit.get_assets_history()
        >>> histories
        [{'tick': 100, 'ticker': 'ETF-Redemption', ...}, ...]
        >>> histories[0].tick
        100
        >>> histories[0]['tick']
        100

        :param ticker: The optional asset ticker. If unspecified, a full
                       list of assets is retrieved.
        :param period: Period to retrieve data from. Defaults to the
                       current period.
        :param limit: Result set limit. How this value is interpreted
                      is RIT REST API version dependent.
        :return: The activity log for assets.
        """
        return self.__get('/v1/assets/history', kwargs)

    @overload  # type: ignore[misc]
    def get_securities(
            self,
            *,
            ticker: Optional[str] = None,
    ) -> Sequence[Security]:
        pass

    def get_securities(self, **kwargs: Any) -> Any:
        """Get a list of available securities and associated positions.

        >>> rit = RIT('G4DNIZ5D')
        >>> securities = rit.get_securities(ticker='RITC')
        >>> securities[0]
        {'ticker': 'RITC', 'type': 'STOCK', 'size': 1, ...}
        >>> securities[0].ticker
        'RITC'
        >>> securities[0].bid
        24.21
        >>> securities[0]['ask']
        24.36

        :param ticker: The optional :attr:`Security.ticker`. If
                       unspecified, a full list of securities is
                       retrieved.
        :return: The lists of available securites and associated
                 positions.
        """
        return self.__get('/v1/securities', kwargs)

    @overload  # type: ignore[misc]
    def get_securities_book(
            self,
            *,
            ticker: str,
            limit: Optional[int] = None,
    ) -> Security.Book:
        pass

    def get_securities_book(self, **kwargs: Any) -> Any:
        """Get the order book of a security.

        >>> rit = RIT('G4DNIZ5D')
        >>> book = rit.get_securities_book(ticker='RITC')
        >>> len(book.bids)
        20
        >>> book.bids[:2]
        [{'order_id': 2505, 'period': 1, 'tick': 132, ...}, ...]
        >>> book.bids[0].ticker
        'RITC'
        >>> book.bids[0].price
        25.06
        >>> book.bids[0]['type']
        'LIMIT'

        :param ticker: The :attr:`Security.ticker`.
        :param limit: Maximum number of orders to return for each side of the
                      order book. Defaults to ``20``.
        :return: The order book.
        """
        return self.__get('/v1/securities/book', kwargs)

    @overload  # type: ignore[misc]
    def get_securities_history(
            self,
            *,
            ticker: str,
            period: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[Security.History]:
        pass

    def get_securities_history(self, **kwargs: Any) -> Any:
        """Get the OHLC history for a security.

        In ``v1.0.3`` and previous versions, the ``limit`` is
        interpreted as the result set limit, counting backwards from the
        most recent tick. This defaults to retrieving the entire period.

        In ``v1.0.4``, the ``limit`` is interpreted as the result set
        limit, counting backwards from the most recent item. This
        defaults to ``20``.

        >>> rit = RIT('G4DNIZ5D')
        >>> histories = rit.get_securities_history(ticker='RITC')
        >>> len(histories)
        224
        >>> histories[:2]
        [{'tick': 224, 'open': 26.27, 'high': 26.42, 'low': 26.27, ...}, ...]
        >>> histories[0].tick
        224
        >>> histories[0]['high']
        26.42

        :param ticker: The :attr:`Security.ticker`.
        :param period: Period to retrieve data from. Defaults to the
                       current period.
        :param limit: Result set limit. How this value is interpreted
                      is RIT REST API version dependent.
        :return: The OHLC history.
        """
        return self.__get('/v1/securities/history', kwargs)

    @overload  # type: ignore[misc]
    def get_securities_tas(
            self,
            *,
            ticker: str,
            after: Optional[int] = None,
            period: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[Security.TAS]:
        pass

    def get_securities_tas(self, **kwargs: Any) -> Any:
        """Get time and sales history for a security.

        Data is anonymized.

        In ``v1.0.3`` and previous versions, the ``limit`` is
        interpreted as the result set limit, counting backwards from the
        most recent tick. This defaults to retrieving the entire period.

        In ``v1.0.4``, the ``limit`` is interpreted as the result set
        limit, counting backwards from the most recent item. This
        defaults to ``20``.

        For ``v1.0.3`` and lower, there are two modes of retrieval for
        this endpoint.

        If ``after`` is specified, then only data with an ``id`` value
        greater than ``after`` will be returned. This allows only
        incremental data to be retrieved by storing the last ``id``
        value returned. Setting ``after`` to ``0`` will return all time
        and sales data.

        Alternatively, specifying ``period`` and ``limit`` will fetch
        data from the corresponding ``period`` and ``tick`` window. For
        example, setting ``limit`` to ``0`` returns only data from the
        current period and current tick.

        Both modes are simultaneously supported onwards from ``v1.0.4``.

        >>> rit = RIT('G4DNIZ5D')
        >>> tas = rit.get_securities_tas(ticker='RITC')
        >>> len(tas)
        579
        >>> tas[:2]
        [{'id': 2099, 'period': 1, 'tick': 299, 'price': 26.33, ...}, ...]
        >>> tas[0].id
        2099
        >>> tas[0].price
        26.33

        :param ticker: The :attr:`Security.ticker`.
        :param after: Retrieve only data with an
                      :attr:`Security.TAS.id` value greater than this
                      value.
        :param period: Period to retrieve data from. Defaults to the
                       current period.
        :param limit: Result set limit. How this value is interpreted
                      is RIT REST API version dependent.
        :return: The time and sales history.
        """
        return self.__get('/v1/securities/tas', kwargs)

    @overload
    def get_orders(
            self,
            *,
            status: Optional[Order.Status] = None,
    ) -> Sequence[Order]:
        pass

    @overload
    def get_orders(self, id: int) -> Order:
        pass

    def get_orders(self, id: Optional[int] = None, **kwargs: Any) -> Any:
        """Get a list of all orders or details of a specific order.

        if ``id`` is specified, a single order is returned instead of a
        list of orders.

        >>> rit = RIT('G4DNIZ5D')
        >>> orders = rit.get_orders()
        >>> len(orders)
        5
        >>> orders
        [{'order_id': 714, 'period': 1, 'tick': 31, ...}, ...]
        >>> orders[0].ticker
        'BEAR'
        >>> orders[0].price
        15.04
        >>> orders[0].action == Order.Action.SELL
        True

        :param status: The status of the orders to return. Defaults to
                       :attr:`Order.Status.OPEN`.
        :param id: The optional :attr:`Order.order_id` of the order.
        :return: The list of all orders or a single order.
        """
        if id is None:
            url = '/v1/orders'
        else:
            url = f'/v1/orders/{id}'

        return self.__get(url, kwargs)

    @overload  # type: ignore[misc]
    def post_orders(
            self,
            wait: bool = False,
            *,
            ticker: str,
            type: Order.Type,
            quantity: float,
            action: Order.Action,
            price: Optional[float] = None,
            dry_run: Optional[int] = None,
    ) -> Order:
        pass

    def post_orders(self, wait: bool = False, **kwargs: Any) -> Any:
        """Insert a new order.

        Note that this endpoint is rate-limited. If the rate limit is
        exceeded, the ``ritc`` library will internally sleep and hang
        until the desired timeout has passed and try to post the order
        again.

        >>> rit = RIT('G4DNIZ5D')
        >>> order = rit.post_orders(
        ...     ticker='RITC',
        ...     type=Order.Type.MARKET,
        ...     quantity=5,
        ...     action=Order.Action.BUY,
        ... )
        >>> order
        {'order_id': 3135, 'period': 1, 'tick': 180, ...}
        >>> order = rit.post_orders(
        ...     ticker='RITC',
        ...     type='LIMIT',
        ...     quantity=5,
        ...     action='SELL',
        ...     price=24.5,
        ... )
        >>> order
        {'order_id': 3835, 'period': 1, 'tick': 223, ...}

        :param wait: Wait if rate limit is exceeded, defaults to
                     ``False``.
        :param ticker: The ticker.
        :param type: The order type.
        :param quantity: The order quantity.
        :param action: The order action.
        :param price: The optional price. Required if type is
                      :attr:`Order.Type.LIMIT`. Ignored otherwise.
        :param dry_run: Only available if type is
                        :attr:`Order.Type.MARKET`. Simulates the
                        order execution and returns the result as if the
                        order was executed.
        :return: The newly posted order.
        """
        return self.__post('/v1/orders', kwargs, wait)

    @overload  # type: ignore[misc]
    def delete_orders(self, id: int) -> SuccessResult:
        pass

    def delete_orders(self, id: int, **kwargs: Any) -> Any:
        """Cancel an open order.

        >>> rit = RIT('G4DNIZ5D')
        >>> result = rit.delete_orders(563)
        >>> result
        {'success': True}
        >>> result.success
        True
        >>> result['success']
        True

        :param id: The :attr:`Order.id` of the order.
        :return: The newly posted order.
        """
        return self.__delete(f'/v1/orders/{id}', kwargs)

    @overload  # type: ignore[misc]
    def get_tenders(self) -> Sequence[Tender]:
        pass

    def get_tenders(self, **kwargs: Any) -> Any:
        """Get a list of all active tenders.

        >>> rit = RIT('G4DNIZ5D')
        >>> tenders = rit.get_tenders()
        >>> tenders
        [{'tender_id': 1507, 'period': 1, 'tick': 104, ...}, ...]

        :return: The list of all active tenders.
        """
        return self.__get('/v1/tenders', kwargs)

    @overload  # type: ignore[misc]
    def post_tenders(
            self,
            id: int,
            *,
            price: Optional[float] = None,
    ) -> SuccessResult:
        pass

    def post_tenders(self, id: int, **kwargs: Any) -> Any:
        """Accept the tender.

        In RIT REST API ``v1.0.3`` and lower, the parameter ``price`` is
        required only if the tender is not fixed-bid.

        From RIT REST API ``v1.0.4``, the bid ``price`` parameter is
        always required. If the tender is fixed-bid, the value must
        match the tender price.

        >>> rit = RIT('G4DNIZ5D')
        >>> result = rit.post_tenders(563)
        >>> result
        {'success': True}
        >>> result.success
        True

        :param id: The :attr:`Tender.tender_id` of the tender.
        :param price: Bid price of the tender. Its requirement is RIT
                      REST API version dependent.
        :return: The success result.
        """
        return self.__post(f'/v1/tenders/{id}', kwargs)

    @overload  # type: ignore[misc]
    def delete_tenders(self, id: int) -> SuccessResult:
        pass

    def delete_tenders(self, id: int, **kwargs: Any) -> Any:
        """Decline the tender.

        >>> rit = RIT('G4DNIZ5D')
        >>> result = rit.delete_tenders(563)
        >>> result
        {'success': True}
        >>> result.success
        True

        :param id: The :attr:`Tender.tender_id` of the tender.
        :return: The success result.
        """
        return self.__delete(f'/v1/tenders/{id}', kwargs)

    @overload
    def get_leases(self) -> Sequence[Asset.Lease]:
        pass

    @overload
    def get_leases(self, id: int) -> Asset.Lease:
        pass

    def get_leases(self, id: Optional[int] = None, **kwargs: Any) -> Any:
        """List all assets currently being leased or being used or get
        a single leased or used asset.

        if ``id`` is specified, a single lease is returned instead of a
        list of leases.

        >>> rit = RIT('G4DNIZ5D')
        >>> leases = rit.get_leases()
        >>> leases
        [{'id': 3, 'ticker': 'ETF-Creation', 'type': 'REFINERY', ...}, ...]
        >>> leases[0].type
        'REFINERY'

        :param id: The optional :attr:`Asset.Lease.id` of the asset lease.
        :return: The list of all assets or a single asset currently being
                 leased or used.
        """
        if id is None:
            url = '/v1/leases'
        else:
            url = f'/v1/leases/{id}'

        return self.__get(url, kwargs)

    @overload
    def post_leases(
            self,
            *,
            ticker: str,
            from1: Optional[str] = None,
            quantity1: Optional[float] = None,
            from2: Optional[str] = None,
            quantity2: Optional[float] = None,
            from3: Optional[str] = None,
            quantity3: Optional[float] = None,
    ) -> Asset.Lease:
        pass

    @overload
    def post_leases(
            self,
            id: int,
            *,
            from1: str,
            quantity1: float,
            from2: Optional[str] = None,
            quantity2: Optional[float] = None,
            from3: Optional[str] = None,
            quantity3: Optional[float] = None,
    ) -> Asset.Lease:
        pass

    def post_leases(self, id: Optional[int] = None, **kwargs: Any) -> Any:
        """Lease or use an asset.

        >>> rit = RIT('G4DNIZ5D')
        >>> lease = rit.post_leases(ticker='ETF-Creation')
        >>> lease
        {'id': 3, 'ticker': 'ETF-Creation', 'type': 'REFINERY', ...}
        >>> lease.type
        'REFINERY'
        >>> lease = rit.post_leases(
        ...     1,
        ...     from1='BULL',
        ...     quantity1=10000,
        ...     from2='BEAR',
        ...     quantity2=10000,
        ...     from3='USD',
        ...     quantity3=1500,
        ... )
        >>> lease
        {'id': 1, 'ticker': 'ETF-Creation', 'type': 'REFINERY', ...}

        Depending on the type of asset, you will need to specify the
        ``fromN`` and ``quantityN`` parameters. Only specify subsequent
        ``fromN`` and ``quantityN`` parameters if needed.

        :param id: The optional :attr:`Asset.Lease.id` of the asset lease.
        :param ticker: :attr:`Asset.Lease.ticker` of the asset to lease
                       or use.
        :param from1: Required for assets that can be used without
                      leasing first (such as :attr:`Asset.Type.REFINERY`
                      type assets).  Specifies the source ticker.
        :param quantity1: Required for assets that can be used without
                          leasing first (such as
                          :attr:`Asset.Type.REFINERY` type assets).
                          Specifies the source quantity.
        :param from2: Specifies the 2nd source ticker (if required).
        :param quantity2: Specifies the 2nd source quantity (if
                          required).
        :param from3: Specifies the 3rd source ticker (if required).
        :param quantity3: Specifies the 3rd source quantity (if
                          required).
        :return: The leased or used asset.
        """
        if id is None:
            url = '/v1/leases'
        else:
            url = f'/v1/leases/{id}'

        return self.__post(url, kwargs)

    @overload  # type: ignore[misc]
    def delete_leases(self, id: int) -> SuccessResult:
        pass

    def delete_leases(self, id: int, **kwargs: Any) -> Any:
        """Unlease an asset.

        >>> rit = RIT('G4DNIZ5D')
        >>> result = rit.delete_leases(3)
        >>> result
        {'success': True}

        :param id: The :attr:`Asset.Lease.id` of the asset lease.
        :return: The success result.
        """
        return self.__delete(f'/v1/leases/{id}', kwargs)

    @overload
    def post_commands_cancel(self, *, all: Literal[1]) -> CancellationResult:
        pass

    @overload
    def post_commands_cancel(self, *, ticker: str) -> CancellationResult:
        pass

    @overload
    def post_commands_cancel(self, *, ids: str) -> CancellationResult:
        pass

    @overload
    def post_commands_cancel(self, *, query: str) -> CancellationResult:
        pass

    def post_commands_cancel(self, **kwargs: Any) -> Any:
        """Bulk cancel open orders.

        Exactly one query parameter must be specified. If multiple query
        parameters are specified, only the first available parameter in
        the order below will be processed. Returns a result object that
        specifies which orders were actually cancelled.

        The ``query`` parameter was removed in RIT REST API ``v1.0.4``.

        >>> rit = RIT('G4DNIZ5D')
        >>> rit.post_commands_cancel(all=1)
        {'cancelled_order_ids': [3791, 3793, 3836, 3837, 3790, 3792, ...]}

        :param all: Set to ``1`` to cancel all open orders.
        :param ticker: Cancel all open orders for a security.
        :param ids: Cancel a set of orders referenced via a
                    comma-separated list of :attr:`Order.order_id`. For
                    example, ``'12,13,91,1'``
        :param query: Query string to select orders for cancellation.
                      For example,
                      ``"Ticker='CL' AND Price>124.23 AND Volume<0"``
                      will cancel all open sell orders for ``CL`` priced
                      above ``124.23``.
        :return: The cancellation result.
        """
        return self.__post('/v1/commands/cancel', kwargs)

    def __get(
            self,
            path: str,
            parameters: dict[Any, Any],
            wait: bool = False,
    ) -> Any:
        return self.__request('GET', path, parameters, wait)

    def __post(
            self,
            path: str,
            parameters: dict[Any, Any],
            wait: bool = False,
    ) -> Any:
        return self.__request('POST', path, parameters, wait)

    def __delete(
            self,
            path: str,
            parameters: dict[Any, Any],
            wait: bool = False,
    ) -> Any:
        return self.__request('DELETE', path, parameters, wait)

    def __request(
            self,
            method: str,
            path: str,
            parameters: dict[Any, Any],
            wait: bool = False,
    ) -> Any:
        data = None

        while data is None:
            response = self.__session.request(
                method,
                f'http://{self.hostname}:{self.port}{path}',
                parameters,
            )
            data = response.json()

            if wait and not response.ok and 'wait' in data:
                sleep(data['wait'])
                data = None
            else:
                response.raise_for_status()

        if not isinstance(data, str) and isinstance(data, Sequence):
            data = _NestedSequence(data)
        elif isinstance(data, Mapping):
            data = _NestedMapping(data)

        return data

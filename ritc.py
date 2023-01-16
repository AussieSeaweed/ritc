from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from time import sleep
from typing import Any, Literal, Optional, Protocol, Union, overload

from requests import Session


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

        if isinstance(item, Sequence):
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

        if isinstance(item, Sequence):
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
    code: str
    message: str


class Case(Protocol):
    class Status(str, Enum):
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
    trader_id: str
    first_name: str
    last_name: str
    nlv: float


class Limit(Protocol):
    name: str
    gross: float
    net: float
    gross_limit: float
    net_limit: float
    gross_fine: float
    net_fine: float


class New(Protocol):
    news_id: int
    period: int
    tick: int
    ticker: str
    headline: str
    body: str


class Ticker(Protocol):
    class Quantity(Protocol):
        ticker: str
        quantity: float

    class Price(Protocol):
        ticker: str
        price: float


class Asset(Protocol):
    class Type(str, Enum):
        CONTAINER: str = 'CONTAINER'
        PIPELINE: str = 'PIPELINE'
        SHIP: str = 'SHIP'
        REFINERY: str = 'REFINERY'
        POWER_PLANT: str = 'POWER_PLANT'
        PRODUCER: str = 'PRODUCER'

    class History(Protocol):
        ticker: str
        tick: int
        action: str
        cost: float
        convert_from: Sequence[Ticker.Quantity]
        convert_to: Sequence[Ticker.Quantity]
        convert_from_price: Sequence[Ticker.Price]
        convert_to_price: Sequence[Ticker.Price]

    class Lease(Protocol):
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
    total_quantity: float
    available_quantity: float
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
    class Type(str, Enum):
        MARKET: str = 'MARKET'
        LIMIT: str = 'LIMIT'

    class Action(str, Enum):
        BUY: str = 'BUY'
        SELL: str = 'SELL'

    class Status(str, Enum):
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
    success: bool


class CancellationResult(Protocol):
    cancelled_order_ids: Sequence[int]


class Security(Protocol):
    class Type(str, Enum):
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
        name: str
        units: float

    class Book(Protocol):
        bid: Sequence[Order]
        ask: Sequence[Order]

    class History(Protocol):
        tick: int
        open: float
        high: float
        low: float
        close: float

    class TAS(Protocol):
        id: int
        period: int
        tick: int
        price: float
        quantity: float

    ticker: str
    type: Type
    size: float
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
    unit_multiplier: float
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
    bond_coupon: float
    interest_payments_per_period: int
    base_security: str
    fixing_ticker: str
    api_orders_per_second: int
    execution_delay_ms: int
    interest_rate_ticker: float
    otc_price_range: float


class Tender(Protocol):
    tender_id: int
    period: int
    tick: int
    expires: int
    caption: str
    quantity: float
    action: Order.Action
    is_fixed_bid: bool
    price: float


@dataclass(frozen=True)
class RIT:
    @dataclass(frozen=True)
    class Error(ValueError):
        data: Error

        def __str__(self) -> str:
            return f'Error response received with data \'{self.data}\''

    x_api_key: str
    hostname: str = 'localhost'
    port: int = 9999
    __session: Session = field(default_factory=Session, init=False)

    def __post_init__(self) -> None:
        self.__session.headers.update({'X-API-Key': self.x_api_key})

    @overload  # type: ignore[misc]
    def get_case(self) -> Case:
        pass

    def get_case(self, **kwargs: Any) -> Any:
        return self.__get('/v1/case', kwargs)

    @overload  # type: ignore[misc]
    def get_trader(self) -> Trader:
        pass

    def get_trader(self, **kwargs: Any) -> Any:
        return self.__get('/v1/trader', kwargs)

    @overload  # type: ignore[misc]
    def get_limits(self) -> Sequence[Limit]:
        pass

    def get_limits(self, **kwargs: Any) -> Any:
        return self.__get('/v1/limits', kwargs)

    @overload
    def get_news(
            self,
            *,
            since: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[New]:
        pass

    @overload
    def get_news(
            self,
            *,
            after: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> Sequence[New]:
        pass

    def get_news(self, **kwargs: Any) -> Any:
        return self.__get('/v1/news', kwargs)

    @overload  # type: ignore[misc]
    def get_assets(self, *, ticker: Optional[str] = None) -> Sequence[Asset]:
        pass

    def get_assets(self, **kwargs: Any) -> Any:
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
        return self.__get('/v1/assets/history', kwargs)

    @overload  # type: ignore[misc]
    def get_securities(
            self,
            *,
            ticker: Optional[str] = None,
    ) -> Sequence[Security]:
        pass

    def get_securities(self, **kwargs: Any) -> Any:
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
        if id is None:
            url = '/v1/orders'
        else:
            url = f'/v1/orders/{id}'

        return self.__get(url, kwargs)

    @overload  # type: ignore[misc]
    def post_orders(
            self,
            *,
            ticker: str,
            type: Order.Type,
            quantity: int,
            action: Order.Action,
            price: Optional[float] = None,
            dry_run: Optional[int] = None,
    ) -> Order:
        pass

    def post_orders(self, **kwargs: Any) -> Any:
        return self.__post('/v1/orders', kwargs)

    @overload  # type: ignore[misc]
    def delete_orders(self, id: int) -> SuccessResult:
        pass

    def delete_orders(self, id: int, **kwargs: Any) -> Any:
        return self.__delete(f'/v1/orders/{id}', kwargs)

    @overload  # type: ignore[misc]
    def get_tenders(self) -> Sequence[Tender]:
        pass

    def get_tenders(self, **kwargs: Any) -> Any:
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
        return self.__post(f'/v1/tenders/{id}', kwargs)

    @overload  # type: ignore[misc]
    def delete_tenders(self, id: int) -> SuccessResult:
        pass

    def delete_tenders(self, id: int, **kwargs: Any) -> Any:
        return self.__delete(f'/v1/tenders/{id}', kwargs)

    @overload
    def get_leases(self) -> Sequence[Asset.Lease]:
        pass

    @overload
    def get_leases(self, id: int) -> Asset.Lease:
        pass

    def get_leases(self, id: Optional[int] = None, **kwargs: Any) -> Any:
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
        if id is None:
            url = '/v1/leases'
        else:
            url = f'/v1/leases/{id}'

        return self.__post(url, kwargs)

    @overload  # type: ignore[misc]
    def delete_leases(self, id: int) -> SuccessResult:
        pass

    def delete_leases(self, id: int, **kwargs: Any) -> Any:
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
        return self.__post('/v1/commands/cancel', **kwargs)

    def __get(self, path: str, parameters: dict[Any, Any]) -> Any:
        return self.__request('GET', path, parameters)

    def __post(self, path: str, parameters: dict[Any, Any]) -> Any:
        return self.__request('POST', path, parameters)

    def __delete(self, path: str, parameters: dict[Any, Any]) -> Any:
        return self.__request('DELETE', path, parameters)

    def __request(
            self,
            method: str,
            path: str,
            parameters: dict[Any, Any],
    ) -> Any:
        data = None

        while data is None:
            response = self.__session.request(
                method,
                f'http://{self.hostname}:{self.port}{path}',
                parameters,
            )
            data = response.json()

            if not response.ok:
                wait = data.get('wait')

                if wait is None:
                    raise self.Error(data)

                sleep(wait)
                data = None

        if isinstance(data, Sequence):
            data = _NestedSequence(data)
        elif isinstance(data, Mapping):
            data = _NestedMapping(data)

        return data

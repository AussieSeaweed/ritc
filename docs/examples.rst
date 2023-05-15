Example Usages
==============

Some examples that use ``ritc`` is shown here.

Market Making
-------------

Below is an example market-making code using ``ritc``. Obviously, there are some
improvements that can be made.

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor
   from traceback import format_exc

   from requests import HTTPError
   from ritc import Case, Order, RIT, Security

   X_API_KEY = '2X4P2XFA'
   MIN_SPREAD = 0.07


   def make_market(rit, ticker):
       while rit.get_case().status == Case.Status.ACTIVE:
           security = rit.get_securities(ticker=ticker)[0]
           position = security.position
           max_trade_size = security.max_trade_size
           book = rit.get_securities_book(ticker=ticker, limit=1)

           if not book.bids or not book.asks:
               continue

           bid = book.bids[0].price
           ask = book.asks[0].price
           spread = ask - bid

           if spread < MIN_SPREAD:
               continue

           bid_quantity = min(max_trade_size, max_trade_size - position)
           ask_quantity = min(max_trade_size, max_trade_size + position)

           if bid_quantity > 0:
               rit.post_commands_cancel(
                   query=f'Ticker=\'{ticker}\' AND Price<{bid} AND Volume>0',
               )

               try:
                   rit.post_orders(
                       True,
                       ticker=ticker,
                       type=Order.Type.LIMIT,
                       quantity=bid_quantity,
                       action=Order.Action.BUY,
                       price=bid,
                   )
               except HTTPError as error:
                   print(format_exc())
                   print(error.response.json())
           else:
               rit.post_commands_cancel(query=f'Ticker=\'{ticker}\' AND Volume>0')

           if ask_quantity > 0:
               rit.post_commands_cancel(
                   query=f'Ticker=\'{ticker}\' AND Price>{ask} AND Volume<0',
               )

               try:
                   rit.post_orders(
                       True,
                       ticker=ticker,
                       type=Order.Type.LIMIT,
                       quantity=ask_quantity,
                       action=Order.Action.SELL,
                       price=ask,
                   )
               except HTTPError as error:
                   print(format_exc())
                   print(error.response.json())
           else:
               rit.post_commands_cancel(query=f'Ticker=\'{ticker}\' AND Volume<0')


   def main():
       rit = RIT(X_API_KEY)
       securities = rit.get_securities()
       executor = ThreadPoolExecutor()
       futures = []

       for security in securities:
           if security.type == Security.Type.STOCK:
               futures.append(executor.submit(make_market, rit, security.ticker))

       for future in futures:
           future.result()


   if __name__ == '__main__':
       main()

Position Sell-off
-----------------

Below is an example code where the trader's position is liquidated as fast as
possible using market orders. Note that this is a bad thing to do and can be
costly!

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor
   from time import sleep
   from traceback import format_exc

   from requests import HTTPError
   from ritc import Case, Order, RIT, Security

   X_API_KEY = '2X4P2XFA'
   SLEEP_TIME = 0.1


   def sell_off_position(rit, ticker):
       while rit.get_case().status == Case.Status.ACTIVE:
           rit.post_commands_cancel(all=1)

           security = rit.get_securities(ticker=ticker)[0]
           position = security.position
           max_trade_size = security.max_trade_size
           bid_quantity = min(max_trade_size, -position)
           ask_quantity = min(max_trade_size, position)

           if bid_quantity > 0:
               try:
                   rit.post_orders(
                       True,
                       ticker=ticker,
                       type=Order.Type.MARKET,
                       quantity=bid_quantity,
                       action=Order.Action.BUY,
                   )
               except HTTPError as error:
                   print(format_exc())
                   print(error.response.json())

           if ask_quantity > 0:
               try:
                   rit.post_orders(
                       True,
                       ticker=ticker,
                       type=Order.Type.MARKET,
                       quantity=ask_quantity,
                       action=Order.Action.SELL,
                   )
               except HTTPError as error:
                   print(format_exc())
                   print(error.response.json())

           sleep(SLEEP_TIME)


   def main():
       rit = RIT(X_API_KEY)
       securities = rit.get_securities()
       executor = ThreadPoolExecutor()
       futures = []

       for security in securities:
           if security.type == Security.Type.STOCK:
               futures.append(
                   executor.submit(sell_off_position, rit, security.ticker),
               )

       for future in futures:
           future.result()


   if __name__ == '__main__':
       main()

Average Spread Report I
-----------------------

The following code calculates the average spread and displays it to the console.
Here, the average calculated weighs all polled bid and ask prices equally.

.. code-block:: python

   from collections import defaultdict

   from ritc import Case, RIT, Security

   X_API_KEY = '2X4P2XFA'


   def get_spread(rit, ticker):
       book = rit.get_securities_book(ticker=ticker, limit=1)

       if not book.bids or not book.asks:
           return None

       bid = book.bids[0].price
       ask = book.asks[0].price

       return bid, ask

   def merge(spread, average_spread, count):
       merged_spread = list(average_spread)
       merged_spread[0] *= count / (count + 1)
       merged_spread[1] *= count / (count + 1)
       merged_spread[0] += spread[0] / (count + 1)
       merged_spread[1] += spread[1] / (count + 1)

       return tuple(merged_spread), count + 1

   def main():
       rit = RIT(X_API_KEY)
       securities = rit.get_securities()
       averages = defaultdict(lambda: ((0, 0), 0))

       while rit.get_case().status == Case.Status.ACTIVE:
           for security in securities:
               if security.type == Security.Type.STOCK:
                   spread = get_spread(rit, security.ticker)

                   if spread is not None:
                       averages[security.ticker] \
                           = merge(spread, *averages[security.ticker])

           tokens = []

           for key, value in averages.items():
               tokens.append(key)
               tokens.append(f'{value[0][0]:.2f}')
               tokens.append(f'{value[0][1]:.2f}')

           print('\t'.join(tokens), end='\r')


   if __name__ == '__main__':
       main()

Average Spread Report II
------------------------

The following code calculates the average spread and displays it to the console.
Here, the average calculated gives more weights to bid and ask prices polled
later.

.. code-block:: python

   from collections import defaultdict

   from ritc import Case, RIT, Security

   X_API_KEY = '2X4P2XFA'


   def get_spread(rit, ticker):
       book = rit.get_securities_book(ticker=ticker, limit=1)

       if not book.bids or not book.asks:
           return None

       bid = book.bids[0].price
       ask = book.asks[0].price

       return bid, ask

   def merge(spread, average_spread, count):
       merged_spread = list(average_spread)
       merged_spread[0] *= count / (count + 2)
       merged_spread[1] *= count / (count + 2)
       merged_spread[0] += 2 * spread[0] / (count + 2)
       merged_spread[1] += 2 * spread[1] / (count + 2)

       return tuple(merged_spread), count + 1

   def main():
       rit = RIT(X_API_KEY)
       securities = rit.get_securities()
       averages = defaultdict(lambda: ((0, 0), 0))

       while rit.get_case().status == Case.Status.ACTIVE:
           for security in securities:
               if security.type == Security.Type.STOCK:
                   spread = get_spread(rit, security.ticker)

                   if spread is not None:
                       averages[security.ticker] \
                           = merge(spread, *averages[security.ticker])

           tokens = []

           for key, value in averages.items():
               tokens.append(key)
               tokens.append(f'{value[0][0]:.2f}')
               tokens.append(f'{value[0][1]:.2f}')

           print('\t'.join(tokens), end='\r')


   if __name__ == '__main__':
       main()

Tips
----

- Minimize the API calls for maximum speed and to minimize the period of time
  your code blocks.
- Look at the source code of ``ritc`` and make changes you think is necessary!
- Use simple logic. If a function gets too long or convoluted, you can
  definitely make it simpler! Plus, it reduces the number of potential bugs.

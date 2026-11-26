"""Application entry point for the Lift Pass Pricing Flask service.

Read: The prices module and its configured Flask app.
Modify: Starts the development HTTP server on port 3005.
Output: Prints the startup URL and serves GET/PUT requests for lift-pass prices.
Business logic: This file contains transport startup only; pricing and database
behavior are delegated to prices.py and db.py.
"""

from prices import app

if __name__ == "__main__":
    print("""LiftPassPricing Api started on 3005,
you can open http://127.0.0.1:3005/prices?type=night&age=23&date=2019-02-18 in a navigator
and you'll get the price of the list pass for the day.""")
    app.run(port=3005, threaded=False)

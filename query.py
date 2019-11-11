import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

# tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
# app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://xc2444:950101@34.74.165.156/proj1part2"
engine = create_engine(DATABASEURI)

def create_app(test_config=None):
    app = Flask(__name__)

    @app.before_request
    def before_request():
        try:
            g.conn = engine.connect()
        except:
            print("uh oh, problem connecting to database")
            import traceback; traceback.print_exc()
            g.conn = None

    @app.teardown_request
    def teardown_request(exception):
        try:
            g.conn.close()
        except Exception as e:
            pass

    @app.route('/')
    def index():
        # DEBUG: this is debugging code to see what request looks like
        print(request.args)
        return render_template("index.html")



    @app.route('/returned', methods=['POST'])
    def returned_search():
        email_address = request.form['email']
        query = 'SELECT * FROM request WHERE email_address = \'{}\''.format(email_address)
        cursor = g.conn.execute(query)
        entries = []
        for result in cursor:
            returned_user = {}
            returned_user['email_address'] = result['email_address']
            returned_user['date'] = result['date']
            returned_user['preference'] = result['preference']
            returned_user['origin'] = result['origin']
            returned_user['destination'] = result['destination']
            returned_user['request_id'] = result['request_id']
            entries.append(returned_user)
        cursor.close()  

        if not entries:
            return redirect('/no_results')
        else:
            #######################
            context = dict(result = entries, returned_user = email_address)
            return render_template('returned.html', **context)                


    # convert time '1800' to '18:00'
    def change_time(t):
        t = str(t)
        min = t[(-2):]
        hr = t[:(-2)]
        return hr + ':' + min



    @app.route('/search', methods = ['POST'])
    def flight_search():
        depart = request.form['departure']
        arr = request.form['arrival']
        date = request.form['date']

        key = request.form['sort']

        print("[DEBUG]" + str(depart))
        print("[DEBUG]" + str(arr))
        print("[DEBUG]" + str(date))
        print("[DEBUG]" + str(key))


        if key == 'default':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'""".format(date, depart, arr)
        elif key == 'shortest_duration':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'
                        ORDER BY actual_elapse""".format(date, depart, arr)
        elif key == 'earliest_departure':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'
                        ORDER BY exp_dep_time""".format(date, depart, arr)

        elif key == 'latest_departure':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'
                        ORDER BY exp_dep_time DESC""".format(date, depart, arr)


        cursor = g.conn.execute(query)
        entries = []
        for result in cursor:
            flight = {}
            ## flight_date, flight_no, carrier_code, origin, destination, 
            # exp_dep_time, exp_arr_time, actual_elapse
            flight['flight_no'] = result['carrier_code'] + str(result['flight_no'])
            flight['from'] = result['origin']
            flight['to'] = result['destination']
            flight['date'] = result['flight_date']
            flight['departure_time'] = change_time(result['exp_dep_time'])
            flight['arrival_time'] = change_time(result['exp_arr_time'])
            flight['duration'] = result['actual_elapse']
            entries.append(flight)
            ###############
        cursor.close()

        if not entries:
            return redirect('/no_results')

        else:
            context = dict(flight = entries)
            return render_template('flight_search.html', **context)



    @app.route('/recommend', methods = ['POST'])
    def recommend():
        depart = request.form['departure']
        arr = request.form['arrival']
        date = request.form['date']

        print("[DEBUG]" + str(depart))
        print("[DEBUG]" + str(arr))
        print("[DEBUG]" + str(date))

        query = """
                WITH r1 AS (
                    SELECT airline_id,ROUND(AVG(arr_delay), 0) AS avg_delay, RANK() OVER (ORDER BY AVG(arr_delay)) AS rank1, ROUND(AVG(actual_elapse), 0) AS avg_duration, RANK() OVER (ORDER BY AVG(actual_elapse)) AS rank2
                    FROM flight
                    WHERE  origin = \'{}\' AND destination = \'{}\' AND actual_elapse != 0 
                    GROUP BY airline_id), r2 AS(
                    SELECT airline_id, carrier_name, CAST (no_of_managers AS DECIMAL) / no_of_employees AS ratio, RANK() OVER (ORDER BY no_of_managers / no_of_employees::float DESC) AS rank3
                    FROM airline)
                SELECT r1.airline_id AS airline_id, carrier_name, CASE WHEN r1.avg_delay <0 THEN 0 ELSE r1.avg_delay END, r1.avg_duration, ROUND(r2.ratio, 3) AS ratio, (100 - r1.rank1*0.5 - r1.rank2*0.3 - r2.rank3 * 0.2) AS score, RANK() OVER (ORDER BY 100 - r1.rank1*0.5 - r1.rank2*0.3 - r2.rank3 * 0.2 DESC)
                FROM r1, r2
                WHERE r1.airline_id = r2.airline_id AND r1.airline_id in (SELECT airline_id FROM flight as f WHERE flight_date = \'{}\')
                ORDER BY score DESC
                LIMIT 10""".format(depart, arr, date)
        


        cursor = g.conn.execute(query)
        entries = []
        for result in cursor:
            flight = {}
            flight['airline_id'] = result['airline_id']
            flight['carrier_name'] = result['carrier_name']
            flight['avg_delay'] = result['avg_delay']
            flight['avg_duration'] = result['avg_duration']
            flight['ratio'] = result['ratio']
            flight['score'] = result['score']
            flight['rank'] = result['rank']

            entries.append(flight)
            ###############
        cursor.close()
# [{'airline_id': 19790, 'carrier_name': 'Delta Air Lines Inc.', 
# 'avg_delay': Decimal('7'), 'avg_duration': Decimal('150'), 'ratio': Decimal('0.005'), 
# 'score': Decimal('92.6'), 'rank': 1}]
        print(entries)

        if not entries:
            return redirect('/no_results')

        else:
            context = dict(flight = entries)
            return render_template('recommend.html', **context)



    @app.route('/top10_airports', methods=['GET'])
    def top10_airports():
        query = """
                SELECT a AS airport, sum(c) AS total_flight, airport.city FROM ((SELECT a, c
                FROM (SELECT origin AS a, COUNT(*) AS c
                FROM flight
                GROUP by a) s1 )
                UNION ALL
                (SELECT a, c
                FROM (SELECT destination AS a, COUNT(*) AS c
                FROM flight
                GROUP by a) s2 )
                )q
                INNER JOIN airport
                ON (a = airport.airport_abbr) GROUP BY a, airport.city ORDER BY sum(c) DESC LIMIT 10
                """
        cursor = g.conn.execute(query)
        entries = []
        for result in cursor:
            airport_info = {}
            airport_info['airport'] = result['airport']
            airport_info['total_flight'] = result['total_flight']
            airport_info['city'] = result['city']
            entries.append(airport_info)

        cursor.close() 
        context = dict(result = entries)

        return render_template('top10_airports.html', **context)



    @app.route('/top5_airlines', methods=['GET'])
    def facts_top5_airlines():
        query = """
            SELECT A.carrier_name AS Airline_Carrier, F.c AS no_flights
            FROM (SELECT airline_id, COUNT(*) as c 
            FROM flight GROUP by airline_id ) AS F 
            INNER JOIN airline AS A 
            ON(F.airline_id = A.airline_id)
            ORDER BY F.c DESC
            LIMIT 5
                """
        cursor = g.conn.execute(query)
        entries = []
        for result in cursor:
            airline_info = {}
            airline_info['airline_carrier'] = result['airline_carrier']
            airline_info['no_flights'] = result['no_flights']
            entries.append(airline_info)
        cursor.close() 
        context = dict(result = entries)
        return render_template('top5_airlines.html', **context)



    @app.route('/longest_delay', methods=['GET'])
    def facts_longest_delay():
        query = """
                SELECT a.carrier_name AS Airline_Carrier, 
                ROUND(AVG(arr_delay), 2) AS Avg_arrival_delay
                FROM flight as f
                INNER JOIN airline AS a 
                ON (f.airline_id = a.airline_id)
                WHERE f.delay_cause <> 'NO DELAY' AND arr_delay > 0
                GROUP BY a.carrier_name
                ORDER BY AVG(arr_delay) DESC
                LIMIT 10
                """
        cursor = g.conn.execute(query)
        entries = []
        for result in cursor:
            delay_info = {}
            delay_info['airline_carrier'] = result['airline_carrier']
            delay_info['avg_arrival_delay'] = result['avg_arrival_delay']
            entries.append(delay_info)
        cursor.close() 
        context = dict(result = entries)
        return render_template('longest_delay.html', **context)      





    @app.route('/no_results')
    def no_results():
        return render_template("no_results.html")



    return app


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8110, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

				python server.py

		Show the help text using:

				python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app = create_app()
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

	run() # pylint: disable=no-value-for-parameter
	
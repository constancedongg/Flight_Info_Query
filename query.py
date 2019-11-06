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

    return app

'''

    def change_date(d):
        month, date, year = d.split('/')
        return '-'.join([year, month, date])

    @app.route('/search', method = ['POST'])
    def flight_search():
        depart = request.form['departure']
        arr = request.form['arrival']
        date = request.form['date']
        date = change_date(date)

        key = request.form['sort']

        print("[DEBUG]" + str(depart))
        print("[DEBUG]" + str(arr))
        print("[DEBUG]" + str(date))
        print("[DEBUG]" + str(key))

        ##############

        query = ''
        if key == 'Default':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'""".format(date, depart, arr)
        elif key == 'Fatest':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'
                        ORDER BY actual_elapse""".format(date, depart, arr)
        elif key == 'Earliest':
            query = """
                    SELECT flight_date, flight_no, carrier_code, origin, destination, exp_dep_time, exp_arr_time, actual_elapse
                    FROM flight AS f
                        INNER JOIN airline AS a
                        ON (f.airline_id = a.airline_id) 
                    WHERE flight_date = \'{}\' AND Origin = \'{}\' AND destination = \'{}\'
                        ORDER BY exp_dep_time""".format(date, depart, arr)

        elif key == 'Latest':
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
            flight['Flight num'] = result['carrier_code'] + result['flight_no']
            flight['From'] = result['origin']
            flight['To'] = result['destination']
            flight['Date'] = result['flight_date']
            flight['Departure time'] = result['exp_dep_time']
            flight['Arrival time'] = result['exp_arr_time']
            flight['Duration'] = result['actual_elapse']
            entries.append(flight)
            ###############
        cursor.close()

        if not entries:
            ############## write no_results.html#############
            return redirect('/no_results')
        else:
            ##############
            context = dict(flight = entries)
            return render_template('flight_search.html', **context)


    @app.route('/recommend', method = ['POST'])
    def recommend():
        depart = request.form['departure']
        arr = request.form['arrival']
        date = request.form['date']
        date = change_date(date)
        
        print("[DEBUG]" + str(depart))
        print("[DEBUG]" + str(arr))
        print("[DEBUG]" + str(date))
        print("[DEBUG]" + str(key))




    @app.route('/no_results')
    def no_results():
        return render_template("no_results.html")


'''

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
	
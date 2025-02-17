import pytz
import os

from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for

from app import app
from app.commands import chia_cli, plotman_cli

@app.route('/')
def index():
    if not chia_cli.is_setup():
        return redirect(url_for('setup'))
    farming = chia_cli.load_farm_summary()
    plotting = plotman_cli.load_plotting_summary()
    now = datetime.now(tz=None)
    return render_template('index.html', reload_seconds=60, now=now,
        farming=farming.__dict__, plotting=plotting.__dict__)

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/plotting', methods=['GET', 'POST'])
def plotting():
    if request.method == 'POST':
        if request.form.get('action') == 'plot_on':
            plotman_cli.start_plot_run()
        else:
            app.logger.info("Plotting form submitted: {0}".format(request.form))
    plotting = plotman_cli.load_plotting_summary()
    now = datetime.now(tz=None)
    return render_template('plotting.html', reload_seconds=60, now=now, plotting=plotting)

@app.route('/farming')
def farming():
    farming = chia_cli.load_farm_summary()
    plots = chia_cli.load_plots_farming()
    now = datetime.now(tz=None)
    return render_template('farming.html', now=now, farming=farming, plots=plots)

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/wallet')    
def wallet():
    wallet = chia_cli.load_wallet_show()
    return render_template('wallet.html', wallet=wallet.text)

@app.route('/network/blockchain')
def network_blockchain():
    blockchain = chia_cli.load_blockchain_show()
    return render_template('network/blockchain.html', blockchain=blockchain.text)

@app.route('/network/connections', methods=['GET', 'POST'])
def network_connections():
    if request.method == 'POST':
        connection = request.form.get("connection")
        chia_cli.add_connection(connection)
    connections = chia_cli.load_connections_show()
    return render_template('network/connections.html', connections=connections.text)

@app.route('/settings/plotting', methods=['GET', 'POST'])
def settings_plotting():
    if request.method == 'POST':
        config = request.form.get("plotman")
        plotman_cli.save_config(config)
    else: # Load config fresh from disk
        config = open('/root/.chia/plotman/plotman.yaml','r').read()
    return render_template('settings/plotting.html', config=config)

@app.route('/settings/farming', methods=['GET', 'POST'])
def settings_farming():
    if request.method == 'POST':
        config = request.form.get("config")
        chia_cli.save_config(config)
    else: # Load config fresh from disk
        config = open('/root/.chia/mainnet/config/config.yaml','r').read()
    return render_template('settings/farming.html', config=config)

@app.route('/settings/alerts')
def settings_alerts():
    return render_template('settings/alerts.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')
import os
import platform
import socket

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory
)

from database import (
    initialize_database,
    get_recent_packets,
    get_packet,
    get_statistics,
    clear_packets,
    export_csv
)

from packet_capture import capture


app = Flask(__name__)

initialize_database()


def system_information():

    hostname = socket.gethostname()

    try:

        local_ip = capture.get_local_ip()

    except Exception:

        local_ip = "127.0.0.1"


    return {
        "hostname": hostname,
        "ip": local_ip,
        "os": platform.system(),
        "os_version": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version()
    }


@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route("/api/system")
def api_system():

    return jsonify(
        system_information()
    )


@app.route("/api/status")
def api_status():

    return jsonify(
        capture.get_status()
    )


@app.route("/api/start", methods=["POST"])
def api_start():

    success, message = capture.start()

    return jsonify({
        "success": success,
        "message": message
    })


@app.route("/api/stop", methods=["POST"])
def api_stop():

    success, message = capture.stop()

    return jsonify({
        "success": success,
        "message": message
    })


@app.route("/api/packets")
def api_packets():

    try:

        limit = int(
            request.args.get(
                "limit",
                200
            )
        )

    except ValueError:

        limit = 200


    limit = max(
        1,
        min(limit, 1000)
    )


    return jsonify(
        get_recent_packets(
            limit
        )
    )


@app.route("/api/packet/<int:packet_id>")
def api_packet(packet_id):

    packet = get_packet(
        packet_id
    )

    if packet is None:

        return jsonify({
            "error": "Packet not found."
        }), 404


    return jsonify(packet)


@app.route("/api/statistics")
def api_statistics():

    return jsonify(
        get_statistics()
    )


@app.route("/api/clear", methods=["POST"])
def api_clear():

    if capture.running:

        return jsonify({
            "success": False,
            "message": "Stop capture before clearing packets."
        }), 400


    clear_packets()

    return jsonify({
        "success": True,
        "message": "Packet database cleared."
    })


@app.route("/api/export")
def api_export():

    filename = export_csv()

    return jsonify({
        "success": True,
        "filename": filename,
        "url": f"/exports/{filename}"
    })


@app.route("/exports/<path:filename>")
def download_export(filename):

    export_directory = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "exports"
    )

    return send_from_directory(
        export_directory,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":

    print()
    print("=" * 60)
    print(" NETSCOPE - Network Packet Analyzer")
    print("=" * 60)

    print(
        f" Hostname : {socket.gethostname()}"
    )

    print(
        f" Local IP : {capture.get_local_ip()}"
    )

    print(
        " URL      : http://127.0.0.1:5000"
    )

    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
import sqlite3
import os
import csv
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "packets.db")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


def get_connection():
    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            protocol TEXT NOT NULL,
            source_ip TEXT,
            destination_ip TEXT,
            source_port INTEGER,
            destination_port INTEGER,
            packet_length INTEGER,
            tcp_flags TEXT,
            info TEXT
        )
    """)

    connection.commit()
    connection.close()


def insert_packet(packet):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO packets (
            timestamp,
            protocol,
            source_ip,
            destination_ip,
            source_port,
            destination_port,
            packet_length,
            tcp_flags,
            info
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        packet.get("timestamp"),
        packet.get("protocol"),
        packet.get("source_ip"),
        packet.get("destination_ip"),
        packet.get("source_port"),
        packet.get("destination_port"),
        packet.get("packet_length"),
        packet.get("tcp_flags"),
        packet.get("info")
    ))

    connection.commit()

    packet_id = cursor.lastrowid

    connection.close()

    return packet_id


def get_recent_packets(limit=200):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM packets
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_packet(packet_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM packets
        WHERE id = ?
    """, (packet_id,))

    row = cursor.fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def clear_packets():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("DELETE FROM packets")

    connection.commit()

    connection.close()


def get_statistics():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM packets
    """)

    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS tcp
        FROM packets
        WHERE protocol = 'TCP'
    """)

    tcp = cursor.fetchone()["tcp"]

    cursor.execute("""
        SELECT COUNT(*) AS udp
        FROM packets
        WHERE protocol = 'UDP'
    """)

    udp = cursor.fetchone()["udp"]

    cursor.execute("""
        SELECT COUNT(*) AS icmp
        FROM packets
        WHERE protocol = 'ICMP'
    """)

    icmp = cursor.fetchone()["icmp"]

    cursor.execute("""
        SELECT COUNT(*) AS dns
        FROM packets
        WHERE protocol = 'DNS'
    """)

    dns = cursor.fetchone()["dns"]

    cursor.execute("""
        SELECT COUNT(*) AS http
        FROM packets
        WHERE protocol = 'HTTP'
    """)

    http = cursor.fetchone()["http"]

    cursor.execute("""
        SELECT COUNT(*) AS https
        FROM packets
        WHERE protocol = 'HTTPS'
    """)

    https = cursor.fetchone()["https"]

    cursor.execute("""
        SELECT COALESCE(SUM(packet_length), 0) AS bytes
        FROM packets
    """)

    total_bytes = cursor.fetchone()["bytes"]

    cursor.execute("""
        SELECT protocol, COUNT(*) AS count
        FROM packets
        GROUP BY protocol
        ORDER BY count DESC
    """)

    protocol_rows = cursor.fetchall()

    protocols = {
        row["protocol"]: row["count"]
        for row in protocol_rows
    }

    connection.close()

    return {
        "total": total,
        "tcp": tcp,
        "udp": udp,
        "icmp": icmp,
        "dns": dns,
        "http": http,
        "https": https,
        "bytes": total_bytes,
        "protocols": protocols
    }


def export_csv():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"netscope_packets_{timestamp}.csv"

    filepath = os.path.join(
        EXPORT_DIR,
        filename
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            protocol,
            source_ip,
            destination_ip,
            source_port,
            destination_port,
            packet_length,
            tcp_flags,
            info
        FROM packets
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Timestamp",
            "Protocol",
            "Source IP",
            "Destination IP",
            "Source Port",
            "Destination Port",
            "Packet Length",
            "TCP Flags",
            "Info"
        ])

        for row in rows:

            writer.writerow([
                row["id"],
                row["timestamp"],
                row["protocol"],
                row["source_ip"],
                row["destination_ip"],
                row["source_port"],
                row["destination_port"],
                row["packet_length"],
                row["tcp_flags"],
                row["info"]
            ])

    return filename
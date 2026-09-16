import socket
import threading
import time

from scapy.all import (
    AsyncSniffer,
    IP,
    IPv6,
    TCP,
    UDP,
    ICMP,
    DNS,
    DNSQR,
    conf
)

from database import insert_packet


class PacketCapture:

    def __init__(self):

        self.sniffer = None
        self.running = False
        self.start_time = None
        self.packet_count = 0

        self.lock = threading.Lock()


    # ---------------------------------------------------------
    # SYSTEM INFORMATION
    # ---------------------------------------------------------

    def get_hostname(self):

        try:
            return socket.gethostname()

        except Exception:
            return "Unknown"


    def get_local_ip(self):

        sock = None

        try:

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

            sock.connect(
                ("8.8.8.8", 80)
            )

            ip = sock.getsockname()[0]

            return ip

        except Exception:

            try:

                return socket.gethostbyname(
                    socket.gethostname()
                )

            except Exception:

                return "127.0.0.1"

        finally:

            if sock:

                try:
                    sock.close()

                except Exception:
                    pass


    # ---------------------------------------------------------
    # START PACKET CAPTURE
    # ---------------------------------------------------------

    def start(self):

        if self.running:

            return False, "Capture is already running."


        try:

            # Reset counters
            with self.lock:

                self.packet_count = 0


            self.start_time = time.time()

            self.running = True


            # Display interface being used
            print()
            print("=" * 60)
            print("NETSCOPE PACKET CAPTURE")
            print("=" * 60)
            print("Capture interface:")
            print(conf.iface)
            print("Npcap enabled:", conf.use_pcap)
            print("=" * 60)
            print()


            # Create Scapy sniffer
            self.sniffer = AsyncSniffer(

                iface=conf.iface,

                prn=self.process_packet,

                store=False

            )


            # Start background capture
            self.sniffer.start()


            print("Packet capture started successfully.")

            return True, "Packet capture started."


        except Exception as error:

            self.running = False

            self.sniffer = None

            print()
            print("CAPTURE START ERROR:")
            print(error)
            print()

            return False, str(error)


    # ---------------------------------------------------------
    # STOP PACKET CAPTURE
    # ---------------------------------------------------------

    def stop(self):

        if not self.running:

            return False, "Capture is not running."


        try:

            if self.sniffer:

                self.sniffer.stop()


            self.sniffer = None

            self.running = False


            print()
            print("Packet capture stopped.")
            print(
                "Packets captured:",
                self.packet_count
            )
            print()


            return True, "Packet capture stopped."


        except Exception as error:

            self.sniffer = None

            self.running = False


            print()
            print("CAPTURE STOP ERROR:")
            print(error)
            print()


            return False, str(error)


    # ---------------------------------------------------------
    # PROCESS EVERY CAPTURED PACKET
    # ---------------------------------------------------------

    def process_packet(self, packet):

        if not self.running:

            return


        try:

            # Convert raw Scapy packet
            # into database-compatible dictionary
            parsed = self.parse_packet(packet)


            if parsed:

                # Save packet to SQLite
                insert_packet(parsed)


                # Increase packet counter
                with self.lock:

                    self.packet_count += 1


                # Display capture information
                print(
                    f"[{parsed['protocol']}] "
                    f"{parsed['source_ip']} "
                    f"-> "
                    f"{parsed['destination_ip']} "
                    f"| "
                    f"{parsed['packet_length']} bytes"
                )


        except Exception as error:

            # IMPORTANT:
            # Never silently hide packet errors
            print(
                "Packet processing error:",
                error
            )


    # ---------------------------------------------------------
    # PARSE PACKET
    # ---------------------------------------------------------

    def parse_packet(self, packet):

        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        source_ip = ""

        destination_ip = ""

        source_port = None

        destination_port = None

        tcp_flags = ""

        protocol = "OTHER"

        info = ""


        # Packet size
        try:

            packet_length = len(packet)

        except Exception:

            packet_length = 0


        # -----------------------------------------------------
        # IPv4
        # -----------------------------------------------------

        if IP in packet:

            source_ip = packet[IP].src

            destination_ip = packet[IP].dst


        # -----------------------------------------------------
        # IPv6
        # -----------------------------------------------------

        elif IPv6 in packet:

            source_ip = packet[IPv6].src

            destination_ip = packet[IPv6].dst


        # -----------------------------------------------------
        # TCP
        # -----------------------------------------------------

        if TCP in packet:

            source_port = int(
                packet[TCP].sport
            )

            destination_port = int(
                packet[TCP].dport
            )


            tcp_flags = str(
                packet[TCP].flags
            )


            # HTTP
            if (
                source_port in (80, 8080)
                or
                destination_port in (80, 8080)
            ):

                protocol = "HTTP"


            # HTTPS
            elif (
                source_port == 443
                or
                destination_port == 443
            ):

                protocol = "HTTPS"


            # Normal TCP
            else:

                protocol = "TCP"


            info = self.tcp_information(
                packet[TCP]
            )


        # -----------------------------------------------------
        # UDP
        # -----------------------------------------------------

        elif UDP in packet:

            source_port = int(
                packet[UDP].sport
            )

            destination_port = int(
                packet[UDP].dport
            )


            # DNS
            if (
                source_port == 53
                or
                destination_port == 53
            ):

                protocol = "DNS"

                info = self.dns_information(
                    packet
                )


            # Normal UDP
            else:

                protocol = "UDP"


        # -----------------------------------------------------
        # ICMP
        # -----------------------------------------------------

        elif ICMP in packet:

            protocol = "ICMP"

            info = "ICMP packet"


        # -----------------------------------------------------
        # DNS
        # -----------------------------------------------------

        elif DNS in packet:

            protocol = "DNS"

            info = self.dns_information(
                packet
            )


        # -----------------------------------------------------
        # Ignore packets without IP address
        # -----------------------------------------------------

        if not source_ip and not destination_ip:

            return None


        # -----------------------------------------------------
        # DATABASE RECORD
        # -----------------------------------------------------

        return {

            "timestamp": timestamp,

            "protocol": protocol,

            "source_ip": source_ip,

            "destination_ip": destination_ip,

            "source_port": source_port,

            "destination_port": destination_port,

            "packet_length": packet_length,

            "tcp_flags": tcp_flags,

            "info": info

        }


    # ---------------------------------------------------------
    # TCP INFORMATION
    # ---------------------------------------------------------

    def tcp_information(self, tcp_layer):

        try:

            flags = str(
                tcp_layer.flags
            )

        except Exception:

            return "TCP packet"


        readable = []


        if "S" in flags:

            readable.append("SYN")


        if "A" in flags:

            readable.append("ACK")


        if "F" in flags:

            readable.append("FIN")


        if "R" in flags:

            readable.append("RST")


        if "P" in flags:

            readable.append("PSH")


        if "U" in flags:

            readable.append("URG")


        if readable:

            return (
                "TCP Flags: "
                +
                ", ".join(readable)
            )


        return "TCP packet"


    # ---------------------------------------------------------
    # DNS INFORMATION
    # ---------------------------------------------------------

    def dns_information(self, packet):

        try:

            if DNSQR in packet:

                query = packet[
                    DNSQR
                ].qname.decode(
                    errors="ignore"
                ).rstrip(".")


                if query:

                    return (
                        "DNS Query: "
                        +
                        query
                    )


        except Exception as error:

            print(
                "DNS parsing error:",
                error
            )


        return "DNS traffic"


    # ---------------------------------------------------------
    # CAPTURE STATUS
    # ---------------------------------------------------------

    def get_status(self):

        duration = 0


        if self.start_time:

            duration = (
                time.time()
                -
                self.start_time
            )


        with self.lock:

            count = self.packet_count


        return {

            "running": self.running,

            "packet_count": count,

            "duration": round(
                duration,
                1
            )

        }


# -------------------------------------------------------------
# GLOBAL PACKET CAPTURE OBJECT
# -------------------------------------------------------------

capture = PacketCapture()
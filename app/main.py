import socket
import struct
from collections import OrderedDict

header_config = OrderedDict(
    {
        "id": 1234,
        "qr": 1,
        "opcode": 0,
        "aa": 0,
        "tc": 0,
        "rd": 0,
        "ra": 0,
        "z": 0,
        "rcode": 0,
        "qdcount": 1, # Number of questions
        "ancount": 1, # Number of answer records
        "nscount": 0,
        "arcount": 1, # Number of additional records
        "name": "codecrafters.io",
        "qtype": 1,
        "qclass": 1,
    }
)


def encode_dns_name(name: str) -> bytes:
    parts = name.split('.')
    encoded = b''
    for part in parts:
        encoded += bytes([len(part)]) + part.encode('ascii')
    encoded += b'\x00'
    return encoded


def generate_response(config, buffer: bytes = None):
    # Pack flags into a single 16-bit integer
    flags = (
        # hex values are bit masks to limit the values to the appropriate bits
        # creates a 16-bit integer with header flags packed
        # << bitwise left shift
        # (1 & 0x1) << 15 returns an integer
        (config["qr"] & 0x1) << 15 # Left shift by 15 positions (add 15 zeros to the right). equivalent to multiplying by 2^15
        | (config["opcode"] & 0xF) << 11 # & 0xF limits the value to 4 bits (0-15)
        | (config["aa"] & 0x1) << 10
        | (config["tc"] & 0x1) << 9
        | (config["rd"] & 0x1) << 8
        | (config["ra"] & 0x1) << 7
        | (config["z"] & 0x7) << 4
        | (config["rcode"] & 0xF)
    )

    pid = struct.unpack(">H", buffer[:2])[0] if buffer else config["id"]

    packed_fields = OrderedDict(
        [
            ("id", pid),
            ("flags", flags),
            ("qdcount", config["qdcount"]),
            ("ancount", config["ancount"]),
            ("nscount", config["nscount"]),
            ("arcount", config["arcount"]),
        ]
    )

    # H = unsigned short (2 bytes)
    # "H" means "give me an integer, I'll convert it to 2 bytes"
    # struct.pack will convert the values into a bytes object
    # big endian is a byte ordering format

    domain_name = encode_dns_name(config["name"])

    # Each \xNN is one byte (8 bits).

    header = struct.pack(">HHHHHH", *packed_fields.values())
    question = domain_name + struct.pack(">HH", config["qtype"], config["qclass"])
    answer = domain_name + struct.pack(">HHIH", config["qtype"], config["qclass"], 60, 4) + b"\x7f\x00\x00\x01"
    return header + question + answer



def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")


    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))

    while True:
        try:
            buf, source = udp_socket.recvfrom(512)
            # buf is a bytes object containing the received data
            # b'*\xb9\x01 \x00\x01\x00\x00\x00\x00\x00\x00\x0ccodecrafters\x02io\x00\x00\x01\x00\x01'
            # * is a byte.
            # first two bytes are the ID

            print(buf)

            response = generate_response(header_config, buffer=buf)

            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()

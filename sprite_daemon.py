from smtplib import SMTP_SSL
import json
import os

SERVER_DETAILS = ('smtp.gmail.com', 465)


def load_details(keys=('username', 'password', 'recipient')):
    credentials_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'credentials.json'
    )
    with open(credentials_file_path) as fd:
        data = json.load(fd)

    return (data[key] for key in keys)


def main():
    username, password, recipient = load_details()

    server = SMTP_SSL(*SERVER_DETAILS)
    server.ehlo()
    server.login(username, password)

    server.sendmail(username, recipient, 'Buy Sprite')

    server.close()


if __name__ == '__main__':
    main()

#!/bin/bash
import os


def main():
    port = 22
    i = str(input("which NASA user is this? (1-6): "))
    hostname = f"NASA{i}"
    username = f"user{i}"

    es = attempt_ssh(username, hostname, port)
    # change hostname to default raspberrypi
    hostname = "raspberrypi"
    es = attempt_ssh(username, hostname, port)

    # change user to default user pi
    username = "pi"
    es = attempt_ssh(username, hostname, port)

    hostname = f"NASA{i}"
    es = attempt_ssh(username, hostname, port)


def attempt_ssh(username, hostname, port):
    print(f"trying ssh hostname: {hostname},  user: {username},  port : {port}")
    try:
        exitStatus = os.system(f"ssh {username}@{hostname} -p {port}")

        if exitStatus != 0:
            print(f"could not connect on ssh for {hostname} using {username}\n\n\n")

    except Exception as e:
        print("fuck.")
        print(e)

    return exitStatus


def checkEs(es):
    print("Exit staus is ", es)
    if es != 0:
        print("an error occurred maybe")


if __name__ == "__main__":
    main()

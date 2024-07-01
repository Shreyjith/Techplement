#SHREYJITH S (PYTHON DEVELOPER TECHPLEMENT)
#WEEK-1 TASK : RANDOM PASSWORD GENERATOR
import string
import os
import argparse 
# ^for string constants,generating random bytes and to parse command line arguments

def gen_random_pass(length, incl_uppercase, incl_lowercase, incl_digits, incl_special):
    if length < 1:
        raise ValueError("Password length must be at least 1") #makes sure that the password length is atleast 1

    character_sets = []
    if incl_uppercase:
        character_sets.append(string.ascii_uppercase)
    if incl_lowercase:
        character_sets.append(string.ascii_lowercase)
    if incl_digits:
        character_sets.append(string.digits)
    if incl_special:
        character_sets.append(string.punctuation) #all the character sets are collected

    if not character_sets:
        raise ValueError("At least one character set must be selected") #makes sure that atleast one character set is selected

    pass_chars = [os.urandom(1)[0] % len(cs) for cs in character_sets]
    password = [cs[p] for p, cs in zip(pass_chars, character_sets)] #makes sure that password includes atleast one character from each selected set

    all_chars = ''.join(character_sets)
    while len(password) < length:
        random_index = os.urandom(1)[0] % len(all_chars)
        password.append(all_chars[random_index]) #the rest of the password is filled with random characters from selected sets

    for i in range(len(password)):
        swap_index = os.urandom(1)[0] % len(password)
        password[i], password[swap_index] = password[swap_index], password[i] #used for shuffling characters to make it more random

    return ''.join(password) #returns the password

def parse_args():
    parser = argparse.ArgumentParser(description='Random Password Generator')
    parser.add_argument('--length', type=int, required=True, help='Length of the password')
    parser.add_argument('--uppercase', action='store_true', help='Include uppercase letters')
    parser.add_argument('--lowercase', action='store_true', help='Include lowercase letters')
    parser.add_argument('--digits', action='store_true', help='Include digits')
    parser.add_argument('--special', action='store_true', help='Include special characters')
    return parser.parse_args()
# ^using argparse library to handle commandline arguments such as length, uppercase,lowercase,digits and special 

def main():
    try:
        args = parse_args()
        password = gen_random_pass(
            length=args.length,
            incl_uppercase=args.uppercase,
            incl_lowercase=args.lowercase,
            incl_digits=args.digits,
            incl_special=args.special
        )
        print(f'Generated password: {password}')
    except ValueError as e:
        print(f'Error: {e}')
    except SystemExit as e:
        print(f'Argument parsing failed: {e}')
        print('Make sure that you run the script in this format: ')
        print('python random_password_generator.py --length LENGTH [--uppercase] [--lowercase] [--digits] [--special]')
# ^try block: calls parse_args() to get commandline arguments; calls gen_random_pass() to generate password with provided options and then print the password generated
# ^except block: for error handling

if __name__ == '__main__':
    main() #to ensre main function runs correctly
from collections import UserDict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import rich.box

console = Console()

class AddressBook(UserDict):
    def search(self, name=None, phone=None):
        results = []
        for record in self.data.values():
            if name and name.lower() in record.name.get_value().lower():
                results.append(record)
            if phone and any(
                phone.lower() == p.get_value().lower() for p in record.fields.get('Phone', [])
            ):
                results.append(record)
        return results


class Record:
    def __init__(self, name):
        self.name = name
        self.fields = {}

    def edit_name(self, new_name):
        self.name.set_value(new_name)

    def add_field(self, field):
        field_name = type(field).__name__
        if field_name not in self.fields:
            self.fields[field_name] = []
        self.fields[field_name].append(field)

    def remove_field(self, field):
        field_name = type(field).__name__
        if field_name in self.fields and field in self.fields[field_name]:
            self.fields[field_name].remove(field)

    def edit_field(self, field, new_value):
        field_name = type(field).__name__
        if field_name in self.fields and field in self.fields[field_name]:
            field.set_value(new_value)

    def get_key(self):
        return self.name.get_value()


class Field:
    def __init__(self, value):
        self.value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class Name(Field):
    pass


class Phone(Field):
    pass


class PhoneBook:
    def __init__(self):
        self.data = {}

    def find(self, **kwargs):
        results = []
        for record in self.data.values():
            for field, value in kwargs.items():
                if field == 'n':
                    if value.lower() in record.name.get_value().lower():
                        results.append(record)
                        break
                elif field == 'p':
                    if any(
                        value.lower() == phone.get_value().lower()
                        for phone in record.fields.get('Phone', [])
                    ):
                        results.append(record)
        return results


    def add_record(self, record):
        key = record.get_key()
        self.data[key] = record
        print(f'Contact "{record.name.get_value()}" has been added.')
        return key


phonebook = PhoneBook()

commands = {
    'hello': 1,
    'add': 2,
    'change': 3,
    'find': 4,
    'show all': 5,
    'good bye': 6,
    'close': 6,
    'exit': 6,
    'edit name': 7, # пасхалки. не зазначені в переліку команд 
    'delete': 8,    # пасхалки. не зазначені в переліку команд
    'end': 0
}


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            print(str(e))
        except Exception:
            print('Command processing error.')

    return wrapper


@input_error
def edit_name_command():
    name = input('Enter contact name: ')
    new_name = input('Enter new name: ')
    if name in phonebook.data:
        contact = phonebook.data[name]
        contact.edit_name(new_name)
        print(f'Name for contact "{name}" has been updated to "{new_name}".')
    else:
        print('Contact not found.')


@input_error
def add_contact(name, *phone_numbers):
    if name in phonebook.data:
        contact = phonebook.data[name]
        for number in phone_numbers:
            contact.add_field(Phone(number))
        print(f'Phone number(s) for contact "{name}" have been added.')
    else:
        record = Record(Name(name))
        for number in phone_numbers:
            record.add_field(Phone(number))

        key = phonebook.add_record(record)
        print(f'Contact with key "{key}" has been added.')


@input_error
def change_phone_number(name, old_phone_number, new_phone_number):
    if name in phonebook.data:
        contact = phonebook.data[name]
        if old_phone_number in [phone.get_value() for phone in contact.fields['Phone']]:
            contact.fields['Phone'] = [
                Phone(new_phone_number) if phone.get_value() == old_phone_number else phone
                for phone in contact.fields['Phone']
            ]
            print(f'Phone number for contact "{name}" has been updated.')
        else:
            print(f'Phone number "{old_phone_number}" not found for contact "{name}".')
    else:
        print('Contact not found.')


@input_error
def get_phone_number(name):
    if name in phonebook.data:
        print(f'Phone number for contact "{name}": {phonebook.data[name].fields["Phone"][0].get_value()}')
    else:
        print('Contact not found.')


def show_all_contacts():
    if phonebook.data:
        console = Console()
        table = Table(show_header=True, header_style="bold", box=rich.box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")

        for record in phonebook.data.values():
            name = record.name.get_value()
            phone_numbers = ', '.join([phone.get_value() for phone in record.fields.get('Phone', [])])
            table.add_row(name, phone_numbers)

        console.print(table)
    else:
        print('No contacts saved.')


def add_contact_command():
    name = input('Enter contact name: ')
    phone_numbers = input('Enter phone number(s) (space-separated): ').split()

    add_contact(name, *phone_numbers)


def change_phone_number_command():
    input_args = input('Give me name, old phone, and new phone with a space please: ').split()
    if len(input_args) != 3:
        print('Incorrect input. Give me name, old phone, and new phone with a space please.')
        return
    name, old_phone_number, new_phone_number = input_args
    change_phone_number(name, old_phone_number, new_phone_number)


def delete_contact_command():
    name = input('Enter contact name: ')
    if name in phonebook.data:
        confirm = input(f'Are you sure you want to delete the contact "{name}"? (yes/no): ')
        if confirm.lower() == 'yes':
            del phonebook.data[name]
            print(f'Contact "{name}" has been deleted.')
        else:
            print('Deletion canceled.')
    else:
        print('Contact not found.')


def display_contact(contact):
    name = contact.name.get_value()
    return f"[b]{name}[/b]"


def find_command():
    search_type = input("Search by name (n) or phone number (p)? ")
    if search_type.lower() == 'n':
        name = input('Enter contact name: ')
        results = phonebook.find(n=name)
    elif search_type.lower() == 'p':
        phone_number = input('Enter phone number: ')
        results = phonebook.find(p=phone_number)
    else:
        print('Invalid search type.')
        return

    if results:
        table = Table(show_header=True, header_style="bold", box=rich.box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")

        for result in results:
            name = display_contact(result)
            phone_numbers = result.fields.get('Phone', [])
            for phone in phone_numbers:
                table.add_row(name, phone.get_value())

        console.print(table)
    else:
        print('No matching contacts found.')


def search_command():
    search_type = input("Search by name (n) or phone number (p)? ")
    if search_type.lower() == 'n':
        name = input('Enter contact name: ')
        results = phonebook.search(name=name)
    elif search_type.lower() == 'p':
        phone_number = input('Enter phone number: ')
        results = phonebook.search(phone=phone_number)
    else:
        print('Invalid search type.')
        return

    if results:
        table = Table(show_header=True, header_style="bold", box=rich.box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")

        for result in results:
            name = display_contact(result)
            table.add_row(name, "")

        console.print(table)
    else:
        print('No matching contacts found.')


def show_all_command():
    show_all_contacts()


def process_command(command):
    if command.isdigit():
        command = int(command)
        if command not in commands.values():
            print('Unknown command. Try one of the following commands:')
            print('1 - hello')
            print('2 - add Give me name and phone with a space')
            print('3 - change Give me name, old phone, and new phone with a space')
            print('4 - find')
            print('5 - show all')
            print('6 - good bye, close, exit, end')
            return True
        command = next((k for k, v in commands.items() if v == command), None)

    command_functions = {
        'hello': lambda: print('How can I help you?'),
        'add': add_contact_command,
        'change': change_phone_number_command,
        'find': find_command,
        'show all': show_all_command,
        'edit name': edit_name_command,
        'delete': delete_contact_command,
        'good bye': lambda: print('Good bye!'),
        'close': lambda: print('Good bye!'),
        'exit': lambda: print('Good bye!'),
        'end': lambda: print('Good bye!')
    }

    command_function = command_functions.get(command)
    if command_function:
        command_function()
        if command in ['good bye', 'close', 'exit', 'end']:
            return False
        return True

    print('Unknown command. Try one of the following commands:')
    print('1 - hello')
    print('2 - add Give me name and phone with a space')
    print('3 - change Give me name, old phone, and new phone with a space')
    print('4 - find')
    print('5 - show all')
    print('6 - good bye, close, exit, end')
    return True


def main():
    print('Hello! This is your phonebook.')
    phonebook = AddressBook()  # Зміна назви класу
    while True:
        user_input = input('Enter the command: ')
        if user_input.lower() in ['good bye', 'close', 'exit', 'end']:
            process_command(user_input.lower())
            break

        if user_input.strip().isdigit() and int(user_input) == 0:
            process_command('end')
            break

        should_continue = process_command(user_input)
        if not should_continue:
            break


if __name__ == '__main__':
    main()
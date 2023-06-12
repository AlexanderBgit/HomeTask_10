from collections import UserDict


class AddressBook(UserDict):
    def search(self, **kwargs):
        result = []
        for record in self.data.values():
            if all(
                field in record.fields and value in record.fields[field].get_values()
                for field, value in kwargs.items()
            ):
                result.append(record)
        return result
    
    def add_record(self, record):
        key = record.get_key()
        self.data[key] = record
        print(f'Contact "{record.name.get_value()}" has been added.')
        return key


class Record:
    def __init__(self, name):
        self.name = name
        self.fields = {}
    
    def add_field(self, field):
        field_name = field.get_field_name()
        if field_name not in self.fields:
            self.fields[field_name] = []
        self.fields[field_name].append(field)
    
    def remove_field(self, field):
        field_name = field.get_field_name()
        if field_name in self.fields and field in self.fields[field_name]:
            self.fields[field_name].remove(field)
    
    def edit_field(self, field, new_value):
        field_name = field.get_field_name()
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
    
    def get_field_name(self):
        return type(self).__name__


class Name(Field):
    pass


class Phone(Field):
    pass


phonebook = AddressBook()

commands = {
    'hello': 1,
    'add': 2,
    'change': 3,
    'phone': 4,
    'show all': 5,
    'good bye': 6,
    'close': 6,
    'exit': 6,
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
def add_contact(name, phone_number):
    record = Record(Name(name))
    record.add_field(Phone(phone_number))
    
    key = phonebook.add_record(record)
    print(f'Contact "{record.name.get_value()}" has been added.')


@input_error
def change_phone_number(name, new_phone_number):
    if name in phonebook.data:
        phonebook.data[name].fields['Phone'][0].set_value(new_phone_number)
        print(f'Phone number for contact "{name}" updated.')
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
        print('Saved contacts:')
        print('-' * 45)
        print('| {:<20} | {:<20} |'.format('Name', 'Phone number'))
        print('-' * 45)
        for record in phonebook.data.values():
            print('| {:<20} | {:<20} |'.format(record.name.get_value(), record.fields['Phone'][0].get_value()))

        print('-' * 45)
    else:
        print('No contacts saved.')


def add_contact_command():
    input_args = input('Give me name and phone with a space please: ').split()
    if len(input_args) != 2:
        print('Incorrect input. Give me name and phone with a space please.')
        return
    name, phone_number = input_args
    
    record = Record(Name(name))
    record.add_field(Phone(phone_number))
    
    key = phonebook.add_record(record)
    print(f'Contact with key "{key}" has been added.')


def change_phone_number_command():
    input_args = input('Give me name and New phone with a space please: ').split()
    if len(input_args) != 2:
        print('Incorrect input. Give me name and New phone with a space please.')
        return
    name, new_phone_number = input_args
    change_phone_number(name, new_phone_number)


def phone_command():
    name = input('Enter user name: ')
    get_phone_number(name)


def show_all_command():
    show_all_contacts()


def process_command(command):
    command_functions = {
        'hello': lambda: print('How can I help you?'),
        'add': add_contact_command,
        'change': change_phone_number_command,
        'phone': phone_command,
        'show all': show_all_command,
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
    print('3 - change Give me name and New phone with a space')
    print('4 - phone Enter user name')
    print('5 - show all')
    print('6 - good bye, close, exit, end')
    return True


def main():
    print("Hello! I'm an assistant app. How can I help?")
    while True:
        user_input = input('Enter the command: ')

        if user_input.isdigit():
            command = next((k for k, v in commands.items() if v == int(user_input)), None)
        else:
            command = user_input

        if command is None:
            print('Unknown command. Try one of the following commands:')
            print('1 - hello')
            print('2 - add Give me name and phone with a space')
            print('3 - change Give me name and New phone with a space')
            print('4 - phone Enter user name')
            print('5 - show all')
            print('6 - good bye, close, exit, end')
            continue

        if not process_command(command):
            break


if __name__ == '__main__':
    main()

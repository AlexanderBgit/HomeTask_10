from collections import UserDict
from rich.console import Console
from rich.table import Table
from rich import box


# Клас Field, який буде батьківським для всіх полів, 
# у ньому потім реалізуємо логіку, загальну для всіх полів.   
class Field:
    def __init__(self, value) -> None:
        self.value = value
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return str(self)

# Клас Name, обов'язкове поле з ім'ям.     
class Name(Field):
    ...

# Клас Phone, необов'язкове поле з телефоном 
# та таких один запис (Record) може містити кілька.   
class Phone(Field):
    ...

# Клас Record, який відповідає за логіку додавання/видалення/редагування 
# необов'язкових полів та зберігання обов'язкового поля Name.
class Record:
    def __init__(self, name: Name, phone: Phone = None) -> None:
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
    
    def add_phone(self, phone: Phone):
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)
            return f"phone {phone} add to contact {self.name}"
        return f"{phone} present in phones of contact {self.name}"
    
    def change_phone(self, old_phone, new_phone):
        for idx, p in enumerate(self.phones):
            if old_phone.value == p.value:
                self.phones[idx] = new_phone
                return f"old phone {old_phone} change to {new_phone}"
        return f"{old_phone} not present in phones of contact {self.name}"

    def change_name(self, new_name: Name):
        self.name = new_name
        return f"Name changed to {new_name} for contact {self.name}"    
    
    def __str__(self) -> str:
        return f"{self.name}: {', '.join(str(p) for p in self.phones)}"


# Клас AddressBook, який наслідується від UserDict, 
# та ми потім додамо логіку пошуку за записами до цього класу.
class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[str(record.name)] = record
        return f"Contact {record} add success"
    
    def delete_record(self, name: str):
        if name in self.data:
            del self.data[name]
            return f"Contact with name '{name}' deleted successfully"
        return f"No contact with name '{name}' in address book"

    def __str__(self) -> str:
        return "\n".join(str(r) for r in self.data.values())
# another module .py


address_book = AddressBook()


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except IndexError as e:
            return e
        except NameError as e:
            return e
    return wrapper


# Record реалізує методи для додавання об'єктів Phone.
@input_error
def add_command(*args):
    name = Name(args[0])
    phone = Phone(args[1])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.add_phone(phone)
    rec = Record(name, phone)
    return address_book.add_record(rec)

# Record реалізує методи для редагування об'єктів Phone.
@input_error
def change_command(*args):
    name = Name(args[0])
    old_phone = Phone(args[1])
    new_phone = Phone(args[2])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.change_phone(old_phone, new_phone)
    return f"No contact {name} in address book"

# Record реалізує методи для редагування об'єктів Phone.
def edit_name_command(*args):
    name = Name(args[0])
    new_name = Name(args[1])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.change_name(new_name)
    return f"No contact {name} in address book"


# Record реалізує методи для видалення об'єктів Phone.
@input_error
def delete_contact_command(*args):
    if args:
        name = args[0]
        return address_book.delete_record(name)
    else:
        return "Please provide a name to delete the contact."


def find_command(*args):
    query = args[0]  # Або номер або ім'я
    
    matching_records = []
    for record in address_book.data.values():
        # Перевірка відповідності запиту імені чи номеру телефону
        if query.lower() in str(record.name).lower()\
              or any(query.lower() in str(phone).lower() for phone in record.phones):
            matching_records.append(record)
    
    if matching_records:
        console = Console()
        table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")

        for record in matching_records:
            name = str(record.name)
            phone_numbers = ', '.join([str(phone) for phone in record.phones])
            table.add_row(name, phone_numbers)

        console.print(table)
    else:
        return f"No records found for the query: {query}"


def exit_command(*args):
    return "Good bye!"
    

def unknown_command(*args):
    pass


def show_all_command(*args):
    if address_book.data:
        console = Console()
        table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")

        for record in address_book.data.values():
            name = str(record.name)
            phone_numbers = ', '.join([str(phone) for phone in record.phones])
            table.add_row(name, phone_numbers)

        console.print(table)
    else:
        print('No contacts saved.')
#     return address_book

def hello_command(*args):
    return "How can I help you?"

COMMANDS = {
    add_command: ("add", "+", "2"),
    change_command: ("change", "зміни", "3"),
    exit_command: ("bye", "exit", "end", "0"),
    delete_contact_command:("del","8"),
    find_command: ("find", "4"),
    show_all_command: ("show all", "5"),
    hello_command:("hello", "1"),
    edit_name_command: ("edit", "7")   
}


def parser(text:str):
    for cmd, kwds in COMMANDS.items():
        for kwd in kwds:
            if text.lower().startswith(kwd):
                # print(cmd)
                data = text[len(kwd):].strip().split()
                # print(data)
                return cmd, data 
    return unknown_command, []


def main():
    while True:
        user_input = input("--->>>")
        
        cmd, data = parser(user_input)
        
        result = cmd(*data)
        
        print(result)
        
        if cmd == exit_command:
            break

if __name__ == "__main__":
    main()
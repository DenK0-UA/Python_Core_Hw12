from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        self._value = None
        self.value = value

    @Field.value.setter
    def value(self, new_value):
        if not new_value.isdigit() or len(new_value) != 10:
            raise ValueError(
                "Phone number must be 10 digits and contain only numbers")
        self._value = new_value


class Birthday(Field):
    def __init__(self, value=None):
        self._value = None
        self.value = value

    @Field.value.setter
    def value(self, new_value):
        if new_value is not None:
            try:
                datetime.strptime(new_value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "Invalid birthday format. Please use YYYY-MM-DD")
        self._value = new_value

    def days_to_birthday(self):
        if self._value is None:
            return None
        today = datetime.now().date()
        birthday = datetime.strptime(
            self._value, "%Y-%m-%d").date().replace(year=today.year)
        if birthday < today:
            birthday = birthday.replace(year=today.year + 1)
        return (birthday - today).days

    def to_string(self):
        date = datetime.strptime(self._value, "%Y-%m-%d")
        return date.strftime('%Y-%m-%d')


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break
        else:
            raise ValueError("Phone number does not exist")

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break
        else:
            raise ValueError("Phone number does not exist")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def search(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                results.append(record)
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
                    break
        return results

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load(self, filename):
        with open(filename, 'rb') as file:
            self.data = pickle.load(file)

    def __iter__(self):
        return iter(self.data.values())


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(e)

    return inner


class Menu:
    def __init__(self):
        self.address_book = AddressBook()
        self.choices = {
            "1": self.show_contacts,
            "2": self.add_contact,
            "3": self.edit_contact,
            "4": self.delete_contact,
            "5": self.find_contact,
            "6": self.days_until_birthday,
            "7": self.search_contacts,
            "8": self.save_address_book,
            "9": self.load_address_book,
            "0": self.quit
        }

    def menu(self):
        print("""
        1. Show contacts
        2. Add contact
        3. Edit contact
        4. Delete contact
        5. Find contact
        6. Days until birthday
        7. Search contacts
        8. Save address book
        9. Load address book             
        0. Quit
        """)

    def run(self):
        while True:
            self.menu()
            choice = input("Enter an option: ")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print(f"{choice} is not a valid choice")

    def show_contacts(self):
        if self.address_book:
            for contact in self.address_book:
                print(contact)
        else:
            print("Address book is empty")

    def days_until_birthday(self):
        name = input("Enter the name of the contact: ")
        contact = self.address_book.find(name)
        if contact:
            birthday = datetime.strptime(
                contact.birthday.to_string(), '%Y-%m-%d')
            today = datetime.today()
            next_birthday = datetime(today.year, birthday.month, birthday.day)
            if today > next_birthday:
                next_birthday = datetime(
                    today.year+1, birthday.month, birthday.day)
            delta = next_birthday - today
            print(f"There are {delta.days} days until {name}'s birthday.")
        else:
            print("Contact not found.")

    @input_error
    def add_contact(self):
        name = input("Enter name: ")
        phones = input("Enter phone numbers separated by space: ").split()
        birthday = input("Enter birthday (optional, format: YYYY-MM-DD): ")
        record = Record(name, birthday)
        for phone in phones:
            record.add_phone(phone)
        self.address_book.add_record(record)

    @input_error
    def edit_contact(self):
        name = input("Enter name: ")
        record = self.address_book.find(name)
        if record:
            phone = input("Enter phone number: ")
            new_phone = input("Enter new phone number: ")
            record.edit_phone(phone, new_phone)
        else:
            print("Contact does not exist")

    @input_error
    def delete_contact(self):
        name = input("Enter name: ")
        self.address_book.delete(name)

    @input_error
    def find_contact(self):
        name = input("Enter name: ")
        record = self.address_book.find(name)
        if record:
            print(record)
        else:
            print("Contact does not exist")

    def search_contacts(self):
        query = input("Enter search query: ")
        results = self.address_book.search(query)
        if results:
            for contact in results:
                print(contact)
        else:
            print("No matching contacts found")

    def save_address_book(self):
        filename = input("Enter filename to save address book: ")
        self.address_book.save(filename)
        print("Address book saved successfully")

    def load_address_book(self):
        filename = input("Enter filename to load address book from: ")
        try:
            self.address_book.load(filename)
            print("Address book loaded successfully")
        except FileNotFoundError:
            print("File not found")

    def quit(self):
        print("Bye")
        exit()


if __name__ == "__main__":
    Menu().run()

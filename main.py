from collections import UserDict
from datetime import datetime
import csv


class Field:
    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return str(self.__value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone number must be 10 digits and contain only numbers")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value=None):
        if value is not None:
            value = self.__validate_birthday(value)
        super().__init__(value)

    def __validate_birthday(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                "Invalid birthday format. Please use the format 'YYYY-MM-DD'")

    @Field.value.setter
    def value(self, new_value):
        if new_value is not None:
            self.__value = self.__validate_birthday(new_value)


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

    def days_to_birthday(self):
        if self.birthday.value is None:
            return None
        today = datetime.today().date()
        next_birthday = datetime(
            today.year, self.birthday.value.month, self.birthday.value.day).date()
        if next_birthday < today:
            next_birthday = datetime(
                today.year + 1, self.birthday.value.month, self.birthday.value.day).date()
        return (next_birthday - today).days

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def save(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for record in self.data.values():
                writer.writerow([record.name.value, record.birthday.value] +
                                [phone.value for phone in record.phones])

    def load(self):
        self.data.clear()
        with open(self.filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0]
                birthday = row[1] if row[1] != '' else None
                phones = row[2:]
                record = Record(name, birthday)
                for phone in phones:
                    record.add_phone(phone)
                self.add_record(record)

    def search(self, query):
        results = []
        for record in self.data.values():
            if query in record.name.value or any(query in phone.value for phone in record.phones):
                results.append(record)
        return results

    def __iter__(self):
        return self.iterator()

    def iterator(self, N=1):
        records = list(self.data.values())
        for i in range(0, len(records), N):
            yield [str(record) for record in records[i:i+N]]


# Example:

# Add a record
address_book = AddressBook("address_book.csv")

# Record 1
record1 = Record("Denis Yevtushenko", "1988-09-26")
record1.add_phone("0637344967")
address_book.add_record(record1)

# Record 2
record2 = Record("Nataliia Yevtushenko", "1987-01-30")
record2.add_phone("0638280932")
address_book.add_record(record2)

# Record 3
record3 = Record("Vasylyna Yevtushenko", "2014-01-04")
record3.add_phone("0930635314")
address_book.add_record(record3)

# Save the address book
address_book.save()

# Search for contacts
results = address_book.search(input("Enter search query: "))
for result in results:
    print(result)

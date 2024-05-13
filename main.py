import os
from abc import ABC, abstractmethod
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import input_dialog

from tough_assistant.address_book import storage_addressbook, contacts, VERSION
from tough_assistant.note_book import storage_notebook, notes
from tough_assistant.commands import command_dict
from tough_assistant.decorators import input_error


class Output(ABC):

    @abstractmethod
    def output_message(self, result):
        pass


class TerminalOutput(Output):

    def __init__(self):
        self.delimiter = '-----'

    def output_message(self, result: str):
        # os.system('cls')
        print(self.delimiter, result, self.delimiter, sep='\n')


class Event:
    _observers = []

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message: str):
        for observer in self._observers:
            observer(message)


@input_error
def parse_input(user_input: str) -> str:
    new_input = user_input
    data = ''
    for key in command_dict:
        if user_input.strip().lower().startswith(key):
            new_input = key
            data = user_input[len(new_input):].split()
            break
    if data:
        return handler(new_input)(*data)
    return handler(new_input)()


def break_func():
    """
    If the user enters a command that is not in the command_dict, then we send back message
    """
    return 'Wrong command!'


def handler(command):
    return command_dict.get(command, break_func)


def main():
    event = Event()
    terminal = TerminalOutput()
    event.register(terminal.output_message)

    version = '{:<15} {}\n{:<15} {}\n{:<15} {}'.format('Tough Assistant', VERSION, 'AddressBook', contacts.version, 'NoteBook', notes.version)
    event.notify(version)

    # terminal.output('Hello. I am your contact-assistant. What should I do with your contacts?')
    event.notify('Hello. I am your contact-assistant. What should I do with your contacts?')

    # print('{:<15} {}\n{:<15} {}\n{:<15} {}\n'.format('Tough Assistant', VERSION, 'AddressBook', contacts.version, 'NoteBook', notes.version))


    completer = WordCompleter(command_dict, ignore_case=True)
    try:
        while True:

            # User request for action
            user_input = prompt("Type 'help' to view available commands. Type 'exit' to exit.\n>>> ", completer=completer)

            # Processing user command
            result = parse_input(user_input)

            # Displaying the result of command processing
            # print(f'{result}\n------\n')
            event.notify(result)
            # Termination condition. The user should enter a command: close | exit | good bye
            if result == 'Good Bye!':
                break
    finally:
        # Upon completion, we save the contacts and notes.
        storage_addressbook.save(contacts)
        storage_notebook.save(notes)
        # print(f'Contacts saved to file: {storage_addressbook.storage.filename}')
        # print(f'Notes saved to file: {storage_addressbook.storage.filename}')
        event.notify(f'Contacts saved to file: {storage_addressbook.storage.filename}')
        event.notify(f'Notes saved to file: {storage_addressbook.storage.filename}')



if __name__ == "__main__":
    main()

from typing import NamedTuple

from draw_command import DrawCommand, DrawCommandType

class Path(NamedTuple):
    commands: list[DrawCommand]

    def to_string(self) -> str:
        return " ".join(command.to_string() for command in self.commands)

    @staticmethod
    def of(data: str):
        commands = []
        last_index = 0
        index = 0
        while index < len(data):
            char = data[index]
            if DrawCommandType.has(char.upper()):
                if last_index < index:
                    commands.append(DrawCommand.of(data[last_index], data[last_index + 1:index]))
                last_index = index
            index += 1
        if last_index < index:
            commands.append(DrawCommand.of(data[last_index], data[last_index + 1:index]))
        return Path(commands)

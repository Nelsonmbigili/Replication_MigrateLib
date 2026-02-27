from dataclasses import dataclass


@dataclass
class API:
    qualified_name: str
    short_name: str
    signature: str
    type: str
    file: str
    line: int
    doc: str

    __is_public: bool = None

    @property
    def id(self):
        return f"{self.qualified_name}__{self.file}__{self.line}"

    @classmethod
    def parse_id(cls, id: str):
        qualified_name, file, line = id.split("__")
        return qualified_name, file, int(line)

    def is_public(self):
        if self.__is_public is None:
            if self.short_name[0] == "_":
                self.__is_public = False
            else:
                parts = self.qualified_name.split(".")
                self.__is_public = not any(part[0] == "_" for part in parts)

        return self.__is_public

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

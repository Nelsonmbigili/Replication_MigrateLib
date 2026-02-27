import time
from typing import Any, Optional, Text, Tuple
from mako.template import Template  # pip install mako

def kb(value: int) -> str:
    return str(value // 1024) + " KB"


def mb(value: int) -> str:
    return str(value // 1024 // 1024) + " MB"


def gb(value: int) -> str:
    return str(value // 1024 / 1024 // 1024) + " GB"


def uptime(boot_time: float) -> str:
    upt = time.time() - boot_time

    retval = ""
    days = int(upt / (60 * 60 * 24))

    if days != 0:
        retval += str(days) + " " + ("days" if days > 1 else "day") + ", "

    minutes = int(upt / 60)
    hours = int(minutes / 60)
    hours %= 24
    minutes %= 60

    if hours != 0:
        retval += str(hours) + ":" + (str(minutes) if minutes >= 10 else "0" + str(minutes))
    else:
        retval += str(minutes) + " min"

    return retval


def uptimesec(boot_time: float) -> int:
    upt = time.time() - boot_time
    return round(upt)


class Formatter:
    '''
    '''
    @classmethod
    def get_format(cls, path: str) -> Tuple[str, Optional[str]]:
        '''
        Tuple would be a better choice for typing
        '''
        i = path.find("{{")
        if i > 0:
            i = path.rfind("/", 0, i)
            if i > 0:
                return (path[0:i], path[i+1:])
        return (path, None)

    @classmethod
    def format(cls, f: str, value: Any) -> Text:
        # Create a Mako template and render it with the provided value and filters
        template = Template(f)
        return template.render(
            **(value if isinstance(value, dict) else {"x": value}),
            KB=kb,
            MB=mb,
            GB=gb,
            uptime=uptime,
            uptimesec=uptimesec
        )

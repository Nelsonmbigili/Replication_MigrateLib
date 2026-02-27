### Explanation of Changes:
The original code uses the `colorama` library for text styling and coloring in the terminal. To migrate to the `termcolor` library:
1. Removed the `colorama` import (`init`, `Fore`, `Style`) and replaced it with `termcolor`'s `colored` function.
2. Replaced all instances of `Fore` and `Style` with equivalent `termcolor` functionality:
   - `Fore.<COLOR>` is replaced with the `colored` function's `color` argument.
   - `Style.DIM` and `Style.NORMAL` are not directly supported in `termcolor`, so they are omitted.
3. Updated the `log` function to use `colored` for text coloring.
4. Adjusted inline color formatting to use `colored` instead of concatenating `Fore` and `Style`.

### Modified Code:
```python
import os
import random
import string
from getpass import getpass

from termcolor import colored

from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator


def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message, color='blue'):
    print(colored(f'[*] {message}', color))


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())


def main():
    log(colored('Starting PyNubank context creation.', 'magenta'))

    device_id = generate_random_id()

    log(f'Generated random id: {device_id}')

    cpf = input('[>] Enter your CPF(Numbers only): ')
    password = getpass('[>] Enter your password (Used on the app/website): ')

    generator = CertificateGenerator(cpf, password, device_id)

    log('Requesting e-mail code')
    try:
        email = generator.request_code()
    except NuException:
        log(colored('Failed to request code. Check your credentials!', 'red'), 'red')
        return

    log(f'Email sent to {colored(email, "grey")}')
    code = input('[>] Type the code received by email: ')

    cert1, cert2 = generator.exchange_certs(code)

    save_cert(cert1, 'cert.p12')

    print(colored('Certificates generated successfully. (cert.pem)', 'green'))
    print(colored('Warning, keep these certificates safe (Do not share or version in git)', 'yellow'))


if __name__ == '__main__':
    main()
```

### Key Changes:
1. **Replaced `Fore` and `Style` with `colored`**:
   - Example: `Fore.BLUE` → `colored(..., 'blue')`
   - Example: `Fore.MAGENTA` → `colored(..., 'magenta')`
   - Removed `Style.DIM` and `Style.NORMAL` as they are not supported in `termcolor`.

2. **Updated `log` function**:
   - The `color` argument now directly maps to `termcolor`'s `colored` function.

3. **Inline color formatting**:
   - Replaced concatenated `Fore` and `Style` with `colored` calls.
   - Example: `f'{Fore.MAGENTA}{Style.DIM}PyNubank{Style.NORMAL}{Fore.LIGHTBLUE_EX}'` → `colored('PyNubank', 'magenta')`.

This ensures the code now uses `termcolor` for terminal text styling while maintaining the original functionality.
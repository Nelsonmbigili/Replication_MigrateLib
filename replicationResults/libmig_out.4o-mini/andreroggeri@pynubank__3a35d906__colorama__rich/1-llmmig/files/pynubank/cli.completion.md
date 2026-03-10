### Explanation of Changes
To migrate the code from using the `colorama` library to the `rich` library, the following changes were made:

1. **Import Statements**: The import statement for `colorama` was removed, and `rich` was imported instead.
2. **Color and Style Handling**: The `rich` library uses a different syntax for coloring text. Instead of using `Fore` and `Style` from `colorama`, we now use `rich`'s `print` function with inline styling.
3. **Initialization**: The `init()` function from `colorama` is not needed when using `rich`, so it was removed.

The modified code reflects these changes while maintaining the original structure and functionality.

### Modified Code
```python
import os
import random
import string
from getpass import getpass

from rich import print

from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator


def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message, color='blue'):
    print(f'[{color}][*] {message}')


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())


def main():
    log(f'Starting [magenta]PyNubank[/magenta] context creation.')

    device_id = generate_random_id()

    log(f'Generated random id: {device_id}')

    cpf = input(f'[>] Enter your CPF(Numbers only): ')
    password = getpass('[>] Enter your password (Used on the app/website): ')

    generator = CertificateGenerator(cpf, password, device_id)

    log('Requesting e-mail code')
    try:
        email = generator.request_code()
    except NuException:
        log(f'[red]Failed to request code. Check your credentials![/red]', 'red')
        return

    log(f'Email sent to [light_black]{email}[/light_black]')
    code = input('[>] Type the code received by email: ')

    cert1, cert2 = generator.exchange_certs(code)

    save_cert(cert1, 'cert.p12')

    print(f'[green]Certificates generated successfully. (cert.pem)[/green]')
    print(f'[yellow]Warning, keep these certificates safe (Do not share or version in git)[/yellow]')


if __name__ == '__main__':
    main()
```
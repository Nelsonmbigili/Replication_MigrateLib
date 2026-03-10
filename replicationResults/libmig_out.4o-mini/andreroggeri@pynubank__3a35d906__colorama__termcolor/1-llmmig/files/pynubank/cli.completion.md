### Explanation of Changes
To migrate the code from using the `colorama` library to the `termcolor` library, the following changes were made:

1. **Import Statement**: The import statement for `colorama` was replaced with the import statement for `termcolor`.
2. **Initialization**: The `init()` function from `colorama` was removed, as `termcolor` does not require any initialization.
3. **Color and Style Usage**: The color and style constants were updated to use `termcolor`'s syntax. Instead of using `Fore` and `Style` from `colorama`, the `colored` function from `termcolor` was used to apply colors and styles directly in the `log` function and other print statements.

### Modified Code
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
    print(colored(f'[*] {message}', color, attrs=['dim']))


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())


def main():
    log(f'Starting {colored("PyNubank", "magenta", attrs=["dim"])} context creation.')

    device_id = generate_random_id()

    log(f'Generated random id: {device_id}')

    cpf = input(f'[>] Enter your CPF(Numbers only): ')
    password = getpass('[>] Enter your password (Used on the app/website): ')

    generator = CertificateGenerator(cpf, password, device_id)

    log('Requesting e-mail code')
    try:
        email = generator.request_code()
    except NuException:
        log(colored('Failed to request code. Check your credentials!', 'red'))
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
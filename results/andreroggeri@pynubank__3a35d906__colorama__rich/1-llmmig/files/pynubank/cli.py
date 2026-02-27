import os
import random
import string
from getpass import getpass

from rich.console import Console
from rich.text import Text

from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator

console = Console()

def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message, color="blue"):
    console.print(f"[*] {message}", style=color)


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())


def main():
    log(f"Starting [magenta dim]PyNubank[/magenta dim] context creation.", color="light_blue")

    device_id = generate_random_id()

    log(f"Generated random id: {device_id}")

    cpf = input(f"[>] Enter your CPF(Numbers only): ")
    password = getpass("[>] Enter your password (Used on the app/website): ")

    generator = CertificateGenerator(cpf, password, device_id)

    log("Requesting e-mail code")
    try:
        email = generator.request_code()
    except NuException:
        log("[red]Failed to request code. Check your credentials![/red]", color="red")
        return

    log(f"Email sent to [light_black]{email}[/light_black]", color="light_blue")
    code = input("[>] Type the code received by email: ")

    cert1, cert2 = generator.exchange_certs(code)

    save_cert(cert1, 'cert.p12')

    console.print("[green]Certificates generated successfully. (cert.pem)[/green]")
    console.print("[yellow]Warning, keep these certificates safe (Do not share or version in git)[/yellow]")


if __name__ == '__main__':
    main()

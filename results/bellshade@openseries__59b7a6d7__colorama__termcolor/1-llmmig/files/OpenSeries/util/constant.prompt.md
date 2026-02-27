The following Python code currently uses the library "colorama" version 0.4.6.
Migrate this code to use the library "termcolor" version 3.0.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "colorama" to "termcolor".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "colorama" and "termcolor".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from colorama import Fore, Style

# bilangan pi adalah nilai konstant dalam matematika yang merupakan perbandingan keliling
# lingkaran dengan diameternya
PI: float = 3.14159265358979323846

# bilangan euler adalah nilai konstant yang dimana nilai kira-kiranya sama dengan 2.71828
# dan dikarakterisasi dalam berbagai cara
BILANGAN_EULER: float = 2.718281828459045235360

# variable ini juga mewakili dari konstanta planck, tetapi dinyatan dalam satuan
# elektron volt per detik (eV/s) nilainya adalah 4.1357 × 10⁻¹⁵ eV s⁻¹
KONSTANTA_PLANCK: float = 4.1357 * pow(10, -15)

# default error dari warna menggunakan kode ANSI escape
# merah
red: str = Fore.RED
# reset kembali warna ke default
reset_warna: str = Style.RESET_ALL

```
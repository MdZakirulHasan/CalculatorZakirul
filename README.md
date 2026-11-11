# Engineering Scientific Calculator V2 (Android / Python)

A multi-tool engineering calculator made with Python and Kivy.

## Modules
- Scientific calculator: DEG/RAD, trig and inverse trig, hyperbolic functions, logarithms, roots, powers, factorial, gamma, constants, Ans and memory.
- Equation solver: quadratic equation (real or complex roots), Newton-Raphson and bisection for `f(x)=0`.
- Calculus: central-difference derivative, numerical two-sided limit estimate, Simpson's 1/3 integration and trapezoidal integration.
- Matrix: addition, subtraction, multiplication, determinant, inverse and transpose.
- Unit conversion: length, mass, pressure, energy, power and temperature.
- Numerical methods: Newton-Raphson and bisection.
- 2D graph plotter for `y=f(x)`.
- Calculation history.

## Run on a computer
Python 3.10 or 3.11 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Build Android APK (Ubuntu / WSL2 recommended)
Buildozer Android packaging is best supported on Linux. On Windows, install WSL2 and Ubuntu first.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip \
  openjdk-17-jdk build-essential autoconf libtool pkg-config \
  zlib1g-dev libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev
```

Then from this project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython
buildozer android debug
```

The first build downloads Android SDK/NDK and may take a while. The APK is generated in `bin/`.
Install on a connected Android device with USB debugging:

```bash
buildozer android deploy run
```

Or transfer the APK from `bin/` to the phone and install it. You may need to permit installation from that source.

## Expression syntax
Use `x` as the independent variable in equation/calculus/graph modules.
Examples: `x^2 + 3*x - 4`, `sin(x)`, `exp(-x^2)`.
Use `*` for multiplication: write `2*x`, not `2x`.
In the scientific calculator, use `sin(30)` in DEG mode or `sin(pi/6)` in RAD mode.

## Important numerical notes
- Derivative uses a central finite difference, not symbolic differentiation.
- Limit is estimated from nearby left/right points; it is not a formal proof and may fail at discontinuities.
- Simpson's rule automatically adjusts an odd number of subintervals to an even number.
- Bisection requires a bracket with opposite signs at the endpoints.
- Newton-Raphson depends on the initial guess and can fail for a zero/near-zero derivative.
- Matrix determinant and inverse require square matrices; inverse is unavailable for singular matrices.
- Graph y-range is currently fixed from -5 to +5.
- This is an engineering numerical calculator, not a computer algebra system (CAS). Verify critical engineering results independently.

## Included files
- `main.py`: Kivy user interface and screens
- `math_engine.py`: expression evaluator and numerical/matrix functions
- `buildozer.spec`: Android package configuration
- `requirements.txt`: desktop Python dependency

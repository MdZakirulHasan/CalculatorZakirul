"""Mathematical engine for Engineering Scientific Calculator."""
import ast
import math
import operator

class MathEngine:
    def __init__(self):
        self.angle_mode = "DEG"
        self.ans = 0.0
        self.memory = 0.0

    def _angle(self, x):
        return math.radians(x) if self.angle_mode == "DEG" else x

    def _out_angle(self, x):
        return math.degrees(x) if self.angle_mode == "DEG" else x

    @staticmethod
    def factorial(x):
        if int(x) != x or x < 0:
            raise ValueError("Factorial requires a non-negative integer")
        return math.factorial(int(x))

    def functions(self):
        return {
            "sin": lambda x: math.sin(self._angle(x)),
            "cos": lambda x: math.cos(self._angle(x)),
            "tan": lambda x: math.tan(self._angle(x)),
            "asin": lambda x: self._out_angle(math.asin(x)),
            "acos": lambda x: self._out_angle(math.acos(x)),
            "atan": lambda x: self._out_angle(math.atan(x)),
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
            "sqrt": math.sqrt, "cbrt": lambda x: math.copysign(abs(x)**(1/3), x),
            "log": math.log10, "ln": math.log, "log2": math.log2,
            "exp": math.exp, "abs": abs, "floor": math.floor, "ceil": math.ceil,
            "factorial": self.factorial, "gamma": math.gamma,
            "degrees": math.degrees, "radians": math.radians,
            "hypot": math.hypot, "atan2": lambda y,x: self._out_angle(math.atan2(y,x)),
            "pow": pow, "min": min, "max": max,
        }

    def evaluate(self, expression, x_value=None):
        expr = expression.replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
        tree = ast.parse(expr, mode="eval")
        names = {"pi": math.pi, "e": math.e, "tau": math.tau,
                 "Ans": self.ans, "M": self.memory}
        if x_value is not None:
            names["x"] = x_value
        names.update(self.functions())
        result = self._eval_node(tree.body, names)
        if isinstance(result, complex):
            return result
        if not math.isfinite(float(result)):
            raise ValueError("Result is not finite")
        return result

    def _eval_node(self, node, names):
        binops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                  ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
                  ast.FloorDiv: operator.floordiv}
        unops = {ast.UAdd: operator.pos, ast.USub: operator.neg}
        if isinstance(node, ast.Constant) and isinstance(node.value, (int,float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in names and not callable(names[node.id]):
                return names[node.id]
            raise ValueError("Unknown variable/constant: " + node.id)
        if isinstance(node, ast.BinOp) and type(node.op) in binops:
            return binops[type(node.op)](self._eval_node(node.left,names), self._eval_node(node.right,names))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unops:
            return unops[type(node.op)](self._eval_node(node.operand,names))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = names.get(node.func.id)
            if not callable(fn) or node.keywords:
                raise ValueError("Unsupported function call")
            return fn(*[self._eval_node(a,names) for a in node.args])
        raise ValueError("Unsupported expression")

    def derivative(self, expr, x, h=1e-5):
        return (self.evaluate(expr, x+h)-self.evaluate(expr, x-h))/(2*h)

    def integrate_simpson(self, expr, a, b, n=1000):
        n = max(2, int(n))
        if n % 2: n += 1
        h = (b-a)/n
        total = self.evaluate(expr, a) + self.evaluate(expr, b)
        total += 4*sum(self.evaluate(expr, a+i*h) for i in range(1,n,2))
        total += 2*sum(self.evaluate(expr, a+i*h) for i in range(2,n,2))
        return total*h/3

    def integrate_trapezoid(self, expr, a, b, n=1000):
        n = max(1, int(n))
        h = (b-a)/n
        total = (self.evaluate(expr,a)+self.evaluate(expr,b))/2
        total += sum(self.evaluate(expr,a+i*h) for i in range(1,n))
        return total*h

    def bisection(self, expr, a, b, tol=1e-10, max_iter=200):
        fa, fb = self.evaluate(expr,a), self.evaluate(expr,b)
        if fa == 0: return a, 0
        if fb == 0: return b, 0
        if fa*fb > 0: raise ValueError("f(a) and f(b) must have opposite signs")
        for i in range(1,max_iter+1):
            c=(a+b)/2; fc=self.evaluate(expr,c)
            if abs(fc)<tol or abs(b-a)/2<tol: return c,i
            if fa*fc<0: b,fb=c,fc
            else: a,fa=c,fc
        return (a+b)/2,max_iter

    def newton(self, expr, x0, tol=1e-10, max_iter=100):
        x=x0
        for i in range(1,max_iter+1):
            fx=self.evaluate(expr,x)
            d=self.derivative(expr,x)
            if abs(d)<1e-14: raise ValueError("Derivative is zero; Newton method stopped")
            xn=x-fx/d
            if abs(xn-x)<tol: return xn,i
            x=xn
        return x,max_iter

    def quadratic(self, a,b,c):
        if abs(a)<1e-15:
            if abs(b)<1e-15: raise ValueError("Not a valid linear/quadratic equation")
            return [-c/b]
        d=b*b-4*a*c
        if d>=0:
            return [(-b+math.sqrt(d))/(2*a),(-b-math.sqrt(d))/(2*a)]
        return [complex(-b/(2*a),math.sqrt(-d)/(2*a)),
                complex(-b/(2*a),-math.sqrt(-d)/(2*a))]

def matrix_parse(text):
    rows=[]
    for line in text.strip().splitlines():
        vals=[float(v.strip()) for v in line.replace(",", " ").split()]
        if vals: rows.append(vals)
    if not rows: raise ValueError("Enter matrix rows, e.g. 1 2; 3 4")
    if any(len(r)!=len(rows[0]) for r in rows): raise ValueError("All matrix rows must have equal length")
    return rows

def matrix_add(A,B,sign=1):
    if len(A)!=len(B) or len(A[0])!=len(B[0]): raise ValueError("Matrix dimensions must match")
    return [[A[i][j]+sign*B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def matrix_multiply(A,B):
    if len(A[0])!=len(B): raise ValueError("Columns of A must equal rows of B")
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

def matrix_det(A):
    n=len(A)
    if n!=len(A[0]): raise ValueError("Determinant requires a square matrix")
    M=[r[:] for r in A]; det=1
    for i in range(n):
        pivot=max(range(i,n),key=lambda r:abs(M[r][i]))
        if abs(M[pivot][i])<1e-14: return 0.0
        if pivot!=i: M[i],M[pivot]=M[pivot],M[i]; det*=-1
        p=M[i][i]; det*=p
        for r in range(i+1,n):
            f=M[r][i]/p
            for c in range(i+1,n): M[r][c]-=f*M[i][c]
    return det

def matrix_inverse(A):
    n=len(A)
    if n!=len(A[0]): raise ValueError("Inverse requires a square matrix")
    M=[A[i][:]+[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda r:abs(M[r][i]))
        if abs(M[pivot][i])<1e-14: raise ValueError("Matrix is singular")
        M[i],M[pivot]=M[pivot],M[i]
        p=M[i][i]; M[i]=[v/p for v in M[i]]
        for r in range(n):
            if r!=i:
                f=M[r][i]; M[r]=[M[r][c]-f*M[i][c] for c in range(2*n)]
    return [r[n:] for r in M]

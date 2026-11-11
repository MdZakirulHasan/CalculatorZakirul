import math
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from math_engine import MathEngine, matrix_parse, matrix_add, matrix_multiply, matrix_det, matrix_inverse

BG=(0.035,0.055,0.085,1); PANEL=(0.075,0.105,0.15,1)
BLUE=(0.08,0.36,0.62,1); KEY=(0.12,0.17,0.24,1); GREEN=(0.12,0.43,0.34,1)

class GraphWidget(Widget):
    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs); self.engine=engine; self.expr="sin(x)"; self.xmin=-10; self.xmax=10
        self.bind(pos=self.redraw,size=self.redraw)
    def plot(self, expr, xmin, xmax):
        self.expr=expr; self.xmin=xmin; self.xmax=xmax; self.redraw()
    def redraw(self,*args):
        self.canvas.clear()
        if self.width<10 or self.height<10: return
        with self.canvas:
            Color(0.10,0.15,0.21,1); Rectangle(pos=self.pos,size=self.size)
            x0,y0=self.x+dp(30),self.y+dp(20); w=self.width-dp(45); h=self.height-dp(35)
            Color(0.35,0.42,0.50,1); Line(rectangle=(x0,y0,w,h),width=1)
            # axes
            def px(x): return x0+(x-self.xmin)/(self.xmax-self.xmin)*w
            ymin,ymax=-5,5
            def py(y): return y0+(y-ymin)/(ymax-ymin)*h
            Color(0.40,0.48,0.58,0.8)
            if self.xmin<=0<=self.xmax: Line(points=[px(0),y0,px(0),y0+h],width=1)
            if ymin<=0<=ymax: Line(points=[x0,py(0),x0+w,py(0)],width=1)
            pts=[]; last_valid=False
            for i in range(501):
                x=self.xmin+(self.xmax-self.xmin)*i/500
                try:
                    y=float(self.engine.evaluate(self.expr,x))
                    if not math.isfinite(y) or abs(y)>1e4: raise ValueError()
                    pts.extend([px(x),py(max(ymin,min(ymax,y)))]); last_valid=True
                except Exception:
                    if len(pts)>=4:
                        Color(0.20,0.85,0.70,1); Line(points=pts,width=1.6)
                    pts=[]; last_valid=False
            if len(pts)>=4:
                Color(0.20,0.85,0.70,1); Line(points=pts,width=1.6)

class CalculatorApp(App):
    def build(self):
        self.title="Engineering Scientific Calculator"
        Window.clearcolor=BG
        self.eng=MathEngine(); self.history=[]
        self.root=BoxLayout(orientation="vertical",padding=dp(8),spacing=dp(6))
        top=BoxLayout(size_hint_y=None,height=dp(42))
        top.add_widget(Label(text="ENGINEERING SCIENTIFIC",bold=True,color=(.55,.82,1,1),font_size="15sp"))
        self.mode=Button(text="DEG",size_hint_x=None,width=dp(65),background_normal="",background_color=BLUE)
        self.mode.bind(on_release=self.toggle_angle); top.add_widget(self.mode)
        self.root.add_widget(top)
        self.nav=GridLayout(cols=4,size_hint_y=None,height=dp(84),spacing=dp(4))
        for name in ["Calc","Equation","Calculus","Matrix","Units","Numerical","Graph","History"]:
            b=self.btn(name,self.show_page,KEY,13); b.page=name; self.nav.add_widget(b)
        self.root.add_widget(self.nav)
        self.body=BoxLayout(orientation="vertical",spacing=dp(6))
        self.root.add_widget(self.body)
        self.show_page("Calc")
        return self.root

    def btn(self,text,callback,color=KEY,size=15):
        b=Button(text=text,font_size=f"{size}sp",bold=True,background_normal="",background_color=color,color=(1,1,1,1))
        b.bind(on_release=lambda *_: callback(text))
        return b
    def field(self,hint="",text="",height=dp(44),multi=False):
        return TextInput(hint_text=hint,text=text,multiline=multi,size_hint_y=None,height=height,
                         font_size="16sp",padding=dp(9),background_color=PANEL,foreground_color=(1,1,1,1),
                         hint_text_color=(.55,.62,.7,1),cursor_color=(.4,.8,1,1))
    def label(self,text="",height=dp(34),size=15,color=(.85,.9,.96,1)):
        return Label(text=text,size_hint_y=None,height=height,font_size=f"{size}sp",color=color,
                     halign="left",valign="middle")
    def result(self,text):
        self.out.text=str(text)
    def show_page(self,page):
        self.page=page; self.body.clear_widgets()
        if page=="Calc": self.page_calc()
        elif page=="Equation": self.page_equation()
        elif page=="Calculus": self.page_calculus()
        elif page=="Matrix": self.page_matrix()
        elif page=="Units": self.page_units()
        elif page=="Numerical": self.page_numerical()
        elif page=="Graph": self.page_graph()
        elif page=="History": self.page_history()

    def add_output(self):
        self.out=self.label("Ready",dp(58),17,(.35,.9,.72,1)); self.body.add_widget(self.out)
    def page_calc(self):
        self.expr=self.field("Expression (e.g. sin(30)+log(100))",height=dp(60)); self.body.add_widget(self.expr)
        self.add_output()
        rows=[
          ["sin(","cos(","tan(","asin(","acos("],
          ["atan(","sinh(","cosh(","tanh(","sqrt("],
          ["log(","ln(","log2(","exp(","factorial("],
          ["π","e","(",")","^"],
          ["7","8","9","÷","⌫"],["4","5","6","×","AC"],["1","2","3","−","+"],
          ["0",".","Ans","M","="]]
        g=GridLayout(cols=5,spacing=dp(4))
        for row in rows:
            for key in row:
                g.add_widget(self.btn(key,self.calc_key,BLUE if key=="=" else (GREEN if key=="AC" else KEY),14))
        self.body.add_widget(g)
        mem=GridLayout(cols=4,size_hint_y=None,height=dp(42),spacing=dp(4))
        for k in ["M+","MR","MC","History"]:
            mem.add_widget(self.btn(k,self.calc_key,KEY,13))
        self.body.add_widget(mem)
    def calc_key(self,k):
        if k=="=":
            try:
                v=self.eng.evaluate(self.expr.text); s=f"{v:.12g}" if isinstance(v,float) else str(v)
                self.eng.ans=v; self.expr.text=s; self.result("= "+s); self.history.insert(0,f"{s} ← {self.expr.text}")
            except Exception as e: self.result("Error: "+str(e))
        elif k=="AC": self.expr.text=""; self.result("Cleared")
        elif k=="⌫": self.expr.text=self.expr.text[:-1]
        elif k=="M+": 
            try: self.eng.memory=float(self.eng.evaluate(self.expr.text)); self.result("Stored in memory")
            except Exception as e: self.result("Error: "+str(e))
        elif k=="MR": self.expr.text+="M"
        elif k=="MC": self.eng.memory=0; self.result("Memory cleared")
        elif k=="History": self.show_page("History")
        elif k=="π": self.expr.text+="pi"
        elif k=="Ans": self.expr.text+="Ans"
        elif k=="M": self.expr.text+="M"
        else: self.expr.text+=k

    def toggle_angle(self,*_):
        self.eng.angle_mode="RAD" if self.eng.angle_mode=="DEG" else "DEG"; self.mode.text=self.eng.angle_mode

    def page_equation(self):
        self.body.add_widget(self.label("Quadratic equation: ax² + bx + c = 0",dp(35),16))
        self.a=self.field("a coefficient","1"); self.b=self.field("b coefficient","-3"); self.c=self.field("c coefficient","2")
        for f in [self.a,self.b,self.c]: self.body.add_widget(f)
        self.body.add_widget(self.btn("Solve quadratic",self.solve_quad,BLUE))
        self.body.add_widget(self.label("General equation f(x) = 0",dp(35),16))
        self.eq=self.field("f(x), use x; e.g. x^3 - 2*x - 5"); self.x0=self.field("Initial guess / lower bound","2")
        self.body.add_widget(self.eq); self.body.add_widget(self.x0)
        self.body.add_widget(self.btn("Solve using Newton-Raphson",self.solve_newton,GREEN))
        self.body.add_widget(self.btn("Solve using Bisection (use x0 as a, add b below)",self.solve_bisect,BLUE))
        self.xb=self.field("Upper bound b","3"); self.body.add_widget(self.xb); self.add_output()
    def solve_quad(self,*_):
        try:
            roots=self.eng.quadratic(float(self.a.text),float(self.b.text),float(self.c.text))
            self.result("Roots: "+", ".join(str(round(r.real,10))+(" ± "+str(round(abs(r.imag),10))+"i" if r.imag else "") if isinstance(r,complex) else f"{r:.10g}" for r in roots))
        except Exception as e: self.result("Error: "+str(e))
    def solve_newton(self,*_):
        try:
            root,n=self.eng.newton(self.eq.text,float(self.x0.text)); self.result(f"Root ≈ {root:.12g}  | iterations: {n}")
        except Exception as e: self.result("Error: "+str(e))
    def solve_bisect(self,*_):
        try:
            root,n=self.eng.bisection(self.eq.text,float(self.x0.text),float(self.xb.text)); self.result(f"Root ≈ {root:.12g}  | iterations: {n}")
        except Exception as e: self.result("Error: "+str(e))

    def page_calculus(self):
        self.body.add_widget(self.label("Numerical calculus (define f(x) using x)",dp(35),16))
        self.cexpr=self.field("f(x), e.g. x^2 + sin(x)","x^2")
        self.cx=self.field("Point x (derivative / limit)","2")
        self.ca=self.field("Lower integration limit a","0"); self.cb=self.field("Upper integration limit b","1")
        self.cn=self.field("Subintervals (even for Simpson)","1000")
        for f in [self.cexpr,self.cx,self.ca,self.cb,self.cn]: self.body.add_widget(f)
        g=GridLayout(cols=2,spacing=dp(5),size_hint_y=None,height=dp(96))
        for name,fn in [("Derivative",self.do_derivative),("Limit",self.do_limit),("Simpson 1/3",self.do_simpson),("Trapezoidal",self.do_trap)]:
            g.add_widget(self.btn(name,fn,BLUE,13))
        self.body.add_widget(g); self.add_output()
    def do_derivative(self,*_):
        try: self.result(f"f'({self.cx.text}) ≈ {self.eng.derivative(self.cexpr.text,float(self.cx.text)):.12g}")
        except Exception as e: self.result("Error: "+str(e))
    def do_limit(self,*_):
        try:
            x=float(self.cx.text); h=1e-4
            left=self.eng.evaluate(self.cexpr.text,x-h); right=self.eng.evaluate(self.cexpr.text,x+h)
            self.result(f"Left ≈ {left:.10g} | Right ≈ {right:.10g} | two-sided ≈ {(left+right)/2:.10g}")
        except Exception as e: self.result("Limit estimate error: "+str(e))
    def do_simpson(self,*_):
        try: self.result(f"Simpson's 1/3 ≈ {self.eng.integrate_simpson(self.cexpr.text,float(self.ca.text),float(self.cb.text),int(self.cn.text)):.12g}")
        except Exception as e: self.result("Error: "+str(e))
    def do_trap(self,*_):
        try: self.result(f"Trapezoidal ≈ {self.eng.integrate_trapezoid(self.cexpr.text,float(self.ca.text),float(self.cb.text),int(self.cn.text)):.12g}")
        except Exception as e: self.result("Error: "+str(e))

    def page_matrix(self):
        self.body.add_widget(self.label("Matrix input: one row per line; values separated by spaces or commas",dp(45),14))
        self.ma=self.field("Matrix A","1 2\n3 4",dp(115),True); self.mb=self.field("Matrix B","5 6\n7 8",dp(115),True)
        self.body.add_widget(self.ma); self.body.add_widget(self.mb)
        g=GridLayout(cols=3,spacing=dp(5),size_hint_y=None,height=dp(100))
        for name in ["A + B","A − B","A × B","det(A)","A inverse","Transpose A"]:
            g.add_widget(self.btn(name,self.matrix_action,BLUE,13))
        self.body.add_widget(g); self.add_output()
    def matrix_action(self,action):
        try:
            A=matrix_parse(self.ma.text); B=matrix_parse(self.mb.text)
            if action=="A + B": v=matrix_add(A,B)
            elif action=="A − B": v=matrix_add(A,B,-1)
            elif action=="A × B": v=matrix_multiply(A,B)
            elif action=="det(A)": v=matrix_det(A)
            elif action=="A inverse": v=matrix_inverse(A)
            else: v=[list(r) for r in zip(*A)]
            self.result("\n".join("  ".join(f"{x:.6g}" for x in row) for row in v) if isinstance(v,list) else f"{v:.12g}")
        except Exception as e: self.result("Error: "+str(e))

    def page_units(self):
        self.body.add_widget(self.label("Engineering unit converter",dp(35),17))
        self.unit_category=self.field("Category: length, mass, pressure, energy, power, temperature","pressure")
        self.unit_value=self.field("Value","1")
        self.unit_from=self.field("From unit (e.g. bar)","bar")
        self.unit_to=self.field("To unit (e.g. Pa)","Pa")
        for f in [self.unit_category,self.unit_value,self.unit_from,self.unit_to]: self.body.add_widget(f)
        self.body.add_widget(self.btn("Convert",self.convert_unit,GREEN)); self.add_output()
        self.body.add_widget(self.label("Supported: length (m, km, cm, mm, ft, in), mass (kg, g, lb), pressure (Pa, kPa, MPa, bar, atm, psi), energy (J, kJ, cal, kcal), power (W, kW, hp), temperature (C, F, K)",dp(105),12))
    def convert_unit(self,*_):
        try:
            cat=self.unit_category.text.strip().lower(); val=float(self.unit_value.text); u=self.unit_from.text.strip(); v=self.unit_to.text.strip()
            scales={
             "length":{"m":1,"km":1000,"cm":.01,"mm":.001,"ft":.3048,"in":.0254},
             "mass":{"kg":1,"g":.001,"lb":.45359237},
             "pressure":{"Pa":1,"kPa":1000,"MPa":1e6,"bar":1e5,"atm":101325,"psi":6894.757293},
             "energy":{"J":1,"kJ":1000,"cal":4.184,"kcal":4184},
             "power":{"W":1,"kW":1000,"hp":745.699872}}
            if cat=="temperature":
                def to_k(x,unit):
                    return x+273.15 if unit=="C" else (x-32)*5/9+273.15 if unit=="F" else x if unit=="K" else (_ for _ in ()).throw(ValueError("Use C, F or K"))
                k=to_k(val,u); out=k-273.15 if v=="C" else (k-273.15)*9/5+32 if v=="F" else k if v=="K" else None
                if out is None: raise ValueError("Use C, F or K")
            else:
                table=scales[cat]; out=val*table[u]/table[v]
            self.result(f"{val:g} {u} = {out:.12g} {v}")
        except Exception as e: self.result("Conversion error: "+str(e))

    def page_numerical(self):
        self.body.add_widget(self.label("Numerical methods – solve f(x) = 0",dp(35),16))
        self.nexpr=self.field("f(x)","x^3 - x - 2")
        self.na=self.field("Initial guess x₀ / lower a","1.5")
        self.nb=self.field("Upper bound b (bisection only)","2")
        for f in [self.nexpr,self.na,self.nb]: self.body.add_widget(f)
        g=GridLayout(cols=2,spacing=dp(5),size_hint_y=None,height=dp(95))
        g.add_widget(self.btn("Newton-Raphson",self.num_newton,BLUE,13))
        g.add_widget(self.btn("Bisection",self.num_bisect,BLUE,13))
        self.body.add_widget(g); self.add_output()
        self.body.add_widget(self.label("Newton-Raphson uses a numerical central-difference derivative. Bisection requires a sign change over [a,b].",dp(70),12))
    def num_newton(self,*_):
        try:
            r,n=self.eng.newton(self.nexpr.text,float(self.na.text)); self.result(f"Root = {r:.12g}; iterations = {n}")
        except Exception as e: self.result("Error: "+str(e))
    def num_bisect(self,*_):
        try:
            r,n=self.eng.bisection(self.nexpr.text,float(self.na.text),float(self.nb.text)); self.result(f"Root = {r:.12g}; iterations = {n}")
        except Exception as e: self.result("Error: "+str(e))

    def page_graph(self):
        self.body.add_widget(self.label("2D function plotter – y = f(x)",dp(35),16))
        row=BoxLayout(size_hint_y=None,height=dp(45),spacing=dp(4))
        self.gexpr=self.field("f(x)","sin(x)",dp(45)); row.add_widget(self.gexpr)
        self.gmin=self.field("xmin","-10",dp(45)); self.gmin.size_hint_x=.45; row.add_widget(self.gmin)
        self.gmax=self.field("xmax","10",dp(45)); self.gmax.size_hint_x=.45; row.add_widget(self.gmax)
        self.body.add_widget(row)
        self.graph=GraphWidget(self.eng,size_hint_y=1); self.body.add_widget(self.graph)
        self.body.add_widget(self.btn("Plot function",self.draw_graph,GREEN))
        self.draw_graph()
    def draw_graph(self,*_):
        try: self.graph.plot(self.gexpr.text,float(self.gmin.text),float(self.gmax.text))
        except Exception as e: self.popup(str(e))

    def page_history(self):
        self.body.add_widget(self.label("Recent calculations",dp(35),17))
        sc=ScrollView(); lab=Label(text="\n\n".join(self.history) if self.history else "No calculations yet",
             size_hint_y=None,halign="left",valign="top",color=(1,1,1,1))
        lab.bind(texture_size=lambda w,s:setattr(w,"size",s)); sc.add_widget(lab); self.body.add_widget(sc)
        self.body.add_widget(self.btn("Clear history",self.clear_history,BLUE))
    def clear_history(self,*_): self.history=[]; self.show_page("History")
    def popup(self,msg):
        p=Popup(title="Information",content=Label(text=msg),size_hint=(.85,.35))
        p.open()

if __name__=="__main__":
    CalculatorApp().run()

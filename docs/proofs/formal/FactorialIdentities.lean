/- Universal polynomial identities for falling-factorial products.
   Expectation, Poisson sampling and concentration are not formalized here. -/
import Std

set_option maxHeartbeats 5000000

namespace FactorialCheckpoint

def f2 (x : Int) : Int := x * (x - 1)
def f3 (x : Int) : Int := x * (x - 1) * (x - 2)
def f4 (x : Int) : Int := x * (x - 1) * (x - 2) * (x - 3)
def f5 (x : Int) : Int := x * (x - 1) * (x - 2) * (x - 3) * (x - 4)
def f6 (x : Int) : Int := x * (x - 1) * (x - 2) * (x - 3) * (x - 4) * (x - 5)

theorem product11 (x : Int) : x*x = f2 x + x := by
  unfold f2
  grind

theorem product12 (x : Int) : x*f2 x = f3 x + 2*f2 x := by
  unfold f2 f3
  grind

theorem product13 (x : Int) : x*f3 x = f4 x + 3*f3 x := by
  unfold f3 f4
  grind

theorem product22 (x : Int) : f2 x*f2 x = f4 x + 4*f3 x + 2*f2 x := by
  unfold f2 f3 f4
  grind

theorem product23 (x : Int) : f2 x*f3 x = f5 x + 6*f4 x + 6*f3 x := by
  unfold f2 f3 f4 f5
  grind

theorem product33 (x : Int) : f3 x*f3 x = f6 x + 9*f5 x + 18*f4 x + 6*f3 x := by
  unfold f3 f4 f5 f6
  grind

#print axioms product11
#print axioms product12
#print axioms product13
#print axioms product22
#print axioms product23
#print axioms product33

end FactorialCheckpoint

import asts
import scanner
import parser
import typecheck
import bindings

if __name__ == "__main__":
    omega_add_func_decl = \
    """
        func add(x: int, y: int): int {
            return x + y
        }
    """
    omega_sub_func_decl = \
    """
        func subtract(x: int, y: int): int {
            return x - y
        }
    """
    omega_mult_func_decl = \
    """
        func multiply(x: int, y:int):int {
            return x*y
        }
    """
    omega_div_func_decl = \
    """
        func divide(x:int, y:int):int {
            return x/ y
        }
    """
    silly = \
    """
    func silly(x:int, y:[]int):int {
        {
            var x : int
            x = 3
            y[0+x-x] = x+x*x
            print x
            print y
        }
        {
            var y : bool
            y = x < x+2
            print y
        }
        return x
    }

    func fact(x:int):int {
        if x == 0 {return 1}
        else {return x * fact(x-1)}
    }

    func main(x:int) {
        var a : [1]int
        a[0] = 7
        print silly(x,a)
        print fact(x)
    }
    """

    omega_sources = [
        omega_sub_func_decl,
        omega_add_func_decl,
        omega_mult_func_decl,
        omega_div_func_decl,
        f"{omega_add_func_decl}\n{omega_sub_func_decl}\n"+\
        f"{omega_mult_func_decl}\n{omega_div_func_decl}\n",
        silly
    ]

    for omega_source in omega_sources:
        lexer = scanner.Scanner(omega_source)
        psr = parser.Parser(lexer)
        tree: asts.Program = psr.program()
        bindings.program(tree)
        typecheck.program(tree)
        print(f"=== Input ===\n{omega_source}\n=== Tree ===\n")
        tree.pprint("")


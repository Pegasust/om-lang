import math
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
    occurences = \
    """
    func occurences(a: [] int, k:int):int{
        var l : int
        var i : int 
        var occr : int
        occr = 0
        i = 0
        l = 5
        while i < l{
            if a[i] == k{
                occr = occr + 1
            }
            i = i + 1
        }
        print occr
        return 0
    }
    func main (){
        var array : [5] int
        var i : int
        var k : int
        k = 5
        array[0] = 5
        array[1] = 1
        array[2] = 4
        array[3] = 2
        array[4] = 5
        call occurences(array, k)
    }
    """
    smallest_elem = \
    """
    func smallestElement(a : [] int):int{
        var l : int
        var i : int
        var smallest: int
        smallest = a[0]
        l = 4
        i = 0
        while i < l{
            if a[i] < smallest{
                smallest = a[i]
            }
            i = i + 1

        }
        print smallest
        return 0
    }
    func main(){
        var array : [4] int
        var i : int
        array[0] = 5
        array[1] = 1
        array[2] = 4
        array[3] = 2
        call smallestElement(array)
    }
    """
    largest_elem = \
    """
    func largestElement(a : [] int):int{
        var l : int
        var i : int
        var largest: int
        largest = a[0]
        l = 4
        i = 0
        while i < l{
            if a[i] > largest{
                largest = a[i]
            }
            i = i + 1

        }
        print largest
        return 0
    }

    func main(){
        var array : [4] int
        var i : int
        array[0] = 5
        array[1] = 1
        array[2] = 4
        array[3] = 2
        call largestElement(array)

    }
    """
    bubblesort = \
    """
    func printSortedArray(sortedArray : [] int):int{
        var l : int
        var n: int
        n = 4
        l = 0
        while l < 4{
            print sortedArray[l]
            l = l + 1
        }
        return 0
    }
    func bubblesort(a : [] int):int{
        var n : int
        var i : int
        var j : int
        var temp: int
        n = 4 
        i = 0
        j = 0
        while i < n{
            j = 0
            while j < n-i-1{
                if a[j] > a[j+1]{
                    temp = a[j]
                    a[j] = a[j+1]
                    a[j+1] = temp
                }
                j = j+1
            }
            i = i+1
        }
        call printSortedArray(a)
        return 0
    }
    func main(){
        var array : [4] int
        var i : int
        array[0] = 5
        array[1] = 1
        array[2] = 4
        array[3] = 2
        call bubblesort(array)

    }
    """
    omega_sources = [
        omega_sub_func_decl,
        omega_add_func_decl,
        omega_mult_func_decl,
        omega_div_func_decl,
        f"{omega_add_func_decl}\n{omega_sub_func_decl}\n"+\
        f"{omega_mult_func_decl}\n{omega_div_func_decl}\n",
        silly,
        occurences,
        smallest_elem,
        largest_elem,
        bubblesort
    ]

    for omega_source in omega_sources:
        lines = omega_source.splitlines()
        digits = math.ceil(math.log10(len(lines)+1))
        line_sep_src = "\n".join([f"{str(idx+1).zfill(digits)} {line}" 
                                     for idx, line in enumerate(lines)])
        print(f"=== Input ===\n{line_sep_src}")
        lexer = scanner.Scanner(omega_source)
        psr = parser.Parser(lexer)
        tree: asts.Program = psr.program()
        bindings.program(tree)
        typecheck.program(tree)
        print(f"=== Tree ===\n")
        tree.pprint("")


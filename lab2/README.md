# ECE358 Lab 2 (Using Python)

## Use Case
The Makefile can be used to simply run the Python script:

> make

The Python file itself can also be run using Python3. Running:

> python3 lab2.py --help

will give the following:

> usage: lab2.py [-h] [-A a] [-T t] [-P]
>
> Simulate CSMA/CD of nodes (ECE358 Lab 2)
> 
> optional arguments:
>   -h, --help            show this help message and exit
>   -A a, --arrival\_rate a
>                         Average packet arrival rate [packets/second]
>   -T t, --time t        Time of the simulation
>   -P, --non\_persistent  Non-persistent CSMA/CD simulation (default:
>                         persistent)

To run the test for the persistent CSMA/CD simulation with A = 7, 10, 20:
> python3 py\_lab1.py -A 7
> python3 py\_lab1.py -A 10
> python3 py\_lab1.py -A 20

To run the test for the non-persistent CSMA/CD simulation with A = 7, 10, 20:
> python3 py\_lab1.py --non\_persistent -A 7
> python3 py\_lab1.py --non\_persistent -A 10
> python3 py\_lab1.py --non\_persistent -A 20


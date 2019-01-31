# ECE358 Lab 1 (Using Python)

## Use Case
The Makefile can be used to simply run the Python script:

> make

The Python file itself can also be run using Python3. Running:

> python3 py\_lab1.py --help

will give the following:

> usage: py\_lab1.py \[-h] \[-K n] \[-T t] \[-R r] \[-Q1]
>
> Simulate networking packet buffer (ECE358 Lab1)
> 
> optional arguments:
>   -h, --help            show this help message and exit
>   -K n, --queue\_size n  Size of the queue/buffer (default: infinite)
>   -T t, --time\_units t  Time units to run each simulation for
>   -R r, --rho r         Rho value to simulate (no value implies range from
>                         [0.4, 10])
>   -Q1, --question1      Calculate the values for question 1

To run the test for question 1:
> python3 py\_lab1.py -Q1

To run the test for question 3:
> python3 py\_lab1.py

To run the test for question 4:
> python3 py\_lab.py -R 1.2

To run the test for question 6:
> python3 py\_lab.py -K 10
> python3 py\_lab.py -K 25
> python3 py\_lab.py -K 50


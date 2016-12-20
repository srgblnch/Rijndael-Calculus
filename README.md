# Rijndael-Calculus

This repository has been made to store the information about the tests and the calculations related with the [rijndael](https://github.com/srgblnch/Rijndael)'s python generalisation code.

All these calculations require much calculations. The first ones have their implementation for parallelise their computation. But later on, the development of the [yamp](https://github.com/srgblnch/yamp) encapsulates the feature to use the library instead of rewrite it. The calculations made before the yamp are not migrated to it because, to the external review of the work, it is important to provide information about how the things were calculated (more than how can be calculated).

## BinaryPolynomials

It contains the script, execution logs and results of the search for binary polynomials for _wordsizes_ different than the 8 of the original Rijndael.

## PolynomialRings

Like the previous, but for the polynomial rings for different _number of rows_ than the 4 and _wordsizes_ than the 8 of the original Rijndael.

## FullDiffusion

Script, using the yamp-0.0.5-5 to calculate, for each of the generalisation settings, how many rounds are needed to provide [Shannon's](https://en.wikipedia.org/wiki/Claude_Shannon) full diffusion (as part of the [Confusion and diffusion](https://en.wikipedia.org/wiki/Confusion_and_diffusion) properties) provided by the non-linear operations.

## XORctr

The best way that the authors of this [Rijndael's generalisation](https://github.com/srgblnch/Rijndael) think to compare the parameter combinations is to know how many _very basic_ operations are made. The most basic operation is the addition in the binary field that are bitwise XORs. The products in the binary field are ANDs, but the products made are in the binary field extension and they only do XORs in the level below.

Another way one can think to compare is by performance, but the [implementation](https://github.com/srgblnch/Rijndael) wasn't thought with bit optimisation in mind. Then the use of memory or the inputs and outputs to the processor will not reveal any difference to help distinguishing between parameter combinations.

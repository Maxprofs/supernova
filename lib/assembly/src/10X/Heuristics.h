// Copyright (c) 2016 10X Genomics, Inc. All rights reserved.

// For heuristics shared across files.

#ifndef TENX_HEURISTICS_H
#define TENX_HEURISTICS_H

#include "CoreTools.h"

// Should have MIN_KMERS1 = MIN_LEN = one constant!

const int MIN_KMERS1 = 100;  // minimum number of kmers to use for nhood seed edge
const int MIN_KMERS2 = 100;  // minimum number of kmers in edge linked to by it
const int MIN_LEN = 100;
const double MIN_NHOOD_FRAC = 0.1;

// These heuristics define a line everywhere in the code base 
// EXCEPT when we are evaluating the assembly

const int MAX_CELL_PATHS = 20;
const int MAX_CELL_DEPTH = 5;

// Heuristics that define a line for evaluation

const int MAX_CELL_PATHS_EVALUATION = 4000;
const int MAX_CELL_DEPTH_EVALUATION = 20;

// const int MAX_CELL_PATHS_NEW = 20000;
// const int MAX_CELL_DEPTH_NEW = 40;

#endif

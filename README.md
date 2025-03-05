# note-level-alignment

Python program to generate note-level-alignment between score and performance using beat-level-alignment

# preparation

Score, Performance, beat-level-alignment are required to make
note-level-alignment.  

In this program, the function of loading scores and performances are handled by [Partitura](https://github.com/CPJKU/partitura), so install it in advance.

Beat-level-alignment is information that indicates the correspondence between the performance time and the beat of the score.

Prepare a text file which each line represents a (score)beat- time(performance), as follows:

```
0,0.8713541626930237
1,1.4583333730697632
2,1.9874999523162842
3,2.444791555404663
4,2.992708206176758
    ・
    ・
    ・
```
# Output
Output is a text file which each line represents a score note (beat,pitch,id)- performance note (beat,pitch,id), as follows:

```
(0.25, 60, n16-1),(1.0708333, 60, n5)
(0.5, 59, n17-1),(1.1989583, 59, n6)
(0.75, 60, n18-1),(1.3291667, 60, n7)
(1.0, 48, n19-1),(1.4583334, 48, n8)
    ・
    ・
    ・
```

# Usage

A program to generate `note_alignment.txt` with `score.musicxml`, `performance.midi` and `beat_alignment.txt` as input is written in `main.py`.

Change the input and output destinations as appropriate. If you change the file format of the input, you must change the function to load.

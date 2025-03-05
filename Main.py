import partitura as pt
import Generate

def main():
    #input
    score_path="score.musicxml"
    performance_path="performance.mid"
    beat_level_alignment_path="beat_alignment.txt"

    #output destination
    note_level_alignment_path="note_alignment.txt"

    #load
    score=pt.load_musicxml(score_path)
    perf=pt.load_performance(performance_path)

    beat_alignment=[]
    with open(beat_level_alignment_path, 'r') as f:
      for line in f:
         temp=line.split(",")
         beat_alignment.append([float(temp[0]),float(temp[1])])
    

    #make note_level_alignment
    note_alignment=Generate.make_note_alignment(score,perf,beat_alignment)
   

    with open(note_level_alignment_path, 'w') as f:
       for note_al in note_alignment:
          x=""
          for val in note_al:
            x=x+","+str(val)
          x=x+"\n"
          f.write(x[1:])
          
       
      




if __name__ == "__main__":
  main()

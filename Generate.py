import partitura as pt
from scipy.interpolate import interp1d
import numpy as np

#音符対応情報生成
#入力: 楽譜score、演奏perf、拍対応情報beat_alignment
#出力: 音符対応情報note_alignment

def make_note_alignment(score,perf,beat_alignment):

    snote_array = score.note_array()
    #snote_onset_array: 楽譜上の音符の集合 [(onset_beat,pitch,id),(onset_beat,pitch,id)...]
    #s_onset_ls:  楽譜のonset時間の集合(重複なし) [onset_time,onset_time,]
    snote_onset_array=[]
    s_onset_ls=[]
    for snote in snote_array:
        if "overlap" not in snote['id'] :
            snote_onset_array.append((snote['onset_beat'],snote['pitch'],snote['id']))
            if snote['onset_beat'] not in s_onset_ls:
                s_onset_ls.append(snote['onset_beat'])
    s_onset_ls=sorted(s_onset_ls)


    pnote_array = perf.note_array()
    #pnote_onset_array: 演奏上の音符の集合 [(onset_time,pitch,id),(onset_time,pitch,id)...]
    #p_onset_ls:  演奏のonset時間の集合 [onset_time,onset_time...]
    p_onset_array=[]
    pnote_onset_array=list([])
    for pn in pnote_array:
        pnote_onset_array.append((pn["onset_sec"],pn["pitch"],pn["id"]))
        p_onset_array.append(pn["onset_sec"])
    pnote_onset_array=sorted(pnote_onset_array)
    p_onset_array=sorted(p_onset_array)


    #拍対応情報から線形予測関数の作成
    sbeat_time=[]
    perf_time=[]
    for an in beat_alignment:
        sbeat_time.append(an[0])
        perf_time.append(an[1])
    stime_to_ptime_map_from_annotation = interp1d(sbeat_time, perf_time,kind='linear',fill_value='extrapolate')
    #x: 楽譜の音符のonset時間(重複なし)
    #y: xの時間に対応する演奏時間
    x = s_onset_ls
    y = stime_to_ptime_map_from_annotation(x)


    #クラスタ対応情報生成部分(拍対応情報の補強部分)
    cluster_alignment=beat_alignment
    score_copy=snote_onset_array.copy()
    perf_copy=pnote_onset_array.copy()


    #探索範囲の絞り込み
    for i in range(len(s_onset_ls)):
        if s_onset_ls[i].is_integer():
            #拍頭についてはすでに拍対応情報があるためパス
            pass

        else:
            if i==0:
                prev_time=y[i]-0.3
                next_time=0.5*y[i]+0.5*y[i+1]
            elif i==len(s_onset_ls)-1:
                prev_time=0.5*y[i-1]+0.5*y[i]
                next_time=y[i]+0.3
            else:
                prev_time= (0.5*y[i-1]+0.5*y[i])
                next_time= (0.5*y[i+1]+0.5*y[i])
            

            group_score=get_notes_in_time(score_copy,x[i]-0.001,x[i]+0.001)
            gpitch0=[]
            for snote in group_score:
                gpitch0.append(snote[1])

            #特異度チェック
            near_group_list=[]
            near_s_onset_list=[j for j in s_onset_ls if abs(x[i]-j)<=0.5 and abs(x[i]-j)>=0.001]
            for t in near_s_onset_list:
                g = get_notes_in_time(score_copy,t-0.001,t+0.001)
                near_group_list.append(g)

        
            flag=True

            for g in near_group_list:
                gpitch_temp=[]
                for snote in g:
                    gpitch_temp.append(snote[1])
                if len(set(gpitch0) & set(gpitch_temp)) /len(gpitch0) >= 0.75:
                    flag=False

        
            if flag==False:
                pass
            else:
                group_perf=get_notes_in_time(perf_copy,prev_time,next_time)

                time_list=[]
                #楽譜の和音を構成する各音符について...
                for sn in group_score:
                    #楽譜上の音符とピッチが等しい音をグループ内から全て取得
                    pn_ls=search_same_pitch(group_perf,sn[1])
                    #同じピッチの音の中で、最もpre_matchの予測時間に近いものを選択
                    if len(pn_ls)!=0:
                        pn_time_ls=[]
                        for pn in pn_ls:
                            pn_time_ls.append(pn[0])
                        id = np.abs(np.asarray(pn_time_ls) - y[i]).argmin()
                        pn=pn_ls[id]
                        time_list.append(pn[0])
            
                #探索範囲内に楽譜の和音構成音それぞれに対応する音符が見つかった時、クラスタ対応情報に追加
                if  len(group_score)==len(time_list) :
                    cluster_alignment.append([x[i],np.median(time_list)])


    #クラスタ対応情報から線形予測関数を作成
    scluster_time=[]
    p_time=[]
    for m in cluster_alignment:
        scluster_time.append(m[0])
        p_time.append(m[1])
    stime_to_ptime_map_from_new_annotation = interp1d(scluster_time, p_time,kind='linear',fill_value='extrapolate')
    xnew = s_onset_ls
    ynew = stime_to_ptime_map_from_new_annotation(xnew)


    #音符対応情報生成部分

    note_alignment=[]

    for i in range(len(s_onset_ls)):

        if i==0:
            #最初から
            prev_time=ynew[i]-0.5
            next_time=0.5*ynew[i+1]
        elif i==len(s_onset_ls)-1:
            prev_time=0.5*ynew[i-1]+0.5*ynew[i]
            #最後まで
            next_time=ynew[i]+0.5

        else:
            prev_time= (0.5*ynew[i-1]+0.5*ynew[i])
            next_time= (0.5*ynew[i+1]+0.5*ynew[i])

        group_score=get_notes_in_time(score_copy,xnew[i]-0.001,xnew[i]+0.001)
        group_perf=get_notes_in_time(perf_copy,prev_time,next_time)


        for sn in group_score:
            pn_ls=search_same_pitch(group_perf,sn[1])

            if len(pn_ls)!=0:
                pn_time_ls=[]
                for pn in pn_ls:
                    pn_time_ls.append(pn[0])
                id = np.abs(np.asarray(pn_time_ls) - ynew[i]).argmin()
                pn=pn_ls[id]

                note_alignment.append((sn,pn))
                score_copy=delete_note(score_copy,sn[0],sn[1],sn[2])
                group_perf=delete_note(group_perf,pn[0],pn[1],pn[2])
                perf_copy=delete_note(perf_copy,pn[0],pn[1],pn[2])



    #条件を緩和して最探索
    
    new_s_onset_ls=[]
    for snote in score_copy:
        if snote[0] not in new_s_onset_ls:
            new_s_onset_ls.append(snote[0])
    xnew =new_s_onset_ls
    ynew = stime_to_ptime_map_from_new_annotation(xnew)

    for i in range(len(new_s_onset_ls)):
        if i==0:
            #最初から
            prev_time=ynew[0]-1
            next_time=ynew[i]+1

        elif i==len(new_s_onset_ls)-1:
            prev_time=ynew[i]-1
            #最後まで
            next_time=ynew[-1]+1

        else:
            prev_time= max(ynew[i]-1.0,0.5*ynew[i]+0.5*ynew[i-1])
            next_time= min(ynew[i]+1.0,0.5*ynew[i]+0.5*ynew[i+1])
        
        
        
        group_score=get_notes_in_time(score_copy,xnew[i]-0.001,xnew[i]+0.001)
        group_perf=get_notes_in_time(perf_copy,prev_time,next_time)


        for sn in group_score:
            pn_ls=search_same_pitch(group_perf,sn[1])

            if len(pn_ls)!=0:
                pn_time_ls=[]
                for pn in pn_ls:
                    pn_time_ls.append(pn[0])
                id = np.abs(np.asarray(pn_time_ls) - ynew[i]).argmin()
                pn=pn_ls[id]

                note_alignment.append((sn,pn))
                score_copy=delete_note(score_copy,sn[0],sn[1],sn[2])
                group_perf=delete_note(group_perf,pn[0],pn[1],pn[2])
                perf_copy=delete_note(perf_copy,pn[0],pn[1],pn[2])   
    note_alignment=resolve_closs(note_alignment)

    return note_alignment




#音符対応情報生成において用いる関数



def get_notes_in_time(onset_note_array,start_time,end_time):
#onset_note_array...音符を取得する元の配列([start,pitch])
#start_time...範囲の始まりの時間
#end_time...範囲の終わりの時間
    group = [i for i in onset_note_array if (i[0] > start_time and i[0]< end_time)]
    return group

#音のなる時間、音の高さを指定してonset_note_arrayから該当する音符を削除する関数
def delete_note(onset_note_array,onset_time,pitch,id):
    onset_note_array.remove((onset_time,pitch,id)) 
    return onset_note_array

#グループ内の指定した音高の音全てを返す関数
def search_same_pitch(group,pitch):
    ls=[]
    for i in group:
        if i[1]==pitch:
            ls.append(i)
    return ls



#ステップ3において順序逆転を解消する関数(pitch_separate~resolve_closs)
def pitch_separate(note_alignment):
    separate_note_alignment_list=[]
    for i in range(1,128):
        separate_note_alignment_list.append([])
    for noteal in note_alignment:
        pitch=noteal[0][1]
        separate_note_alignment_list[pitch].append(noteal)
    separate_note_alignment_list=[i for i in separate_note_alignment_list if len(i)!=0]
        
    return separate_note_alignment_list

def check_preserve_order(note_alignment):
    separate_note_alignment_list=pitch_separate(note_alignment)
    f=True
    for nal in separate_note_alignment_list:
        nal=sorted(nal)
    for i in range(len(nal)-1):
        if (nal[i][0][0]<nal[i+1][0][0]) and (nal[i][1][0]>nal[i+1][1][0]):
            f=False
            break
        else:
            continue
    return f
    
def resolve_closs(note_alignment):
    separate_note_alignment_list=pitch_separate(note_alignment)
    nal_list=[]
    for nal in separate_note_alignment_list:
        nal=sorted(nal)
        while check_preserve_order(nal)==False:
            for i in range(len(nal)-1):
                if (nal[i][0][0]<=nal[i+1][0][0]) and (nal[i][1][0]>nal[i+1][1][0]):
                    tmp1=(nal[i][0],nal[i+1][1])
                    tmp2=(nal[i+1][0],nal[i][1])
                    nal[i]=tmp1
                    nal[i+1]=tmp2
                    nal=sorted(nal)
        nal_list.extend(nal)
    return nal_list

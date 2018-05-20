#include<string>
#include<stdio.h>
#include<iostream>
#include<stdlib.h>
#include<fstream>
#include <algorithm>
#include <memory.h>

using namespace std;
int readGraphemeFile(float grapheme_map[27][27]);
int ** readList(int &list_len, string filename);
void writeResults(int *output_idx, float *output_score, int len_list, string outfile_name);
void printArr(int *word);

int main(int argc, char **argv){

    string oov_list_name="oov_list.txt";
    string outfile_name="oov_hyps.txt";

    //declare thresholds and limits
    int max_len_diff=5;
    float score_threshold=20;
    if(argc>=2){
        max_len_diff=atoi(argv[1]);
        score_threshold=atof(argv[2]);
    }

    int max_comb = 40;

    if(argc>=4){
        oov_list_name=argv[3];
        outfile_name=argv[4];
    }

    //cout << argc << outfile_name << oov_list_name;
    //loop runners
    int i,j,k,l,m,n;

    //read Grapheme Map
    float grapheme_map[27][27];
	readGraphemeFile(grapheme_map);

    //read IV List
	int iv_list_len;
	int ** iv_list;
	iv_list=readList(iv_list_len, "iv_list.txt");

    if(iv_list_len>150000)
        max_comb=100;

    //read OOV List
    int oov_list_len;
    int ** oov_list;
    oov_list=readList(oov_list_len, oov_list_name);

    //Score counts for each hypothesis word
    float *scores, *new_scores, *zero_scores;
    scores=(float*)malloc(max_comb*sizeof(float));
    new_scores=(float*)malloc(max_comb*sizeof(float));
    zero_scores=(float*)malloc(max_comb*sizeof(float));
    for (i=0;i<max_comb;i++)
        zero_scores[i]=0.0;
    memcpy(scores, zero_scores, max_comb*sizeof(int));
    memcpy(new_scores, zero_scores, max_comb*sizeof(int));

    //min_score for space based thresholding
    float min_score[30],thousand_score[30];
    for (i=0;i<30;i++){
        thousand_score[i]=1000;
    }

    //space counts for each hypothesis word
	int *spaces, *new_spaces;
	spaces=(int*)malloc(max_comb*sizeof(int));
	new_spaces=(int*)malloc(max_comb*sizeof(int));
    memset(spaces, 0, max_comb*sizeof(int));
    memset(new_spaces, 0, max_comb*sizeof(int));

    //min_word = best hypothesis
    int min_dist_idx;
    float min_word_score,min_dist_score;

    //output array
    float *output_score;
    int * output_idx;
    output_score =(float*)malloc(oov_list_len*sizeof(float));
    output_idx=(int*)malloc(oov_list_len*sizeof(int));

    //variables needed for scoring logic
    int oov_len, iv_len, max_len, min_len, len_diff,char_idx,valid_entries,new_valid_entries;
    bool iv_first, search;
    int space_calc, pad_word_pos;
    float score_calc;
    bool threshold_reached=false;
    //padding word and original length word
    int pad_word[32];
    int org_word[32];
	//cout << "Declared Variables and read files" << endl;
    for(int oov_idx=0; oov_idx<oov_list_len; oov_idx++){
        //cout << oov_idx << ": ";
        //printArr(oov_list[oov_idx]);
        min_dist_idx=-1;
        min_dist_score=1000;
        for(int iv_idx=0; iv_idx<iv_list_len; iv_idx++){
            //printArr(oov_list[oov_idx]);
            //printArr(iv_list[iv_idx]);
            //if(iv_idx%20000==0)
              // cout << iv_idx << " " << min_dist_score << " " << min_dist_idx << endl;
            oov_len = oov_list[oov_idx][0];
            iv_len = iv_list[iv_idx][0];
            if(abs(oov_len-iv_len)<=max_len_diff){
                if(iv_len>oov_len){
                    max_len=iv_len;
                    min_len=oov_len;
                    iv_first=true;
                    memcpy(pad_word, oov_list[oov_idx], 32*sizeof(int) );
                    memcpy(org_word, iv_list[iv_idx], 32*sizeof(int) );
                }
                else{
                    max_len=oov_len;
                    min_len=iv_len;
                    iv_first=false;
                    memcpy(org_word, oov_list[oov_idx], 32*sizeof(int));
                    memcpy(pad_word, iv_list[iv_idx], 32*sizeof(int));
                }

                len_diff=max_len-min_len;
            
                search=true;
                memset(spaces, 0, max_comb*sizeof(int));
                memcpy(scores, zero_scores, max_comb*sizeof(int));
                spaces[0]=len_diff;
                scores[0]=0;
                valid_entries=1;

                char_idx=1;
                while(search){
                    memcpy(min_score,thousand_score,30*sizeof(float));
                    memset(new_spaces, 0, max_comb*sizeof(int));
                    memcpy(new_scores, zero_scores, max_comb*sizeof(int));
                    new_valid_entries=0;

                    /*cout << "==== " << char_idx-1 << endl; ;
                    for (j=0;j<valid_entries;j++)
                        cout << spaces[j] << "," << scores[j] << "\t";
                    cout << endl;*/

                    for(i=0;i<valid_entries;i++){
                        pad_word_pos = char_idx - (len_diff - spaces[i]);
                        //substitution
                        if(pad_word_pos<min_len+1){
                            (iv_first) ? (score_calc=grapheme_map[org_word[char_idx]][pad_word[pad_word_pos]]) 
                            : (score_calc=grapheme_map[pad_word[pad_word_pos]][org_word[char_idx]]);
                            //cout << char(pad_word[pad_word_pos]+97) << " " << char(org_word[char_idx] + 97) << " " << score_calc << " " << scores[i] << endl;
                            score_calc += scores[i];
                            new_spaces[new_valid_entries]=spaces[i];
                            new_scores[new_valid_entries]=score_calc;
                            new_valid_entries++;
                            //cout << "iv_idx: " << iv_idx << " ve: " << valid_entries << " pwp: " << pad_word_pos << " Len Diff" << len_diff << " spaces_i" << spaces[i] << endl;
                            if(score_calc<min_score[spaces[i]])
                                min_score[spaces[i]]=score_calc;
                        }

                        //padding
                        if(spaces[i]>0){
                            (iv_first) ? (score_calc=grapheme_map[org_word[char_idx]][26]) 
                            : (score_calc=grapheme_map[26][org_word[char_idx]]);
                            score_calc += scores[i];
                            space_calc = spaces[i]-1;
                            new_spaces[new_valid_entries]=space_calc;
                            new_scores[new_valid_entries]=score_calc;
                            new_valid_entries++;
                            if(score_calc<min_score[space_calc])
                                min_score[space_calc]=score_calc;
                        }
                    }

                    /*for (j=0;j<new_valid_entries;j++)
                        cout << new_spaces[j] << "," << new_scores[j] << "\t";
                    cout << endl;*/

                    memset(spaces, 0, max_comb*sizeof(int));
                    memcpy(scores, zero_scores, max_comb*sizeof(float));
                    valid_entries=0;

                    for(i=0;i<new_valid_entries;i++){
                        //cout << i << ": " << min_score[new_spaces[i]] << " " << new_scores[i] <<  " " << new_spaces[i] << " " << score_threshold << " " << min_dist_score << endl;
                        if(new_scores[i]<=min_score[new_spaces[i]] && new_scores[i]<=score_threshold && new_scores[i]<=min_dist_score){
                            spaces[valid_entries]=new_spaces[i];
                            scores[valid_entries]=new_scores[i];
                            valid_entries++;
                        }
                    }
                    //cout << new_valid_entries << " " << valid_entries << endl;
                    //cout << "iv_idx: " << iv_idx << " char idx: " << char_idx << " ve: " << valid_entries <<endl;
                    char_idx++;
                   
                    if(char_idx==max_len+1){
                        //cout << int(char_idx==max_len) << endl;
                        search=false;
                    }

                    if(valid_entries==0 and char_idx<max_len+1){
                        threshold_reached=true;
                    }
                }
                if(!threshold_reached){
                    min_word_score=1000;
                    for(i=0;i<new_valid_entries;i++){
                        if (new_scores[i]<min_word_score)
                            min_word_score=new_scores[i];
                    }
                    
                    if(min_word_score<min_dist_score){
                        min_dist_score=min_word_score;
                        min_dist_idx=iv_idx;
                    }
                }
                threshold_reached=false;

                

            }
        }
        output_score[oov_idx] = min_dist_score;
        output_idx[oov_idx]=min_dist_idx;
        //printArr(oov_list[oov_idx]);
        //if (min_dist_idx>=0)
        //    printArr(iv_list[min_dist_idx]);
        
        //cout << min_dist_score <<endl;
        //cout << output_score[oov_idx] << " " << output_idx[oov_idx] << " " << min_word_score << endl;
        //cout << "=====" << endl;
    }
    //cout << "=====";
    //for (i=0;i<oov_list_len;i++)
    //    cout << output_score[i] << " " << output_idx[i] << endl;
    writeResults(output_idx, output_score, oov_list_len, outfile_name);
	return 0;
}

//reads grapheme map
int readGraphemeFile(float grapheme_map[27][27]){
	int i,j, oov_ch_idx, iv_ch_idx;
	float score;
	char oov_ch, iv_ch;
    ifstream infile("gmap.txt");

	while(infile >> oov_ch >> iv_ch >> score){
		//i++;
		oov_ch_idx = int(oov_ch)-97;
		iv_ch_idx = int(iv_ch)-97;
		//cout << oov_ch_idx << " " << iv_ch_idx << " " << score << endl;
		grapheme_map[oov_ch_idx][iv_ch_idx]=float(score);
		//cout << grapheme_map[oov_ch_idx][iv_ch_idx] << endl;
	}
	return 0;
}

//write results to file
void writeResults(int *output_idx, float *output_score, int len_list, string outfile_name){
    ofstream outfile(outfile_name);
    cout << len_list << endl;
    if(outfile.is_open()){
        for(int i; i<len_list;i++){
            cout << i;
            cout << output_idx[i] << " " << output_score[i] << endl;
            outfile << output_idx[i] << " " << output_score[i] << " \n";
        }
    }
}

//read iv or oov list as arrays contain word length and chars converted to int
int ** readList(int &list_len, string filename){
	ifstream infile(filename);
	int ** list;
	int string_len;
	string word;
	infile >> string_len >> list_len;

	list = static_cast<int**>(malloc(list_len * sizeof(int*)));

	for (int i =0; i<list_len; i++){
		list[i] = static_cast<int*>(malloc(string_len * sizeof(int)));
		infile >> word;
	//	cout << word << " " << word.length() << endl;
		list[i][0]=word.length();
		for (int j=1; j<word.length();j++){
			list[i][j]=int(word[j-1])-97;
		}
	}
	return list;
}

//print word in array
void printArr(int *word){
    int length = word[0];
    cout << length << ": ";
    for (int i=1;i<=length;i++){
        cout << char(word[i]+97) ;
    }
    cout << endl;
}
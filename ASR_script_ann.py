import subprocess

pracann="/home/okz21/Speech_Coursework/pracann/exp/"
pracgmm="/home/okz21/Speech_Coursework/pracgmm/exp/"
pracgmm_align="/home/okz21/Speech_Coursework/pracgmm/exp/PMFC_D_A_Z_FlatStart/"
pracgmm_tri_align="/home/okz21/Speech_Coursework/pracann/exp/triphone/align-tri-hmm164/"

csvHeader = ",InLayers,OutLayers,TrainAcc,ValAcc,WCorr,WAcc,WH,WD,WS,WI,WN,SCorr,SH,SS,SN\n"

def writeFile(outputString, fileName):
	f = open(fileName, 'w')
	f.write(outputString)
	f.close()

def getWordDetails(output_dir):
	grep = subprocess.Popen(["grep", "WORD:", output_dir + "/test/LOG"], stdout=subprocess.PIPE)
	output, error = grep.communicate()
	Corr = output.split()[1].split("=")[1].replace(",", "")
	Acc = output.split()[2].split("=")[1].replace(",", "")
	H = output.split()[3].split("=")[1].replace(",", "")
	D = output.split()[4].split("=")[1].replace(",", "")
	S = output.split()[5].split("=")[1].replace(",", "")
	I = output.split()[6].split("=")[1].replace(",", "")
	N = output.split()[7].split("=")[1].replace(",", "").replace("]", "")
	result = "{},{},{},{},{},{},{}".format(Corr,Acc,H,D,S,I,N)
	print output
	return result


def getSentDetails(output_dir):
	grep = subprocess.Popen(["grep", "SENT:", output_dir + "/test/LOG"], stdout=subprocess.PIPE)
	output, error = grep.communicate()
	Corr = output.split()[1].split("=")[1].replace(",", "")
	H = output.split()[2].split("=")[1].replace(",", "")
	S = output.split()[3].split("=")[1].replace(",", "")
	N = output.split()[4].split("=")[1].replace(",", "").replace("]", "")
	result = "{},{},{},{}".format(Corr,H,S,N)
	print output
	return result

def generateContextWidth(L,R):
    contextList = []
    for i in range (-L,R+1):
            context = str(i)
            if(i>0):
                context = "+" + context
            contextList.append(context)
    return ",".join(contextList)

def getTrainDetails(train_dir):
	grep = subprocess.Popen(["grep", "Train Accuracy", train_dir + "/hmm0/LOG"], stdout=subprocess.PIPE)
	output, error = grep.communicate()
	train_acc = output.split("\n")[-2].split("=")[1].split(" ")[1].replace("%","")
	grep = subprocess.Popen(["grep", "Validation Accuracy", train_dir + "/hmm0/LOG"], stdout=subprocess.PIPE)
	print output
	output, error = grep.communicate()
	validation_acc = output.split("\n")[-2].split("=")[1].split(" ")[1].replace("%","")
	result = "{},{}".format(train_acc,validation_acc)
	print output
	return result

#For Triphones
def getLayerDetails(train_dir):
	grep = subprocess.Popen(["grep", "layerin", train_dir + "/hmm0/LOG"], stdout=subprocess.PIPE)
	output, error = grep.communicate()
	print output
	in_layer = output.split("\n")[0].split(" ")[4].replace("(","")

	grep = subprocess.Popen(["grep", "layerout", train_dir + "/hmm0/LOG"], stdout=subprocess.PIPE)
	output, error = grep.communicate()
	out_layer = output.split("\n")[0].split(" ")[7]
	result = "{},{}".format(in_layer,out_layer)
	print output
	return result


#======================================GMM Mono Alignment============================
"""
#mono alignment for ANNs
subprocess.call(["../tools/steps/step-align", "~/Speech_Coursework/pracgmm/exp/PMFC_D_A_Z_FlatStart/mono", "hmm164", "ann_align-mono-hmm164"])
"""
#===================Decode 1L===========================
"""
searchParams = ["Insword"]
output_csv = ",".join(searchParams) + csvHeader
train_dir =  pracann + "MH0/dnntrain_1L"

ipen_grid = [0, -1, -2, -3, -4, -5, -6, -7, -8, -12, -16, -20, -24, -28, -32]
for ipen in ipen_grid:
	output_dir = "MH0/decode_DNN_1L_INS_" + str(ipen)
	subprocess.call(["../tools/steps/step-decode", "-BEAMWIDTH", "250", "-INSWORD", str(ipen), train_dir, "hmm0", output_dir])

	params = [str(ipen)]
	print ",".join(params)
	output_csv = output_csv + ",".join(params) + "," + getTrainDetails(train_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv,"ann_insword_results.csv")
"""
#============================Create Files 6.3===========================
"""
parm_grid = {'MFCC_E_D_A_Z':39, 'MFCC_E_D_Z':26, 'MFCC_E_Z':13, 'FBANK_Z':24, 'FBANK_D_Z':48, 'FBANK_D_A_Z':72}
context_grid = range(0,11)
for parm in parm_grid:
	for context in context_grid:
		with open('DNN-1L.ReLU.MFCC_E_D_A_Z.ini', 'r') as file :
  			filedata = file.read()
		print parm+" "+str(parm_grid[parm])+" "+str(context)
		out_filename = "63_inifile/DNN_1L_" + parm + "_" + str(context) + ".ini"
		filedata = filedata.replace('MFCC_E_D_A_Z', parm)
		filedata = filedata.replace('39', str(parm_grid[parm]))
		filedata = filedata.replace('-4,-3,-2,-1,0,+1,+2,+3,+4', generateContextWidth(context,context))
		with open(out_filename, 'w') as file:
			file.write(filedata)
"""
#====================6.3 Training=================================

"""
searchParams=["Parameterization","ContextWidth"]
output_csv = ",".join(searchParams) + csvHeader
parm_grid = {'FBANK_Z':24, 'FBANK_D_Z':48, 'FBANK_D_A_Z':72, 'MFCC_E_D_A_Z':39, 'MFCC_E_D_Z':26, 'MFCC_E_Z':13}
context_grid = range(0,11)
filter_grid = {'FBANK_Z':"fbk25d/env/environment_Z", 'FBANK_D_Z':"fbk25d/env/environment_D_Z", 'FBANK_D_A_Z':"fbk25d/env/environment_D_A_Z", 'MFCC_E_D_A_Z':"mfc13d/env/environment_E_D_A_Z", 'MFCC_E_D_Z':"mfc13d/env/environment_E_D_Z", 'MFCC_E_Z':"mfc13d/env/environment_E_Z"}
for parm in parm_grid:
	for context in context_grid:
		current_training = parm+" "+str(parm_grid[parm])+" "+str(context)
		f = open('63_training_progress.txt','a')
		train_log =current_training + ": Training Started\n"
		f.write(train_log)
		f.close()
		print current_training
		out_filename = "63_inifile/DNN_1L_" + parm + "_" + str(context) + ".ini"

		print "+==============================================+"
		print "../tools/steps/step-dnntrain" +" "+ "-vvv" +" "+ "-GPUID" +" "+ "0" +" "+ "-MODELINI" +" "+ out_filename +" "+ "../convert/" + filter_grid[parm] +" "+pracgmm_align + "align-mono-hmm84/align/timit_train.mlf" +" "+pracgmm_align + "mono/hmm164/MMF" +" "+pracgmm_align + "mono/hmms.mlist" +" "+"63_Train/dnntrain_" + parm + "_" + str(context)
		print "+==============================================+\n\n"

		subprocess.call(["../tools/steps/step-dnntrain", "-vvv", "-GPUID", "0", "-MODELINI", out_filename , "../convert/" + filter_grid[parm] ,pracgmm_align + "align-mono-hmm164/align/timit_train.mlf" ,pracgmm_align + "mono/hmm164/MMF" ,pracgmm_align + "mono/hmms.mlist" ,"63_Train/dnntrain_" + parm + "_" + str(context)])

		f = open('63_training_progress.txt','a')
		train_log = current_training + ": Training Ended\n"
		f.write(train_log)
		f.close()
"""
#============================Grid Search 6.3============================
"""
parm_grid = {'FBANK_Z':24, 'FBANK_D_Z':48, 'FBANK_D_A_Z':72, 'MFCC_E_D_A_Z':39, 'MFCC_E_D_Z':26, 'MFCC_E_Z':13}
context_grid = range(0,11)
searchParams = ["Parameterization", "Context_width"]
output_results = ""
output_csv = ",".join(searchParams) + csvHeader
for parm in parm_grid:
	for context in context_grid:
		train_dir = pracann + "63_Train/dnntrain_" + parm + "_" + str(context)
		output_dir = pracann + "63_Decode/Decode_" + parm + "_" + str(context) + "_ST"
		subprocess.call(["../tools/steps/step-decode", "-SUBTRAIN", "-BEAMWIDTH", "250", "-INSWORD", "-4", train_dir, "hmm0", output_dir])
		print "Param=" + parm
		print "Context_Width=" + str(context)
		params = [parm, str(context)]
		print ",".join(params)
		output_csv = output_csv  + ",".join(params) + "," + getLayerDetails(train_dir) + "," + getTrainDetails(train_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"
writeFile(output_csv,"63_results_ST.csv")
"""
#====================6.4 Create Files=================================
"""
for hLayer in range(1,11):
	with open('DNN_1L_FBANK_D_A_Z_8.ini', 'r') as file :
			filedata = file.read()
	print hLayer
	out_filename = "64_inifile/DNN_" + str(hLayer) + "L_FBANK_D_A_Z_8"  + ".ini"

	if(hLayer>1):
		layerout_rep = 'FeatureElement1.Source = layer{}'.format(hLayer+1)
		filedata = filedata.replace('FeatureElement1.Source = layerin', layerout_rep)

	layerPre="[Layer:layer"
	layerMid ="]\nKind = FC\nFeatureMixture.Num = 1\nFeatureElement1.Dim = @HiddenLayerDim\nFeatureElement1.ContextShiftSet = {0}\nFeatureElement1.Source = layer"
	layerPost = "\nHasBias = True\nOutputDim = @HiddenLayerDim\nActivationFunction = @HiddenActFunc\n"
	layers=""
	for i in range(1,hLayer):
		if (i==1):
			layers = layers + layerPre + str(i+2) + layerMid + "in" + layerPost
		else:
			layers = layers + layerPre + str(i+2) + layerMid + str(i+1) + layerPost
	filedata = filedata.replace('[Layer:layerout]', layers + '[Layer:layerout]')

	layerNames = 'Layer2.Name = layerin\n'
	for i in range(2,hLayer+1):
		layerNames = layerNames + 'Layer{}.Name = layer{}\n'.format(i+1,i+1)
	layerNames = layerNames + 'Layer{}.Name = layerout\n'.format(hLayer+2)
	filedata = filedata.replace('Layer2.Name = layerin\nLayer3.Name = layerout\n', layerNames)

	with open(out_filename, 'w') as file:
		file.write(filedata)
"""
#====================6.4 Training=================================
"""
for layer_num in range(1,11):
	out_filename = "64_inifile/DNN_" + str(layer_num) + "L_FBANK_D_A_Z_8"  + ".ini"
	subprocess.call(["../tools/steps/step-dnntrain", "-vvv", "-GPUID" ,"0" , "-MODELINI", out_filename , "../convert/fbk25d/env/environment_D_A_Z" ,pracgmm_align + "align-mono-hmm84/align/timit_train.mlf" ,pracgmm_align + "mono/hmm84/MMF" ,pracgmm_align + "mono/hmms.mlist" ,"64_Train/dnntrain_" + str(layer_num)])
	print "../tools/steps/step-dnntrain" +" "+ "-vvv" +" "+ "-GPUID" +" "+ "0" +" "+ "-MODELINI" +" "+ out_filename +" "+ "../convert/fbk25d/env/environment_D_A_Z" +" "+ pracgmm_align + "align-mono-hmm84/align/timit_train.mlf" +" "+ pracgmm_align + "mono/hmm84/MMF" +" "+ pracgmm_align + "mono/hmms.mlist" +" "+"64_Train/dnntrain_" + str(layer_num)
"""
#====================6.4 Decode====================================
"""
context_grid = range(0,11)
searchParams = ["Layers"]
output_csv = ",".join(searchParams) + csvHeader
for layer_num in range (1,11):
	train_dir = pracann + "64_Train/dnntrain_" + str(layer_num)
	output_dir = pracann + "64_Decode/Decode_" + str(layer_num) + "_ST"
	subprocess.call(["../tools/steps/step-decode", "-SUBTRAIN", "-BEAMWIDTH", "250", "-INSWORD", "-4", train_dir, "hmm0", output_dir])
	print layer_num
	params = [str(layer_num)]
	print ",".join(params)
	output_csv = output_csv  + ",".join(params) + "," + getLayerDetails(train_dir) + "," + getTrainDetails(train_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"
writeFile(output_csv,"64_results_ST.csv")
"""
#========================6.5
"""
output_csv = "InLayers,OutLayers,TrainAcc,ValAcc,WCorr,WAcc,WH,WD,WS,WI,WN,SCorr,SH,SS,SN\n"
train_dir = pracann + "triphone/dnntrain_5_TRI"
output_dir = pracann + "triphone/dnntrain_5_TRI/decode"
subprocess.call(["../tools/steps/step-align", pracgmm + "triphones/xwtri_50_400", "hmm164", "triphone/align-tri-hmm164"])

subprocess.call(["../tools/steps/step-dnntrain", "-vvv", "-GPUID", "0", "-MODELINI", "64_inifile/DNN_5L_TRI_FBANK_D_A_Z_8.ini", "../convert/fbk25d/env/environment_D_A_Z", pracgmm_tri_align + "align/timit_train.mlf", pracgmm_tri_align + "alignHMMs/MMF", pracgmm_tri_align + "hmms.mlist", "triphone/dnntrain_5_TRI"])

subprocess.call(["../tools/steps/step-decode", "-CORETEST", "-BEAMWIDTH", "250", "-INSWORD", "-4", train_dir, "hmm0", output_dir])

output_csv = output_csv + getLayerDetails(train_dir) + "," + getTrainDetails(train_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"
writeFile(output_csv,"65_triphone_results_5L_TRI.csv")
"""
#=====================================6.6 monophones

#train

total_layer_grid = [5,10,20,40]
for layer_num in total_layer_grid:
	out_filename = "66_inifile/RNN-1L.ReLU.FBANK_D_A_Z_" + str(layer_num) + ".ini"
	print "../tools/steps/step-dnntrain"+ " " + "-vvv"+ " " + "-GPUID" + " " +"0" + " " + "-MODELINI"+ " " + out_filename + " " + "../convert/fbk25d/env/environment_D_A_Z" + " " +pracgmm_align + "align-mono-hmm84/align/timit_train.mlf" + " " +pracgmm_align + "mono/hmm84/MMF" + " " +pracgmm_align + "mono/hmms.mlist" + " " +"66_train/rnntrain_" + str(layer_num)
	subprocess.call(["../tools/steps/step-dnntrain", "-vvv", "-GPUID" ,"0" , "-MODELINI", out_filename , "../convert/fbk25d/env/environment_D_A_Z" ,pracgmm_align + "align-mono-hmm84/align/timit_train.mlf" ,pracgmm_align + "mono/hmm84/MMF" ,pracgmm_align + "mono/hmms.mlist" ,"66_train/rnntrain_" + str(layer_num)])


#decode
searchParams = ["RNN_Unfolding"]
output_results = ""
output_csv = ",".join(searchParams) + csvHeader

for layer_num in total_layer_grid:
	train_dir = pracann + "66_train/rnntrain_" + str(layer_num)
	output_dir = pracann + "66_decode/rnntrain_" + str(layer_num) + "_ST"
	subprocess.call(["../tools/steps/step-decode", "-SUBTRAIN", "-BEAMWIDTH", "250", "-INSWORD", "-4", train_dir, "hmm0", output_dir])
	print layer_num
	params = [str(layer_num)]
	print ",".join(params)
	output_csv = output_csv  + ",".join(params) + "," + getLayerDetails(train_dir) + "," + getTrainDetails(train_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv, "66_unfolding_results_ST.csv")

#=====================================6.6 triphones

#train
"""
total_layer_grid = [5,10,20]
for layer_num in total_layer_grid:
	out_filename = "66_inifile/RNN-1L.ReLU.FBANK_D_A_Z_" + str(layer_num) + ".ini"
	print "../tools/steps/step-dnntrain"+ " " + "-vvv"+ " " + "-GPUID" + " " +"0" + " " + "-MODELINI"+ " " + out_filename + " " + "../convert/fbk25d/env/environment_D_A_Z" + " " +pracgmm_tri_align + "align/timit_train.mlf"+ " " + pracgmm_tri_align + "alignHMMs/MMF"+ " " + pracgmm_tri_align + "hmms.mlist"+ " " +"triphone/66_train/rnntrain_" + str(layer_num)
	subprocess.call(["../tools/steps/step-dnntrain", "-vvv", "-GPUID" ,"0" , "-MODELINI", out_filename , "../convert/fbk25d/env/environment_D_A_Z" ,pracgmm_tri_align + "align/timit_train.mlf", pracgmm_tri_align + "alignHMMs/MMF", pracgmm_tri_align + "hmms.mlist","triphone/66_train/rnntrain_" + str(layer_num)])


#decode
total_layer_grid = [5,10,20]
searchParams = ["RNN_Unfolding"]
output_results = ""
output_csv = ",".join(searchParams) + csvHeader

for layer_num in total_layer_grid:
	train_dir = pracann + "triphone/66_train/rnntrain_" + str(layer_num)
	output_dir = pracann + "triphone/66_decode/rnntrain_" + str(layer_num)
	subprocess.call(["../tools/steps/step-decode", "-CORETEST", "-BEAMWIDTH", "250", "-INSWORD", "-4", train_dir, "hmm0", output_dir])
	print layer_num
	params = [str(layer_num)]
	print ",".join(params)
	output_csv = output_csv  + ",".join(params) + "," + getLayerDetails(train_dir) + "," + getTrainDetails(train_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv, "66_triphone_results.csv")
"""

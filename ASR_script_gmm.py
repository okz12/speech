import subprocess

pracann="/home/okz21/Speech_Coursework/pracann/exp/"
pracgmm="/home/okz21/Speech_Coursework/pracgmm/exp/"

csvHeader = ",WCorr,WAcc,WH,WD,WS,WI,WN,SCorr,SH,SS,SN\n"
triphoneHeaderAdd = ",InitStates,FinalStates"

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

#For Triphones
def getStateTyingDetails(train_dir):
	grep = subprocess.Popen(["grep", "total", train_dir + "/hmm10/LOG"], stdout=subprocess.PIPE)
	output, error = grep.communicate()
	initState, finalState = output.split("\n")[-2].split(" ")[7].split("->")
	result = "{},{}".format(initState,finalState)
	return result
#===================Grid Trianing==================
"""
FBANK_P = ["Z", "D_Z", "D_A_Z"]
for param in FBANK_P:
        print "Training FBANK Init " + param
        subprocess.call(["../tools/steps/step-mono", "-NUMMIXES", "16", "../convert/fbk25d/env/environment_" + param, "PFBK_" + param + "_Init" + "/mono"])
        print "Training FBANK FlatStart " + param
        subprocess.call(["../tools/steps/step-mono", "-FLATSTART", "-NUMMIXES", "16", "../convert/fbk25d/env/environment_" + param, "PFBK_" + param + "_FlatStart" + "/mono"])
        print "Training MFCC Init " + param
        subprocess.call(["../tools/steps/step-mono", "-NUMMIXES", "16", "../convert/mfc13d/env/environment_E_" + param, "PMFC_" + param + "_Init" + "/mono"])
        print "Training MFCC FlatStart " + param
        subprocess.call(["../tools/steps/step-mono", "-FLATSTART", "-NUMMIXES", "16", "../convert/mfc13d/env/environment_E_" + param, "PMFC_" + param + "_FlatStart" + "/mono"])
"""

#===================Insertion Penalty===============
"""
searchParams = ["Insword"]
output_csv = ",".join(searchParams) + csvHeader

ipen_grid = [4, 0, -4, -8, -12, -16, -20, -24, -28, -32]
for ipen in ipen_grid:
	output_dir = "PFBK_Z_Init/decode-mono-hmm84_INS_" + str(ipen)
	subprocess.call(["../tools/steps/step-decode", "-BEAMWIDTH", "250", "-INSWORD", str(ipen), pracgmm + "PFBK_Z_Init/mono", "hmm84", "PFBK_Z_Init/decode-mono-hmm84_INS_" + str(ipen)])

	params = [str(ipen)]
	print ",".join(params)
	output_csv = output_csv + ",".join(params) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv,"insword_results.csv")

"""
#================Beamwidth======================
"""
searchParams = ["Beamwidth"]
output_csv = ",".join(searchParams) + csvHeader

bwgrid = [50, 100, 150, 200, 250, 300, 350, 400]
for bw in bwgrid:
	output_dir = "PFBK_Z_Init_BW/decode-mono-hmm84_BW_" + str(bw)
	subprocess.call(["../tools/steps/step-decode", "-BEAMWIDTH", str(bw), pracgmm + "PFBK_Z_Init/mono", "hmm84", "PFBK_Z_Init/decode-mono-hmm84_BW_" + str(bw)])
	params = [str(bw)]
	print ",".join(params)
	output_csv = output_csv + ",".join(params) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv,"beamwidth_results.csv")
"""
#=====================Mass Grid Search===========
"""
searchParams = ["Parameterisation", "Parameters","Initialisation","Gaussians"]
output_csv = ",".join(searchParams) + csvHeader

model_type = ["FBK", "MFC"]
param_type = ["Z", "D_Z", "D_A_Z"]
init_type = ["Init", "FlatStart"]
gaussian_num = ["hmm24", "hmm44", "hmm64", "hmm84","hmm104","hmm124","hmm144","hmm164"]

for model in model_type:
	for param in param_type:
		for init in init_type:
			for gaussian in gaussian_num:
				folder_name = "P" + model + "_" + param + "_" + init
				training_dir = pracgmm + folder_name + "/mono"
				output_dir = "decode_run_1/" + folder_name + "/decode-mono-" + gaussian
				subprocess.call(["../tools/steps/step-decode", "-BEAMWIDTH", "250", "-INSWORD", "-16", training_dir, gaussian, output_dir])

				params = [model,param,init,gaussian]
				print ",".join(params)
				output_csv = output_csv + ",".join(params) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv,"massgrid_results.csv")
"""
#===========================Triphone Training===============
"""
tb_grid = ["50", "100", "200", "400", "800"]
ro_grid = ["50", "100", "200", "400", "800"]
for tb_val in tb_grid:
	for ro_val in ro_grid:
		training_dir = "triphones/xwtri_" + str(ro_val) + "_" + str(tb_val)
		print training_dir
		subprocess.call(["../tools/steps/step-xwtri", "-NUMMIXES", "16", "-ROVAL", str(ro_val), "-TBVAL", str(tb_val), pracgmm + "PMFC_D_A_Z_FlatStart/mono", "hmm14", training_dir])
"""
#===========================Triphone Decoding===============

#clusters inversely proportional to gmms
"""
searchParams = ["TB_VAL","RO_VAL"]
output_csv = ",".join(searchParams) + triphoneHeaderAdd + csvHeader

tb_grid = ["50", "100", "200", "400", "800"]
ro_grid = ["50", "100", "200", "400", "800"]
for tb_val in tb_grid:
	for ro_val in ro_grid:
		training_dir = pracgmm + "triphones/xwtri_" + ro_val + "_" + tb_val
		output_dir = "triphones/decode/" + str(ro_val) + "_" + str(tb_val) + "_hmm164"
		subprocess.call(["../tools/steps/step-decode", "-CORETEST", "-BEAMWIDTH", "250", "-INSWORD", "-16", training_dir, "hmm164", output_dir])
		params = [tb_val,ro_val]
		print ",".join(params)
		output_csv = output_csv + ",".join(params) + "," + getStateTyingDetails(training_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv,"triphone_results.csv")
"""
#=======================================Triphones vs Mixtures===============
#clusters inversely proportional to gmms

searchParams = ["RO_TB","NUMMIX"]
output_csv = ",".join(searchParams) + triphoneHeaderAdd + csvHeader
ro_tb_grid = ["800_800", "400_400", "200_200", "50_200", "100_100", "50_100", "100_50"];
gaussian_num = ["hmm24", "hmm44", "hmm64", "hmm84", "hmm104", "hmm124", "hmm144","hmm164"]
for ro_tb_val in ro_tb_grid:
	for gaussian in gaussian_num:
		training_dir = pracgmm + "triphones/xwtri_" + ro_tb_val
		output_dir = "triphones/decode/" + ro_tb_val + "_" + gaussian
		subprocess.call(["../tools/steps/step-decode", "-CORETEST", "-BEAMWIDTH", "250", "-INSWORD", "-16", training_dir, gaussian, output_dir])
		params = [ro_tb_val, gaussian]
		print ",".join(params)
		output_csv = output_csv + ",".join(params) + "," + getStateTyingDetails(training_dir) + "," + getWordDetails(output_dir) + "," + getSentDetails(output_dir) + "\n"

writeFile(output_csv,"triphone_gmm_results.csv")

#======================================GMM Mono Alignment============================
"""
#mono alignment for ANNs
subprocess.call(["../tools/steps/step-align", "~/Speech_Coursework/pracgmm/exp/PMFC_D_A_Z_FlatStart/mono", "hmm164", "PMFC_D_A_Z_FlatStart/align-mono-hmm164"])
"""


How to run the DroidSim


1. create a root directory and put the file  CBCFG.jar in it.

this is use our tool CBCFG to generate the component-based CFG graph

2. run python getSignature.py file which can parse the dex file and get the CFG

you can modify the path and change into your personal apk path and you can get the CFG signature.

If you want to run the CFG you should modify the file getSignature.py




#****************************************
# Using method :
# java -jar CBCFG.jar
#
# before we run this file we should run the CFGScanDroid
# sudo apt-get install maven
# ./build.sh 
#  This will create a file:
# target/CFGScanDroid.jar
#***********************************************


3.When you finish get the CFG signature you can use the file parseCFGResult.py to get the CFG graph

#**********************************************************************
#  when we use CFGScanDroid scan the dex file we can get the signature 
#  of each apk (CFG)
#  the signature format:
#  La.a()Z;8;0:1,2,3,4,5;6:7
#  interceptSMS;4;0:1,2;1:3;2:3,0
#  the signature name is interceptSMS, there are 4 vertices
#  0:1,2
#  1:3
#  2:3,0
#  in this way we can get the edge relation
#  
#  the edges:
#  0->1
#  0->2
#  1->3
#  2->3
#  2->0
#**********************************************************************


4. if you want to delete the ad libs you can run this file

python deleteAds.py to delete the ad libs

Generally, you should delet the libs first and then you just parse the CFG graph you should run this file first and then run the parseCFGResult.py


5. run python VF2.py you can get the similar Values of each app pairs.

should install the networkx



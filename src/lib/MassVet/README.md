MassVet is consist of two parts

1,ViewDroid

2.3d-CFG


How to get the CFG graph


1. create a root directory and put the file  CFGScanDroid.jar in it.

2. run python getSignature.py file which can parse the dex file and get the CFG

you can modify the path and change into your personal apk path and you can get the CFG signature.'


When you finish get the CFG signature you can use the file parseCFGResult.py to get the CFG graph


#****************************************
# Using method :
# java -jar CFGScanDroid.jar
#
# before we run this file we should run the CFGScanDroid
# sudo apt-get install maven
# ./build.sh 
#  This will create a file:
# target/CFGScanDroid.jar
#***********************************************




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


3. we can run the m core by running the file : python mcore.py 

you can find the file in the directory named 3D-CFG

4. use the mjaccard.py to get the mcore similarity

running : python python mjaccard.py




**********************************************************************

how to get the view core  



we need to download thress tools
1. apktool
2. dex2jar
3. A3E


install the apktool and dex2jar 

install jdk, unzip


1. We first should create the VFG graph.

When we generate the VFG, we should install the A3E.

You can download the A3E here: https://github.com/tanzirul/a3e


When we download the a3e tools we should put the file createSatg.py into the a3e-master/satg
runing the file python createSatg.py you can create the ATG.

if you want to run this file, you need to change the path of the a3e result.


when you open the file parseSatg.py you also can see the instruction

===========================================================
running : python parseSatg.py
you can input different number to choose the different PATH
**********************************************************
input : 0 -> original APKs 
input : 1 -> repackaged APKs 
input : 2 -> test PATH 
input : 3 -> your PATH 
===========================================================
'''

When we get the the results which is create by the a3e we should create  the graph.


A3E helps us get the Activity invocation relations, we use the relations to get the ATG.


    ##################
    # the format of satg
    # <ActivityGraph>
    #   <Activity name = "com.anddoes.launcher">
    #       <ChildActivity name = "com.anddoes.launcher" />  # the same name with the Activity
    #       <ChildActivity name = "com.anddoes.launcher2.launcher" event_handler="click" />
    #       <ChildActivity name = "com.anddoes.launcher2.launcher" event_handler="double_click" />
    #       <ChildActivity name = "com.anddoes.APxService">
    #   </Activity>
    # </ActivityGraph>


We can get the running results of A3E but we should also parse this file and get the following results for each app


B8B15A52DFC953B2A5E448A8A762EBEE190E0E425C53325D32E78058C65DBE34
0
e com.tgb.coldjustice.StartGame --> com.tgb.coldjustice.MainMenu
e 0 --> 1
e com.tgb.coldjustice.MainMenu --> com.tgb.coldjustice.LevelSelection
e 1 --> 2
e com.tgb.coldjustice.MainMenu --> com.tgb.coldjustice.activities.LBAds
e 1 --> 3
e com.tgb.coldjustice.MainMenu --> com.tgb.coldjustice.Help
e 1 --> 4
e com.tgb.coldjustice.MainMenu --> com.tgb.coldjustice.inapp.CJInApPurchase
e 1 --> 5
e com.tgb.coldjustice.LevelSelection --> com.tgb.coldjustice.inapp.CJInApPurchase
e 2 --> 5
e com.tgb.coldjustice.activities.CJActivity --> com.tgb.coldjustice.inapp.CJInApPurchase
e 6 --> 5
e com.tgb.coldjustice.activities.CJActivity --> com.tgb.coldjustice.MissionFail
e 6 --> 7
e com.tgb.coldjustice.activities.CJActivity --> com.tgb.coldjustice.MissionComplete
e 6 --> 8
e com.tgb.coldjustice.managers.IntentReceiver --> com.tgb.coldjustice.MainMenu
e 9 --> 1
e com.tgb.coldjustice.Pause --> com.tgb.coldjustice.inapp.CJInApPurchase
e 10 --> 5
e com.tgb.coldjustice.Pause --> com.tgb.coldjustice.activities.CJActivity
e 10 --> 6
e com.tgb.coldjustice.Pause --> com.tgb.coldjustice.activities.LBAds
e 10 --> 3
e com.tgb.coldjustice.Pause --> com.tgb.coldjustice.LevelSelection
e 10 --> 2
e com.tgb.coldjustice.MissionComplete --> com.tgb.coldjustice.activities.CJActivity
e 8 --> 6
e com.tgb.coldjustice.MissionComplete --> com.tgb.coldjustice.activities.LBAds
e 8 --> 3
e com.tgb.coldjustice.MissionComplete --> com.tgb.coldjustice.LevelSelection
e 8 --> 2
e com.tgb.coldjustice.MissionFail --> com.tgb.coldjustice.activities.CJActivity
e 7 --> 6
e com.tgb.coldjustice.MissionFail --> com.tgb.coldjustice.activities.LBAds
e 7 --> 3
e com.tgb.coldjustice.MissionFail --> com.tgb.coldjustice.inapp.CJInApPurchase
e 7 --> 5
e com.tgb.coldjustice.MissionFail --> com.tgb.coldjustice.LevelSelection
e 7 --> 2

Runing the parseSatg.py file, we can create the Activitiy Graph 

the ATG (Activity Transition Graph) will be store in the files

0 1
0 2
0 3
0 4
1 5
2 3
2 5
3 4
3 6
3 7
3 8
3 9
3 10


2. we get the above result by running the file  createATGraph_*.py

you can choose different files based on deleting the third-party libs or not.

each graph can be indicates in this way and each number indicates a node 

each line indicates a edge

We when compare these graph, we also set up the pre-filter by comparing the size and node features and edge features



4. python vcore.py you can get the vcore value vector


5. the getWeight.py file can calculate the weight value of the m graph and v graph







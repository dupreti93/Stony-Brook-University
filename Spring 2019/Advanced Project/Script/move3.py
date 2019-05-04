import traceback
import re
import os
import sys
from datetime import datetime

def main(student_names, workspace, file_name,argsInfo,recArg,keyWdArg):
    # Get the names from student-info - As before
    student_info = open(student_names, "r")
    names = {}
    for student in student_info:
        info = student.split()
        names[info[0]] = info[1]

    # Get the list of python files - As before
    path = workspace
    files = os.listdir(path)
    python_files = [i for i in files if i.endswith(".py")]


    d_student = {}
    for file in python_files:

        # We won't touch the driver move2.py file
        if file=='move3.py':
            continue


        source_path = path + "/" + file



        # Change - 1 : Checking for invalid input() functions
        content = open(source_path, "r").readlines()
        excep = False
        for i in content:
            if bool(re.search('input\(\)', i)):
                excep = True
                break
            if bool(re.search('__main__', i)):
                break

        #Getting the complete data of file
        data = open(source_path, "r").read().strip()
        #Creating regex patterns
        pat="([\s\S]*)__name__"
        data = re.findall(pat,data)
        if len(data)==0:
            data=""
        else:
            data = data[0]
        try:
            if excep:
                raise Exception

            pattern_sbuID = "#(.*?)(\d{9})"
            pattern_funcID = "([A-Za-z0-9\-\_\,]+\s*\([A-Za-z0-9\-\_\,\s]+\))" # Change - 2 Reg ex pattern to match the function name along with arguments(may contain spaces)

            #Extracting all the functions names that file can possibly have
            function_list = file_name.split(',')
            argsList = argsInfo.split(",")
            recList = recArg.split(',')
            keyWdList = keyWdArg.split(',')

            #Extracting SBU ID and functions present in file

            sbuID = re.findall(pattern_sbuID, data)[0][1]
            functions = re.findall(pattern_funcID, data)
            print(functions)
            #Extracting only main function that will represent name of the file
            flag1=True
            count=0 #Change -3
            prevName = None
            f_id = None
            for i in range(len(functions)):
                s=functions[i]
                funcNamePat ="[A-Za-z0-9\-\_\,\s]+"
                argsPat = "\([A-Za-z0-9\-\_\,\s]+\)"
                fName = re.findall(funcNamePat, s)[0].strip()
                print(fName,len(fName))
                args = re.findall(argsPat,s)
                numArgs = len(args[0].split(","))
                print(numArgs)

                for j in range(len(function_list)):
                    if fName == function_list[j] and numArgs==int(argsList[j]):
                        flag1=False
                        function_name=fName
                        f_id=j
                        if prevName is not None and prevName!=function_name:
                            raise Exception()
                        prevName = function_name
                        count+=1
            print("count:",count)
            if flag1:   #Change - 3
                raise Exception()
            if count==1 and recList[f_id]=='Y':
                raise Exception()
            if keyWdList[f_id] is not 'None':
                if re.search(keyWdList[f_id],data):
                    raise Exception()

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            #Change 4 Rejected directory
            if not os.path.exists(path+'/Rejected'):
                os.makedirs(path+'/Rejected')
            os.rename(source_path, path+'/Rejected'+'/'+file)
            continue



        if sbuID in names.keys():   # - As before
            netID = names[sbuID]
            if netID in d_student:
                flag=True
                for i in range(len(d_student[netID])):
                    a,b,c = d_student[netID][i]
                    if a== function_name:
                        if b<os.stat(source_path).st_mtime:
                            flag=False
                            del(d_student[netID][i])
                            d_student[netID].append((a,os.stat(source_path).st_mtime,file))
                        else:
                            flag=False
                if flag:
                    d_student[netID].append((function_name,os.stat(source_path).st_mtime,file))
            else:
                d_student[netID]=[(function_name,os.stat(source_path).st_mtime,file)]
        else:
            print("here is the failure")
            if not os.path.exists(path+'/Rejected'):
                os.makedirs(path+'/Rejected')
            os.rename(source_path, path+'/Rejected'+'/'+file)
            continue


    for netID in d_student:
        destination_folder = path + "/" + netID
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        for j in range(len(d_student[netID])):
            function_name,time,file_name = d_student[netID][j]
            source_path = path + "/" + file_name
            func_name_wo_params = ""
            for i in range(len(function_name)):
                if function_name[i]=='(':
                    break
                func_name_wo_params+=function_name[i]
            os.rename(source_path, destination_folder + "/" + func_name_wo_params + ".py")



    

if __name__ == '__main__':
    # "./student-info.txt"
    # "./sorting workspace"
    # Arg 1 = Student Info file - As before
    # Arg 2 = Workspace Folder - As before
    # Arg 3 = function names separaetd by a delimiter symbol of your choice (I have taken '*') eg. : "funcA*funcB*funcC*funcD"
    #main("student-info.txt","/Users/divyansh_upreti/Downloads/this/","getSeconds*tip_amount*population")
    main(sys.argv[1], sys.argv[2], sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    '''
    Type this in terminal:
    
    
            'python move2.py student-info.txt /Users/divyansh_upreti/Downloads/this/ funcA,funcB,funcC,funcD 1,2,1,3 Y,N,N,N sort(),None,None,None
    
    
                Please replace the second argument with the directory which contains the file move2.py
    '''

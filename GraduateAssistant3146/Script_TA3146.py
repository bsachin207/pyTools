# -*- coding: utf-8 -*-
"""
Created on Mon Oct 03 13:49:37 2016

Restriction- 
1. First 3 lines of gradebook should be header(mute the assignment before exporting the gradebook)
2. Defaulter student get 0 score
3. OS specific and python version(2.7) specific
4. Code is written for Windows Platform. Directory path notations are different for different OS.
5. Do not keep the script in the same directory of csv files

Usage-
1. Copy the csv files of video questions to be graded in a directory
2. The directory should also contain the exported gradebook
3. The directory should only contain above files (no other files should be in the directory)
4. Program will ask you for the directory path and should be entered in quotes
5. Program will display the list of assignments. Select the one you are grading
6. Program will show Defaulter student's list - The student who did not attemp the video quetions
7. Program will generate the upload ready version with the same name as of gradebook
8. The upload ready gradebook will in the same directory as of program.
9. You may directly import the generated csv in your gradebook.

Please feel free to provide your suggesetions/modification or contact me for any help
at - sbadguja@uncc.edu

@author: Sachin


"""

#import pandas
import os
import csv
import sys
import collections

student_dict = {} #contails name as a key and loginID as a value


def create_gradebook(gradebook,class_grades):
    upload_grade = gradebook.split('\\')[-1]
    fread = open(gradebook,'rb')
    grade_reader = csv.reader(fread)
    fwrite = open(upload_grade,'wb')
    grade_writer = csv.writer(fwrite)
    idx = -1
    for row in grade_reader:        
        if assignment_name in row:
            idx = row.index(assignment_name)
        if row[0] in class_grades:
            row[idx] = class_grades[row[0]]
        
        grade_writer.writerow([row[x] for x in [0,1,2,3,idx]])        
        #This writes the complete gradebook
        #grade_writer.writerow(row)
        
    fread.close()
    print upload_grade
    fwrite.close()
    
    
def write_grades(grades_dict):
    class_grades = collections.defaultdict(int)
    for k in student_dict:
        name_parts = k.split(',')
        name = name_parts[1].strip()+ ' '+ name_parts[0]
        if name in grades_dict:
            class_grades[k] = grades_dict[name]
            
        elif student_dict[k] in grades_dict:
      
            class_grades[k] = grades_dict[student_dict[k]]
      
        else:
            class_grades[k] = -1
    
    return class_grades

# this function displays all the assignment list to choose from     
def selectAssignment(filepath):
    f = open(filepath,'r')
    reader = csv.reader(f)
    header_list = reader.next()
    reader.next()
    reader.next()
    for row in reader:
        student_dict[row[0]] = row[2]
    
    if 'Student, Test' in student_dict :
        del student_dict['Student, Test']
    f.close()
    
    assignment_list = [element for element in header_list if element.strip().endswith(')')]
    print "Please select the assignment you want to grade-\n"
    for i in range(len(assignment_list)):
        print str(i)+". "+assignment_list[i]
    selector = int(input("Enter your choice- "))
    return assignment_list[selector]
    
    
def calculateGrades(dirpath):
    grades_dict = collections.defaultdict(int)
    class_total_grades = collections.defaultdict(int)
    defaulter_list = collections.defaultdict(list)
    for file_path in dirpath:
        f = open(file_path, 'r')
        reader = csv.reader(f)
        reader.next()
        for k,v in reader:
            grades_dict[k] = int(v[9:10])

        f.close()
        
        class_grades = write_grades(grades_dict)
        for k in class_grades:
            if class_grades[k] < 0:
                defaulter_list[file_path].append(k)
                class_total_grades[k] = 0
            else:
                class_total_grades[k] += class_grades[k]

    return class_total_grades, defaulter_list

    
    
            
if __name__ == '__main__':
    mypath = input("Please enter the grading directory path-")
    if not os.path.isdir(mypath):
        print "This is not a valid directory path"
        sys.exit()
    #mypath = "D:\TA-ITSC3146\ScriptInput"
    onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    gradebook = [x for x in onlyfiles if x.find('Grades')][0]
    
    if len(gradebook) < 1:
        print "\nThere is no gradebook in the directory\n"
        sys.exit()

    onlyfiles.pop(onlyfiles.index(gradebook))
    
    assignment_name = selectAssignment(gradebook)
    
    class_grades, defaulter_list = calculateGrades(onlyfiles)
    
    create_gradebook(gradebook,class_grades)
    
    print "\n******************Defaulter List********************\n"
    for element in defaulter_list:
        print element.split('\\')[-1] +" - "
        print defaulter_list[element]
        print "\n"
    
 

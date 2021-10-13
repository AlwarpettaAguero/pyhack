import requests
import json
from datetime import date, timedelta, datetime
from dateutil import parser
import sys

study_id = 'StudyHack'
ae_domain_id ='ae'
cm_domain_id = 'cm'

base_url = 'https://pyhack-dot-pharmanlp-177020.uc.r.appspot.com/api/1/'
ae_subject_id_url = base_url + study_id+'/'+ae_domain_id+'/subject/list'
cm_subject_id_url = base_url + study_id+'/'+ae_domain_id+'/subject/list'

try:
    ae_response_data1 = requests.get(ae_subject_id_url)
    ae_response_value1 = json.loads (ae_response_data1.text)
    ae_subject_ids = ae_response_value1['data']
except:
    sys.exit("Unable to get the values!")
    
try:
    cm_response_data1 = requests.get(cm_subject_id_url)
    cm_response_value1 = json.loads (cm_response_data1)
    cm_subject_ids = cm_response_value1['data']
except:
    sys.exit("Unable to get the values!")

discrepancy_master_list = []



# Patient and row for which Medication is given prior to Adverse Event
# Function will get data at subject_id level 
# Identify discrepancy and return discrepancy_list as a list 

def type1_check(ae_subject_data,cm_subject_data):
    discrepancy_list = []
    

    #Iterate through cm_subject_data
    for cm_row in cm_subject_data:
        
        #fetch cmaeno, cmstdat,cmendat, cmtrt from cm_subject_data 
        cmaeno = cm_row['cmaeno']
        cmstdat = cm_row['cmstdat']
        cmendat = cm_row['cmendat']
        cmtrt = cm_row['cmtrt']
        #Iterate through ae_subject_data
        for ae_row in ae_subject_data:
            
            #fetch aespid, aestdat, aeendat, aeterm from ae_subject_data

            aespid = ae_row['aespid']
            aestdat = ae_row['aestdat']
            aeendat = ae_row['aeendat']
            aeterm = ae_row['aeterm']
            
            #Check whether aespid and cm_ae_no are equal
            if aespid == cmaeno:
                #Check whether cmstdat is lesser than aestdat
                if cmstdat<aestdat:
                    #For the records satisfying condition prepare payload
                    payload={}
                    payload['formname'] = cm_row['formname']
                    payload['formid'] = cm_row['formid']
                    payload['formidx']= cm_row['formidx']
                    payload['type'] = 'TYPE1'
                    payload['subjectid'] = cm_row['subjectid']
                    discrepancy_list.append(payload)
            
    return discrepancy_list

#Type 2 check : Patients and rows for which days Medications are given and Adverse Event occur don't match

# Patients and rows for which days Medications are given and Adverse Event occur don't match
# Function will get data at subject_id level 
# Identify discrepancy and return discrepancy_list as a list 

def type2_check(ae_subject_data,cm_subject_data):
    discrepancy_list = []
    

    #Iterate through cm_subject_data
    for cm_row in cm_subject_data:
        
        #fetch cmaeno, cmstdat,cmendat, cmtrt from cm_subject_data 
        cmaeno = cm_row['cmaeno']
        cmstdat = cm_row['cmstdat']
        cmendat = cm_row['cmendat']
        cmtrt = cm_row['cmtrt']
        #Iterate through ae_subject_data
        for ae_row in ae_subject_data:
            
            #fetch aespid, aestdat, aeendat, aeterm from ae_subject_data
            aespid = ae_row['aespid']
            aestdat = ae_row['aestdat']
            aeendat = ae_row['aeendat']
            aeterm = ae_row['aeterm']
            #Check whether aespid and cm_ae_no are equal
            if aespid == cmaeno:
                #Check whether aeendat is lesser than cmstdat
                if aeendat<cmstdat:
                    #For the records satisfying condition prepare payload
                    payload={}
                    payload['formname'] = cm_row['formname']
                    payload['formid'] = cm_row['formid']
                    payload['formidx']= cm_row['formidx']
                    payload['type'] = 'TYPE2'
                    payload['subjectid'] = cm_row['subjectid']
                    discrepancy_list.append(payload)
            
    return discrepancy_list


# Write a method to calculate the dates between two given dates 
# Return a list of dates in between two given dates
# for e.g. 01/01/2021 and 01/05/2021 are the two dates. Function should return 
# 01/01/2021,01/02/2021,01/03/2021,01/04/2021,01/05/2021

def func_inbetween_dates(start_date,end_date):
  try:
    inbetween_dates=[]


    start_date=datetime.strptime(start_date, '%d-%b-%y').strftime('%m/%d/%Y')
    end_date=datetime.strptime(end_date, '%d-%b-%y').strftime('%m/%d/%Y')


    start_date_new=start_date.split('/')#split the date based on delimiter
    year=int(start_date_new[2])#extract and store the year as int in a variable
    month=int(start_date_new[0])#extract and store the month as int in a variable
    day=int(start_date_new[1])#extract and store the day as int in a variable
    sdate=date(year,month,day)#create sdate to pass as an argument


    end_date_new=end_date.split('/')
    year=int(end_date_new[2])
    month=int(end_date_new[0])
    day=int(end_date_new[1])
    edate=date(year,month,day)


    delta = edate - sdate       # as timedelta

    for i in range(delta.days + 1):
      day = sdate + timedelta(days=i)
      day1 = day.strftime('%m/%d/%Y')
      inbetween_dates.append(day1)

      return inbetween_dates
  except Exception :
    return list()


#Type 3 check : Duplicate Adverse events are entered or Adverse Events overlap. 

def type3_check(ae_subject_data):
    discrepancy_list = []
    
    #Iterate through ae_subject_data
    
    for ae_row in ae_subject_data:
        
        #fetch aespid,aestdat,aeendat,aeterm 
        aespid = ae_row['aespid']
        aestdat = ae_row['aestdat']
        aeendat = ae_row['aeendat']
        aeterm = ae_row['aeterm']
        #call func_inbetween_dates method and get the list of dates in between aestdat,aeendat
        
        inbetween_dates = func_inbetween_dates(aestdat,aeendat)

        
        #Nested for loop on ae_subject_data 
        for ae_row1 in ae_subject_data:
            
            #fetch aespid,aestdat,aeendat,aeterm and assign it to different variables 
            aespidnew = ae_row['aespid']
            aestdatnew = ae_row['aestdat']
            aeendatnew = ae_row['aeendat']
            aetermnew = ae_row['aeterm']


            # Check to make sure that you are not looking at the same row using aespid check.
            if aespid != aespidnew:


             # Check to make sure aeterm between loop1 and loop2 are matching.
              if aeterm == aetermnew:


              # check to see whether aestdat from loop2 is in inbetween_dates or aeendat from loop2 is in inbetween_dates
                payload={}
                payload['formname'] = ae_row['formname']
                payload['formid'] = ae_row['formid']
                payload['formidx']= ae_row['formidx']
                payload['type'] = 'TYPE3'
                payload['subjectid'] = ['subjectid']
                discrepancy_list.append(payload)
              
                        
    return discrepancy_list


#Type 4 check : Duplicate Concomitant Medications or overlap. 

def type4_check(cm_subject_data):
    
    discrepancy_list = []
    
    #Iterate through cm_subject_data
    
    for cm_row in cm_subject_data:
        
        #fetch cmaeno,cmstdat,cmendat,cmtrt 
        cmaeno = cm_row['cmaeno']
        cmstdat = cm_row['cmstdat']
        cmendat = cm_row['cmendat']
        cmtrt = cm_row['cmtrt']



        #call func_inbetween_dates method and get the list of dates in between aestdat,aeendat        
        inbetween_dates = func_inbetween_dates(cmstdat,cmendat)


        #Nested for loop on cm_subject_data
        
        for cm_row1 in cm_subject_data:
        
            #fetch cmaeno,cmstdat,cmendat,cmtrt  and assign it to different variables
            cmaenonew = cm_row['cmaeno']
            cmstdatnew = cm_row['cmstdat']
            cmendatnew = cm_row['cmendat']
            cmtrtnew = cm_row['cmtrt']


            # Check to make sure that you are not looking at the same row using cmaeno check
            if cmaeno != cmaenonew :
                

             # Check to make sure cmtrt between loop1 and loop2 are matching.
              if cmtrtnew==cmtrt:


               # check to see whether cmstdat from loop2 is in inbetween_dates or cmendat from loop2 is in inbetween_dates
                payload ={}
                payload['formname'] = cm_row['formname']
                payload['formid'] = cm_row['formid']
                payload['formidx']= cm_row['formidx']
                payload['type'] = 'TYPE4'
                payload['subjectid'] = cm_row['subjid']
                discrepancy_list.append(payload)

    return discrepancy_list

def type5_check(ae_subject_data,cm_subject_data):
    discrepancy_list = []
    

    #Iterate through cm_subject_data
    for cm_row in cm_subject_data:
        
        #fetch cmaeno, cmstdat,cmendat, cmtrt from cm_subject_data 
        cmaeno = cm_row['cmaeno']
        cmstdat = cm_row['cmstdat']
        cmendat = cm_row['cmendat']
        cmtrt = cm_row['cmtrt']
        #Iterate through ae_subject_data
        for ae_row in ae_subject_data:
            
            #fetch aespid, aestdat, aeendat, aeterm from ae_subject_data
            aespid = ae_row['aespid']
            aestdat = ae_row['aestdat']
            aeendat = ae_row['aeendat']
            aeterm = ae_row['aeterm']
            #Check whether aespid and cm_ae_no are equal
            if aespid == cmaeno:
                #Check whether aeendat is greater than cmendat
                if aeendat>cmendat:
                    #For the records satisfying condition prepare payload
                    payload={}
                    payload['formname'] = cm_row['formname']
                    payload['formid'] = cm_row['formid']
                    payload['formidx']= cm_row['formidx']
                    payload['type'] = 'TYPE2'
                    payload['subjectid'] = cm_row['subjectid']
                    discrepancy_list.append(payload)
            
    return discrepancy_list


# iterate through ae_subject_ids 

for subject in ae_subject_ids:
    ae_subject_data_url = base_url + "/" + study_id+"/" + ae_domain_id + "/subject/" + str(subject)+ "/list"
    ae_response_data2 =  requests.get(ae_subject_data_url)
    ae_response_value2 = json.loads(ae_response_data2.text)
    ae_subject_data = ae_response_value2['data']
    
    cm_subject_data_url = base_url + "/" + study_id+"/" + cm_domain_id + "/subject/" + str(subject)+ "/list"
    cm_response_data2 = requests.get(cm_subject_data_url)
    cm_response_value2 =json.loads(cm_response_data2) 
    cm_subject_data = cm_response_value2['data']
    
    
    discrepancy_list = type1_check(ae_subject_data,cm_subject_data)
    #check whether discrepancy list is not empty then add it to discrepancy_master_list
    if discrepancy_list:
      discrepancy_master_list.append(discrepancy_list)

    discrepancy_list = type2_check(ae_subject_data,cm_subject_data)
    #check whether discrepancy list is not empty then add it to discrepancy_master_list
    if discrepancy_list:
      discrepancy_master_list.append(discrepancy_list)

    discrepancy_list = type3_check(ae_subject_data)
    #check whether discrepancy list is not empty then add it to discrepancy_master_list
    if discrepancy_list:
      discrepancy_master_list.append(discrepancy_list)
    
    discrepancy_list = type4_check(cm_subject_data)
    #check whether discrepancy list is not empty then add it to discrepancy_master_list
    if discrepancy_list:
      discrepancy_master_list.append(discrepancy_list)
    

    discrepancy_list = type5_check(cm_subject_data)
    #check whether discrepancy list is not empty then add it to discrepancy_master_list
    if discrepancy_list:
      discrepancy_master_list.append(discrepancy_list)



# To submit discrepancies    
submission_url = base_url + study_id
email_address = "venkatr636@gmail.com"

# iterate through every discrepancy in discrepancy_master_list

for discrepancy in discrepancy_master_list:
    discrepancy["venkatr636@gmail.com"] = email_address
    try:
        r = requests.post(submission_url,data=discrepancy)
    except:
        sys.exit("Unable to submit discrepancy")
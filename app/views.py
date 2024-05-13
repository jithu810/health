from django.shortcuts import render,redirect
from.models import*
from django.contrib.auth.models import auth,User
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
import os
import pandas as pd
import random


df_map = None
filtered_df= None
dallies={}
c={}

# Create your views here.
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect(upload_file)  # Redirect to admin dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request,'index.html')


def Mapping(dataframe)-> pd.DataFrame:
    column_mapping1={
        "qhwlthi": "Wealth index quintile","qb113": "Hemoglobin level (g/dl)",
        "hc27": "Gender","hc57": "Anemia level",
        "q711e": "Child drank commercially produced infant formula",
        "q711h": "Child ate commercially fortified cereal (baby food)", 
        "qb103d": "day", "qb103m": "month", "qb103y": "year",
        "qb105": "Weight in kilograms",
        "qcsd7": "BMI Standard deviations  (according to WHO)",
        "q521": "Number of days took iron tablets",
        }
    category_mapping = {
    1: 'Severe anemia',
    2: 'Moderate anemia',
    3: 'Mild anemia',
    4: 'Normal anemia'
    }
    category_mapping2 = {
    1: 'Poorest',
    2: 'Second',
    3: 'Third',
    4: 'Fourth',
    5: 'Richest'
    }
    category_mapping3 = {
    1: 'Male',
    2: 'Female'
    }
    # Rename columns based on the mapping dictionary
    columns_to_drop = [col for col in dataframe.columns if col not in column_mapping1.keys()]
    dataframe = dataframe.rename(columns=column_mapping1)
    # Map integers to categories
    bins = pd.qcut(dataframe['Weight in kilograms'], q=5, precision=0)

    # Get the bin labels
    bin_labels = [f"{int(bin_.left)} - {int(bin_.right)}" for bin_ in bins]

    # Assign the bin labels to a new column in the DataFrame
    dataframe['Weight in kilograms'] = bin_labels
    bins1 = pd.qcut(dataframe['Number of days took iron tablets'], q=10,duplicates='drop', precision=0)

    # Get the bin labels
    bin_labels1 = [f"{int(bin_.left)} - {int(bin_.right)}" for bin_ in bins1]
    
    dataframe['Number of days took iron tablets'] = bin_labels1
    bins2 = pd.qcut(dataframe['BMI Standard deviations  (according to WHO)'], q=10,duplicates='drop', precision=0)

    # Get the bin labels
    bin_labels2 = [f"{int(bin_.left)} - {int(bin_.right)}" for bin_ in bins2]

    # Assign the bin labels to a new column in the DataFrame
    dataframe['BMI Standard deviations  (according to WHO)'] = bin_labels2
    dataframe['Anemia level'] = dataframe['Anemia level'].map(category_mapping)
    dataframe["Wealth index quintile"] = dataframe["Wealth index quintile"].map(category_mapping2)
    dataframe['Gender'] = dataframe['Gender'].map(category_mapping3)
    dataframe['Hemoglobin level (g/dl)'] = dataframe['Hemoglobin level (g/dl)'].apply(lambda x: 'Anemia' if x >= 11 else 'No anemia')
    dataframe["Child drank commercially produced infant formula"] = dataframe["Child drank commercially produced infant formula"].apply(lambda x: 'No' if x > 1 else 'Yes')
    dataframe["Child ate commercially fortified cereal (baby food)"] = dataframe["Child ate commercially fortified cereal (baby food)"].apply(lambda x: 'No' if x > 1 else 'Yes')
    dataframe = dataframe.drop(columns=columns_to_drop)
    return dataframe






def upload_file(request):
    acc = User.objects.get(username = request.user)
    name = acc.username
    global df_map
    global df_copy
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        # Save the file to a specific location
        # Define the path to save the uploaded file
        upload_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'csv_files')
        os.makedirs(upload_path, exist_ok=True)  # Create the directory if it doesn't exist
        
        # Save the uploaded file to the upload path
        file_path = os.path.join(upload_path, uploaded_file.name)
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        df = pd.read_csv(file_path)
        df_map = Mapping(df)
        df_copy = df_map.copy()

        
        df_copy = df_copy.drop(columns=['Anemia level','day','month','year'])

        context = {
            'key':df_copy,
            'title1':'Home',
            'title2':'Dashboard',
            'title3':'Result',
            'main_title':'Result',
            'name':name
        }
        return redirect(file_upload_result_one)
    context ={
        'title1':'Home',
        'title2':'Dashboard',
        'title3':'File Upload',
        'main_title':'File Upload',
        'name':name
    }
    return render(request,'upload_file.html',context)

def dashboard(request):
    return render(request,'dashboard.html')

def file_upload_result_one(request):
    acc = User.objects.get(username = request.user)
    name = acc.username
    dallies.clear()
    context = {
        'key':df_copy,
        'title1':'Home',
        'title2':'Dashboard',
        'title3':'Result',
        'main_title':'Result',
        'name':name
    }
    return render(request,'file_upload_result_one.html',context)


def get_unique_list(df,value):
    unique_value_list = df[value].unique()
    return unique_value_list


def file_upload_result_two(request):
    acc = User.objects.get(username = request.user)
    name = acc.username
    if request.method == 'POST':
        i_value = request.POST['selected_value']

        unique_value_list=get_unique_list(df_map,i_value)
        data={}
        for i in unique_value_list:
            # print(len(df_map[df_map[i_value] == i]))
            data[i]=len(df_map[df_map[i_value] == i])

        context = {
                'key':data,
                'title1':'Home',
                'title2':'Dashboard',
                'title3':'Result',
                'main_title':'Result',
                'name':name,
                'column_name':i_value
            }
        return render(request,'file_upload_result_two.html',context)
import json

def graph_one(request):
    dallies.clear()
    acc = User.objects.get(username=request.user)
    name = acc.username
    if request.method == 'POST':
        i_value = request.POST['selected_value']
        unique_value_list = get_unique_list(df_map, i_value)
        data = {}
        for i in unique_value_list:
            count = len(df_map[df_map[i_value] == i])
            data[i] = {'count': count}
        
        keys_list = list(data.keys())
        keys_list_val = list(data.values())
        # print('hello',keys_list_val)
        values_list = [item['count'] for item in keys_list_val]

        # Generate barColors dynamically
        barColors = ['#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)) for _ in range(len(keys_list))]
        # Construct keys_list_enum as list of tuples (key, color)
        keys_list_enum = [(key, color) for key, color in zip(keys_list, barColors)]
        all_list = [{"label": key, "color": color, "count": int(count)} for key, color, count in zip(keys_list, barColors, values_list)]
        
        # Convert the list to a JSON string
        json_string = json.dumps(all_list)
        context = {
            'key1': data,
            'all_list': json_string,
            'title1': 'Home',
            'title2': 'Dashboard',
            'title3': 'Result',
            'main_title': 'Result',
            'name': name,
            'column_name': i_value
        }

        return render(request, 'graph_one.html', context)

def get_anemia_count(filtered_df,anemia,anemia_level):
    result_df = filtered_df[filtered_df[anemia] == anemia_level]
    return result_df


def graph_two(request):
    global filtered_df
    dallies.clear()
    acc = User.objects.get(username = request.user)
    name = acc.username
    if request.method == 'POST':
        i_value = request.POST['selected_value']
        column_name = request.POST['column_name']

        Anemia_level = df_map['Anemia level'].unique()
        filtered_df = df_map[df_map[column_name] == i_value]
        data={}
        for i in Anemia_level:
            # get_anemia=get_anemia_count(filtered_df,'Anemia level',i)
            data[i]=len(get_anemia_count(filtered_df,'Anemia level',i))

        keys_list = list(data.keys())
        values_list = list(data.values())
        barColors = ['#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)) for _ in range(len(keys_list))]
        all_list = [{"label": key, "color": color, "count": count} for key, color, count in zip(keys_list, barColors, values_list)]

        # Convert the list to a JSON string
        json_string = json.dumps(all_list)

        context = {
                'key2':data,
                'all_list': json_string,
                'title1':'Home',
                'title2':'Dashboard',
                'title3':'Result',
                'main_title':'Result',
                'name':name,
                'dataframe':filtered_df
            }
        return render(request,'graph_two.html',context)


def group(count):
    count['period'] = (count['year'] - 2019) * 2 + (count['month'] - 1) // 6 + 1
    grouped_df = count.groupby('period')
    group_list = []
    for period, group in grouped_df:
        group_list.append(group)
    return group_list

# views.py
def calculate_daly(count_value, Disability_weights, deaths, L, LYLL):
    YLD=count_value+Disability_weights+L
    YLL=deaths * LYLL
    DALY=YLD+YLL
    return DALY


import json
import numpy as np
from scipy.interpolate import interp1d

def gggraph(request):
    global dallies
    if request.method == 'POST':
        year_range = request.POST.get('yearRange')
        print("Selected year range:", year_range)

        if year_range.isdigit():
            year_range = int(year_range)
        else:
            year_range = 1  

        chart_data = []
        for label, values in dallies.items():
            original_x = np.arange(1, len(values) + 1)
            original_y = np.array(values)

            if len(original_x) > 1:  # Ensure there are enough points to interpolate
                interpolator = interp1d(original_x, original_y, kind='linear', fill_value="extrapolate")
                new_x = np.linspace(1, year_range, num=year_range)  # Create new x values up to the selected year range
                new_y = interpolator(new_x)
            else:
                new_x = np.arange(1, year_range + 1)
                new_y = np.full_like(new_x, original_y[0] if original_y.size > 0 else 0)

            new_data = [{'x': int(x), 'y': float(y)} for x, y in zip(new_x, new_y)]
            chart_data.append({
                'label': label,
                'data': new_data
            })

        chart_data = json.dumps(chart_data)
    return render(request, 'your_template.html', {'chart_data': chart_data})



def pie_chart(request):
    global c,dallies
    if request.method == 'POST':
        m=[]
        for key, value in c.items():
            key_value = request.POST.get(f"{key}_key")
            count = request.POST.get(f"{key}_count")
            Disability_weight = request.POST.get(f"{key}_input1")
            death = request.POST.get(f"{key}_input2")
            l = request.POST.get(f"{key}_input3")
            lyll = request.POST.get(f"{key}_input4")

            count=int(count)
            Disability_weight=float(Disability_weight)
            death=float(death)
            l=float(l)
            lyll=float(lyll)
            DALY = calculate_daly(count,Disability_weight,death, l, lyll)
            m.append(DALY)
        dallies[key_value]=m

        chart_data = []
        for label, values in dallies.items():
            chart_data.append({
                'label': label,
                'data': [{'x': i, 'y': val} for i, val in enumerate(values, start=1)]
            })

        chart_data = json.dumps(chart_data)
        return render(request, 'your_template.html', {'chart_data': chart_data})
  


def graph_three(request):
    global filtered_df,c
    acc = User.objects.get(username = request.user)
    name = acc.username
    if request.method == 'POST':
        d_weights=[0.001,0.004,0.052,0.149]
        i_value = request.POST['selected_value']
        selected_value = i_value
        count=get_anemia_count(filtered_df,'Anemia level',i_value)
        data=group(count)
        for idx, df in enumerate(data):
            c["time"+str(idx + 1)]=len(df)
        if selected_value=="Normal anemia":
            Disability_weight=d_weights[0]
        elif selected_value=="Mild anemia":
            Disability_weight=d_weights[1]
        elif selected_value=="Moderate anemia":
            Disability_weight=d_weights[2]
        elif selected_value=="Severe anemia":
            Disability_weight=d_weights[3]

        deaths=0.02
        context = {
                    'Disability_weight': Disability_weight,
                'deaths':deaths,
                'count_value':c,
                'selected_value':selected_value,
                'title1':'Home',
                'title2':'Dashboard',
                'title3':'Result',
                'main_title':'Result',
                'name':name,
                'dataframe':filtered_df
            }
        return render(request,'graph_three.html',context)




def file_upload_result_three(request):
    global filtered_df ,result_value
    acc = User.objects.get(username = request.user)
    name = acc.username
    i_value = request.GET.get('i', None)
    column_name = request.GET.get('column_name', None)
    Anemia_level = df_map['Anemia level'].unique()
    filtered_df = df_map[df_map[column_name] == i_value]
    data={}
    for i in Anemia_level:
        # get_anemia=get_anemia_count(filtered_df,'Anemia level',i)
        data[i]=len(get_anemia_count(filtered_df,'Anemia level',i))

    if request.method == 'POST':
        result_value = data
        print(result_value)
        context = {
            'data':data
        }
        return render(request,'input.html',context)

    context = {
            'key':data,
            'title1':'Home',
            'title2':'Dashboard',
            'title3':'Result',
            'main_title':'Result',
            'name':name,
            'dataframe':filtered_df
        }
    return render(request,'file_upload_result_three.html',context)


def logout_user(request):
    logout(request)
    return redirect(index)


def get_anemia_count(filtered_df,anemia,anemia_level):
    result_df = filtered_df[filtered_df[anemia] == anemia_level]
    return result_df

def input(request):
    input = []
    if request.method == 'POST':
        n1 = int(request.POST['fnum'])
        input.append(n1)
        n2 = int(request.POST['snum'])
        input.append(n2)
        n3 = int(request.POST['tnum'])
        input.append(n3)
        n4 = int(request.POST['fonum'])
        input.append(n4)

        data_value = request.POST['data_value']
        values_list = list(result_value.values())
        keys_list = list(result_value.keys())
        context={
            'keys_list':keys_list,
            'values_list':values_list,
            'input':input
        }
        return render(request,'graph.html',context)
    context ={
        'title1':'Home',
        'title2':'Dashboard',
        'title3':'Input',
        'main_title':'Input',
        
    }
    return render(request,'input.html',context)

def input_first(request):
    global filtered_df
    acc = User.objects.get(username = request.user)
    name = acc.username
    i_value = request.GET.get('i', None)
    column_name = request.GET.get('column_name', None)

    if request.method == 'POST':
        n1 = request.POST['fnum']
        n2 = request.POST['snum']
        n3 = request.POST['tnum']

        return redirect(graph)
    context ={
        'title1':'Home',
        'title2':'Dashboard',
        'title3':'Input',
        'main_title':'Input',
        'name':name
    }
    return render(request,'input.html',context)

def graph(request):
    acc = User.objects.get(username = request.user)
    name = acc.username
    context ={
        'title1':'Home',
        'title2':'Dashboard',
        'title3':'Graph',
        'main_title':'Graph',
        'name':name
    }
    return render(request,'graph.html',context)
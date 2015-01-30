from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.forms import formset_factory
from queryBuilder.forms import QueryForm, ConditionForm
from queryBuilder.models import Query

import datetime
import time
import json
import os


# Builds a query given user input
@login_required
def query_builder(request):
    condition_form_set = formset_factory(ConditionForm, extra=2, max_num=2)
    username = None
    creation_date = None
    query_model = Query()
    if request.user.is_authenticated():
        username = request.user.username
        query_model.user_name = username
        creation_date = time.strftime("%Y-%m-%d %H:%M:%S")
        query_model.create_date_time = creation_date

    if request.method == 'POST':
        form = QueryForm(request.POST, request.FILES)
        condition_form = condition_form_set(request.POST)
        if form.is_valid() and condition_form.is_valid():
            query_model.query_name = form.cleaned_data['query_name']
            start_date = form.cleaned_data['start_date']
            start_time = form.cleaned_data['start_time']
            start_date_time = datetime.datetime.combine(start_date, start_time)
            query_model.start_date_time = start_date_time
            end_date = form.cleaned_data['end_date']
            end_time = form.cleaned_data['end_time']
            end_date_time = datetime.datetime.combine(end_date, end_time)
            query_model.end_date_time = end_date_time
            stations = form.cleaned_data['stations']
            measurement = form.cleaned_data['measurement']
            nominal_volts = form.cleaned_data['nominal_volts']
            circuit_number = form.cleaned_data['circuit_number']
            measurement_identifier = form.cleaned_data['measurement_identifier']
            suffix = form.cleaned_data['suffix']
            conditions = []
            condition_type = form.cleaned_data['condition_type']
            condition_operator = form.cleaned_data['condition_operator']
            condition_value = form.cleaned_data['condition_value']
            primary_condition = Condition(condition_type, condition_operator, condition_value)
            conditions.append(primary_condition)

            for condition_field in condition_form:
                condition = Condition(condition_field.cleaned_data['condition_type'],
                                      condition_field.cleaned_data['condition_operator'],
                                      condition_field.cleaned_data['condition_value'])
                conditions.append(condition)

            file = request.FILES["file"]
            file_name = file.name
            query_model.file_name = file_name
            save_file(file)
            file_content = stringify_file(file)

            query_model.save()

            print(convert_to_json(username, query_model.id, creation_date, start_date_time, end_date_time,
                                  stations, conditions, measurement, nominal_volts, circuit_number,
                                  measurement_identifier, suffix, file_name, "r", file_content))

            delete_file(file)

            return HttpResponseRedirect('/query-result/')
    else:
        form = QueryForm()

    context = {'username': username, 'form': form, 'formset': condition_form_set}
    return render(request, 'queryBuilder/query-builder.html', context)


def stringify_file(file_path):
    data = ""
    with open(file_path.name, "rb") as file:
        for chunk in file_path.chunks():
            data += chunk.decode(encoding='UTF-8').replace('\r\n', '')

    return data


def save_file(file_path):
    destination = open(file_path.name, "wb")
    for chunk in file_path.chunks():
        destination.write(chunk)
    destination.close()


def delete_file(file_path):
    os.remove(file_path.name)

def convert_to_json(user_name, query_id, creation_date, start_date_time, end_date_time,
                    stations, conditions, measurement, nominal_volts, circuit_number,
                    measurement_identifier, suffix, file_name, file_type, file_content):

    query = json.dumps({
        "query": {
            "query_id": query_id,
            "created": creation_date.__str__(),
            "start": start_date_time.__str__(),
            "end": end_date_time.__str__(),
            "stations": stations,
            "analysis": {
                "file": file_name,
                "type": file_type,
                "content": file_content
            },
            "conditions": {
                "voltage": [],
                "current": [],
                "freq": []
            },
            "signal": {
                "measurement": measurement.__str__(),
                "nomvolts": nominal_volts,
                "circuit": circuit_number,
                "identifier": measurement_identifier.__str__(),
                "suffix": suffix.__str__()
            },
            "user": {
                "name": user_name.__str__()
            }
        }
    })

    return query


class Condition:
    def __init__(self, condition_type, condition_operator, condition_value):
        self.condition_type = condition_type
        self.condition_operator = condition_operator
        self.condition_value = condition_value

import json
from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
from app.models import Data_Shift, MeasurementData, Parameter_Settings, paraTableData


def report(request):
    if request.method == 'POST':
        raw_data = request.POST.get('data')
        if raw_data:
            data = json.loads(raw_data)

            from_date = data.get('from_date')
            part_model = data.get('part_model')
            mode = data.get('mode')
            to_date = data.get('to_date')
            shift = data.get('shift')
            status = data.get('status')

            if not all([from_date, to_date, part_model]):
                return JsonResponse({'error': 'Missing required fields: from_date, to_date, or part_model'}, status=400)

            filter_kwargs = {
                'date__range': (from_date, to_date),
                'part_model': part_model,
            }

            if shift != "ALL":
                filter_kwargs['shift'] = shift

            if status != "ALL":
                filter_kwargs['overall_status'] = status

            filtered_data = MeasurementData.objects.filter(**filter_kwargs).order_by('date')

            # Data dictionary for the table
            data_dict = {
                'Date': [],
                'Job Numbers': [],
                'Shift': [],
                'Operator': [],
                'Status': [],
            }

            # Add parameter data keys dynamically
            parameter_data = paraTableData.objects.filter(
                parameter_settings__part_model=part_model
            ).values('parameter_name', 'usl', 'lsl')

            for param in parameter_data:
                param_name = param['parameter_name']
                usl = param['usl']
                lsl = param['lsl']
                key = f"{param_name} <br>{usl} <br>{lsl}"
                data_dict[key] = []

            unique_dates = set()
            # Group data by Date
            grouped_data = {}
            for record in filtered_data:
                date = record.date.strftime('%d-%m-%Y %I:%M:%S %p')
                unique_dates.add(date)  # Track unique dates
                if date not in grouped_data:
                    grouped_data[date] = {
                        'Job Numbers': set(),
                        'Shift': record.shift,
                        'Operator': record.operator,
                        'Status': record.overall_status,
                        'Parameters': {key: set() for key in data_dict if key not in ['Date', 'Shift', 'Operator', 'Status', 'Job Numbers']}
                    }

                # Collect unique job numbers
                if record.comp_sr_no:
                    grouped_data[date]['Job Numbers'].add(record.comp_sr_no)

                # Add parameter data
                for param in parameter_data:
                    param_name = param['parameter_name']
                    usl = param['usl']
                    lsl = param['lsl']
                    key = f"{param_name} <br>{usl} <br>{lsl}"

                    parameter_values = MeasurementData.objects.filter(
                        comp_sr_no=record.comp_sr_no,
                        date=record.date,
                        parameter_name=param_name
                    )

                    for pv in parameter_values:
                        value_to_display = ""
                        if mode == 'max':
                            value_to_display = pv.max_value
                        elif mode == 'min':
                            value_to_display = pv.min_value
                        elif mode == 'tir':
                            value_to_display = pv.tir_value
                        else:
                            value_to_display = pv.output

                        if pv.overall_status == 'ACCEPT':
                            value_to_display = f'<span style="background-color: #00ff00; padding: 2px;">{value_to_display}</span>'
                        elif pv.overall_status == 'REWORK':
                            value_to_display = f'<span style="background-color: yellow; padding: 2px;">{value_to_display}</span>'
                        elif pv.overall_status == 'REJECT':
                            value_to_display = f'<span style="background-color: red; padding: 2px;">{value_to_display}</span>'

                        grouped_data[date]['Parameters'][key].add(value_to_display)

            # Convert grouped data into a DataFrame
            for date, group in grouped_data.items():
                data_dict['Date'].append(date)

                # Join all job numbers as a single string for display
                job_numbers_combined = "<br>".join(sorted(group['Job Numbers']))
                data_dict['Job Numbers'].append(job_numbers_combined)

                data_dict['Shift'].append(group['Shift'])
                data_dict['Operator'].append(group['Operator'])
                data_dict['Status'].append(group['Status'])

                for key, values in group['Parameters'].items():
                    # Combine unique values and display only once
                    data_dict[key].append("<br>".join(sorted(values)))

            df = pd.DataFrame(data_dict)
            df.index = df.index + 1

            table_html = df.to_html(index=True, escape=False, classes='table table-striped')

            return JsonResponse({
                'table_html': table_html,
                'total_count': len(unique_dates),
            })

   
           
    
    elif request.method == 'GET':
        shift_values = Data_Shift.objects.order_by('id').values_list('shift', 'shift_time').distinct()
        shift_name_queryset = Data_Shift.objects.order_by('id').values_list('shift', flat=True).distinct()
        shift_name = list(shift_name_queryset)
        print ("shift_name",shift_name)

        # Convert the QuerySet to a list of lists
        shift_values_list = list(shift_values)
        
        # Serialize the list to JSON
        shift_values_json = json.dumps(shift_values_list)
        print("shift_values_json",shift_values_json)

         # Create a context dictionary to pass the data to the template
        context = {
            'shift_values': shift_values_json,
            'shift_name':shift_name,
        }
    return render(request,'app/report.html',context)
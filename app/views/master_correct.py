import json
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from app.models import Parameter_Settings,paraTableData,master_data
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


@csrf_exempt
def master(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.POST.get('payload', '[]'))  # Parse the JSON payload
        print('your data from front end:',data)

        # Handle AJAX POST
        part_name = request.POST.get('part_name', '')
        print(f"your received value from front end:: {part_name}")

        # Step 1: Filter `Parameter_Settings` by `part_model`
        # Step 1: Fetch filtered records from Parameter_Settings and order by 'id'
        filtered_data = Parameter_Settings.objects.filter(
            part_model=part_name
        ).order_by('id')  # Ensures the order is by 'id'

        print('Filtered data from Parameter_Settings:', filtered_data)

        # Step 2: Get all `parameter_name` values from `paraTableData` related to `filtered_data`
        parameter_names = paraTableData.objects.filter(
            parameter_settings__in=filtered_data
        ).values_list('parameter_name', flat=True).distinct().order_by('parameter_settings__id')

        print('Parameter names from paraTableData:', list(parameter_names))

        last_stored_parameters = {
            item['parameter_name']: item
            for item in master_data.objects.filter(
                part_model=part_name,
                parameter_name__in = parameter_names.values_list('parameter_name', flat=True)
                  # Ensure it matches the selected_value context
            ).values().order_by('parameter_name')  # Fetch all fields
        }

        # Step 4: Print the required fields (id, e, d, o1) for each parameter_name
        for param_name, values in last_stored_parameters.items():
            id = values.get('id')
            e = values.get('e')
            d = values.get('d')
            o1 = values.get('o1')
            print(f"Parameter: {param_name}, id: {id}, e: {e}, d: {d}, o1: {o1}")


        for item in data:
            try:
                # Validate and parse date_time
                date_time = datetime.strptime(item['date_time'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS.'}, status=400)

            # Save data to MasterData
            master_data.objects.create(
                a=item['a'],
                a1=item['a1'],
                b=item['b'],
                b1=item['b1'],
                e=item['e'],
                d=item['d'],
                o1=item['o1'],
                parameter_name=item['parameter_name'],
                part_model=item['part_model'],
                date_time=date_time,
                mastering=item['mastering'],
                probe_number = item['probeNumber']
            )



        

        # Filter all Parameter_Settings entries matching the part_model
        matching_settings = Parameter_Settings.objects.filter(part_model=part_name)
        parameter_names = []
        low_masters = []
        high_masters = []
        probe_number = []
        nominals = []
        lsls = []
        usls = []
        ltls = []
        utls = []
        stepnumbers = []
        idorod = []

        if matching_settings.exists():
            print(f"Matching Parameter_Settings entries for part_model '{part_name}':")
            for setting in matching_settings:
                print(f"Parameter_Settings ID: {setting.id}, sr_no: {setting.sr_no}, part_name: {setting.part_name}")
                
                # Filter related paraTableData entries for each setting
                related_data = paraTableData.objects.filter(parameter_settings=setting).order_by('id')
                
                
                if related_data.exists():
                    print(f"Related paraTableData entries for Parameter_Settings ID {setting.id}:")
                    for data in related_data:

                        parameter_names.append(data.parameter_name)  # Collect parameter names
                        low_masters.append(data.low_master)
                        high_masters.append(data.high_master)
                        probe_number.append(data.channel_no)
                        nominals.append(data.nominal)
                        lsls.append(data.lsl)
                        usls.append(data.usl)
                        ltls.append(data.ltl)
                        utls.append(data.utl)
                        stepnumbers.append(data.step_no)
                        idorod.append(data.id_od)


                else:
                    print(f"  No paraTableData entries found for Parameter_Settings ID {setting.id}")
        else:
            print(f"No Parameter_Settings entries found for part_model '{part_name}'")


        parameter_values = [
            {
                "parameter_name": param_name,
                "id": values.get("id"),
                "e": values.get("e"),
                "d": values.get("d"),
                "o1": values.get("o1")
            }
            for param_name, values in last_stored_parameters.items()
        ]    

        # Respond with redirect URL for client-side navigation
        return JsonResponse({
            "redirect_url": reverse('master'),
            "parameter_names": parameter_names, 
            "low_masters":low_masters, 
            "high_masters":high_masters,
            "probe_number":probe_number,
            "nominals":nominals,
            "lsls":lsls,
            "usls":usls,
            "ltls":ltls,
            "utls":utls,
            "stepnumbers":stepnumbers,
            "idorod":idorod,
            "parameter_values": parameter_values,  # Add this
        })

    # Render the page with the part_name (default to empty string if not provided)
    part_name = request.GET.get('part_model', '')  # Optional: Use a query param or other logic
    return render(request, 'app/master.html', {'part_name': part_name})
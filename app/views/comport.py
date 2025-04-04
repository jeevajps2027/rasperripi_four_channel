import json
from django.http import JsonResponse
from django.shortcuts import render
from app.models import BackupSettings, Operator_setting, ComportSetting,Data_Shift  # Import your models
import serial.tools.list_ports  # Import list_ports module


def comport(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            print('Your data from comport:', data)


            request_type = data[0].get("request_type") if isinstance(data, list) and len(data) > 0 else data.get("request_type")  # Safely get the request type

            if request_type == 'delete':
                operator_no = data.get("operator_no")
                operator_name = data.get("operator_name")

                if operator_no and operator_name:
                    # Try to find and delete the operator using operator_no
                    try:
                        operator = Operator_setting.objects.get(operator_no=operator_no)
                        operator.delete()
                        return JsonResponse({"status": "success", "message": "Operator deleted successfully"})
                    except Operator_setting.DoesNotExist:
                        return JsonResponse({"status": "error", "message": "Operator not found"})
            
            elif request_type == 'backup_date':
                # Get the backup date from the request data
                backup_date = data.get('backup_data')
                confirm_backup = data.get('confirm_backup')  # Retrieve checkbox value

                
                print("Backup Date Settings:")
                print("backup_date:", backup_date)  # Print the received backup date
                print("Confirm Backup Checkbox:", confirm_backup)  # Print checkbox value


                BackupSettings.objects.create(
                    backup_date=backup_date,
                    confirm_backup=confirm_backup  # Save the checkbox state
                )

                return JsonResponse({'status': 'success'})

            elif request_type == "shift_settings":
                shift = data.get('shift')
                shift_time = data.get('shift_time')

                print("Shift Settings:")
                print("shift:", shift)
                print("shift_time:", shift_time)

                existing_shift = Data_Shift.objects.filter(shift=shift).first()

                if existing_shift:
                    existing_shift.shift_time = shift_time
                    existing_shift.save()
                else:
                    shift_settings_obj = Data_Shift.objects.create(shift=shift, shift_time=shift_time)
                    shift_settings_obj.save()


                return JsonResponse({"status": "success", "message": "Shift settings saved successfully!"})
    

            

            elif request_type == "comport":
                # Handle comport data
                com_port = data.get("com_port")
                baud_rate = data.get("baud_rate")
                parity = data.get("parity")
                stop_bit = data.get("stop_bit")
                data_bit = data.get("data_bit")

                # Validate the extracted values
                if com_port and baud_rate and parity and stop_bit and data_bit:
                    # Save to database using get_or_create
                    setting, created = ComportSetting.objects.get_or_create(
                        id=1,  # Assuming only one record for global settings
                        defaults={
                            "com_port": com_port,
                            "baud_rate": baud_rate,
                            "parity": parity,
                            "stop_bit": stop_bit,
                            "data_bit": data_bit,
                        }
                    )
                    if not created:
                        # Update the existing record
                        setting.com_port = com_port
                        setting.baud_rate = baud_rate
                        setting.parity = parity
                        setting.stop_bit = stop_bit
                        setting.data_bit = data_bit
                        setting.save()

                    return JsonResponse({"status": "success", "message": "Comport data saved successfully"})
                else:
                    return JsonResponse({"status": "error", "message": "Missing comport data"})

            elif request_type == "operator":
                # Handle operator data
                if isinstance(data, list):  # Ensure we received a list of operator data
                    for row in data:
                        operator_no = row.get("operator_no")
                        operator_name = row.get("operator_name")

                        if operator_no and operator_name:
                            # Create or update the operator setting using operator_no as the unique key
                            operator, created = Operator_setting.objects.get_or_create(
                                operator_no=operator_no,
                                defaults={'operator_name': operator_name}
                            )
                            if not created:
                                # If the record exists, update the operator_name
                                operator.operator_name = operator_name
                                operator.save()

                            print(f"Operator No: {operator_no}, Operator Name: {operator_name}")
                        else:
                            return JsonResponse({"status": "error", "message": "Missing operator_no or operator_name"})
                    
                    return JsonResponse({"status": "success", "message": "Operator data saved successfully"})
                else:
                    return JsonResponse({"status": "error", "message": "Invalid operator data format"})

            else:
                return JsonResponse({"status": "error", "message": "Unknown request type"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
        
    elif request.method == "GET":
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        
        # Print the serial ports to the terminal
        print("Available Serial Ports:")
        for port in port_list:
            print(port)


        operators_value = Operator_setting.objects.all().order_by('id')
        comport_data = ComportSetting.objects.all()
        shift_settings = Data_Shift.objects.all().order_by('id')
        backup_date = BackupSettings.objects.order_by('-id').first()
        print('your data from shift_settings is this:',shift_settings)
        print('your comport data is thiss::',comport_data)
        context = {
            "operators_value": operators_value,
            "port_list": port_list,
            'shift_settings': shift_settings,
             'backup_date': backup_date,
        }
    
        return render(request, "app/comport.html", context)



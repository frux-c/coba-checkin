import pandas as pd
import datetime
from django.template import Template, Context

def calculate_delta(row):
    if pd.notna(row['auto_time_in']) and pd.notna(row['auto_time_out']):
        checkin_dt = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.strptime(row['auto_time_in'], "%H:%M:%S.%f").time())
        checkout_dt = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.strptime(row['auto_time_out'], "%H:%M:%S.%f").time())
        return (checkout_dt - checkin_dt).seconds / 3600  # Convert to hours
    return 0.0

def create_report_in_time_window(*args, **kwargs):
    # from .pdfc import PDF, construct
    from .serializers import CheckInSerializer
    from .models import CheckIn
    import pandas as pd

    """
    create a report of all students who have checked in between the start and end time
    :param start_time: start time of the time window
    :param end_time: end time of the time window
    """
    start_time = kwargs.get("start_time")
    end_time = kwargs.get("end_time")
    employees = kwargs.get("employees")
    # filter out students in date range
    if employees:
        employees = CheckIn.objects.filter(
            creation_date__range=[start_time, end_time], is_on_clock=False, timed_out=False, employee__in=employees
        )
    else:
        employees = CheckIn.objects.filter(
            creation_date__range=[start_time, end_time], is_on_clock=False, timed_out=False
        )
    # get the serialized data
    serealized_employees = CheckInSerializer(employees, many=True).data
    df = pd.DataFrame(serealized_employees)
    df['checkin_delta'] = df.apply(calculate_delta, axis=1)
    # remove rows that have checkin_delta > 8 hours and < 30 minutes
    df = df[(df['checkin_delta'] > 0.5) & (df['checkin_delta'] < 8)]
    # group the df by field 'creation_date'
    grouped_records = df.groupby('creation_date').apply(lambda x: x.to_dict(orient='records')).to_dict()
        
    # create the plots in a local folder to later on be applied on pdf page

    # populated_folder = construct(serealized_employees)
    # pdf = PDF(start_time, end_time)
    # for elem in populated_folder:
    #     pdf.print_page(elem)
    
    # return pdf
    return grouped_records

def create_report_in_time_window_for_reports(report_obj, start_time, end_time, employees):
    from io import BytesIO
    result = create_report_in_time_window(start_time=start_time, end_time=end_time, employees=employees)
    with open(f"coba/templates/checkin_report_template.html", "r") as f:
        template = Template(f.read())
        context = Context({'data': result})
        rendered_template = template.render(context)
        result_content = BytesIO(rendered_template.encode())
        report_obj.file.save(name="report.html", content=result_content, save=True)
        report_obj.save()
        result_content.close()
    return True
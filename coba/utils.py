def create_report_in_time_window(*args, **kwargs):
    try:
        from pdf import PDF, construct
    except ModuleNotFoundError:
        from .pdf import PDF, construct
    from .serializers import CheckInSerializer
    from .models import CheckIn
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
    # create the plots in a local folder to later on be applied on pdf page
    populated_folder = construct(serealized_employees)
    pdf = PDF(start_time, end_time)
    for elem in populated_folder:
        pdf.print_page(elem)
    return pdf

def create_report_in_time_window_for_reports(report_obj, start_time, end_time, employees):
    from io import BytesIO
    result = create_report_in_time_window(start_time=start_time, end_time=end_time, employees=employees).result()
    result_content = BytesIO(result.output(dest='S'))
    report_obj.file.save(name="WeeklyReport.pdf", content=result_content, save=True)
    report_obj.save()
    return True
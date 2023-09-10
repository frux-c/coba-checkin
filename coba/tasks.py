import os
import threading
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMessage

from .models import CheckIn

try:
    from pdf import PDF, construct
except ModuleNotFoundError:
    from .pdf import PDF, construct

def time_out_signed():
    """
    sign out anyone after 6:40pm, from the checkin database/model
    """
    default_time_out = datetime.now()
    timed_out_students = CheckIn.objects.filter(is_on_clock=True)
    names = list()
    for student in timed_out_students:
        student.auto_time_out = default_time_out
        student.is_on_clock = False
        student.timed_out = True
        student.save()
        names.append(str(student))
    return str(list())


# def notify_timed_out(students: list) -> None:
#     subject = "Auto Signed Out"
#     message = """Hi {},
# 	This is a message to notify you that you have been automatically signed out of COBA check-in system.
# 	"""
#     messages = tuple(
#         (
#             subject,
#             message.format(student.first_name),
#             settings.EMAIL_HOST_USER,
#             [student.email],
#         )
#         for student in students
#     )
#     send_mass_mail(messages, fail_silently=False)


def weekly_report():
    # dateback 6 days since this function call
    enddate = datetime.today()
    startdate = enddate - timedelta(days=4)

    # filter out students in date range of 6 days from now
    students = CheckIn.objects.filter(
        date_created__range=[startdate, enddate], is_on_clock=False, timed_out=False
    )

    # serialize query "Look in models.py for more serialize detail"
    serealized_students = []
    for student in students:
        serealized_students.append(student.serialize())

    # create the plots in a local folder to later on be applied on pdf page
    populated_folder = construct(serealized_students)

    pdf = PDF(startdate.date(), enddate.date())

    for elem in populated_folder:
        pdf.print_page(elem)

    pdf.output(f"Report.pdf", "F")
    # list of email recepients
    recepients = os.environ.get("WEEKLY_REPORT_EMAIL_RECEPIENTS").split(",")
    mail = EmailMessage(
        "Weekly Report",  # 	Subject
        f"This report covers days between {startdate.date()} and {enddate.date()}",  # 	Message
        settings.EMAIL_HOST_USER,  # From
        recepients,  # To
    )
    mail.attach_file(f"Weekly_Report.pdf")
    mail.send()


def run_weekly_report():
    mail_thread = threading.Thread(target=weekly_report, daemon=True)
    mail_thread.start()
    return 200

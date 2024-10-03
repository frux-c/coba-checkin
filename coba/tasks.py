import os
import threading
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from channels.layers import get_channel_layer  # channel websocket import
from asgiref.sync import async_to_sync  # channel websocket import

from .models import CheckIn
from .consumers import CheckInConsumer

from .utils import create_report_in_time_window

def test_task(*args, **kwargs):
    print("Hello World!")
    return "test complete"

def time_out_signed(*args, **kwargs):
    """
    sign out anyone after 6:10pm, from the checkin database
    """
    default_time_out = datetime.now()
    timed_out_students = CheckIn.objects.filter(is_on_clock=True)
    channel_layer = get_channel_layer()
    names = list()
    for student in timed_out_students:
        student.auto_time_out = default_time_out
        student.is_on_clock = False
        student.timed_out = True
        student.save()
        # send message to websocket
        async_to_sync(channel_layer.group_send)(
            "events",
            {
                "type": "send_group_message",
                "message": f"{student.first_name} {student.last_name} has been signed out automatically",
                "type": "auto_time_out",
            },
        )
        names.append(str(student))
    channel = get_channel_layer()
    async_to_sync(channel.group_send)(
        CheckInConsumer.GROUP_NAME,
            {
                "type": "send_group_message",
                "message": [],
                "event": "websocket.update_employees",
            },
    )
    return str(list())

def weekly_report():
    # path to pdf file
    pdf_file_path = os.path.join(settings.BASE_DIR, "WeeklyReport.pdf")

    # dateback 6 days since this function call
    end_date = datetime.today()
    start_date = end_date - timedelta(days=4)

    # create the report
    pdf = create_report_in_time_window(start_time=start_date, end_time=end_date)
    pdf.output(pdf_file_path)
    
    # print the file 
    # os.system(f"lp -d {settings.LP_PRINTER_DESTINATION} {pdf_file_path}")

    # list of email recepients
    recepients = os.environ.get("WEEKLY_REPORT_EMAIL_RECEPIENTS").split(",")

    # send email
    mail = EmailMessage(
        "Weekly Report",  # 	Subject
        f"This report covers days between {start_date.date()} and {end_date.date()}",  # 	Message
        settings.EMAIL_HOST_USER,  # From
        recepients,  # To
    )
    mail.attach_file(pdf_file_path)
    mail.send()

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

def run_weekly_report():
    mail_thread = threading.Thread(target=weekly_report, daemon=True)
    mail_thread.start()
    return 0

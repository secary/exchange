import subprocess
import smtplib
from email.mime.text import MIMEText


def send_notification(title, message):
    """
    使用 BurntToast 发送 Windows 通知，显式加载模块路径
    """
    powershell_path = r"/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    burnttoast_path = r"C:\Users\secar\Documents\PowerShell\Modules\BurntToast"

    try:
        command = f'Import-Module "{burnttoast_path}"; New-BurntToastNotification -Text "{title}", "{message}"'
        subprocess.run([
            powershell_path,
            "-NoProfile",  # 跳过加载配置文件
            "-Command",
            command
        ], check=True)
        print("BurntToast 通知发送成功")
    except Exception as e:
        print(f"BurntToast 通知发送失败: {e}")




def send_email(subject, body, sender, password, receiver, smtp_server, smtp_port=465):
    """
    发送邮件提醒
    """
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"发送邮件失败: {e}")

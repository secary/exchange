import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

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


logging.basicConfig(filename="log/error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def send_email(subject, body, sender, password, receiver, smtp_server, smtp_port=587):
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # 连接 SMTP 服务器并发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo("example.com")  # 第一次发送 EHLO
            server.starttls()  # 启用 TLS
            server.login(sender, password)  # 登录 SMTP 服务器
            server.sendmail(sender, receiver, msg.as_string())  # 发送邮件

        print("邮件发送成功！")
    except smtplib.SMTPAuthenticationError as auth_error:
        logging.error(f"SMTP 认证失败: {auth_error}")
        print("SMTP 认证失败，请检查用户名或密码是否正确。")
    except smtplib.SMTPConnectError as conn_error:
        logging.error(f"SMTP 连接失败: {conn_error}")
        print("SMTP 连接失败，请检查网络连接或服务器地址。")
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        print(f"邮件发送失败: {e}")

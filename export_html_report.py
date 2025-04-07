import configparser
import smtplib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dominate.tags import *

import database.export_data as data_info

config = configparser.ConfigParser()
config.read('config.ini')
from_addr = config.get('email', 'addr')
pwd = config.get('email', 'pwd')
server = config.get('email', 'server')
port = config.getint('email', 'port')

style_applied = '''
    body{
        font-family: verdana,arial,sans-serif;
        font-size:11px;
    }
    table.gridtable {
        color: #333333;
        border-width: 1px;
        border-color: #666666;
        border-collapse: collapse;
        font-size:11px;
    }
    table.gridtable th {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #666666;
        background-color: #DDEBF7;
    }
    table.gridtable td {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #666666;
        background-color: #ffffff;
        text-align:center;
    }
    table.gridtable td.failed {
        font-weight:bold;
        color:#ED5F5F;
    }
    table.gridtable td.passrate {
        font-weight:bold;
        color:green;
    }
    li {
        margin-top:5px;
    }
    div{
        margin-top:10px;
        }
    '''


def convert_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f'{int(hours)}时{int(minutes)}分{int(remaining_seconds)}秒'


def set_Hello(studnet, classtime):
    hello_str = "这是你在 " + classtime + " 开始的课程的表现报告 "
    hello_div = div(id='hello')
    hello_div.add(p(f'{studnet}同学,'))
    hello_div.add(p(hello_str))


def set_table_head():
    with tr():
        th(style='background-color:white')
        th("次数")
        th("时间")
        th("课堂时间占比")


def fill_table_data(action_type, action_count, time_count, class_time_rate):
    data_tr = tr()
    data_tr += td(action_type)
    data_tr += td(action_count)
    data_tr += td(time_count)
    if float(class_time_rate) >= 0.1:
        cls = 'failed'
    else:
        cls = 'passrate'
    data_tr += td(class_time_rate, cls=cls)


def generate_result_table(actions, duration):
    result_div = div(id='test case result')
    with result_div.add(table(cls='gridtable')).add(tbody()):
        set_table_head()
        fill_table_data('睡觉',
                        actions['sleep']['action_count'],
                        convert_seconds(actions['sleep']['time_count'] / 1000),
                        f'{actions['sleep']['time_count'] / duration:.2f}')
        fill_table_data('玩手机',
                        actions['phone']['action_count'],
                        convert_seconds(actions['phone']['time_count'] / 1000),
                        f'{actions['phone']['time_count'] / duration:.2f}')
        fill_table_data('交头接耳',
                        actions['talk']['action_count'],
                        convert_seconds(actions['talk']['time_count'] / 1000),
                        f'{actions['talk']['time_count'] / duration:.2f}')


def generate_build_cause(cause):
    br()
    div(b(font('统计', color='#0B610B')))
    div(hr(size=2, alignment='center', width='100%'))
    div((b(font('情况:' + cause))))


def generate_list_link(category, href_link):
    with li(category + ':'):
        a(href_link, href=href_link)


def generate_build_info(build_type, build_url):
    build_type_div = div()
    build_type_fond = b()
    build_type_fond += font(build_type + ' Test Build')
    build_type_div += build_type_fond
    with ul():
        generate_list_link('Build', build_url)
        generate_list_link('Cucumber Report', build_url + '/cucumber-html-reports/overview-features.html')
        generate_list_link('Log Files', build_url + '/artifact/target/rest-logs/')


def generate_ending():
    br()
    p('** 这是由智慧教室系统生成的课堂表现报告 **')
    p('如有疑问请联系教务处邮箱xxxx@xxx.com')


def insert_image():
    div(b(font('时间甘特图', color='#0B610B')))
    div(hr(size=2, alignment='center', width='100%'))
    img(src='cid:time_plot')


def generate_html_report(class_id, date):
    studnets = data_info.get_students()
    class_info = data_info.get_class(class_id, date)
    print(class_info)
    class_id, duration, date = class_info
    date = date.strftime("%Y年%m月%d日 %H时%M分")
    for student in studnets[:-1]:
        student_id, name, email = student
        actions = data_info.get_actions(student_id, class_id)
        statistics = actions.statistics
        html_root = html()
        # html head
        with html_root.add(head()):
            style(style_applied, type='text/css')
        # html body
        with html_root.add(body()):
            set_Hello(name, date)
            generate_build_cause(
                f'在该课程长达{convert_seconds(duration / 1000)}的时间中,检测到你的课堂异常行为如下')
            generate_result_table(statistics, duration)
            # generate_build_info('Smoke', 'smoke build url')
            # generate_build_info('Regression', 'regression build url')
            data_info.save_action_plot(actions, duration)
            insert_image()
            generate_ending()
        # save as html file
        send_email(email, html_root.render())
        with open('email_report.html', 'w') as f:
            f.write(html_root.render())


def send_email(to_addrs, render):
    msg = MIMEMultipart()

    msg['Subject'] = Header('课堂表现报告', 'utf-8').encode()

    msg['From'] = f'{from_addr} <{from_addr}>'

    msg['To'] = to_addrs

    content = render
    msg.attach(MIMEText(content, 'html', 'utf-8'))

    image = MIMEImage(open('tmp_plot.png', 'rb').read())
    image.add_header('Content-ID', '<time_plot>')
    msg.attach(image)
    print(server, port)
    smtp = smtplib.SMTP_SSL(server, port)
    # smtp.ehlo()
    # smtp.starttls()
    smtp.login(from_addr, pwd)
    smtp.sendmail(from_addr, to_addrs, msg.as_string())
    smtp.quit()


def run():
    generate_html_report('./test_video2.mp4', '2024-08-03 14:12:11')


if __name__ == '__main__':
    run()

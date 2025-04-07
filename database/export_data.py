from database.db_manager import DBManager
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

zh_font = fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')
db = DBManager()


def convert_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return hours, minutes, remaining_seconds


class Action_Machine:
    def __init__(self):
        self.states = ['learing', 'action']
        self.state = 'learing'
        self.start_time = 0
        self.end_time = 0
        self.action = None

        self.res = []
        self.statistics = {}

        self.duration = 500

    def behavioral_statistics(self):
        action_types = ['phone', 'sleep', 'talk']
        statistics = {}
        for action_type in action_types:
            statistics[action_type] = {
                'action_count': 0,
                'time_count': 0
            }
        for action in self.res:
            action_type, start_time, end_time = action
            statistics[action_type]['action_count'] += 1
            statistics[action_type]['time_count'] += end_time - start_time
        self.statistics = statistics

    def run(self, action):
        if self.state == 'learing':
            self.state = 'action'
            self.action = action[0]
            self.start_time = action[1]
            self.end_time = self.start_time + self.duration
        elif self.state == 'action':
            if self.action != action[0]:
                self.res.append([self.action, self.start_time, self.end_time].copy())
                self.action = action[0]
                self.start_time = action[1]
                self.end_time = self.start_time + self.duration
                return
            if action[1] - self.end_time < self.duration:
                self.end_time = action[1]
            else:
                self.res.append([self.action, self.start_time, self.end_time].copy())
                self.state = 'learing'


def save_action_plot(actions, duration):
    actions = actions.res
    action_labels = [action[0] for action in actions]
    start_times = [(action[1] / 1000) for action in actions]
    end_times = [action[2] / 1000 for action in actions]
    durations = [(action[2] - action[1]) / 1000 for action in actions]
    plt.figure(figsize=(10, 6))
    bars = plt.barh(action_labels, durations, left=start_times, color='skyblue')
    # for bar, start_time, end_time in zip(bars, start_times, end_times):
    #     plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
    #              f'{start_time}s 至 {end_time}s',
    #              ha='center', va='center', color='black', fontproperties=zh_font)
    plt.title(f'课堂表现甘特图', fontproperties=zh_font)
    plt.xlabel('时间', fontproperties=zh_font)
    plt.ylabel('行为', fontproperties=zh_font)
    plt.xlim([0, duration / 1000])
    plt.grid(axis='x')
    plt.savefig('tmp_plot.png')


def get_class(class_id, date):
    class_info = db.get_class_info(class_id, date)
    return class_info


def get_students():
    students = db.get_students()
    return students


def get_actions(student, class_id):
    action_machine = Action_Machine()
    actions = db.get_actions(student, class_id)
    actions.sort(key=lambda x: x[1])

    for action in actions:
        action_machine.run(action)
    action_machine.behavioral_statistics()
    return action_machine

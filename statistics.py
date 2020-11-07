import ping


def print_stat(stat):
    res = f'Ping statistics:\n ' \
          f'{stat.results["success"] + stat.results["failed"]} ' \
          f'times sent\n{stat.results["success"]} successful ' \
          f'{stat.results["failed"]} failed\n'
    if stat.avg_time != 0:
        res += f'Time statistics:\n' \
               f'Min = {stat.min_time}ms, Max = ' \
               f'{stat.max_time}ms, Avg = {stat.avg_time}ms'
    print(res)


class Stat:
    def __init__(self):
        self.time = []
        self.results = {'success': 0, 'failed': 0}
        self.min_time = 0
        self.max_time = 0
        self.avg_time = 0

    def get(self):
        if self.time:
            self.min_time = min(self.time)
            self.max_time = max(self.time)
            self.avg_time = sum(self.time) / len(self.time)

    def add(self, reasone, time, dst_host, dst_port):
        if time != 0:
            time = round(time, 3)
            self.time.append(time)
        if reasone is ping.Answer.port_open:
            self.results['success'] += 1
        else:
            self.results['failed'] += 1

        res = f'Ping {dst_host}:{dst_port} ' \
              f'- {reasone} - time={time}ms'
        print(res)

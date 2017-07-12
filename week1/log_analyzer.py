#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import gzip
import re
import json
from datetime import datetime

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

nginx_log_pattern = re.compile(r'^.+?\"\S+\s(\S+).+\s(\d+\.\d+)$')
filename_pattern = re.compile(r'nginx-access-ui\.log-(\d+)')


def find_latest_file():
    files = glob.glob(
        '{dir}/nginx-access-*.log-*'.format(dir=config['LOG_DIR'])
    )
    return max(files) if files else None


def get_log_contents(filename):
    if filename.endswith('.gz'):
        log_file = gzip.open(filename, 'r')
    else:
        log_file = open(filename, 'r')
    with log_file:
        for line in log_file:
            url, time = nginx_log_pattern.findall(line)[0]
            yield url, float(time)


def publish_report(report_suffix, table):
    with open(
            '{dir}/report.html'.format(dir=config['REPORT_DIR']),
            'r'
    ) as template_file:
        template = template_file.read()

    rendered = template.replace('$table_json', json.dumps(table))
    with open(
            '{dir}/report-{dt}.html'.format(
                dir=config['REPORT_DIR'],
                dt=report_suffix
            ),
            'w'
    ) as report_file:
        report_file.write(rendered)


def main():
    filename = find_latest_file()
    if not filename:
        print 'No logs found.'
        exit(1)

    url_stats_map = {}
    total_time = 0.0
    total_count = 0
    contents = get_log_contents(filename)
    for url, time in contents:
        url_stats = url_stats_map.setdefault(url, {
            'time': 0.0,
            'count': 0.0
        })
        url_stats['time'] += time
        url_stats['count'] += 1
        total_time += time
        total_count += 1
    print 'Reading file finished.'
    table = []
    for url, url_stats in url_stats_map.iteritems():
        table.append({
            'url': url,
            'count': url_stats['count'],
            'time_sum': url_stats['time'],
            'time_avg': url_stats['time'] / url_stats['count'],
            'time_med': 0,
            'time_perc': 0,
            'count_perc': 0
        })
        # TODO: add time_med, time_perc, count_perc
    print 'Table filled.'
    table.sort(key=lambda x: x['time_avg'], reverse=True)
    table = table[:config['REPORT_SIZE']]
    print 'Sorted and cropped.'

    report_suffix = filename_pattern.findall(filename)[0]
    publish_report(report_suffix, table)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    This file is part of speedtest-reporter.

    Speedtest-reporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Speedtest-reporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with speedtest-reporter. If not, see <http://www.gnu.org/licenses/>
'''


import ConfigParser
import datetime
from speedtest_cli import *
import json
import logging
import pygal
from pygal.style import DarkSolarizedStyle
import time

__license__ = "GPL-V3"

__all__ = ['report', 'speedtest']

class SpeedTestReporter(object):
    def __init__(self, config_file='speedtest_reporter.cfg'):

        ## config file (INI)
        self.config_file = config_file

        try:
            cfg = open(self.config_file, 'r')
        except IOError:
            logging.critical('Config file not found %s' % self.config_file)
            exit(1)

        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
 
        # chart
        self.chart_bandwidth = self.config.get('chart', 'bandwidth')
        self.chart_ping = self.config.get('chart', 'ping')

        ## log file
        logging.basicConfig(level=self.config.get('log', 'level'),
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    #format='%(asctime)-8s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=self.config.get('log', 'log_file'),
                    filemode='a+'
        )]
 

        ## saved data file (JSON)
        try:
            self.data_file = self.config.get('JSON', 'data_file')
            self.json_encoding = self.config.get('JSON', 'encoding')
            self.json_indent = self.config.get('JSON', 'indent')
            
            
            try:
                with open(self.data_file, "r") as data_file:
                    self.saved_data = json.load(data_file)
            except Exception, err:
                print err
                self.saved_data = []
        except:
            logging.info('no json data file in cfg file')

        # speedtest elements (st = speedtest)
        self.st_config = getConfig()
        self.st_servers = closestServers(self.st_config['client'])
        self.st_best_server = getBestServer(self.st_servers)
    
    def calculate_avg_speed(self, dataset):
        '''
        calculate avg speed

        dataset structure is a dic
        {
            "first": {
                "ulspeed": 91986.95638790992, 
                "ping": 120, 
                "dlspeed": 862759.2691430907, 
                "img": "3016554088"
            }
        }, 
        {
            "second": {
                "ulspeed": 93407.6172199004, 
                "ping": 122, 
                "img": "3016561560", 
                "dlspeed": 733504.8944757946
            }
        }
            the self.saved_data can be used

        '''

        nbdata = 0
        dlsum = 0
        ulsum = 0
        pingsum = 0

        for data in dataset:
            nbdata += 1.
            sample = data.keys()[0]
            dlsum += data[sample]['dlspeed']
            ulsum += data[sample]['ulspeed']
            pingsum += data[sample]['ping']

        avg = {'dlspeed': dlsum / nbdata,
               'ulspeed': ulsum / nbdata,
               'ping': pingsum / nbdata 
        }

        return avg



    def create_chart(self, klass, filename, title, data, x_labels,
                     x_label_rotation=30, 
                     interpolate='cubic',
                     interpolation_precision=10,
                     style=DarkSolarizedStyle,
                     **kwargs):
        '''create chart using pygal

        Args
            filename : filename (full path) of the desired chart
            title : chart title
            data : grap data (eg: {'prod1':[1,2,3], 'prod2':[2,4,6]})
            x_labels : abcysse labels (eg:['jan','feb', 'mar'])
        Returns
            True in case of success / False if fails
        '''

        chart = klass(x_label_rotation=30, 
                           interpolate='cubic',
                           interpolation_precision=10,
                           style=DarkSolarizedStyle
        )
        chart.title = title
        chart.x_labels = x_labels
        for key in data.keys():
            chart.add(key, data[key])
        chart.render_to_file(filename)

        
    def create_img(self, dlspeed, ulspeed, ping):

        dlspeedk = int(round((dlspeed / 1000) * 8, 0))
        ulspeedk = int(round((ulspeed / 1000) * 8, 0))

        apiData = [
            'download=%s' % dlspeedk,
            'ping=%s' % ping,
            'upload=%s' % ulspeedk,
            'promo=',
            'startmode=%s' % 'pingselect',
            'recommendedserverid=%s' % self.st_best_server['id'],
            'accuracy=%s' % 1,
            'serverid=%s' % self.st_best_server['id'],
            'hash=%s' % md5(('%s-%s-%s-%s' %
                             (ping, ulspeedk, dlspeedk, '297aae72'))
                            .encode()).hexdigest()]
        print
        print apiData
        print
        req = Request('http://www.speedtest.net/api/api.php',
                      data='&'.join(apiData).encode())
        req.add_header('Referer', 'http://c.speedtest.net/flash/speedtest.swf')
        f = urlopen(req)
        response = f.read()
        code = f.code
        f.close()

        if int(code) != 200:
            print_('Could not submit results to speedtest.net')
            sys.exit(1)

        qsargs = parse_qs(response.decode())
        resultid = qsargs.get('resultid')
        print resultid
        if not resultid or len(resultid) != 1:
            print_('Could not submit results to speedtest.net')
            sys.exit(1)

        print_('Share results: http://www.speedtest.net/result/%s.png' %
               resultid[0])

        return resultid[0]
    
    def draw_charts(self):
        '''draw speedtest_charts using pygal'''
        
        # chart creation
        x_labels = []
        download = []
        upload = []
        ping = []
        
        for data in self.saved_data:
            date = data.keys()[0]
            x_labels.append(date)
            download.append(round(data[date]['dlspeed'] / 1000 / 1000 * 8, 2))
            upload.append(round(data[date]['ulspeed'] / 1000 / 1000 * 8, 2))
            ping.append(data[date]['ping'])

        # upload / download chart
        data = {'download': download,
                'upload': upload
        }
        self.create_chart(pygal.Line,
                          self.chart_bandwidth, 
                          'upload/download (mbit/s)',
                          data, 
                          x_labels
        )
        
        # ping chart
        data = {'ping': ping} 
        self.create_chart(pygal.Bar,
                          self.chart_ping, 
                          'ping (ms)', 
                          data, 
                          x_labels
        )



    def save_data(self):
        '''enregistre les data au json format'''
        '''
        print self.data 
        with open(self.data_file, "w") as f:
            f.close()
        try:
            with open(self.data_file, "w") as data_file:
                json.dump(self.data, data_file, indent=4)
                logging.info(_('bot data recorded in %s' % self.data_file)) 
        '''
        try:
            with open(self.data_file, "w") as data_file:
                #json.dump(self.saved_data, data_file, indent=self.json_indent)
                json.dump(self.saved_data, data_file, indent=4)
            logging.info('bot data recorded in %s' % self.data_file)
            data_file.close()
        except:
            logging.critical('unable to save json data in %s' % self.data_file)


    def share(self):
        '''
        export charts and ref to the speedtest's img to a distant server
        to share results with others

        note for the speedtest's img, only a PHP file with the img number is copied,
        a template on the distant server call the img via url like:
        http://www.speedtest.net/result/3016617196.png
        
        '''

    def speedtest(self):
        now = time.strftime('%d/%m/%Y %H:%M')
        
        dlspeed = self.st_download()
        ulspeed = self.st_upload()
        ping = self.st_ping()

        img = self.create_img(dlspeed, ulspeed, ping)

        
        result = {now: {'dlspeed': dlspeed,
                 'ulspeed': ulspeed,
                 'ping': ping,
                 'img': img}
        }

        return result

    def st_download(self):
        '''test download speed

        Returns
            download speed in mbit/s
        '''

        sizes = [350, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
        urls = []
        for size in sizes:
            for i in range(0, 4):
                urls.append('%s/random%sx%s.jpg' %
                        (os.path.dirname(self.st_best_server['url']), size, size))
        dlspeed = downloadSpeed(urls, quiet=True)
        #download = round(dlspeed / 1000 / 1000 * 8, 2)
        return dlspeed

    def st_ping(self):
        '''test ping 

        Returns
            ping in ms
        '''

        ping = int(round(self.st_best_server['latency'], 0))
        return ping

    def st_upload(self):
        '''test upload speed

        Returns
            upload speed in mbit/s
        '''

        sizesizes = [int(.25 * 1000 * 1000), int(.5 * 1000 * 1000)]
        sizes = []
        for size in sizesizes:
            for i in range(0, 25):
                sizes.append(size)

        ulspeed = uploadSpeed(self.st_best_server['url'], sizes, quiet=True)
        #upload = round(ulspeed / 1000 / 1000 * 8, 2)
        return ulspeed
        

    def report(self):
        
        self.saved_data.append(self.speedtest())
        self.save_data()

        self.draw_charts()

        avg = self.calculate_avg_speed(self.saved_data)
        avg_id_png = self.create_img(avg['dlspeed'],
                                     avg['ulspeed'],
                                     avg['ping']
        )
        
def mbits(bits, unit=False):
    '''
    convert bits in Mbits

    Args:
        bits: bits amount (integer)
        unit: flag to append or not Mbit/s after the converted result (boolean)
    
    Return:
        string reprensentig nb Mbits
        eg 10.5 Mbits (if unit)
    '''

    if unit:
        return '%0.2f Mbit/s' % ((bits / 1000 / 1000) * 8)
    else:
        return '%0.2f' % ((bits / 1000 / 1000) * 8)

def slownesstest(server=None):
    config = getConfig()

    if server != None:
        servers = closestServers(config['client'], True)
        try:
            best = getBestServer(filter(lambda x: x['id'] == args.server,
                                        servers))
        except IndexError:
            print_('Invalid server ID')
            sys.exit(1)

    else:
        servers = closestServers(config['client'])
        best = getBestServer(servers)
    
    #print_('Hosted by %(sponsor)s (%(name)s) [%(d)0.2f km]: '
    #           '%(latency)s ms' % best)
    #print "best", best!D!%

    sizes = [350, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
    urls = []
    for size in sizes:
        for i in range(0, 4):
            urls.append('%s/random%sx%s.jpg' %
                        (os.path.dirname(best['url']), size, size))
    dlspeed = downloadSpeed(urls, True)
    print_('Download: %0.2f Mbit/s' % ((dlspeed / 1000 / 1000) * 8))

    ##
    sizesizes = [int(.25 * 1000 * 1000), int(.5 * 1000 * 1000)]
    sizes = []
    for size in sizesizes:
        for i in range(0, 25):
            sizes.append(size)

    ulspeed = uploadSpeed(best['url'], sizes, quiet=True)
    print_('Upload: %0.2f Mbit/s' % ((ulspeed / 1000 / 1000) * 8))
    print 'dlspeed', dlspeed, type(dlspeed)
    print 'ulspeed', ulspeed, type(ulspeed)

    dlspeedk = int(round((dlspeed / 1000) * 8, 0))
    ping = int(round(best['latency'], 0))
    ulspeedk = int(round((ulspeed / 1000) * 8, 0))
    
    ##
    print 'dl', mbits(dlspeedk, True)
    print 'ping', ping
    print 'ul', mbits(ulspeedk, True)

def main():
    try:
        agent = SpeedTestReporter(config_file = 'speedtest_reporter.cfg')
        agent.report()
        exit(0)
    except KeyboardInterrupt:
        print_('\nCancelling...')

if __name__ == '__main__':
    main()


    


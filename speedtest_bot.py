#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from speedtest_cli import *
import json
import logging
import pygal

__license__ = "GPL-V3"


data_file = "speedtest_data.json"
json_indent = 4

#with open(data_file, 'w') as f:
#    json.dump(playlist, f, indent=json_indent)

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
 
        # graph
        self.graph_bandwidth = self.config.get('graph', 'bandwidth')
        self.graph_ping = self.config.get('graph', 'ping')

        ## log file
        logging.basicConfig(level=self.config.get('log', 'level'),
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    #format='%(asctime)-8s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=self.config.get('log', 'log_file'),
                    filemode='a+'
        )
 

        ## saved data file (JSON)
        try:
            self.data_file = self.config.get('JSON', 'data_file')
            self.json_encoding = self.config.get('JSON', 'encoding') 
            
            
            try:
                with open(self.data_file, "r") as data_file:
                    self.saved_data = json.load(data_file)
            except Exception, err:
                print err
                self.saved_data = {'ping':[],
                        'download':[],
                        'upload':[],
                        'datetime':[]
                }
        except:
            logging.info('no json data file in cfg file')

        # speedtest elements (st = speedtest)
        self.st_config = getConfig()
        print ''
        print self.st_config['client']
        print ''
        self.st_servers = closestServers(self.st_config['client'])
        print self.st_servers
        self.st_best_server = getBestServer(self.st_servers)
        print self.st_best_server

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
        with open(self.data_file, "w") as f:
            f.close()
        try:
            with open(self.data_file, "w") as data_file:
                json.dump(self.saved_data, data_file, indent=4)
                logging.info(_('bot data recorded in %s' % self.data_file)) 
            return True
        except:
            logging.critical(_('unable to save json data in %s' % self.data_file))

    def speedtest(self):
        result={'download': self.st_download(),
                'upload': self.st_upload(),
                'ping': self.st_ping()
        }

        return result

    def st_download(self):
        sizes = [350, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
        urls = []
        for size in sizes:
            for i in range(0, 4):
                urls.append('%s/random%sx%s.jpg' %
                        (os.path.dirname(self.st_best_server['url']), size, size))
        dlspeed = downloadSpeed(urls, quiet=True)
        print_('download: %0.2f mbit/s' % ((dlspeed / 1000 / 1000) * 8))
        return dlspeed

    def st_ping(self):
        ping = int(round(self.st_best_server['latency'], 0))
        return ping

    def st_upload(self):
        sizesizes = [int(.25 * 1000 * 1000), int(.5 * 1000 * 1000)]
        sizes = []
        for size in sizesizes:
            for i in range(0, 25):
                sizes.append(size)

        ulspeed = uploadSpeed(self.st_best_server['url'], sizes, quiet=True)
        print_('Upload: %0.2f Mbit/s' % ((ulspeed / 1000 / 1000) * 8))
        return ulspeed
        
    

    def report(self):
        speedtest = self.speedtest()
                                                                                                                                                                                            
        self.saved_data['ping'].append(speedtest['ping'])
        self.saved_data['download'].append(speedtest['download'])
        self.saved_data['upload'].append(speedtest['upload'])

        print self.saved_data
        self.save_data()





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
        slownesstest()
    except KeyboardInterrupt:
        print_('\nCancelling...')

if __name__ == '__main__':
    agent = SpeedTestReporter(config_file = 'speedtest_reporter.cfg')
    agent.report()
    #friends = ia.twittapi.GetFriends()

    #agent.exit()
    exit(0)


    


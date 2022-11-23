import datetime
import psutil

from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.views.generic import (View)


class ShowHost(View):
    """ Display dashboard like page showing an overview of host data """
    template_name = 'handyhelpers/host/bs5/detail_host.html'

    def get(self, request, *args, **kwargs):
        now = datetime.datetime.now()
        context = dict()
        context['title'] = 'Host Dashboard'
        context['subtitle'] = psutil.os.uname()[1]
        context['cpu_count'] = psutil.cpu_count(logical=False)
        context['memory'] = psutil.virtual_memory()
        context['disk_usage'] = psutil.disk_usage('/')
        context['disk_io_counters'] = psutil.disk_io_counters()
        context['network'] = psutil.net_connections()
        context['pids'] = psutil.pids()

        boot_time = psutil.boot_time()
        diff = relativedelta(now, datetime.datetime.fromtimestamp(boot_time))
        context['times'] = dict()
        context['times']['boot_time'] = datetime.datetime.fromtimestamp(boot_time)
        context['times']['up_time'] = f'{diff.days} days, {diff.hours} hours, {diff.minutes} minutes, ' \
                                      f'{diff.seconds} seconds'

        context['platform'] = psutil.os.uname()

        return render(request, self.template_name, context=context)


class ShowHostProcesses(View):
    """ Display dashboard like page showing host process data """
    template_name = 'handyhelpers/host/bs5/processes.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'Host Processes'
        context['subtitle'] = psutil.os.uname()[1]
        context['process_list'] = list(psutil.process_iter())
        counts = dict(
            running=len([i for i in list(psutil.process_iter()) if i.status() == 'running']),
            sleeping=len([i for i in list(psutil.process_iter()) if i.status() == 'sleeping']),
            stopped=len([i for i in list(psutil.process_iter()) if i.status() == 'stopped']),
            zombie=len([i for i in list(psutil.process_iter()) if i.status() == 'zombie']),
            dead=len([i for i in list(psutil.process_iter()) if i.status() == 'dead']),
        )
        context['counts'] = counts
        return render(request, self.template_name, context=context)


class ShowHostNetwork(View):
    """ Display dashboard like page showing host network data """
    template_name = 'handyhelpers/host/bs5/network.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'Network Dashboard'
        context['subtitle'] = psutil.os.uname()[1]
        context['connection_list'] = psutil.net_connections()
        context['interface_list'] = psutil.net_if_addrs()
        context['stats_list'] = psutil.net_if_stats()
        context['counters'] = psutil.net_io_counters()
        return render(request, self.template_name, context=context)


class ShowHostDisk(View):
    """ Display dashboard like page showing host disk data """
    template_name = 'handyhelpers/host/bs5/disk.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'Disk Dashboard'
        context['subtitle'] = psutil.os.uname()[1]
        context['usage'] = psutil.disk_usage('/')
        context['io_counters'] = psutil.disk_io_counters()
        context['partition_lists'] = psutil.disk_partitions()
        return render(request, self.template_name, context=context)


class ShowHostMemory(View):
    """ Display dashboard like page showing host memory data """
    template_name = 'handyhelpers/host/bs5/memory.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'Memory Dashboard'
        context['subtitle'] = psutil.os.uname()[1]
        context['virtual'] = psutil.virtual_memory()
        context['swap'] = psutil.swap_memory()
        return render(request, self.template_name, context=context)


class ShowHostCpu(View):
    """ Display dashboard like page showing host cpu data """
    template_name = 'handyhelpers/host/bs5/cpu.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'CPU Dashboard'
        context['subtitle'] = psutil.os.uname()[1]
        context['stats'] = psutil.cpu_stats()
        context['physical_count'] = psutil.cpu_count(logical=False)
        context['logical_count'] = psutil.cpu_count(logical=True)
        context['percent'] = psutil.cpu_percent(interval=None)
        context['times_list'] = psutil.cpu_times(percpu=True)
        context['times_percent_list'] = psutil.cpu_times_percent(percpu=True)
        context['percent_list'] = psutil.cpu_percent(interval=None, percpu=True)
        context['frequency_list'] = psutil.cpu_freq(percpu=True)
        context['cpu_range'] = [i for i in range(psutil.cpu_count(logical=True))]
        cpu_data = dict()
        for i in range(context['logical_count']):
            cpu_data[i] = dict(
                times=context['times_list'][i],
                time_percent=context['times_percent_list'][i],
                percent=context['percent_list'][i],
                frequency=context['frequency_list'][i],
            )
        context['cpu_data'] = cpu_data
        context['load_avg_1'], context['load_avg_5'], context['load_avg_15'] = \
            [round(x / psutil.cpu_count() * 100, 2) for x in psutil.getloadavg()]
        return render(request, self.template_name, context=context)

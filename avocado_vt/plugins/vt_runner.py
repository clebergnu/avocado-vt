import multiprocessing
import tempfile
import time

from avocado.core import job, loader, nrunner
from avocado.core.test import TestID
from avocado.core.tree import TreeNode

from ..test import VirtTest


class VTTestRunner(nrunner.BaseRunner):
    """
    Runner for Avocado INSTRUMENTED tests

    Runnable attributes usage:

     * uri: name of VT test

     * args: not used

     * kwargs: all the VT specific parameters
    """
    DEFAULT_TIMEOUT = 86400

    @staticmethod
    def _run_avocado_vt(runnable, queue):
        test_factory = [VirtTest,
                        {'name': TestID(1, runnable.uri),
                         'params': (TreeNode(), []),
                         'job': job.Job(),
                         'base_logdir': tempfile.mkdtemp(),
                         'vt_params': runnable.kwargs,
                         }]

        instance = loader.loader.load_test(test_factory)
        early_state = instance.get_state()
        queue.put(early_state)
        instance.run_avocado()
        state = instance.get_state()
        # This should probably be done in a translator
        if 'status' in state:
            status = state['status'].lower()
            if status in ['pass', 'fail', 'skip', 'error']:
                state['result'] = status
                state['status'] = 'finished'
            else:
                state['status'] = 'running'

        # This is a hack because the name is a TestID instance that can not
        # at this point be converted to JSON
        if 'name' in state:
            del state['name']
        if 'time_start' in state:
            del state['time_start']
        queue.put(state)

    def run(self):
        queue = multiprocessing.SimpleQueue()
        process = multiprocessing.Process(target=self._run_avocado_vt,
                                          args=(self.runnable, queue))

        process.start()

        time_started = time.monotonic()
        yield self.prepare_status('started')

        # Waiting for early status
        while queue.empty():
            time.sleep(nrunner.RUNNER_RUN_CHECK_INTERVAL)

        early_status = queue.get()
        timeout = float(early_status.get('timeout') or self.DEFAULT_TIMEOUT)
        interrupted = False
        most_current_execution_state_time = None
        while queue.empty():
            time.sleep(nrunner.RUNNER_RUN_CHECK_INTERVAL)
            now = time.monotonic()
            if most_current_execution_state_time is not None:
                next_execution_state_mark = (most_current_execution_state_time +
                                             nrunner.RUNNER_RUN_STATUS_INTERVAL)
            if (most_current_execution_state_time is None or
                    now > next_execution_state_mark):
                most_current_execution_state_time = now
                yield self.prepare_status('running')
            if (now - time_started) > timeout:
                process.terminate()
                interrupted = True
                break
        if interrupted:
            status = early_status
            status['result'] = 'interrupted'
            status['status'] = 'finished'
            if 'name' in status:
                del status['name']
            if 'time_start' in status:
                del status['time_start']
        else:
            status = queue.get()
        status['time'] = time.monotonic()
        yield status


class RunnerApp(nrunner.BaseRunnerApp):
    PROG_NAME = 'avocado-runner-avocado-vt'
    PROG_DESCRIPTION = 'nrunner application for Avocado-VT tests'
    RUNNABLE_KINDS_CAPABLE = {
        'avocado-vt': VTTestRunner
    }


def main():
    nrunner.main(RunnerApp)


if __name__ == '__main__':
    main()

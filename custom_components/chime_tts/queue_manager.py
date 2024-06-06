"""Chime TTS service call queue manager."""

import logging
import asyncio
from datetime import datetime

from .const import QUEUE_TIMEOUT_DEFAULT

_LOGGER = logging.getLogger(__name__)

class ChimeTTSQueueManager:
    """Chime TTS class to manage the service call queue manager."""

    def __init__(self, p_timeout_s: int = QUEUE_TIMEOUT_DEFAULT):
        """Initialize the queue manager."""
        self.running_tasks = []
        self.timeout_s = p_timeout_s
        self._shutdown = False
        self.semaphore = None
        self.queue = None

    async def async_process_queue(self):
        """Process the Chime TTS service call queue."""
        # Use a semaphore to allow only one task at a time
        if not self.semaphore:
            self.semaphore = asyncio.Semaphore(1)
        while not self._shutdown:
            async with self.semaphore:
                service_call = await self.queue.get()

                if service_call is None:
                    _LOGGER.debug("Queue empty")
                    self.queue.task_done()
                    break  # Signal to exit the queue processing

                try:
                    start_time = datetime.now()
                    result = await asyncio.wait_for(
                        service_call['function'](*service_call['args'], **service_call['kwargs']),
                        timeout=self.timeout_s
                    )
                    service_call['future'].set_result(result)
                except asyncio.TimeoutError:
                    end_time = datetime.now()
                    completion_time = round((end_time - start_time).total_seconds(), 2)
                    elapsed_time = (f"{completion_time}s"
                                    if completion_time >= 1
                                    else f"{completion_time * 1000}ms")
                    service_call['future'].set_exception(Exception(f"Service call timed out after {elapsed_time} (configured timeout = {self.timeout_s}s)"))
                except Exception as e:
                    service_call['future'].set_exception(e)
                finally:
                    self.queue.task_done()

    async def queue_processor(self):
        """Continuously process the Chime TTS service call queue."""
        while not self._shutdown:
            await asyncio.sleep(0.1)  # Adjust the sleep duration as needed
            if not self.queue.empty():
                tasks = [self.async_process_queue() for _ in range(self.queue.qsize())]
                await asyncio.gather(*tasks)

    def add_to_queue(self, function, p_timeout, *args, **kwargs):
        """Add a new service call to the Chime TTS service call queue."""
        self.set_timeout(p_timeout)
        if not self.queue:
            self.start_queue_processor()

        future = asyncio.Future()
        _LOGGER.debug("Adding service call to queue")
        try:
            self.queue.put_nowait({
                'function': function,
                'args': args,
                'kwargs': kwargs,
                'future': future
            })
        except Exception as error:
            _LOGGER.error("Unable to add Chime TTS task to queue: %s", str(error))
        return future

    def reset_queue(self):
        """Remove any existing items in the queue and reset."""
        self._shutdown = True
        if self.queue is not None:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        self.queue = asyncio.Queue()
        self._shutdown = False
        _LOGGER.debug("Queue reset")

        # Start the queue processor if not already running
        if not self.running_tasks:
            self.start_queue_processor()

    def set_timeout(self, p_timeout):
        """Set the timeout duration for queued service calls."""
        self.timeout_s = p_timeout

    def start_queue_processor(self):
        """Start the queue processor task."""
        self.queue = asyncio.Queue()
        task = asyncio.create_task(self.queue_processor())
        self.running_tasks.append(task)

    def stop_queue_processor(self):
        """Stop the queue processor task."""
        self._shutdown = True
        for task in self.running_tasks:
            task.cancel()
        self.running_tasks.clear()

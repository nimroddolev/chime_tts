"""Chime TTS service call queue manager."""

import logging
import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import TypedDict
from .const import (
    QUEUE_TIMEOUT_DEFAULT,
    MAX_CONCURRENT_TASKS,
    MAX_TIMEOUT,
    QUEUE_PROCESSOR_SLEEP_TIME
)

_LOGGER = logging.getLogger(__name__)

class ServiceCall(TypedDict):
    """Represents a service call in the Chime TTS queue."""

    function: Callable[..., Coroutine[any, any, any]]
    args: tuple
    kwargs: dict
    future: asyncio.Future

class ChimeTTSQueueManager:
    """Manage the Chime TTS service call queue."""

    def __init__(self, p_timeout_s: int = QUEUE_TIMEOUT_DEFAULT):
        """Initialize the queue manager."""
        self.running_tasks: list[asyncio.Task] = []
        self.timeout_s: int = min(p_timeout_s, MAX_TIMEOUT)
        self._shutdown_event: asyncio.Event = asyncio.Event()
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
        self.queue: asyncio.Queue[ServiceCall | None] = asyncio.Queue()

    async def async_process_queue(self) -> None:
        """Process the Chime TTS service call queue."""
        while not self._shutdown_event.is_set():
            try:
                service_call = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            if service_call is None:
                _LOGGER.debug("Queue empty")
                self.queue.task_done()
                continue  # Keep processing instead of breaking

            # Process the service call
            await self._process_service_call(service_call)

    async def _process_service_call(self, service_call: ServiceCall) -> None:
        """Process a single service call."""
        start_time = datetime.now()
        try:
            async with self.semaphore:
                result = await asyncio.wait_for(
                    service_call['function'](*service_call['args'], **service_call['kwargs']),
                    timeout=self.timeout_s
                )
                try:
                    service_call['future'].set_result(result)
                except Exception as e:
                    _LOGGER.error("Error setting result for service call %s: %s", service_call, str(e))

        except asyncio.TimeoutError:
            self._handle_timeout_error(service_call, start_time)
        except asyncio.CancelledError:
            _LOGGER.info("Service call %s was cancelled", service_call)
            service_call['future'].set_exception(asyncio.CancelledError())
        except Exception as e:
            _LOGGER.error("Error processing service call %s: %s", service_call, str(e))
            service_call['future'].set_exception(e)
        finally:
            self.queue.task_done()

    def _handle_timeout_error(self, service_call: ServiceCall, start_time: datetime) -> None:
        """Handle timeout error for a service call."""
        end_time = datetime.now()
        completion_time = round((end_time - start_time).total_seconds(), 2) or 0
        elapsed_time = f"{completion_time}s" if completion_time >= 1 else f"{completion_time * 1000}ms"
        _LOGGER.warning("Service call %s timed out after %s", service_call, elapsed_time)
        service_call['future'].set_exception(
            TimeoutError(f"Service call timed out after {elapsed_time} (configured timeout = {self.timeout_s}s)")
        )

    async def async_queue_processor(self) -> None:
        """Continuously process the Chime TTS service call queue."""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(QUEUE_PROCESSOR_SLEEP_TIME)
            if not self.queue.empty():
                await self.async_process_queue()

    def add_to_queue(self,
                     function: Callable[..., Coroutine[any, any, any]],
                     p_timeout: int,
                     *args: any,
                     **kwargs: any) -> asyncio.Future:
        """Add a new service call to the Chime TTS service call queue."""
        self.set_timeout(p_timeout)
        future: asyncio.Future = asyncio.Future()
        queue_size = self.queue.qsize()
        if queue_size == 0:
            _LOGGER.debug("Adding service call to queue")
        else:
            _LOGGER.debug("Adding service call to queue (%s ahead)", str(queue_size))
        try:
            self.queue.put_nowait(ServiceCall(
                function=function,
                args=args,
                kwargs=kwargs,
                future=future
            ))
        except asyncio.QueueFull:
            _LOGGER.error("Unable to add Chime TTS task to queue: Queue is full")
            future.set_exception(RuntimeError("Queue is full"))
        return future

    def reset_queue(self) -> None:
        """Remove any existing items in the queue and reset."""
        _LOGGER.info("Resetting queue")
        self._shutdown_event.set()
        self._clear_queue()
        self._shutdown_event.clear()
        _LOGGER.debug("Queue reset")
        if not self.running_tasks:
            self.start_queue_processor()

    def _clear_queue(self) -> None:
        """Clear all items from the queue."""
        while not self.queue.empty():
            try:
                task = self.queue.get_nowait()
                if isinstance(task, asyncio.Future):
                    task.cancel()
                self.queue.task_done()
            except asyncio.QueueEmpty:
                break

    def set_timeout(self, p_timeout: int) -> None:
        """Set the timeout duration for queued service calls."""
        self.timeout_s = min(p_timeout, MAX_TIMEOUT)

    def start_queue_processor(self) -> None:
        """Start the queue processor task."""
        task = asyncio.create_task(self.async_queue_processor())
        task.add_done_callback(lambda t: self.running_tasks.remove(t) if t in self.running_tasks else None)
        self.running_tasks.append(task)

    async def stop_queue_processor(self) -> None:
        """Stop the queue processor task."""
        _LOGGER.info("Stopping queue processor")
        self._shutdown_event.set()
        for task in self.running_tasks:
            task.cancel()  # Gracefully cancel tasks
            try:
                await task  # Await task to handle asyncio.CancelledError cleanly
            except asyncio.CancelledError:
                _LOGGER.debug("Task was cancelled cleanly")
        self.running_tasks.clear()

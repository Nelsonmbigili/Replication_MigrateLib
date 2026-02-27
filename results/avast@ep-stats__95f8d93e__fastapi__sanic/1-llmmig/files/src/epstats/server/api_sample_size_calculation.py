import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from sanic import Sanic, response
from sanic.exceptions import SanicException

from ..toolkit.statistics import Statistics
from .req import SampleSizeCalculationData
from .res import SampleSizeCalculationResult

_logger = logging.getLogger("epstats")


def get_sample_size_calculation_app(get_executor_pool) -> Sanic:
    app = Sanic("SampleSizeCalculationApp")

    def _sample_size_calculation(data: SampleSizeCalculationData):
        try:
            if data.std is None:
                f = Statistics.required_sample_size_per_variant_bernoulli
            else:
                f = Statistics.required_sample_size_per_variant

            sample_size_per_variant = f(**data.dict())

            _logger.info((f"Calculation finished, sample_size_per_variant = {sample_size_per_variant}."))
            return SampleSizeCalculationResult(sample_size_per_variant=sample_size_per_variant)
        except Exception as e:
            _logger.error(f"Cannot calculate the sample size because of: '{e}'")
            _logger.exception(e)
            raise SanicException(
                f"Cannot calculate the sample size because of: '{e}'", status_code=500
            )

    @app.post("/sample-size-calculation")
    async def sample_size_calculation(request):
        """
        Calculates sample size based on `data`.
        """
        try:
            data = SampleSizeCalculationData(**request.json)
        except Exception as e:
            _logger.error(f"Invalid request data: {e}")
            raise SanicException(f"Invalid request data: {e}", status_code=400)

        _logger.info(f"Calling the sample size calculation with {data.json()}")
        evaluation_pool = get_executor_pool()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(evaluation_pool, _sample_size_calculation, data)
        return response.json(result.dict())

    return app
